'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { api } from '../../lib/api';
import type { DataSourceItem } from '../../lib/types';
import { Activity, Server, AlertCircle, CheckCircle, Clock } from 'lucide-react';

export default function SourcesPage() {
  const [currentTab, setCurrentTab] = useState('sources');
  const [searchQuery, setSearchQuery] = useState('');
  const [sources, setSources] = useState<DataSourceItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSources = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/sources`);
        const data = await response.json();
        setSources(data);
      } catch (err) {
        console.error("Failed to load sources", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSources();
  }, []);

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 overflow-y-auto max-w-[1720px] mx-auto w-full flex flex-col">
          <div className="mb-6 flex items-center justify-between border-b border-slate-200 pb-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900">Source Health</h1>
              <p className="text-sm text-slate-500 mt-1">Monitor satellite and sensor data ingestion status</p>
            </div>
            <div className="flex gap-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 text-green-700 border border-green-200 rounded-lg text-sm font-semibold">
                <CheckCircle className="w-4 h-4" /> {sources.filter(s => s.status === 'ONLINE').length} Online
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-red-50 text-red-700 border border-red-200 rounded-lg text-sm font-semibold">
                <AlertCircle className="w-4 h-4" /> {sources.filter(s => s.status === 'OFFLINE' || s.status === 'ERROR').length} Offline
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 text-slate-700 border border-slate-200 rounded-lg text-sm font-semibold">
                <Server className="w-4 h-4" /> {sources.filter(s => s.status === 'NOT CONFIGURED').length} Not Configured
              </div>
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {sources.map(source => (
                <div key={source.name} className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex flex-col">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-bold text-slate-900">{source.name}</h3>
                      <p className="text-xs text-slate-500 font-mono mt-1">{source.source_type}</p>
                    </div>
                    {source.status === 'ONLINE' && <span className="px-2 py-1 bg-green-100 text-green-700 text-[10px] font-bold rounded uppercase tracking-wider flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Online</span>}
                    {source.status === 'OFFLINE' && <span className="px-2 py-1 bg-red-100 text-red-700 text-[10px] font-bold rounded uppercase tracking-wider flex items-center gap-1"><AlertCircle className="w-3 h-3"/> Offline</span>}
                    {source.status === 'ERROR' && <span className="px-2 py-1 bg-red-100 text-red-700 text-[10px] font-bold rounded uppercase tracking-wider flex items-center gap-1"><AlertCircle className="w-3 h-3"/> Error</span>}
                    {source.status === 'NOT CONFIGURED' && <span className="px-2 py-1 bg-slate-100 text-slate-600 text-[10px] font-bold rounded uppercase tracking-wider flex items-center gap-1"><Server className="w-3 h-3"/> Not Configured</span>}
                    {source.status.includes('OFFLINE CACHE') && <span className="px-2 py-1 bg-blue-100 text-blue-700 text-[10px] font-bold rounded uppercase tracking-wider flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Cache</span>}
                  </div>
                  
                  <div className="space-y-3 flex-1">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-500">Coverage</span>
                      <span className="font-medium text-slate-800">{source.coverage}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-500">Latency</span>
                      <span className="font-medium text-slate-800">{source.latency_ms ? `${source.latency_ms} ms` : 'N/A'}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-500">Errors</span>
                      <span className="font-medium text-slate-800">{source.errors || 0}</span>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-500">Records Ingested</span>
                      <span className="font-medium text-slate-800">{source.record_count.toLocaleString()}</span>
                    </div>
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-slate-100">
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <Clock className="w-3.5 h-3.5" />
                      <span>Last fetch: {source.last_fetch ? new Date(source.last_fetch).toLocaleString() : 'Never'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
