import { createClient } from '@supabase/supabase-js';
import { projectId, publicAnonKey } from '/utils/supabase/info';

// Supabase client for frontend
export const supabase = createClient(
  `https://${projectId}.supabase.co`,
  publicAnonKey
);

// Server API base URL
export const API_BASE_URL = `https://${projectId}.supabase.co/functions/v1/make-server-380ff3c6`;

// Helper function to make API calls to server
export async function callServer(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${publicAnonKey}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`Server error on ${endpoint}:`, errorText);
    throw new Error(`Server error: ${response.status} - ${errorText}`);
  }

  return response.json();
}
