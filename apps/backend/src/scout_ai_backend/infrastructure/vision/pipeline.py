import base64
import subprocess
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import httpx
import numpy as np
import supervision as sv
from ultralytics import YOLO

from scout_ai_backend.domain.entities.player import Player, Position, TeamSide
from scout_ai_backend.domain.entities.statistics import (
    MatchStatistics,
    MomentumPoint,
    PassEdge,
    PassTimelinePoint,
    TeamSplit,
)

# Unified class ids used downstream, regardless of which detector produced
# them (local YOLO's COCO classes, or Roboflow's football-specific classes).
PERSON_CLASS_ID = 0
BALL_CLASS_ID = 1

_COCO_PERSON_CLASS_ID = 0
_COCO_BALL_CLASS_ID = 32

# Raised from 0.3: Roboflow's model sometimes classifies sideline officials
# (assistant referees/linesmen) as "player" rather than "referee", and those
# misclassifications tend to score lower confidence than genuine in-play
# detections. This is a blunt instrument, not a targeted fix — it may also
# drop real players who are small, distant, or partially occluded.
MIN_PERSON_CONFIDENCE = 0.45
MIN_BALL_CONFIDENCE = 0.15

SAMPLE_FPS = 5.0
# 300 sampled frames at 5fps covers 60s of play, matching the ~60-90s clips
# this pipeline expects. Each sampled frame is a Roboflow API round-trip, so
# raising this multiplies total processing time roughly linearly.
MAX_SAMPLED_FRAMES = 300
# Drop short-lived spurious tracks (false positives, occlusions). At 5
# sampled fps, 20 frames is ~4s of continuous presence — measured empirically
# on real footage: ByteTrack's IoU matching is designed for near-30fps input,
# so at our much sparser sampling rate, fast-moving players routinely get
# reassigned a new track ID every few seconds even when detection itself is
# solid. Scale this with SAMPLE_FPS to hold the same ~4s real-world
# threshold. A dedicated re-identification model would fix this properly;
# out of scope for now.
MIN_TRACK_FRAMES = 20
HEATMAP_COLS = 20
HEATMAP_ROWS = 12
MOMENTUM_BUCKETS = 10

HOME_COLOR = sv.Color.from_hex("#18C37E")
# Matches the "away" rose used by the dashboard charts — reads far better on
# grass than the old gray.
AWAY_COLOR = sv.Color.from_hex("#FB7185")
BALL_COLOR = sv.Color.from_hex("#FFD700")

# Standard pitch dimensions, used to convert normalized on-screen movement
# into an approximate distance. No camera calibration/homography is applied,
# so this is a rough estimate, not a precise measurement.
PITCH_LENGTH_KM = 0.105
PITCH_WIDTH_KM = 0.068

_model: YOLO | None = None
_http_client: httpx.Client | None = None


def _get_model() -> YOLO:
    global _model
    if _model is None:
        _model = YOLO("yolov8n.pt")
    return _model


def _get_http_client() -> httpx.Client:
    global _http_client
    if _http_client is None:
        _http_client = httpx.Client(timeout=15.0)
    return _http_client


def _select_top_ball(detections: sv.Detections) -> sv.Detections:
    """Keep at most one ball detection per frame — the highest-confidence
    one — since exactly one ball can be on the pitch at a time."""
    ball_mask = detections.class_id == BALL_CLASS_ID
    if ball_mask.sum() <= 1:
        return detections
    ball_indices = np.flatnonzero(ball_mask)
    best_ball = ball_indices[np.argmax(detections.confidence[ball_indices])]
    drop = np.setdiff1d(ball_indices, [best_ball])
    keep = np.ones(len(detections), dtype=bool)
    keep[drop] = False
    return detections[keep]


def _detect_local(frame: np.ndarray) -> sv.Detections:
    """COCO-pretrained YOLOv8n. No API key required, so the pipeline works
    out of the box — but it has near-zero recall on a small ball at
    broadcast distance (COCO's "sports ball" class skews toward close-up
    basketballs/baseballs, not small distant footballs)."""
    model = _get_model()
    results = model(frame, classes=[_COCO_PERSON_CLASS_ID, _COCO_BALL_CLASS_ID], verbose=False)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections.class_id = np.where(
        detections.class_id == _COCO_PERSON_CLASS_ID, PERSON_CLASS_ID, BALL_CLASS_ID
    )
    return _select_top_ball(detections)


