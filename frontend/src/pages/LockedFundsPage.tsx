import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { bidsApi } from "../api/bids";
import { useAuth } from "../auth/AuthContext";
import { EmptyState } from "../components/EmptyState";
import { ErrorAlert } from "../components/ErrorAlert";
import { Pagination } from "../components/Pagination";
import { StatusBadge } from "../components/StatusBadge";
import type { Meta, MyBid } from "../types";
import { formatDate, formatMoney } from "../utils";

export const LockedFundsPage = () => {
  const { user } = useAuth();
  const [bids, setBids] = useState<MyBid[]>([]);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [totalLockedAmount, setTotalLockedAmount] = useState("0.00");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    bidsApi
      .listMine({ page, limit: 20 })
      .then((response) => {
        if (!active) return;
        setBids(response.items);
        setMeta(response.meta);
        setTotalLockedAmount(response.summary.total_locked_amount);
      })
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));

    return () => {
      active = false;
    };
  }, [page]);

  const activeLocks = useMemo(() => bids.filter((bid) => bid.is_locked), [bids]);
  const unlockedHistoryCount = bids.length - activeLocks.length;

  return (
    <section className="content-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Фінанси</p>
          <h1>Заблоковані кошти</h1>
        </div>
        <Link className="ghost-button" to="/profile">
          До профілю
        </Link>
      </div>

      <div className="summary-grid">
        <div className="summary-card">
          <span>Заблоковано зараз</span>
          <strong>{formatMoney(totalLockedAmount)}</strong>
          <small>Сума активних лідируючих ставок</small>
        </div>
        <div className="summary-card">
          <span>Поточне блокування в профілі</span>
          <strong>{formatMoney(user?.locked_balance ?? "0")}</strong>
          <small>Значення з профілю користувача</small>
        </div>
        <div className="summary-card">
          <span>Активні блокування на сторінці</span>
          <strong>{activeLocks.length}</strong>
          <small>{unlockedHistoryCount} записів уже не блокують кошти</small>
        </div>
      </div>

      {loading && <div className="page-state">Завантажуємо блокування...</div>}
      {error ? <ErrorAlert error={error} /> : null}

      {!loading && !error && bids.length === 0 ? (
        <EmptyState
          title="Ставок поки немає"
          text="Коли ви почнете торги, тут з'явиться список ставок і буде видно, де саме заблоковані кошти."
        />
      ) : null}

      {!loading && !error && bids.length > 0 ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Лот</th>
                <th>Аукціон</th>
                <th>Моя ставка</th>
                <th>Поточна ціна</th>
                <th>Статус</th>
                <th>Заблоковано</th>
                <th>Дата</th>
              </tr>
            </thead>
            <tbody>
              {bids.map((bid) => (
                <tr key={bid.id} className={bid.is_locked ? "highlight-row" : ""}>
                  <td>
                    <div className="row-stack">
                      <Link className="table-link" to={`/lots/${bid.lot_id}`}>
                        {bid.lot_title}
                      </Link>
                      <div className="status-row">
                        <StatusBadge status={bid.lot_status} />
                      </div>
                    </div>
                  </td>
                  <td>
                    <div className="row-stack">
                      <span>{bid.auction_title}</span>
                      <div className="status-row">
                        <StatusBadge status={bid.auction_status} />
                      </div>
                    </div>
                  </td>
                  <td>{formatMoney(bid.amount)}</td>
                  <td>{formatMoney(bid.current_price)}</td>
                  <td>
                    <span className={bid.is_locked ? "lock-indicator locked" : "lock-indicator released"}>
                      {bid.is_locked ? "Кошти заблоковані" : "Кошти розблоковані"}
                    </span>
                  </td>
                  <td>{formatMoney(bid.locked_amount)}</td>
                  <td>{formatDate(bid.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      <Pagination meta={meta} onPageChange={setPage} />
    </section>
  );
};
