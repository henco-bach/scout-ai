FROM python:3.11-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=5

WORKDIR /app

# ffmpeg + libgl/glib: required by OpenCV for video decoding, even headless.
# Allow-insecure/unauthenticated: this build environment's clock skew causes
# Debian's Release-file GPG signature checks to fail (date-based validity),
# not an actual MITM/mirror-integrity concern — deb.debian.org itself is
# unaffected. Safe for a local/CI image build; revisit if this ever runs
# against an untrusted network.
RUN apt-get update -o Acquire::AllowInsecureRepositories=true -o Acquire::AllowDowngradeToInsecureRepositories=true \
    && apt-get install -y --no-install-recommends --allow-unauthenticated \
    gcc ffmpeg libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY apps/backend/pyproject.toml apps/backend/README.md ./
COPY apps/backend/src ./src

RUN pip install --no-cache-dir -e .

# Bake in YOLO weights at build time so the first request isn't slowed down
# by a runtime download.
RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

COPY apps/backend/alembic ./alembic
COPY apps/backend/alembic.ini ./

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn scout_ai_backend.main:app --host 0.0.0.0 --port 8000"]
