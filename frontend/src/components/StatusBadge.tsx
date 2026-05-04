import type { AuctionStatus, LotStatus, PaymentStatus } from "../types";
import { auctionStatusLabels, lotStatusLabels, paymentStatusLabels } from "../utils";

type Props = {
  status: AuctionStatus | LotStatus | PaymentStatus;
};

export const StatusBadge = ({ status }: Props) => {
  const labels = { ...auctionStatusLabels, ...lotStatusLabels, ...paymentStatusLabels };
  return <span className={`status status-${status.toLowerCase()}`}>{labels[status]}</span>;
};
