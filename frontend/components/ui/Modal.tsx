"use client";

import { useEffect, type ReactNode } from "react";

export function Modal({
  open,
  onClose,
  children,
  widthClassName = "max-w-[560px]",
}: {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  widthClassName?: string;
}) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="animate-overlay-in fixed inset-0 z-[400] flex items-center justify-center bg-[#0F1E33]/55 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Pump details"
        className={`animate-modal-in scroll-thin w-full ${widthClassName} max-h-[88vh] overflow-y-auto rounded-squircle-xl bg-surface p-7 shadow-elevated`}
      >
        {children}
      </div>
    </div>
  );
}
