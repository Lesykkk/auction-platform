import axios, {
  AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig
} from "axios";

type TokenGetter = () => string | null;
type TokenSetter = (token: string | null) => void;
type UnauthorizedHandler = () => void;

let getAccessToken: TokenGetter = () => null;
let setAccessToken: TokenSetter = () => undefined;
let onUnauthorized: UnauthorizedHandler = () => undefined;
let refreshRequest: Promise<string> | null = null;

export const api: AxiosInstance = axios.create({
  baseURL: "/api/v1",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json"
  }
});

export const configureHttpAuth = (
  getter: TokenGetter,
  setter: TokenSetter,
  unauthorizedHandler: UnauthorizedHandler
) => {
  getAccessToken = getter;
  setAccessToken = setter;
  onUnauthorized = unauthorizedHandler;
};

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    const isAuthRoute = original?.url?.startsWith("/auth/login") || original?.url?.startsWith("/auth/refresh");

    if (error.response?.status !== 401 || !original || original._retry || isAuthRoute) {
      return Promise.reject(error);
    }

    original._retry = true;

    try {
      if (!refreshRequest) {
        refreshRequest = api
          .post("/auth/refresh")
          .then((response) => response.data.access_token as string)
          .finally(() => {
            refreshRequest = null;
          });
      }

      const token = await refreshRequest;
      setAccessToken(token);
      original.headers.Authorization = `Bearer ${token}`;
      return api(original);
    } catch (refreshError) {
      setAccessToken(null);
      onUnauthorized();
      return Promise.reject(refreshError);
    }
  }
);

export const getErrorMessage = (error: unknown) => {
  return getApiError(error).message;
};

export const compactParams = <T extends Record<string, unknown>>(params: T): Partial<T> =>
  Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== "")
  ) as Partial<T>;

export type ApiErrorInfo = {
  status?: number;
  message: string;
  details: string[];
  path?: string;
};

export const getApiError = (error: unknown): ApiErrorInfo => {
  if (!axios.isAxiosError(error)) {
    return {
      message: "Щось пішло не так. Спробуйте ще раз.",
      details: []
    };
  }

  const responseData = error.response?.data as
    | {
        message?: unknown;
        detail?: unknown;
        errors?: Array<{ field?: unknown; message?: unknown }>;
        path?: unknown;
      }
    | undefined;

  const status = error.response?.status;
  const path = typeof responseData?.path === "string" ? responseData.path : undefined;
  const details: string[] = [];

  if (Array.isArray(responseData?.errors)) {
    for (const item of responseData.errors) {
      const field = typeof item.field === "string" ? item.field : "";
      const message = typeof item.message === "string" ? item.message : "";
      if (message) {
        details.push(field ? `${field}: ${message}` : message);
      }
    }
  }

  const messageCandidates = [responseData?.message, responseData?.detail];
  const message = messageCandidates.find((candidate): candidate is string => typeof candidate === "string");

  return {
    status,
    message: message ?? (details.length > 0 ? details[0] : "Щось пішло не так. Спробуйте ще раз."),
    details,
    path
  };
};
