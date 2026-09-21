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
  Building2,
  AlertTriangle,
  CheckCircle,
  CheckCircle2,
  HelpCircle,
  XCircle,
  Send,
  Radio,
  FileCheck,
  History,
  Eye,
  Wind,
  Sparkles,
  Filter
} from 'lucide-react';
import { EventDetail, TimelinePoint, EvidenceItem } from '../lib/types';
import { verifyEvent } from '../lib/api';

interface EventDetailPanelProps {
  event: EventDetail | null;
  timeline: TimelinePoint[];
  onEventUpdated: () => void;
}

export function getEventOverviewMetrics(event: EventDetail | null, timeline: TimelinePoint[] = []) {
  if (!event) {
    return {
      frpValue: 'Not available',
      frpLabel: 'current thermal intensity',
      frpTrend: '',
      frpColor: 'text-slate-600',
      footprintValue: 'Not available',
      footprintLabel: 'current vs baseline',
      footprintTrend: '',
      footprintColor: 'text-slate-600',
      observationsValue: 'Not available',
      observationsLabel: 'last 6 hours',
      observationsTrend: '',
      behaviorValue: 'Not available',
      behaviorLabel: 'pattern status',
      behaviorColor: 'text-slate-600',
    };
  }

  // 1. OBSERVATIONS COUNT (from event or chronological timeline)
  let obsCount: number | null = null;
  if (event.observations_count != null && !isNaN(event.observations_count)) {
    obsCount = Number(event.observations_count);
  } else if (timeline && timeline.length > 0) {
    obsCount = timeline.length;
  }
  const observationsValue = obsCount != null ? `${obsCount}` : 'Not available';
  const observationsLabel = 'last 6 hours';
  const observationsTrend = obsCount != null && obsCount > 0 ? '↑' : '';

  // 2. BEHAVIOR (derive from actual event.behavior, distinct from state)
  const behaviorValue = event.behavior || 'Not available';
  let behaviorLabel = 'pattern status';
  let behaviorColor = 'text-red-600';
  const bLower = (event.behavior || '').toLowerCase();
  if (bLower.includes('rapid') || bLower.includes('expansion')) {
    behaviorLabel = 'rapid increase';
    behaviorColor = 'text-red-600';
  } else if (bLower.includes('spike') || bLower.includes('surge')) {
    behaviorLabel = 'acute surge';
    behaviorColor = 'text-red-600';
  } else if (bLower.includes('stable')) {
    behaviorLabel = 'within baseline';
    behaviorColor = 'text-emerald-600';
  } else if (bLower.includes('declining') || bLower.includes('cooling')) {
    behaviorLabel = 'active cooling';
    behaviorColor = 'text-blue-600';
  } else if (event.abnormality) {
    behaviorLabel = event.abnormality.toLowerCase();
    behaviorColor = event.abnormality.toLowerCase().includes('normal') ? 'text-emerald-600' : 'text-red-600';
  }

  // 3. FOOTPRINT (from event.footprint_expansion_factor or parsed historical baseline)
  let fpFactor: number | null = null;
  if (event.footprint_expansion_factor != null && !isNaN(event.footprint_expansion_factor)) {
    fpFactor = Number(event.footprint_expansion_factor);
  } else if (event.evidence) {
    const hist = event.evidence.find(
      (e) => (e.evidence_type || '').toLowerCase().includes('historical') || (e.source || '').toLowerCase().includes('fingerprint')
    );
    if (hist && hist.value) {
      const match = hist.value.match(/([\d.]+)x/i);
      if (match) fpFactor = parseFloat(match[1]);
    }
  }

  let footprintValue = 'Not available';
  let footprintLabel = 'current vs baseline';
  let footprintTrend = '';
  let footprintColor = 'text-slate-800';

  if (fpFactor != null) {
    footprintValue = `${fpFactor.toFixed(1)}×`;
    if (fpFactor > 1.05) {
      footprintLabel = 'expanding';
      footprintTrend = '↑';
      footprintColor = 'text-red-600';
    } else if (fpFactor < 0.95) {
      footprintLabel = 'contracting';
      footprintTrend = '↓';
      footprintColor = 'text-blue-600';
    } else {
      footprintLabel = 'stable';
      footprintTrend = '';
      footprintColor = 'text-slate-800';
    }
  }

  // 4. FRP (Fire Radiative Power)
  // Check for explicit API change percentage if available
  let frpPct: number | null = null;
  if (event.frp_change_pct != null && !isNaN(event.frp_change_pct) && event.frp_change_pct !== 0) {
    frpPct = Number(event.frp_change_pct);
  } else if (event.evidence) {
    for (const ev of event.evidence) {
      if (ev.value) {
        const match = ev.value.match(/([+-]?\d+(?:\.\d+)?)\s*%/);
        if (match) {
          frpPct = parseFloat(match[1]);
          break;
        }
      }
    }
  }

  // Find latest chronological FRP from timeline
  let latestFrp: number | null = null;
  if (timeline && timeline.length > 0) {
    const sortedTimeline = [...timeline].sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
    const lastPoint = sortedTimeline[sortedTimeline.length - 1];
    if (lastPoint && lastPoint.frp != null && !isNaN(lastPoint.frp)) {
      latestFrp = Number(lastPoint.frp);
    }
  }

  if (latestFrp == null && event.evidence) {
    for (const ev of event.evidence) {
      if (ev.value && (ev.evidence_type === 'Thermal' || ev.source.includes('VIIRS') || ev.value.includes('MW'))) {
        const match = ev.value.match(/([\d.]+)\s*MW/i);
        if (match) {
          latestFrp = parseFloat(match[1]);
          break;
        }
      }
    }
  }

  let frpValue = 'Not available';
  let frpLabel = 'current thermal intensity';
  let frpTrend = '';
  let frpColor = 'text-slate-800';

  if (frpPct != null) {
    const sign = frpPct > 0 ? '+' : '';
    frpValue = `${sign}${frpPct.toFixed(0)}%`;
    frpLabel = 'vs historical avg.';
    if (frpPct > 0) {
      frpTrend = '↑';
      frpColor = 'text-red-600';
    } else if (frpPct < 0) {
      frpTrend = '↓';
      frpColor = 'text-emerald-600';
    } else {
      frpTrend = '';
      frpColor = 'text-slate-800';
    }
  } else if (latestFrp != null) {
    frpValue = `${latestFrp.toFixed(1)} MW`;
    frpLabel = 'current thermal intensity';
    frpTrend = latestFrp > 50 ? '↑' : '';
    frpColor = latestFrp > 50 ? 'text-red-600' : 'text-slate-800';
  }

  return {
    frpValue,
    frpLabel,
    frpTrend,
    frpColor,
    footprintValue,
    footprintLabel,
    footprintTrend,
    footprintColor,
    observationsValue,
    observationsLabel,
    observationsTrend,
    behaviorValue,
    behaviorLabel,
    behaviorColor,
  };
}

