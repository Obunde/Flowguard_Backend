import type { HTMLAttributes, ReactNode } from "react";
import { cx } from "@/lib/utils";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  padded?: boolean;
  interactive?: boolean;
}

export function Card({ children, className, padded = true, interactive = false, ...rest }: CardProps) {
  return (
    <div
      className={cx(
        "bg-card border border-border rounded-xl shadow-sm",
        padded && "p-5",
        interactive && "transition-all duration-200 ease-out hover:shadow-md hover:border-primary cursor-pointer",
        className
      )}
      {...rest}
    >
      {children}
    </div>
  );
}
