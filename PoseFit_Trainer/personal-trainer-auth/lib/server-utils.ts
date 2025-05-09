import { cookies } from 'next/headers';
import { BACKEND_URL } from './api-utils';

// Utility for handling API authorization
export async function getAuthToken() {
  const cookieStore = await cookies();
  return cookieStore.get('session')?.value;
}

// Generic API request handler with auth
export async function apiRequest<T>(url: string, options: RequestInit = {}): Promise<T> {
  const token = await getAuthToken();
  
  if (!token) {
    throw new Error('Unauthorized - No token found');
  }
  
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`
  };
  
  const response = await fetch(`${BACKEND_URL}${url}`, {
    ...options,
    headers
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.error || `Request failed with status ${response.status}`);
  }
  
  return data as T;
} 