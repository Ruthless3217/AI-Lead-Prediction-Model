import React from 'react';
import { cn } from '../../lib/utils';

const StatCard = ({ label, value, subtext, type, icon: Icon }) => {
    const styles = {
        fire: "text-orange-600 bg-orange-50 border-orange-100",
        success: "text-emerald-600 bg-emerald-50 border-emerald-100",
        warning: "text-amber-600 bg-amber-50 border-amber-100",
        neutral: "text-slate-600 bg-slate-50 border-slate-100",
        primary: "text-primary-600 bg-primary-50 border-primary-100"
    };

    const currentStyle = styles[type] || styles.neutral;

    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm font-medium text-slate-500 mb-1">{label}</p>
                    <h3 className="text-3xl font-bold text-slate-800 tracking-tight">{value}</h3>
                </div>
                <div className={cn("p-3 rounded-xl", currentStyle)}>
                    <Icon size={24} />
                </div>
            </div>
            {subtext && <p className="text-sm text-slate-500 mt-3 font-medium">{subtext}</p>}
        </div>
    );
};

export default StatCard;
