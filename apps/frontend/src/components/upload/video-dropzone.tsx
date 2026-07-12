"use client";

import { useCallback, useRef, useState } from "react";
import { UploadCloud, FileVideo, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface VideoDropzoneProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
}

export function VideoDropzone({ file, onFileChange }: VideoDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const next = files?.[0];
      if (next && next.type.startsWith("video/")) {
        onFileChange(next);
      }
    },
    [onFileChange],
  );

  if (file) {
    return (
      <div className="flex items-center gap-4 rounded-xl border border-border bg-card p-5">
        <FileVideo className="size-8 shrink-0 text-primary" strokeWidth={1.5} />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium">{file.name}</p>
          <p className="font-mono text-xs text-muted-foreground">
            {(file.size / (1024 * 1024)).toFixed(1)} MB
          </p>
        </div>
        <button
          type="button"
          onClick={() => onFileChange(null)}
          className="rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          aria-label="Remove video"
        >
          <X className="size-4" />
        </button>
      </div>
    );
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      onClick={() => inputRef.current?.click()}
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-border bg-card/50 px-6 py-16 text-center transition-colors hover:border-primary/50 hover:bg-card",
        isDragging && "border-primary bg-primary/5",
      )}
    >
      <UploadCloud className="size-10 text-muted-foreground" strokeWidth={1.5} />
      <div>
        <p className="font-medium">Drop your match video here</p>
        <p className="mt-1 text-sm text-muted-foreground">
          or click to browse: MP4, MOV, or WebM
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}
