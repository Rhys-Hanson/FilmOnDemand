const trimTrailingSlash = (value: string) => value.replace(/\/+$/, '');

const getWindowOrigin = () =>
  typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000';

const getEnvValue = (value: string | undefined) => {
  if (!value) return undefined;
  const trimmed = value.trim();
  return trimmed ? trimTrailingSlash(trimmed) : undefined;
};

const appUrl = getEnvValue(import.meta.env.VITE_APP_URL) ?? getWindowOrigin();
const apiBaseUrl =
  getEnvValue(import.meta.env.VITE_API_BASE_URL) ??
  getEnvValue(import.meta.env.VITE_BACKEND_URL)?.concat('/api') ??
  'http://localhost:8000/api';

const backendOrigin = apiBaseUrl.endsWith('/api')
  ? apiBaseUrl.slice(0, -4)
  : apiBaseUrl;

const wsBaseUrl =
  getEnvValue(import.meta.env.VITE_WS_BASE_URL) ??
  backendOrigin.replace(/^http/i, 'ws');

export const APP_URL = appUrl;
export const API_BASE_URL = apiBaseUrl;
export const ROOMS_API_URL = `${API_BASE_URL}/rooms`;
export const WS_ROOMS_URL = `${wsBaseUrl}/ws/rooms`;
export const getRoomJoinUrl = (roomCode: string) => `${APP_URL}/join/${roomCode}`;
