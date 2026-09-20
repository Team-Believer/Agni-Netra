'use client';

import React from 'react';
import { EventItem } from '../lib/types';
import { ShieldAlert, ArrowRight, Eye, Clock } from 'lucide-react';

interface UnderVerificationQueueProps {
  events: EventItem[];
  onSelectEvent: (eventId: string) => void;
}

export const UnderVerificationQueue: React.FC<UnderVerificationQueueProps> = ({ events, onSelectEvent }) => {
  const priorityOrder: Record<string, number> = {
    'Critical': 4,
    'High': 3,
    'Medium': 2,
    'Low': 1,
    'Monitor': 0
  };

  const verificationQueue = [...events].filter(
    (ev) => ev.status === 'Needs Verification' || ev.status === 'Under Verification'
  ).sort((a, b) => {
    const pA = priorityOrder[a.priority || 'Monitor'] || 0;
    const pB = priorityOrder[b.priority || 'Monitor'] || 0;
    if (pA !== pB) return pB - pA; // Descending priority
    const tA = a.last_seen ? new Date(a.last_seen).getTime() : 0;
    const tB = b.last_seen ? new Date(b.last_seen).getTime() : 0;
    return tB - tA; // Descending time
  });

  // Requirement: "must display ONLY ONE event at a time"
  const nextEvent = verificationQueue.length > 0 ? verificationQueue[0] : null;

  if (!nextEvent) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-6 text-center shadow-sm mb-4">
        <ShieldAlert className="w-8 h-8 text-slate-300 mx-auto mb-2" />
        <h3 className="text-sm font-bold text-slate-700">No Action Required</h3>
        <p className="text-xs text-slate-500 mt-1">No events currently require verification.</p>
      </div>
    );
  }

  const timeStr = nextEvent.last_seen 
    ? new Date(nextEvent.last_seen).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) 
    : '--:--';

  return (
    <div className="bg-indigo-50 border border-indigo-200/80 rounded-xl overflow-hidden shadow-sm mb-4">
      <div className="px-4 py-3 bg-indigo-600 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-white" />
          <h3 className="text-sm font-bold text-white">Action Required: Next Event to Verify</h3>
        </div>
        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-white/20 text-white">
          {verificationQueue.length} in Queue
        </span>
      </div>
      
      <div className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-4 flex-1">
          <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
            <Eye className="w-6 h-6 text-indigo-600" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-extrabold text-indigo-900">{nextEvent.event_id}</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded text-amber-700 bg-amber-100 border border-amber-200">
                {nextEvent.status}
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded text-red-700 bg-red-100 border border-red-200">
                {nextEvent.priority}
              </span>
            </div>
            <p className="text-xs text-indigo-800 font-semibold mb-0.5">
              {nextEvent.classification || nextEvent.title}
            </p>
            <div className="flex items-center gap-3 text-[11px] text-indigo-600/80">
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" /> Last observation: {timeStr}
              </span>
              <span>•</span>
              <span className="truncate max-w-[200px]">{nextEvent.location}</span>
            </div>
            {nextEvent.current_assessment && (
              <p className="text-xs text-indigo-700 mt-1.5 line-clamp-1 italic">
                "{nextEvent.current_assessment}"
              </p>
            )}
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-2">
          <a 
            href="tel:112"
            className="flex-shrink-0 bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-3 rounded-lg text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm"
          >
            <ShieldAlert className="w-3.5 h-3.5" /> 112 Emergency
          </a>
          <button 
            onClick={() => onSelectEvent(nextEvent.event_id)}
            className="flex-shrink-0 bg-white hover:bg-indigo-50 border border-indigo-200 text-indigo-700 font-bold py-2 px-3 rounded-lg text-xs transition-colors shadow-sm"
          >
            Needs More Info
          </button>
          <button 
            onClick={() => onSelectEvent(nextEvent.event_id)}
            className="flex-shrink-0 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-3 rounded-lg text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm"
          >
            Verify Event <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
      {verificationQueue.length > 1 && (
        <div className="px-4 py-2 bg-indigo-50/50 border-t border-indigo-100 flex justify-end">
          <button onClick={() => {}} className="text-[11px] font-semibold text-indigo-600 hover:text-indigo-800">
            View All ({verificationQueue.length})
          </button>
        </div>
      )}
    </div>
  );
};
