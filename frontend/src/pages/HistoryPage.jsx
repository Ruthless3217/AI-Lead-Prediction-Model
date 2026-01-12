import React, { useEffect, useState } from 'react';
import client from '../api/client';
import { Clock, FileText, ChevronRight, Loader2 } from 'lucide-react';

const HistoryPage = ({ setView, handleHistoryClick, loadingHistoryId }) => {
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await client.get('/prediction-history');
                setHistory(res.data.history);
            } catch (e) {
                console.error(e);
            }
        };
        fetchHistory();
    }, []);

    // We can add caching here or in a hook later.
    // For now, implementing the UI.

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-slate-800">Prediction History</h2>
                {/* Refresh can be added here */}
            </div>

            {history.length === 0 ? (
                <div className="text-center py-12 bg-white border border-slate-200 rounded-xl">
                    <Clock className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                    <p className="text-slate-500">No history available yet.</p>
                    <button onClick={() => setView('home')} className="mt-4 text-primary-600 font-medium">Start your first analysis</button>
                </div>
            ) : (
                <div className="grid gap-4">
                    {history.map((run) => {
                        const isLoading = loadingHistoryId === run.run_id;
                        return (
                            <div
                                key={run.run_id}
                                onClick={() => !isLoading && handleHistoryClick(run.run_id)}
                                className={`bg-white p-6 rounded-xl border border-slate-200 hover:shadow-md transition-shadow cursor-pointer flex items-center justify-between group ${isLoading ? 'opacity-70 pointer-events-none' : ''}`}
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-lg bg-primary-50 text-primary-600 flex items-center justify-center">
                                        <FileText size={24} />
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-slate-800">{run.filename}</h4>
                                        <p className="text-xs text-slate-500">{new Date(run.timestamp).toLocaleString()}</p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-8">
                                    <div className="text-center">
                                        <p className="text-xs text-slate-400 uppercase font-bold">Leads</p>
                                        <p className="font-bold text-slate-700">{run.total_leads}</p>
                                    </div>
                                    <div className="text-center">
                                        <p className="text-xs text-slate-400 uppercase font-bold">High Prio</p>
                                        <p className="font-bold text-primary-600">{run.high_priority_count}</p>
                                    </div>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            if (!isLoading) handleHistoryClick(run.run_id);
                                        }}
                                        disabled={isLoading}
                                        className="p-2 hover:bg-slate-100 rounded-full transition-colors"
                                    >
                                        {isLoading ? (
                                            <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />
                                        ) : (
                                            <ChevronRight className="text-slate-300 group-hover:text-primary-500 transition-colors" />
                                        )}
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

export default HistoryPage;
