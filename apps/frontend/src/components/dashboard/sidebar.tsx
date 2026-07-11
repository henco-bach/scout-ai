"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { BarChart3, Upload } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/matches", label: "Analyses", icon: BarChart3 },
  { href: "/upload", label: "Upload Video", icon: Upload },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col border-r border-border bg-card/40 px-4 py-6">
      <Link href="/" className="mb-8 flex items-center gap-2 px-2">
        <Image src="/brand/icon.png" alt="" width={28} height={28} className="shrink-0" />
        <Image
          src="/brand/wordmark.png"
          alt="Scout AI"
          width={100}
          height={20}
          className="h-5 w-auto"
        />
      </Link>

      <nav className="flex flex-col gap-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              <item.icon className="size-4" strokeWidth={1.75} />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
