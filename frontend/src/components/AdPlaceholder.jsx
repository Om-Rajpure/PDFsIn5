import '../styles/ads.css';

/**
 * AdPlaceholder Component
 * A temporary container ready for Google AdSense <ins> or <iframe> tags.
 * Designed to hold space and look clean before the ad loads.
 *
 * Props:
 *  format (string) - 'rectangle' | 'horizontal' | 'fluid' (default)
 *  className (string) - optional extra CSS classes
 */
export default function AdPlaceholder({ format = 'fluid', className = '' }) {
    return (
        <div className={`ad-placeholder ad-placeholder--${format} ${className}`}>
            {/* The actual AdSense script/ins tag will go here later */}
            <div className="ad-placeholder__content">
                <span className="ad-placeholder__label">Advertisement</span>
            </div>
        </div>
    );
}
