import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import './ToolCard.css';

/**
 * ToolCard — represents a single PDF tool on the Home grid.
 *
 * Props:
 *  icon        — React icon component
 *  title       — tool name string
 *  description — short description
 *  to          — react-router-dom link path
 *  color       — CSS hex for the icon accent  (default: --clr-primary)
 *  index       — grid index for stagger delay
 */
export default function ToolCard({ icon: Icon, title, description, to, color, index = 0 }) {
    return (
        <motion.div
            className="tool-card"
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-40px' }}
            transition={{ duration: 0.35, delay: index * 0.045, ease: 'easeOut' }}
            whileHover={{ y: -6, transition: { type: 'spring', stiffness: 320, damping: 22 } }}
        >
            <Link to={to} className="tool-card__inner" aria-label={title}>
                {/* Icon */}
                <div
                    className="tool-card__icon-wrap"
                    style={color ? { '--tc': color } : {}}
                >
                    {Icon && <Icon className="tool-card__icon" />}

                    {/* subtle shine overlay */}
                    <span className="tool-card__shine" aria-hidden="true" />
                </div>

                {/* Text */}
                <h3 className="tool-card__title">{title}</h3>
                <p className="tool-card__desc">{description}</p>

                {/* Arrow indicator */}
                <span className="tool-card__arrow" aria-hidden="true">→</span>
            </Link>
        </motion.div>
    );
}
