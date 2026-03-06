import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiMail, FiLock, FiLogIn } from 'react-icons/fi';
import './Auth.css';

export default function Login() {
    const [form, setForm] = useState({ email: '', password: '' });
    const [error, setError] = useState('');

    const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!form.email || !form.password) {
            setError('Please fill in all fields.');
            return;
        }
        setError('');
        // TODO: connect to backend auth endpoint
        console.log('Login payload:', form);
        alert('Login endpoint not yet connected.');
    };

    return (
        <div className="auth-page">
            <motion.div
                className="auth-card"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
            >
                <Link to="/" className="auth-logo">⚡ PDFsIn<span>5</span></Link>
                <h1 className="auth-title">Welcome back</h1>
                <p className="auth-sub">Sign in to your account to continue.</p>

                {error && <p className="auth-error">{error}</p>}

                <form className="auth-form" onSubmit={handleSubmit} noValidate>
                    <div className="auth-field">
                        <label htmlFor="email">Email</label>
                        <div className="auth-input-wrap">
                            <FiMail className="auth-input-icon" />
                            <input
                                id="email"
                                type="email"
                                name="email"
                                placeholder="you@example.com"
                                value={form.email}
                                onChange={handleChange}
                                autoComplete="email"
                            />
                        </div>
                    </div>

                    <div className="auth-field">
                        <label htmlFor="password">Password</label>
                        <div className="auth-input-wrap">
                            <FiLock className="auth-input-icon" />
                            <input
                                id="password"
                                type="password"
                                name="password"
                                placeholder="••••••••"
                                value={form.password}
                                onChange={handleChange}
                                autoComplete="current-password"
                            />
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary auth-submit">
                        <FiLogIn /> Sign in
                    </button>
                </form>

                <p className="auth-switch">
                    Don&apos;t have an account? <Link to="/signup">Sign up free</Link>
                </p>
            </motion.div>
        </div>
    );
}
