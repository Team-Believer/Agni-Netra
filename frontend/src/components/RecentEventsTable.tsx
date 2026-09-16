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
        return 'bg-red-50 text-red-600 border border-red-100';
      case 'Medium':
        return 'bg-amber-50 text-amber-700 border border-amber-100';
      case 'Low':
      default:
        return 'bg-emerald-50 text-emerald-700 border border-emerald-100';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Needs Verification':
      case 'Under Verification':
        return 'bg-amber-50 text-amber-700 border border-amber-200/80';
      case 'Monitoring':
        return 'bg-blue-50 text-blue-700 border border-blue-100';
      case 'Active':
        return 'bg-red-50 text-red-600 border border-red-100';
      case 'Confirmed':
        return 'bg-emerald-50 text-emerald-700 border border-emerald-100';
      default:
        return 'bg-slate-100 text-slate-600 border border-slate-200';
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs mt-4">
      {/* Header */}
      <div className="px-4 py-2.5 border-b border-slate-100 flex items-center justify-between">
        <h3 className="text-xs font-bold text-slate-900">Recent Events</h3>
        <button className="text-[11px] font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1 transition-colors">
          View All <ArrowRight className="w-3 h-3" />
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50/50 text-[11px] font-semibold text-slate-500">
              <th className="py-2.5 px-4">Event ID</th>
              <th className="py-2.5 px-4">Date & Time (IST)</th>
              <th className="py-2.5 px-4">Location</th>
              <th className="py-2.5 px-4">Classification</th>
              <th className="py-2.5 px-4">Priority</th>
              <th className="py-2.5 px-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
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
                <tr
                  key={ev.event_id}
                  onClick={() => onSelectEvent(ev.event_id)}
                  className={`cursor-pointer transition-colors ${
                    isSelected ? 'bg-blue-50/60 font-medium' : 'hover:bg-slate-50/80'
                  }`}
                >
                  <td className="py-2.5 px-4 font-semibold text-blue-600 underline-offset-2 hover:underline">
                    {ev.event_id}
                  </td>
                  <td className="py-2.5 px-4 text-slate-600 text-[11px]">
                    {dateStr}, {timeStr}
                  </td>
                  <td className="py-2.5 px-4 text-slate-800 font-medium">
                    {ev.location}
                  </td>
                  <td className="py-2.5 px-4 text-slate-700">
                    {ev.classification}
                  </td>
                  <td className="py-2.5 px-4">
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${getPriorityBadge(ev.priority)}`}>
                      {ev.priority}
                    </span>
                  </td>
                  <td className="py-2.5 px-4">
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${getStatusBadge(ev.status)}`}>
                      {ev.status}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
