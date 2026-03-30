import { Hono } from "npm:hono";
import { cors } from "npm:hono/cors";
import { logger } from "npm:hono/logger";
import * as kv from "./kv_store.tsx";
import * as db from "./db.tsx";

const app = new Hono();

// Enable logger
app.use('*', logger(console.log));

// Enable CORS for all routes and methods
app.use(
  "/*",
  cors({
    origin: "*",
    allowHeaders: ["Content-Type", "Authorization"],
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    exposeHeaders: ["Content-Length"],
    maxAge: 600,
  }),
);

// Health check endpoint
app.get("/make-server-380ff3c6/health", (c) => {
  return c.json({ status: "ok", timestamp: new Date().toISOString() });
});

// ===========================
// PRODUCTION ORDERS ENDPOINTS
// ===========================

// Get all production orders
app.get("/make-server-380ff3c6/production-orders", async (c) => {
  try {
    const data = await db.getAllProductionOrders();
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error fetching production orders:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get production order by ID
app.get("/make-server-380ff3c6/production-orders/:id", async (c) => {
  try {
    const id = c.req.param('id');
    const data = await db.getProductionOrderById(id);
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error fetching production order:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Create production order
app.post("/make-server-380ff3c6/production-orders", async (c) => {
  try {
    const body = await c.req.json();
    const data = await db.createProductionOrder(body);
    return c.json({ success: true, data }, 201);
  } catch (error) {
    console.error('Error creating production order:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Update production order
app.put("/make-server-380ff3c6/production-orders/:id", async (c) => {
  try {
    const id = c.req.param('id');
    const body = await c.req.json();
    const data = await db.updateProductionOrder(id, body);
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error updating production order:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Delete production order
app.delete("/make-server-380ff3c6/production-orders/:id", async (c) => {
  try {
    const id = c.req.param('id');
    const result = await db.deleteProductionOrder(id);
    return c.json({ success: true, data: result });
  } catch (error) {
    console.error('Error deleting production order:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// ===========================
// ROUTES ENDPOINTS
// ===========================

// Get all routes
app.get("/make-server-380ff3c6/routes", async (c) => {
  try {
    const data = await db.getAllRoutes();
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error fetching routes:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get route by ID
app.get("/make-server-380ff3c6/routes/:id", async (c) => {
  try {
    const id = c.req.param('id');
    const data = await db.getRouteById(id);
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error fetching route:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get operations by route ID
app.get("/make-server-380ff3c6/routes/:id/operations", async (c) => {
  try {
    const id = c.req.param('id');
    const data = await db.getOperationsByRouteId(id);
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error fetching operations:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// ===========================
// STATIONS ENDPOINTS
// ===========================

// Get all stations
app.get("/make-server-380ff3c6/stations", async (c) => {
  try {
    const data = await db.getAllStations();
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error fetching stations:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get station by ID
app.get("/make-server-380ff3c6/stations/:id", async (c) => {
  try {
    const id = c.req.param('id');
    const data = await db.getStationById(id);
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error fetching station:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// ===========================
// EXECUTION ENDPOINTS
// ===========================

// Start execution
app.post("/make-server-380ff3c6/execution/start", async (c) => {
  try {
    const body = await c.req.json();
    const record = {
      ...body,
      status: 'Started',
      start_time: new Date().toISOString(),
    };
    const data = await db.createExecutionRecord(record);
    return c.json({ success: true, data }, 201);
  } catch (error) {
    console.error('Error starting execution:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Complete execution
app.post("/make-server-380ff3c6/execution/complete", async (c) => {
  try {
    const body = await c.req.json();
    const { execution_id, ...updates } = body;
    const data = await db.updateExecutionRecord(execution_id, {
      ...updates,
      status: 'Completed',
      end_time: new Date().toISOString(),
    });
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error completing execution:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get executions by station
app.get("/make-server-380ff3c6/execution/station/:stationId", async (c) => {
  try {
    const stationId = c.req.param('stationId');
    const data = await db.getExecutionRecordsByStation(stationId);
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error fetching executions:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// ===========================
// QUALITY ENDPOINTS
// ===========================

// Submit QC result
app.post("/make-server-380ff3c6/quality/result", async (c) => {
  try {
    const body = await c.req.json();
    const data = await db.createQualityResult(body);
    return c.json({ success: true, data }, 201);
  } catch (error) {
    console.error('Error creating quality result:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get QC results by execution
app.get("/make-server-380ff3c6/quality/execution/:executionId", async (c) => {
  try {
    const executionId = c.req.param('executionId');
    const data = await db.getQualityResultsByExecution(executionId);
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error fetching quality results:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// ===========================
// DEFECTS ENDPOINTS
// ===========================

// Create defect
app.post("/make-server-380ff3c6/defects", async (c) => {
  try {
    const body = await c.req.json();
    const data = await db.createDefect(body);
    return c.json({ success: true, data }, 201);
  } catch (error) {
    console.error('Error creating defect:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Get all defects
app.get("/make-server-380ff3c6/defects", async (c) => {
  try {
    const data = await db.getAllDefects();
    return c.json({ success: true, data });
  } catch (error) {
    console.error('Error fetching defects:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// ===========================
// KV STORE ENDPOINTS (Optional - for flexible storage)
// ===========================

// Get from KV store
app.get("/make-server-380ff3c6/kv/:key", async (c) => {
  try {
    const key = c.req.param('key');
    const value = await kv.get(key);
    return c.json({ success: true, data: value });
  } catch (error) {
    console.error('Error getting from KV store:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

// Set in KV store
app.post("/make-server-380ff3c6/kv/:key", async (c) => {
  try {
    const key = c.req.param('key');
    const body = await c.req.json();
    await kv.set(key, body);
    return c.json({ success: true });
  } catch (error) {
    console.error('Error setting in KV store:', error);
    return c.json({ success: false, error: error.message }, 500);
  }
});

Deno.serve(app.fetch);
