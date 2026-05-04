import { api } from "./http";
import { compactParams } from "./http";
import type { PaginatedResponse, PaginationParams, Payment, PaymentStatus } from "../types";

export type PaymentsParams = PaginationParams & {
  status?: PaymentStatus | "";
};

export const paymentsApi = {
  async listMine(params: PaymentsParams = {}) {
    const { data } = await api.get<PaginatedResponse<Payment>>("/payments", { params: compactParams(params) });
    return data;
  }
};
