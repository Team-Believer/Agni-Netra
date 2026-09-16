'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { Settings, Database, Cpu, Activity, Server, Shield } from 'lucide-react';

interface DataSource {
  name: string;
  source_type: string;
  status: string;
  coverage: string;
  latency_ms: number;
}

interface ModelStatus {
  model_id: string;
  status: string;
  version: string;
  last_loaded: string;
  config: any;
}

export default function SettingsPage() {
  const [currentTab, setCurrentTab] = useState('settings');
  const [searchQuery, setSearchQuery] = useState('');
  const [sources, setSources] = useState<DataSource[]>([]);
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sourcesRes, modelRes] = await Promise.all([
          fetch('http://localhost:8000/api/sources'),
          fetch('http://localhost:8000/api/models/status')
        ]);
        if (sourcesRes.ok) setSources(await sourcesRes.json());
        if (modelRes.ok) setModelStatus(await modelRes.json());
      } catch (err) {
        console.error('Error fetching settings data', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />
        <main className="flex-1 p-6 overflow-y-auto max-w-[1200px] mx-auto w-full">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
              <Settings className="w-6 h-6 text-blue-600" />
              System Settings & Configuration
            </h1>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Data Sources Configuration */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center gap-2">
                <Database className="w-5 h-5 text-slate-600" />
                <h2 className="font-semibold text-slate-800">Ingestion Adapters</h2>
              </div>
              <div className="p-4">
                {isLoading ? (
                  <div className="text-sm text-slate-500">Loading sources...</div>
                ) : (
                  <div className="space-y-4">
                    {sources.map((src, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 border border-slate-100 rounded-lg hover:border-slate-200 transition-colors">
                        <div className="flex items-center gap-3">
                          <Server className={`w-5 h-5 ${src.status === 'ONLINE' ? 'text-green-500' : 'text-amber-500'}`} />
                          <div>
                            <div className="font-medium text-sm text-slate-800">{src.name}</div>
                            <div className="text-xs text-slate-500">{src.coverage} • {src.source_type}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${src.status === 'ONLINE' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'}`}>
                            {src.status}
                          </span>
                          <div className="text-xs text-slate-400 mt-1">{src.latency_ms}ms latency</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* AI Models & Environment */}
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-slate-600" />
                  <h2 className="font-semibold text-slate-800">AI Model Registry</h2>
                </div>
                <div className="p-4">
                  {isLoading ? (
                     <div className="text-sm text-slate-500">Loading model status...</div>
                  ) : modelStatus ? (
                     <div className="space-y-3">
                       <div className="flex justify-between items-center pb-2 border-b border-slate-100">
                          <span className="text-sm text-slate-500">Active Model</span>
                          <span className="text-sm font-medium text-slate-800">{modelStatus.model_id}</span>
                       </div>
                       <div className="flex justify-between items-center pb-2 border-b border-slate-100">
                          <span className="text-sm text-slate-500">Status</span>
                          <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">{modelStatus.status}</span>
                       </div>
                       <div className="flex justify-between items-center pb-2 border-b border-slate-100">
                          <span className="text-sm text-slate-500">Algorithm</span>
                          <span className="text-sm font-medium text-slate-800">XGBoost (4-Class)</span>
                       </div>
                       <div className="flex justify-between items-center">
                          <span className="text-sm text-slate-500">Features</span>
                          <span className="text-sm font-medium text-slate-800">24 Canonical Extraction</span>
                       </div>
                     </div>
                  ) : (
                    <div className="text-sm text-amber-600 font-medium bg-amber-50 p-3 rounded border border-amber-100">
                      Primary inference model disconnected.
                    </div>
                  )}
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-slate-600" />
                  <h2 className="font-semibold text-slate-800">System Information</h2>
                </div>
                <div className="p-4 space-y-3">
                   <div className="flex justify-between items-center pb-2 border-b border-slate-100">
                      <span className="text-sm text-slate-500">Database</span>
                      <span className="text-sm font-medium text-slate-800">SQLite (Local)</span>
                   </div>
                   <div className="flex justify-between items-center pb-2 border-b border-slate-100">
                      <span className="text-sm text-slate-500">Environment</span>
                      <span className="text-sm font-medium text-slate-800">Production (MVP)</span>
                   </div>
                   <div className="flex justify-between items-center">
                      <span className="text-sm text-slate-500">Security</span>
                      <span className="text-sm font-medium text-green-600 flex items-center gap-1">
                        <Shield className="w-4 h-4" /> Secure
                      </span>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
