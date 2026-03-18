import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import './ToolCard.css';

export default function ToolCard({ 
    icon: Icon, 
    title, 
    description, 
    to, 
    color, 
    index = 0,
    illustration,
    isPremium = false
}) {
    return (
        <motion.div
            className={`tool-card ${isPremium ? 'tool-card--premium' : ''}`}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-40px' }}
            transition={{ duration: 0.35, delay: index * 0.045, ease: 'easeOut' }}
            whileHover={{ y: -8, transition: { type: 'spring', stiffness: 320, damping: 22 } }}
        >
            <Link to={to} className="tool-card__inner glass-card" aria-label={title}>
                {illustration ? (
                    <div className="tool-card__visual">
                        <img src={illustration} alt={title} className="tool-card__illustration" />
                    </div>
                ) : (
                    <div
                        className="tool-card__icon-wrap"
                        style={color ? { '--tc': color } : {}}
                    >
                        {Icon && <Icon className="tool-card__icon" />}
                        <span className="tool-card__shine" aria-hidden="true" />
                    </div>
                )}

                <div className="tool-card__content">
                    <h3 className="tool-card__title">{title}</h3>
                    <p className="tool-card__desc">{description}</p>
                </div>

                <div className="tool-card__footer">
                    <span className="tool-card__action">Get Started →</span>
                </div>
            </Link>
        </motion.div>
    );
}

