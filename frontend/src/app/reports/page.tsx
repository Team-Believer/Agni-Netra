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
                   <span className="text-xs font-medium px-2 py-1 bg-blue-100 text-blue-700 rounded-md">
                     {selectedEventForReport}
                   </span>
                 )}
               </div>
               <div className="flex-1 p-4 bg-slate-900 overflow-auto">
                  {reportData ? (
                    <pre className="text-green-400 text-xs font-mono whitespace-pre-wrap">
                      {JSON.stringify(reportData, null, 2)}
                    </pre>
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
