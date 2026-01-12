import React from 'react';
import { Menu, Search, Bell } from 'lucide-react';
import { cn } from '../../lib/utils'; // Adjust path if needed

const Header = ({ title, setIsMobileOpen, searchQuery, setSearchQuery, handleSearch, notifications, markRead, isNotiOpen, setIsNotiOpen }) => {
    return (
        <header className="bg-primary-600 border-b border-primary-700 h-16 px-6 flex items-center justify-between z-10 w-full shadow-md">
            <div className="flex items-center gap-4">
                <button onClick={() => setIsMobileOpen(true)} className="lg:hidden text-primary-100 hover:text-white">
                    <Menu size={24} />
                </button>
                <h1 className="text-xl font-bold text-white">{title}</h1>
            </div>
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-4">
                    {/* Search and Notifications removed */}
                </div>
            </div>
        </header>
    );
};
export default Header;