def _detect_roboflow(frame: np.ndarray, *, api_key: str, model_id: str) -> sv.Detections:
    """Roboflow-hosted "football-players-detection" model — trained
    specifically on ball/goalkeeper/player/referee, so it actually finds
    the ball. Requires a (free) Roboflow API key."""
    _, buffer = cv2.imencode(".jpg", frame)
    response = _get_http_client().post(
        f"https://detect.roboflow.com/{model_id}",
        params={"api_key": api_key, "confidence": 10},
        content=base64.b64encode(buffer).decode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status()
    detections = sv.Detections.from_inference(response.json())

    class_names = detections.data.get("class_name", [])
    unified = np.array(
        [
            PERSON_CLASS_ID
            if name in ("player", "goalkeeper")
            else BALL_CLASS_ID
            if name == "ball"
            else -1
            for name in class_names
        ]
    )
    detections = detections[unified >= 0]
    detections.class_id = unified[unified >= 0]
    return _select_top_ball(detections)


def _detect(frame: np.ndarray, *, roboflow_api_key: str, roboflow_model_id: str) -> sv.Detections:
    if roboflow_api_key:
        return _detect_roboflow(frame, api_key=roboflow_api_key, model_id=roboflow_model_id)
    return _detect_local(frame)


@dataclass
class _TrackAccumulator:
    positions: list[tuple[float, float]] = field(default_factory=list)
    sample_indices: list[int] = field(default_factory=list)
    shirt_colors: list[np.ndarray] = field(default_factory=list)
    ball_frames: int = 0


# ByteTrack loses and reassigns IDs constantly on real footage sampled at a
# sparse 2fps (measured: 50-100+ distinct IDs for ~10-14 actual players).
# Rather than a full re-identification model, stitch fragments back together
# when they're close in time, close in position, and similar shirt color —
# a cheap heuristic that catches the common case (brief occlusion or a
# missed detection), not full re-identification.
STITCH_MAX_GAP_SAMPLES = 6  # ~3s at 2fps
STITCH_MAX_DISTANCE = 0.12  # normalized pitch-space distance
STITCH_MAX_COLOR_DISTANCE = 40.0


def _avg_color(colors: list[np.ndarray]) -> np.ndarray | None:
    if not colors:
        return None
    return np.mean(np.array(colors), axis=0)


def _stitch_tracks(
    tracks: dict[int, _TrackAccumulator],
) -> tuple[dict[int, _TrackAccumulator], dict[int, int]]:
    fragments = sorted(
        (
            {
                "id": tid,
                "start": acc.sample_indices[0],
                "end": acc.sample_indices[-1],
                "start_pos": acc.positions[0],
                "end_pos": acc.positions[-1],
                "color": _avg_color(acc.shirt_colors),
            }
            for tid, acc in tracks.items()
            if acc.positions
        ),
        key=lambda f: f["start"],
    )

    remap: dict[int, int] = {}
    chain_tails: dict[int, dict] = {}

    for frag in fragments:
        best_id: int | None = None
        best_dist: float | None = None
        for canonical_id, tail in chain_tails.items():
            gap = frag["start"] - tail["end"]
            if gap <= 0 or gap > STITCH_MAX_GAP_SAMPLES:
                continue
            dist = _distance(tail["end_pos"], frag["start_pos"])
            if dist > STITCH_MAX_DISTANCE:
                continue
            if tail["color"] is not None and frag["color"] is not None:
                color_dist = float(np.linalg.norm(tail["color"] - frag["color"]))
                if color_dist > STITCH_MAX_COLOR_DISTANCE:
                    continue
            if best_dist is None or dist < best_dist:
                best_id, best_dist = canonical_id, dist

        canonical_id = best_id if best_id is not None else frag["id"]
        remap[frag["id"]] = canonical_id
        chain_tails[canonical_id] = {
            "end": frag["end"],
            "end_pos": frag["end_pos"],
            "color": frag["color"],
        }

    merged: dict[int, _TrackAccumulator] = defaultdict(_TrackAccumulator)
    for tid in sorted(
        (t for t in tracks if tracks[t].positions), key=lambda t: tracks[t].sample_indices[0]
    ):
        acc = tracks[tid]
        target = merged[remap[tid]]
        target.positions.extend(acc.positions)
        target.sample_indices.extend(acc.sample_indices)
        target.shirt_colors.extend(acc.shirt_colors)
        target.ball_frames += acc.ball_frames

    return dict(merged), remap


def analyze_video_sync(
    video_path: str,
    match_id: uuid.UUID,
    *,
    kickoff_offset_seconds: float = 0.0,
    roboflow_api_key: str = "",
    roboflow_model_id: str = "",
) -> tuple[MatchStatistics, list[Player], str]:
    """Run YOLO detection + ByteTrack tracking over a sampled set of frames,
    cluster players into two teams by shirt color, and compute a possession
    estimate, average positions, heatmaps, distance covered, a passing
    network, and time-bucketed momentum. Also renders an annotated copy of
    the video (player boxes/IDs colored by team, ball highlighted) and
    returns its path alongside the stats.

    This is synchronous, CPU/IO-bound work — call it via
    `asyncio.to_thread` from async code so it doesn't block the event loop.
    """
    # frame_rate must reflect our actual sampling cadence (2 fps), not a
    # real video's ~30fps — ByteTrack uses it to size its lost-track buffer.
    tracker = sv.ByteTrack(frame_rate=SAMPLE_FPS)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    source_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_interval = max(int(round(source_fps / SAMPLE_FPS)), 1)
    if kickoff_offset_seconds > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(kickoff_offset_seconds * source_fps))

    tracks: dict[int, _TrackAccumulator] = defaultdict(_TrackAccumulator)
    # (sample_index, nearest_track_id) for every sampled frame where the
    # ball was detected and someone was nearest it. Used after clustering
    # to derive both the passing network and momentum over time.
    possession_sequence: list[tuple[int, int]] = []
    # Per-sampled-frame boxes, cached so the annotation pass can redraw them
    # without re-running YOLO a second time.
    frame_people_boxes: list[dict[int, tuple[float, float, float, float]]] = []
    frame_ball_box: list[tuple[float, float, float, float] | None] = []
    frame_index = 0
    sampled = 0

    while sampled < MAX_SAMPLED_FRAMES:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_index % frame_interval != 0:
            frame_index += 1
            continue
        frame_index += 1
        sampled += 1

        height, width = frame.shape[:2]
        detections = _detect(
            frame, roboflow_api_key=roboflow_api_key, roboflow_model_id=roboflow_model_id
        )

        person_detections = detections[
            (detections.class_id == PERSON_CLASS_ID) & (detections.confidence >= MIN_PERSON_CONFIDENCE)
        ]
        people = tracker.update_with_detections(person_detections)
        ball_detections = detections[
            (detections.class_id == BALL_CLASS_ID) & (detections.confidence >= MIN_BALL_CONFIDENCE)
        ]
        ball_boxes = ball_detections.xyxy

        frame_positions: dict[int, tuple[float, float]] = {}
        people_boxes: dict[int, tuple[float, float, float, float]] = {}
        for box, tracker_id in zip(people.xyxy, people.tracker_id, strict=True):
            # Cast off numpy's float32 immediately — it isn't JSON-serializable,
            # and every downstream value (positions, distances, heatmap) is
            # eventually persisted as JSON.
            x1, y1, x2, y2 = (float(v) for v in box)
            cx, cy = (x1 + x2) / 2 / width, (y1 + y2) / 2 / height
            frame_positions[int(tracker_id)] = (cx, cy)
            people_boxes[int(tracker_id)] = (x1, y1, x2, y2)

            acc = tracks[int(tracker_id)]
            acc.positions.append((cx, cy))
            acc.sample_indices.append(sampled - 1)

            crop = frame[max(int(y1), 0) : int(y2), max(int(x1), 0) : int(x2)]
            shirt_color = _dominant_shirt_color(crop)
            if shirt_color is not None:
                acc.shirt_colors.append(shirt_color)
        frame_people_boxes.append(people_boxes)

        if len(ball_boxes) > 0 and frame_positions:
            bx1, by1, bx2, by2 = (float(v) for v in ball_boxes[0])
            ball_center = ((bx1 + bx2) / 2 / width, (by1 + by2) / 2 / height)
            nearest_id = min(
                frame_positions, key=lambda tid: _distance(frame_positions[tid], ball_center)
            )
            tracks[nearest_id].ball_frames += 1
            possession_sequence.append((sampled - 1, nearest_id))
            frame_ball_box.append((bx1, by1, bx2, by2))
        else:
            frame_ball_box.append(None)

    cap.release()

    tracks, track_remap = _stitch_tracks(tracks)
    possession_sequence = [
        (sample_idx, track_remap.get(tid, tid)) for sample_idx, tid in possession_sequence
    ]
    frame_people_boxes = [
        {track_remap.get(tid, tid): box for tid, box in frame.items()} for frame in frame_people_boxes
    ]

    valid_tracks = {
        tid: acc for tid, acc in tracks.items() if len(acc.positions) >= MIN_TRACK_FRAMES
    }
    team_by_track = _cluster_teams(valid_tracks)
    display_number_by_track = _assign_display_numbers(team_by_track, valid_tracks)

    pass_counts, passes_made, passes_received, turnovers_by_team = _compute_passes(
        possession_sequence, team_by_track
    )
    momentum = _compute_momentum(possession_sequence, team_by_track, sampled)
    pass_timeline = _compute_pass_timeline(possession_sequence, team_by_track, sampled)

    passes_by_team = {TeamSide.HOME: 0, TeamSide.AWAY: 0}
    for tid, count in passes_made.items():
        passes_by_team[team_by_track[tid]] += count

    def _accuracy(team: TeamSide) -> float:
        made = passes_by_team[team]
        lost = turnovers_by_team.get(team, 0)
        return round(made / (made + lost) * 100, 1) if (made + lost) > 0 else 0.0

    passes_team_split = TeamSplit(home=passes_by_team[TeamSide.HOME], away=passes_by_team[TeamSide.AWAY])
    pass_accuracy = TeamSplit(home=_accuracy(TeamSide.HOME), away=_accuracy(TeamSide.AWAY))

    players: list[Player] = []
    home_distances: list[float] = []
    away_distances: list[float] = []
    home_ball_frames = 0
    away_ball_frames = 0

    touches_by_track = {tid: acc.ball_frames for tid, acc in valid_tracks.items()}
    max_distance = max((_path_distance_km(acc.positions) for acc in valid_tracks.values()), default=0.0)
    max_touches = max(touches_by_track.values(), default=0)
    max_passes = max(
        (passes_made.get(tid, 0) + passes_received.get(tid, 0) for tid in valid_tracks), default=0
    )

    for tid, acc in valid_tracks.items():
        team = team_by_track[tid]
        avg_x = sum(p[0] for p in acc.positions) / len(acc.positions)
        avg_y = sum(p[1] for p in acc.positions) / len(acc.positions)
        distance_km = _path_distance_km(acc.positions)

        if team is TeamSide.HOME:
            home_distances.append(distance_km)
            home_ball_frames += acc.ball_frames
        else:
            away_distances.append(distance_km)
            away_ball_frames += acc.ball_frames

        rating = _compute_rating(
            distance_km=distance_km,
            touches=touches_by_track.get(tid, 0),
            passes=passes_made.get(tid, 0) + passes_received.get(tid, 0),
            max_distance=max_distance,
            max_touches=max_touches,
            max_passes=max_passes,
        )

        players.append(
            Player(
                id=uuid.uuid4(),
                match_id=match_id,
                team=team,
                track_id=str(tid),
                average_position=Position(x=avg_x, y=avg_y),
                distance_covered_km=distance_km,
                heatmap=_build_heatmap(acc.positions),
                touches=touches_by_track.get(tid, 0),
                passes_made=passes_made.get(tid, 0),
                passes_received=passes_received.get(tid, 0),
                rating=rating,
            )
        )

    total_ball_frames = home_ball_frames + away_ball_frames
    possession = (
        TeamSplit(
            home=round(home_ball_frames / total_ball_frames * 100, 1),
            away=round(away_ball_frames / total_ball_frames * 100, 1),
        )
        if total_ball_frames > 0
        else TeamSplit(home=50.0, away=50.0)
    )

    stats = MatchStatistics(
        match_id=match_id,
        possession_estimate=possession,
        average_distance_covered_km=TeamSplit(
            home=round(sum(home_distances) / len(home_distances), 2) if home_distances else 0.0,
            away=round(sum(away_distances) / len(away_distances), 2) if away_distances else 0.0,
        ),
        players_tracked=len(players),
        passing_network=[
            PassEdge(from_track_id=str(a), to_track_id=str(b), count=count)
            for (a, b), count in pass_counts.items()
        ],
        momentum=momentum,
        pass_timeline=pass_timeline,
        passes_by_team=passes_team_split,
        pass_accuracy=pass_accuracy,
    )

    annotated_path = _render_annotated_video(
        video_path,
        frame_interval=frame_interval,
        frame_people_boxes=frame_people_boxes,
        frame_ball_box=frame_ball_box,
        team_by_track=team_by_track,
        display_number_by_track=display_number_by_track,
        source_fps=source_fps,
        kickoff_offset_seconds=kickoff_offset_seconds,
    )

    return stats, players, annotated_path


