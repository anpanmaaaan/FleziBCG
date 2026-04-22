import { request } from "./httpClient";


export interface DowntimeReasonOption {
  reason_code: string;
  reason_name: string;
  reason_group: string;
  planned_flag: boolean;
  requires_comment: boolean;
  requires_supervisor_review: boolean;
}


export const fetchDowntimeReasons = () => {
  return request<DowntimeReasonOption[]>("/v1/downtime-reasons");
};