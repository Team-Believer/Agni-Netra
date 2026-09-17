'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { fetchEvents } from '../../lib/api';
import { EventItem } from '../../lib/types';
import { Flame, Radio, AlertTriangle, Eye, MapPin, Clock, RefreshCw, Layers, ChevronRight, Compass, Thermometer } from 'lucide-react';

const INDIA_CENTER: [number, number] = [81.5, 22.0];
const INDIA_DEFAULT_ZOOM = 4.1;

const PRIORITY_CONFIG: Record<string, { color: string; label: string }> = {
  'Critical': { color: '#ef4444', label: 'Critical' },
  'High':     { color: '#f97316', label: 'High' },
  'Medium':   { color: '#eab308', label: 'Medium' },
  'Low':      { color: '#3b82f6', label: 'Low' },
  'Monitor':  { color: '#64748b', label: 'Monitor' },
};

// Regional thermal stations directly matching the reference graphic & key national hubs
const REGIONAL_THERMAL_STATIONS = [
  { name: 'Barmer', lon: 71.3967, lat: 25.7521, temp: '44.4°C', peak: '48.1°C', intensity: 0.98 },
  { name: 'Delhi', lon: 77.2090, lat: 28.6139, temp: '44.1°C', peak: '40.4°C', intensity: 0.95 },
  { name: 'Bhopal', lon: 77.4126, lat: 23.2599, temp: '40.7°C', peak: '43.9°C', intensity: 0.90 },
  { name: 'Nagpur', lon: 79.0882, lat: 21.1458, temp: '45.2°C', peak: '46.2°C', intensity: 0.98 },
  { name: 'Hyderabad', lon: 78.4867, lat: 17.3850, temp: '39.9°C', peak: '42.0°C', intensity: 0.88 },
  { name: 'Mumbai', lon: 72.8777, lat: 19.0760, temp: '38.4°C', peak: '39.6°C', intensity: 0.82 },
  { name: 'Ahmedabad', lon: 72.5714, lat: 23.0225, temp: '42.4°C', peak: '45.8°C', intensity: 0.92 },
  { name: 'Kolkata', lon: 88.3639, lat: 22.5726, temp: '38.7°C', peak: '39.6°C', intensity: 0.85 },
  { name: 'Jamshedpur', lon: 86.2029, lat: 22.8046, temp: '43.3°C', peak: '43.6°C', intensity: 0.94 },
  { name: 'Kozhikode', lon: 75.7804, lat: 11.2588, temp: '36.0°C', peak: '39.0°C', intensity: 0.45 },
  { name: 'Srinagar', lon: 74.7973, lat: 34.0837, temp: '27.4°C', peak: '31.2°C', intensity: 0.15 },
  { name: 'Leh', lon: 77.5771, lat: 34.1526, temp: '21.5°C', peak: '25.0°C', intensity: 0.08 },
  { name: 'Guwahati', lon: 91.7362, lat: 26.1445, temp: '34.8°C', peak: '37.1°C', intensity: 0.65 },
  { name: 'Chennai', lon: 80.2707, lat: 13.0827, temp: '37.8°C', peak: '41.5°C', intensity: 0.75 },
  { name: 'Bengaluru', lon: 77.5946, lat: 12.9716, temp: '33.2°C', peak: '36.8°C', intensity: 0.60 },
  { name: 'Raipur', lon: 81.6296, lat: 21.2514, temp: '43.8°C', peak: '45.9°C', intensity: 0.94 },
  { name: 'Singrauli', lon: 82.6734, lat: 24.1997, temp: '44.5°C', peak: '46.7°C', intensity: 0.96 },
  { name: 'Jaipur', lon: 75.7873, lat: 26.9124, temp: '43.2°C', peak: '45.1°C', intensity: 0.92 }
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
  const [showCityLabels, setShowCityLabels] = useState(true);
  
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const cityMarkersRef = useRef<maplibregl.Marker[]>([]);
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

  // Initialize Map
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
      center: INDIA_CENTER,
      zoom: INDIA_DEFAULT_ZOOM,
      minZoom: 3.5,
      maxZoom: 14,
      maxBounds: [
        [52.0, 0.0],
        [110.0, 42.0]
      ]
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
    map.current.addControl(new maplibregl.ScaleControl({ maxWidth: 200 }), 'bottom-left');

    map.current.on('load', () => {
      if (!map.current) return;

      // 1. Add Heatmap Source
      map.current.addSource('thermal-heat', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });

      // 2. Add Inverted World Mask Source (to darken everything outside India)
      map.current.addSource('india-mask', {
        type: 'geojson',
        data: '/data/india-mask.json'
      });

      // 3. Add India Boundary Source
      map.current.addSource('india-boundary', {
        type: 'geojson',
        data: '/data/india-boundary.json'
      });

      // 4. Add Continuous Thermal Heatmap Layer (renders wide, smooth heat contours)
      map.current.addLayer({
        id: 'thermal-heatmap',
        type: 'heatmap',
        source: 'thermal-heat',
        maxzoom: 15,
        paint: {
          'heatmap-weight': [
            'interpolate', ['linear'], ['get', 'intensity'],
            0, 0.3,
            0.5, 0.75,
            1, 1.4
          ],
          'heatmap-intensity': [
            'interpolate', ['linear'], ['zoom'],
            3, 1.6,
            4.3, 2.4,
            6, 3.5,
            10, 5.0
          ],
          'heatmap-color': [
            'interpolate', ['linear'], ['heatmap-density'],
            0,    'rgba(0,0,0,0)',
            0.05, 'rgba(129,140,248,0.25)',  // Cool violet / lavender
            0.15, 'rgba(56,189,248,0.45)',   // Light blue
            0.30, 'rgba(250,204,21,0.65)',   // Golden yellow
            0.50, 'rgba(249,115,22,0.80)',   // Vivid warm orange
            0.70, 'rgba(239,68,68,0.90)',    // Fiery red
            0.88, 'rgba(185,28,28,0.96)',    // Deep crimson
            1.0,  'rgba(127,29,29,1.0)'      // Intense peak heat core
          ],
          'heatmap-radius': [
            'interpolate', ['linear'], ['zoom'],
            3, 55,
            4.3, 95,
            6, 130,
            9, 170
          ],
          'heatmap-opacity': [
            'interpolate', ['linear'], ['zoom'],
            3, 0.85,
            6, 0.80,
            10, 0.65
          ]
        }
      });

      // 5. Add Outside India Dimming Mask (clips heat cleanly at national border)
      map.current.addLayer({
        id: 'outside-india-dim',
        type: 'fill',
        source: 'india-mask',
        paint: {
          'fill-color': '#060b14',
          'fill-opacity': 0.88
        }
      });

      // 6. Add India Glowing National Boundary
      map.current.addLayer({
        id: 'india-boundary-glow',
        type: 'line',
        source: 'india-boundary',
        paint: {
          'line-color': '#ea580c',
          'line-width': 6,
          'line-opacity': 0.40,
          'line-blur': 4
        }
      });

      // 7. Add India Boundary Crisp Line
      map.current.addLayer({
        id: 'india-boundary-line',
        type: 'line',
        source: 'india-boundary',
        paint: {
          'line-color': '#fb923c',
          'line-width': 2.2,
          'line-opacity': 0.90
        }
      });

      // Immediately center on India
      const fitIndia = () => {
        if (!map.current) return;
        map.current.resize();
        map.current.jumpTo({
          center: INDIA_CENTER,
          zoom: INDIA_DEFAULT_ZOOM
        });
      };

      fitIndia();
      setTimeout(fitIndia, 150);
      setTimeout(fitIndia, 600);

      (window as any).agniMap = map.current;
      setMapReady(true);
    });

    // Auto-resize observer when container dimensions change
    const resizeObserver = new ResizeObserver(() => {
      if (map.current) {
        map.current.resize();
      }
    });
    if (mapContainer.current) {
      resizeObserver.observe(mapContainer.current);
    }

    return () => {
      resizeObserver.disconnect();
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [mapToken]);

  // Update Continuous Heatmap Data (No Dots!)
  useEffect(() => {
    if (!map.current || !mapReady) return;

    const heatSource = map.current.getSource('thermal-heat') as maplibregl.GeoJSONSource;
    if (heatSource) {
      // 1. Live satellite thermal events
      const eventFeatures = events
        .filter(e => e.latitude != null && e.longitude != null)
        .map(event => ({
          type: 'Feature' as const,
          geometry: {
            type: 'Point' as const,
            coordinates: [event.longitude, event.latitude]
          },
          properties: {
            intensity: Math.min(Math.max((event.risk_index || 50) / 100, 0.45), 1.0),
            priority: event.priority,
            event_id: event.event_id
          }
        }));

      // 2. Regional thermal stations to provide smooth national thermal interpolation
      const stationFeatures = REGIONAL_THERMAL_STATIONS.map(st => ({
        type: 'Feature' as const,
        geometry: {
          type: 'Point' as const,
          coordinates: [st.lon, st.lat]
        },
        properties: {
          intensity: st.intensity,
          priority: 'High',
          event_id: st.name
        }
      }));

      heatSource.setData({
        type: 'FeatureCollection',
        features: [...eventFeatures, ...stationFeatures]
      });
    }

    // Clear previous city markers
    cityMarkersRef.current.forEach(m => m.remove());
    cityMarkersRef.current = [];

    // Render Clean City Labels (matching reference graphic - WITHOUT any dots)
    if (showCityLabels) {
      REGIONAL_THERMAL_STATIONS.slice(0, 10).forEach(st => {
        const el = document.createElement('div');
        el.className = 'city-temp-card';
        el.style.cssText = `
          display: flex;
          flex-direction: column;
          align-items: center;
          pointer-events: none;
          user-select: none;
        `;
        el.innerHTML = `
          <span style="font-size: 11px; font-weight: 800; color: #ffffff; text-shadow: 0 1px 3px rgba(0,0,0,0.9), 0 0 6px rgba(0,0,0,0.8); letter-spacing: -0.01em;">${st.name}</span>
          <div style="display: flex; flex-direction: column; align-items: center; margin-top: 2px; padding: 2px 6px; border-radius: 4px; background: rgba(185, 28, 28, 0.85); border: 1px solid rgba(254, 202, 202, 0.4); box-shadow: 0 2px 8px rgba(0,0,0,0.6); backdrop-filter: blur(2px);">
            <span style="font-size: 10px; font-weight: 800; color: #ffffff; font-family: monospace; line-height: 1.1;">${st.temp}</span>
            <span style="font-size: 8px; font-weight: 700; color: #fecaca; font-family: monospace; line-height: 1;">${st.peak}</span>
          </div>
        `;

        const marker = new maplibregl.Marker({ element: el, anchor: 'center' })
          .setLngLat([st.lon, st.lat])
          .addTo(map.current!);

        cityMarkersRef.current.push(marker);
      });
    }
  }, [events, mapReady, showCityLabels]);

  // Snap camera back to full India view
  const focusIndia = () => {
    if (map.current) {
      map.current.flyTo({
        center: INDIA_CENTER,
        zoom: INDIA_DEFAULT_ZOOM,
        duration: 900
      });
      if (popupRef.current) {
        popupRef.current.remove();
      }
      setSelectedEvent(null);
    }
  };

  const flyToEvent = (event: EventItem) => {
    setSelectedEvent(event);
    if (map.current && event.latitude != null && event.longitude != null) {
      map.current.flyTo({
        center: [event.longitude, event.latitude],
        zoom: 8.5,
        duration: 1200
      });

      if (popupRef.current) popupRef.current.remove();
      popupRef.current = new maplibregl.Popup({ closeButton: true, closeOnClick: true, offset: 15 })
        .setLngLat([event.longitude, event.latitude])
        .setHTML(`
          <div style="padding: 12px 16px; font-family: sans-serif; min-width: 190px;">
            <div style="font-size: 10px; font-weight: bold; color: #f97316; letter-spacing: 0.05em; text-transform: uppercase;">${event.event_id}</div>
            <div style="font-size: 13px; font-weight: bold; color: #ffffff; margin: 3px 0;">${event.classification || 'Thermal Anomaly'}</div>
            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">${event.location || 'India'}</div>
            <div style="display: flex; gap: 8px; border-t: 1px solid #334155; padding-top: 6px; font-size: 10px;">
              <span style="color: #cbd5e1;">Risk: <b style="color: #f87171;">${event.risk_index != null ? event.risk_index.toFixed(0) : '--'}/100</b></span>
              <span style="color: #cbd5e1;">Priority: <b style="color: #fb923c;">${event.priority}</b></span>
            </div>
          </div>
        `)
        .addTo(map.current);
    }
  };

  const totalCritical = events.filter(e => e.priority === 'Critical').length;
  const totalHigh = events.filter(e => e.priority === 'High').length;
  const totalActive = events.filter(e => e.status === 'Active' || e.status === 'Detected' || e.status === 'Emerging').length;

  return (
    <div className="fixed inset-0 w-screen h-screen bg-[#0f172a] flex flex-col overflow-hidden">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <style jsx global>{`
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
          box-shadow: 0 8px 32px rgba(0,0,0,0.6) !important;
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

      <div className="flex-1 flex overflow-hidden min-h-0">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 flex flex-col overflow-hidden min-h-0">
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
              {/* Focus India Button */}
              <button
                onClick={focusIndia}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-orange-500/15 border border-orange-500/30 text-xs font-semibold text-orange-300 hover:bg-orange-500/25 transition-all"
                title="Reset view to India"
              >
                <Compass className="w-3.5 h-3.5 text-orange-400" />
                Focus India
              </button>

              {/* City Labels Toggle */}
              <button
                onClick={() => setShowCityLabels(!showCityLabels)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  showCityLabels
                    ? 'bg-blue-500/15 border border-blue-500/30 text-blue-400'
                    : 'bg-slate-700 border border-slate-600 text-slate-400'
                }`}
                title="Toggle Regional City Temperature Labels"
              >
                <Thermometer className="w-3.5 h-3.5" />
                {showCityLabels ? 'City Labels: On' : 'City Labels: Off'}
              </button>

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
          <div className="flex-1 flex relative overflow-hidden min-h-0">
            {/* Map Container */}
            <div className="flex-1 relative min-h-0 h-full">
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

              {/* Reference-Style Title Badge (Top Right of Map) */}
              <div className="absolute top-4 right-14 bg-[#0f172a]/90 backdrop-blur-md border border-slate-700/80 rounded-xl px-4 py-3 z-10 shadow-2xl flex flex-col items-end">
                <span className="text-[11px] font-extrabold text-red-500 tracking-wider uppercase">HOTTEST REGIONS</span>
                <div className="flex items-center gap-1.5 mt-1">
                  <span className="px-2 py-0.5 bg-red-950 border border-red-600/60 rounded text-xs font-black text-white tracking-widest font-mono">2017</span>
                  <span className="px-2 py-0.5 bg-slate-800 border border-slate-600 rounded text-xs font-black text-slate-200 tracking-widest font-mono">2024</span>
                </div>
                <span className="text-[9px] text-slate-400 mt-1.5 font-medium tracking-tight">Realtime Spaceborne Thermal Anomaly</span>
              </div>

              {/* Reference-Style Gradient Legend Bar (Bottom Right of Map) */}
              <div className="absolute bottom-6 right-14 bg-[#0f172a]/95 backdrop-blur-md border border-slate-700/90 rounded-xl px-4 py-3 z-10 shadow-2xl min-w-[280px]">
                <div className="flex items-center justify-between text-xs font-black mb-1.5">
                  <span className="text-red-500 tracking-wider">HOT</span>
                  <span className="text-indigo-300 tracking-wider">COOL</span>
                </div>
                {/* Continuous Gradient Bar matching reference image */}
                <div 
                  className="w-full h-4 rounded-md border border-white/20 shadow-inner"
                  style={{
                    background: 'linear-gradient(to right, #7f1d1d 0%, #b91c1c 15%, #ea580c 35%, #facc15 65%, #38bdf8 85%, #818cf8 100%)'
                  }}
                />
                <div className="text-[9px] text-slate-400 uppercase tracking-widest text-center mt-2 font-semibold">
                  THIS MAP IS FOR REPRESENTATIONAL PURPOSE ONLY.
                </div>
              </div>

              {/* Priority Summary (Top Left) */}
              <div className="absolute top-4 left-4 bg-[#0f172a]/90 backdrop-blur-md border border-slate-700 rounded-xl p-3 z-10 shadow-xl">
                <div className="text-[10px] font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Layers className="w-3 h-3 text-orange-400" />
                  Thermal Priority Index
                </div>
                <div className="flex flex-col gap-1.5">
                  {Object.entries(PRIORITY_CONFIG).map(([key, cfg]) => (
                    <div key={key} className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full" style={{ background: cfg.color, boxShadow: `0 0 6px ${cfg.color}` }}></div>
                      <span className="text-[10px] text-slate-400 font-medium">{cfg.label}</span>
                      <span className="text-[10px] text-slate-500 ml-auto font-mono">
                        {events.filter(e => e.priority === key).length}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Side Panel */}
            <div className={`bg-[#1e293b] border-l border-slate-700 transition-all duration-300 flex flex-col ${isPanelOpen ? 'w-[340px]' : 'w-0'} overflow-hidden shrink-0 h-full min-h-0`}>
              <div className="p-3 border-b border-slate-700 flex items-center justify-between shrink-0">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Eye className="w-4 h-4 text-blue-400" />
                  Monitored Events ({events.length})
                </h3>
                <button onClick={() => setIsPanelOpen(false)} className="text-slate-500 hover:text-white transition-colors">
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto min-h-0">
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
