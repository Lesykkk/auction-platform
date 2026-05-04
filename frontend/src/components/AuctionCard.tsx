import { Link } from "react-router-dom";
import type { Auction } from "../types";
import { formatDate, getTimeLeft } from "../utils";
import { StatusBadge } from "./StatusBadge";

type Props = {
  auction: Auction;
};

export const AuctionCard = ({ auction }: Props) => (
  <article className="auction-card">
    <div className="card-body">
      <div className="card-topline">
        <StatusBadge status={auction.status} />
        <span>{getTimeLeft(auction.closes_at)}</span>
      </div>
      <h3>{auction.title}</h3>
      <p>{auction.description}</p>
      <dl className="meta-grid">
        <div>
          <dt>Створено</dt>
          <dd>{formatDate(auction.created_at)}</dd>
        </div>
        <div>
          <dt>Завершення</dt>
          <dd>{formatDate(auction.closes_at)}</dd>
        </div>
      </dl>
    </div>
    <Link to={`/auctions/${auction.id}`} className="primary-button">
      Переглянути лоти
    </Link>
  </article>
);
