'use client';

import React, { useState } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import {
  Globe, Shield, Cpu, Zap, Activity, Info, Search, Eye, Target, Users,
  Satellite, Radio, Layers, Wind, MapPin, BarChart3, Brain, CheckCircle2,
  AlertTriangle, ArrowRight, Flame, TrendingUp, ShieldCheck, FileSearch,
  Gauge, Bell, HelpCircle, Lock, Lightbulb, CircleDot, ArrowDown
} from 'lucide-react';

/* ─────────────── DATA ─────────────── */

const pillars = [
  { icon: Satellite, label: 'Detect', desc: 'Multi-source thermal observations' },
  { icon: Search, label: 'Understand', desc: 'AI + contextual analysis' },
  { icon: Target, label: 'Prioritize', desc: 'Risk & impact assessment' },
  { icon: Users, label: 'Enable Action', desc: 'Human verification & alerts' },
];

const technicalEnablers = [
  { name: 'VIIRS Nightfire', desc: 'High-T thermal physics → Multispectral Planck fitting for hot persistent sources and flare characterization.' },
  { name: 'INSAT-3DS', desc: 'High-cadence GEO monitoring → 4 km / 15–30 min Indian thermal observations (ISRO/SAC validation).' },
  { name: 'Sentinel-2 SWIR', desc: 'Fine spatial refinement → 20 m optical/SWIR context for facility-level thermal segmentation and corroboration.' },
  { name: 'TROPOMI', desc: 'Atmospheric corroboration → NO₂/SO₂/CO evidence to support or challenge thermal-event hypotheses.' },
  { name: 'NiSAR / Sentinel-1', desc: 'Structural context → SAR-based infrastructure/surface-change evidence (context layer).' },
  { name: 'AlphaEarth', desc: 'Facility fingerprint + novelty → 10 m, 64-dimensional contextual embeddings for structural/change and OOD signals.' },
  { name: 'CAAQMS', desc: 'Ground air-quality context → 15–60 minute cross-checks from ~300 sites (proposed/pilot, not standalone proof).' },
];

const workflowSteps = [
  'Satellite / Sensor Data',
  'Thermal Observation',
  'Event Reconstruction',
  'Source Attribution',
  'Historical Behavior',
  'Abnormality Detection',
  'Multi-Sensor Evidence Fusion',
  'Uncertainty / OOD',
  'Risk Assessment',
  'Priority',
  'Human Verification',
  'Action & Monitoring',
];

const whyDifferent = [
  { capability: 'Persistent Event Intelligence', matter: 'Converts fragmented observations into one evolving event.' },
  { capability: 'Dual Thermal Intelligence', matter: 'Detects both high-T flares and lower-T persistent industrial heat.' },
  { capability: 'Evidence Fusion + Conflict Handling', matter: 'Combines independent sensors without forcing conflicting evidence into one answer.' },
  { capability: 'Historical Fingerprint + Change Detection', matter: 'Determines whether current behavior is normal or abnormal for that location.' },
  { capability: 'Uncertainty + OOD + Abstention', matter: 'Can return Unknown / Insufficient Evidence instead of forcing a wrong class.' },
  { capability: 'Risk → Priority → Verification', matter: 'Converts detection into an actionable, human-verifiable operational decision.' },
];

const existingGaps = [
  { title: 'Thermal anomaly ≠ source', desc: 'Same thermal signature can represent fire, flare, biomass or other heat.' },
  { title: 'Observations ≠ physical event', desc: 'Multiple detections may belong to one evolving incident.' },
  { title: 'Coarse spatial resolution', desc: 'Thermal pixels may not identify the exact facility/unit involved.' },
  { title: 'Revisit & verification latency', desc: 'Different sensors have different revisit times and data latency.' },
  { title: 'High-T bias', desc: 'Flare-focused methods can miss lower-temperature industrial heat.' },
  { title: 'No adaptive normality / uncertainty', desc: 'Static detection cannot reliably handle abnormal, conflicting or unknown events.' },
  { title: 'Limited Indian ground truth', desc: 'Models need India-/facility-specific validation and transfer testing.' },
];

