import { cx } from "@/lib/utils";

export function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={cx(
        "rounded-pill border px-3.5 py-1.5 text-[12px] font-semibold transition-colors duration-150",
        active ? "border-dark bg-dark text-white" : "border-border bg-surface text-text hover:bg-black/[0.03]"
      )}
    >
      {children}
    </button>
  );
}
