import React, { useState } from 'react';
import { User, Phone, BarChart2, Activity } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import StatCard from '../components/common/StatCard';
import { cn } from '../lib/utils'; // Adjust path if needed

const DashboardPage = ({ metrics, predictionHistory, allLeads, highPriorityLeads }) => {
    const [activeTab, setActiveTab] = useState('high');
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 50;

    // Reset page when tab changes
    React.useEffect(() => {
        setCurrentPage(1);
    }, [activeTab]);

    const [expandedLead, setExpandedLead] = useState(null);

    const currentMetrics = metrics || { total: 0, high: 0, medium: 0, low: 0, accuracy: 0, f1: 0, auprc: 0, precision_k: 0, recall_k: 0 };

    const getFilteredLeads = () => {
        if (activeTab === 'high') return highPriorityLeads;
        if (activeTab === 'medium') return allLeads.filter(l => l.priority === 'Medium');
        if (activeTab === 'low') return allLeads.filter(l => l.priority === 'Low');
        return allLeads;
    };

    return (
        <div className="max-w-6xl mx-auto space-y-6">
            {/* Metrics Grid */}
            {currentMetrics.drift_alert && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6 flex items-start gap-3">
                    <div className="text-amber-500 mt-0.5">
                        <Activity size={20} />
                    </div>
                    <div>
                        <h4 className="text-sm font-semibold text-amber-800">Data Drift Detected</h4>
                        <p className="text-sm text-amber-700 mt-1">
                            The data you uploaded deviates significantly from the training data (&gt;30% change in key features).
                            Predictions may be less accurate. Consider retraining the model with this new data profile.
                        </p>
                    </div>
                </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <StatCard
                    label="Total Leads"
                    value={currentMetrics.total}
                    type="primary"
                    icon={User}
                />
                <StatCard
                    label="High Priority"
                    value={currentMetrics.high}
                    subtext="Likely to convert"
                    type="fire"
                    icon={Phone}
                />
                <StatCard
                    label="Medium Priority"
                    value={currentMetrics.medium}
                    type="warning"
                    icon={BarChart2}
                />
            </div>

            <div className="grid grid-cols-1 gap-8">
                {/* Lead Generation / Priority Distribution Graph */}
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <div className="mb-6">
                        <h3 className="text-lg font-bold text-slate-800">Lead Quality Distribution</h3>
                        <p className="text-sm text-slate-500">Breakdown of leads from current CSV by priority</p>
                    </div>
                    <div className="h-[300px] w-full">
                        {allLeads && allLeads.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={[
                                    { name: 'High', value: currentMetrics.high, color: '#10b981' },
                                    { name: 'Medium', value: currentMetrics.medium, color: '#f59e0b' },
                                    { name: 'Low', value: currentMetrics.low, color: '#64748b' }
                                ]} layout="vertical" margin={{ left: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#E2E8F0" />
                                    <XAxis type="number" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                                    <YAxis
                                        dataKey="name"
                                        type="category"
                                        stroke="#64748b"
                                        fontSize={14}
                                        fontWeight={500}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <Tooltip
                                        cursor={{ fill: '#f1f5f9' }}
                                        contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                                    />
                                    <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={40}>
                                        {
                                            [
                                                { name: 'High', value: currentMetrics.high, color: '#10b981' },
                                                { name: 'Medium', value: currentMetrics.medium, color: '#f59e0b' },
                                                { name: 'Low', value: currentMetrics.low, color: '#64748b' }
                                            ].map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.color} />
                                            ))
                                        }
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full flex items-center justify-center text-slate-400">
                                <p>Process a file to see lead distribution</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Leads Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                {/* Table Header & Tabs */}
                <div className="p-6 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <h3 className="text-lg font-bold text-slate-800">Prioritized Leads</h3>

                    <div className="flex bg-slate-100 p-1 rounded-lg">
                        {['high', 'medium', 'low'].map((tab) => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={cn(
                                    "px-4 py-2 text-sm font-medium rounded-md transition-all",
                                    activeTab === tab
                                        ? "bg-white text-slate-800 shadow-sm"
                                        : "text-slate-500 hover:text-slate-700"
                                )}
                            >
                                {tab.charAt(0).toUpperCase() + tab.slice(1)} Priority
                            </button>
                        ))}
                    </div>

                    <button className="text-primary-600 text-sm font-medium hover:underline">Export CSV</button>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-slate-50">
                            <tr>
                                <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Lead ID</th>
                                <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Source</th>
                                <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Score</th>
                                <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Priority</th>
                                <th className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {getFilteredLeads().slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage).map((lead, i) => (
                                <React.Fragment key={i}>
                                    <tr className="hover:bg-slate-50 transition-colors group">
                                        <td className="px-6 py-4 text-sm font-medium text-slate-900">
                                            {lead.lead_id || lead['Lead Number'] || 'N/A'}
                                        </td>
                                        <td className="px-6 py-4 text-sm text-slate-500">
                                            {lead.Source || lead['Lead Source'] || 'Unknown'}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <div className="w-16 h-2 bg-slate-100 rounded-full overflow-hidden">
                                                    <div
                                                        className={cn("h-full rounded-full",
                                                            lead.priority === 'High' ? 'bg-emerald-500' :
                                                                lead.priority === 'Medium' ? 'bg-amber-500' : 'bg-slate-300'
                                                        )}
                                                        style={{ width: `${(lead.score || 0) * 100}%` }}
                                                    />
                                                </div>
                                                <span className="text-sm font-bold text-slate-700">{((lead.score || 0) * 100).toFixed(0)}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={cn(
                                                "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                                                lead.priority === 'High' ? "bg-emerald-100 text-emerald-800" :
                                                    lead.priority === 'Medium' ? "bg-amber-100 text-amber-800" :
                                                        "bg-slate-100 text-slate-600"
                                            )}>
                                                {lead.priority}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={() => setExpandedLead(expandedLead === i ? null : i)}
                                                className="text-primary-600 hover:text-primary-800 font-medium text-sm"
                                            >
                                                {expandedLead === i ? 'Hide' : 'Details'}
                                            </button>
                                        </td>
                                    </tr>
                                    {expandedLead === i && (
                                        <tr className="bg-slate-50">
                                            <td colSpan={5} className="px-6 py-4">
                                                <div className="p-4 bg-white rounded-lg border border-slate-200">
                                                    <h4 className="font-semibold text-slate-800 mb-2">Analysis</h4>
                                                    <p className="text-slate-600 mb-2">{lead.explanation || "No explanation available."}</p>
                                                    <div className="flex gap-4 text-sm">
                                                        <div>
                                                            <span className="text-slate-500">Next Action:</span>
                                                            <span className="ml-2 font-medium text-slate-700">{lead.next_action || 'Review Lead'}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </React.Fragment>
                            ))}
                            {getFilteredLeads().length === 0 && (
                                <tr>
                                    <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                                        No leads found in this category.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination Controls */}
                {getFilteredLeads().length > itemsPerPage && (
                    <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/50">
                        <div className="text-sm text-slate-500 font-medium">
                            Showing <span className="text-slate-900">{(currentPage - 1) * itemsPerPage + 1}</span> to <span className="text-slate-900">{Math.min(currentPage * itemsPerPage, getFilteredLeads().length)}</span> of <span className="text-slate-900">{getFilteredLeads().length}</span> results
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                                disabled={currentPage === 1}
                                className="px-4 py-2 text-sm font-medium border border-slate-300 rounded-lg bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                            >
                                Previous
                            </button>
                            <button
                                onClick={() => setCurrentPage(prev => Math.min(prev + 1, Math.ceil(getFilteredLeads().length / itemsPerPage)))}
                                disabled={currentPage >= Math.ceil(getFilteredLeads().length / itemsPerPage)}
                                className="px-4 py-2 text-sm font-medium border border-slate-300 rounded-lg bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                            >
                                Next
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DashboardPage;
