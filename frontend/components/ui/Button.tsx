import type { ButtonHTMLAttributes } from "react";
import { cx } from "@/lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
  size?: "sm" | "md";
}

export function Button({ variant = "primary", size = "md", className, ...rest }: ButtonProps) {
  return (
    <button
      className={cx(
        "inline-flex items-center justify-center rounded-md font-semibold transition-all duration-150 ease-out active:scale-[0.97]",
        size === "md" ? "px-4 py-2 text-[13px]" : "px-3 py-1.5 text-[12px]",
        variant === "primary"
          ? "bg-primary text-white shadow-sm hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-50"
          : "bg-card border border-border text-foreground hover:bg-accent",
        className
      )}
      {...rest}
    />
  );
}
