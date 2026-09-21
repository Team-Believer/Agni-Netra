'use client';

import React from 'react';
import { Flame, AlertTriangle, Eye, CheckCircle2 } from 'lucide-react';
import { DashboardSummary } from '../lib/types';

interface KpiCardsProps {
  summary: DashboardSummary | null;
}

export const KpiCards: React.FC<KpiCardsProps> = ({ summary }) => {
  const totalActive = summary?.total_active ?? 12;
  const highPriority = summary?.high_priority ?? 4;
  const underVerification = summary?.under_verification ?? 3;
  const resolved24h = summary?.resolved_24h ?? 8;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5 mb-4">
      {/* 1. Total Active Events */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-3 flex items-center gap-3.5 shadow-sm hover:shadow-card-hover hover:border-red-200/80 transition-all duration-200">
        <div className="flex items-center justify-center flex-shrink-0 text-red-500">
          <Flame className="w-5 h-5 sm:w-6 sm:h-6 fill-red-500 text-red-500" />
        </div>
        <div>
          <div className="text-[11px] font-semibold text-slate-500">Total Active Events</div>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span className="text-xl font-extrabold text-slate-900 leading-tight">{totalActive}</span>
            <span className="text-[10px] font-bold text-red-600 bg-red-50 px-1.5 py-0.5 rounded border border-red-100 flex items-center">
              ↑ 3 <span className="font-medium text-slate-400 ml-1 text-[9px]">24h</span>
            </span>
          </div>
        </div>
      </div>

      {/* 2. High Priority */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-3 flex items-center gap-3.5 shadow-sm hover:shadow-card-hover hover:border-orange-200/80 transition-all duration-200">
        <div className="flex items-center justify-center flex-shrink-0 text-orange-600">
          <AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6 text-orange-600" />
        </div>
        <div>
          <div className="text-[11px] font-semibold text-slate-500">High Priority</div>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span className="text-xl font-extrabold text-slate-900 leading-tight">{highPriority}</span>
            <span className="text-[10px] font-bold text-orange-600 bg-orange-50 px-1.5 py-0.5 rounded border border-orange-100 flex items-center">
              ↑ 2 <span className="font-medium text-slate-400 ml-1 text-[9px]">24h</span>
            </span>
          </div>
        </div>
      </div>

      {/* 3. Under Verification */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-3 flex items-center gap-3.5 shadow-sm hover:shadow-card-hover hover:border-indigo-200/80 transition-all duration-200">
        <div className="flex items-center justify-center flex-shrink-0 text-indigo-600">
          <Eye className="w-5 h-5 sm:w-6 sm:h-6 text-indigo-600" />
        </div>
        <div>
          <div className="text-[11px] font-semibold text-slate-500">Under Verification</div>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span className="text-xl font-extrabold text-slate-900 leading-tight">{underVerification}</span>
            <span className="text-[10px] font-bold text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-100 flex items-center">
              ↓ 1 <span className="font-medium text-slate-400 ml-1 text-[9px]">24h</span>
            </span>
          </div>
        </div>
      </div>

      {/* 4. Resolved (24h) */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-3 flex items-center gap-3.5 shadow-sm hover:shadow-card-hover hover:border-emerald-200/80 transition-all duration-200">
        <div className="flex items-center justify-center flex-shrink-0 text-emerald-600">
          <CheckCircle2 className="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600" />
        </div>
        <div>
          <div className="text-[11px] font-semibold text-slate-500">Resolved (24h)</div>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span className="text-xl font-extrabold text-slate-900 leading-tight">{resolved24h}</span>
            <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-100 flex items-center">
              ↑ 4 <span className="font-medium text-slate-400 ml-1 text-[9px]">24h</span>
            </span>
          </div>
        </div>
      </div>

      {/* 5. Date & Time / Operational Status */}
      <div className="bg-gradient-to-br from-slate-900 to-indigo-950 text-white rounded-xl p-3 flex flex-col justify-center shadow-md relative overflow-hidden">
        <div className="absolute right-0 top-0 w-24 h-24 bg-indigo-500/10 rounded-full blur-xl pointer-events-none"></div>
        <div className="text-[10px] font-bold text-indigo-300 uppercase tracking-wider">
          System Operational
        </div>
        <div className="flex items-baseline gap-1.5 mt-0.5">
          <span className="text-xl font-extrabold tracking-tight text-white">14:32</span>
          <span className="text-[10px] font-bold text-slate-400">IST</span>
        </div>
        <div className="flex items-center gap-1.5 mt-1">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-[10px] font-semibold text-emerald-300">Spaceborne Feed Active</span>
        </div>
      </div>
    </div>
  );
};
