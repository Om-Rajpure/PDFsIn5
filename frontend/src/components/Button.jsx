import { forwardRef } from 'react';
import { motion } from 'framer-motion';
import './Button.css';

/**
 * Reusable Button component.
 *
 * Props:
 *  variant  — 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
 *  size     — 'sm' | 'md' | 'lg'
 *  icon     — ReactNode prepended before children
 *  iconEnd  — ReactNode appended after children
 *  loading  — shows a spinner and disables interactions
 *  fullWidth— stretches to 100% width
 *  ...rest  — any valid <button> props (onClick, disabled, type…)
 */
const Button = forwardRef(function Button(
    {
        children,
        variant = 'primary',
        size = 'md',
        icon,
        iconEnd,
        loading = false,
        fullWidth = false,
        className = '',
        ...rest
    },
    ref
) {
    const classes = [
        'btn',
        `btn--${variant}`,
        `btn--${size}`,
        fullWidth ? 'btn--full' : '',
        loading ? 'btn--loading' : '',
        className,
    ]
        .filter(Boolean)
        .join(' ');

    return (
        <motion.button
            ref={ref}
            className={classes}
            disabled={loading || rest.disabled}
            whileHover={!loading && !rest.disabled ? { scale: 1.025 } : {}}
            whileTap={!loading && !rest.disabled ? { scale: 0.975 } : {}}
            transition={{ type: 'spring', stiffness: 400, damping: 22 }}
            {...rest}
        >
            {loading ? (
                <span className="btn__spinner" aria-hidden="true" />
            ) : (
                icon && <span className="btn__icon btn__icon--start">{icon}</span>
            )}
            {children && <span className="btn__label">{children}</span>}
            {!loading && iconEnd && (
                <span className="btn__icon btn__icon--end">{iconEnd}</span>
            )}
        </motion.button>
    );
});

export default Button;
