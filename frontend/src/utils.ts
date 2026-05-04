import type { AuctionStatus, LotStatus, PaymentStatus } from "./types";

export const auctionStatusLabels: Record<AuctionStatus, string> = {
  PENDING: "Очікує",
  ACTIVE: "Активний",
  CLOSED: "Закритий",
  CANCELLED: "Скасований"
};

export const lotStatusLabels: Record<LotStatus, string> = {
  PENDING: "Очікує",
  ACTIVE: "Активний",
  SOLD: "Продано",
  UNSOLD: "Без продажу",
  CANCELLED: "Скасовано"
};

export const paymentStatusLabels: Record<PaymentStatus, string> = {
  COMPLETED: "Оплачено",
  REFUNDED: "Повернено"
};

export const formatMoney = (value: string | number) =>
  new Intl.NumberFormat("uk-UA", {
    style: "currency",
    currency: "UAH",
    maximumFractionDigits: 0
  }).format(Number(value));

export const formatDate = (value: string) =>
  new Intl.DateTimeFormat("uk-UA", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));

export const toDateTimeLocal = (value: string) => {
  const date = new Date(value);
  const offset = date.getTimezoneOffset() * 60000;
  return new Date(date.getTime() - offset).toISOString().slice(0, 16);
};

export const fromDateTimeLocal = (value: string) => new Date(value).toISOString();

export const getTimeLeft = (value: string) => {
  const diff = new Date(value).getTime() - Date.now();
  if (diff <= 0) return "завершено";

  const minutes = Math.floor(diff / 60000);
  const days = Math.floor(minutes / 1440);
  const hours = Math.floor((minutes % 1440) / 60);
  const mins = minutes % 60;

  if (days > 0) return `${days} дн ${hours} год`;
  if (hours > 0) return `${hours} год ${mins} хв`;
  return `${mins} хв`;
};

export const nextBidAmount = (currentPrice: string, minIncrement: string) =>
  (Number(currentPrice) + Number(minIncrement)).toFixed(2);

export const placeholderPalette = [
  ["#e8dfd5", "#b69575"],
  ["#d9d4cc", "#8a7563"],
  ["#eee6dc", "#b9a48f"],
  ["#ded8d0", "#9f866e"],
  ["#e6e0d7", "#a78766"],
  ["#f1e9dd", "#b28f6f"]
];

export const getPlaceholderColors = (seed: string) => {
  const total = [...seed].reduce((sum, char) => sum + char.charCodeAt(0), 0);
  return placeholderPalette[total % placeholderPalette.length];
};
