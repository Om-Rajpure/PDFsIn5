import { useState, useEffect, useCallback, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FiZap, FiChevronDown, FiMenu, FiX } from 'react-icons/fi';
import MegaMenu, { TOOL_CATEGORIES } from './MegaMenu';
import '../styles/navbar.css';

export default function Navbar() {
    const [menuOpen, setMenuOpen] = useState(false);
    const [mobileOpen, setMobileOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const toolsRef = useRef(null);
    const location = useLocation();

    /* Scroll shadow */
    useEffect(() => {
        const handle = () => setScrolled(window.scrollY > 10);
        window.addEventListener('scroll', handle, { passive: true });
        return () => window.removeEventListener('scroll', handle);
    }, []);

    /* Close mega menu on click outside */
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

    /* Lock body scroll */
    useEffect(() => {
        const isMobileMenu = menuOpen && window.innerWidth <= 768;
        document.body.style.overflow = (mobileOpen || isMobileMenu) ? 'hidden' : '';
        return () => { document.body.style.overflow = ''; };
    }, [mobileOpen, menuOpen]);

    /* Auto-close mobile on resize */
    useEffect(() => {
        const handle = () => { if (window.innerWidth >= 1024) setMobileOpen(false); };
        window.addEventListener('resize', handle);
        return () => window.removeEventListener('resize', handle);
    }, []);

    /* Close menus on route change */
    useEffect(() => {
        setMenuOpen(false);
        setMobileOpen(false);
    }, [location]);

    const closeMenu = useCallback(() => setMenuOpen(false), []);
    const closeMobile = useCallback(() => setMobileOpen(false), []);

    const navLinks = [
        { label: 'AI Tools', to: '/ai-tools' },
        { label: 'Image Tools', to: '/image-tools' },
        { label: 'Blogs', to: '/blog' },
        { label: 'About', to: '/about' },
    ];

    return (
        <header className={`navbar ${scrolled ? 'navbar--scrolled' : ''}`}>
            <div className="navbar__inner container">
                {/* Logo */}
                <Link to="/" className="navbar__logo" onClick={closeMobile}>
                    <span className="navbar__logo-icon"><FiZap /></span>
                    PDFsIn<span className="navbar__logo-num">5</span>
                </Link>

                {/* Desktop Navigation */}
                <nav className="navbar__nav">
                    {/* All Tools Trigger */}
                    <div className="mega-menu-anchor" ref={toolsRef}>
                        <button
                            className={`nav-link nav-link--tools ${menuOpen ? 'active' : ''}`}
                            onClick={() => setMenuOpen((v) => !v)}
                            aria-haspopup="dialog"
                            aria-expanded={menuOpen}
                        >
                            All Tools
                            <motion.span
                                className="nav-link__chevron"
                                animate={{ rotate: menuOpen ? 180 : 0 }}
                                transition={{ duration: 0.2 }}
                            >
                                <FiChevronDown />
                            </motion.span>
                            <span className="nav-link__underline" />
                        </button>
                    </div>

                    {navLinks.map((link) => (
                        <Link key={link.to} to={link.to} className="nav-link">
                            {link.label}
                            <span className="nav-link__underline" />
                        </Link>
                    ))}
                </nav>

                {/* Mega Menu anchored to .navbar__inner.container */}
                <MegaMenu isOpen={menuOpen} onClose={closeMenu} />

                {/* Mobile Controls */}
                <div className="navbar__mobile-toggle">
                    <motion.button
                        className="navbar__hamburger"
                        onClick={() => setMobileOpen((v) => !v)}
                        aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
                        whileTap={{ scale: 0.9 }}
                    >
                        {mobileOpen ? <FiX /> : <FiMenu />}
                    </motion.button>
                </div>
            </div>

            {/* Mobile Drawer */}
            <AnimatePresence>
                {mobileOpen && (
                    <motion.div
                        className="mobile-menu glass"
                        initial={{ opacity: 0, x: '100%' }}
                        animate={{ opacity: 1, x: '0%' }}
                        exit={{ opacity: 0, x: '100%' }}
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    >
                        <div className="mobile-menu__inner">
                            <div className="mobile-menu__main">
                                <Link to="/" className="mobile-menu__link" onClick={closeMobile}>Home</Link>
                                {navLinks.map((link) => (
                                    <Link key={link.to} to={link.to} className="mobile-menu__link" onClick={closeMobile}>
                                        {link.label}
                                    </Link>
                                ))}
                            </div>

                            <div className="mobile-menu__tools">
                                <p className="mobile-menu__label">All PDF Tools</p>
                                {TOOL_CATEGORIES.map((cat) => (
                                    <div key={cat.label} className="mobile-menu__tool-cat">
                                        <p className="mobile-menu__cat-title">{cat.label}</p>
                                        {cat.tools.map((tool) => (
                                            <Link
                                                key={tool.id}
                                                to={`/tool/${tool.id}`}
                                                className="mobile-menu__tool-link"
                                                onClick={closeMobile}
                                            >
                                                {tool.name}
                                            </Link>
                                        ))}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </header>
    );
}


