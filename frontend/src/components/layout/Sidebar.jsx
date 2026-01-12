import React from 'react';
import { Home, BarChart2, MessageSquare, Clock, X } from 'lucide-react';
import { cn } from '../../lib/utils'; // Assuming we'll create utils

const Sidebar = ({ currentView, setView, isMobileOpen, setIsMobileOpen }) => {
    const navItems = [
        { id: 'home', label: 'Upload Data', icon: Home },
        { id: 'dashboard', label: 'Dashboard', icon: BarChart2 },
        { id: 'chat', label: 'AI Assistant', icon: MessageSquare },
        { id: 'history', label: 'History', icon: Clock },
    ];

    return (
        <>
            {/* Mobile Overlay */}
            {isMobileOpen && (
                <div
                    className="fixed inset-0 bg-slate-900/20 z-20 lg:hidden backdrop-blur-sm"
                    onClick={() => setIsMobileOpen(false)}
                />
            )}

            {/* Sidebar Container */}
            <aside className={cn(
                "fixed lg:static inset-y-0 left-0 z-30 w-64 bg-white text-slate-600 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 border-r border-slate-200",
                isMobileOpen ? "translate-x-0" : "-translate-x-full"
            )}>
                <div className="h-16 bg-primary-600 flex items-center justify-between px-6 shadow-md z-10">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center text-white font-bold shadow-sm backdrop-blur-sm border border-white/20">
                            AI
                        </div>
                        <span className="text-lg font-bold text-white tracking-tight">LeadPrioritizer</span>
                    </div>
                    <button onClick={() => setIsMobileOpen(false)} className="lg:hidden text-primary-100 hover:text-white">
                        <X size={20} />
                    </button>
                </div>

                <nav className="flex-1 px-4 py-4 space-y-1">
                    {navItems.map((item) => (
                        <button
                            key={item.id}
                            onClick={() => {
                                setView(item.id);
                                setIsMobileOpen(false);
                            }}
                            className={cn(
                                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                                currentView === item.id
                                    ? "bg-primary-50 text-primary-700 shadow-sm ring-1 ring-primary-100"
                                    : "hover:bg-slate-50 hover:text-slate-900"
                            )}
                        >
                            <item.icon size={18} className={cn(currentView === item.id ? "text-primary-700" : "text-slate-400 group-hover:text-slate-600")} />
                            {item.label}
                        </button>
                    ))}
                </nav>

                {/* User Profile removed */}
            </aside>
        </>
    );
};

export default Sidebar;
