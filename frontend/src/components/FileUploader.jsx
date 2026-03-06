import { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiUploadCloud, FiFile, FiX, FiPlus } from 'react-icons/fi';
import '../styles/upload.css';

/**
 * FileUploader — drag-and-drop upload zone.
 *
 * Props:
 *   accept     — accepted MIME / extension string (default '.pdf')
 *   multiple   — allow multiple files (default false)
 *   maxSizeMB  — max file size per file in MB (default 100)
 *   files      — controlled list of File objects
 *   onChange   — fn(files: File[]) called when list changes
 *   label      — custom primary label
 */
export default function FileUploader({
    accept = '.pdf,application/pdf',
    multiple = false,
    maxSizeMB = 100,
    files = [],
    onChange,
    label,
}) {
    const [dragging, setDragging] = useState(false);
    const inputRef = useRef(null);

    const fmt = (bytes) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    const addFiles = useCallback((incoming) => {
        const list = Array.from(incoming).filter(
            (f) => f.size <= maxSizeMB * 1024 * 1024,
        );
        if (!list.length) return;
        const next = multiple ? [...files, ...list] : [list[0]];
        onChange?.(next);
    }, [files, multiple, maxSizeMB, onChange]);

    const remove = (idx) => {
        const next = files.filter((_, i) => i !== idx);
        onChange?.(next);
        if (inputRef.current) inputRef.current.value = '';
    };

    const onDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        addFiles(e.dataTransfer.files);
    };

    const hasFiles = files.length > 0;

    return (
        <div className="file-uploader-container">
            {/* Drop zone */}
            <motion.div
                className={[
                    'file-uploader',
                    dragging ? 'file-uploader--drag' : '',
                ].filter(Boolean).join(' ')}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={onDrop}
                animate={dragging ? { scale: 1.01 } : { scale: 1 }}
                transition={{ type: 'spring', stiffness: 400, damping: 28 }}
            >
                <input
                    ref={inputRef}
                    id="file-uploader-input"
                    type="file"
                    accept={accept}
                    multiple={multiple}
                    className="file-uploader__input"
                    onChange={(e) => e.target.files?.length && addFiles(e.target.files)}
                />

                <label htmlFor="file-uploader-input" className="file-uploader__zone">
                    {/* Icon */}
                    <motion.div
                        className="file-uploader__icon-wrap"
                        animate={dragging ? { y: -6, scale: 1.1 } : { y: 0, scale: 1 }}
                        transition={{ type: 'spring', stiffness: 300, damping: 18 }}
                    >
                        <FiUploadCloud />
                    </motion.div>

                    {/* Text */}
                    <AnimatePresence mode="wait">
                        {dragging ? (
                            <motion.p
                                key="drop"
                                className="file-uploader__drop-hint"
                                initial={{ opacity: 0, y: 6 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                            >
                                Drop files here!
                            </motion.p>
                        ) : (
                            <motion.div
                                key="idle"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                style={{ textAlign: 'center' }}
                            >
                                <p className="file-uploader__primary">
                                    {label || 'Drag & Drop your PDF file here'}
                                </p>
                                <p className="file-uploader__secondary">
                                    or <span>click to browse</span> from your device
                                </p>
                                <p className="file-uploader__limit">
                                    Up to {maxSizeMB} MB per file
                                    {multiple ? ' · Multiple files allowed' : ''}
                                </p>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </label>
            </motion.div>

            {/* File list */}
            <AnimatePresence>
                {hasFiles && (
                    <motion.div
                        className="file-uploader__list"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.22 }}
                    >
                        {files.map((f, i) => (
                            <motion.div
                                key={`${f.name}-${i}`}
                                className="file-uploader__row"
                                initial={{ opacity: 0, x: -12 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -12 }}
                                transition={{ delay: i * 0.04 }}
                            >
                                <FiFile className="file-uploader__row-icon" />
                                <span className="file-uploader__row-name" title={f.name}>{f.name}</span>
                                <span className="file-uploader__row-size">{fmt(f.size)}</span>
                                <button
                                    className="file-uploader__row-remove"
                                    onClick={() => remove(i)}
                                    aria-label={`Remove ${f.name}`}
                                >
                                    <FiX />
                                </button>
                            </motion.div>
                        ))}

                        {/* Add more (if multiple) */}
                        {multiple && (
                            <label htmlFor="file-uploader-input" className="file-uploader__add-more">
                                <FiPlus /> Add more files
                            </label>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
