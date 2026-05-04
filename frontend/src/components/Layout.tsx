import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { formatMoney } from "../utils";

export const Layout = () => {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="site-header">
        <Link to="/auctions" className="brand">
          <span className="brand-icon">⌁</span>
          <span>AUCTIO</span>
        </Link>
        <nav className="main-nav">
          <NavLink to="/auctions">Аукціони</NavLink>
          <a href="#how-it-works">Як це працює</a>
          <a href="#contacts">Контакти</a>
          {user && <NavLink to="/organizer">Керування</NavLink>}
          {user && <NavLink to="/locked-funds">Блокування</NavLink>}
          {user && <NavLink to="/payments">Платежі</NavLink>}
        </nav>
        <div className="header-actions">
          {user ? (
            <>
              <Link to="/profile" className="user-pill">
                <span className="avatar">{user.username.slice(0, 1).toUpperCase()}</span>
                <span>{user.username}</span>
                <small>{formatMoney(user.balance)}</small>
              </Link>
              <button className="ghost-button" onClick={logout}>
                Вийти
              </button>
            </>
          ) : (
            <>
              <Link className="ghost-button" to="/login">
                Увійти
              </Link>
              <Link className="primary-button small" to="/register">
                Реєстрація
              </Link>
            </>
          )}
        </div>
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="site-footer" id="contacts">
        <div>
          <Link to="/auctions" className="footer-brand">
            AUCTIO
          </Link>
          <p>Онлайн-аукціони для цінних речей</p>
        </div>
        <div className="footer-links">
          <a href="#how-it-works">Як це працює</a>
          <a href="#terms">Умови використання</a>
          <a href="#privacy">Політика конфіденційності</a>
        </div>
        <p>© 2026 Auctio. Усі права захищені.</p>
      </footer>
    </div>
  );
};