def _lerp_box(
    a: tuple[float, float, float, float], b: tuple[float, float, float, float], t: float
) -> tuple[float, float, float, float]:
    return (
        a[0] + (b[0] - a[0]) * t,
        a[1] + (b[1] - a[1]) * t,
        a[2] + (b[2] - a[2]) * t,
        a[3] + (b[3] - a[3]) * t,
    )


def _render_annotated_video(
    video_path: str,
    *,
    frame_interval: int,
    frame_people_boxes: list[dict[int, tuple[float, float, float, float]]],
    frame_ball_box: list[tuple[float, float, float, float] | None],
    team_by_track: dict[int, TeamSide],
    display_number_by_track: dict[int, int],
    source_fps: float,
    kickoff_offset_seconds: float = 0.0,
) -> str:
    """Re-reads the video (no re-inference — boxes are cached from the
    first pass) and draws team-colored player boxes + track IDs and the
    ball, at the original frame rate so playback speed/duration match the
    source video. Stops once the analyzed portion ends.

    Plain OpenCV drawing calls rather than supervision's annotators — we
    already have the exact boxes/colors we want per detection, so there's
    no need to round-trip through `sv.Detections` just to draw them."""
    cap = cv2.VideoCapture(video_path)
    if kickoff_offset_seconds > 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(kickoff_offset_seconds * source_fps))
    output_path = str(Path(video_path).with_name(f"{Path(video_path).stem}_annotated.mp4"))
    raw_path = str(Path(video_path).with_name(f"{Path(video_path).stem}_annotated_raw.mp4"))
    writer: cv2.VideoWriter | None = None

    frame_index = 0
    last_sample = len(frame_people_boxes) - 1

    while True:
        ok, frame = cap.read()
        if not ok or frame_index // frame_interval > last_sample:
            break
        sample_index = min(frame_index // frame_interval, last_sample)
        next_index = min(sample_index + 1, last_sample)
        # How far this native frame sits between the two surrounding 2fps
        # samples — lets us glide positions smoothly instead of holding
        # each sample for ~12-15 frames and snapping to the next one.
        t = (frame_index % frame_interval) / frame_interval
        frame_index += 1

        if writer is None:
            height, width = frame.shape[:2]
            writer = cv2.VideoWriter(
                raw_path, cv2.VideoWriter_fourcc(*"mp4v"), source_fps, (width, height)
            )

        current_boxes = frame_people_boxes[sample_index]
        next_boxes = frame_people_boxes[next_index]
        for track_id, box in current_boxes.items():
            # Tracks that never reached MIN_TRACK_FRAMES don't have a team
            # or roster number — drawing them anyway is exactly the flicker
            # of spurious, scattered-looking ids we don't want on screen.
            if track_id not in display_number_by_track:
                continue
            if track_id in next_boxes:
                box = _lerp_box(box, next_boxes[track_id], t)
            team = team_by_track.get(track_id, TeamSide.HOME)
            color = (HOME_COLOR if team is TeamSide.HOME else AWAY_COLOR).as_bgr()
            _draw_player_marker(frame, box, display_number_by_track[track_id], color)

        ball_box = frame_ball_box[sample_index]
        next_ball_box = frame_ball_box[next_index]
        if ball_box is not None:
            if next_ball_box is not None:
                ball_box = _lerp_box(ball_box, next_ball_box, t)
            _draw_ball_marker(frame, ball_box)

        writer.write(frame)

    cap.release()
    if writer is None:
        return video_path

    writer.release()

    # OpenCV's VideoWriter only reliably emits MPEG-4 Part 2 ("mp4v"), which
    # browsers don't decode in a <video> tag. Re-encode to H.264 so the
    # annotated file is actually playable, then drop the intermediate file.
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", raw_path,
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            output_path,
        ],
        check=True,
        capture_output=True,
    )
    Path(raw_path).unlink(missing_ok=True)
    return output_path


