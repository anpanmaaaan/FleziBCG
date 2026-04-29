import { StatusBadge } from "./StatusBadge";

interface RoutingLifecycleBadgeProps {
  status: string | null | undefined;
}

interface RoutingOperationSequenceBadgeProps {
  sequence: number;
}

interface BackendRequiredNoticeProps {
  message: string;
  tone?: "amber" | "blue";
}

export function RoutingLifecycleBadge({ status }: RoutingLifecycleBadgeProps) {
  const normalized = (status || "").trim().toUpperCase();

  let variant: "success" | "warning" | "error" | "neutral" = "neutral";
  if (normalized === "RELEASED") variant = "success";
  else if (normalized === "DRAFT") variant = "warning";
  else if (normalized === "RETIRED") variant = "error";

  return (
    <StatusBadge variant={variant} size="sm">
      {status || "-"}
    </StatusBadge>
  );
}

export function RoutingOperationSequenceBadge({ sequence }: RoutingOperationSequenceBadgeProps) {
  return (
    <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-xs font-semibold text-slate-700">
      Seq {sequence}
    </span>
  );
}

export function BackendRequiredNotice({ message, tone = "amber" }: BackendRequiredNoticeProps) {
  const palette =
    tone === "blue"
      ? "border-blue-200 bg-blue-50 text-blue-900"
      : "border-amber-200 bg-amber-50 text-amber-900";

  return <div className={`mb-4 rounded-lg border px-4 py-3 text-sm ${palette}`}>{message}</div>;
}
