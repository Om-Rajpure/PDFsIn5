import { motion } from 'framer-motion';
import { FiDownload, FiCheckCircle, FiRefreshCw } from 'react-icons/fi';

import { useState } from 'react';

/**
 * DownloadResult — shown when backend returns a processed file.
 *
 * Props:
 *   downloadUrl  — blob URL or server URL for the file
 *   filename     — suggested download filename
 *   fileSize     — optional file size string e.g. "1.4 MB"
 *   onReset      — callback to reset and process another file
 */
export default function DownloadResult({ downloadUrl, filename = 'result.pdf', fileSize, onReset }) {
    const isZip = filename.toLowerCase().endsWith('.zip');
    const [customFilename, setCustomFilename] = useState('');
    let downloadLabel = isZip ? 'Download ZIP' : 'Download File';
    if (filename.toLowerCase().includes('rotated')) {
        downloadLabel = 'Download Rotated PDF';
    }

    const extension = isZip ? '.zip' : filename.substring(filename.lastIndexOf('.'));
    const finalDownloadName = customFilename.trim()
        ? (customFilename.trim().toLowerCase().endsWith(extension)
            ? customFilename.trim()
            : `${customFilename.trim()}${extension}`)
        : filename;

    return (
        <motion.div
            className="download-result"
            initial={{ opacity: 0, y: 16, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.97 }}
            transition={{ duration: 0.32, ease: [0.16, 1, 0.3, 1] }}
        >
            {/* Success icon */}
            <motion.div
                className="download-result__icon"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.1, type: 'spring', stiffness: 260, damping: 18 }}
            >
                <FiCheckCircle />
            </motion.div>

            {/* Text */}
            <div className="download-result__text">
                <h3 className="download-result__heading">Your file is ready!</h3>
                <p className="download-result__sub">
                    <strong>{filename}</strong>
                    {fileSize && <span className="download-result__size"> — {fileSize}</span>}
                </p>

                <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'center' }}>
                    <label htmlFor="customName" style={{ fontSize: '0.9rem', color: 'var(--clr-text-muted)' }}>
                        Output file name:
                    </label>
                    <input
                        id="customName"
                        type="text"
                        value={customFilename}
                        onChange={(e) => setCustomFilename(e.target.value)}
                        placeholder="[ my-file-name ]"
                        style={{
                            padding: '10px 14px',
                            border: '1px solid var(--clr-border)',
                            borderRadius: '8px',
                            width: '100%',
                            maxWidth: '300px',
                            textAlign: 'center',
                            fontSize: '1rem',
                            outline: 'none'
                        }}
                    />
                </div>
            </div>

            {/* Actions */}
            <div className="download-result__actions">
                <motion.a
                    href={downloadUrl}
                    download={finalDownloadName}
                    className="btn btn--primary btn--lg download-result__btn"
                    whileHover={{ scale: 1.03, y: -1 }}
                    whileTap={{ scale: 0.97 }}
                    transition={{ type: 'spring', stiffness: 380, damping: 22 }}
                >
                    <FiDownload />
                    {downloadLabel}
                </motion.a>

                {onReset && (
                    <motion.button
                        className="btn btn--secondary download-result__reset"
                        onClick={onReset}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.97 }}
                    >
                        <FiRefreshCw />
                        Process another file
                    </motion.button>
                )}
            </div>

            {/* Privacy note */}
            <p className="download-result__privacy">
                🔒 Your file will be automatically deleted within 1 hour.
            </p>
        </motion.div>
    );
}
