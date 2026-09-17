'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../../../components/Header';
import { Sidebar } from '../../../components/Sidebar';
import { ArrowLeft, Flame, AlertTriangle, CheckCircle, XCircle, Info, ShieldAlert } from 'lucide-react';
import Link from 'next/link';
import { fetchEventDetail } from '../../../lib/api';
import type { EventDetail, EvidenceItem } from '../../../lib/types';

export default function EventDetailPage({ params }: { params: { id: string } }) {
  const [currentTab, setCurrentTab] = useState('events');
  const [searchQuery, setSearchQuery] = useState('');
  const [event, setEvent] = useState<EventDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvent = async () => {
      try {
        const data = await fetchEventDetail(params.id);
        setEvent(data);
      } catch (err) {
        setError("Failed to load event details or event not found.");
      } finally {
        setLoading(false);
      }
    };
    fetchEvent();
  }, [params.id]);

  const renderEvidenceSection = (title: string, type: string) => {
    if (!event) return null;
    const items = event.evidence.filter(e => e.evidence_type === type);
    
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-6 mb-6 shadow-xs">
        <h3 className="text-lg font-bold text-slate-800 mb-4">{title}</h3>
        {items.length === 0 ? (
          <p className="text-sm text-slate-500 italic">Evidence not available.</p>
        ) : (
          <div className="space-y-4">
            {items.map(item => (
              <div key={item.id} className="flex flex-col sm:flex-row gap-4 p-4 rounded-lg bg-slate-50 border border-slate-100">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-slate-700">{item.source} {item.sensor ? `(${item.sensor})` : ''}</span>
                    {item.direction === 'SUPPORTING' && <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-bold rounded-full">Supporting</span>}
                    {item.direction === 'CONFLICTING' && <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-bold rounded-full">Conflicting</span>}
                    {item.direction === 'MISSING' && <span className="px-2 py-0.5 bg-slate-200 text-slate-600 text-xs font-bold rounded-full">Missing</span>}
                    {item.direction === 'NEUTRAL' && <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-bold rounded-full">Neutral</span>}
                  </div>
                  <p className="text-sm font-medium text-slate-900 mb-1">{item.value}</p>
                  <p className="text-xs text-slate-500">{item.explanation}</p>
                </div>
                <div className="text-right text-xs text-slate-400">
                  <p>Quality: {item.quality != null ? (item.quality * 100).toFixed(0) : '--'}%</p>
                  <p>Relevance: {item.relevance != null ? (item.relevance * 100).toFixed(0) : '--'}%</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 overflow-y-auto max-w-[1720px] mx-auto w-full flex flex-col">
          <div className="mb-4">
            <Link href="/events" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-blue-600 transition-colors">
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Events
            </Link>
          </div>

          {loading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : error || !event ? (
            <div className="flex-1 bg-white border border-slate-200 rounded-xl p-10 flex flex-col items-center justify-center text-center shadow-xs">
              <AlertTriangle className="w-12 h-12 text-slate-300 mb-4" />
              <h3 className="text-lg font-bold text-slate-800">Event not found</h3>
              <p className="text-sm text-slate-500 mt-2 max-w-md">{error}</p>
            </div>
          ) : (
            <>
              {/* Header Section */}
              <div className="bg-white border border-slate-200 rounded-xl p-6 mb-6 shadow-xs flex flex-wrap justify-between items-start gap-4">
                <div>
                  <h1 className="text-2xl font-bold text-slate-900 mb-1">{event.title}</h1>
                  <p className="text-sm text-slate-500 flex items-center gap-2">
                    <span>{event.event_id}</span> • <span>{event.location}</span>
                  </p>
                </div>
                <div className="flex gap-3">
                  <div className="text-center px-4 py-2 bg-slate-50 rounded-lg border border-slate-100">
                    <p className="text-xs text-slate-500 mb-0.5">Priority</p>
                    <p className="font-bold text-slate-900">{event.priority}</p>
                  </div>
                  <div className="text-center px-4 py-2 bg-slate-50 rounded-lg border border-slate-100">
                    <p className="text-xs text-slate-500 mb-0.5">Risk Index</p>
                    <p className="font-bold text-slate-900">{event.risk_index}/100</p>
                  </div>
                  <div className="text-center px-4 py-2 bg-slate-50 rounded-lg border border-slate-100">
                    <p className="text-xs text-slate-500 mb-0.5">Status</p>
                    <p className="font-bold text-slate-900">{event.status}</p>
                  </div>
                </div>
              </div>

              {/* Explainability Section */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
                  <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600"/> WHY</h3>
                  <ul className="space-y-2">
                    {(event.explanations?.why || []).map((reason, i) => (
                      <li key={i} className="text-sm text-slate-600">• {reason}</li>
                    ))}
                    {(!event.explanations?.why || event.explanations.why.length === 0) && <li className="text-sm text-slate-400 italic">No supporting reasons available</li>}
                  </ul>
                </div>
                <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
                  <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2"><XCircle className="w-4 h-4 text-red-600"/> WHY NOT</h3>
                  <ul className="space-y-2">
                    {(event.explanations?.why_not || []).map((reason, i) => (
                      <li key={i} className="text-sm text-slate-600">• {reason}</li>
                    ))}
                    {(!event.explanations?.why_not || event.explanations.why_not.length === 0) && <li className="text-sm text-slate-400 italic">No contradicting reasons available</li>}
                  </ul>
                </div>
                <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
                  <h3 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2"><Info className="w-4 h-4 text-blue-600"/> WHAT CHANGED</h3>
                  <ul className="space-y-2">
                    {(event.explanations?.what_changed || []).map((change, i) => (
                      <li key={i} className="text-sm text-slate-600">• {change}</li>
                    ))}
                    {(!event.explanations?.what_changed || event.explanations.what_changed.length === 0) && <li className="text-sm text-slate-400 italic">No dynamic changes detected</li>}
                  </ul>
                </div>
              </div>

              {/* Conformal Uncertainty & Prediction Section */}
              {event.predictions && event.predictions.length > 0 && (
                <div className="bg-blue-50 border border-blue-100 rounded-xl p-6 mb-6 shadow-xs">
                  <div className="flex items-center gap-2 mb-4">
                    <ShieldAlert className="w-5 h-5 text-blue-600" />
                    <h3 className="text-lg font-bold text-slate-800">Model Prediction & Uncertainty</h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Primary Classification</p>
                      <p className="font-semibold text-slate-900">{event.predictions[0].predicted_class}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Confidence</p>
                      <p className="font-semibold text-slate-900">{event.predictions[0].confidence != null ? (event.predictions[0].confidence * 100).toFixed(1) : '--'}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-1">Prediction Set (Conformal)</p>
                      <div className="flex flex-wrap gap-1">
                        {(event.predictions[0].prediction_set || []).map((cls, i) => (
                          <span key={i} className="px-2 py-0.5 bg-white border border-slate-200 rounded text-xs text-slate-700">{cls}</span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-slate-500 mb-1">OOD Status</p>
                      <p className="font-semibold text-slate-900">
                        {event.predictions[0].ood_status ? (
                          <span className="text-red-600">Out of Distribution</span>
                        ) : (
                          <span className="text-green-600">Within Domain</span>
                        )}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Evidence Multi-Sensor Graph */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <div>
                  {renderEvidenceSection('Thermal Evidence (Primary)', 'Thermal')}
                  {renderEvidenceSection('Geostationary Temporal Evidence', 'Temporal')}
                  {renderEvidenceSection('Optical / SWIR Corroboration', 'Optical')}
                </div>
                <div>
                  {renderEvidenceSection('SAR / Structural Context', 'SAR')}
                  {renderEvidenceSection('Atmospheric / Weather Plume', 'Weather')}
                  {renderEvidenceSection('Facility Infrastructure Context', 'Facility')}
                  {renderEvidenceSection('Historical Fingerprint', 'Historical')}
                </div>
              </div>

            </>
          )}
        </main>
      </div>
    </div>
  );
}
