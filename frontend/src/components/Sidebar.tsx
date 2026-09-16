'use client';

import React from 'react';
import {
  LayoutDashboard,
  MapPin,
  Flame,
  BarChart3,
  Factory,
  History,
  FileText,
  Settings,
  HelpCircle,
  ShieldCheck
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onTabChange }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'map', label: 'Live Map', icon: MapPin },
    { id: 'events', label: 'Events', icon: Flame },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'facilities', label: 'Facilities', icon: Factory },
    { id: 'history', label: 'Historical Search', icon: History },
    { id: 'reports', label: 'Reports', icon: FileText },
  ];

  return (
    <aside className="w-56 bg-white border-r border-slate-200 flex flex-col justify-between py-4 px-3 select-none flex-shrink-0">
      <div className="space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-blue-50/80 text-blue-700 font-semibold border border-blue-100/60 shadow-xs'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="space-y-4 pt-4 border-t border-slate-100">
        <div className="space-y-1">
          <button
            onClick={() => onTabChange('settings')}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors"
          >
            <Settings className="w-4 h-4 text-slate-400" />
            <span>Settings</span>
          </button>
          <button
            onClick={() => onTabChange('help')}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-50 transition-colors"
          >
            <HelpCircle className="w-4 h-4 text-slate-400" />
            <span>Help & Support</span>
          </button>
        </div>

        {/* Footer Mission Badge */}
        <div className="p-3 bg-gradient-to-br from-slate-50 to-blue-50/30 border border-slate-200/80 rounded-xl text-center">
          <div className="flex justify-center mb-1.5 text-blue-600">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div className="text-[11px] font-semibold text-slate-800 leading-tight">
            A Safer India
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            From Space to Ground
          </div>
        </div>
      </div>
    </aside>
  );
};
