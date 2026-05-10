import { HttpError } from "@/app/api";

export type StationCommandErrorSeverity = "warning" | "danger";

export interface StationCommandErrorMessage {
  code: string;
  titleKey: string;
  messageKey: string;
  recoveryKey: string;
  severity: StationCommandErrorSeverity;
}

type StationCommandErrorTemplate = Omit<StationCommandErrorMessage, "code">;

const FALLBACK_ERROR: StationCommandErrorTemplate = {
  titleKey: "station.commandError.fallback.title",
  messageKey: "station.commandError.fallback.message",
  recoveryKey: "station.commandError.fallback.recovery",
  severity: "warning",
};

const ERROR_MAP: Record<string, StationCommandErrorTemplate> = {
  STATION_SESSION_REQUIRED: {
    titleKey: "station.commandError.sessionRequired.title",
    messageKey: "station.commandError.sessionRequired.message",
    recoveryKey: "station.commandError.sessionRequired.recovery",
    severity: "warning",
  },
  STATION_SESSION_OPERATOR_MISMATCH: {
    titleKey: "station.commandError.operatorMismatch.title",
    messageKey: "station.commandError.operatorMismatch.message",
    recoveryKey: "station.commandError.operatorMismatch.recovery",
    severity: "warning",
  },
  STATION_SESSION_STATION_MISMATCH: {
    titleKey: "station.commandError.stationMismatch.title",
    messageKey: "station.commandError.stationMismatch.message",
    recoveryKey: "station.commandError.stationMismatch.recovery",
    severity: "warning",
  },
  STATION_SESSION_CLOSED: {
    titleKey: "station.commandError.sessionClosed.title",
    messageKey: "station.commandError.sessionClosed.message",
    recoveryKey: "station.commandError.sessionClosed.recovery",
    severity: "warning",
  },
  AUTH_SCOPE_FAIL: {
    titleKey: "station.commandError.permission.title",
    messageKey: "station.commandError.permission.message",
    recoveryKey: "station.commandError.permission.recovery",
    severity: "danger",
  },
  OPERATION_CLOSED: {
    titleKey: "station.commandError.operationClosed.title",
    messageKey: "station.commandError.operationClosed.message",
    recoveryKey: "station.commandError.operationClosed.recovery",
    severity: "danger",
  },
  STATE_CLOSED_RECORD: {
    titleKey: "station.commandError.operationClosed.title",
    messageKey: "station.commandError.operationClosed.message",
    recoveryKey: "station.commandError.operationClosed.recovery",
    severity: "danger",
  },
  OPERATION_QUALITY_HOLD_OPEN: {
    titleKey: "station.commandError.qualityHold.title",
    messageKey: "station.commandError.qualityHold.message",
    recoveryKey: "station.commandError.qualityHold.recovery",
    severity: "danger",
  },
  STATE_QC_HOLD_ACTIVE: {
    titleKey: "station.commandError.qualityHold.title",
    messageKey: "station.commandError.qualityHold.message",
    recoveryKey: "station.commandError.qualityHold.recovery",
    severity: "danger",
  },
  EQUIPMENT_REQUIRED: {
    titleKey: "station.commandError.equipmentRequired.title",
    messageKey: "station.commandError.equipmentRequired.message",
    recoveryKey: "station.commandError.equipmentRequired.recovery",
    severity: "warning",
  },
  EQUIPMENT_MISMATCH: {
    titleKey: "station.commandError.equipmentMismatch.title",
    messageKey: "station.commandError.equipmentMismatch.message",
    recoveryKey: "station.commandError.equipmentMismatch.recovery",
    severity: "warning",
  },
  STATION_SESSION_ACTIVE_EXECUTION: {
    titleKey: "station.commandError.sessionActiveExecution.title",
    messageKey: "station.commandError.sessionActiveExecution.message",
    recoveryKey: "station.commandError.sessionActiveExecution.recovery",
    severity: "warning",
  },
};

const KNOWN_CODE_PATTERN = /^(STATION_SESSION_[A-Z_]+|AUTH_SCOPE_FAIL|OPERATION_CLOSED|STATE_CLOSED_RECORD|OPERATION_QUALITY_HOLD_OPEN|STATE_QC_HOLD_ACTIVE|EQUIPMENT_REQUIRED|EQUIPMENT_MISMATCH)$/;

function readString(value: unknown): string | null {
  return typeof value === "string" && value.trim().length > 0 ? value.trim() : null;
}

function extractErrorCode(error: unknown): { code: string | null; status?: number } {
  if (error instanceof HttpError) {
    return {
      code: readString(error.detail) ?? readString(error.message),
      status: error.status,
    };
  }

  if (typeof error === "object" && error !== null) {
    const candidate = error as {
      code?: unknown;
      detail?: unknown;
      message?: unknown;
      status?: unknown;
    };

    return {
      code: readString(candidate.code) ?? readString(candidate.detail) ?? readString(candidate.message),
      status: typeof candidate.status === "number" ? candidate.status : undefined,
    };
  }

  return { code: null };
}

function normalizeKnownCode(rawCode: string, status?: number): string {
  const code = rawCode.trim().toUpperCase();

  if (ERROR_MAP[code]) {
    return code;
  }

  if (code === "FORBIDDEN" || code === "AUTH_SCOPE_FAIL" || status === 403) {
    return "AUTH_SCOPE_FAIL";
  }

  if (code === "STATION IS OUTSIDE YOUR STATION SCOPE") {
    return "AUTH_SCOPE_FAIL";
  }

  if (code === "OPERATION_CLOSED" || code === "STATE_CLOSED_RECORD" || code === "STATE_CLOSED" || code.includes("CLOSED_RECORD")) {
    return "STATE_CLOSED_RECORD";
  }

  if (code === "STATION SESSION IS CLOSED" || code === "STATION SESSION IS ALREADY CLOSED") {
    return "STATION_SESSION_CLOSED";
  }

  if (code === "STATION_SESSION_ACTIVE_EXECUTION") {
    return "STATION_SESSION_ACTIVE_EXECUTION";
  }

  if (code === "EQUIPMENT_REQUIRED" || code.includes("EQUIPMENT") && code.includes("REQUIRED")) {
    return "EQUIPMENT_REQUIRED";
  }

  if (code === "EQUIPMENT_MISMATCH" || code.includes("EQUIPMENT") && code.includes("MISMATCH")) {
    return "EQUIPMENT_MISMATCH";
  }

  if (code === "OPERATION_QUALITY_HOLD_OPEN" || code === "STATE_QC_HOLD_ACTIVE" || code.includes("QC_HOLD")) {
    return "OPERATION_QUALITY_HOLD_OPEN";
  }

  if (
    code === "STATION_SESSION_REQUIRED" ||
    code === "STATION_SESSION_OPERATOR_MISMATCH" ||
    code === "STATION_SESSION_STATION_MISMATCH" ||
    code === "STATION_SESSION_CLOSED"
  ) {
    return code;
  }

  if (status === 409 && KNOWN_CODE_PATTERN.test(code)) {
    return code;
  }

  return "";
}

export function normalizeStationCommandError(error: unknown): StationCommandErrorMessage {
  const { code: rawCode, status } = extractErrorCode(error);
  const code = rawCode ? normalizeKnownCode(rawCode, status) : "";
  const template = code && ERROR_MAP[code] ? ERROR_MAP[code] : FALLBACK_ERROR;

  return {
    code: code || rawCode || "UNKNOWN",
    ...template,
  };
}
