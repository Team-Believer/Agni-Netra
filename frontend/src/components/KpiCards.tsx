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
    <div className="grid grid-cols-5 gap-3.5 mb-4">
      {/* 1. Total Active Events */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-3 flex items-center gap-3.5 shadow-2xs">
        <div className="w-10 h-10 rounded-full bg-red-50 flex items-center justify-center flex-shrink-0">
          <Flame className="w-5 h-5 text-red-500 fill-red-500" />
        </div>
        <div>
          <div className="text-[11px] font-medium text-slate-500">Total Active Events</div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold text-slate-900 leading-tight">{totalActive}</span>
            <span className="text-[11px] font-semibold text-red-600 flex items-center">
              ↑ 3 <span className="font-normal text-slate-400 ml-1 text-[10px]">vs last 24h</span>
            </span>
          </div>
        </div>
      </div>

      {/* 2. High Priority */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-3 flex items-center gap-3.5 shadow-2xs">
        <div className="w-10 h-10 rounded-full bg-orange-50 flex items-center justify-center flex-shrink-0">
          <AlertTriangle className="w-5 h-5 text-red-500" />
        </div>
        <div>
          <div className="text-[11px] font-medium text-slate-500">High Priority</div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold text-slate-900 leading-tight">{highPriority}</span>
            <span className="text-[11px] font-semibold text-red-600 flex items-center">
              ↑ 2 <span className="font-normal text-slate-400 ml-1 text-[10px]">vs last 24h</span>
            </span>
          </div>
        </div>
      </div>

      {/* 3. Under Verification */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-3 flex items-center gap-3.5 shadow-2xs">
        <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0">
          <Eye className="w-5 h-5 text-blue-600" />
        </div>
        <div>
          <div className="text-[11px] font-medium text-slate-500">Under Verification</div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold text-slate-900 leading-tight">{underVerification}</span>
            <span className="text-[11px] font-semibold text-emerald-600 flex items-center">
              ↓ 1 <span className="font-normal text-slate-400 ml-1 text-[10px]">vs last 24h</span>
            </span>
          </div>
        </div>
      </div>

      {/* 4. Resolved (24h) */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-3 flex items-center gap-3.5 shadow-2xs">
        <div className="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center flex-shrink-0">
          <CheckCircle2 className="w-5 h-5 text-emerald-600" />
        </div>
        <div>
          <div className="text-[11px] font-medium text-slate-500">Resolved (24h)</div>
          <div className="flex items-baseline gap-2">
            <span className="text-xl font-bold text-slate-900 leading-tight">{resolved24h}</span>
            <span className="text-[11px] font-semibold text-emerald-600 flex items-center">
              ↑ 4 <span className="font-normal text-slate-400 ml-1 text-[10px]">vs previous 24h</span>
            </span>
          </div>
        </div>
      </div>

      {/* 5. Date & Time / Operational Status */}
      <div className="bg-white border border-slate-200/90 rounded-xl p-3 flex flex-col justify-center shadow-2xs">
        <div className="text-[11px] font-medium text-slate-500">
          Tue, 26 Nov 2024
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-xl font-bold text-slate-900 tracking-tight">14:32</span>
          <span className="text-[11px] font-semibold text-slate-500">IST</span>
        </div>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-[11px] font-medium text-emerald-700">System Operational</span>
        </div>
      </div>
    </div>
  );
};
