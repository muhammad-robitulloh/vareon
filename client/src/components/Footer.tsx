import { Link } from "wouter";
import { Github, Twitter, Linkedin } from "lucide-react";

export default function Footer() {
  const footerSections = [
    {
      title: "Product",
      links: [
        { label: "Arcana AI", href: "/arcana-demo" },
        { label: "NEOSYNTIS", href: "/neosyntis-demo" },
        { label: "MYNTRIX", href: "/myntrix-demo" },
      ],
    },
    {
      title: "Resources",
      links: [
        { label: "Documentation", href: "#" },
        { label: "API Reference", href: "#" },
        { label: "GitHub", href: "https://github.com/orgs/VAREON-co/dashboard" },
      ],
    },
    {
      title: "Company",
      links: [
        { label: "About", href: "#" },
        { label: "Blog", href: "#" },
        { label: "Contact", href: "#" },
      ],
    },
  ];

  return (
    <footer className="border-t border-border bg-card">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-8 md:grid-cols-4">
          <div>
            <div className="mb-4 flex items-center space-x-2">
              <div className="flex h-8 w-8 items-center justify-center rounded bg-primary">
                <span className="text-sm font-bold text-primary-foreground">V</span>
              </div>
              <span className="text-xl font-bold text-foreground">VAREON</span>
            </div>
            <p className="mb-4 text-sm text-muted-foreground">
              Engineering Adaptive Intelligence for the modern enterprise.
            </p>
            <div className="flex space-x-4">
              <a href="https://github.com/muhammad-robitulloh" className="text-muted-foreground hover:text-foreground">
                <Github className="h-5 w-5" />
              </a>
              <a href="https://x.com/mrbtlhh?t=cw7vpkOcpoC0gzT3wlTMvw&s=09" className="text-muted-foreground hover:text-foreground">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="https://www.linkedin.com/in/muhammad-robitulloh" className="text-muted-foreground hover:text-foreground">
                <Linkedin className="h-5 w-5" />
              </a>
            </div>
          </div>

          {footerSections.map((section) => (
            <div key={section.title}>
              <h3 className="mb-4 text-sm font-semibold text-foreground">
                {section.title}
              </h3>
              <ul className="space-y-2">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <Link href={link.href}>
                      <a className="text-sm text-muted-foreground hover:text-foreground">
                        {link.label}
                      </a>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 border-t border-border pt-8">
          <p className="text-center text-sm text-muted-foreground">
            © {new Date().getFullYear()} VAREON. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
