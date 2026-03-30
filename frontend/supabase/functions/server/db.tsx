import { createClient } from "jsr:@supabase/supabase-js@2.49.8";

const getClient = () => createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

// ===========================
// PRODUCTION ORDERS
// ===========================
export async function getAllProductionOrders() {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('production_orders')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

export async function getProductionOrderById(id: string) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('production_orders')
    .select('*')
    .eq('id', id)
    .single();

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

export async function createProductionOrder(order: any) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('production_orders')
    .insert(order)
    .select()
    .single();

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

export async function updateProductionOrder(id: string, updates: any) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('production_orders')
    .update({
      ...updates,
      updated_at: new Date().toISOString()
    })
    .eq('id', id)
    .select()
    .single();

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

export async function deleteProductionOrder(id: string) {
  const supabase = getClient();
  const { error } = await supabase
    .from('production_orders')
    .delete()
    .eq('id', id);

  if (error) throw new Error(`Database error: ${error.message}`);
  return { success: true };
}

// ===========================
// ROUTES
// ===========================
export async function getAllRoutes() {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('routes')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

export async function getRouteById(id: string) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('routes')
    .select('*')
    .eq('id', id)
    .single();

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

// ===========================
// OPERATIONS
// ===========================
export async function getOperationsByRouteId(routeId: string) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('operations')
    .select('*')
    .eq('route_id', routeId)
    .order('sequence', { ascending: true });

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

export async function getOperationById(id: string) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('operations')
    .select('*')
    .eq('id', id)
    .single();

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

// ===========================
// STATIONS
// ===========================
export async function getAllStations() {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('stations')
    .select('*')
    .order('line_id', { ascending: true });

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

export async function getStationById(id: string) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('stations')
    .select('*')
    .eq('id', id)
    .single();

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

// ===========================
// EXECUTION RECORDS
// ===========================
export async function createExecutionRecord(record: any) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('execution_records')
    .insert(record)
    .select()
    .single();

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

export async function updateExecutionRecord(id: string, updates: any) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('execution_records')
    .update({
      ...updates,
      updated_at: new Date().toISOString()
    })
    .eq('id', id)
    .select()
    .single();

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

export async function getExecutionRecordsByStation(stationId: string) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('execution_records')
    .select('*')
    .eq('station_id', stationId)
    .order('created_at', { ascending: false });

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

// ===========================
// QUALITY
// ===========================
export async function createQualityResult(result: any) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('quality_results')
    .insert(result)
    .select()
    .single();

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

export async function getQualityResultsByExecution(executionId: string) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('quality_results')
    .select('*, quality_checkpoints(*)')
    .eq('execution_record_id', executionId);

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

// ===========================
// DEFECTS
// ===========================
export async function createDefect(defect: any) {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('defects')
    .insert(defect)
    .select()
    .single();

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}

export async function getAllDefects() {
  const supabase = getClient();
  const { data, error } = await supabase
    .from('defects')
    .select('*')
    .order('detected_at', { ascending: false });

  if (error) throw new Error(`Database error: ${error.message}`);
  return data;
}