export const EventDetailPanel: React.FC<EventDetailPanelProps> = ({
  event,
  timeline,
  onEventUpdated,
}) => {
  const [activeTab, setActiveTab] = useState<'Overview' | 'Evidence' | 'Timeline' | 'Media' | 'Actions'>('Overview');
  const [evidenceFilter, setEvidenceFilter] = useState<'ALL' | 'SUPPORTING' | 'CONFLICTING' | 'MISSING'>('ALL');
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

  const metrics = getEventOverviewMetrics(event, timeline);

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

  const getSourceIcon = (type: string, source: string) => {
    const t = (type || '').toLowerCase();
    const s = (source || '').toLowerCase();
    if (t.includes('thermal') || s.includes('viirs') || s.includes('firms') || s.includes('modis')) {
      return <Flame className="w-3.5 h-3.5 text-orange-500 shrink-0" />;
    }
    if (t.includes('facility') || s.includes('osm') || s.includes('gidc') || s.includes('gis')) {
      return <Building2 className="w-3.5 h-3.5 text-indigo-500 shrink-0" />;
    }
    if (t.includes('historical') || s.includes('fingerprint') || s.includes('baseline')) {
      return <History className="w-3.5 h-3.5 text-blue-500 shrink-0" />;
    }
    if (t.includes('sar') || s.includes('sentinel_1') || s.includes('radar')) {
      return <Radio className="w-3.5 h-3.5 text-purple-500 shrink-0" />;
    }
    if (t.includes('optical') || s.includes('sentinel_2') || t.includes('swir')) {
      return <Eye className="w-3.5 h-3.5 text-cyan-600 shrink-0" />;
    }
    if (t.includes('weather') || s.includes('imd') || s.includes('wind')) {
      return <Wind className="w-3.5 h-3.5 text-teal-500 shrink-0" />;
    }
    if (t.includes('temporal') || s.includes('insat')) {
      return <Clock className="w-3.5 h-3.5 text-amber-500 shrink-0" />;
    }
    return <Layers className="w-3.5 h-3.5 text-slate-500 shrink-0" />;
  };

  const renderEvidenceCard = (item: EvidenceItem, isPrimary = false) => {
    const isSupporting = item.direction === 'SUPPORTING';
    const isConflicting = item.direction === 'CONFLICTING';
    const isMissing = item.direction === 'MISSING';
    const isHistorical = (item.evidence_type || '').toLowerCase().includes('historical') || (item.source || '').toLowerCase().includes('fingerprint');
    const isFacility = (item.evidence_type || '').toLowerCase().includes('facility') || (item.source || '').toLowerCase().includes('gis');

    return (
      <div 
        key={item.id} 
        className={`rounded-lg p-3.5 transition-all duration-150 border ${
          isPrimary
            ? 'bg-white border-slate-200/90 shadow-2xs border-l-3 border-l-orange-500 hover:border-slate-300'
            : isConflicting
            ? 'bg-red-50/20 border-red-200 hover:border-red-300'
            : isMissing
            ? 'bg-slate-50/50 border-dashed border-slate-200 text-slate-400'
            : 'bg-white border-slate-200/80 hover:border-slate-300 shadow-2xs'
        }`}
      >
        <div className="flex items-center justify-between gap-2 mb-1.5">
          <div className="flex items-center gap-2 min-w-0">
            {getSourceIcon(item.evidence_type, item.source)}
            <span className="font-bold text-slate-800 tracking-tight text-[11px] truncate">
              {item.source}
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              • {item.evidence_type}
            </span>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            {isSupporting && (
              <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200/60">
                SUPPORTING
              </span>
            )}
            {isConflicting && (
              <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-red-50 text-red-700 border border-red-200">
                ⚠ CONFLICTING
              </span>
            )}
            {isMissing && (
              <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-slate-100 text-slate-500 border border-slate-200">
                MISSING
              </span>
            )}
          </div>
        </div>

        <div className="mt-1">
          <div className="text-xs font-bold text-slate-900 leading-snug">
            {item.value}
          </div>
          {item.explanation && (
            <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
              {item.explanation}
            </p>
          )}
        </div>

        {!isMissing && (
          <div className="mt-2.5 pt-2 border-t border-slate-100 grid grid-cols-2 gap-3">
            <div>
              <div className="flex justify-between items-center text-[10px] font-medium text-slate-500 mb-1">
                <span>Quality</span>
                <span className="text-slate-800 font-bold">
                  {item.quality != null ? `${Math.round(item.quality * 100)}%` : '--'}
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-1 overflow-hidden">
                <div 
                  className="bg-emerald-500 h-full rounded-full transition-all duration-300" 
                  style={{ width: `${item.quality != null ? item.quality * 100 : 0}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center text-[10px] font-medium text-slate-500 mb-1">
                <span>Relevance</span>
                <span className="text-slate-800 font-bold">
                  {item.relevance != null ? `${Math.round(item.relevance * 100)}%` : '--'}
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-1 overflow-hidden">
                <div 
                  className="bg-indigo-500 h-full rounded-full transition-all duration-300" 
                  style={{ width: `${item.relevance != null ? item.relevance * 100 : 0}%` }}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-white border border-slate-200/90 rounded-xl shadow-sm overflow-hidden flex flex-col h-[740px]">
      {/* 1. Event Workspace Header */}
      <div className="px-5 py-3.5 sm:py-4 border-b border-slate-200/80 bg-white">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="text-[14px] sm:text-[15px] font-bold text-slate-900 tracking-tight">{event.event_id}</span>
            <span className="text-[10px] sm:text-[11px] font-semibold px-2 py-0.5 rounded-md bg-red-50 text-red-700 border border-red-200/80 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-red-600 animate-pulse"></span>
              {event.risk_level === 'Critical' ? 'Critical Priority' : `${event.priority || 'High'} Priority`}
            </span>
            <span className="text-[10px] sm:text-[11px] font-semibold px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200/80 flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
              {event.status || 'Needs Verification'}
            </span>
          </div>
          <button className="text-slate-400 hover:text-slate-600 p-1 rounded-md hover:bg-slate-100 transition-colors">
            <MoreVertical className="w-4 h-4" />
          </button>
        </div>

        <h2 className="text-[17px] sm:text-[18px] font-semibold text-slate-900 leading-snug">
          {event.title}
        </h2>
        <div className="flex items-center gap-1.5 text-[13px] sm:text-[14px] text-slate-500 mt-0.5 font-normal">
          <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span>{event.location}</span>
        </div>
      </div>

      {/* 2. Sub-navigation Tabs */}
      <div className="px-5 border-b border-slate-200/80 bg-slate-50/50 flex items-center gap-6 text-xs font-semibold h-[48px]">
        {(['Overview', 'Evidence', 'Timeline', 'Media', 'Actions'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`h-full relative px-1 flex items-center text-[13px] transition-colors ${
              activeTab === tab
                ? 'text-indigo-600 font-bold border-b-2 border-indigo-600'
                : 'text-slate-500 hover:text-slate-800 font-medium'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* 3. Tab Body Content (Scrollable) */}
      <div className="flex-1 overflow-y-auto p-5 text-xs">
        {activeTab === 'Overview' && (
          <>
            {/* Satellite Context Preview Canvas */}
            <div className="w-full h-36 rounded-xl overflow-hidden relative border border-slate-200 bg-slate-900 group cursor-pointer mb-4" onClick={() => setImageModalOpen(true)}>
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
                {event.location || 'Unknown Location'}
              </div>
              {/* Thermal Hotspot Pulsing Indicator */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
                <span className="w-8 h-8 rounded-full bg-red-500/40 animate-ping absolute"></span>
                <span className="w-3.5 h-3.5 rounded-full bg-red-500 ring-2 ring-white shadow-lg"></span>
              </div>
            </div>

            {/* Compact 2-Column Metadata Grid */}
            <div className="grid grid-cols-[1fr_auto] gap-y-2.5 items-center text-[12px] sm:text-[13px]">
              <div className="flex items-center gap-2 text-slate-500">
                <Compass className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span className="font-normal">Latitude / Longitude</span>
              </div>
              <div className="font-semibold text-slate-800 text-right font-mono text-[12px] sm:text-[13px]">
                {event.latitude != null ? `${event.latitude.toFixed(2)}° N` : '--'}, {event.longitude != null ? `${event.longitude.toFixed(2)}° E` : '--'}
              </div>

              <div className="flex items-center gap-2 text-slate-500">
                <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span className="font-normal">First Seen</span>
              </div>
              <div className="font-semibold text-slate-800 text-right">
                {event.first_seen ? new Date(event.first_seen).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : 'Unknown'}, {event.first_seen ? new Date(event.first_seen).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) : '--:--'}
              </div>

              <div className="flex items-center gap-2 text-slate-500">
                <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span className="font-normal">Last Seen</span>
              </div>
              <div className="font-semibold text-slate-800 text-right">
                {event.last_seen ? new Date(event.last_seen).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : 'Unknown'}, {event.last_seen ? new Date(event.last_seen).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) : '--:--'}
              </div>

              <div className="flex items-center gap-2 text-slate-500">
                <Radio className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span className="font-normal">Observations</span>
              </div>
              <div className="font-semibold text-slate-800 text-right">
                {metrics.observationsValue} (last 6 hours)
              </div>

              <div className="flex items-center gap-2 text-slate-500">
                <Building className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span className="font-normal">Nearby Facility</span>
              </div>
              <div className="font-semibold text-slate-800 text-right truncate max-w-[220px]">
                {event.nearby_facility}
              </div>

              <div className="flex items-center gap-2 text-slate-500">
                <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <span className="font-normal">District</span>
              </div>
              <div className="font-semibold text-slate-800 text-right truncate max-w-[220px]">
                {event.district}
              </div>
            </div>

            {/* Subtle Divider between Context and Assessment */}
            <div className="my-4 border-b border-slate-200/80" />

            {/* 4 KPI Cards Assessment Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3">
              <div className="bg-slate-50/70 border border-slate-200/90 rounded-xl p-3 sm:p-3.5 flex flex-col justify-between min-h-[86px]">
                <div className="text-[11px] sm:text-[12px] text-slate-500 font-medium leading-tight">Classification Confidence</div>
                <div className="text-[18px] sm:text-[20px] font-bold text-emerald-600 leading-snug pb-0.5">
                  {event.confidence != null ? (event.confidence * 100).toFixed(0) : '--'}%
                </div>
              </div>

              <div className="bg-slate-50/70 border border-slate-200/90 rounded-xl p-3 sm:p-3.5 flex flex-col justify-between min-h-[86px]">
                <div className="text-[11px] sm:text-[12px] text-slate-500 font-medium leading-tight">Evidence Completeness</div>
                <div className="text-[18px] sm:text-[20px] font-bold text-amber-600 leading-snug pb-0.5">
                  {event.evidence_completeness != null ? (event.evidence_completeness * 100).toFixed(0) : '--'}%
                </div>
              </div>

              <div className="bg-red-50/40 border border-red-200/70 rounded-xl p-3 sm:p-3.5 flex flex-col justify-between min-h-[86px]">
                <div className="text-[11px] sm:text-[12px] text-red-600 font-medium leading-tight">Risk Index</div>
                <div className="text-[18px] sm:text-[20px] font-bold text-red-600 leading-snug pb-0.5">
                  {event.risk_index != null ? event.risk_index.toFixed(0) : '--'}{' '}
                  <span className="text-[11px] font-normal text-slate-400">/ 100</span>
                </div>
              </div>

              <div className="bg-red-50/40 border border-red-200/70 rounded-xl p-3 sm:p-3.5 flex flex-col justify-between min-h-[86px]">
                <div className="text-[11px] sm:text-[12px] text-red-600 font-medium leading-tight">Priority</div>
                <div className="text-[18px] sm:text-[20px] font-bold text-red-600 leading-snug pb-0.5">
                  {event.risk_level === 'Critical' ? 'Critical' : event.priority || 'High'}
                </div>
              </div>
            </div>

            {/* Current Assessment Alert Panel */}
            <div className="mt-3.5 sm:mt-4 bg-red-50/60 border border-red-200/80 rounded-xl p-3.5 sm:p-4 flex items-start gap-3">
              <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-[13px] font-semibold text-red-800 tracking-tight">CURRENT ASSESSMENT</div>
                <div className="text-[13px] sm:text-[14px] text-red-700 leading-relaxed mt-0.5">
                  {event.current_assessment}
                </div>
              </div>
            </div>

            {/* "What Happened?" Section with 4 Cards */}
            <div className="mt-4.5 sm:mt-5">
              <h4 className="text-[12px] sm:text-[13px] font-bold text-slate-900 uppercase tracking-wider mb-2.5">
                WHAT HAPPENED?
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-2.5">
                <div className="bg-white border border-slate-200/90 rounded-xl p-2.5 sm:p-3 shadow-2xs flex flex-col justify-between min-h-[80px]">
                  <div className="text-[11px] text-slate-500 font-medium">FRP</div>
                  <div className={`text-[15px] sm:text-[16px] font-bold flex items-center gap-0.5 leading-snug pb-0.5 ${metrics.frpColor}`}>
                    {metrics.frpTrend && <span>{metrics.frpTrend}</span>} {metrics.frpValue}
                  </div>
                  <div className="text-[10px] sm:text-[11px] text-slate-400 truncate">{metrics.frpLabel}</div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-xl p-2.5 sm:p-3 shadow-2xs flex flex-col justify-between min-h-[80px]">
                  <div className="text-[11px] text-slate-500 font-medium">Footprint</div>
                  <div className={`text-[15px] sm:text-[16px] font-bold flex items-center gap-0.5 leading-snug pb-0.5 ${metrics.footprintColor}`}>
                    {metrics.footprintTrend && <span>{metrics.footprintTrend}</span>} {metrics.footprintValue}
                  </div>
                  <div className="text-[10px] sm:text-[11px] text-slate-400 truncate">{metrics.footprintLabel}</div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-xl p-2.5 sm:p-3 shadow-2xs flex flex-col justify-between min-h-[80px]">
                  <div className="text-[11px] text-slate-500 font-medium">Observations</div>
                  <div className="text-[15px] sm:text-[16px] font-bold text-red-600 flex items-center gap-0.5 leading-snug pb-0.5">
                    {metrics.observationsTrend && <span>{metrics.observationsTrend}</span>} {metrics.observationsValue}
                  </div>
                  <div className="text-[10px] sm:text-[11px] text-slate-400 truncate">{metrics.observationsLabel}</div>
                </div>

                <div className="bg-white border border-slate-200/90 rounded-xl p-2.5 sm:p-3 shadow-2xs flex flex-col justify-between min-h-[80px]">
                  <div className="text-[11px] text-slate-500 font-medium">Behavior</div>
                  <div className={`text-[15px] sm:text-[16px] font-bold leading-snug pb-0.5 ${metrics.behaviorColor}`}>
                    {metrics.behaviorValue}
                  </div>
                  <div className="text-[10px] sm:text-[11px] text-slate-400 truncate">{metrics.behaviorLabel}</div>
                </div>
              </div>
            </div>

            {/* Explainability Breakdown (WHY / WHY NOT) */}
            <div className="mt-5.5 sm:mt-6 space-y-2.5">
              <div className="bg-slate-50/70 border border-slate-200/90 rounded-xl p-3 sm:p-3.5">
                <div className="text-[11px] sm:text-[12px] font-bold text-slate-800 uppercase tracking-wide">
                  WHY {(event.classification || 'FOREST FIRE').toUpperCase()}?
                </div>
                <ul className="list-disc list-inside text-[12px] text-slate-600 space-y-1 mt-1.5 leading-relaxed">
                  {event.explanations?.why?.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              </div>

              {event.explanations?.why_not && event.explanations.why_not.length > 0 && (
                <div className="bg-slate-50/70 border border-slate-200/90 rounded-xl p-3 sm:p-3.5">
                  <div className="text-[11px] sm:text-[12px] font-bold text-slate-800 uppercase tracking-wide">
                    WHY NOT ROUTINE FLARE?
                  </div>
                  <ul className="list-disc list-inside text-[12px] text-slate-600 space-y-1 mt-1.5 leading-relaxed">
                    {event.explanations.why_not.map((wn, i) => (
                      <li key={i}>{wn}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Bottom Action Buttons */}
            <div className="grid grid-cols-3 gap-2 pt-3">
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
            {/* 1. Compact Multi-Sensor Contribution Summary (90-110px) */}
            {(() => {
              const allItems = event.evidence || [];
              const supportingItems = allItems.filter(e => e.direction === 'SUPPORTING');
              const conflictingItems = allItems.filter(e => e.direction === 'CONFLICTING');
              const missingItems = allItems.filter(e => e.direction === 'MISSING');
              const total = allItems.length;
              const supportPct = total > 0 ? Math.round((supportingItems.length / total) * 100) : 100;
              const activeCategories = Array.from(new Set(allItems.map(e => e.evidence_type))).filter(Boolean);

              // Semantic Groups
              const isPrimary = (item: EvidenceItem) => {
                const t = (item.evidence_type || '').toLowerCase();
                const s = (item.source || '').toLowerCase();
                return t.includes('thermal') || s.includes('viirs') || s.includes('firms') || s.includes('modis');
              };
              const isContextual = (item: EvidenceItem) => {
                const t = (item.evidence_type || '').toLowerCase();
                const s = (item.source || '').toLowerCase();
                return t.includes('facility') || t.includes('historical') || s.includes('osm') || s.includes('gidc') || s.includes('fingerprint') || s.includes('baseline');
              };

              const filteredItems = allItems.filter(item => {
                if (evidenceFilter === 'SUPPORTING') return item.direction === 'SUPPORTING';
                if (evidenceFilter === 'CONFLICTING') return item.direction === 'CONFLICTING';
                if (evidenceFilter === 'MISSING') return item.direction === 'MISSING';
                return true;
              });

              const primaryGroup = filteredItems.filter(item => isPrimary(item));
              const contextualGroup = filteredItems.filter(item => isContextual(item));
              const corroboratingGroup = filteredItems.filter(item => !isPrimary(item) && !isContextual(item));

              return (
                <>
                  {/* Summary Card */}
                  <div className="bg-white border border-slate-200/90 rounded-xl p-3.5 sm:p-4 shadow-2xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                        Multi-Sensor Contribution
                      </span>
                      <span className="text-xs font-black text-emerald-700 font-mono">
                        {supportPct}% Support
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-700">
                        {supportingItems.length} Supporting {supportingItems.length === 1 ? 'Source' : 'Sources'}
                      </span>
                      <span className="text-[11px] text-slate-500 font-medium">
                        {total} Connected Feeds
                      </span>
                    </div>

                    {/* Thin Progress Bar (4-5px) */}
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all duration-300 ${
                          supportPct >= 80 ? 'bg-emerald-500' : supportPct >= 50 ? 'bg-amber-500' : 'bg-red-500'
                        }`} 
                        style={{ width: `${supportPct}%` }}
                      />
                    </div>

                    {/* Category Checklist Chips */}
                    {activeCategories.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5 pt-1">
                        {activeCategories.map((cat, idx) => (
                          <span 
                            key={idx} 
                            className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-50 border border-slate-200/80 text-slate-700"
                          >
                            <span>{cat}</span>
                            <span className="text-emerald-600 font-bold">✓</span>
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* 2. Detailed Evidence Ledger Header & Filter Tabs */}
                  <div className="space-y-2 pt-1">
                    <div className="flex items-center justify-between pb-1.5 border-b border-slate-100">
                      <div>
                        <h4 className="text-xs font-bold uppercase tracking-wide text-slate-900">
                          Detailed Evidence Ledger
                        </h4>
                        <p className="text-[10px] text-slate-500">
                          Evidence contributing to current event assessment
                        </p>
                      </div>
                      <span className="text-[10px] bg-slate-100 border border-slate-200/80 text-slate-700 px-2 py-0.5 rounded-full font-bold">
                        {total} {total === 1 ? 'Source' : 'Sources'}
                      </span>
                    </div>

                    {/* Filter Pills (All / Supporting / Conflicting / Missing) */}
                    {total > 3 && (
                      <div className="flex items-center gap-1.5 text-[10px] font-semibold overflow-x-auto pb-1">
                        <button
                          onClick={() => setEvidenceFilter('ALL')}
                          className={`px-2.5 py-1 rounded-md transition-colors ${
                            evidenceFilter === 'ALL'
                              ? 'bg-slate-900 text-white font-bold shadow-2xs'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                          }`}
                        >
                          All ({total})
                        </button>
                        <button
                          onClick={() => setEvidenceFilter('SUPPORTING')}
                          className={`px-2.5 py-1 rounded-md transition-colors ${
                            evidenceFilter === 'SUPPORTING'
                              ? 'bg-emerald-700 text-white font-bold shadow-2xs'
                              : 'bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100'
                          }`}
                        >
                          Supporting ({supportingItems.length})
                        </button>
                        {conflictingItems.length > 0 && (
                          <button
                            onClick={() => setEvidenceFilter('CONFLICTING')}
                            className={`px-2.5 py-1 rounded-md transition-colors ${
                              evidenceFilter === 'CONFLICTING'
                                ? 'bg-red-700 text-white font-bold shadow-2xs'
                                : 'bg-red-50 text-red-700 border border-red-200 hover:bg-red-100'
                            }`}
                          >
                            Conflicting ({conflictingItems.length})
                          </button>
                        )}
                        {missingItems.length > 0 && (
                          <button
                            onClick={() => setEvidenceFilter('MISSING')}
                            className={`px-2.5 py-1 rounded-md transition-colors ${
                              evidenceFilter === 'MISSING'
                                ? 'bg-slate-700 text-white font-bold shadow-2xs'
                                : 'bg-slate-100 text-slate-600 border border-slate-200 hover:bg-slate-200'
                            }`}
                          >
                            Missing ({missingItems.length})
                          </button>
                        )}
                      </div>
                    )}
                  </div>

                  {/* 3. Structured Evidence Rows by Semantic Grouping */}
                  {filteredItems.length === 0 ? (
                    <div className="p-6 text-center text-slate-400 bg-slate-50 border border-slate-200 rounded-lg text-xs italic">
                      No evidence records match the selected filter.
                    </div>
                  ) : evidenceFilter !== 'ALL' ? (
                    <div className="space-y-2.5">
                      {filteredItems.map(item => renderEvidenceCard(item))}
                    </div>
                  ) : (
                    <div className="space-y-3.5">
                      {/* Section A: Primary Evidence */}
                      {primaryGroup.length > 0 && (
                        <div className="space-y-2">
                          <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                            <Flame className="w-3 h-3 text-orange-500" />
                            <span>Primary Evidence (Thermal Passes)</span>
                          </div>
                          <div className="space-y-2">
                            {primaryGroup.map(item => renderEvidenceCard(item, true))}
                          </div>
                        </div>
                      )}

                      {/* Section B: Corroborating Evidence */}
                      {corroboratingGroup.length > 0 && (
                        <div className="space-y-2">
                          <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider pt-1 border-t border-slate-100">
                            <Layers className="w-3 h-3 text-cyan-600" />
                            <span>Corroborating Evidence (Multi-Sensor Overpasses)</span>
                          </div>
                          <div className="space-y-2">
                            {corroboratingGroup.map(item => renderEvidenceCard(item, false))}
                          </div>
                        </div>
                      )}

                      {/* Section C: Contextual & Historical Baseline */}
                      {contextualGroup.length > 0 && (
                        <div className="space-y-2">
                          <div className="flex items-center gap-1.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider pt-1 border-t border-slate-100">
                            <History className="w-3 h-3 text-blue-500" />
                            <span>Contextual & Historical Baseline</span>
                          </div>
                          <div className="space-y-2">
                            {contextualGroup.map(item => renderEvidenceCard(item, false))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </>
              );
            })()}
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
