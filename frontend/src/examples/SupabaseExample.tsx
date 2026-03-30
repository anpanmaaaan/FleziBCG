/**
 * EXAMPLE: How to use Supabase in MES Lite
 * 
 * This file demonstrates different ways to interact with the database
 */

import { useEffect, useState } from 'react';
import { supabase, callServer } from '/src/utils/supabase';
import type { ProductionOrder, ApiResponse } from '/src/types/database';

export function SupabaseExample() {
  const [productionOrders, setProductionOrders] = useState<ProductionOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ===========================
  // METHOD 1: Direct Supabase Query (Frontend)
  // ===========================
  async function fetchProductionOrdersDirect() {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('production_orders')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      setProductionOrders(data || []);
    } catch (err: any) {
      setError(err.message);
      console.error('Error fetching production orders:', err);
    } finally {
      setLoading(false);
    }
  }

  // ===========================
  // METHOD 2: Call Server API (Recommended)
  // ===========================
  async function fetchProductionOrdersViaServer() {
    try {
      setLoading(true);
      const response: ApiResponse<ProductionOrder[]> = await callServer('/production-orders');
      
      if (response.success && response.data) {
        setProductionOrders(response.data);
      } else {
        throw new Error(response.error || 'Unknown error');
      }
    } catch (err: any) {
      setError(err.message);
      console.error('Error fetching production orders:', err);
    } finally {
      setLoading(false);
    }
  }

  // ===========================
  // CREATE: Add New Production Order
  // ===========================
  async function createProductionOrder() {
    try {
      const newOrder: ProductionOrder = {
        id: 'PO-' + Date.now(),
        product_id: 'PROD-001',
        product_name: 'Widget A',
        quantity: 100,
        route_id: 'ROUTE-001',
        priority: 'High',
        status: 'Planned',
        notes: 'Created from example',
      };

      const response: ApiResponse<ProductionOrder> = await callServer('/production-orders', {
        method: 'POST',
        body: JSON.stringify(newOrder),
      });

      if (response.success && response.data) {
        console.log('Created:', response.data);
        // Refresh list
        fetchProductionOrdersViaServer();
      }
    } catch (err: any) {
      console.error('Error creating production order:', err);
    }
  }

  // ===========================
  // UPDATE: Modify Production Order
  // ===========================
  async function updateProductionOrder(id: string) {
    try {
      const updates = {
        status: 'In Progress',
        actual_start_date: new Date().toISOString(),
      };

      const response: ApiResponse<ProductionOrder> = await callServer(`/production-orders/${id}`, {
        method: 'PUT',
        body: JSON.stringify(updates),
      });

      if (response.success) {
        console.log('Updated:', response.data);
        // Refresh list
        fetchProductionOrdersViaServer();
      }
    } catch (err: any) {
      console.error('Error updating production order:', err);
    }
  }

  // ===========================
  // DELETE: Remove Production Order
  // ===========================
  async function deleteProductionOrder(id: string) {
    try {
      const response = await callServer(`/production-orders/${id}`, {
        method: 'DELETE',
      });

      if (response.success) {
        console.log('Deleted:', id);
        // Refresh list
        fetchProductionOrdersViaServer();
      }
    } catch (err: any) {
      console.error('Error deleting production order:', err);
    }
  }

  // ===========================
  // REAL-TIME SUBSCRIPTION (Optional)
  // ===========================
  useEffect(() => {
    // Subscribe to real-time changes
    const channel = supabase
      .channel('production_orders_changes')
      .on(
        'postgres_changes',
        {
          event: '*', // Listen to all events (INSERT, UPDATE, DELETE)
          schema: 'public',
          table: 'production_orders',
        },
        (payload) => {
          console.log('Real-time change detected:', payload);
          // Refresh data when changes occur
          fetchProductionOrdersViaServer();
        }
      )
      .subscribe();

    // Cleanup subscription on unmount
    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  // Load data on mount
  useEffect(() => {
    fetchProductionOrdersViaServer();
  }, []);

  // ===========================
  // RENDER
  // ===========================
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Supabase Integration Example</h1>

      {/* Actions */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={fetchProductionOrdersDirect}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Fetch Direct
        </button>
        <button
          onClick={fetchProductionOrdersViaServer}
          className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Fetch via Server
        </button>
        <button
          onClick={createProductionOrder}
          className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
        >
          Create New
        </button>
      </div>

      {/* Status */}
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">Error: {error}</p>}

      {/* Data */}
      <div className="space-y-2">
        {productionOrders.map((order) => (
          <div key={order.id} className="p-4 border rounded flex justify-between items-center">
            <div>
              <h3 className="font-bold">{order.product_name}</h3>
              <p className="text-sm text-gray-600">
                {order.id} - Qty: {order.quantity} - Status: {order.status}
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => updateProductionOrder(order.id)}
                className="px-3 py-1 bg-yellow-500 text-white rounded text-sm hover:bg-yellow-600"
              >
                Update
              </button>
              <button
                onClick={() => deleteProductionOrder(order.id)}
                className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
