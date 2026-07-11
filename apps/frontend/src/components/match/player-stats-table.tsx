"use client";

import { useState } from "react";
import type { Player } from "@scout-ai/shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Pencil } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { renamePlayer } from "@/lib/api/matches";

function PlayerNameCell({ matchId, player }: { matchId: string; player: Player }) {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(player.name ?? "");

  const mutation = useMutation({
    mutationFn: (name: string) => renamePlayer(player.id, name || null),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["match", matchId] });
      setEditing(false);
    },
  });

  if (editing) {
    return (
      <Input
        autoFocus
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onBlur={() => mutation.mutate(value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") mutation.mutate(value);
          if (e.key === "Escape") setEditing(false);
        }}
        className="h-7 w-32 text-sm"
        disabled={mutation.isPending}
      />
    );
  }

  return (
    <button
      type="button"
      onClick={() => setEditing(true)}
      className="group flex items-center gap-1.5 text-left font-mono text-sm"
    >
      {player.name ?? `#${player.track_id}`}
      <Pencil className="size-3 text-muted-foreground opacity-0 group-hover:opacity-100" />
    </button>
  );
}

export function PlayerStatsTable({ matchId, players }: { matchId: string; players: Player[] }) {
  const sorted = [...players].sort((a, b) => b.rating - a.rating);

  return (
    <div className="rounded-xl border border-border bg-card">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Player</TableHead>
            <TableHead>Team</TableHead>
            <TableHead className="text-right">Distance</TableHead>
            <TableHead className="text-right">Touches</TableHead>
            <TableHead className="text-right">Passes</TableHead>
            <TableHead className="text-right">Rating</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((player) => (
            <TableRow key={player.id}>
              <TableCell>
                <PlayerNameCell matchId={matchId} player={player} />
              </TableCell>
              <TableCell>
                <Badge
                  variant="outline"
                  className={
                    player.team === "home"
                      ? "border-primary/40 text-primary"
                      : "border-border text-muted-foreground"
                  }
                >
                  {player.team === "home" ? "Home" : "Away"}
                </Badge>
              </TableCell>
              <TableCell className="text-right font-mono text-sm">
                {player.distance_covered_km.toFixed(2)}km
              </TableCell>
              <TableCell className="text-right font-mono text-sm">{player.touches}</TableCell>
              <TableCell className="text-right font-mono text-sm">
                {player.passes_made + player.passes_received}
              </TableCell>
              <TableCell className="text-right font-mono text-sm font-semibold text-primary">
                {player.rating.toFixed(1)}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