def _draw_player_marker(
    frame: np.ndarray,
    box: tuple[float, float, float, float],
    track_id: int,
    color: tuple[int, int, int],
) -> None:
    """Broadcast-style marker: a flat ellipse under the player's feet plus a
    filled ID tag above their head — instead of a bounding box, which reads
    as 'debug output' rather than a product."""
    x1, y1, x2, y2 = box
    cx = int((x1 + x2) / 2)
    feet_y = int(y2)
    half_w = max(int((x2 - x1) * 0.55), 12)

    # Ellipse under the feet (partial arc looks lighter than a full ring).
    cv2.ellipse(
        frame,
        center=(cx, feet_y),
        axes=(half_w, max(int(half_w * 0.35), 5)),
        angle=0,
        startAngle=-45,
        endAngle=235,
        color=color,
        thickness=3,
        lineType=cv2.LINE_4,
    )

    # Filled ID tag centered above the head.
    label = f"#{track_id}"
    font, scale, thickness = cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1
    (tw, th), baseline = cv2.getTextSize(label, font, scale, thickness)
    pad = 5
    tag_w, tag_h = tw + pad * 2, th + baseline + pad
    tag_x1 = cx - tag_w // 2
    tag_y2 = max(int(y1) - 6, tag_h)
    tag_y1 = tag_y2 - tag_h
    cv2.rectangle(frame, (tag_x1, tag_y1), (tag_x1 + tag_w, tag_y2), color, -1)
    # Black text on the bright team colors stays readable on both.
    cv2.putText(
        frame,
        label,
        (tag_x1 + pad, tag_y2 - baseline - 2),
        font,
        scale,
        (10, 10, 11),
        thickness,
        lineType=cv2.LINE_AA,
    )


