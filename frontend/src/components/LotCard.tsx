import { Link } from "react-router-dom";
import type { Lot } from "../types";
import { formatMoney } from "../utils";
import { PlaceholderImage } from "./PlaceholderImage";
import { StatusBadge } from "./StatusBadge";

type Props = {
  lot: Lot;
  onDelete?: (lot: Lot) => void;
  onEdit?: (lot: Lot) => void;
  editable?: boolean;
};

export const LotCard = ({ lot, editable = false, onDelete, onEdit }: Props) => (
  <article className="lot-card">
    <PlaceholderImage seed={lot.id} label={lot.title} />
    <div className="lot-card-content">
      <div className="card-topline">
        <StatusBadge status={lot.status} />
        <span>Крок {formatMoney(lot.min_bid_increment)}</span>
      </div>
      <h3>{lot.title}</h3>
      <p>{lot.description}</p>
      <div className="lot-price-row">
        <div>
          <span>Поточна ставка</span>
          <strong>{formatMoney(lot.current_price)}</strong>
        </div>
        <div>
          <span>Старт</span>
          <strong>{formatMoney(lot.starting_price)}</strong>
        </div>
      </div>
      <div className="card-actions">
        <Link to={`/lots/${lot.id}`} className="primary-button">
          Деталі лота
        </Link>
        {editable && (
          <>
            <button className="ghost-button" onClick={() => onEdit?.(lot)}>
              Редагувати
            </button>
            <button className="danger-button" onClick={() => onDelete?.(lot)}>
              Видалити
            </button>
          </>
        )}
      </div>
    </div>
  </article>
);
