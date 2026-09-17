'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { fetchEvents } from '../../lib/api';
import { EventItem } from '../../lib/types';
import { Flame, Radio, AlertTriangle, Eye, MapPin, Clock, RefreshCw, Layers, ChevronRight } from 'lucide-react';

const PRIORITY_CONFIG: Record<string, { color: string; pulseColor: string; label: string }> = {
  'Critical': { color: '#ef4444', pulseColor: 'rgba(239,68,68,0.4)', label: 'Critical' },
  'High':     { color: '#f97316', pulseColor: 'rgba(249,115,22,0.4)', label: 'High' },
  'Medium':   { color: '#eab308', pulseColor: 'rgba(234,179,8,0.4)', label: 'Medium' },
  'Low':      { color: '#3b82f6', pulseColor: 'rgba(59,130,246,0.3)', label: 'Low' },
  'Monitor':  { color: '#64748b', pulseColor: 'rgba(100,116,139,0.3)', label: 'Monitor' },
};

const THERMAL_GRADIENT = [
  { temp: '<9°C', color: '#2563eb', label: 'Cold / No Thermal Stress' },
  { temp: '9–26°C', color: '#22c55e', label: 'Moderate Thermal' },
  { temp: '26–32°C', color: '#eab308', label: 'Moderate Heat Stress' },
  { temp: '32–38°C', color: '#f97316', label: 'Strong Heat Stress' },
  { temp: '>38°C', color: '#dc2626', label: 'Extreme / Active Fire' },
];

