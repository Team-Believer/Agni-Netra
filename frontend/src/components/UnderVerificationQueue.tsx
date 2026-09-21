'use client';

import React, { useState } from 'react';
import { EventItem, EventDetail } from '../lib/types';
import { resolveVerificationContact, VerificationContactResult } from '../lib/verificationContact';
import { verifyEvent } from '../lib/api';
import { 
  ShieldAlert, 
  ArrowRight, 
  Eye, 
  Clock, 
  MapPin, 
  Phone, 
  PhoneCall, 
  Building2, 
  Trees, 
  Info, 
  CheckCircle2, 
  AlertCircle,
  FileCheck,
  Send,
  X
} from 'lucide-react';

interface UnderVerificationQueueProps {
  events: EventItem[];
  selectedEvent?: EventItem | EventDetail | null;
  onSelectEvent: (eventId: string) => void;
  onEventUpdated?: () => void;
}

export const UnderVerificationQueue: React.FC<UnderVerificationQueueProps> = ({ 
  events, 
  selectedEvent,
  onSelectEvent,
  onEventUpdated 
}) => {
  const [callInitiated, setCallInitiated] = useState<string | null>(null);
  const [verifyModalOpen, setVerifyModalOpen] = useState(false);
  const [verifyDecision, setVerifyDecision] = useState<'confirmed' | 'rejected' | 'needs_more_evidence'>('confirmed');
  const [verifyComment, setVerifyComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [actionSuccessMsg, setActionSuccessMsg] = useState<string | null>(null);

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

  // Source of truth for display: currently selected event on dashboard, or top of queue
  const displayedEvent = selectedEvent || (verificationQueue.length > 0 ? verificationQueue[0] : null);

  if (!displayedEvent) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-6 text-center shadow-sm mb-4">
        <ShieldAlert className="w-8 h-8 text-slate-300 mx-auto mb-2" />
        <h3 className="text-sm font-bold text-slate-700">No Action Required</h3>
        <p className="text-xs text-slate-500 mt-1">No events currently require verification.</p>
      </div>
    );
  }

  const timeStr = displayedEvent.last_seen 
    ? new Date(displayedEvent.last_seen).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) 
    : '--:--';

  // Resolve official contact dynamically based on the CURRENT displayedEvent
  const contact = resolveVerificationContact(displayedEvent);

  const isCritical = displayedEvent.priority === 'Critical' || displayedEvent.priority === 'High';

  const getContactIcon = (type?: string) => {
    switch (type) {
      case 'Facility':
        return <Building2 className="w-4 h-4 text-indigo-600" />;
      case 'Forest Authority':
        return <Trees className="w-4 h-4 text-emerald-600" />;
      default:
        return <Phone className="w-4 h-4 text-blue-600" />;
    }
  };

  const handlePhoneClick = () => {
    if (contact) {
      setCallInitiated(contact.formattedPhone);
      setTimeout(() => setCallInitiated(null), 7000);
    }
  };

  const handleOpenVerifyModal = (decision: 'confirmed' | 'needs_more_evidence') => {
    onSelectEvent(displayedEvent.event_id);
    setVerifyDecision(decision);
    setVerifyComment(decision === 'needs_more_evidence' ? 'Requesting additional sensor pass corroboration & ground check.' : '');
    setVerifyModalOpen(true);
  };

  const handleVerifySubmit = async () => {
    setIsSubmitting(true);
    try {
      const res = await verifyEvent(displayedEvent.event_id, {
        decision: verifyDecision,
        comment: verifyComment || `Analyst verification recorded for ${displayedEvent.event_id}`,
        reviewer: 'Ananya Sharma'
      });
      if (res.success) {
        setVerifyModalOpen(false);
        setVerifyComment('');
        setActionSuccessMsg(`Verification recorded successfully for ${displayedEvent.event_id}: ${verifyDecision.toUpperCase()}`);
        setTimeout(() => setActionSuccessMsg(null), 5000);
        if (onEventUpdated) onEventUpdated();
      } else {
        alert(res.error || 'Verification submission failed');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white border border-indigo-100 rounded-xl overflow-hidden shadow-sm mb-4">
      {/* Card Header */}
      <div className="px-5 py-3.5 bg-gradient-to-r from-indigo-700 via-indigo-600 to-indigo-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-1 rounded-md bg-white/10 text-white">
            <ShieldAlert className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide">
              Action Required: Next Event to Verify
            </h3>
            <p className="text-[11px] text-indigo-100/90 font-normal">
              Analyst verification queue & evidence gathering
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-white/20 text-white border border-white/20 shadow-inner">
            {verificationQueue.length} in Queue
          </span>
        </div>
      </div>
      
      {/* Card Body with 20-24px padding */}
      <div className="p-5 sm:p-6 space-y-4">
        {/* Success Alert if Verification Submitted */}
        {actionSuccessMsg && (
          <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded-lg text-xs font-semibold text-emerald-800 flex items-center gap-2 animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>{actionSuccessMsg}</span>
          </div>
        )}

        {/* Top: Event Metadata Block */}
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="flex items-start gap-3 flex-1">
            <div className="flex items-center justify-center flex-shrink-0 text-indigo-600 mt-1">
              <Eye className="w-5 h-5 sm:w-6 sm:h-6" />
            </div>
            <div className="space-y-1 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={() => onSelectEvent(displayedEvent.event_id)}
                  className="text-sm font-black text-slate-900 tracking-tight hover:text-indigo-600 hover:underline text-left cursor-pointer"
                  title="Click to focus event on Live Map and view details"
                >
                  {displayedEvent.event_id}
                </button>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded text-amber-800 bg-amber-50 border border-amber-200">
                  {displayedEvent.status}
                </span>
                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${
                  displayedEvent.priority === 'Critical' 
                    ? 'text-red-700 bg-red-50 border-red-200'
                    : displayedEvent.priority === 'High'
                    ? 'text-orange-700 bg-orange-50 border-orange-200'
                    : 'text-blue-700 bg-blue-50 border-blue-200'
                }`}>
                  {displayedEvent.priority} Priority
                </span>
                <span className="text-[11px] font-medium text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
                  {displayedEvent.classification || displayedEvent.title}
                </span>
              </div>

              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-600 pt-0.5">
                <span className="flex items-center gap-1.5 font-medium">
                  <Clock className="w-3.5 h-3.5 text-slate-400" /> 
                  Last observation: <span className="text-slate-800 font-semibold">{timeStr}</span>
                </span>
                <span className="text-slate-300">•</span>
                <span className="flex items-center gap-1.5 font-medium truncate max-w-[280px]">
                  <MapPin className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                  <span className="text-slate-800 truncate">{displayedEvent.location}</span>
                </span>
              </div>

              {displayedEvent.current_assessment && (
                <p className="text-xs text-slate-600 italic bg-slate-50/80 rounded-md p-2 border border-slate-100 mt-1 line-clamp-2">
                  &ldquo;{displayedEvent.current_assessment}&rdquo;
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Middle: Verification Contact Panel */}
        <div className={`rounded-xl border transition-all ${
          isCritical 
            ? 'bg-slate-50/80 border-slate-200/90 shadow-xs' 
            : 'bg-slate-50/50 border-slate-200'
        } p-3.5 sm:p-4`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                Verification Contact
              </span>
              <div className="group relative inline-flex items-center">
                <Info className="w-3.5 h-3.5 text-slate-400 cursor-help" />
                <div className="absolute left-0 bottom-full mb-1 hidden group-hover:block z-20 w-64 p-2 bg-slate-900 text-white text-[11px] rounded shadow-lg font-normal">
                  Use this verified public contact to corroborate whether the thermal detection is genuine before recording a decision. Calling does not auto-confirm the event.
                </div>
              </div>
            </div>
            {contact?.contactType && (
              <span className="text-[10px] font-semibold text-slate-600 bg-white border border-slate-200 px-2 py-0.5 rounded-md shadow-2xs">
                {contact.contactType}
              </span>
            )}
          </div>

          {contact ? (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  {getContactIcon(contact.contactType)}
                  <span className="text-xs font-bold text-slate-900">
                    {contact.name}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-x-2 text-[11px] text-slate-500">
                  <span>{contact.role}</span>
                  <span>•</span>
                  <span className="font-mono text-slate-700 font-bold flex items-center gap-1">
                    ☎ {contact.formattedPhone}
                  </span>
                  <span>•</span>
                  <span className="text-[10px] text-slate-400 italic">Source: {contact.source}</span>
                </div>
              </div>

              {/* Click-to-Call Action Button targeting Current Event */}
              <div className="flex items-center gap-2 flex-shrink-0">
                <a
                  href={`tel:${contact.phone}`}
                  onClick={handlePhoneClick}
                  className="inline-flex items-center gap-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold py-2 px-3.5 rounded-lg text-xs transition-colors shadow-sm cursor-pointer"
                  title="Evidence gathering: Call official authority/facility to verify detection."
                >
                  <PhoneCall className="w-3.5 h-3.5 text-emerald-400" />
                  <span>☎ {contact.actionLabel}</span>
                </a>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between py-1 text-xs text-slate-500">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-amber-500" />
                <span>No verified official facility or local authority contact is available for this event.</span>
              </div>
            </div>
          )}

          {callInitiated && (
            <div className="mt-2 text-[11px] text-emerald-700 bg-emerald-50 border border-emerald-200 rounded p-2 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span>
                Calling <strong>{callInitiated}</strong>. Corroborate on-ground condition with authority and record the decision below.
              </span>
            </div>
          )}
        </div>

        {/* Bottom Action Controls: Verification Decision vs Escalation */}
        <div className="pt-1 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-100">
          {/* Subtle Emergency Escalation Secondary Option */}
          <div className="flex items-center gap-1.5 text-xs text-slate-500 w-full sm:w-auto justify-start">
            <span className="text-[11px] text-slate-400">Emergency escalation:</span>
            <a 
              href="tel:112"
              className="text-[11px] font-semibold text-rose-600 hover:text-rose-800 hover:underline inline-flex items-center gap-1"
              title="Escalate directly to National Emergency Services if verified imminent threat exists."
            >
              <ShieldAlert className="w-3 h-3 text-rose-500" /> 112 Emergency
            </a>
          </div>

          {/* Primary & Secondary Decision Buttons */}
          <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
            <button 
              onClick={() => handleOpenVerifyModal('needs_more_evidence')}
              className="flex-1 sm:flex-none bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 font-bold py-2 px-3.5 rounded-lg text-xs transition-colors shadow-xs cursor-pointer"
            >
              Needs More Info
            </button>
            <button 
              onClick={() => handleOpenVerifyModal('confirmed')}
              className="flex-1 sm:flex-none bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm cursor-pointer"
            >
              <span>Verify Event</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Footer Queue Pagination / View All */}
      {verificationQueue.length > 1 && (
        <div className="px-5 py-2.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
          <span className="text-[11px] text-slate-500">
            {selectedEvent ? `Inspecting ${displayedEvent.event_id}` : 'Showing top verification candidate by priority & recency'}
          </span>
          <button 
            onClick={() => onSelectEvent(verificationQueue[0].event_id)} 
            className="text-[11px] font-bold text-indigo-600 hover:text-indigo-800 hover:underline inline-flex items-center gap-1 cursor-pointer"
          >
            View All ({verificationQueue.length})
          </button>
        </div>
      )}

      {/* Verification Decision Modal */}
      {verifyModalOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-5 shadow-xl border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                <FileCheck className="w-4 h-4 text-indigo-600" />
                Record Verification: {displayedEvent.event_id}
              </h3>
              <button onClick={() => setVerifyModalOpen(false)} className="text-slate-400 hover:text-slate-600 text-sm p-1 rounded">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="py-4 space-y-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Verification Decision
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => setVerifyDecision('confirmed')}
                    className={`py-2 px-2 rounded-lg text-xs font-semibold border transition-all ${
                      verifyDecision === 'confirmed'
                        ? 'bg-emerald-50 border-emerald-500 text-emerald-700 shadow-xs'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    Confirm Event
                  </button>
                  <button
                    onClick={() => setVerifyDecision('rejected')}
                    className={`py-2 px-2 rounded-lg text-xs font-semibold border transition-all ${
                      verifyDecision === 'rejected'
                        ? 'bg-red-50 border-red-500 text-red-700 shadow-xs'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    Reject / False
                  </button>
                  <button
                    onClick={() => setVerifyDecision('needs_more_evidence')}
                    className={`py-2 px-2 rounded-lg text-xs font-semibold border transition-all ${
                      verifyDecision === 'needs_more_evidence'
                        ? 'bg-amber-50 border-amber-500 text-amber-700 shadow-xs'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    Need More Data
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Analyst Rationale / Verification Evidence
                </label>
                <textarea
                  value={verifyComment}
                  onChange={(e) => setVerifyComment(e.target.value)}
                  rows={3}
                  placeholder="Record outcome of phone contact / satellite corroboration (e.g. Verified with facility control room)..."
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100">
              <button
                onClick={() => setVerifyModalOpen(false)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
              >
                Cancel
              </button>
              <button
                disabled={isSubmitting}
                onClick={handleVerifySubmit}
                className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors flex items-center gap-1.5 shadow-sm"
              >
                <Send className="w-3.5 h-3.5" />
                Submit Verification
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};


