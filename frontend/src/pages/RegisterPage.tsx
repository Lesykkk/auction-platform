import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { ErrorAlert } from "../components/ErrorAlert";

export const RegisterPage = () => {
  const { register } = useAuth();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await register({ username, email, password });
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-page">
      <div className="auth-panel">
        <p className="eyebrow">Новий учасник</p>
        <h1>Створіть акаунт</h1>
        <form onSubmit={onSubmit} className="stack-form">
          <label>
            Ім'я користувача
            <input value={username} minLength={3} onChange={(event) => setUsername(event.target.value)} required />
          </label>
          <label>
            Email
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>
          <label>
            Пароль
            <input
              type="password"
              value={password}
              minLength={8}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {error ? <ErrorAlert error={error} /> : null}
          <button className="primary-button" disabled={loading}>
            {loading ? "Створюємо..." : "Зареєструватися"}
          </button>
        </form>
        <p className="auth-switch">
          Вже маєте акаунт? <Link to="/login">Увійти</Link>
        </p>
      </div>
    </section>
  );
};
