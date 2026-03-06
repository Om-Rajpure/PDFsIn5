import { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiUploadCloud, FiFile, FiX, FiPlus, FiAlertCircle } from 'react-icons/fi';
import '../styles/upload.css';

/**
 * FileUploader — drag-and-drop upload zone with upload progress.
 *
 * Props:
 *   accept      — accepted MIME / extension string (default '.pdf')
 *   multiple    — allow multiple files (default false)
 *   maxSizeMB   — client-side max file size in MB (default 50)
 *   files       — controlled list of File objects
 *   onChange    — fn(files: File[]) called when list changes
 *   uploading   — boolean: show upload progress bar (from parent)
 *   uploadPct   — 0-100 upload percentage (from parent)
 *   uploadError — string error from parent to display inline
 *   label       — custom primary label
 */
export default function FileUploader({
    accept = '.pdf,application/pdf',
    multiple = false,
    maxSizeMB = 50,
    files = [],
    onChange,
    uploading = false,
    uploadPct = 0,
    uploadError = null,
    label,
}) {
    const [dragging, setDragging] = useState(false);
    const [sizeError, setSizeError] = useState(null);
    const inputRef = useRef(null);

    const fmt = (bytes) => {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    };

    const addFiles = useCallback((incoming) => {
        setSizeError(null);
        const maxBytes = maxSizeMB * 1024 * 1024;
        const oversized = [];
        const valid = [];

        Array.from(incoming).forEach((f) => {
            if (f.size > maxBytes) oversized.push(f.name);
            else valid.push(f);
        });

        if (oversized.length) {
            setSizeError(
                `${oversized.join(', ')} exceeds the ${maxSizeMB} MB limit and was removed.`
            );
        }
        if (!valid.length) return;

        const next = multiple ? [...files, ...valid] : [valid[0]];
        onChange?.(next);
    }, [files, multiple, maxSizeMB, onChange]);

    const remove = (idx) => {
        const next = files.filter((_, i) => i !== idx);
        onChange?.(next);
        if (inputRef.current) inputRef.current.value = '';
        setSizeError(null);
    };

    const onDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        addFiles(e.dataTransfer.files);
    };

    const hasFiles = files.length > 0;
    const errorMsg = uploadError || sizeError;
    const isUploading = uploading;
    const showProgress = isUploading && uploadPct > 0;

    return (
        <div className="file-uploader-container">
            {/* Drop zone */}
            <motion.div
                className={[
                    'file-uploader',
                    dragging ? 'file-uploader--drag' : '',
                    isUploading ? 'file-uploader--busy' : '',
                    errorMsg ? 'file-uploader--has-error' : '',
                ].filter(Boolean).join(' ')}
                onDragOver={(e) => { e.preventDefault(); if (!isUploading) setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => { if (!isUploading) onDrop(e); }}
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
                    disabled={isUploading}
                    onChange={(e) => e.target.files?.length && addFiles(e.target.files)}
                />

                <label
                    htmlFor={isUploading ? undefined : 'file-uploader-input'}
                    className="file-uploader__zone"
                    style={{ cursor: isUploading ? 'default' : 'pointer' }}
                >
                    {/* Icon */}
                    <AnimatePresence mode="wait">
                        {isUploading ? (
                            <motion.div
                                key="uploading-icon"
                                className="file-uploader__icon-wrap file-uploader__icon-wrap--busy"
                                initial={{ scale: 0.8, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0.8, opacity: 0 }}
                            >
                                <motion.div
                                    className="file-uploader__spinner"
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                                />
                            </motion.div>
                        ) : (
                            <motion.div
                                key="idle-icon"
                                className="file-uploader__icon-wrap"
                                animate={dragging ? { y: -6, scale: 1.12 } : { y: 0, scale: 1 }}
                                transition={{ type: 'spring', stiffness: 300, damping: 18 }}
                                initial={{ scale: 0.8, opacity: 0 }}
                                exit={{ scale: 0.8, opacity: 0 }}
                            >
                                <FiUploadCloud />
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Text */}
                    <AnimatePresence mode="wait">
                        {isUploading ? (
                            <motion.div
                                key="uploading-text"
                                initial={{ opacity: 0, y: 4 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                style={{ textAlign: 'center' }}
                            >
                                <p className="file-uploader__primary">
                                    Uploading…&nbsp;
                                    <motion.span
                                        style={{ color: 'var(--color-primary)', fontVariantNumeric: 'tabular-nums' }}
                                        animate={{ opacity: [1, 0.7, 1] }}
                                        transition={{ duration: 1.2, repeat: Infinity }}
                                    >
                                        {uploadPct}%
                                    </motion.span>
                                </p>
                                <p className="file-uploader__secondary">Please wait while your file uploads…</p>
                            </motion.div>
                        ) : dragging ? (
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
                                    {label || 'Drag & Drop your file here'}
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

                {/* Upload progress bar */}
                <AnimatePresence>
                    {showProgress && (
                        <motion.div
                            className="file-uploader__progress"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                        >
                            <motion.div
                                className="file-uploader__progress-fill"
                                initial={{ scaleX: 0 }}
                                animate={{ scaleX: uploadPct / 100 }}
                                style={{ originX: 0 }}
                                transition={{ ease: 'easeOut', duration: 0.2 }}
                            />
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>

            {/* Inline error banner */}
            <AnimatePresence>
                {errorMsg && (
                    <motion.div
                        className="file-uploader__error"
                        initial={{ opacity: 0, y: -6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.22 }}
                    >
                        <FiAlertCircle />
                        <span>{errorMsg}</span>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* File list */}
            <AnimatePresence>
                {hasFiles && !isUploading && (
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
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -10 }}
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

                        {/* Add more (multiple mode) */}
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
