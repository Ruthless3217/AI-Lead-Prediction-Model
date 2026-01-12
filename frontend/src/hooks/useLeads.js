import { useState, useRef } from 'react';
import axios from 'axios';
import client from '../api/client';

export const useLeads = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [progressMessage, setProgressMessage] = useState('');
    const [error, setError] = useState('');
    const [metrics, setMetrics] = useState(null);
    const [highPriorityLeads, setHighPriorityLeads] = useState([]);
    const [allLeads, setAllLeads] = useState([]);
    const [currentFilename, setCurrentFilename] = useState('');

    // For Cancellation
    const abortControllerRef = useRef(null);
    const [uploadProgress, setUploadProgress] = useState(0); // Progress bar support if needed

    const handleFileUpload = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            if (!selected.name.toLowerCase().endsWith('.csv')) {
                setError("Invalid file type. Please upload a CSV.");
                setFile(null);
                return;
            }
            if (selected.size > 50 * 1024 * 1024) { // 50MB
                setError("File too large. Max 50MB.");
                setFile(null);
                return;
            }
            setFile(selected);
            setError('');
        }
    };

    const cancelAnalysis = () => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
            setLoading(false);
            setProgressMessage('Cancelled.');
            // Optional: Notification toast here
        }
    };

    const analyzeLeads = async () => {
        if (!file) return;

        setLoading(true);
        setError('');

        // Create new cancellation token
        abortControllerRef.current = new AbortController();
        const signal = abortControllerRef.current.signal;

        try {
            setProgressMessage('Uploading...');
            const formData = new FormData();
            formData.append('file', file);

            await client.post('/upload', formData, {
                signal,
                onUploadProgress: (progressEvent) => {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setUploadProgress(percentCompleted);
                }
            });

            if (signal.aborted) return;

            setProgressMessage('Processing...');
            await client.post('/train', { filename: file.name, target_col: 'Converted' }, { signal });

            if (signal.aborted) return;

            setProgressMessage('Analyzing...');
            const predictRes = await client.post('/predict', { filename: file.name }, { signal });

            const leads = predictRes.data.results;
            const high = leads.filter(l => l.priority === 'High');
            const medium = leads.filter(l => l.priority === 'Medium');
            const low = leads.filter(l => l.priority === 'Low');

            setAllLeads(leads);
            setHighPriorityLeads(high);
            setCurrentFilename(predictRes.data.filename);

            setMetrics({
                total: leads.length,
                high: high.length,
                medium: medium.length,
                low: low.length,
                accuracy: predictRes.data.accuracy_metrics
            });

            return true; // Success

        } catch (err) {
            if (axios.isCancel(err)) {
                console.log('Request canceled', err.message);
            } else {
                console.error(err);

                // Robust Error Handling for Objects/Arrays
                let errMsg = "Failed to process file.";
                const detail = err.response?.data?.detail;
                const message = err.response?.data?.message;

                if (typeof detail === 'string') {
                    errMsg = detail;
                } else if (Array.isArray(detail)) {
                    // Start of complex validation error
                    errMsg = detail.map(e => `${e.loc ? e.loc.join('.') : 'Field'}: ${e.msg}`).join(', ');
                } else if (typeof detail === 'object' && detail !== null) {
                    // Single object error
                    errMsg = detail.msg || JSON.stringify(detail);
                } else if (message) {
                    errMsg = message;
                }

                setError(errMsg);
            }
            return false;
        } finally {
            // Only unset loading if not aborted (or handled above)
            if (abortControllerRef.current && !abortControllerRef.current.signal.aborted) {
                setLoading(false);
            }
            // Cleaning up the controller if finished normally
            abortControllerRef.current = null;
            setProgressMessage('');
        }
    };

    return {
        file,
        handleFileUpload,
        analyzeLeads,
        cancelAnalysis,
        loading,
        progressMessage,
        error,
        metrics,
        allLeads,
        highPriorityLeads,
        currentFilename,
        setMetrics, // Allow manual updates (e.g. from history)
        setAllLeads,
        setHighPriorityLeads,
        setCurrentFilename
    };
};