def _draw_ball_marker(frame: np.ndarray, box: tuple[float, float, float, float]) -> None:
    """Filled triangle pointing down at the ball, like broadcast graphics."""
    bx1, by1, bx2, by2 = box
    cx = int((bx1 + bx2) / 2)
    top_y = max(int(by1) - 8, 0)
    size = 10
    points = np.array(
        [[cx, top_y], [cx - size, top_y - size * 2], [cx + size, top_y - size * 2]],
        dtype=np.int32,
    )
    color = BALL_COLOR.as_bgr()
    cv2.fillPoly(frame, [points], color)
    cv2.polylines(frame, [points], isClosed=True, color=(10, 10, 11), thickness=1)


def _dominant_shirt_color(crop: np.ndarray) -> np.ndarray | None:
    if crop.size == 0:
        return None
    h, w = crop.shape[:2]
    # Torso region only — avoids grass below and head/background above.
    torso = crop[int(h * 0.15) : int(h * 0.55), int(w * 0.25) : int(w * 0.75)]
    if torso.size == 0:
        return None
    hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)
    green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
    non_green = torso[green_mask == 0]
    if non_green.size == 0:
        return None
    return np.median(non_green.reshape(-1, 3), axis=0)


def _hue_features(bgr: np.ndarray) -> list[float]:
    """Project a BGR color onto a hue-angle unit circle, scaled by
    saturation. Clustering on raw BGR mixes hue with brightness, so two
    kits with different lighting (a shadowed red vs a sunlit yellow) can
    end up closer in BGR space than two same-lit shirts of genuinely
    different colors — and red itself wraps around at hue 0/180, so a
    single red kit can split across both ends of the raw scale. The
    circular (cos, sin) encoding fixes both: distance reflects true hue
    difference, and red no longer straddles a seam. Low-saturation kits
    (white/black/grey, referees) collapse toward the origin instead of
    forcing themselves into either team's cluster."""
    pixel = np.uint8([[np.clip(bgr, 0, 255)]])
    h, s, _ = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0, 0]
    angle = np.deg2rad(float(h) * 2.0)
    weight = float(s) / 255.0
    return [np.cos(angle) * weight, np.sin(angle) * weight]


