import type { OperationExecutionStatus } from "../operationApi";

type StatusBadgeVariant = "success" | "warning" | "error" | "info" | "neutral";

export const mapExecutionStatusText = (status: OperationExecutionStatus): string => {
  const normalizedStatus = String(status).toUpperCase();

  switch (normalizedStatus) {
    case "PLANNED":
      // Current semantics: PLANNED is execution-pending for UI purposes.
      return "Pending";
    case "PENDING":
      return "Pending";
    case "IN_PROGRESS":
      return "In Progress";
    case "COMPLETED":
      return "Completed";
    case "COMPLETED_LATE":
      return "Completed Late";
    case "ABORTED":
      return "Aborted";
    case "BLOCKED":
      return "Blocked";
    case "LATE":
      return "Delayed";
    default:
      return String(status);
  }
};

export const mapExecutionStatusBadgeVariant = (
  status: OperationExecutionStatus,
): StatusBadgeVariant => {
  const normalizedStatus = String(status).toUpperCase();

  switch (normalizedStatus) {
    case "COMPLETED":
      return "success";
    case "COMPLETED_LATE":
      return "warning";
    case "IN_PROGRESS":
      return "info";
    case "PLANNED":
    case "PENDING":
      return "neutral";
    case "BLOCKED":
    case "ABORTED":
      return "error";
    case "LATE":
      return "warning";
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