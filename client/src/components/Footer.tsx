import React from "react";

export default function Footer() {
  return (
    <footer className="w-full border-t border-border bg-card py-6 text-center text-muted-foreground">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <p className="text-sm">
          &copy; {new Date().getFullYear()} VAREON. All rights reserved.
        </p>
        <p className="mt-2 text-xs">
          Built with Adaptive Intelligence and Multi-Agent Orchestration.
        </p>
      </div>
    </footer>
  );
}