def _cluster_teams(tracks: dict[int, _TrackAccumulator]) -> dict[int, TeamSide]:
    colored_ids = [tid for tid, acc in tracks.items() if acc.shirt_colors]
    if len(colored_ids) < 2:
        return dict.fromkeys(tracks, TeamSide.HOME)

    samples = np.array(
        [
            _hue_features(np.median(np.array(tracks[tid].shirt_colors), axis=0))
            for tid in colored_ids
        ],
        dtype=np.float32,
    )
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5)
    _, labels, _ = cv2.kmeans(samples, 2, None, criteria, 5, cv2.KMEANS_PP_CENTERS)

    team_by_track = {
        tid: (TeamSide.HOME if label == 0 else TeamSide.AWAY)
        for tid, label in zip(colored_ids, labels.flatten(), strict=True)
    }
    for tid in tracks:
        team_by_track.setdefault(tid, TeamSide.HOME)
    return team_by_track


def _assign_display_numbers(
    team_by_track: dict[int, TeamSide], tracks: dict[int, _TrackAccumulator]
) -> dict[int, int]:
    """Raw ByteTrack ids are whatever survived stitching — arbitrary, often
    large, and in no particular order. Renumber each team 1..N by first
    appearance so the on-video tags read like a roster instead of
    scattered debug ids."""
    display_by_track: dict[int, int] = {}
    for team in (TeamSide.HOME, TeamSide.AWAY):
        team_ids = sorted(
            (tid for tid in tracks if team_by_track.get(tid) is team),
            key=lambda tid: min(tracks[tid].sample_indices, default=0),
        )
        for number, tid in enumerate(team_ids, start=1):
            display_by_track[tid] = number
    return display_by_track


