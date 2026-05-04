import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode
} from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { authApi } from "../api/auth";
import { configureHttpAuth } from "../api/http";
import { usersApi, type RegisterPayload, type UpdateMePayload } from "../api/users";
import type { User } from "../types";

type AuthContextValue = {
  accessToken: string | null;
  user: User | null;
  initializing: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  updateUser: (payload: UpdateMePayload) => Promise<void>;
  topUp: (amount: string) => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [initializing, setInitializing] = useState(true);
  const tokenRef = useRef<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  const setToken = useCallback((token: string | null) => {
    tokenRef.current = token;
    setAccessToken(token);
  }, []);

  useEffect(() => {
    configureHttpAuth(
      () => tokenRef.current,
      setToken,
      () => {
        setUser(null);
        if (!["/login", "/register"].includes(window.location.pathname)) {
          window.location.assign("/login");
        }
      }
    );
  }, [setToken]);

  const refreshUser = useCallback(async () => {
    const currentUser = await usersApi.me();
    setUser(currentUser);
  }, []);

  useEffect(() => {
    let active = true;

    const restoreSession = async () => {
      try {
        const tokenResponse = await authApi.refresh();
        if (!active) return;
        setToken(tokenResponse.access_token);
        const currentUser = await usersApi.me();
        if (active) setUser(currentUser);
      } catch {
        if (active) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (active) setInitializing(false);
      }
    };

    restoreSession();
    return () => {
      active = false;
    };
  }, [setToken]);

  const login = useCallback(
    async (username: string, password: string) => {
      const tokenResponse = await authApi.login({ username, password });
      setToken(tokenResponse.access_token);
      const currentUser = await usersApi.me();
      setUser(currentUser);
      navigate((location.state as { from?: string } | null)?.from ?? "/auctions");
    },
    [location.state, navigate, setToken]
  );

  const register = useCallback(
    async (payload: RegisterPayload) => {
      await usersApi.register(payload);
      await login(payload.username, payload.password);
    },
    [login]
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } finally {
      setToken(null);
      setUser(null);
      navigate("/login");
    }
  }, [navigate, setToken]);

  const updateUser = useCallback(async (payload: UpdateMePayload) => {
    const updated = await usersApi.updateMe(payload);
    setUser(updated);
  }, []);

  const topUp = useCallback(async (amount: string) => {
    const updated = await usersApi.topUp(amount);
    setUser(updated);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      accessToken,
      user,
      initializing,
      login,
      register,
      logout,
      refreshUser,
      updateUser,
      topUp
    }),
    [accessToken, user, initializing, login, register, logout, refreshUser, updateUser, topUp]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};
