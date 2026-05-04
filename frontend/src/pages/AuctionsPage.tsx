import { useEffect, useMemo, useState } from "react";
import { auctionsApi } from "../api/auctions";
import { AuctionCard } from "../components/AuctionCard";
import { EmptyState } from "../components/EmptyState";
import { ErrorAlert } from "../components/ErrorAlert";
import { Pagination } from "../components/Pagination";
import type { Auction, AuctionStatus, Meta } from "../types";

const statusOptions: Array<{ value: AuctionStatus | ""; label: string }> = [
  { value: "", label: "Усі" },
  { value: "ACTIVE", label: "Активні" },
  { value: "PENDING", label: "Очікують" },
  { value: "CLOSED", label: "Завершені" }
];

export const AuctionsPage = () => {
  const [auctions, setAuctions] = useState<Auction[]>([]);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [status, setStatus] = useState<AuctionStatus | "">("");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("closes_at");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    const loadAllAuctions = async () => {
      const firstPage = await auctionsApi.list({ page: 1, limit: 100, ...(status ? { status } : {}) });
      const allAuctions = [...firstPage.items];

      for (let currentPage = 2; currentPage <= firstPage.meta.total_pages; currentPage += 1) {
        const response = await auctionsApi.list({ page: currentPage, limit: 100, ...(status ? { status } : {}) });
        allAuctions.push(...response.items);
      }

      if (!active) return;
      setAuctions(allAuctions);
    };

    loadAllAuctions()
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));

    return () => {
      active = false;
    };
  }, [status]);

  const filteredAuctions = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return [...auctions]
      .filter((auction) => {
        if (!normalized) return true;
        return `${auction.title} ${auction.description}`.toLowerCase().includes(normalized);
      })
      .sort((a, b) => {
        if (sort === "created_at") return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        if (sort === "oldest") return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
        if (sort === "title") return a.title.localeCompare(b.title, "uk");
        return new Date(a.closes_at).getTime() - new Date(b.closes_at).getTime();
      });
  }, [auctions, query, sort]);

  const total = filteredAuctions.length;
  const totalPages = Math.max(1, Math.ceil(total / 9));
  const safePage = Math.min(page, totalPages);
  const visibleAuctions = filteredAuctions.slice((safePage - 1) * 9, safePage * 9);

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  useEffect(() => {
    setPage(1);
  }, [query, sort, status]);

  useEffect(() => {
    setMeta({ total, page: safePage, limit: 9, total_pages: totalPages });
  }, [total, safePage, totalPages]);

  return (
    <section className="content-section">
      <div className="hero-panel">
        <div>
          <p className="eyebrow">Онлайн-аукціон</p>
          <h1>Аукціони</h1>
          <p>
            Переглядайте активні торги, відкривайте лоти та робіть ставки після авторизації. Дані надходять
            напряму з наявних сервісів платформи.
          </p>
        </div>
      </div>

      <div className="toolbar">
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Пошук аукціонів..." />
        <select value={sort} onChange={(event) => setSort(event.target.value)}>
          <option value="closes_at">До завершення</option>
          <option value="created_at">Найновіші</option>
          <option value="oldest">Найстаріші</option>
          <option value="title">За назвою</option>
        </select>
      </div>

      <div className="tabs">
        {statusOptions.map((option) => (
          <button
            key={option.value || "all"}
            className={status === option.value ? "active" : ""}
            onClick={() => {
              setStatus(option.value);
            }}
          >
            {option.label}
          </button>
        ))}
      </div>

      {loading && <div className="page-state">Завантажуємо аукціони...</div>}
      {error ? <ErrorAlert error={error} /> : null}
      {!loading && !error && visibleAuctions.length === 0 && (
        <EmptyState title="Аукціони не знайдено" text="Змініть фільтр або створіть перший аукціон у кабінеті." />
      )}
      <div className="auction-grid">
        {visibleAuctions.map((auction) => (
          <AuctionCard key={auction.id} auction={auction} />
        ))}
      </div>
      <Pagination meta={meta} onPageChange={setPage} />

      <section className="info-band" id="how-it-works">
        <div>
          <h2>Як це працює</h2>
          <p>Організатор створює аукціон і лоти, відкриває торги, покупці роблять ставки, а закриття аукціону запускає розрахунки.</p>
        </div>
      </section>
    </section>
  );
};