def _compute_passes(
    possession_sequence: list[tuple[int, int]], team_by_track: dict[int, TeamSide]
) -> tuple[dict[tuple[int, int], int], dict[int, int], dict[int, int], dict[TeamSide, int]]:
    """A 'pass' is inferred whenever the nearest-to-ball player changes to a
    different player on the same team. Changes between different teams are
    turnovers/interceptions, counted separately (by the team that lost the
    ball) so pass accuracy can be computed honestly from the same signal
    rather than invented."""
    pass_counts: dict[tuple[int, int], int] = defaultdict(int)
    passes_made: dict[int, int] = defaultdict(int)
    passes_received: dict[int, int] = defaultdict(int)
    turnovers_by_team: dict[TeamSide, int] = defaultdict(int)

    for (_, prev_id), (_, next_id) in zip(possession_sequence, possession_sequence[1:], strict=False):
        if prev_id == next_id:
            continue
        if prev_id not in team_by_track or next_id not in team_by_track:
            continue
        if team_by_track[prev_id] != team_by_track[next_id]:
            turnovers_by_team[team_by_track[prev_id]] += 1
            continue
        pass_counts[(prev_id, next_id)] += 1
        passes_made[prev_id] += 1
        passes_received[next_id] += 1

    return dict(pass_counts), dict(passes_made), dict(passes_received), dict(turnovers_by_team)


