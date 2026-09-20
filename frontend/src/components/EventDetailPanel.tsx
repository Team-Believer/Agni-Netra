'use client';

import React, { useState } from 'react';
import {
  Factory,
  MapPin,
  MoreVertical,
  Compass,
  Clock,
  Flame,
  Layers,
  Building,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  XCircle,
  Send,
  Radio,
  FileCheck
} from 'lucide-react';
import { EventDetail, TimelinePoint } from '../lib/types';
import { verifyEvent } from '../lib/api';

interface EventDetailPanelProps {
  event: EventDetail | null;
  timeline: TimelinePoint[];
  onEventUpdated: () => void;
}

export const EventDetailPanel: React.FC<EventDetailPanelProps> = ({
  event,
  timeline,
  onEventUpdated,
}) => {
  const [activeTab, setActiveTab] = useState<'Overview' | 'Evidence' | 'Timeline' | 'Media' | 'Actions'>('Overview');
  const [verifyModalOpen, setVerifyModalOpen] = useState(false);
  const [verifyDecision, setVerifyDecision] = useState<'confirmed' | 'rejected' | 'needs_more_evidence'>('confirmed');
  const [verifyComment, setVerifyComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [imageModalOpen, setImageModalOpen] = useState(false);

  if (!event) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-8 flex flex-col items-center justify-center text-center h-[720px] text-slate-400">
        <Flame className="w-8 h-8 text-slate-300 mb-2" />
        <p className="text-xs font-medium">Select an event from the map or table to inspect details.</p>
      </div>
    );
  }

  const handleVerifySubmit = async (decision: string, comment?: string) => {
    setIsSubmitting(true);
    try {
      const res = await verifyEvent(event.event_id, {
        decision,
        comment: comment || verifyComment,
        reviewer: 'Ananya Sharma'
      });
      if (res.success) {
        setVerifyModalOpen(false);
        setVerifyComment('');
        onEventUpdated();
      } else {
        alert(res.error || 'Verification failed');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white border border-slate-200/90 rounded-xl shadow-sm overflow-hidden flex flex-col h-[740px]">
      {/* 1. Header Bar with Persistent ID & Badges */}
      <div className="px-5 py-3 border-b border-slate-100 flex items-center justify-between bg-white/80">
        <div className="flex items-center gap-2">
          <span className="text-sm font-extrabold text-slate-900">{event.event_id}</span>
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-red-50 text-red-700 border border-red-200/80 flex items-center gap-1.5 shadow-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-red-600 animate-pulse"></span>
            High Priority
          </span>
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200/80 flex items-center gap-1.5 shadow-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
            {event.status}
          </span>
        </div>
        <button className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition-colors">
          <MoreVertical className="w-4 h-4" />
        </button>
      </div>

      {/* 2. Title & Facility Info */}
      <div className="px-5 py-3 border-b border-slate-100 bg-slate-50/40">
        <div className="flex items-center gap-2 text-orange-600">
          <Factory className="w-4 h-4 shrink-0" />
          <h2 className="text-xs font-extrabold text-slate-900 leading-tight">{event.title}</h2>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1 font-medium">
          <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span>{event.location}</span>
        </div>
      </div>

      {/* 3. Sub-navigation Tabs */}
      <div className="px-5 border-b border-slate-200/80 bg-slate-50/70 flex items-center gap-6 text-xs font-semibold">
        {(['Overview', 'Evidence', 'Timeline', 'Media', 'Actions'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`py-2.5 relative transition-all duration-150 ${
              activeTab === tab
                ? 'text-indigo-600 font-extrabold border-b-2 border-indigo-600'
                : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* 4. Tab Body Content (Scrollable) */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
        {activeTab === 'Overview' && (
          <>
            {/* Satellite Context Preview Canvas */}
            <div className="w-full h-40 rounded-lg overflow-hidden relative border border-slate-200 bg-slate-900 group cursor-pointer" onClick={() => setImageModalOpen(true)}>
              <img
                src={event.satellite_image_url || "https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?auto=format&fit=crop&w=600&q=80"}
                alt="Satellite Optical & Thermal"
                className="w-full h-full object-cover opacity-80 group-hover:opacity-95 transition-opacity"
              />
              <div className="absolute inset-0 bg-radial from-transparent to-black/60 pointer-events-none" />
              <div className="absolute top-2 left-2 bg-black/60 backdrop-blur-xs text-white text-[10px] px-2 py-0.5 rounded font-mono">
                VIIRS / SENTINEL-2 SWIR
              </div>
              <div className="absolute bottom-2 right-2 bg-black/60 backdrop-blur-xs text-white text-[10px] px-2 py-0.5 rounded font-mono">
                Jamnagar Petrochemical Quadrant
              </div>
              {/* Thermal Hotspot Pulsing Indicator */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
                <span className="w-8 h-8 rounded-full bg-red-500/40 animate-ping absolute"></span>
                <span className="w-4 h-4 rounded-full bg-red-500 ring-2 ring-white shadow-lg"></span>
              </div>
            </div>

            {/* Meta Attributes Grid */}
            <div className="grid grid-cols-2 gap-y-2 gap-x-4 border-b border-slate-100 pb-3 text-[11px]">
              <div className="flex items-center gap-2 text-slate-500">
                <Compass className="w-3.5 h-3.5 text-slate-400" />
                <span>Latitude / Longitude</span>
              </div>
              <div className="font-semibold text-slate-800 text-right">
                {event.latitude != null ? event.latitude.toFixed(2) : '--'}° N, {event.longitude != null ? event.longitude.toFixed(2) : '--'}° E
              </div>

              <div className="flex items-center gap-2 text-slate-500">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span>First Seen</span>
              </div>
              <div className="font-semibold text-slate-800 text-right">
                {event.first_seen ? new Date(event.first_seen).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : 'Unknown'}, {event.first_seen ? new Date(event.first_seen).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) : '--:--'}
              </div>

              <div className="flex items-center gap-2 text-slate-500">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                <span>Last Seen</span>
              </div>
              <div className="font-semibold text-slate-800 text-right">
                {event.last_seen ? new Date(event.last_seen).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : 'Unknown'}, {event.last_seen ? new Date(event.last_seen).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) : '--:--'}
              </div>

              <div className="flex items-center gap-2 text-slate-500">
                <Radio className="w-3.5 h-3.5 text-slate-400" />
                <span>Observations</span>
              </div>
              <div className="font-semibold text-slate-800 text-right">
                {event.observations_count} (last 6 hours)
              </div>

              <div className="flex items-center gap-2 text-slate-500">
                <Building className="w-3.5 h-3.5 text-slate-400" />
                <span>Nearby Facility</span>
              </div>
              <div className="font-semibold text-slate-800 text-right truncate">
                {event.nearby_facility}
              </div>

              <div className="flex items-center gap-2 text-slate-500">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                <span>District</span>
              </div>
              <div className="font-semibold text-slate-800 text-right truncate">
                {event.district}
              </div>
            </div>

            {/* 4 Score Cards (Matches Reference UI) */}
            <div className="grid grid-cols-4 gap-2">
              <div className="bg-slate-50/80 border border-slate-200/90 rounded-lg p-2.5 text-center">
                <div className="text-[10px] text-slate-500 font-medium leading-tight">Classification Confidence</div>
                <div className="text-base font-bold text-emerald-600 mt-1">
                  {event.confidence != null ? (event.confidence * 100).toFixed(0) : '--'}%
                </div>
              </div>

              <div className="bg-slate-50/80 border border-slate-200/90 rounded-lg p-2.5 text-center">
                <div className="text-[10px] text-slate-500 font-medium leading-tight">Evidence Completeness</div>
                <div className="text-base font-bold text-amber-600 mt-1">
                  {event.evidence_completeness != null ? (event.evidence_completeness * 100).toFixed(0) : '--'}%
                </div>
              </div>

              <div className="bg-red-50/50 border border-red-200/80 rounded-lg p-2.5 text-center">
                <div className="text-[10px] text-red-600 font-medium leading-tight">Risk Index</div>
                <div className="text-base font-bold text-red-600 mt-1">
                  {event.risk_index != null ? event.risk_index.toFixed(0) : '--'} <span className="text-[10px] font-normal text-slate-400">/ 100</span>
                </div>
              </div>

              <div className="bg-red-50/50 border border-red-200/80 rounded-lg p-2.5 text-center">
                <div className="text-[10px] text-red-600 font-medium leading-tight">Priority</div>
                <div className="text-base font-bold text-red-600 mt-1">
                  {event.risk_level === 'Critical' ? 'Critical' : event.priority}
                </div>
              </div>
            </div>

            {/* Current Assessment Alert Banner */}
            <div className="bg-red-50/70 border border-red-200/80 rounded-lg p-3 flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-[11px] font-bold text-red-700">Current Assessment</div>
                <div className="text-[11px] text-red-700 leading-snug mt-0.5">
                  {event.current_assessment}
                </div>
              </div>
            </div>

            {/* "What Happened?" Section with 4 Cards */}
            <div>
              <h4 className="text-xs font-bold text-slate-900 mb-2">What Happened?</h4>
              <div className="grid grid-cols-4 gap-2">
                <div className="bg-white border border-slate-200 rounded-lg p-2 shadow-sm">
                  <div className="text-[10px] text-slate-400 font-medium">FRP</div>
                  <div className="text-xs font-bold text-red-600 flex items-center gap-0.5 mt-0.5">
                    ↑ {event.frp_change_pct !== undefined && event.frp_change_pct !== null ? event.frp_change_pct.toFixed(0) : '0'}%
                  </div>
                  <div className="text-[9px] text-slate-400">vs. historical avg.</div>
                </div>

                <div className="bg-white border border-slate-200 rounded-lg p-2 shadow-sm">
                  <div className="text-[10px] text-slate-400 font-medium">Footprint</div>
                  <div className="text-xs font-bold text-red-600 flex items-center gap-0.5 mt-0.5">
                    ↑ {event.footprint_expansion_factor !== undefined && event.footprint_expansion_factor !== null ? event.footprint_expansion_factor.toFixed(1) : '1.0'}×
                  </div>
                  <div className="text-[9px] text-slate-400">expanding</div>
                </div>

                <div className="bg-white border border-slate-200 rounded-lg p-2 shadow-sm">
                  <div className="text-[10px] text-slate-400 font-medium">Observations</div>
                  <div className="text-xs font-bold text-red-600 flex items-center gap-0.5 mt-0.5">
                    ↑ {event.observations_count}
                  </div>
                  <div className="text-[9px] text-slate-400">in last 6 hours</div>
                </div>

                <div className="bg-white border border-slate-200 rounded-lg p-2 shadow-sm">
                  <div className="text-[10px] text-slate-400 font-medium">Behavior</div>
                  <div className="text-xs font-bold text-red-600 mt-0.5 truncate">
                    Escalating
                  </div>
                  <div className="text-[9px] text-slate-400">rapid increase</div>
                </div>
              </div>
            </div>

            {/* Explainability Breakdown (WHY, WHY NOT, WHAT CHANGED) */}
            <div className="space-y-2 border-t border-slate-100 pt-3">
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5">
                <div className="text-[10px] font-bold text-slate-800 uppercase tracking-wide">
                  WHY {(event.classification || 'UNKNOWN').toUpperCase()}?
                </div>
                <ul className="list-disc list-inside text-[11px] text-slate-600 space-y-1 mt-1">
                  {event.explanations?.why?.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5">
                <div className="text-[10px] font-bold text-slate-800 uppercase tracking-wide">
                  WHY NOT ROUTINE FLARE?
                </div>
                <ul className="list-disc list-inside text-[11px] text-slate-600 space-y-1 mt-1">
                  {event.explanations?.why_not?.map((wn, i) => (
                    <li key={i}>{wn}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Action Buttons (Matches Reference UI) */}
            <div className="grid grid-cols-3 gap-2 pt-2">
              <button
                onClick={() => setVerifyModalOpen(true)}
                className="bg-slate-900 hover:bg-slate-800 text-white font-semibold py-2 px-3 rounded-lg text-xs flex items-center justify-center gap-1.5 shadow-xs transition-colors"
              >
                <CheckCircle className="w-3.5 h-3.5" />
                Verify Event
              </button>

              <button
                onClick={() => handleVerifySubmit('needs_more_evidence', 'Requested tasking from next orbital pass')}
                className="bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 font-semibold py-2 px-2 rounded-lg text-[11px] flex items-center justify-center gap-1 shadow-2xs transition-colors"
              >
                <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
                Request More Data
              </button>

              <button
                onClick={() => handleVerifySubmit('false_alarm', 'Marked as false alarm / operational sensor glint')}
                className="bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 font-semibold py-2 px-2 rounded-lg text-[11px] flex items-center justify-center gap-1 shadow-2xs transition-colors"
              >
                <XCircle className="w-3.5 h-3.5 text-slate-400" />
                Mark as False Alarm
              </button>
            </div>
          </>
        )}

        {activeTab === 'Evidence' && (
          <div className="space-y-4">
            {/* Multi-sensor Visual Summary */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
              <h4 className="text-xs font-bold text-slate-800 mb-3">Multi-Sensor Contribution Summary</h4>
              <div className="space-y-3">
                {['SUPPORTING', 'CONFLICTING', 'NEUTRAL'].map(direction => {
                  const sources = event.evidence?.filter(e => e.direction === direction) || [];
                  const count = sources.length;
                  const total = event.evidence?.length || 1;
                  const pct = Math.round((count / total) * 100);
                  
                  if (count === 0 && direction !== 'SUPPORTING') return null;
                  
                  let barColor = 'bg-slate-300';
                  let textColor = 'text-slate-700';
                  if (direction === 'SUPPORTING') { barColor = 'bg-emerald-500'; textColor = 'text-emerald-700'; }
                  if (direction === 'CONFLICTING') { barColor = 'bg-red-500'; textColor = 'text-red-700'; }

                  return (
                    <div key={direction} className="space-y-1">
                      <div className="flex justify-between text-[10px] font-semibold">
                        <span className={textColor}>{direction} SOURCES ({count})</span>
                        <span>{pct}%</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div className={`h-full ${barColor} rounded-full`} style={{ width: `${pct}%` }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="space-y-2.5">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <span className="font-semibold text-slate-700">Detailed Evidence Ledger</span>
                <span className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-medium">
                  {event.evidence?.length || 0} Sources
                </span>
              </div>
              {event.evidence?.map((item) => (
                <div key={item.id} className="bg-slate-50 border border-slate-200/90 rounded-lg p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{item.source} ({item.evidence_type})</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      item.direction === 'SUPPORTING'
                        ? 'bg-emerald-100 text-emerald-800'
                        : item.direction === 'CONFLICTING'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-slate-200 text-slate-700'
                    }`}>
                      {item.direction}
                    </span>
                  </div>
                  <div className="text-[11px] font-semibold text-slate-700">{item.value}</div>
                  <div className="text-[11px] text-slate-600">{item.explanation}</div>
                  
                  {/* Quality & Relevance Mini-bars */}
                  <div className="grid grid-cols-2 gap-3 pt-1">
                    <div>
                      <div className="flex justify-between text-[9px] text-slate-500 mb-0.5">
                        <span>Quality</span>
                        <span>{item.quality != null ? (item.quality * 100).toFixed(0) : '--'}%</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-1">
                        <div className="bg-blue-500 h-1 rounded-full" style={{ width: `${item.quality != null ? item.quality * 100 : 0}%` }}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-[9px] text-slate-500 mb-0.5">
                        <span>Relevance</span>
                        <span>{item.relevance != null ? (item.relevance * 100).toFixed(0) : '--'}%</span>
                      </div>
                      <div className="w-full bg-slate-200 rounded-full h-1">
                        <div className="bg-indigo-500 h-1 rounded-full" style={{ width: `${item.relevance != null ? item.relevance * 100 : 0}%` }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'Timeline' && (
          <div className="space-y-3">
            <span className="font-semibold text-slate-700">Observation History</span>
            <div className="space-y-2 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-slate-200">
              {timeline.map((point, idx) => (
                <div key={idx} className="relative flex items-start gap-3 pl-8">
                  <div className="absolute left-2 top-1.5 w-3 h-3 rounded-full bg-red-500 border-2 border-white shadow-xs"></div>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-2.5 flex-1">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-bold text-slate-800">{point.satellite}</span>
                      <span className="text-slate-400">
                        {point.timestamp ? new Date(point.timestamp).toLocaleTimeString() : ''}
                      </span>
                    </div>
                    <div className="mt-1 flex items-center gap-3 text-[11px] text-slate-600">
                      <span>FRP: <strong>{point.frp} MW</strong></span>
                      <span>Brightness: <strong>{point.brightness_temperature} K</strong></span>
                      <span>Quality: <strong>{point.quality}</strong></span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'Media' && (
          <div className="space-y-3 text-center py-6">
            <div className="w-full h-48 border border-slate-200 rounded-lg overflow-hidden relative cursor-pointer" onClick={() => setImageModalOpen(true)}>
              <img
                src={event.satellite_image_url || "https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?auto=format&fit=crop&w=600&q=80"}
                alt="High Resolution Corroboration"
                className="w-full h-full object-cover"
              />
            </div>
            <p className="text-[11px] text-slate-500">
              ESA Sentinel-2 B12 (SWIR-2 2.2μm) orthorectified image layer captured over Jamnagar Refinery quadrant.
            </p>
          </div>
        )}

        {activeTab === 'Actions' && (
          <div className="space-y-4">
            <h4 className="font-bold text-slate-800">Verification Audit Trail</h4>
            {event.verifications?.length > 0 ? (
              <div className="space-y-2">
                {event.verifications.map((v, i) => (
                  <div key={i} className="bg-slate-50 border border-slate-200 rounded-lg p-2.5">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-slate-900">{v.reviewer}</span>
                      <span className="text-slate-400">{v.timestamp ? new Date(v.timestamp).toLocaleString() : ''}</span>
                    </div>
                    <div className="text-[11px] font-medium text-blue-600 mt-0.5">{v.new_status} ({v.decision})</div>
                    {v.comment && <div className="text-[11px] text-slate-600 mt-1 italic">"{v.comment}"</div>}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-400 text-xs italic">No manual verifications logged yet.</p>
            )}

            <button
              onClick={() => setVerifyModalOpen(true)}
              className="w-full bg-slate-900 text-white font-semibold py-2 px-4 rounded-lg text-xs hover:bg-slate-800 transition-colors"
            >
              Add Verification Decision
            </button>
          </div>
        )}
      </div>

      {/* Human Verification Modal */}
      {verifyModalOpen && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-5 shadow-xl border border-slate-200 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                <FileCheck className="w-4 h-4 text-blue-600" />
                Verify Event: {event.event_id}
              </h3>
              <button onClick={() => setVerifyModalOpen(false)} className="text-slate-400 hover:text-slate-600 text-sm">
                ✕
              </button>
            </div>

            <div className="py-4 space-y-3">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                  Analyst Decision
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
                    Confirm Fire
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
                  Reviewer Notes / Evidence Rationale
                </label>
                <textarea
                  value={verifyComment}
                  onChange={(e) => setVerifyComment(e.target.value)}
                  rows={3}
                  placeholder="State basis for decision (e.g. plume corroborated by Sentinel-2 SWIR band)..."
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500"
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
                onClick={() => handleVerifySubmit(verifyDecision)}
                className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-50 transition-colors flex items-center gap-1.5"
              >
                <Send className="w-3 h-3" />
                Submit Verification
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Full Screen Image Modal */}
      {imageModalOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-[60] p-4" onClick={() => setImageModalOpen(false)}>
          <div className="relative max-w-5xl w-full">
            <button className="absolute -top-10 right-0 text-white hover:text-slate-300 text-3xl" onClick={() => setImageModalOpen(false)}>×</button>
            <img
              src={event.satellite_image_url || "https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?auto=format&fit=crop&w=600&q=80"}
              alt="Full Resolution Satellite"
              className="w-full h-auto max-h-[85vh] object-contain rounded-lg shadow-2xl border border-white/20"
              onClick={(e) => e.stopPropagation()}
            />

          </div>
        </div>
      )}
    </div>
  );
};
