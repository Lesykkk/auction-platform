import { FormEvent, useEffect, useMemo, useState } from "react";
import { auctionsApi, type AuctionPayload } from "../api/auctions";
import { useAuth } from "../auth/AuthContext";
import { ErrorAlert } from "../components/ErrorAlert";
import { AuctionCard } from "../components/AuctionCard";
import { EmptyState } from "../components/EmptyState";
import type { Auction } from "../types";
import { fromDateTimeLocal } from "../utils";

export const OrganizerPage = () => {
  const { user } = useAuth();
  const [auctions, setAuctions] = useState<Auction[]>([]);
  const [form, setForm] = useState<AuctionPayload>({ title: "", description: "", closes_at: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);
  const [notice, setNotice] = useState("");

  const loadAuctions = async () => {
    const response = await auctionsApi.list({ page: 1, limit: 100 });
    setAuctions(response.items);
  };

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    loadAuctions()
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  const myAuctions = useMemo(() => auctions.filter((auction) => auction.user_id === user?.id), [auctions, user?.id]);

  const createAuction = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setNotice("");
    try {
      await auctionsApi.create({ ...form, closes_at: fromDateTimeLocal(form.closes_at) });
      setForm({ title: "", description: "", closes_at: "" });
      setNotice("Аукціон створено. Тепер додайте лоти в деталях аукціону.");
      await loadAuctions();
    } catch (err) {
      setError(err);
    }
  };

  return (
    <section className="content-section">
      <p className="eyebrow">Організатор</p>
      <h1>Керування аукціонами</h1>
      {error ? <ErrorAlert error={error} /> : null}
      {notice && <p className="form-success">{notice}</p>}
      <div className="management-grid">
        <form className="management-panel stack-form" onSubmit={createAuction}>
          <h2>Новий аукціон</h2>
          <label>
            Назва
            <input
              value={form.title}
              minLength={5}
              onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
              required
            />
          </label>
          <label>
            Опис
            <textarea
              value={form.description}
              minLength={10}
              onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
              required
            />
          </label>
          <label>
            Дата завершення
            <input
              type="datetime-local"
              value={form.closes_at}
              onChange={(event) => setForm((current) => ({ ...current, closes_at: event.target.value }))}
              required
            />
          </label>
          <button className="primary-button">Створити</button>
        </form>
        <div className="management-panel">
          <h2>Можливості</h2>
          <ul className="plain-list">
            <li>Створення аукціону у статусі очікування.</li>
            <li>Додавання лотів до відкриття торгів.</li>
            <li>Відкриття, закриття та розрахунок через бекенд.</li>
          </ul>
        </div>
      </div>

      <div className="section-heading">
        <h2>Мої аукціони</h2>
        <span>{myAuctions.length} всього</span>
      </div>
      {loading && <div className="page-state">Завантажуємо...</div>}
      {!loading && myAuctions.length === 0 ? (
        <EmptyState title="Ви ще не створили аукціон" text="Перший аукціон можна створити формою вище." />
      ) : (
        <div className="auction-grid">
          {myAuctions.map((auction) => (
            <AuctionCard key={auction.id} auction={auction} />
          ))}
        </div>
      )}
    </section>
  );
};