def _compute_momentum(
    possession_sequence: list[tuple[int, int]],
    team_by_track: dict[int, TeamSide],
    total_sampled: int,
) -> list[MomentumPoint]:
    if total_sampled == 0:
        return []

    bucket_size = max(total_sampled / MOMENTUM_BUCKETS, 1)
    home_counts = [0] * MOMENTUM_BUCKETS
    away_counts = [0] * MOMENTUM_BUCKETS

    for sample_index, track_id in possession_sequence:
        team = team_by_track.get(track_id)
        if team is None:
            continue
        bucket = min(int(sample_index / bucket_size), MOMENTUM_BUCKETS - 1)
        if team is TeamSide.HOME:
            home_counts[bucket] += 1
        else:
            away_counts[bucket] += 1

    points: list[MomentumPoint] = []
    for i in range(MOMENTUM_BUCKETS):
        total = home_counts[i] + away_counts[i]
        home_pct = round(home_counts[i] / total * 100, 1) if total > 0 else 50.0
        away_pct = round(100 - home_pct, 1) if total > 0 else 50.0
        time_seconds = round((i + 1) * bucket_size / SAMPLE_FPS, 1)
        points.append(
            MomentumPoint(
                time_seconds=time_seconds, home_possession_pct=home_pct, away_possession_pct=away_pct
            )
        )
    return points


def _compute_pass_timeline(
    possession_sequence: list[tuple[int, int]],
    team_by_track: dict[int, TeamSide],
    total_sampled: int,
) -> list[PassTimelinePoint]:
    """Same bucketing as momentum, but counting completed passes (same-team
    possession transitions) per window instead of possession share."""
    if total_sampled == 0:
        return []

    bucket_size = max(total_sampled / MOMENTUM_BUCKETS, 1)
    counts = [0] * MOMENTUM_BUCKETS

    for (prev_sample, prev_id), (_, next_id) in zip(
        possession_sequence, possession_sequence[1:], strict=False
    ):
        if prev_id == next_id:
            continue
        if prev_id not in team_by_track or next_id not in team_by_track:
            continue
        if team_by_track[prev_id] != team_by_track[next_id]:
            continue
        bucket = min(int(prev_sample / bucket_size), MOMENTUM_BUCKETS - 1)
        counts[bucket] += 1

    return [
        PassTimelinePoint(time_seconds=round((i + 1) * bucket_size / SAMPLE_FPS, 1), count=counts[i])
        for i in range(MOMENTUM_BUCKETS)
    ]


def _compute_rating(
    *,
    distance_km: float,
    touches: int,
    passes: int,
    max_distance: float,
    max_touches: int,
    max_passes: int,
) -> float:
    """Transparent composite score (3-10), not an invented subjective
    number: relative distance covered, ball involvement, and passing
    activity, each normalized against the match's own maximum."""
    distance_score = distance_km / max_distance if max_distance > 0 else 0.5
    touches_score = touches / max_touches if max_touches > 0 else 0.5
    passes_score = passes / max_passes if max_passes > 0 else 0.5
    composite = 0.4 * distance_score + 0.4 * touches_score + 0.2 * passes_score
    return round(3 + composite * 7, 1)


def _path_distance_km(positions: list[tuple[float, float]]) -> float:
    total = 0.0
    for (x1, y1), (x2, y2) in zip(positions, positions[1:], strict=False):
        dx = (x2 - x1) * PITCH_LENGTH_KM
        dy = (y2 - y1) * PITCH_WIDTH_KM
        total += (dx**2 + dy**2) ** 0.5
    return round(total, 3)


def _build_heatmap(positions: list[tuple[float, float]]) -> list[list[float]]:
    grid = [[0.0] * HEATMAP_COLS for _ in range(HEATMAP_ROWS)]
    for x, y in positions:
        col = min(int(x * HEATMAP_COLS), HEATMAP_COLS - 1)
        row = min(int(y * HEATMAP_ROWS), HEATMAP_ROWS - 1)
        grid[row][col] += 1
    max_count = max((max(row) for row in grid), default=0) or 1
    return [[round(cell / max_count, 3) for cell in row] for row in grid]


def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
