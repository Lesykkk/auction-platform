import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuctionDetailPage } from "./pages/AuctionDetailPage";
import { AuctionsPage } from "./pages/AuctionsPage";
import { LoginPage } from "./pages/LoginPage";
import { LotDetailPage } from "./pages/LotDetailPage";
import { OrganizerPage } from "./pages/OrganizerPage";
import { PaymentsPage } from "./pages/PaymentsPage";
import { ProfilePage } from "./pages/ProfilePage";
import { RegisterPage } from "./pages/RegisterPage";

export const App = () => (
  <Routes>
    <Route element={<Layout />}>
      <Route index element={<Navigate to="/auctions" replace />} />
      <Route path="/auctions" element={<AuctionsPage />} />
      <Route path="/auctions/:auctionId" element={<AuctionDetailPage />} />
      <Route path="/lots/:lotId" element={<LotDetailPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/payments" element={<PaymentsPage />} />
        <Route path="/organizer" element={<OrganizerPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/auctions" replace />} />
    </Route>
  </Routes>
);
