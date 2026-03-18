import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiGithub, FiLinkedin, FiInstagram, FiYoutube } from 'react-icons/fi';
import './DevProfile.css';

const SOCIAL_LINKS = [
    { icon: FiGithub, url: 'https://github.com/omrajpure', color: '#fff' },
    { icon: FiLinkedin, url: 'https://linkedin.com/in/omrajpure', color: '#0077b5' },
    { icon: FiInstagram, url: 'https://instagram.com/omrajpure', color: '#e4405f' },
    { icon: FiYoutube, url: 'https://youtube.com/@omrajpure', color: '#ff0000' },
];

export default function DevProfile() {
    const [isHovered, setIsHovered] = useState(false);

    return (
        <div
            className="dev-profile"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            <div className="dev-profile__trigger">
                <img
                    src="https://github.com/omrajpure.png"
                    alt="Developer Avatar"
                    className="dev-profile__avatar"
                />
                <span className="dev-profile__name">Om Rajpure</span>
            </div>

            <AnimatePresence>
                {isHovered && (
                    <motion.div
                        className="dev-profile__dropdown glass"
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                        transition={{ duration: 0.2 }}
                    >
                        <div className="dev-profile__info">
                            <img
                                src="https://github.com/omrajpure.png"
                                alt="Om Rajpure"
                                className="dev-profile__info-img"
                            />
                            <h4>Om Rajpure</h4>
                            <p className="text-muted">Fullstack Developer & UI/UX Architect</p>
                        </div>

                        <div className="dev-profile__socials">
                            {SOCIAL_LINKS.map((link, i) => (
                                <a
                                    key={i}
                                    href={link.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="dev-profile__social-link"
                                    style={{ '--social-color': link.color }}
                                >
                                    <link.icon />
                                </a>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
