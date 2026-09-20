'use client';

import React from 'react';
import { EventItem } from '../lib/types';
import { ArrowRight } from 'lucide-react';

interface RecentEventsTableProps {
  events: EventItem[];
  selectedEventId: string | null;
  onSelectEvent: (eventId: string) => void;
}

export const RecentEventsTable: React.FC<RecentEventsTableProps> = ({
  events,
  selectedEventId,
  onSelectEvent,
}) => {
  // Sort descending by last_seen
  const displayEvents = [...events].slice(0, 5);

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'Critical':
      case 'High':
        return 'bg-red-50 text-red-700 border border-red-200/80';
      case 'Medium':
        return 'bg-amber-50 text-amber-800 border border-amber-200/80';
      case 'Low':
      default:
        return 'bg-emerald-50 text-emerald-700 border border-emerald-200/80';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Needs Verification':
      case 'Under Verification':
        return 'bg-amber-50 text-amber-700 border border-amber-200/80';
      case 'Monitoring':
        return 'bg-indigo-50 text-indigo-700 border border-indigo-200/80';
      case 'Active':
        return 'bg-red-50 text-red-600 border border-red-200/80';
      case 'Confirmed':
        return 'bg-emerald-50 text-emerald-700 border border-emerald-200/80';
      default:
        return 'bg-slate-100 text-slate-600 border border-slate-200';
    }
  };

  return (
    <div className="bg-white border border-slate-200/90 rounded-xl overflow-hidden shadow-sm mt-4">
      {/* Top Header Controls */}
      <div className="px-4 py-3 border-b border-slate-100 flex items-center justify-between bg-slate-50/40">
        <div className="flex items-center gap-2">
          <h3 className="text-xs font-bold text-slate-900">Recent Events</h3>
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
            {events.length} Active
          </span>
        </div>
        <button className="text-[11px] font-bold text-indigo-600 hover:text-indigo-700 flex items-center gap-1 transition-colors group">
          View All <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
        </button>
      </div>

      {/* Horizontal Scroll Wrapper */}
      <div className="overflow-x-auto w-full">
        <div className="min-w-[910px]">
          {/* Shared CSS Grid Header */}
          <div className="grid grid-cols-[140px_190px_1fr_1fr_100px_140px_140px] items-center px-4 py-2.5 border-b border-slate-100 bg-slate-50/80 text-[10px] font-bold uppercase tracking-wider text-slate-500">
            <div>Event ID</div>
            <div>Date & Time (IST)</div>
            <div>Location</div>
            <div>Classification</div>
            <div>Priority</div>
            <div>Status</div>
            <div>Source</div>
          </div>

          {/* Shared CSS Grid Data Rows */}
          <div className="divide-y divide-slate-100">
            {displayEvents.map((ev) => {
              const isSelected = ev.event_id === selectedEventId;
              const dateStr = ev.last_seen ? new Date(ev.last_seen).toLocaleDateString('en-GB', {
                day: '2-digit',
                month: 'short',
                year: 'numeric'
              }) : 'Unknown';
              const timeStr = ev.last_seen ? new Date(ev.last_seen).toLocaleTimeString('en-GB', {
                hour: '2-digit',
                minute: '2-digit'
              }) : '--:--';

              return (
                <div
                  key={ev.event_id}
                  onClick={() => onSelectEvent(ev.event_id)}
                  className={`grid grid-cols-[140px_190px_1fr_1fr_100px_140px_140px] items-center px-4 py-2.5 min-h-[48px] text-xs cursor-pointer transition-all duration-150 ${
                    isSelected
                      ? 'bg-indigo-50/70 border-l-4 border-indigo-600 font-semibold'
                      : 'hover:bg-slate-50/90'
                  }`}
                >
                  {/* ID (140px, single line, indigo text) */}
                  <div className="whitespace-nowrap font-bold text-indigo-600 hover:text-indigo-800">
                    {ev.event_id}
                  </div>

                  {/* Date & Time (190px, single line) */}
                  <div className="whitespace-nowrap text-slate-600 text-[11px] font-medium">
                    {dateStr}, {timeStr}
                  </div>

                  {/* Location (1fr, max 2 lines) */}
                  <div className="line-clamp-2 text-slate-800 font-semibold pr-3">
                    {ev.location}
                  </div>

                  {/* Classification (1fr, max 2 lines) */}
                  <div className="line-clamp-2 text-slate-700 font-medium pr-3">
                    {ev.classification}
                  </div>

                  {/* Priority (100px, single line pill) */}
                  <div className="whitespace-nowrap flex items-center">
                    <span className={`h-6 inline-flex items-center justify-center text-[10px] font-bold px-2.5 rounded-md ${getPriorityBadge(ev.priority)}`}>
                      {ev.priority}
                    </span>
                  </div>

                  {/* Status (140px, single line pill) */}
                  <div className="whitespace-nowrap flex items-center">
                    <span className={`h-6 inline-flex items-center justify-center text-[10px] font-bold px-2.5 rounded-md ${getStatusBadge(ev.status)}`}>
                      {ev.status}
                    </span>
                  </div>

                  {/* Source (140px) */}
                  <div className="whitespace-nowrap text-slate-600 font-semibold pr-3 text-[10px]">
                    SATELLITE (MULTI)
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
