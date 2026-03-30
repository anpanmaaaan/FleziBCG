// Database Types for MES Lite Universal Manufacturing

export interface ProductionOrder {
  id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  route_id: string;
  priority: 'Low' | 'Medium' | 'High' | 'Urgent';
  status: 'Planned' | 'Released' | 'In Progress' | 'Completed' | 'On Hold' | 'Cancelled';
  target_start_date?: string;
  target_end_date?: string;
  actual_start_date?: string;
  actual_end_date?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Route {
  id: string;
  name: string;
  version: string;
  product_id?: string;
  status: 'Active' | 'Inactive' | 'Draft';
  description?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Operation {
  id: string;
  route_id: string;
  sequence: number;
  name: string;
  station_id: string;
  station_name: string;
  cycle_time?: number; // seconds
  status: 'Pending' | 'In Progress' | 'Completed' | 'Blocked' | 'Skipped';
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Station {
  id: string;
  name: string;
  line_id: string;
  line_name: string;
  type?: string;
  status: 'Available' | 'Occupied' | 'Maintenance' | 'Offline';
  created_at?: string;
  updated_at?: string;
}

export interface ExecutionRecord {
  id: string;
  production_order_id: string;
  operation_id: string;
  station_id: string;
  operator_id?: string;
  operator_name?: string;
  status: 'Started' | 'Paused' | 'Completed' | 'Failed';
  start_time?: string;
  end_time?: string;
  quantity_completed?: number;
  quantity_rejected?: number;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface QualityCheckpoint {
  id: string;
  operation_id: string;
  checkpoint_name: string;
  checkpoint_type: 'Dimensional' | 'Visual' | 'Functional' | 'Other';
  specification?: string;
  is_mandatory: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface QualityResult {
  id: string;
  execution_record_id: string;
  checkpoint_id: string;
  result: 'Pass' | 'Fail' | 'NA';
  measured_value?: string;
  inspector_id?: string;
  inspector_name?: string;
  timestamp?: string;
  notes?: string;
  created_at?: string;
}

export interface Defect {
  id: string;
  production_order_id?: string;
  operation_id?: string;
  defect_code: string;
  defect_name: string;
  category?: string;
  severity: 'Critical' | 'Major' | 'Minor';
  quantity: number;
  detected_by?: string;
  detected_at?: string;
  status: 'Open' | 'In Review' | 'Resolved' | 'Closed';
  resolution?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Material {
  id: string;
  material_code: string;
  material_name: string;
  material_type?: string;
  unit_of_measure?: string;
  current_stock?: number;
  min_stock?: number;
  max_stock?: number;
  created_at?: string;
  updated_at?: string;
}

export interface MaterialConsumption {
  id: string;
  execution_record_id: string;
  material_id: string;
  quantity_used: number;
  lot_number?: string;
  consumed_at?: string;
  created_at?: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}
