import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import MainLayout from './layouts/MainLayout';
import Home from './pages/Home';
import ToolPage from './pages/ToolPage';
import Login from './pages/Login';
import Signup from './pages/Signup';

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <MainLayout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/tool/:toolName" element={<ToolPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="*" element={
              <div style={{ textAlign: 'center', padding: '100px 24px' }}>
                <h1 style={{ fontSize: '6rem', fontWeight: 900, color: 'var(--clr-primary)', lineHeight: 1 }}>404</h1>
                <p style={{ marginTop: 16, color: 'var(--clr-text-muted)', fontSize: 'var(--text-lg)' }}>
                  Page not found.
                </p>
              </div>
            } />
          </Routes>
        </MainLayout>
      </BrowserRouter>
    </ThemeProvider>
  );
}
