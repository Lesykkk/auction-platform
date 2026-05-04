import { api } from "./http";
import type { TokenResponse } from "../types";

export type LoginPayload = {
  username: string;
  password: string;
};

export const authApi = {
  async login(payload: LoginPayload) {
    const { data } = await api.post<TokenResponse>("/auth/login", payload);
    return data;
  },
  async refresh() {
    const { data } = await api.post<TokenResponse>("/auth/refresh");
    return data;
  },
  async logout() {
    await api.post("/auth/logout");
  }
};
