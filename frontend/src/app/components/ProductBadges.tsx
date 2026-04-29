import { StatusBadge } from "./StatusBadge";

interface ProductBadgeProps {
  value: string | null | undefined;
}

const normalize = (value: string | null | undefined) => {
  return (value || "").trim().toUpperCase();
};

export function ProductLifecycleBadge({ value }: ProductBadgeProps) {
  const normalized = normalize(value);

  let variant: "success" | "warning" | "error" | "info" | "neutral" | "purple" | "cyan" = "neutral";

  if (normalized === "RELEASED" || normalized === "ACTIVE") {
    variant = "success";
  } else if (normalized === "DRAFT" || normalized === "INACTIVE") {
    variant = "warning";
  } else if (normalized === "RETIRED" || normalized === "OBSOLETE") {
    variant = "error";
  }

  return <StatusBadge variant={variant} size="sm">{value || "-"}</StatusBadge>;
}

export function ProductTypeBadge({ value }: ProductBadgeProps) {
  const normalized = normalize(value);

  let variant: "success" | "warning" | "error" | "info" | "neutral" | "purple" | "cyan" = "neutral";

  if (normalized === "MANUFACTURED") {
    variant = "info";
  } else if (normalized === "PURCHASED") {
    variant = "cyan";
  } else if (normalized === "ASSEMBLY") {
    variant = "purple";
  }

  return <StatusBadge variant={variant} size="sm">{value || "-"}</StatusBadge>;
}
