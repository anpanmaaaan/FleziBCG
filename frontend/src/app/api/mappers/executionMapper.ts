import type { OperationExecutionStatus } from "../operationApi";

type StatusBadgeVariant = "success" | "warning" | "error" | "info" | "neutral";

export const mapExecutionStatusText = (status: OperationExecutionStatus): string => {
  switch (status) {
    case "PENDING":
      return "Pending";
    case "IN_PROGRESS":
      return "In Progress";
    case "COMPLETED":
      return "Completed";
    default:
      return String(status);
  }
};

export const mapExecutionStatusBadgeVariant = (
  status: OperationExecutionStatus,
): StatusBadgeVariant => {
  switch (status) {
    case "COMPLETED":
      return "success";
    case "IN_PROGRESS":
      return "info";
    case "PENDING":
      return "neutral";
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