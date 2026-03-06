import { motion, AnimatePresence } from 'framer-motion';
import { FiSun, FiMoon } from 'react-icons/fi';
import { useTheme } from '../context/ThemeContext';
import './ThemeToggle.css';

/**
 * ThemeToggle — standalone icon button that switches light ↔ dark.
 *
 * Props:
 *  size     — 'sm' | 'md' | 'lg'   (default: 'md')
 *  className — extra class names
 */
export default function ThemeToggle({ size = 'md', className = '' }) {
    const { theme, toggleTheme } = useTheme();
    const isDark = theme === 'dark';

    return (
        <motion.button
            className={`theme-toggle theme-toggle--${size} ${className}`}
            onClick={toggleTheme}
            title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
            aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.88 }}
            transition={{ type: 'spring', stiffness: 400, damping: 22 }}
        >
            <AnimatePresence mode="wait" initial={false}>
                {isDark ? (
                    <motion.span
                        key="sun"
                        className="theme-toggle__icon"
                        initial={{ rotate: -90, opacity: 0, scale: 0.7 }}
                        animate={{ rotate: 0, opacity: 1, scale: 1 }}
                        exit={{ rotate: 90, opacity: 0, scale: 0.7 }}
                        transition={{ duration: 0.2 }}
                    >
                        <FiSun />
                    </motion.span>
                ) : (
                    <motion.span
                        key="moon"
                        className="theme-toggle__icon"
                        initial={{ rotate: 90, opacity: 0, scale: 0.7 }}
                        animate={{ rotate: 0, opacity: 1, scale: 1 }}
                        exit={{ rotate: -90, opacity: 0, scale: 0.7 }}
                        transition={{ duration: 0.2 }}
                    >
                        <FiMoon />
                    </motion.span>
                )}
            </AnimatePresence>
        </motion.button>
    );
}
