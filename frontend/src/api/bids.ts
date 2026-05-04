import { api } from "./http";
import type { Bid, MyBidsPaginatedResponse, PaginatedResponse, PaginationParams } from "../types";

export const bidsApi = {
  async listByLot(lotId: string, params: PaginationParams = {}) {
    const { data } = await api.get<PaginatedResponse<Bid>>("/bids", {
      params: { lot_id: lotId, ...params }
    });
    return data;
  },
  async placeBid(lotId: string, amount: string) {
    const { data } = await api.post<Bid>("/bids", { lot_id: lotId, amount });
    return data;
  },
  async listMine(params: PaginationParams = {}) {
    const { data } = await api.get<MyBidsPaginatedResponse>("/bids/me", { params });
    return data;
  }
};
