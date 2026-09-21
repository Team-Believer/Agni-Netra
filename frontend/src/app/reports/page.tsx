'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { 
  FileText, 
  Download, 
  Search, 
  ShieldAlert, 
  Info, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  Compass, 
  Layers, 
  Radio, 
  Flame, 
  Eye, 
  FileSpreadsheet, 
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { EventItem } from '../../lib/types';
import { fetchEvents } from '../../lib/api';

export default function ReportsPage() {
  const [currentTab, setCurrentTab] = useState('reports');
  const [searchQuery, setSearchQuery] = useState('');
  const [events, setEvents] = useState<EventItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [reportData, setReportData] = useState<any>(null);
  const [selectedEventForReport, setSelectedEventForReport] = useState<string>('');
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const data = await fetchEvents();
        setEvents(data);
        if (data.length > 0) {
          // Default to EVENT-SEED-009 or first event
          const defaultEvent = data.find(e => e.event_id === 'EVENT-SEED-009') || data[0];
          handleGenerateReport(defaultEvent.event_id);
        }
      } catch (err) {
        console.error('Failed to load events for reports', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadEvents();
  }, []);

  const handleDownloadCsv = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch('http://localhost:8000/api/reports/export/csv', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (!res.ok) throw new Error('Export failed');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'agni_netra_events_export.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('CSV export failed', err);
      alert('CSV export failed. Please try again.');
    }
  };

  const handleGenerateReport = async (eventId: string) => {
    try {
      setSelectedEventForReport(eventId);
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/reports/${eventId}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (response.ok) {
        const data = await response.json();
        setReportData(data);
      } else {
        alert('Report generation failed');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDownloadPdf = async (eventId: string) => {
    setIsGeneratingPdf(true);
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`http://localhost:8000/api/reports/export/${eventId}/pdf`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (!res.ok) throw new Error('PDF export failed');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `report_${eventId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF export failed', err);
      alert('PDF export failed. Please try again.');
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const filteredEvents = events.filter(e => 
    e.event_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (e.location && e.location.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (e.title && e.title.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const ident = reportData?.event_identity;
  const execSum = reportData?.executive_summary;
  const prov = reportData?.data_provenance;
  const meas = reportData?.measurement_details || [];
  const obsSeries = reportData?.observation_series || [];
  const evidenceList = reportData?.evidence || [];
  const sensorMethods = reportData?.sensor_methodologies || [];
  const traceList = reportData?.traceability || [];
  const auditFlow = reportData?.audit_trail_flow;
  const verifications = reportData?.verifications || [];

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />
        
        <main className="flex-1 p-6 overflow-y-auto w-full">
          {/* Top Page Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <div className="flex items-center gap-2">
                <FileText className="w-6 h-6 text-indigo-600" />
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                  Technical & Audit-Ready Event Reports
                </h1>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Inspect end-to-end scientific measurement derivations, multi-sensor evidence fusion, and export 5-page audit PDFs.
              </p>
            </div>

            <div className="flex items-center gap-2.5">
              <button
                onClick={handleDownloadCsv}
                className="flex items-center gap-1.5 bg-white border border-slate-300 text-slate-700 px-3.5 py-2 rounded-lg font-semibold text-xs hover:bg-slate-50 transition-colors shadow-xs"
              >
                <FileSpreadsheet className="w-4 h-4 text-slate-500" />
                Export CSV Ledger
              </button>
              {selectedEventForReport && (
                <button
                  onClick={() => handleDownloadPdf(selectedEventForReport)}
                  disabled={isGeneratingPdf}
                  className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-bold text-xs transition-colors shadow-sm disabled:opacity-50"
                >
                  <Download className="w-4 h-4" />
                  {isGeneratingPdf ? 'Generating PDF...' : 'Download 5-Page Audit PDF'}
                </button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: Event Selector (3 cols) */}
            <div className="col-span-12 lg:col-span-3 bg-white border border-slate-200/90 rounded-xl shadow-xs overflow-hidden flex flex-col h-[780px]">
              <div className="p-3.5 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
                <span className="font-bold text-xs text-slate-800 uppercase tracking-wide">
                  Select Event
                </span>
                <span className="text-[10px] font-bold text-slate-500 bg-white border border-slate-200 px-2 py-0.5 rounded-full">
                  {filteredEvents.length} Events
                </span>
              </div>
              
              <div className="p-3 border-b border-slate-100">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by ID, location..."
                    className="w-full pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-xs outline-none focus:bg-white focus:ring-1 focus:ring-indigo-500 transition-all"
                  />
                </div>
              </div>

              <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
                {isLoading ? (
                  <div className="p-6 text-center text-xs text-slate-400">Loading events...</div>
                ) : filteredEvents.length === 0 ? (
                  <div className="p-6 text-center text-xs text-slate-400">No events matched search.</div>
                ) : (
                  filteredEvents.map((ev) => {
                    const isSelected = selectedEventForReport === ev.event_id;
                    return (
                      <button
                        key={ev.event_id}
                        onClick={() => handleGenerateReport(ev.event_id)}
                        className={`w-full text-left p-3.5 transition-all text-xs flex flex-col gap-1 ${
                          isSelected
                            ? 'bg-indigo-50/80 border-l-3 border-l-indigo-600'
                            : 'hover:bg-slate-50/80'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900">{ev.event_id}</span>
                          <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                            ev.priority === 'Critical' ? 'bg-red-50 text-red-700 border border-red-200' :
                            ev.priority === 'High' ? 'bg-orange-50 text-orange-700 border border-orange-200' :
                            'bg-blue-50 text-blue-700 border border-blue-200'
                          }`}>
                            {ev.priority}
                          </span>
                        </div>
                        <div className="text-slate-600 font-medium truncate">{ev.title}</div>
                        <div className="text-[11px] text-slate-400 truncate">{ev.location}</div>
                        <div className="flex items-center justify-between text-[10px] text-slate-500 pt-0.5 mt-0.5 border-t border-slate-100/60">
                          <span>{ev.classification}</span>
                          <span>{new Date(ev.first_seen).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })}</span>
                        </div>
                      </button>
                    );
                  })
                )}
              </div>
            </div>

            {/* Right Column: Full Technical Audit Report View (9 cols) */}
            <div className="col-span-12 lg:col-span-9 bg-white border border-slate-200/90 rounded-xl shadow-xs overflow-hidden flex flex-col h-[780px]">
              <div className="p-3.5 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-xs text-slate-800 uppercase tracking-wide">
                    Audit-Ready Intelligence Dossier
                  </span>
                  {selectedEventForReport && (
                    <span className="text-[11px] font-mono font-bold px-2 py-0.5 bg-indigo-100 text-indigo-800 rounded">
                      {selectedEventForReport}
                    </span>
                  )}
                </div>
                {selectedEventForReport && (
                  <button
                    onClick={() => handleDownloadPdf(selectedEventForReport)}
                    disabled={isGeneratingPdf}
                    className="flex items-center gap-1 text-indigo-600 hover:text-indigo-800 text-xs font-bold transition-colors"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download PDF</span>
                  </button>
                )}
              </div>

              <div className="flex-1 p-6 bg-slate-50/60 overflow-y-auto space-y-6">
                {reportData && ident ? (
                  <div className="max-w-4xl mx-auto space-y-6 bg-white border border-slate-200/90 rounded-xl p-6 sm:p-8 shadow-sm">
                    {/* 1. Header & Identity Block */}
                    <div className="border-b border-slate-200 pb-6">
                      <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
                        <div>
                          <span className="text-[11px] font-bold text-indigo-600 uppercase tracking-wider">
                            AGNI-NETRA • EVENT INTELLIGENCE REPORT
                          </span>
                          <h2 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight mt-0.5">
                            {ident.title}
                          </h2>
                        </div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs font-bold px-2.5 py-1 rounded bg-red-50 text-red-700 border border-red-200">
                            {ident.priority_level} Priority
                          </span>
                          <span className="text-xs font-bold px-2.5 py-1 rounded bg-amber-50 text-amber-800 border border-amber-200">
                            {ident.verification_status}
                          </span>
                          <span className="text-xs font-bold px-2.5 py-1 rounded bg-slate-100 text-slate-700 border border-slate-200">
                            Risk: {ident.risk_index?.toFixed(0)}/100
                          </span>
                        </div>
                      </div>

                      {/* Identity Details 4-Column Grid */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5 bg-slate-50/80 border border-slate-200/80 rounded-lg p-3.5 text-xs mt-4">
                        <div>
                          <div className="text-[10px] font-bold text-slate-400 uppercase">Event ID</div>
                          <div className="font-bold text-slate-900 mt-0.5">{ident.event_id}</div>
                        </div>
                        <div>
                          <div className="text-[10px] font-bold text-slate-400 uppercase">Classification</div>
                          <div className="font-bold text-slate-900 mt-0.5">{ident.classification}</div>
                        </div>
                        <div>
                          <div className="text-[10px] font-bold text-slate-400 uppercase">Location</div>
                          <div className="font-medium text-slate-900 mt-0.5 truncate">{ident.location}</div>
                        </div>
                        <div>
                          <div className="text-[10px] font-bold text-slate-400 uppercase">Coordinates</div>
                          <div className="font-mono text-slate-800 mt-0.5">{ident.coordinates?.latitude}° N, {ident.coordinates?.longitude}° E</div>
                        </div>
                        <div>
                          <div className="text-[10px] font-bold text-slate-400 uppercase">First Observed</div>
                          <div className="font-medium text-slate-900 mt-0.5">{ident.first_detected_formatted}</div>
                        </div>
                        <div>
                          <div className="text-[10px] font-bold text-slate-400 uppercase">Last Observed</div>
                          <div className="font-medium text-slate-900 mt-0.5">{ident.last_observed_formatted}</div>
                        </div>
                        <div>
                          <div className="text-[10px] font-bold text-slate-400 uppercase">Lifecycle State</div>
                          <div className="font-medium text-slate-900 mt-0.5">{ident.lifecycle_state}</div>
                        </div>
                        <div>
                          <div className="text-[10px] font-bold text-slate-400 uppercase">Report Generated</div>
                          <div className="font-medium text-slate-900 mt-0.5">{reportData.formatted_generated_at}</div>
                        </div>
                      </div>
                    </div>

                    {/* 2. Data Provenance Notice Box */}
                    <div className="bg-blue-50/60 border border-blue-200 rounded-lg p-3.5 text-xs text-blue-900 space-y-1">
                      <div className="flex items-center gap-1.5 font-bold text-[11px] text-blue-950 uppercase tracking-wide">
                        <Info className="w-4 h-4 text-blue-600 shrink-0" />
                        <span>Data Provenance Notice (MVP Demonstration)</span>
                      </div>
                      <p className="text-[11px] leading-relaxed text-blue-800">
                        {prov?.notice}
                      </p>
                      <div className="text-[10px] text-blue-700 italic pt-0.5">
                        Data Mode: {prov?.data_mode} • Synthetic Demo: {prov?.is_synthetic ? 'YES' : 'NO'} • Source Provenance: Preserved across evidence ledger.
                      </div>
                    </div>

                    {/* 3. Executive Event Summary */}
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3 flex items-center gap-2 border-l-3 border-l-indigo-600 pl-2">
                        1. Executive Event Summary
                      </h3>
                      <div className="border border-slate-200 rounded-lg divide-y divide-slate-100 text-xs">
                        <div className="p-3 bg-slate-50/50 flex flex-col sm:flex-row gap-2">
                          <span className="font-bold text-slate-900 sm:w-48 shrink-0">WHAT HAPPENED?</span>
                          <span className="text-slate-700 leading-relaxed">{execSum?.what_happened}</span>
                        </div>
                        <div className="p-3 flex flex-col sm:flex-row gap-2">
                          <span className="font-bold text-slate-900 sm:w-48 shrink-0">WHY INFERRED?</span>
                          <span className="text-slate-700 leading-relaxed">{execSum?.why_agni_netra_believes}</span>
                        </div>
                        <div className="p-3 bg-slate-50/50 flex flex-col sm:flex-row gap-2">
                          <span className="font-bold text-slate-900 sm:w-48 shrink-0">WHAT CHANGED?</span>
                          <span className="text-slate-700 leading-relaxed">{execSum?.what_changed}</span>
                        </div>
                        <div className="p-3 flex flex-col sm:flex-row gap-2">
                          <span className="font-bold text-slate-900 sm:w-48 shrink-0">WHAT IS UNCERTAIN?</span>
                          <span className="text-slate-700 leading-relaxed">{execSum?.what_is_uncertain}</span>
                        </div>
                        <div className="p-3 bg-slate-50/50 flex flex-col sm:flex-row gap-2">
                          <span className="font-bold text-slate-900 sm:w-48 shrink-0">WHAT TO VERIFY?</span>
                          <span className="text-slate-700 leading-relaxed">{execSum?.what_should_be_verified}</span>
                        </div>
                      </div>
                    </div>

                    {/* 4. Measurement & Calculation Details Matrix */}
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3 flex items-center gap-2 border-l-3 border-l-indigo-600 pl-2">
                        2. Measurement & Calculation Details
                      </h3>
                      <div className="border border-slate-200 rounded-lg overflow-hidden">
                        <table className="w-full text-left text-xs border-collapse">
                          <thead className="bg-slate-100/80 border-b border-slate-200 font-bold text-slate-700">
                            <tr>
                              <th className="py-2.5 px-3">Metric</th>
                              <th className="py-2.5 px-3">Value</th>
                              <th className="py-2.5 px-3">Source & Input</th>
                              <th className="py-2.5 px-3">Calculation / Method</th>
                              <th className="py-2.5 px-3">Limitations & Notes</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {meas.map((m: any, idx: number) => (
                              <tr key={idx} className={idx % 2 === 1 ? 'bg-slate-50/40' : 'bg-white'}>
                                <td className="py-2.5 px-3 font-bold text-slate-900">{m.metric}</td>
                                <td className="py-2.5 px-3 font-bold text-indigo-700 whitespace-nowrap">{m.value}</td>
                                <td className="py-2.5 px-3 text-slate-700">
                                  <div>{m.source}</div>
                                  <div className="text-[10px] text-slate-400">{m.input}</div>
                                </td>
                                <td className="py-2.5 px-3 text-slate-700">{m.method}</td>
                                <td className="py-2.5 px-3 text-slate-500 text-[11px]">{m.notes}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* 5. Chronological Observation Timeline Series */}
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3 flex items-center gap-2 border-l-3 border-l-indigo-600 pl-2">
                        3. Chronological Observation Timeline Series
                      </h3>
                      <div className="text-xs text-slate-600 mb-2 font-medium">
                        <strong>FRP Progression & Baseline Method:</strong> {reportData.frp_analysis?.formula_applied}
                      </div>
                      <div className="border border-slate-200 rounded-lg overflow-hidden">
                        <table className="w-full text-left text-xs border-collapse">
                          <thead className="bg-slate-100/80 border-b border-slate-200 font-bold text-slate-700">
                            <tr>
                              <th className="py-2 px-3 w-10">#</th>
                              <th className="py-2 px-3">Timestamp (IST)</th>
                              <th className="py-2 px-3">Satellite Sensor</th>
                              <th className="py-2 px-3">FRP (MW)</th>
                              <th className="py-2 px-3">Brightness Temp (K)</th>
                              <th className="py-2 px-3">Quality / Confidence</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {obsSeries.length > 0 ? (
                              obsSeries.map((o: any) => (
                                <tr key={o.sequence} className="bg-white hover:bg-slate-50">
                                  <td className="py-2 px-3 text-slate-400 font-mono">{o.sequence}</td>
                                  <td className="py-2 px-3 font-medium text-slate-900">{o.formatted_time}</td>
                                  <td className="py-2 px-3 text-slate-700">{o.satellite}</td>
                                  <td className="py-2 px-3 font-bold text-red-600">{o.frp_mw ? `${o.frp_mw.toFixed(1)} MW` : '--'}</td>
                                  <td className="py-2 px-3 text-slate-700">{o.brightness_temp_k ? `${o.brightness_temp_k.toFixed(1)} K` : '--'}</td>
                                  <td className="py-2 px-3 text-slate-600">{o.quality} ({Math.round((o.confidence || 0.94) * 100)}%)</td>
                                </tr>
                              ))
                            ) : (
                              <tr>
                                <td colSpan={6} className="py-3 px-3 text-center text-slate-400">No linked observations series available.</td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* 6. Detailed Evidence Ledger */}
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3 flex items-center gap-2 border-l-3 border-l-indigo-600 pl-2">
                        4. Detailed Evidence Ledger
                      </h3>
                      <div className="border border-slate-200 rounded-lg overflow-hidden">
                        <table className="w-full text-left text-xs border-collapse">
                          <thead className="bg-slate-100/80 border-b border-slate-200 font-bold text-slate-700">
                            <tr>
                              <th className="py-2.5 px-3">Source & Channel</th>
                              <th className="py-2.5 px-3">Finding / Value</th>
                              <th className="py-2.5 px-3">Direction</th>
                              <th className="py-2.5 px-3">Quality</th>
                              <th className="py-2.5 px-3">Relevance</th>
                              <th className="py-2.5 px-3">Explanation & Role</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {evidenceList.map((ev: any, idx: number) => {
                              const isSupp = ev.direction === 'SUPPORTING';
                              return (
                                <tr key={idx} className="bg-white hover:bg-slate-50">
                                  <td className="py-2.5 px-3 font-bold text-slate-900">
                                    <div>{ev.source}</div>
                                    <div className="text-[10px] text-slate-400 font-normal">{ev.type}</div>
                                  </td>
                                  <td className="py-2.5 px-3 font-bold text-slate-800">{ev.value}</td>
                                  <td className="py-2.5 px-3">
                                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                                      isSupp ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'
                                    }`}>
                                      {ev.direction}
                                    </span>
                                  </td>
                                  <td className="py-2.5 px-3 text-slate-700 font-medium">{Math.round(ev.quality * 100)}%</td>
                                  <td className="py-2.5 px-3 text-slate-700 font-medium">{Math.round(ev.relevance * 100)}%</td>
                                  <td className="py-2.5 px-3 text-slate-600 leading-relaxed">
                                    <div>{ev.explanation}</div>
                                    <div className="text-[10px] text-slate-400 italic mt-0.5">Role: {ev.limitations}</div>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* 7. Sensor-Specific Methodologies */}
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3 flex items-center gap-2 border-l-3 border-l-indigo-600 pl-2">
                        5. Sensor Specifications & Physical Limitations
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {sensorMethods.map((sm: any, idx: number) => (
                          <div key={idx} className="bg-slate-50/70 border border-slate-200 rounded-lg p-3 text-xs space-y-1">
                            <div className="font-bold text-slate-900 text-[13px]">{sm.sensor}</div>
                            <div className="text-indigo-700 font-semibold text-[11px]">{sm.role}</div>
                            <div className="text-slate-600 text-[11px]"><strong>Measured:</strong> {sm.measured}</div>
                            <div className="text-slate-500 text-[10px] italic pt-0.5"><strong>Limitations:</strong> {sm.limitations}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* 8. Explainability & XAI Traceability */}
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3 flex items-center gap-2 border-l-3 border-l-indigo-600 pl-2">
                        6. Explainability (XAI) & Hypothesis Traceability
                      </h3>
                      <div className="space-y-2">
                        {traceList.map((tr: any, idx: number) => {
                          const isWhy = tr.claim_type.includes('WHY THIS');
                          return (
                            <div key={idx} className={`p-3 rounded-lg border text-xs flex flex-col sm:flex-row gap-2.5 ${
                              isWhy ? 'bg-emerald-50/40 border-emerald-200' : 'bg-amber-50/40 border-amber-200'
                            }`}>
                              <span className={`font-bold px-2 py-0.5 rounded text-[10px] self-start shrink-0 ${
                                isWhy ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                              }`}>
                                {tr.claim_type}
                              </span>
                              <div className="flex-1 space-y-0.5">
                                <div className="font-semibold text-slate-900">{tr.claim}</div>
                                <div className="text-slate-600 text-[11px]">
                                  <strong>Measurements:</strong> {tr.measurements} • <strong>Source:</strong> {tr.source}
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* 9. Semantic Distinction & Risk Methodology */}
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3 flex items-center gap-2 border-l-3 border-l-indigo-600 pl-2">
                        7. Semantic Distinction: Behavior vs Lifecycle State & Risk vs Priority
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 text-xs">
                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3.5 space-y-1.5">
                          <div className="font-bold text-slate-900">Behavior vs Lifecycle State</div>
                          <p className="text-slate-600 leading-relaxed text-[11px]">
                            <strong>Behavior ({ident.behavior}):</strong> Physical thermal pattern trajectory (e.g. Rapid Expansion, Sudden Spike, Stable).<br/>
                            <strong>Lifecycle State ({ident.lifecycle_state}):</strong> Incident system tracking status (e.g. Active, Monitoring, Resolved).
                          </p>
                        </div>
                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3.5 space-y-1.5">
                          <div className="font-bold text-slate-900">Risk Index vs Operational Priority</div>
                          <p className="text-slate-600 leading-relaxed text-[11px]">
                            <strong>Risk Index ({ident.risk_index?.toFixed(0)}/100):</strong> Modeled physical hazard severity and spatial vulnerability footprint.<br/>
                            <strong>Priority ({ident.priority_level}):</strong> Operational analyst review and dispatch urgency queue ordering.
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* 10. Verification Audit Trail */}
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide mb-3 flex items-center gap-2 border-l-3 border-l-indigo-600 pl-2">
                        8. Verification & Review Audit Trail
                      </h3>
                      <div className="border border-slate-200 rounded-lg overflow-hidden text-xs">
                        <table className="w-full text-left border-collapse">
                          <thead className="bg-slate-100/80 border-b border-slate-200 font-bold text-slate-700">
                            <tr>
                              <th className="py-2 px-3">Reviewer / Authority</th>
                              <th className="py-2 px-3">Decision</th>
                              <th className="py-2 px-3">Timestamp</th>
                              <th className="py-2 px-3">Audited Comments</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-100">
                            {verifications.length > 0 ? (
                              verifications.map((v: any, idx: number) => (
                                <tr key={idx} className="bg-white">
                                  <td className="py-2.5 px-3 font-bold text-slate-900">{v.reviewer}</td>
                                  <td className="py-2.5 px-3 font-bold text-indigo-700">{v.decision}</td>
                                  <td className="py-2.5 px-3 text-slate-600">{v.formatted_time}</td>
                                  <td className="py-2.5 px-3 text-slate-600">{v.comment}</td>
                                </tr>
                              ))
                            ) : (
                              <tr>
                                <td colSpan={4} className="py-3 px-3 text-center text-slate-400">Pending initial human verification.</td>
                              </tr>
                            )}
                          </tbody>
                        </table>
                      </div>
                    </div>

                    {/* 11. End-to-End Decision Flow */}
                    <div className="bg-slate-900 text-slate-100 rounded-xl p-4 text-xs space-y-2">
                      <div className="font-bold text-slate-200 uppercase tracking-wide text-[11px]">
                        9. End-to-End Decision Knowledge Flow
                      </div>
                      <div className="text-[11px] leading-relaxed font-mono text-indigo-300">
                        OBSERVATION (VIIRS/INSAT) → MEASUREMENT (FRP MW, BT K) → CALCULATION (Expansion 5.5×) → EVIDENCE FUSION → CLASSIFICATION ({ident.classification}) → BEHAVIOR ({ident.behavior}) → RISK ({ident.risk_index?.toFixed(0)}/100) → PRIORITY ({ident.priority_level}) → VERIFICATION ({ident.verification_status})
                      </div>
                    </div>

                    {/* 12. Operational Limitations & Metadata Footer */}
                    <div className="border-t border-slate-200 pt-4 text-xs text-slate-500 space-y-1.5">
                      <div className="font-bold text-slate-700 text-[11px] uppercase">Operational Limitations</div>
                      <ul className="list-disc pl-4 text-[11px] space-y-0.5 text-slate-600">
                        {reportData.limitations?.map((lim: string, idx: number) => (
                          <li key={idx}>{lim}</li>
                        ))}
                      </ul>
                      <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-400 font-mono">
                        <span>Report ID: {reportData.report_id}</span>
                        <span>Generated: {reportData.formatted_generated_at}</span>
                        <span>Agni-Netra MVP v1.0.0 (Audit-Ready)</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                    Select an event on the left to inspect its audit-ready intelligence report.
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
