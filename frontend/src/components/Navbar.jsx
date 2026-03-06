import { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FiZap, FiChevronDown, FiMenu, FiX } from 'react-icons/fi';
import MegaMenu, { TOOL_CATEGORIES } from './MegaMenu';
import '../styles/navbar.css';

export default function Navbar() {
    const [menuOpen, setMenuOpen] = useState(false); // mega dropdown
    const [mobileOpen, setMobileOpen] = useState(false); // mobile drawer
    const [scrolled, setScrolled] = useState(false);
    const toolsRef = useRef(null); // wraps trigger + panel for click-outside

    /* Scroll shadow */
    useEffect(() => {
        const handle = () => setScrolled(window.scrollY > 8);
        window.addEventListener('scroll', handle, { passive: true });
        return () => window.removeEventListener('scroll', handle);
    }, []);

    /* Close mega menu on click outside the trigger+panel area */
    useEffect(() => {
        if (!menuOpen) return;
        const handle = (e) => {
            if (toolsRef.current && !toolsRef.current.contains(e.target)) {
                setMenuOpen(false);
            }
        };
        document.addEventListener('mousedown', handle);
        return () => document.removeEventListener('mousedown', handle);
    }, [menuOpen]);

    /* Lock body scroll when mobile drawer is open */
    useEffect(() => {
        document.body.style.overflow = mobileOpen ? 'hidden' : '';
        return () => { document.body.style.overflow = ''; };
    }, [mobileOpen]);

    /* Auto-close mobile on resize to desktop */
    useEffect(() => {
        const handle = () => { if (window.innerWidth >= 900) setMobileOpen(false); };
        window.addEventListener('resize', handle);
        return () => window.removeEventListener('resize', handle);
    }, []);

    const closeMenu = useCallback(() => setMenuOpen(false), []);
    const closeMobile = useCallback(() => setMobileOpen(false), []);

    return (
        <>
            {/* ════════════════════════ NAVBAR ════════════════════════ */}
            <header className={`navbar ${scrolled ? 'navbar--scrolled' : ''}`}>
                <div className="navbar__inner">

                    {/* Logo */}
                    <Link to="/" className="navbar__logo" onClick={closeMobile}>
                        <span className="navbar__logo-icon"><FiZap /></span>
                        PDFsIn<span className="navbar__logo-num">5</span>
                    </Link>

                    {/* Desktop — All Tools + MegaMenu */}
                    <nav className="navbar__center">
                        {/* Anchor: wraps trigger button AND mega panel for click-outside */}
                        <div className="mega-menu-anchor" ref={toolsRef}>
                            <motion.button
                                className={`navbar__tools-btn ${menuOpen ? 'active' : ''}`}
                                onClick={() => setMenuOpen((v) => !v)}
                                aria-haspopup="dialog"
                                aria-expanded={menuOpen}
                                whileHover={{ scale: 1.03 }}
                                whileTap={{ scale: 0.96 }}
                                transition={{ type: 'spring', stiffness: 400, damping: 24 }}
                            >
                                All Tools
                                <motion.span
                                    className="navbar__tools-chevron"
                                    animate={{ rotate: menuOpen ? 180 : 0 }}
                                    transition={{ duration: 0.22, ease: 'easeInOut' }}
                                >
                                    <FiChevronDown />
                                </motion.span>
                            </motion.button>

                            {/* Mega panel — rendered inside the anchor */}
                            <MegaMenu isOpen={menuOpen} onClose={closeMenu} />
                        </div>
                    </nav>

                    {/* Right controls */}
                    <div className="navbar__right">
                        <Link to="/login" className="navbar__login">Log in</Link>
                        <Link to="/signup" className="navbar__signup">Sign up</Link>

                        {/* Hamburger (mobile only) */}
                        <motion.button
                            className="navbar__hamburger"
                            onClick={() => setMobileOpen((v) => !v)}
                            aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
                            whileHover={{ scale: 1.08 }}
                            whileTap={{ scale: 0.9 }}
                        >
                            <AnimatePresence mode="wait" initial={false}>
                                {mobileOpen ? (
                                    <motion.span key="x"
                                        initial={{ rotate: -90, opacity: 0 }}
                                        animate={{ rotate: 0, opacity: 1 }}
                                        exit={{ rotate: 90, opacity: 0 }}
                                        transition={{ duration: 0.15 }}
                                        style={{ display: 'flex' }}
                                    ><FiX /></motion.span>
                                ) : (
                                    <motion.span key="burger"
                                        initial={{ rotate: 90, opacity: 0 }}
                                        animate={{ rotate: 0, opacity: 1 }}
                                        exit={{ rotate: -90, opacity: 0 }}
                                        transition={{ duration: 0.15 }}
                                        style={{ display: 'flex' }}
                                    ><FiMenu /></motion.span>
                                )}
                            </AnimatePresence>
                        </motion.button>
                    </div>
                </div>
            </header>

            {/* ════════════════════════ MOBILE DRAWER ════════════════════ */}
            <AnimatePresence>
                {mobileOpen && (
                    <motion.div
                        className="mobile-menu"
                        initial={{ opacity: 0, x: '100%' }}
                        animate={{ opacity: 1, x: '0%' }}
                        exit={{ opacity: 0, x: '100%' }}
                        transition={{ type: 'spring', stiffness: 300, damping: 32 }}
                    >
                        <div className="mobile-menu__inner">
                            {TOOL_CATEGORIES.map((cat) => (
                                <div key={cat.label} className="mobile-menu__section">
                                    <p className="mobile-menu__label">{cat.label}</p>
                                    {cat.tools.map((tool) => (
                                        <Link
                                            key={tool.id}
                                            to={`/tool/${tool.id}`}
                                            className="mobile-menu__link"
                                            onClick={closeMobile}
                                        >
                                            {tool.name}
                                        </Link>
                                    ))}
                                </div>
                            ))}

                            <div className="mobile-menu__auth">
                                <Link to="/login" className="mobile-menu__auth-ghost" onClick={closeMobile}>Log in</Link>
                                <Link to="/signup" className="mobile-menu__auth-cta" onClick={closeMobile}>Sign up</Link>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
