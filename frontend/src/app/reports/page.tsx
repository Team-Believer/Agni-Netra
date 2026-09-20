'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { FileText, Download, FileJson, Search } from 'lucide-react';
import { EventItem } from '../../lib/types';
import { fetchEvents } from '../../lib/api';

export default function ReportsPage() {
  const [currentTab, setCurrentTab] = useState('reports');
  const [searchQuery, setSearchQuery] = useState('');
  const [events, setEvents] = useState<EventItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [reportData, setReportData] = useState<any>(null);
  const [selectedEventForReport, setSelectedEventForReport] = useState<string>('');

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const data = await fetchEvents();
        setEvents(data);
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
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/reports/${eventId}`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (response.ok) {
        const data = await response.json();
        setReportData(data);
        setSelectedEventForReport(eventId);
      } else {
        alert('Report generation failed');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDownloadPdf = async (eventId: string) => {
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
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />
        <main className="flex-1 p-6 overflow-y-auto max-w-[1200px] mx-auto w-full">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
              <FileText className="w-6 h-6 text-blue-600" />
              Event Reports & Exports
            </h1>
            <button
              onClick={handleDownloadCsv}
              className="flex items-center gap-2 bg-slate-800 text-white px-4 py-2 rounded-md font-medium text-sm hover:bg-slate-700 transition-colors shadow-sm"
            >
              <Download className="w-4 h-4" />
              Export All Events (CSV)
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Event List */}
            <div className="col-span-1 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col h-[600px]">
              <div className="p-4 border-b border-slate-100 bg-slate-50/50 font-semibold text-slate-700">
                Select Event for Report
              </div>
              <div className="p-3 border-b border-slate-100">
                <div className="relative">
                  <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="Search by ID or Location..."
                    className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-md text-sm outline-none focus:border-blue-500 transition-colors"
                  />
                </div>
              </div>
              <div className="flex-1 overflow-y-auto">
                {isLoading ? (
                  <div className="p-4 text-center text-sm text-slate-500">Loading...</div>
                ) : (
                  <div className="divide-y divide-slate-100">
                    {events.map(ev => (
                      <button
                        key={ev.event_id}
                        onClick={() => handleGenerateReport(ev.event_id)}
                        className={`w-full text-left p-3 hover:bg-blue-50 transition-colors ${selectedEventForReport === ev.event_id ? 'bg-blue-50' : ''}`}
                      >
                        <div className="font-semibold text-slate-800 text-sm">{ev.event_id}</div>
                        <div className="text-xs text-slate-500 truncate mt-0.5">{ev.location}</div>
                        <div className="text-xs font-medium mt-1 text-slate-600 flex justify-between">
                           <span>Priority: {ev.priority}</span>
                           <span>{new Date(ev.first_seen).toLocaleDateString()}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* JSON Viewer */}
            <div className="col-span-1 lg:col-span-2 bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden flex flex-col h-[600px]">
               <div className="p-4 border-b border-slate-100 bg-slate-50/50 font-semibold text-slate-700 flex justify-between items-center">
                 <div className="flex items-center gap-2">
                   <FileJson className="w-4 h-4 text-slate-500" />
                   Structured Report Data
                 </div>
                 {selectedEventForReport && (
                   <div className="flex items-center gap-3">
                     <span className="text-xs font-medium px-2 py-1 bg-blue-100 text-blue-700 rounded-md">
                       {selectedEventForReport}
                     </span>
                     <button
                       onClick={() => handleDownloadPdf(selectedEventForReport)}
                       className="flex items-center gap-1.5 bg-blue-600 text-white px-3 py-1.5 rounded-md font-medium text-xs hover:bg-blue-700 transition-colors shadow-sm"
                     >
                       <Download className="w-3.5 h-3.5" />
                       Download PDF
                     </button>
                   </div>
                 )}
               </div>
               <div className="flex-1 p-6 bg-slate-50 overflow-auto">
                  {reportData ? (
                    <div className="max-w-4xl mx-auto bg-white border border-slate-200 rounded-xl shadow-xs p-8">
                      {/* Report Header */}
                      <div className="border-b border-slate-200 pb-6 mb-6">
                        <div className="flex items-center justify-between mb-4">
                          <h2 className="text-2xl font-bold text-slate-900">{reportData.title}</h2>
                          <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                            reportData.ai_intelligence?.priority_level === 'Critical' ? 'bg-red-50 text-red-700' :
                            reportData.ai_intelligence?.priority_level === 'High' ? 'bg-orange-50 text-orange-700' :
                            'bg-blue-50 text-blue-700'
                          }`}>
                            {reportData.ai_intelligence?.priority_level} Priority
                          </span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <div className="text-slate-500 text-xs font-medium uppercase mb-1">Event ID</div>
                            <div className="font-semibold text-slate-900">{reportData.event_id}</div>
                          </div>
                          <div>
                            <div className="text-slate-500 text-xs font-medium uppercase mb-1">Location</div>
                            <div className="font-semibold text-slate-900">{reportData.location}</div>
                          </div>
                          <div>
                            <div className="text-slate-500 text-xs font-medium uppercase mb-1">Generated At</div>
                            <div className="font-semibold text-slate-900">{new Date(reportData.generated_at).toLocaleString()}</div>
                          </div>
                          <div>
                            <div className="text-slate-500 text-xs font-medium uppercase mb-1">Status</div>
                            <div className="font-semibold text-slate-900">{reportData.verification_status}</div>
                          </div>
                        </div>
                      </div>

                      {/* AI Intelligence Assessment */}
                      <div className="mb-8">
                        <h3 className="text-lg font-bold text-slate-800 mb-4 border-l-4 border-indigo-500 pl-3">AI Intelligence Assessment</h3>
                        <div className="bg-slate-50 rounded-lg p-5 border border-slate-100">
                          <p className="text-slate-700 text-sm mb-4">
                            <strong>Assessment:</strong> {reportData.ai_intelligence?.current_assessment || 'No assessment provided.'}
                          </p>
                          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                            <div className="bg-white p-3 rounded border border-slate-200">
                              <span className="block text-xs text-slate-500 mb-1">Hypothesis</span>
                              <span className="font-bold text-slate-900">{reportData.ai_intelligence?.source_hypothesis}</span>
                            </div>
                            <div className="bg-white p-3 rounded border border-slate-200">
                              <span className="block text-xs text-slate-500 mb-1">Confidence</span>
                              <span className="font-bold text-slate-900">{reportData.ai_intelligence?.confidence}%</span>
                            </div>
                            <div className="bg-white p-3 rounded border border-slate-200">
                              <span className="block text-xs text-slate-500 mb-1">Behavior</span>
                              <span className="font-bold text-slate-900">{reportData.ai_intelligence?.behavior}</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Explanations */}
                      <div className="mb-8">
                        <h3 className="text-lg font-bold text-slate-800 mb-4 border-l-4 border-emerald-500 pl-3">Explainability (XAI)</h3>
                        <div className="space-y-3 text-sm">
                          {reportData.explanations?.why && (
                            <div className="bg-emerald-50/50 p-4 rounded-lg border border-emerald-100">
                              <strong className="block text-emerald-800 mb-1">Why this classification?</strong>
                              <ul className="list-disc pl-5 text-emerald-700 space-y-1">
                                {Array.isArray(reportData.explanations.why) ? 
                                  reportData.explanations.why.map((r: string, i: number) => <li key={i}>{r}</li>) :
                                  <li>{reportData.explanations.why}</li>
                                }
                              </ul>
                            </div>
                          )}
                          {reportData.explanations?.why_not && (
                            <div className="bg-amber-50/50 p-4 rounded-lg border border-amber-100">
                              <strong className="block text-amber-800 mb-1">Why not something else?</strong>
                              <ul className="list-disc pl-5 text-amber-700 space-y-1">
                                {Array.isArray(reportData.explanations.why_not) ? 
                                  reportData.explanations.why_not.map((r: string, i: number) => <li key={i}>{r}</li>) :
                                  <li>{reportData.explanations.why_not}</li>
                                }
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Evidence */}
                      <div>
                        <h3 className="text-lg font-bold text-slate-800 mb-4 border-l-4 border-blue-500 pl-3">Supporting Evidence</h3>
                        {reportData.evidence && reportData.evidence.length > 0 ? (
                          <div className="overflow-hidden border border-slate-200 rounded-lg">
                            <table className="w-full text-left text-sm">
                              <thead className="bg-slate-50 border-b border-slate-200">
                                <tr>
                                  <th className="py-3 px-4 font-semibold text-slate-600">Source</th>
                                  <th className="py-3 px-4 font-semibold text-slate-600">Direction</th>
                                  <th className="py-3 px-4 font-semibold text-slate-600">Explanation</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-slate-100">
                                {reportData.evidence.map((ev: any, idx: number) => (
                                  <tr key={idx} className="bg-white">
                                    <td className="py-3 px-4 font-medium text-slate-800">{ev.source}</td>
                                    <td className="py-3 px-4">
                                      <span className={`px-2 py-1 rounded text-[10px] font-bold ${ev.direction === 'SUPPORTING' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                                        {ev.direction}
                                      </span>
                                    </td>
                                    <td className="py-3 px-4 text-slate-600">{ev.explanation}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <p className="text-sm text-slate-500">No structured evidence recorded.</p>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="h-full flex items-center justify-center text-slate-500 text-sm font-medium">
                      Select an event to view its structured report data.
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
