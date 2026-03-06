import { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiUploadCloud, FiCheckCircle, FiAlertCircle, FiX } from 'react-icons/fi';
import api from '../lib/axios';
import './UploadBox.css';

/**
 * UploadBox — animated drag-and-drop file uploader.
 *
 * Props:
 *  accept      — MIME types string  (default '*')
 *  multiple    — allow multiple files
 *  endpoint    — API endpoint path  (default '/upload')
 *  hint        — helper text below the main label
 *  onSuccess   — callback(data) after successful upload
 *  onError     — callback(err) on failure
 */
export default function UploadBox({
    accept = '*/*',
    multiple = false,
    endpoint = '/upload',
    hint,
    onSuccess,
    onError,
}) {
    const [dragging, setDragging] = useState(false);
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState(null); // 'success' | 'error'
    const [result, setResult] = useState(null);
    const inputRef = useRef(null);

    const reset = () => {
        setFiles([]); setStatus(null); setResult(null); setProgress(0);
        if (inputRef.current) inputRef.current.value = '';
    };

    const handleFiles = useCallback(async (selected) => {
        const list = Array.from(selected);
        setFiles(list);
        setStatus(null);
        setResult(null);
        setUploading(true);
        setProgress(0);

        try {
            const formData = new FormData();
            list.forEach((f) => formData.append('file', f));
            const res = await api.post(endpoint, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                onUploadProgress: (e) =>
                    e.total && setProgress(Math.round((e.loaded * 100) / e.total)),
            });
            setResult(res.data);
            setStatus('success');
            onSuccess?.(res.data);
        } catch (err) {
            setStatus('error');
            onError?.(err);
        } finally {
            setUploading(false);
        }
    }, [endpoint, onSuccess, onError]);

    const onDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
    };

    return (
        <motion.div
            className={[
                'upload-box',
                dragging ? 'upload-box--drag' : '',
                uploading ? 'upload-box--busy' : '',
                status === 'success' ? 'upload-box--success' : '',
                status === 'error' ? 'upload-box--error' : '',
            ].filter(Boolean).join(' ')}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
        >
            {/* Hidden native file input */}
            <input
                ref={inputRef}
                type="file"
                id="upload-input"
                accept={accept}
                multiple={multiple}
                className="upload-box__input"
                onChange={(e) => e.target.files?.length && handleFiles(e.target.files)}
            />

            {/* Main clickable zone */}
            <label htmlFor="upload-input" className="upload-box__zone">
                {/* Animated icon */}
                <motion.div
                    className="upload-box__icon-wrap"
                    animate={dragging ? { scale: 1.15, y: -6 } : { scale: 1, y: 0 }}
                    transition={{ type: 'spring', stiffness: 300, damping: 18 }}
                >
                    <FiUploadCloud className="upload-box__icon" />
                </motion.div>

                <AnimatePresence mode="wait">
                    {uploading ? (
                        <motion.span
                            key="uploading"
                            className="upload-box__label"
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        >
                            Uploading…&nbsp;<strong>{progress}%</strong>
                        </motion.span>
                    ) : status === 'success' ? (
                        <motion.span
                            key="success"
                            className="upload-box__label upload-box__label--success"
                            initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                        >
                            <FiCheckCircle /> {result?.original_filename || 'File uploaded'}
                        </motion.span>
                    ) : status === 'error' ? (
                        <motion.span
                            key="error"
                            className="upload-box__label upload-box__label--error"
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        >
                            <FiAlertCircle /> Upload failed — please try again.
                        </motion.span>
                    ) : (
                        <motion.span
                            key="idle"
                            className="upload-box__label"
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        >
                            {dragging ? 'Drop files to upload' : 'Drag & Drop files here'}
                        </motion.span>
                    )}
                </AnimatePresence>

                <p className="upload-box__hint">
                    {hint || (uploading
                        ? 'Please wait…'
                        : 'or click to browse your files')}
                </p>
            </label>

            {/* Progress bar */}
            <AnimatePresence>
                {(uploading || progress > 0) && (
                    <motion.div
                        className="upload-box__progress-track"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        <motion.div
                            className="upload-box__progress-fill"
                            initial={{ scaleX: 0 }}
                            animate={{ scaleX: progress / 100 }}
                            style={{ originX: 0 }}
                            transition={{ duration: 0.2 }}
                        />
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Reset button */}
            {(status || files.length > 0) && !uploading && (
                <button className="upload-box__reset" onClick={reset} aria-label="Clear selection">
                    <FiX />
                </button>
            )}
        </motion.div>
    );
}
