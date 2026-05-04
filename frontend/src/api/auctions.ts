import { api } from "./http";
import { compactParams } from "./http";
import type { Auction, AuctionStatus, PaginatedResponse, PaginationParams } from "../types";

export type AuctionPayload = {
  title: string;
  description: string;
  closes_at: string;
};

export type AuctionListParams = PaginationParams & {
  status?: AuctionStatus | "";
};

export const auctionsApi = {
  async list(params: AuctionListParams = {}) {
    const { data } = await api.get<PaginatedResponse<Auction>>("/auctions", { params: compactParams(params) });
    return data;
  },
  async detail(id: string) {
    const { data } = await api.get<Auction>(`/auctions/${id}`);
    return data;
  },
  async create(payload: AuctionPayload) {
    const { data } = await api.post<Auction>("/auctions", payload);
    return data;
  },
  async update(id: string, payload: Partial<AuctionPayload>) {
    const { data } = await api.patch<Auction>(`/auctions/${id}`, payload);
    return data;
  },
  async delete(id: string) {
    await api.delete(`/auctions/${id}`);
  },
  async open(id: string) {
    const { data } = await api.post<Auction>(`/auctions/${id}/open`);
    return data;
  },
  async close(id: string) {
    const { data } = await api.post<Auction>(`/auctions/${id}/close`);
    return data;
  }
};
