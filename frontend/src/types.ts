export type AuctionStatus = "PENDING" | "ACTIVE" | "CLOSED" | "CANCELLED";
export type LotStatus = "PENDING" | "ACTIVE" | "SOLD" | "UNSOLD" | "CANCELLED";
export type PaymentStatus = "COMPLETED" | "REFUNDED";

export type Meta = {
  total: number;
  page: number;
  limit: number;
  total_pages: number;
};

export type PaginatedResponse<T> = {
  items: T[];
  meta: Meta;
};

export type User = {
  id: string;
  username: string;
  email: string;
  balance: string;
  locked_balance: string;
  created_at: string;
};

export type Auction = {
  id: string;
  title: string;
  description: string;
  user_id: string;
  status: AuctionStatus;
  created_at: string;
  closes_at: string;
};

export type Lot = {
  id: string;
  auction_id: string;
  title: string;
  description: string;
  starting_price: string;
  min_bid_increment: string;
  current_price: string;
  status: LotStatus;
  winner_id: string | null;
  created_at: string;
};

export type Bid = {
  id: string;
  lot_id: string;
  user_id: string;
  amount: string;
  created_at: string;
};

export type MyBid = {
  id: string;
  lot_id: string;
  auction_id: string;
  user_id: string;
  amount: string;
  current_price: string;
  lot_title: string;
  lot_status: LotStatus;
  auction_title: string;
  auction_status: AuctionStatus;
  is_locked: boolean;
  locked_amount: string;
  created_at: string;
};

export type MyBidsSummary = {
  total_locked_amount: string;
};

export type MyBidsPaginatedResponse = {
  items: MyBid[];
  meta: Meta;
  summary: MyBidsSummary;
};

export type Payment = {
  id: string;
  lot_id: string;
  user_id: string;
  amount: string;
  status: PaymentStatus;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
};

export type PaginationParams = {
  page?: number;
  limit?: number;
};
