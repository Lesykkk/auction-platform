import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { auctionsApi } from "../api/auctions";
import { lotsApi, type LotPayload } from "../api/lots";
import { useAuth } from "../auth/AuthContext";
import { EmptyState } from "../components/EmptyState";
import { ErrorAlert } from "../components/ErrorAlert";
import { LotCard } from "../components/LotCard";
import { Pagination } from "../components/Pagination";
import { StatusBadge } from "../components/StatusBadge";
import type { Auction, Lot, Meta } from "../types";
import { formatDate, fromDateTimeLocal, toDateTimeLocal } from "../utils";

const emptyLotForm = (auctionId: string): LotPayload => ({
  auction_id: auctionId,
  title: "",
  description: "",
  starting_price: "",
  min_bid_increment: ""
});

export const AuctionDetailPage = () => {
  const { auctionId = "" } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [auction, setAuction] = useState<Auction | null>(null);
  const [lots, setLots] = useState<Lot[]>([]);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [page, setPage] = useState(1);
  const [lotForm, setLotForm] = useState<LotPayload>(emptyLotForm(auctionId));
  const [editingLot, setEditingLot] = useState<Lot | null>(null);
  const [auctionForm, setAuctionForm] = useState({ title: "", description: "", closes_at: "" });
  const [error, setError] = useState<unknown>(null);
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);

  const isOwner = Boolean(user && auction && user.id === auction.user_id);
  const canEditPending = isOwner && auction?.status === "PENDING";

  const loadAuction = async () => {
    const [auctionResponse, lotsResponse] = await Promise.all([
      auctionsApi.detail(auctionId),
      lotsApi.listByAuction({ auction_id: auctionId, page, limit: 9 })
    ]);
    setAuction(auctionResponse);
    setAuctionForm({
      title: auctionResponse.title,
      description: auctionResponse.description,
      closes_at: toDateTimeLocal(auctionResponse.closes_at)
    });
    setLots(lotsResponse.items);
    setMeta(lotsResponse.meta);
  };

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    loadAuction()
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [auctionId, page]);

  const submitLot = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setNotice("");
    try {
      if (editingLot) {
        await lotsApi.update(editingLot.id, {
          title: lotForm.title,
          description: lotForm.description,
          starting_price: lotForm.starting_price,
          min_bid_increment: lotForm.min_bid_increment
        });
        setNotice("Лот оновлено.");
      } else {
        await lotsApi.create(lotForm);
        setNotice("Лот додано.");
      }
      setEditingLot(null);
      setLotForm(emptyLotForm(auctionId));
      await loadAuction();
    } catch (err) {
      setError(err);
    }
  };

  const submitAuction = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setNotice("");
    try {
      await auctionsApi.update(auctionId, {
        ...auctionForm,
        closes_at: fromDateTimeLocal(auctionForm.closes_at)
      });
      setNotice("Аукціон оновлено.");
      await loadAuction();
    } catch (err) {
      setError(err);
    }
  };

  const deleteLot = async (lot: Lot) => {
    if (!window.confirm(`Видалити лот "${lot.title}"?`)) return;
    setError(null);
    try {
      await lotsApi.delete(lot.id);
      await loadAuction();
    } catch (err) {
      setError(err);
    }
  };

  const changeAuctionStatus = async (action: "open" | "close") => {
    setError(null);
    setNotice("");
    try {
      const updated = action === "open" ? await auctionsApi.open(auctionId) : await auctionsApi.close(auctionId);
      setAuction(updated);
      setNotice(action === "open" ? "Аукціон відкрито." : "Аукціон закрито.");
      await loadAuction();
    } catch (err) {
      setError(err);
    }
  };

  const deleteAuction = async () => {
    if (!auction) return;
    if (!window.confirm(`Видалити аукціон "${auction.title}" разом з лотами?`)) return;
    setError(null);
    try {
      await auctionsApi.delete(auctionId);
      navigate("/organizer");
    } catch (err) {
      setError(err);
    }
  };

  const editableLots = useMemo(() => canEditPending, [canEditPending]);

  if (loading) return <div className="page-state">Завантажуємо аукціон...</div>;
  if (!auction) return <div className="page-state">Аукціон не знайдено.</div>;

  return (
    <section className="content-section">
      <Link to="/auctions" className="back-link">
        Назад до аукціонів
      </Link>
      <div className="detail-header">
        <div>
          <div className="card-topline">
            <StatusBadge status={auction.status} />
            <span>Завершення: {formatDate(auction.closes_at)}</span>
          </div>
          <h1>{auction.title}</h1>
          <p>{auction.description}</p>
        </div>
        {isOwner && (
          <div className="detail-actions">
            {auction.status === "PENDING" && (
              <>
                <button className="primary-button" onClick={() => changeAuctionStatus("open")}>
                  Відкрити аукціон
                </button>
                <button className="danger-button" onClick={deleteAuction}>
                  Видалити аукціон
                </button>
              </>
            )}
            {auction.status === "ACTIVE" && (
              <button className="primary-button" onClick={() => changeAuctionStatus("close")}>
                Закрити аукціон
              </button>
            )}
          </div>
        )}
      </div>

      {error ? <ErrorAlert error={error} /> : null}
      {notice && <p className="form-success">{notice}</p>}

      {canEditPending && (
        <div className="management-grid">
          <form className="management-panel stack-form" onSubmit={submitAuction}>
            <h2>Редагувати аукціон</h2>
            <label>
              Назва
              <input
                value={auctionForm.title}
                minLength={5}
                onChange={(event) => setAuctionForm((current) => ({ ...current, title: event.target.value }))}
                required
              />
            </label>
            <label>
              Опис
              <textarea
                value={auctionForm.description}
                minLength={10}
                onChange={(event) => setAuctionForm((current) => ({ ...current, description: event.target.value }))}
                required
              />
            </label>
            <label>
              Дата завершення
              <input
                type="datetime-local"
                value={auctionForm.closes_at}
                onChange={(event) => setAuctionForm((current) => ({ ...current, closes_at: event.target.value }))}
                required
              />
            </label>
            <button className="primary-button">Зберегти аукціон</button>
          </form>

          <form className="management-panel stack-form" onSubmit={submitLot}>
            <h2>{editingLot ? "Редагувати лот" : "Додати лот"}</h2>
            <label>
              Назва
              <input
                value={lotForm.title}
                minLength={5}
                onChange={(event) => setLotForm((current) => ({ ...current, title: event.target.value }))}
                required
              />
            </label>
            <label>
              Опис
              <textarea
                value={lotForm.description}
                minLength={10}
                onChange={(event) => setLotForm((current) => ({ ...current, description: event.target.value }))}
                required
              />
            </label>
            <div className="split-fields">
              <label>
                Стартова ціна
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={lotForm.starting_price}
                  onChange={(event) => setLotForm((current) => ({ ...current, starting_price: event.target.value }))}
                  required
                />
              </label>
              <label>
                Мін. крок
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={lotForm.min_bid_increment}
                  onChange={(event) =>
                    setLotForm((current) => ({ ...current, min_bid_increment: event.target.value }))
                  }
                  required
                />
              </label>
            </div>
            <div className="card-actions">
              <button className="primary-button">{editingLot ? "Зберегти лот" : "Додати лот"}</button>
              {editingLot && (
                <button
                  type="button"
                  className="ghost-button"
                  onClick={() => {
                    setEditingLot(null);
                    setLotForm(emptyLotForm(auctionId));
                  }}
                >
                  Скасувати
                </button>
              )}
            </div>
          </form>
        </div>
      )}

      <div className="section-heading">
        <h2>Лоти</h2>
        <span>{meta?.total ?? lots.length} всього</span>
      </div>
      {lots.length === 0 ? (
        <EmptyState title="Лотів ще немає" text="Організатор може додати лоти до відкриття аукціону." />
      ) : (
        <div className="lot-grid">
          {lots.map((lot) => (
            <LotCard
              key={lot.id}
              lot={lot}
              editable={editableLots}
              onDelete={deleteLot}
              onEdit={(selected) => {
                setEditingLot(selected);
                setLotForm({
                  auction_id: selected.auction_id,
                  title: selected.title,
                  description: selected.description,
                  starting_price: selected.starting_price,
                  min_bid_increment: selected.min_bid_increment
                });
              }}
            />
          ))}
        </div>
      )}
      <Pagination meta={meta} onPageChange={setPage} />
    </section>
  );
};
