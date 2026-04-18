import type { OperationExecutionStatus } from "@/app/api/operationApi";

type StatusBadgeVariant = "success" | "warning" | "error" | "info" | "neutral";

export const mapExecutionStatusText = (status: OperationExecutionStatus): string => {
  const normalizedStatus = String(status).toUpperCase();

  switch (normalizedStatus) {
    case "PLANNED":
      return "Planned";
    case "IN_PROGRESS":
      return "In Progress";
    case "COMPLETED":
      return "Completed";
    case "ABORTED":
      return "Aborted";
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
    case "IN_PROGRESS":
      return "info";
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