
import { useAuth } from '@/hooks/use-auth';

// Helper function to get the auth token
const getToken = (): string | null => {
  // useAuth hook cannot be used here as this is not a component.
  // We need to get the token directly from where it's stored.
  // Based on use-auth.ts, the key is "access_token".
  return localStorage.getItem('access_token');
};

// Custom Error class for API responses
class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

const request = async (
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
  url: string,
  body: Record<string, any> | null = null
) => {
  const token = getToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config: RequestInit = {
    method,
    headers,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(url, config);

  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch (e) {
      errorData = { detail: 'An unknown error occurred.' };
    }
    throw new ApiError(
      errorData.detail || `Request failed with status ${response.status}`,
      response.status,
      errorData
    );
  }

  // Handle cases with no content in response
  if (response.status === 204) {
    return null;
  }

  return response.json();
};

export const api = {
  get: (url: string) => request('GET', url),
  post: (url: string, body: Record<string, any>) => request('POST', url, body),
  put: (url: string, body: Record<string, any>) => request('PUT', url, body),
  delete: (url: string) => request('DELETE', url),
};
