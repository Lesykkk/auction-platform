import { FormEvent, useEffect, useState } from "react";
import { useAuth } from "../auth/AuthContext";
import { ErrorAlert } from "../components/ErrorAlert";
import { formatMoney } from "../utils";

export const ProfilePage = () => {
  const { user, updateUser, topUp } = useAuth();
  const [username, setUsername] = useState(user?.username ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [amount, setAmount] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    setUsername(user?.username ?? "");
    setEmail(user?.email ?? "");
  }, [user]);

  const submitProfile = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setNotice("");
    try {
      await updateUser({ username, email });
      setNotice("Профіль оновлено.");
    } catch (err) {
      setError(err);
    }
  };

  const submitTopUp = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setNotice("");
    try {
      await topUp(amount);
      setAmount("");
      setNotice("Баланс поповнено.");
    } catch (err) {
      setError(err);
    }
  };

  if (!user) return null;

  return (
    <section className="content-section narrow">
      <p className="eyebrow">Акаунт</p>
      <h1>Профіль</h1>
      <div className="balance-strip">
        <div>
          <span>Баланс</span>
          <strong>{formatMoney(user.balance)}</strong>
        </div>
        <div>
          <span>Заблоковано у ставках</span>
          <strong>{formatMoney(user.locked_balance)}</strong>
        </div>
        <div>
          <span>Доступно</span>
          <strong>{formatMoney(Number(user.balance) - Number(user.locked_balance))}</strong>
        </div>
      </div>
      {error ? <ErrorAlert error={error} /> : null}
      {notice && <p className="form-success">{notice}</p>}
      <div className="management-grid">
        <form className="management-panel stack-form" onSubmit={submitProfile}>
          <h2>Дані профілю</h2>
          <label>
            Ім'я користувача
            <input value={username} minLength={3} onChange={(event) => setUsername(event.target.value)} required />
          </label>
          <label>
            Email
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>
          <button className="primary-button">Зберегти</button>
        </form>
        <form className="management-panel stack-form" onSubmit={submitTopUp}>
          <h2>Поповнення балансу</h2>
          <label>
            Сума
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              required
            />
          </label>
          <button className="primary-button">Поповнити</button>
        </form>
      </div>
    </section>
  );
};
