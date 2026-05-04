import { getPlaceholderColors } from "../utils";

type Props = {
  seed: string;
  label: string;
};

export const PlaceholderImage = ({ seed, label }: Props) => {
  const [from, to] = getPlaceholderColors(seed);
  const initials = label
    .split(" ")
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  return (
    <div className="placeholder-image" style={{ background: `linear-gradient(135deg, ${from}, ${to})` }}>
      <div className="placeholder-mark">{initials || "A"}</div>
    </div>
  );
};
