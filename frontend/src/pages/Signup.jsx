import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiUser, FiMail, FiLock, FiUserPlus } from 'react-icons/fi';
import './Auth.css';

export default function Signup() {
    const [form, setForm] = useState({ name: '', email: '', password: '' });
    const [error, setError] = useState('');

    const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!form.name || !form.email || !form.password) {
            setError('Please fill in all fields.');
            return;
        }
        if (form.password.length < 8) {
            setError('Password must be at least 8 characters.');
            return;
        }
        setError('');
        // TODO: connect to backend auth endpoint
        console.log('Signup payload:', form);
        alert('Signup endpoint not yet connected.');
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
                <h1 className="auth-title">Create an account</h1>
                <p className="auth-sub">Sign up for free — no credit card required.</p>

                {error && <p className="auth-error">{error}</p>}

                <form className="auth-form" onSubmit={handleSubmit} noValidate>
                    <div className="auth-field">
                        <label htmlFor="name">Full Name</label>
                        <div className="auth-input-wrap">
                            <FiUser className="auth-input-icon" />
                            <input
                                id="name"
                                type="text"
                                name="name"
                                placeholder="Jane Doe"
                                value={form.name}
                                onChange={handleChange}
                                autoComplete="name"
                            />
                        </div>
                    </div>

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
                                placeholder="Min 8 characters"
                                value={form.password}
                                onChange={handleChange}
                                autoComplete="new-password"
                            />
                        </div>
                    </div>

                    <button type="submit" className="btn btn-primary auth-submit">
                        <FiUserPlus /> Create Account
                    </button>
                </form>

                <p className="auth-switch">
                    Already have an account? <Link to="/login">Sign in</Link>
                </p>
            </motion.div>
        </div>
    );
}
