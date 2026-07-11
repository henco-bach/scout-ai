const links = [
  { href: "#mission", label: "Mission" },
  { href: "#features", label: "Features" },
  { href: "#technology", label: "Technology" },
  { href: "#faq", label: "FAQ" },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-border px-6 py-12">
      <div className="mx-auto flex max-w-5xl flex-col items-center gap-6 sm:flex-row sm:justify-between">
        <div>
          <p className="font-heading text-lg font-semibold">Scout AI</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Built in South Africa. Built for the world.
          </p>
        </div>

        <nav className="flex flex-wrap justify-center gap-6">
          {links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <p className="text-xs text-muted-foreground">
          © {new Date().getFullYear()} Scout AI. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