export default function LiveMapPage() {
  const [currentTab, setCurrentTab] = useState('live-map');
  const [searchQuery, setSearchQuery] = useState('');
  const [events, setEvents] = useState<EventItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<EventItem | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());
  const [isPanelOpen, setIsPanelOpen] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const popupRef = useRef<maplibregl.Popup | null>(null);
  const [mapReady, setMapReady] = useState(false);

  const mapToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;

  const loadEvents = useCallback(async () => {
    try {
      const data = await fetchEvents({ search: searchQuery });
      setEvents(data);
      setLastRefreshed(new Date());
    } catch (err) {
      console.error("Failed to load events for map", err);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery]);

  // Initial load
  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(loadEvents, 30000);
    return () => clearInterval(interval);
  }, [autoRefresh, loadEvents]);

  // Initialize map
  useEffect(() => {
    if (!mapToken) return;
    if (map.current) return;
    if (!mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          'mapbox-tiles': {
            type: 'raster',
            tiles: [
              `https://api.mapbox.com/styles/v1/mapbox/dark-v11/tiles/256/{z}/{x}/{y}@2x?access_token=${mapToken}`
            ],
            tileSize: 256,
            attribution: '&copy; <a href="https://www.mapbox.com/">Mapbox</a>'
          }
        },
        layers: [
          {
            id: 'mapbox-base',
            type: 'raster',
            source: 'mapbox-tiles',
            minzoom: 0,
            maxzoom: 22
          }
        ]
      },
      center: [78.9629, 20.5937],
      zoom: 4.5,
      maxZoom: 18,
      minZoom: 3,
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
    map.current.addControl(new maplibregl.ScaleControl({ maxWidth: 200 }), 'bottom-left');

    // Add heatmap source + layer once map loads
    map.current.on('load', () => {
      if (!map.current) return;

      map.current.addSource('thermal-heat', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });

      map.current.addLayer({
        id: 'thermal-heatmap',
        type: 'heatmap',
        source: 'thermal-heat',
        maxzoom: 15,
        paint: {
          'heatmap-weight': ['interpolate', ['linear'], ['get', 'intensity'], 0, 0, 1, 1],
          'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 0, 1, 15, 3],
          'heatmap-color': [
            'interpolate', ['linear'], ['heatmap-density'],
            0,    'rgba(0,0,0,0)',
            0.1,  'rgba(37,99,235,0.3)',
            0.25, 'rgba(34,197,94,0.5)',
            0.4,  'rgba(234,179,8,0.6)',
            0.6,  'rgba(249,115,22,0.7)',
            0.8,  'rgba(239,68,68,0.8)',
            1,    'rgba(220,38,38,0.95)'
          ],
          'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 0, 15, 5, 30, 10, 50],
          'heatmap-opacity': ['interpolate', ['linear'], ['zoom'], 7, 0.85, 15, 0.4]
        }
      });

      setMapReady(true);
    });
  }, [mapToken]);

  // Update heatmap + markers when events change AND map is ready
  useEffect(() => {
    if (!map.current || !mapReady) return;

    // Update heatmap data
    const heatSource = map.current.getSource('thermal-heat') as maplibregl.GeoJSONSource;
    if (heatSource) {
      const features = events
        .filter(e => e.latitude != null && e.longitude != null)
        .map(event => ({
          type: 'Feature' as const,
          geometry: {
            type: 'Point' as const,
            coordinates: [event.longitude, event.latitude]
          },
          properties: {
            intensity: Math.min((event.risk_index || 0) / 100, 1),
            priority: event.priority,
            event_id: event.event_id
          }
        }));
      heatSource.setData({ type: 'FeatureCollection', features });
    }

    // Clear old markers
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    // Add pulsing markers
    events
      .filter(e => e.latitude != null && e.longitude != null)
      .forEach(event => {
        const config = PRIORITY_CONFIG[event.priority] || PRIORITY_CONFIG['Monitor'];

        const el = document.createElement('div');
        el.style.width = '40px';
        el.style.height = '40px';
        el.style.position = 'relative';
        el.style.cursor = 'pointer';

        // Pulse ring
        const pulse = document.createElement('div');
        pulse.style.cssText = `
          position: absolute;
          top: 0; left: 0;
          width: 40px; height: 40px;
          border-radius: 50%;
          background: ${config.pulseColor};
          animation: thermalPulse 2s ease-out infinite;
        `;
        el.appendChild(pulse);

        // Core dot
        const core = document.createElement('div');
        core.style.cssText = `
          position: absolute;
          top: 50%; left: 50%;
          transform: translate(-50%, -50%);
          width: 14px; height: 14px;
          border-radius: 50%;
          background: ${config.color};
          border: 2.5px solid rgba(255,255,255,0.9);
          box-shadow: 0 0 8px ${config.color}, 0 0 16px ${config.pulseColor};
          z-index: 2;
        `;
        el.appendChild(core);

        el.addEventListener('click', () => {
          setSelectedEvent(event);
          setIsPanelOpen(true);
          map.current?.flyTo({
            center: [event.longitude, event.latitude],
            zoom: 8,
            duration: 1200
          });
        });

        const marker = new maplibregl.Marker({ element: el, anchor: 'center' })
          .setLngLat([event.longitude, event.latitude])
          .addTo(map.current!);

        markersRef.current.push(marker);
      });
  }, [events, mapReady]);

  const flyToEvent = (event: EventItem) => {
    setSelectedEvent(event);
    if (map.current && event.latitude != null && event.longitude != null) {
      map.current.flyTo({
        center: [event.longitude, event.latitude],
        zoom: 9,
        duration: 1200
      });
    }
  };

  const totalCritical = events.filter(e => e.priority === 'Critical').length;
  const totalHigh = events.filter(e => e.priority === 'High').length;
  const totalActive = events.filter(e => e.status === 'Active' || e.status === 'Detected' || e.status === 'Emerging').length;

  return (
    <div className="min-h-screen bg-[#0f172a] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <style jsx global>{`
        @keyframes thermalPulse {
          0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
          100% { transform: translate(-50%, -50%) scale(2.5); opacity: 0; }
        }
        @keyframes statusBlink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        .maplibregl-popup-content {
          background: #1e293b !important;
          color: #e2e8f0 !important;
          border: 1px solid #334155 !important;
          border-radius: 12px !important;
          padding: 0 !important;
          box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important;
        }
        .maplibregl-popup-tip {
          border-top-color: #1e293b !important;
        }
        .maplibregl-ctrl-group {
          background: #1e293b !important;
          border: 1px solid #334155 !important;
        }
        .maplibregl-ctrl-group button {
          filter: invert(1);
        }
      `}</style>

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Top Bar */}
          <div className="px-4 py-2.5 bg-[#1e293b] border-b border-slate-700 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Flame className="w-5 h-5 text-orange-400" />
                <h1 className="text-base font-bold text-white">Thermal Event Monitoring</h1>
              </div>

              <div className="flex items-center gap-2 ml-4">
                <span className="flex items-center gap-1.5 px-2.5 py-1 bg-red-500/15 border border-red-500/30 rounded-lg text-xs font-bold text-red-400">
                  <span className="w-2 h-2 rounded-full bg-red-500" style={{ animation: 'statusBlink 1.5s infinite' }}></span>
                  {totalCritical} Critical
                </span>
                <span className="flex items-center gap-1.5 px-2.5 py-1 bg-orange-500/15 border border-orange-500/30 rounded-lg text-xs font-bold text-orange-400">
                  {totalHigh} High
                </span>
                <span className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-500/15 border border-slate-500/30 rounded-lg text-xs font-bold text-slate-300">
                  <Radio className="w-3 h-3" />
                  {totalActive} Active
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  autoRefresh
                    ? 'bg-green-500/15 border border-green-500/30 text-green-400'
                    : 'bg-slate-700 border border-slate-600 text-slate-400'
                }`}
              >
                <RefreshCw className={`w-3.5 h-3.5 ${autoRefresh ? 'animate-spin' : ''}`} style={{ animationDuration: '3s' }} />
                {autoRefresh ? 'Live' : 'Paused'}
              </button>
              <button onClick={loadEvents} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-700 border border-slate-600 text-xs font-semibold text-slate-300 hover:bg-slate-600 transition-all">
                <RefreshCw className="w-3.5 h-3.5" />
                Refresh
              </button>
              <span className="text-[10px] text-slate-500 font-mono">
                Last: {lastRefreshed.toLocaleTimeString()}
              </span>
            </div>
          </div>

          {/* Map + Panel */}
          <div className="flex-1 flex relative overflow-hidden">
            {/* Map Container */}
            <div className="flex-1 relative">
              {!mapToken ? (
                <div className="absolute inset-0 flex items-center justify-center bg-[#0f172a] z-10">
                  <div className="text-center p-8 bg-slate-800/80 rounded-2xl border border-slate-700">
                    <AlertTriangle className="w-10 h-10 text-amber-400 mx-auto mb-3" />
                    <p className="text-slate-200 font-semibold">Map provider not configured</p>
                    <p className="text-xs text-slate-500 mt-2">Set NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN in .env.local</p>
                  </div>
                </div>
              ) : (
                <div ref={mapContainer} className="w-full h-full" />
              )}

              {/* Thermal Legend */}
              <div className="absolute bottom-6 left-14 bg-[#0f172a]/90 backdrop-blur-md border border-slate-700 rounded-xl p-3 z-10 shadow-xl">
                <div className="text-[10px] font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Layers className="w-3 h-3 text-orange-400" />
                  Thermal Intensity
                </div>
                <div className="flex flex-col gap-1">
                  {THERMAL_GRADIENT.map((item, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <div className="w-5 h-2.5 rounded-sm" style={{ background: item.color }}></div>
                      <span className="text-[9px] text-slate-400 font-medium">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Priority Legend */}
              <div className="absolute top-4 left-4 bg-[#0f172a]/90 backdrop-blur-md border border-slate-700 rounded-xl p-3 z-10 shadow-xl">
                <div className="text-[10px] font-bold text-slate-300 uppercase tracking-wider mb-2">Event Priority</div>
                <div className="flex flex-col gap-1.5">
                  {Object.entries(PRIORITY_CONFIG).map(([key, cfg]) => (
                    <div key={key} className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full border-2 border-white/80" style={{ background: cfg.color, boxShadow: `0 0 6px ${cfg.color}` }}></div>
                      <span className="text-[10px] text-slate-400 font-medium">{cfg.label}</span>
                      <span className="text-[10px] text-slate-600 ml-auto font-mono">
                        {events.filter(e => e.priority === key).length}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Side Panel */}
            <div className={`bg-[#1e293b] border-l border-slate-700 transition-all duration-300 flex flex-col ${isPanelOpen ? 'w-[340px]' : 'w-0'} overflow-hidden shrink-0`}>
              <div className="p-3 border-b border-slate-700 flex items-center justify-between shrink-0">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Eye className="w-4 h-4 text-blue-400" />
                  Monitored Events ({events.length})
                </h3>
                <button onClick={() => setIsPanelOpen(false)} className="text-slate-500 hover:text-white transition-colors">
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto">
                {isLoading ? (
                  <div className="p-6 text-center">
                    <div className="w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
                    <p className="text-xs text-slate-500 mt-3">Loading events...</p>
                  </div>
                ) : events.length === 0 ? (
                  <div className="p-6 text-center">
                    <Radio className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                    <p className="text-sm text-slate-400">No active thermal events</p>
                    <p className="text-xs text-slate-600 mt-1">Monitoring for satellite data...</p>
                  </div>
                ) : (
                  <div className="divide-y divide-slate-700/50">
                    {events.map(event => {
                      const cfg = PRIORITY_CONFIG[event.priority] || PRIORITY_CONFIG['Monitor'];
                      const isSelected = selectedEvent?.event_id === event.event_id;
                      return (
                        <button
                          key={event.event_id}
                          onClick={() => flyToEvent(event)}
                          className={`w-full text-left p-3 hover:bg-slate-800/80 transition-all ${isSelected ? 'bg-slate-800 border-l-2' : 'border-l-2 border-transparent'}`}
                          style={isSelected ? { borderLeftColor: cfg.color } : {}}
                        >
                          <div className="flex items-start justify-between mb-1.5">
                            <div className="flex items-center gap-2">
                              <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: cfg.color, boxShadow: `0 0 6px ${cfg.color}` }}></div>
                              <span className="text-xs font-bold text-white">{event.event_id}</span>
                            </div>
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ background: `${cfg.color}20`, color: cfg.color }}>
                              {event.priority}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-300 font-medium truncate pl-[18px]">{event.classification || 'Unknown'}</p>
                          <p className="text-[10px] text-slate-500 truncate pl-[18px] flex items-center gap-1 mt-0.5">
                            <MapPin className="w-2.5 h-2.5 shrink-0" />
                            {event.location || 'Unknown Location'}
                          </p>
                          <div className="flex items-center gap-3 mt-1.5 pl-[18px]">
                            <span className="text-[9px] text-slate-500">
                              Risk: <span className="text-slate-300 font-bold">{event.risk_index != null ? event.risk_index.toFixed(0) : '--'}/100</span>
                            </span>
                            <span className="text-[9px] text-slate-500">
                              FRP: <span className="text-slate-300 font-bold">{event.frp_change_pct != null ? `${event.frp_change_pct > 0 ? '+' : ''}${event.frp_change_pct.toFixed(0)}%` : '--'}</span>
                            </span>
                            <span className="text-[9px] text-slate-500 flex items-center gap-0.5">
                              <Clock className="w-2.5 h-2.5" />
                              {event.last_seen ? new Date(event.last_seen).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '--'}
                            </span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Panel toggle (when closed) */}
            {!isPanelOpen && (
              <button
                onClick={() => setIsPanelOpen(true)}
                className="absolute right-0 top-1/2 -translate-y-1/2 bg-[#1e293b] border border-slate-700 border-r-0 rounded-l-lg p-2 z-10 hover:bg-slate-700 transition-colors"
              >
                <Eye className="w-4 h-4 text-blue-400" />
              </button>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
