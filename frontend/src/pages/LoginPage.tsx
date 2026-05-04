import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { ErrorAlert } from "../components/ErrorAlert";

export const LoginPage = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(username, password);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-page">
      <div className="auth-panel">
        <p className="eyebrow">З поверненням</p>
        <h1>Увійдіть в Auctio</h1>
        <form onSubmit={onSubmit} className="stack-form">
          <label>
            Ім'я користувача
            <input value={username} minLength={3} onChange={(event) => setUsername(event.target.value)} required />
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
            {loading ? "Входимо..." : "Увійти"}
          </button>
        </form>
        <p className="auth-switch">
          Ще немає акаунта? <Link to="/register">Зареєструватися</Link>
        </p>
      </div>
    </section>
  );
};
