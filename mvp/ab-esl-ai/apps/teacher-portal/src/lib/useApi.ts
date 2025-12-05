'use client';

import { useState, useCallback } from 'react';

interface ApiState<T> {
    data: T | null;
    loading: boolean;
    error: string | null;
}

interface UseApiOptions {
    onSuccess?: (data: unknown) => void;
    onError?: (error: string) => void;
}

/**
 * Custom hook for making API calls with loading, error, and success states.
 * Provides centralized error handling and automatic state management.
 */
export function useApi<T = unknown>(options: UseApiOptions = {}) {
    const [state, setState] = useState<ApiState<T>>({
        data: null,
        loading: false,
        error: null,
    });

    const execute = useCallback(
        async (apiCall: () => Promise<T>): Promise<T | null> => {
            setState((prev) => ({ ...prev, loading: true, error: null }));

            try {
                const data = await apiCall();
                setState({ data, loading: false, error: null });
                options.onSuccess?.(data);
                return data;
            } catch (err) {
                const errorMessage = getErrorMessage(err);
                setState((prev) => ({ ...prev, loading: false, error: errorMessage }));
                options.onError?.(errorMessage);
                return null;
            }
        },
        [options]
    );

    const reset = useCallback(() => {
        setState({ data: null, loading: false, error: null });
    }, []);

    return {
        ...state,
        execute,
        reset,
    };
}

/**
 * Extract a user-friendly error message from various error types.
 */
function getErrorMessage(error: unknown): string {
    if (error instanceof Error) {
        // Handle specific error types
        if (error.name === 'AbortError') {
            return 'Request was cancelled';
        }
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            return 'Unable to connect to server. Please check your internet connection.';
        }
        return error.message;
    }

    if (typeof error === 'string') {
        return error;
    }

    if (error && typeof error === 'object' && 'message' in error) {
        return String((error as { message: unknown }).message);
    }

    return 'An unexpected error occurred';
}

/**
 * Enhanced fetch wrapper with automatic error handling and retries.
 */
export async function apiFetch<T>(
    url: string,
    options: RequestInit = {},
    retries: number = 1
): Promise<T> {
    const defaultHeaders: HeadersInit = {
        'Content-Type': 'application/json',
    };

    const config: RequestInit = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                // Try to parse error response
                let errorMessage = `Request failed with status ${response.status}`;
                try {
                    const errorData = await response.json();
                    if (errorData.detail) {
                        errorMessage = errorData.detail;
                    } else if (errorData.message) {
                        errorMessage = errorData.message;
                    } else if (errorData.error) {
                        errorMessage = errorData.error;
                    }
                } catch {
                    // If we can't parse JSON, use status text
                    errorMessage = response.statusText || errorMessage;
                }

                throw new Error(errorMessage);
            }

            // Handle empty responses
            const contentType = response.headers.get('content-type');
            if (contentType?.includes('application/json')) {
                return await response.json();
            }

            return (await response.text()) as T;
        } catch (error) {
            lastError = error instanceof Error ? error : new Error(String(error));

            // Don't retry on certain errors
            if (
                error instanceof Error &&
                (error.name === 'AbortError' ||
                    error.message.includes('400') ||
                    error.message.includes('401') ||
                    error.message.includes('403') ||
                    error.message.includes('404'))
            ) {
                throw error;
            }

            // Wait before retrying (exponential backoff)
            if (attempt < retries) {
                await new Promise((resolve) => setTimeout(resolve, Math.pow(2, attempt) * 1000));
            }
        }
    }

    throw lastError || new Error('Request failed after retries');
}

/**
 * Hook to check online status and handle offline scenarios.
 */
export function useOnlineStatus() {
    const [isOnline, setIsOnline] = useState(
        typeof window !== 'undefined' ? navigator.onLine : true
    );

    if (typeof window !== 'undefined') {
        window.addEventListener('online', () => setIsOnline(true));
        window.addEventListener('offline', () => setIsOnline(false));
    }

    return isOnline;
}
