/**
 * API Client for Finance Assistant Backend
 * Uses Vite proxy to avoid CORS issues (/api -> localhost:8001)
 */

// Use proxy path in development, direct URL in production
const API_BASE_URL = '/api';

export interface ApiResponse<T> {
    data?: T;
    error?: string;
}

/**
 * Base fetch wrapper with error handling
 */
async function fetchApi<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<ApiResponse<T>> {
    try {
        const url = `${API_BASE_URL}${endpoint}`;
        const response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
            },
        });

        const data = await response.json();

        if (data.error) {
            return { error: data.error };
        }

        return { data };
    } catch (error) {
        console.error('API Error:', error);
        return { error: error instanceof Error ? error.message : 'Unknown error occurred' };
    }
}

/**
 * GET request helper
 */
export async function get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return fetchApi<T>(endpoint, { method: 'GET' });
}

/**
 * POST request helper (JSON body)
 */
export async function post<T>(endpoint: string, body: object): Promise<ApiResponse<T>> {
    return fetchApi<T>(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
    });
}

/**
 * POST request helper (FormData for file uploads)
 */
export async function postFormData<T>(endpoint: string, formData: FormData): Promise<ApiResponse<T>> {
    return fetchApi<T>(endpoint, {
        method: 'POST',
        body: formData,
    });
}

/**
 * Get audio file URL
 */
export function getAudioUrl(filename: string): string {
    return `${API_BASE_URL}/audio/${filename}`;
}

export { API_BASE_URL };
