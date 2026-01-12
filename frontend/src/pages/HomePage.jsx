import React from 'react';
import { Upload, CheckCircle, AlertCircle, ChevronRight, XCircle } from 'lucide-react';

const HomePage = ({ file, handleFileUpload, handleAnalyze, cancelAnalysis, loading, progressMessage, error }) => {
    return (
        <div className="max-w-3xl mx-auto py-12 px-4">
            <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-slate-900 tracking-tight mb-4">Welcome back, User</h2>
                <p className="text-slate-500 text-lg">Upload your latest leads CSV to Generate AI-driven insights.</p>
            </div>

            <div className="bg-white rounded-2xl border-2 border-dashed border-slate-300 p-12 text-center hover:border-primary-500 transition-colors group cursor-pointer relative shadow-sm">
                <input
                    type="file"
                    onChange={handleFileUpload}
                    accept=".csv"
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                <div className="w-16 h-16 bg-primary-50 text-primary-600 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                    {file ? <CheckCircle size={32} /> : <Upload size={32} />}
                </div>
                {file ? (
                    <div>
                        <p className="text-xl font-semibold text-slate-800 mb-1">{file.name}</p>
                        <p className="text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
                    </div>
                ) : (
                    <div>
                        <p className="text-xl font-semibold text-slate-800 mb-1">Click to upload or drag and drop</p>
                        <p className="text-slate-500">CSV files only (max 50MB)</p>
                    </div>
                )}
            </div>

            {file && (
                <div className="mt-8 flex justify-center items-center gap-4">
                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-xl font-medium shadow-lg shadow-primary-200 transition-all flex items-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                <span>{progressMessage || 'Processing...'}</span>
                            </>
                        ) : (
                            <>
                                <span>Analyze Leads</span>
                                <ChevronRight size={18} />
                            </>
                        )}
                    </button>

                    {loading && (
                        <button
                            onClick={cancelAnalysis}
                            className="text-red-500 hover:text-red-700 font-medium px-4 py-2 flex items-center gap-2"
                        >
                            <XCircle size={18} /> Cancel
                        </button>
                    )}
                </div>
            )}

            {error && (
                <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-xl border border-red-200 flex items-center gap-3">
                    <AlertCircle size={20} />
                    <p>{error}</p>
                </div>
            )}
        </div>
    );
};

export default HomePage;