const solutions = [
  { title: 'Persistent Event Reconstruction', desc: 'Multi-sensor observations → physical event ID → lifecycle tracking.' },
  { title: 'Multi-Sensor Evidence Fusion', desc: 'FIRMS/VIIRS + INSAT-3DS + Sentinel + NiSAR/SAR + TROPOMI + weather + geospatial context.' },
  { title: 'Dual Thermal Intelligence', desc: 'High-T VNF/Planck physics + low-T Temporal/DBSCAN facility-source detection.' },
  { title: 'Historical & Behavioral Intelligence', desc: 'Facility thermal fingerprint + change-point detection → normal vs abnormal behavior.' },
  { title: 'Risk Assessment', desc: 'Comprehensive risk & exposure assessment with priority-based response.' },
  { title: 'Uncertainty-Aware Decision Intelligence', desc: 'Evidence conflict + OOD/abstention + conformal uncertainty → Risk → Priority → Verification.' },
];

const benefits = [
  { title: 'Faster Incident Awareness', desc: 'Earlier identification of emerging thermal events.' },
  { title: 'Reduced False Alerts', desc: 'Multi-sensor evidence helps distinguish routine heat from abnormal events.' },
  { title: 'Facility-Level Situational Awareness', desc: 'Clearer picture of what is happening and where.' },
  { title: 'Abnormal Event Detection', desc: 'Identifies behavior that deviates from normal.' },
  { title: 'Risk & Exposure Assessment', desc: 'Assesses event severity and potential impact.' },
  { title: 'Priority-Based Response', desc: 'Focuses attention where it matters most.' },
  { title: 'Explainable & Auditable Decisions', desc: 'WHY / WHY NOT / WHAT CHANGED with evidence.' },
  { title: 'Uncertainty-Aware Intelligence', desc: 'Handles unknown or conflicting evidence safely.' },
];

const aiModels = [
  { icon: Flame, name: 'Industrial Source Classifier', desc: 'Predicts likely source (flare, fire, etc.)' },
  { icon: Activity, name: 'Behavior & Abnormality Model', desc: 'Detects persistence, recurrence, unusual behavior' },
  { icon: Gauge, name: 'Risk & Priority Model', desc: 'Estimates risk and operational priority' },
  { icon: MapPin, name: 'Context / Embedding Model', desc: 'Facility fingerprint + novelty (AlphaEarth)' },
  { icon: HelpCircle, name: 'Uncertainty & OOD Layer', desc: 'Handles unknown / conflicting cases' },
];

const techStack = [
  'Python', 'FastAPI', 'SQLite', 'Next.js', 'React',
  'MapLibre GL', 'GeoPandas', 'Shapely', 'Scikit-learn', 'XGBoost',
];

/* ─────────────── COMPONENT ─────────────── */

