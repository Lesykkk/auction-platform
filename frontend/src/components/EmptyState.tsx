export const EmptyState = ({ title, text }: { title: string; text: string }) => (
  <div className="empty-state">
    <h3>{title}</h3>
    <p>{text}</p>
  </div>
);
