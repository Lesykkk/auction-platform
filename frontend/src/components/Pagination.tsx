import type { Meta } from "../types";

type Props = {
  meta: Meta | null;
  onPageChange: (page: number) => void;
};

export const Pagination = ({ meta, onPageChange }: Props) => {
  if (!meta || meta.total_pages <= 1) return null;

  return (
    <div className="pagination">
      <button className="ghost-button" disabled={meta.page <= 1} onClick={() => onPageChange(meta.page - 1)}>
        Назад
      </button>
      <span>
        Сторінка {meta.page} з {meta.total_pages}
      </span>
      <button
        className="ghost-button"
        disabled={meta.page >= meta.total_pages}
        onClick={() => onPageChange(meta.page + 1)}
      >
        Далі
      </button>
    </div>
  );
};
