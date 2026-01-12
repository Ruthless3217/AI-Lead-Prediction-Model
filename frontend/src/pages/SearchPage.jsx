import React, { useState } from 'react';
import client from '../api/client';
import { Search } from 'lucide-react';
import { cn } from '../lib/utils';
// Note: We might want to move these to a separate component later if reused

const SearchPage = ({ searchQuery }) => {
    const [searchResults, setSearchResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [touched, setTouched] = useState(false);

    // Effect to trigger search when query changes (or could be prop based)
    React.useEffect(() => {
        const search = async () => {
            if (!searchQuery.trim()) return;
            setLoading(true);
            setTouched(true);
            try {
                const res = await client.get(`/search?q=${searchQuery}`);
                setSearchResults(res.data.results);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        // Debounce could be added here
        const handler = setTimeout(search, 300);
        return () => clearTimeout(handler);
    }, [searchQuery]);


    return (
        <div className="max-w-7xl mx-auto space-y-6">
            <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                <Search size={24} className="text-primary-600" />
                Results for "{searchQuery}"
            </h2>

            {loading ? (
                <div className="text-center py-12 text-slate-500">Searching...</div>
            ) : (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead className="bg-slate-50 text-slate-500 text-xs uppercase font-semibold">
                                <tr>
                                    <th className="px-6 py-4">Lead Source</th>
                                    <th className="px-6 py-4">Company</th>
                                    <th className="px-6 py-4">Score</th>
                                    <th className="px-6 py-4">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {searchResults.length === 0 ? (
                                    <tr>
                                        <td colSpan={4} className="p-8 text-center text-slate-500">
                                            {touched ? 'No matches found.' : 'Enter a search term.'}
                                        </td>
                                    </tr>
                                ) : (
                                    searchResults.map((lead, i) => (
                                        <tr key={i} className="hover:bg-slate-50 transition-colors">
                                            <td className="px-6 py-4 font-medium text-slate-900">{lead.source || 'Unknown'}</td>
                                            <td className="px-6 py-4 text-slate-500">{lead.company}</td>
                                            <td className="px-6 py-4">
                                                <span className="font-mono font-bold text-primary-600">
                                                    {lead.score ? (lead.score * 100).toFixed(0) : '0'}%
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={cn(
                                                    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                                                    lead.priority === 'High' ? "bg-orange-100 text-orange-800" : "bg-slate-100 text-slate-600"
                                                )}>
                                                    {lead.priority || 'Standard'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SearchPage;
