export type StationWorkflowStageId =
  | "STX_000_STATION_ENTRY"
  | "STX_001_STATION_SESSION"
  | "STX_002_OPERATOR_IDENTIFICATION"
  | "STX_003_EQUIPMENT_BINDING"
  | "STX_004_QUEUE_COCKPIT"
  | "STX_005_ACTIVE_OPERATION"
  | "STX_006_RUNTIME_VISIBILITY"
  | "STX_007_COMPLETION"
  | "STX_008_SUPERVISOR_REVIEW"
  | "STX_009_END_SESSION";

export interface StationWorkflowStage {
  id: StationWorkflowStageId;
  labelKey: string;
  supervisorOnly?: boolean;
}

export const STATION_WORKFLOW_STAGES: StationWorkflowStage[] = [
  { id: "STX_000_STATION_ENTRY", labelKey: "station.workflow.stage.STX_000_STATION_ENTRY" },
  { id: "STX_001_STATION_SESSION", labelKey: "station.workflow.stage.STX_001_STATION_SESSION" },
  { id: "STX_002_OPERATOR_IDENTIFICATION", labelKey: "station.workflow.stage.STX_002_OPERATOR_IDENTIFICATION" },
  { id: "STX_003_EQUIPMENT_BINDING", labelKey: "station.workflow.stage.STX_003_EQUIPMENT_BINDING" },
  { id: "STX_004_QUEUE_COCKPIT", labelKey: "station.workflow.stage.STX_004_QUEUE_COCKPIT" },
  { id: "STX_005_ACTIVE_OPERATION", labelKey: "station.workflow.stage.STX_005_ACTIVE_OPERATION" },
  { id: "STX_006_RUNTIME_VISIBILITY", labelKey: "station.workflow.stage.STX_006_RUNTIME_VISIBILITY" },
  { id: "STX_007_COMPLETION", labelKey: "station.workflow.stage.STX_007_COMPLETION" },
  {
    id: "STX_008_SUPERVISOR_REVIEW",
    labelKey: "station.workflow.stage.STX_008_SUPERVISOR_REVIEW",
    supervisorOnly: true,
  },
  { id: "STX_009_END_SESSION", labelKey: "station.workflow.stage.STX_009_END_SESSION" },
];
