import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { bidsApi } from "../api/bids";
import { lotsApi } from "../api/lots";
import { useAuth } from "../auth/AuthContext";
import { EmptyState } from "../components/EmptyState";
import { ErrorAlert } from "../components/ErrorAlert";
import { Pagination } from "../components/Pagination";
import { PlaceholderImage } from "../components/PlaceholderImage";
import { StatusBadge } from "../components/StatusBadge";
import type { Bid, Lot, Meta } from "../types";
import { formatDate, formatMoney, nextBidAmount } from "../utils";

export const LotDetailPage = () => {
  const { lotId = "" } = useParams();
  const { user, refreshUser } = useAuth();
  const [lot, setLot] = useState<Lot | null>(null);
  const [bids, setBids] = useState<Bid[]>([]);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [page, setPage] = useState(1);
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);
  const [notice, setNotice] = useState("");

  const loadLot = async () => {
    const [lotResponse, bidsResponse] = await Promise.all([
      lotsApi.detail(lotId),
      bidsApi.listByLot(lotId, { page, limit: 10 })
    ]);
    setLot(lotResponse);
    setBids(bidsResponse.items);
    setMeta(bidsResponse.meta);
    setAmount(nextBidAmount(lotResponse.current_price, lotResponse.min_bid_increment));
  };

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    loadLot()
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [lotId, page]);

  const placeBid = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setNotice("");
    try {
      await bidsApi.placeBid(lotId, amount);
      await Promise.all([loadLot(), refreshUser()]);
      setNotice("Ставку прийнято.");
    } catch (err) {
      setError(err);
    }
  };

  if (loading) return <div className="page-state">Завантажуємо лот...</div>;
  if (!lot) return <div className="page-state">Лот не знайдено.</div>;

  const minimumBid = nextBidAmount(lot.current_price, lot.min_bid_increment);

  return (
    <section className="content-section">
      <Link to={`/auctions/${lot.auction_id}`} className="back-link">
        Назад до аукціону
      </Link>
      <div className="lot-detail">
        <PlaceholderImage seed={lot.id} label={lot.title} />
        <div className="lot-detail-info">
          <div className="card-topline">
            <StatusBadge status={lot.status} />
            <span>Створено: {formatDate(lot.created_at)}</span>
          </div>
          <h1>{lot.title}</h1>
          <p>{lot.description}</p>
          <div className="price-panel">
            <div>
              <span>Поточна ставка</span>
              <strong>{formatMoney(lot.current_price)}</strong>
            </div>
            <div>
              <span>Мінімальний крок</span>
              <strong>{formatMoney(lot.min_bid_increment)}</strong>
            </div>
            <div>
              <span>Наступна ставка від</span>
              <strong>{formatMoney(minimumBid)}</strong>
            </div>
          </div>

          {error ? <ErrorAlert error={error} /> : null}
          {notice && <p className="form-success">{notice}</p>}

          {lot.status === "ACTIVE" ? (
            user ? (
              <form className="bid-form" onSubmit={placeBid}>
                <label>
                  Ваша ставка
                  <input
                    type="number"
                    min={minimumBid}
                    step="0.01"
                    value={amount}
                    onChange={(event) => setAmount(event.target.value)}
                    required
                  />
                </label>
                <button className="primary-button">Зробити ставку</button>
              </form>
            ) : (
              <Link className="primary-button" to="/login">
                Увійти, щоб зробити ставку
              </Link>
            )
          ) : (
            <p className="muted">Ставки доступні лише для активних лотів.</p>
          )}
        </div>
      </div>

      <div className="section-heading">
        <h2>Історія ставок</h2>
        <span>{meta?.total ?? bids.length} всього</span>
      </div>
      {bids.length === 0 ? (
        <EmptyState title="Ставок поки немає" text="Перша ставка визначить поточного лідера лота." />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Сума</th>
                <th>Учасник</th>
                <th>Дата</th>
              </tr>
            </thead>
            <tbody>
              {bids.map((bid) => (
                <tr key={bid.id}>
                  <td>{formatMoney(bid.amount)}</td>
                  <td>{bid.user_id === user?.id ? "Ви" : bid.user_id.slice(0, 8)}</td>
                  <td>{formatDate(bid.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Pagination meta={meta} onPageChange={setPage} />
    </section>
  );
};
