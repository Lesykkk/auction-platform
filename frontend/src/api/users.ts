import { api } from "./http";
import type { User } from "../types";

export type RegisterPayload = {
  username: string;
  email: string;
  password: string;
};

export type UpdateMePayload = {
  username?: string;
  email?: string;
};

export const usersApi = {
  async register(payload: RegisterPayload) {
    const { data } = await api.post<User>("/users/register", payload);
    return data;
  },
  async me() {
    const { data } = await api.get<User>("/users/me");
    return data;
  },
  async updateMe(payload: UpdateMePayload) {
    const { data } = await api.patch<User>("/users/me", payload);
    return data;
  },
  async topUp(amount: string) {
    const { data } = await api.post<User>("/users/me/top-up", { amount });
    return data;
  }
};
