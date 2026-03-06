import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import MainLayout from './layouts/MainLayout';

// Lazy loaded routes for performance chunking
const Home = lazy(() => import('./pages/Home'));
const ToolPage = lazy(() => import('./pages/ToolPage'));
const Blog = lazy(() => import('./pages/Blog'));
const BlogPost = lazy(() => import('./pages/BlogPost'));
const Login = lazy(() => import('./pages/Login'));
const Signup = lazy(() => import('./pages/Signup'));

export default function App() {
  return (
    <HelmetProvider>
      <BrowserRouter>
        <MainLayout>
          <Suspense fallback={<div style={{ padding: '100px', textAlign: 'center' }}>Loading...</div>}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/tool/:toolName" element={<ToolPage />} />
              <Route path="/blog" element={<Blog />} />
              <Route path="/blog/:slug" element={<BlogPost />} />
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
          </Suspense>
        </MainLayout>
      </BrowserRouter>
    </HelmetProvider>
  );
}
