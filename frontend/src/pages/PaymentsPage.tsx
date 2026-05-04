import { useEffect, useState } from "react";
import { paymentsApi } from "../api/payments";
import { EmptyState } from "../components/EmptyState";
import { ErrorAlert } from "../components/ErrorAlert";
import { Pagination } from "../components/Pagination";
import { StatusBadge } from "../components/StatusBadge";
import type { Meta, Payment, PaymentStatus } from "../types";
import { formatDate, formatMoney } from "../utils";

export const PaymentsPage = () => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [status, setStatus] = useState<PaymentStatus | "">("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    const params = status ? { page, limit: 10, status } : { page, limit: 10 };
    paymentsApi
      .listMine(params)
      .then((response) => {
        if (!active) return;
        setPayments(response.items);
        setMeta(response.meta);
      })
      .catch((err) => active && setError(err))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [page, status]);

  return (
    <section className="content-section">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Фінанси</p>
          <h1>Платежі</h1>
        </div>
        <select
          value={status}
          onChange={(event) => {
            setStatus(event.target.value as PaymentStatus | "");
            setPage(1);
          }}
        >
          <option value="">Усі статуси</option>
          <option value="COMPLETED">Оплачені</option>
          <option value="REFUNDED">Повернені</option>
        </select>
      </div>
      {loading && <div className="page-state">Завантажуємо платежі...</div>}
      {error ? <ErrorAlert error={error} /> : null}
      {!loading && payments.length === 0 ? (
        <EmptyState title="Платежів немає" text="Платежі з'являться після закриття аукціону з виграними лотами." />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Сума</th>
                <th>Статус</th>
                <th>Лот</th>
                <th>Дата</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((payment) => (
                <tr key={payment.id}>
                  <td>{formatMoney(payment.amount)}</td>
                  <td>
                    <StatusBadge status={payment.status} />
                  </td>
                  <td>{payment.lot_id.slice(0, 8)}</td>
                  <td>{formatDate(payment.created_at)}</td>
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
