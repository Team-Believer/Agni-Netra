'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Header } from '../../../components/Header';
import { Sidebar } from '../../../components/Sidebar';
import { 
  ArrowLeft, 
  Flame, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  TrendingUp, 
  ShieldAlert, 
  Radio, 
  Clock, 
  Eye, 
  Calendar, 
  Building2, 
  Layers, 
  Wind, 
  History, 
  Sparkles, 
  CheckCircle, 
  X, 
  RotateCcw, 
  ExternalLink,
  ChevronRight,
  Activity,
  AlertOctagon,
  MapPin
} from 'lucide-react';
import Link from 'next/link';
import { fetchEventDetail, fetchEventTimeline, verifyEvent } from '../../../lib/api';
import type { EventDetail, EvidenceItem, TimelinePoint } from '../../../lib/types';
import { formatDistanceToNow, format, parseISO, isValid } from 'date-fns';

export default function EventDetailPage({ params }: { params: { id: string } }) {
  const [currentTab, setCurrentTab] = useState('events');
  const [searchQuery, setSearchQuery] = useState('');
  const [event, setEvent] = useState<EventDetail | null>(null);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals
  const [timelineModalOpen, setTimelineModalOpen] = useState(false);
  const [verifyModalOpen, setVerifyModalOpen] = useState(false);
  const [verifyDecision, setVerifyDecision] = useState<'confirmed' | 'rejected' | 'needs_more_evidence'>('confirmed');
  const [verifyComment, setVerifyComment] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [verifySuccessMsg, setVerifySuccessMsg] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [eventData, timelineData] = await Promise.all([
        fetchEventDetail(params.id),
        fetchEventTimeline(params.id)
      ]);
      if (!eventData) {
        setError(`Event '${params.id}' was not found in the active directory.`);
      } else {
        setEvent(eventData);
        setTimeline(timelineData || []);
      }
    } catch (err: any) {
      console.error('Failed to load event:', err);
      setError(err?.message || 'Failed to load event details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [params.id]);

  const handleVerifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!event) return;
    setIsVerifying(true);
    try {
      const res = await verifyEvent(event.event_id, {
        decision: verifyDecision,
        comment: verifyComment || `Analyst verification: marked as ${verifyDecision}`,
        reviewer: 'Ananya Sharma'
      });
      if (res.success) {
        setVerifySuccessMsg(`Event successfully updated to status '${res.new_status || verifyDecision}'.`);
        setVerifyComment('');
        setTimeout(() => {
          setVerifyModalOpen(false);
          setVerifySuccessMsg(null);
          loadData();
        }, 1200);
      } else {
        alert(res.error || 'Verification failed');
      }
    } catch (e: any) {
      alert(e?.message || 'Verification failed');
    } finally {
      setIsVerifying(false);
    }
  };

  // Evidence Grouping
  const evidenceGroups = useMemo(() => {
    if (!event || !event.evidence) return { primary: [], corroborating: [], contextual: [] };

    const primary: EvidenceItem[] = [];
    const corroborating: EvidenceItem[] = [];
    const contextual: EvidenceItem[] = [];

    event.evidence.forEach(item => {
      const type = (item.evidence_type || '').toLowerCase();
      if (type === 'thermal') {
        primary.push(item);
      } else if (['temporal', 'optical', 'sar', 'weather', 'atmospheric'].includes(type)) {
        corroborating.push(item);
      } else {
        contextual.push(item);
      }
    });

    return { primary, corroborating, contextual };
  }, [event]);

  // Evidence Health Metrics
  const evidenceHealth = useMemo(() => {
    if (!event || !event.evidence || event.evidence.length === 0) {
      return { total: 0, supporting: 0, conflicting: 0, missing: 0, avgQuality: 0, status: 'No Data' };
    }
    const total = event.evidence.length;
    let supporting = 0;
    let conflicting = 0;
    let missing = 0;
    let qualitySum = 0;
    let qualityCount = 0;

    event.evidence.forEach(e => {
      if (e.direction === 'SUPPORTING') supporting++;
      else if (e.direction === 'CONFLICTING') conflicting++;
      else if (e.direction === 'MISSING' || e.availability === false) missing++;
      
      if (e.quality != null) {
        qualitySum += e.quality;
        qualityCount++;
      }
    });

    const avgQuality = qualityCount > 0 ? Math.round((qualitySum / qualityCount) * 100) : 0;
    let status = 'Consistent';
    if (conflicting > 0) status = 'Contradictory Signals';
    else if (missing > supporting) status = 'Sparse Evidence';

    return { total, supporting, conflicting, missing, avgQuality, status };
  }, [event]);

  // Helpers
  const getPriorityBadge = (prio?: string) => {
    switch (prio) {
      case 'Critical':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-50 text-red-700 border border-red-200 shadow-2xs">
            <AlertOctagon className="w-3 h-3 text-red-600 shrink-0" />
            CRITICAL
          </span>
        );
      case 'High':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-orange-50 text-orange-700 border border-orange-200 shadow-2xs">
            <AlertTriangle className="w-3 h-3 text-orange-600 shrink-0" />
            HIGH PRIORITY
          </span>
        );
      case 'Medium':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200 shadow-2xs">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0"></span>
            MEDIUM
          </span>
        );
      case 'Low':
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200 shadow-2xs">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0"></span>
            LOW
          </span>
        );
    }
  };

  const getSourceIcon = (sourceType: string) => {
    const t = sourceType.toLowerCase();
    if (t.includes('thermal') || t.includes('viirs') || t.includes('firms')) return <Flame className="w-4 h-4 text-orange-600" />;
    if (t.includes('temporal') || t.includes('insat') || t.includes('geo')) return <Radio className="w-4 h-4 text-blue-600" />;
    if (t.includes('optical') || t.includes('sentinel_2') || t.includes('swir')) return <Eye className="w-4 h-4 text-emerald-600" />;
    if (t.includes('sar') || t.includes('sentinel_1') || t.includes('structural')) return <Layers className="w-4 h-4 text-indigo-600" />;
    if (t.includes('weather') || t.includes('wind') || t.includes('atmospheric') || t.includes('tropomi')) return <Wind className="w-4 h-4 text-sky-600" />;
    if (t.includes('facility') || t.includes('gis') || t.includes('osm')) return <Building2 className="w-4 h-4 text-slate-700" />;
    if (t.includes('historical') || t.includes('baseline')) return <History className="w-4 h-4 text-purple-600" />;
    return <Activity className="w-4 h-4 text-slate-500" />;
  };

  const getHumanReadableSourceName = (source: string, type: string) => {
    const s = (source || '').toUpperCase();
    if (s.includes('NASA_FIRMS_VIIRS') || s.includes('VIIRS')) return 'NASA FIRMS / VIIRS Thermal';
    if (s.includes('INSAT_3DS') || s.includes('INSAT')) return 'INSAT-3DS Geostationary MIR';
    if (s.includes('SENTINEL_2')) return 'Sentinel-2 Multispectral SWIR';
    if (s.includes('SENTINEL_1')) return 'Sentinel-1 C-Band SAR';
    if (s.includes('IMD_WEATHER')) return 'IMD Surface Weather Feed';
    if (s.includes('TROPOMI_ATMOSPHERIC')) return 'Sentinel-5P TROPOMI Trace Gas';
    if (s.includes('OSM_GIDC_GIS')) return 'OSM / GIDC GIS Facility Boundary';
    if (s.includes('HISTORICAL_FINGERPRINT')) return '90-Day Thermal Baseline Fingerprint';
    if (s.includes('LAND_COVER_GIS')) return 'ISRO Land Cover Surface Model';
    if (s.includes('TEMPORAL_RECURRENCE')) return 'Recurrence & Diurnal Analysis';
    return `${source} (${type})`;
  };

  // Render an individual compact evidence card
  const renderEvidenceCard = (item: EvidenceItem, isPrimary: boolean = false) => {
    const isMissing = item.direction === 'MISSING' || item.availability === false;
    const isConflicting = item.direction === 'CONFLICTING';
    const isSupporting = item.direction === 'SUPPORTING';
    const humanName = getHumanReadableSourceName(item.source, item.evidence_type);

    // Special parsing for Historical Fingerprint baseline vs current
    const isHistorical = item.evidence_type?.toLowerCase() === 'historical' || item.source?.toUpperCase().includes('HISTORICAL');

    return (
      <div 
        key={item.id || item.source} 
        className={`rounded-xl border p-4 transition-colors duration-150 flex flex-col justify-between ${
          isPrimary 
            ? 'bg-orange-50/20 border-orange-200/90 shadow-2xs' 
            : isMissing 
            ? 'bg-slate-50/80 border-slate-200 border-dashed opacity-90' 
            : isConflicting 
            ? 'bg-red-50/30 border-red-200/90' 
            : 'bg-white border-slate-200/90 hover:border-slate-300 shadow-2xs'
        }`}
      >
        <div>
          {/* Card Top Row: Source, Direction Badge & Compact Quality/Relevance */}
          <div className="flex items-center justify-between gap-2 pb-2 mb-2 border-b border-slate-100">
            <div className="min-w-0">
              <div className="text-xs font-bold text-slate-900 truncate">
                {humanName}
              </div>
              <div className="text-[10px] font-mono text-slate-400 truncate">
                {item.source}
              </div>
            </div>

            <div className="flex items-center gap-1.5 shrink-0">
              {isSupporting && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" />
                  Supporting
                </span>
              )}
              {isConflicting && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-red-50 text-red-700 border border-red-200">
                  <XCircle className="w-2.5 h-2.5 text-red-600" />
                  Conflicting
                </span>
              )}
              {isMissing && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-200/70 text-slate-600 border border-slate-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
                  Missing Evidence
                </span>
              )}
              {!isSupporting && !isConflicting && !isMissing && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
                  Neutral
                </span>
              )}
            </div>
          </div>

          {/* Missing State vs Actual Evidence Value */}
          {isMissing ? (
            <div className="py-2">
              <p className="text-xs font-semibold text-slate-700 mb-0.5">{item.value || 'Observation unavailable'}</p>
              <p className="text-xs text-slate-500 leading-relaxed">
                {item.explanation || 'No observation record is currently available for this event.'}
              </p>
            </div>
          ) : isHistorical ? (
            /* Historical Fingerprint Special Layout */
            <div className="py-1">
              <div className="text-xs md:text-sm font-bold text-slate-900 mb-2">{item.value}</div>
              <p className="text-xs text-slate-600 leading-relaxed mb-3">{item.explanation}</p>
            </div>
          ) : (
            <div className="py-1">
              <div className="text-xs md:text-sm font-bold text-slate-900 mb-1 leading-snug">
                {item.value}
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                {item.explanation}
              </p>
            </div>
          )}
        </div>

        {/* Card Footer: Compact Quality & Relevance Chips */}
        {!isMissing && (item.quality != null || item.relevance != null) && (
          <div className="flex items-center justify-between pt-2 mt-2 border-t border-slate-100 text-[11px] text-slate-500 font-medium">
            {item.quality != null && (
              <div className="flex items-center gap-1">
                <span>Quality:</span>
                <span className="font-semibold text-slate-700">{Math.round(item.quality * 100)}%</span>
                <div className="w-10 h-1.5 bg-slate-100 rounded-full overflow-hidden ml-0.5 hidden sm:block">
                  <div 
                    className="h-full bg-blue-500 rounded-full" 
                    style={{ width: `${Math.round(item.quality * 100)}%` }}
                  ></div>
                </div>
              </div>
            )}
            {item.relevance != null && (
              <div className="flex items-center gap-1">
                <span>Relevance:</span>
                <span className="font-semibold text-slate-700">{Math.round(item.relevance * 100)}%</span>
                <div className="w-10 h-1.5 bg-slate-100 rounded-full overflow-hidden ml-0.5 hidden sm:block">
                  <div 
                    className="h-full bg-emerald-500 rounded-full" 
                    style={{ width: `${Math.round(item.relevance * 100)}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col font-sans">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-4 md:p-6 overflow-y-auto max-w-[1720px] mx-auto w-full flex flex-col gap-4">
          
          {loading ? (
            /* 26. SKELETON LOADING STATE */
            <div className="space-y-4 animate-pulse">
              <div className="h-20 bg-white border border-slate-200 rounded-xl"></div>
              <div className="h-14 bg-white border border-slate-200 rounded-xl"></div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-36">
                <div className="bg-white border border-slate-200 rounded-xl"></div>
                <div className="bg-white border border-slate-200 rounded-xl"></div>
                <div className="bg-white border border-slate-200 rounded-xl"></div>
              </div>
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 h-96">
                <div className="bg-white border border-slate-200 rounded-xl"></div>
                <div className="bg-white border border-slate-200 rounded-xl"></div>
              </div>
            </div>
          ) : error || !event ? (
            /* 27. ERROR STATE */
            <div className="bg-white border border-slate-200 rounded-xl p-12 flex flex-col items-center justify-center text-center shadow-2xs">
              <div className="w-12 h-12 rounded-full bg-red-50 text-red-600 flex items-center justify-center mb-3">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <h2 className="text-lg font-bold text-slate-900">Event Not Found</h2>
              <p className="text-xs md:text-sm text-slate-500 mt-1 mb-4 max-w-md">
                {error || "We couldn't locate this event in the active registry."}
              </p>
              <div className="flex gap-2">
                <Link 
                  href="/events"
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
                >
                  <ArrowLeft className="w-3.5 h-3.5" /> Back to Directory
                </Link>
                <button
                  onClick={loadData}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition-colors"
                >
                  <RotateCcw className="w-3.5 h-3.5" /> Retry
                </button>
              </div>
            </div>
          ) : (
            <>
              {/* 1. STICKY COMPACT EVENT HEADER */}
              <div className="sticky top-0 z-20 bg-white/95 backdrop-blur-xs border border-slate-200/90 rounded-xl px-5 py-3.5 shadow-2xs flex flex-col lg:flex-row lg:items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <Link 
                    href="/events" 
                    className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-500 hover:text-slate-900 transition-colors shrink-0"
                    title="Back to Events Directory"
                  >
                    <ArrowLeft className="w-4 h-4" />
                  </Link>

                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <h1 className="text-base md:text-lg font-extrabold text-slate-900 uppercase tracking-tight truncate">
                        {event.title}
                      </h1>
                      <span className="font-mono text-xs font-bold text-slate-600 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                        {event.event_id}
                      </span>
                    </div>
                    
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500 mt-0.5">
                      <span>{event.location}</span>
                      {event.nearby_facility && (
                        <span>• Facility: <strong className="text-slate-700">{event.nearby_facility}</strong></span>
                      )}
                      <span>• Source: <strong className="text-slate-700">{event.classification}</strong></span>
                      {event.behavior && (
                        <span>• State: <strong className="text-slate-700">{event.behavior}</strong></span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Right Header Badges & Fast Actions */}
                <div className="flex flex-wrap items-center gap-2 shrink-0">
                  {getPriorityBadge(event.priority)}

                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                    Risk: <strong className="text-slate-900">{event.risk_index}/100</strong>
                  </span>

                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
                    <Clock className="w-3 h-3 text-amber-600" />
                    {event.status}
                  </span>

                  {/* Action Buttons */}
                  <div className="flex items-center gap-1.5 ml-1">
                    <Link
                      href={`/live-map/${event.event_id}`}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-700 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200/80 px-2.5 py-1 rounded-lg transition-colors"
                      title="View this event on Live Map"
                    >
                      <MapPin className="w-3.5 h-3.5 text-indigo-600" />
                      <span>View on Map</span>
                    </Link>

                    {timeline.length > 0 && (
                      <button
                        onClick={() => setTimelineModalOpen(true)}
                        className="inline-flex items-center gap-1 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 border border-slate-200 px-2.5 py-1 rounded-lg transition-colors"
                      >
                        <Calendar className="w-3.5 h-3.5 text-slate-500" />
                        Timeline ({timeline.length})
                      </button>
                    )}

                    <button
                      onClick={() => setVerifyModalOpen(true)}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded-lg shadow-2xs transition-colors"
                    >
                      <CheckCircle className="w-3.5 h-3.5" />
                      Verify Event
                    </button>
                  </div>
                </div>
              </div>

              {/* 2. EVENT AT A GLANCE METRICS ROW */}
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5">
                <div className="bg-white border border-slate-200/90 rounded-xl p-3 shadow-2xs">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-0.5">Observations</span>
                  <div className="text-base font-bold text-slate-900">
                    {event.observations_count || timeline.length || 1} Passes
                  </div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-xl p-3 shadow-2xs">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-0.5">FRP Peak</span>
                  <div className="text-base font-bold text-orange-600">
                    {timeline.length > 0 ? `${Math.max(...timeline.map(t => t.frp || 0)).toFixed(1)} MW` : 'Active Heat'}
                  </div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-xl p-3 shadow-2xs">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-0.5">FRP Change</span>
                  <div className={`text-base font-bold ${event.frp_change_pct > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                    {event.frp_change_pct != null ? `${event.frp_change_pct > 0 ? '+' : ''}${event.frp_change_pct}%` : 'Stable'}
                  </div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-xl p-3 shadow-2xs">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-0.5">Footprint</span>
                  <div className="text-base font-bold text-slate-900">
                    {event.footprint_expansion_factor ? `${event.footprint_expansion_factor}× Expansion` : '1.0× Point'}
                  </div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-xl p-3 shadow-2xs">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-0.5">Evidence Sources</span>
                  <div className="text-base font-bold text-slate-900">
                    {event.evidence?.length || 0} Connected
                  </div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-xl p-3 shadow-2xs">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-0.5">Completeness</span>
                  <div className="text-base font-bold text-blue-600">
                    {event.evidence_completeness != null ? `${Math.round(event.evidence_completeness * 100)}%` : '90%'}
                  </div>
                </div>
              </div>

              {/* 3. WHY / WHY NOT / WHAT CHANGED SECTION */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
                {/* WHY */}
                <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-2xs flex flex-col">
                  <div className="flex items-center gap-1.5 pb-2 mb-2 border-b border-slate-100 text-xs font-bold text-emerald-800">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>WHY (CONFIRMING REASONS)</span>
                  </div>
                  <ul className="space-y-2 flex-1">
                    {(event.explanations?.why || []).map((reason, i) => (
                      <li key={i} className="text-xs text-slate-700 leading-relaxed flex items-start gap-1.5">
                        <span className="text-emerald-500 font-bold">•</span>
                        <span>{reason}</span>
                      </li>
                    ))}
                    {(!event.explanations?.why || event.explanations.why.length === 0) && (
                      <li className="text-xs text-slate-400 italic">No supporting explanations recorded.</li>
                    )}
                  </ul>
                </div>

                {/* WHY NOT */}
                <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-2xs flex flex-col">
                  <div className="flex items-center gap-1.5 pb-2 mb-2 border-b border-slate-100 text-xs font-bold text-amber-800">
                    <XCircle className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>WHY NOT (EXCLUSION & CONTRADICTION)</span>
                  </div>
                  <ul className="space-y-2 flex-1">
                    {(event.explanations?.why_not || []).map((reason, i) => (
                      <li key={i} className="text-xs text-slate-700 leading-relaxed flex items-start gap-1.5">
                        <span className="text-amber-500 font-bold">•</span>
                        <span>{reason}</span>
                      </li>
                    ))}
                    {(!event.explanations?.why_not || event.explanations.why_not.length === 0) && (
                      <li className="text-xs text-slate-400 italic">No exclusion or contradiction signals.</li>
                    )}
                  </ul>
                </div>

                {/* WHAT CHANGED */}
                <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-2xs flex flex-col">
                  <div className="flex items-center gap-1.5 pb-2 mb-2 border-b border-slate-100 text-xs font-bold text-blue-800">
                    <TrendingUp className="w-4 h-4 text-blue-600 shrink-0" />
                    <span>WHAT CHANGED (DYNAMIC DIVERGENCE)</span>
                  </div>
                  <ul className="space-y-2 flex-1">
                    {(event.explanations?.what_changed || []).map((change, i) => (
                      <li key={i} className="text-xs text-slate-700 leading-relaxed flex items-start gap-1.5">
                        <span className="text-blue-500 font-bold">•</span>
                        <span>{change}</span>
                      </li>
                    ))}
                    {(!event.explanations?.what_changed || event.explanations.what_changed.length === 0) && (
                      <li className="text-xs text-slate-400 italic">No sudden temporal shift detected.</li>
                    )}
                  </ul>
                </div>
              </div>

              {/* 4. EVIDENCE HEALTH SUMMARY */}
              <div className="bg-white border border-slate-200/90 rounded-xl px-4 py-3 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-900">Evidence Health: </span>
                  <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    {evidenceHealth.status}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 font-medium">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span><strong>{evidenceHealth.supporting}</strong> Supporting</span>
                  </div>

                  {evidenceHealth.missing > 0 && (
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-slate-400"></span>
                      <span><strong>{evidenceHealth.missing}</strong> Missing / Obscured</span>
                    </div>
                  )}

                  {evidenceHealth.conflicting > 0 && (
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-red-500"></span>
                      <span><strong>{evidenceHealth.conflicting}</strong> Conflicting</span>
                    </div>
                  )}

                  <div className="hidden md:flex items-center gap-1 text-slate-400">
                    |
                  </div>

                  <div>
                    Avg Quality: <strong className="text-slate-900">{evidenceHealth.avgQuality}%</strong>
                  </div>
                </div>
              </div>

              {/* 5. REORGANIZED MULTI-TIER EVIDENCE SECTION */}
              <div className="space-y-4">
                
                {/* SECTION 1: PRIMARY EVIDENCE */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h2 className="text-xs md:text-sm font-bold text-slate-900 uppercase tracking-wider">
                      Primary Evidence (Thermal Detections)
                    </h2>
                    <span className="text-[11px] font-semibold text-slate-500">
                      Core Sensor Pass
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {evidenceGroups.primary.map(item => renderEvidenceCard(item, true))}
                    {evidenceGroups.primary.length === 0 && (
                      <div className="p-4 rounded-xl border border-slate-200 bg-white text-xs text-slate-400 italic">
                        No primary thermal evidence record found.
                      </div>
                    )}
                  </div>
                </div>

                {/* SECTION 2: CORROBORATING EVIDENCE */}
                <div>
                  <div className="flex items-center justify-between mb-2 pt-2 border-t border-slate-200">
                    <h2 className="text-xs md:text-sm font-bold text-slate-900 uppercase tracking-wider">
                      Corroborating Evidence (Multi-Sensor Overpasses)
                    </h2>
                    <span className="text-[11px] font-semibold text-slate-500">
                      GEO • SWIR • SAR • Weather
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {evidenceGroups.corroborating.map(item => renderEvidenceCard(item, false))}
                    {evidenceGroups.corroborating.length === 0 && (
                      <div className="p-4 rounded-xl border border-slate-200 bg-white text-xs text-slate-400 italic">
                        No corroborating sensor evidence records found.
                      </div>
                    )}
                  </div>
                </div>

                {/* SECTION 3: CONTEXTUAL EVIDENCE & HISTORICAL FINGERPRINT */}
                <div>
                  <div className="flex items-center justify-between mb-2 pt-2 border-t border-slate-200">
                    <h2 className="text-xs md:text-sm font-bold text-slate-900 uppercase tracking-wider">
                      Contextual & Historical Baseline Intelligence
                    </h2>
                    <span className="text-[11px] font-semibold text-slate-500">
                      Infrastructure • 90-Day Baseline
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {evidenceGroups.contextual.map(item => renderEvidenceCard(item, false))}
                    {evidenceGroups.contextual.length === 0 && (
                      <div className="p-4 rounded-xl border border-slate-200 bg-white text-xs text-slate-400 italic">
                        No contextual or facility GIS records found.
                      </div>
                    )}
                  </div>
                </div>

              </div>

              {/* 17. VERIFICATION ACTION / AUDIT TRAIL AREA */}
              <div className="bg-white border border-slate-200/90 rounded-xl p-5 shadow-2xs mt-2 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Analyst Verification & Operational Decision</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Current Status: <strong className="text-slate-800">{event.status}</strong> • Decision audit record is appended to incident history.
                  </p>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={() => { setVerifyDecision('confirmed'); setVerifyModalOpen(true); }}
                    className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-2xs transition-colors"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Confirm Event
                  </button>

                  <button
                    onClick={() => { setVerifyDecision('rejected'); setVerifyModalOpen(true); }}
                    className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors border border-slate-200"
                  >
                    <XCircle className="w-3.5 h-3.5 text-slate-500" />
                    Reject (False Alarm)
                  </button>

                  <button
                    onClick={() => { setVerifyDecision('needs_more_evidence'); setVerifyModalOpen(true); }}
                    className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-amber-50 hover:bg-amber-100 text-amber-800 text-xs font-semibold transition-colors border border-amber-200"
                  >
                    <Clock className="w-3.5 h-3.5 text-amber-600" />
                    Request More Evidence
                  </button>
                </div>
              </div>

              {/* Verification History Logs */}
              {event.verifications && event.verifications.length > 0 && (
                <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-2xs">
                  <span className="text-xs font-bold text-slate-900 block mb-2">Verification Audit Trail</span>
                  <div className="space-y-2">
                    {event.verifications.map((v, i) => (
                      <div key={i} className="flex flex-col sm:flex-row sm:items-center justify-between text-xs py-1.5 px-2.5 rounded bg-slate-50 border border-slate-100 gap-1">
                        <div className="flex items-center gap-2">
                          <strong className="text-slate-800">{v.reviewer}</strong>
                          <span className="text-slate-400">•</span>
                          <span className="font-semibold text-blue-700">{v.decision}</span>
                          {v.comment && <span className="text-slate-600 italic">"{v.comment}"</span>}
                        </div>
                        <div className="text-[11px] text-slate-400">
                          {v.timestamp ? format(parseISO(v.timestamp), 'dd MMM yyyy, HH:mm') : 'Recorded'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </>
          )}

        </main>
      </div>

      {/* TIMELINE MODAL */}
      {timelineModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-3xl w-full p-6 max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">Multi-Sensor Observation Timeline</h3>
                <p className="text-xs text-slate-500 mt-0.5">Chronological passes recorded for {event?.event_id}</p>
              </div>
              <button 
                onClick={() => setTimelineModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="overflow-y-auto flex-1 divide-y divide-slate-100">
              {timeline.map((tp, idx) => (
                <div key={idx} className="py-2.5 flex items-center justify-between text-xs gap-4">
                  <div className="flex items-center gap-2.5">
                    <div className="w-2 h-2 rounded-full bg-orange-500 shrink-0"></div>
                    <div>
                      <span className="font-bold text-slate-800">{tp.satellite}</span>
                      <div className="text-[11px] text-slate-400">
                        {tp.timestamp ? format(parseISO(tp.timestamp), 'dd MMM yyyy, HH:mm:ss') : 'Unknown time'}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-right">
                    <div>
                      <span className="text-[11px] text-slate-400 block">FRP</span>
                      <strong className="text-orange-600 font-bold">{tp.frp} MW</strong>
                    </div>
                    <div>
                      <span className="text-[11px] text-slate-400 block">Temp</span>
                      <span className="text-slate-700 font-semibold">{tp.brightness_temperature} K</span>
                    </div>
                    <div>
                      <span className="text-[11px] text-slate-400 block">Confidence</span>
                      <span className="text-emerald-700 font-semibold">{Math.round((tp.confidence || 0) * 100)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-4 border-t border-slate-200 mt-4 text-right">
              <button
                onClick={() => setTimelineModalOpen(false)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* VERIFY MODAL */}
      {verifyModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-lg w-full p-6">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-900">Verify Event Assessment</h3>
                <p className="text-xs text-slate-500 mt-0.5">{event?.event_id} • {event?.title}</p>
              </div>
              <button 
                onClick={() => setVerifyModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {verifySuccessMsg ? (
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs font-semibold text-center">
                <CheckCircle2 className="w-6 h-6 text-emerald-600 mx-auto mb-1.5" />
                {verifySuccessMsg}
              </div>
            ) : (
              <form onSubmit={handleVerifySubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">Decision</label>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => setVerifyDecision('confirmed')}
                      className={`p-2 rounded-lg text-xs font-semibold border text-center transition-colors ${
                        verifyDecision === 'confirmed'
                          ? 'bg-emerald-50 border-emerald-500 text-emerald-800 ring-1 ring-emerald-500'
                          : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      Confirm
                    </button>
                    <button
                      type="button"
                      onClick={() => setVerifyDecision('rejected')}
                      className={`p-2 rounded-lg text-xs font-semibold border text-center transition-colors ${
                        verifyDecision === 'rejected'
                          ? 'bg-red-50 border-red-500 text-red-800 ring-1 ring-red-500'
                          : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      Reject
                    </button>
                    <button
                      type="button"
                      onClick={() => setVerifyDecision('needs_more_evidence')}
                      className={`p-2 rounded-lg text-xs font-semibold border text-center transition-colors ${
                        verifyDecision === 'needs_more_evidence'
                          ? 'bg-amber-50 border-amber-500 text-amber-800 ring-1 ring-amber-500'
                          : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      Need Evidence
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1.5">Analyst Note / Justification</label>
                  <textarea
                    value={verifyComment}
                    onChange={(e) => setVerifyComment(e.target.value)}
                    placeholder="Provide operational reason for this verification decision..."
                    rows={3}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  ></textarea>
                </div>

                <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-200">
                  <button
                    type="button"
                    onClick={() => setVerifyModalOpen(false)}
                    className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isVerifying}
                    className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-2xs transition-colors disabled:opacity-50"
                  >
                    {isVerifying ? 'Submitting...' : 'Submit Verification'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
