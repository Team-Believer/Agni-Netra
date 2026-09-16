'use client';

import React, { useState } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { Globe, Shield, Cpu, Zap, Activity, Info } from 'lucide-react';

export default function AboutPage() {
  const [currentTab, setCurrentTab] = useState('about');
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 overflow-y-auto max-w-[1720px] mx-auto w-full flex flex-col">
          <div className="mb-8 flex flex-col items-center justify-center border-b border-slate-200 pb-8 pt-4">
            <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Agni-Netra</h1>
            <p className="text-xl text-slate-600 mt-3 font-medium">"The satellite sees heat. Agni-Netra understands the event."</p>
            <div className="mt-4 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-bold tracking-widest uppercase">
              SIH Problem Statement PS162
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto w-full">
            
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
              <div className="w-12 h-12 bg-orange-100 text-orange-600 rounded-xl flex items-center justify-center mb-6">
                <Globe className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 mb-3">Event-Centric Evidence Intelligence</h2>
              <p className="text-slate-600 leading-relaxed mb-4">
                Most platforms simply plot satellite "hotspots" as independent dots on a map. Agni-Netra introduces a paradigm shift: we reconstruct continuous physical events.
              </p>
              <p className="text-slate-600 leading-relaxed">
                We track the entire lifecycle of a thermal anomaly across space and time, fusing evidence from multiple orbital and ground sensors into a unified Evidence Graph.
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center mb-6">
                <Shield className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 mb-3">Real-Data Transparency First</h2>
              <p className="text-slate-600 leading-relaxed mb-4">
                We operate on a strict <strong>NO FAKE DATA</strong> policy. If a sensor (like Sentinel-2 SWIR) is occluded by clouds or not configured, Agni-Netra explicitly flags it as MISSING.
              </p>
              <p className="text-slate-600 leading-relaxed">
                By acknowledging what we <em>don't</em> know, we establish operational trust. You see exactly which sensors are online, offline, or providing conflicting evidence.
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
              <div className="w-12 h-12 bg-purple-100 text-purple-600 rounded-xl flex items-center justify-center mb-6">
                <Cpu className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 mb-3">Conformal ML & OOD Detection</h2>
              <p className="text-slate-600 leading-relaxed mb-4">
                Traditional AI forces a classification (e.g. 60% Confident). Agni-Netra uses Conformal Prediction. When uncertainty is high, the model outputs a <strong>Prediction Set</strong> rather than guessing.
              </p>
              <p className="text-slate-600 leading-relaxed">
                Our Out-of-Distribution (OOD) detection catches entirely novel thermal anomalies that the model has never seen, ensuring we don't blindly misclassify unknown threats.
              </p>
            </div>

            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
              <div className="w-12 h-12 bg-green-100 text-green-600 rounded-xl flex items-center justify-center mb-6">
                <Activity className="w-6 h-6" />
              </div>
              <h2 className="text-xl font-bold text-slate-900 mb-3">Decoupled Priority vs. Risk</h2>
              <p className="text-slate-600 leading-relaxed mb-4">
                Risk is the physical danger (FRP, exposure). Priority is the operational triage urgency.
              </p>
              <p className="text-slate-600 leading-relaxed">
                A massive routine refinery flare has a high thermal risk, but zero abnormality, resulting in a Low monitoring priority. Conversely, a small unexplained fire near a sensitive asset has high abnormality, triggering Critical priority.
              </p>
            </div>

          </div>
          
          <div className="mt-12 text-center text-slate-500 flex items-center justify-center gap-2">
            <Info className="w-4 h-4" /> Designed and engineered for production deployment.
          </div>

        </main>
      </div>
    </div>
  );
}
