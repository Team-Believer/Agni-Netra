'use client';

import React from 'react';
import Link from 'next/link';
import { EventItem } from '../lib/types';
import { ArrowRight, Clock, MapPin, AlertCircle } from 'lucide-react';

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
  // Show up to 6 recent events
  const displayEvents = [...events].slice(0, 6);

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'Critical':
        return 'bg-red-50 text-red-700 border border-red-200';
      case 'High':
        return 'bg-orange-50 text-orange-700 border border-orange-200';
      case 'Medium':
        return 'bg-amber-50 text-amber-800 border border-amber-200';
      case 'Low':
      default:
        return 'bg-emerald-50 text-emerald-700 border border-emerald-200';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Needs Verification':
      case 'Under Verification':
        return 'bg-amber-50 text-amber-800 border border-amber-200';
      case 'Monitoring':
        return 'bg-blue-50 text-blue-700 border border-blue-200';
      case 'Active':
        return 'bg-red-50 text-red-600 border border-red-200';
      case 'Confirmed':
        return 'bg-emerald-50 text-emerald-700 border border-emerald-200';
      case 'Rejected':
        return 'bg-slate-100 text-slate-700 border border-slate-200';
      default:
        return 'bg-slate-100 text-slate-600 border border-slate-200';
    }
  };

  return (
    <div className="w-full bg-white border border-slate-200/90 rounded-xl overflow-hidden shadow-sm mt-4">
      {/* Card Header */}
      <div className="px-5 sm:px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-white">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-bold text-slate-900 tracking-tight">Recent Events</h3>
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200/80">
            {events.length} Active
          </span>
        </div>
        <Link
          href="/events"
          className="text-xs font-bold text-indigo-600 hover:text-indigo-800 flex items-center gap-1.5 transition-colors group"
        >
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
        </Link>
      </div>

      {/* Full-Width Desktop Table Container */}
      <div className="w-full">
        {displayEvents.length === 0 ? (
          <div className="p-8 text-center text-slate-400">
            <AlertCircle className="w-6 h-6 mx-auto mb-2 text-slate-300" />
            <p className="text-xs font-semibold text-slate-600">No recent events detected</p>
            <p className="text-[11px] text-slate-400 mt-0.5">Active satellite overpasses are nominal</p>
          </div>
        ) : (
          <table className="w-full table-fixed border-collapse">
            {/* Column Proportions Totaling 100% */}
            <colgroup>
              <col className="w-[18%]" />
              <col className="w-[16%]" />
              <col className="w-[20%]" />
              <col className="w-[17%]" />
              <col className="w-[12%]" />
              <col className="w-[17%]" />
            </colgroup>

            {/* Table Header */}
            <thead>
              <tr className="border-b border-slate-200/80 bg-slate-50/75 h-[48px] sm:h-[50px] text-[11px] sm:text-xs font-bold uppercase tracking-wider text-slate-500 text-left">
                <th scope="col" className="px-5 sm:px-6 py-3 font-bold">
                  Event ID
                </th>
                <th scope="col" className="px-4 sm:px-5 py-3 font-bold">
                  Date & Time (IST)
                </th>
                <th scope="col" className="px-4 sm:px-5 py-3 font-bold">
                  Location
                </th>
                <th scope="col" className="px-4 sm:px-5 py-3 font-bold">
                  Classification
                </th>
                <th scope="col" className="px-4 sm:px-5 py-3 font-bold">
                  Priority
                </th>
                <th scope="col" className="px-5 sm:px-6 py-3 font-bold text-left">
                  Status
                </th>
              </tr>
            </thead>

            {/* Table Body */}
            <tbody className="divide-y divide-slate-100 text-xs">
              {displayEvents.map((ev) => {
                const isSelected = ev.event_id === selectedEventId;
                const dateStr = ev.last_seen
                  ? new Date(ev.last_seen).toLocaleDateString('en-GB', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric',
                    })
                  : 'Unknown';
                const timeStr = ev.last_seen
                  ? new Date(ev.last_seen).toLocaleTimeString('en-GB', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })
                  : '--:--';

                return (
                  <tr
                    key={ev.event_id}
                    onClick={() => onSelectEvent(ev.event_id)}
                    className={`h-[60px] sm:h-[64px] cursor-pointer transition-colors duration-150 group ${
                      isSelected
                        ? 'bg-indigo-50/70 border-l-4 border-indigo-600 font-semibold'
                        : 'hover:bg-slate-50/90'
                    }`}
                  >
                    {/* 1. Event ID (18%, nowrap, bold indigo) */}
                    <td className="px-5 sm:px-6 py-3.5 whitespace-nowrap">
                      <span className="font-mono text-xs sm:text-[13px] font-black text-indigo-600 group-hover:text-indigo-800 transition-colors">
                        {ev.event_id}
                      </span>
                    </td>

                    {/* 2. Date & Time (16%, nowrap) */}
                    <td className="px-4 sm:px-5 py-3.5 whitespace-nowrap text-slate-600 font-medium text-[11px] sm:text-xs">
                      {dateStr}, {timeStr}
                    </td>

                    {/* 3. Location (20%, max 2 lines clamp) */}
                    <td className="px-4 sm:px-5 py-3.5 text-slate-800 font-semibold text-xs leading-snug">
                      <span className="line-clamp-2" title={ev.location}>
                        {ev.location}
                      </span>
                    </td>

                    {/* 4. Classification (17%, nowrap/tight) */}
                    <td className="px-4 sm:px-5 py-3.5 text-slate-700 font-medium text-xs whitespace-nowrap">
                      <span className="truncate block" title={ev.classification || ev.title}>
                        {ev.classification || ev.title}
                      </span>
                    </td>

                    {/* 5. Priority (12%, compact badge) */}
                    <td className="px-4 sm:px-5 py-3.5 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center justify-center text-[11px] font-bold px-2.5 py-1 rounded-md shadow-2xs ${getPriorityBadge(
                          ev.priority
                        )}`}
                      >
                        {ev.priority}
                      </span>
                    </td>

                    {/* 6. Status (17%, semantic badge) */}
                    <td className="px-5 sm:px-6 py-3.5 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center justify-center text-[11px] font-bold px-2.5 py-1 rounded-md shadow-2xs ${getStatusBadge(
                          ev.status
                        )}`}
                      >
                        {ev.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

