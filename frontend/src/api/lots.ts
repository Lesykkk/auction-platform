import { api } from "./http";
import { compactParams } from "./http";
import type { Lot, LotStatus, PaginatedResponse, PaginationParams } from "../types";

export type LotPayload = {
  auction_id: string;
  title: string;
  description: string;
  starting_price: string;
  min_bid_increment: string;
};

export type LotListParams = PaginationParams & {
  auction_id: string;
  status?: LotStatus | "";
};

export const lotsApi = {
  async listByAuction(params: LotListParams) {
    const { data } = await api.get<PaginatedResponse<Lot>>("/lots", { params: compactParams(params) });
    return data;
  },
  async detail(id: string) {
    const { data } = await api.get<Lot>(`/lots/${id}`);
    return data;
  },
  async create(payload: LotPayload) {
    const { data } = await api.post<Lot>("/lots", payload);
    return data;
  },
  async update(id: string, payload: Partial<Omit<LotPayload, "auction_id">>) {
    const { data } = await api.patch<Lot>(`/lots/${id}`, payload);
    return data;
  },
  async delete(id: string) {
    await api.delete(`/lots/${id}`);
  }
};
