import { motion } from 'framer-motion';
import './SectionTitle.css';

/**
 * SectionTitle — reusable heading block for page sections.
 *
 * Props:
 *  badge    — small badge text above the heading (optional)
 *  title    — main heading (required, supports JSX)
 *  subtitle — secondary paragraph below (optional)
 *  align    — 'left' | 'center'   (default: 'center')
 *  size     — 'sm' | 'md' | 'lg'  (default: 'md')
 */
export default function SectionTitle({
    badge,
    title,
    subtitle,
    align = 'center',
    size = 'md',
}) {
    return (
        <motion.div
            className={`section-title section-title--${align} section-title--${size}`}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-60px' }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
        >
            {badge && (
                <span className="section-title__badge badge">{badge}</span>
            )}
            <h2 className="section-title__heading">{title}</h2>
            {subtitle && (
                <p className="section-title__sub">{subtitle}</p>
            )}
        </motion.div>
    );
}