export default function AboutPage() {
  const [currentTab, setCurrentTab] = useState('about');
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-[1400px] mx-auto px-6 py-8 space-y-10">

            {/* ═══════════ HERO ═══════════ */}
            <section className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="grid grid-cols-1 lg:grid-cols-5 gap-0">
                {/* Left text */}
                <div className="lg:col-span-3 p-8 lg:p-10 flex flex-col justify-center">
                  <h1 className="text-3xl lg:text-4xl font-extrabold text-slate-900 tracking-tight">About Agni-Netra</h1>
                  <p className="mt-2 text-lg text-blue-700 font-semibold italic">The satellite sees heat. Agni-Netra understands the event.</p>
                  <p className="mt-4 text-sm text-slate-600 leading-relaxed max-w-xl">
                    Agni-Netra is an AI-enabled geospatial intelligence system that turns satellite thermal observations and multi-source evidence into
                    persistent events, risk-aware analysis and human-verifiable decisions to support industrial safety, environmental monitoring and disaster response.
                  </p>
                  <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                    {pillars.map((p) => (
                      <div key={p.label} className="flex flex-col items-center text-center bg-slate-50 border border-slate-100 rounded-xl p-4 hover:shadow-md transition-shadow">
                        <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center mb-2">
                          <p.icon className="w-5 h-5" />
                        </div>
                        <span className="text-xs font-bold text-slate-900">{p.label}</span>
                        <span className="text-[10px] text-slate-500 mt-0.5 leading-tight">{p.desc}</span>
                      </div>
                    ))}
                  </div>
                </div>
                {/* Right image */}
                <div className="lg:col-span-2 relative min-h-[280px]">
                  <img src="/satellite-hero.jpg" alt="India from space" className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-gradient-to-l from-transparent to-white/30" />
                  <div className="absolute top-4 right-4 text-right space-y-1">
                    <div className="bg-blue-600 text-white text-[10px] font-bold px-3 py-1.5 rounded-lg shadow-lg">
                      From Space to Safety
                    </div>
                    <div className="bg-slate-900/80 text-white text-[10px] font-semibold px-3 py-1.5 rounded-lg backdrop-blur-sm">
                      A Cleaner, Safer Tomorrow
                    </div>
                  </div>
                  <div className="absolute bottom-4 right-4 space-y-1.5">
                    {['Multi-Sensor Data', 'AI-Powered Analysis', 'Real-time Monitoring', 'Actionable Insights'].map((t) => (
                      <div key={t} className="flex items-center gap-1.5 bg-white/90 backdrop-blur-sm text-[10px] font-semibold text-slate-800 px-2.5 py-1 rounded-md shadow-sm">
                        <CheckCircle2 className="w-3 h-3 text-green-600" />
                        {t}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            {/* ═══════════ KEY TECHNICAL ENABLERS + WORKFLOW + WHY DIFFERENT ═══════════ */}
            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Col 1 — Technical Enablers */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Radio className="w-5 h-5 text-blue-600" />
                  Key Technical Enablers
                </h2>
                <div className="space-y-4">
                  {technicalEnablers.map((t) => (
                    <div key={t.name} className="border-l-3 border-blue-500 pl-3">
                      <div className="text-xs font-bold text-blue-700">{t.name}</div>
                      <div className="text-[11px] text-slate-600 leading-snug mt-0.5">{t.desc}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Col 2 — System Workflow */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Layers className="w-5 h-5 text-indigo-600" />
                  System Workflow
                </h2>
                <div className="flex flex-col items-center gap-0">
                  {workflowSteps.map((step, i) => {
                    const isFirst = i === 0;
                    const isLast = i === workflowSteps.length - 1;
                    const colors = i < 2 ? 'bg-sky-100 text-sky-800 border-sky-200'
                      : i < 5 ? 'bg-blue-100 text-blue-800 border-blue-200'
                      : i < 7 ? 'bg-indigo-100 text-indigo-800 border-indigo-200'
                      : i < 9 ? 'bg-amber-100 text-amber-800 border-amber-200'
                      : i < 11 ? 'bg-emerald-100 text-emerald-800 border-emerald-200'
                      : 'bg-green-100 text-green-800 border-green-200';
                    return (
                      <React.Fragment key={step}>
                        <div className={`w-full text-center text-[11px] font-bold py-2 px-4 rounded-lg border ${colors}`}>
                          {step}
                        </div>
                        {!isLast && (
                          <ArrowDown className="w-3.5 h-3.5 text-slate-400 my-0.5 shrink-0" />
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              </div>

              {/* Col 3 — Why Different */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-amber-500" />
                  Why Agni-Netra is Different
                </h2>
                <div className="space-y-0 border border-slate-200 rounded-lg overflow-hidden">
                  <div className="grid grid-cols-2 bg-slate-100 border-b border-slate-200">
                    <div className="text-[10px] font-bold text-slate-600 uppercase tracking-wider px-3 py-2">Technical Capability</div>
                    <div className="text-[10px] font-bold text-slate-600 uppercase tracking-wider px-3 py-2">Why It Matters</div>
                  </div>
                  {whyDifferent.map((w, i) => (
                    <div key={i} className={`grid grid-cols-2 ${i < whyDifferent.length - 1 ? 'border-b border-slate-100' : ''}`}>
                      <div className="text-[11px] font-semibold text-slate-800 px-3 py-2.5">{w.capability}</div>
                      <div className="text-[11px] text-slate-600 px-3 py-2.5">{w.matter}</div>
                    </div>
                  ))}
                </div>

                {/* Same Thermal Signal comparison */}
                <div className="mt-6">
                  <h3 className="text-xs font-bold text-slate-800 mb-3">Same Thermal Signal → Different Intelligence</h3>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="text-[10px] font-bold text-green-800 mb-2 flex items-center gap-1">
                        <CircleDot className="w-3 h-3" /> Routine Flare
                      </div>
                      <ul className="text-[10px] text-green-700 space-y-1">
                        <li>High thermal signal</li>
                        <li>Persistent / fixed footprint</li>
                        <li>Historical behavior = normal</li>
                        <li>Evidence supports routine flare</li>
                        <li className="font-bold">Normal → Monitor</li>
                      </ul>
                    </div>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div className="text-[10px] font-bold text-red-800 mb-2 flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> Abnormal Industrial Event
                      </div>
                      <ul className="text-[10px] text-red-700 space-y-1">
                        <li>High thermal signal</li>
                        <li>FRP ↑ + expanding footprint</li>
                        <li>Historical behavior = abnormal</li>
                        <li>Evidence supports abnormal event</li>
                        <li className="font-bold">Highly Abnormal → Verify / Escalate</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* ═══════════ GAPS → SOLUTIONS → BENEFITS ═══════════ */}
            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Existing Gaps */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                  Existing Gaps
                </h2>
                <div className="space-y-3">
                  {existingGaps.map((g, i) => (
                    <div key={i} className="flex gap-3">
                      <div className="w-6 h-6 rounded-full bg-red-100 text-red-700 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                        {i + 1}
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800">{g.title}</div>
                        <div className="text-[11px] text-slate-500 leading-snug">{g.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Agni-Netra Solution */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-blue-600" />
                  Agni-Netra Solution
                </h2>
                <div className="space-y-3">
                  {solutions.map((s, i) => (
                    <div key={i} className="flex gap-3">
                      <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                        {i + 1}
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800">{s.title}</div>
                        <div className="text-[11px] text-slate-500 leading-snug">{s.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Key Benefits */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  Key Benefits
                </h2>
                <div className="space-y-3">
                  {benefits.map((b, i) => (
                    <div key={i} className="flex gap-3">
                      <div className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center text-[9px] font-bold shrink-0 mt-0.5">
                        {String(i + 1).padStart(2, '0')}
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800">{b.title}</div>
                        <div className="text-[11px] text-slate-500 leading-snug">{b.desc}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* ═══════════ AI/ML MODELS + TECH STACK ═══════════ */}
            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* AI/ML Models */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-600" />
                  Our AI/ML Models
                </h2>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                  {aiModels.map((m) => (
                    <div key={m.name} className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-center hover:shadow-md transition-shadow flex flex-col items-center">
                      <div className="w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center mb-2">
                        <m.icon className="w-5 h-5" />
                      </div>
                      <div className="text-[10px] font-bold text-slate-800 leading-tight">{m.name}</div>
                      <div className="text-[9px] text-slate-500 mt-1 leading-tight">{m.desc}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Technology Stack */}
              <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
                <h2 className="text-lg font-bold text-slate-900 mb-5 flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-indigo-600" />
                  Technology Stack
                </h2>
                <div className="flex flex-wrap gap-2.5">
                  {techStack.map((t) => (
                    <span key={t} className="px-4 py-2 bg-gradient-to-b from-blue-50 to-blue-100 border border-blue-200 rounded-lg text-xs font-bold text-blue-800 shadow-sm hover:shadow-md transition-shadow cursor-default">
                      {t}
                    </span>
                  ))}
                </div>
                <p className="text-[11px] text-slate-500 mt-4 italic">Simple. Modular. Scalable.</p>
              </div>
            </section>

            {/* ═══════════ FOOTER BANNER ═══════════ */}
            <section className="bg-gradient-to-r from-blue-700 via-blue-600 to-indigo-700 rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-4 shadow-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5 text-white" />
                </div>
                <span className="text-white text-lg font-bold tracking-tight">Towards a Safer, Cleaner and More Resilient India</span>
              </div>
              <div className="text-white/80 text-sm italic text-right">
                <span>&ldquo;Observations to Understanding.</span><br />
                <span>Understanding to Action.&rdquo;</span><br />
                <span className="text-white font-semibold not-italic">— Agni-Netra</span>
              </div>
            </section>

            {/* SIH badge */}
            <div className="text-center pb-4">
              <span className="inline-block px-4 py-1.5 bg-blue-100 text-blue-800 rounded-full text-xs font-bold tracking-widest uppercase">
                SIH Problem Statement PS162
              </span>
            </div>

          </div>
        </main>
      </div>
    </div>
  );
}
