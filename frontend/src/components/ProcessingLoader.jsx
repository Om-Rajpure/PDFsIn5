import { motion } from 'framer-motion';
import { FiLoader } from 'react-icons/fi';

/**
 * ProcessingLoader — shown while the backend is working.
 *
 * Props:
 *   message — custom message (default "Processing your file…")
 *   sub     — secondary line
 */
export default function ProcessingLoader({
    message = 'Processing your file…',
    sub = 'This usually takes just a few seconds.',
}) {
    return (
        <motion.div
            className="processing-loader"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.96 }}
            transition={{ duration: 0.25 }}
        >
            {/* Pulsing ring */}
            <div className="processing-loader__ring-wrap">
                <motion.div
                    className="processing-loader__ring"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
                />
                {/* Inner glow dot */}
                <motion.div
                    className="processing-loader__dot"
                    animate={{ scale: [1, 1.15, 1] }}
                    transition={{ duration: 1.4, repeat: Infinity, ease: 'easeInOut' }}
                />
            </div>

            {/* Text */}
            <motion.p
                className="processing-loader__msg"
                animate={{ opacity: [0.7, 1, 0.7] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            >
                {message}
            </motion.p>
            <p className="processing-loader__sub">{sub}</p>

            {/* Animated progress dots */}
            <div className="processing-loader__dots">
                {[0, 1, 2].map((i) => (
                    <motion.span
                        key={i}
                        className="processing-loader__dot-item"
                        animate={{ y: [0, -6, 0] }}
                        transition={{ duration: 0.7, repeat: Infinity, delay: i * 0.15, ease: 'easeInOut' }}
                    />
                ))}
            </div>
        </motion.div>
    );
}
