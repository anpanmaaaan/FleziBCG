import type { OperationExecutionStatus } from "@/app/api/operationApi";

type StatusBadgeVariant = "success" | "warning" | "error" | "info" | "neutral";

export const mapExecutionStatusText = (status: OperationExecutionStatus): string => {
  const normalizedStatus = String(status).toUpperCase();
  switch (normalizedStatus) {
    case "PLANNED":
      return "station.status.planned";
    case "IN_PROGRESS":
      return "station.status.inProgress";
    case "PAUSED":
      return "station.status.paused";
    case "BLOCKED":
      return "station.status.blocked";
    case "COMPLETED":
      return "station.status.completed";
    case "ABORTED":
      return "station.status.aborted";
    default:
      // Fall back to a safe existing i18n key so the badge never renders a raw
      // status token. Callers that need exact rendering should pre-check.
      return "station.status.planned";
  }
};

export const mapExecutionStatusBadgeVariant = (
  status: OperationExecutionStatus,
): StatusBadgeVariant => {
  const normalizedStatus = String(status).toUpperCase();

  switch (normalizedStatus) {
    case "COMPLETED":
      return "success";
    case "IN_PROGRESS":
      return "info";
    case "PAUSED":
      return "warning";
    case "BLOCKED":
      return "error";
    case "PLANNED":
      return "neutral";
    case "ABORTED":
      return "error";
    default:
      return "warning";
  }
};

export const getProgressPercentage = (input: {
  completedQty: number;
  targetQty: number;
}): number => {
  if (input.targetQty <= 0) {
    return 0;
  }

  const ratio = (input.completedQty / input.targetQty) * 100;
  return Math.max(0, Math.min(100, Math.round(ratio)));
};

export const getYieldRate = (input: {
  goodQty: number;
  completedQty: number;
}): number => {
  if (input.completedQty <= 0) {
    return 0;
  }

  const ratio = (input.goodQty / input.completedQty) * 100;
  return Math.max(0, Math.min(100, Number(ratio.toFixed(2))));
};