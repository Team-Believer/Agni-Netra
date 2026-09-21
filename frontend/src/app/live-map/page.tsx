'use client';

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useParams } from 'next/navigation';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { fetchEvents } from '../../lib/api';
import { EventItem } from '../../lib/types';
import { 
  Flame, 
  Radio, 
  AlertTriangle, 
  Eye, 
  MapPin, 
  Clock, 
  RefreshCw, 
  Layers, 
  ChevronRight, 
  Compass, 
  Thermometer, 
  Search,
  AlertCircle,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

const INDIA_CENTER: [number, number] = [81.5, 22.0];
const INDIA_DEFAULT_ZOOM = 4.1;

const PRIORITY_CONFIG: Record<string, { color: string; label: string }> = {
  'Critical': { color: '#ef4444', label: 'Critical' },
  'High':     { color: '#f97316', label: 'High' },
  'Medium':   { color: '#eab308', label: 'Medium' },
  'Low':      { color: '#3b82f6', label: 'Low' },
  'Monitor':  { color: '#64748b', label: 'Monitor' },
};


function getRelativeUpdatedTime(lastRefreshed: Date): string {
  const diffSec = Math.max(0, Math.floor((new Date().getTime() - lastRefreshed.getTime()) / 1000));
  if (diffSec < 15) return 'Updated just now';
  if (diffSec < 60) return `Updated ${diffSec}s ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `Updated ${diffMin}m ago`;
  const diffHours = Math.floor(diffMin / 60);
  return `Updated ${diffHours}h ago`;
}

function formatEventTime(dateStr?: string | Date): string {
  if (!dateStr) return '--';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '--';

  const now = new Date();
  const isToday =
    date.getDate() === now.getDate() &&
    date.getMonth() === now.getMonth() &&
    date.getFullYear() === now.getFullYear();

  const timeString = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });

  if (isToday) {
    return timeString;
  }

  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return `${monthNames[date.getMonth()]} ${date.getDate()}, ${timeString}`;
}

export default function LiveMapPage({ params: propParams }: { params?: { eventId?: string } } = {}) {
  const routerParams = useParams();
  const routeParamEventId = propParams?.eventId || (routerParams?.eventId ? (Array.isArray(routerParams.eventId) ? routerParams.eventId[0] : routerParams.eventId) : null);
  const targetEventId = routeParamEventId ? decodeURIComponent(routeParamEventId) : null;

  const [currentTab, setCurrentTab] = useState('live-map');
  const [globalSearchQuery, setGlobalSearchQuery] = useState('');
  const [sideSearchQuery, setSideSearchQuery] = useState('');
  const [events, setEvents] = useState<EventItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<EventItem | null>(null);
  const [hoveredEventId, setHoveredEventId] = useState<string | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());
  const [timeAgoText, setTimeAgoText] = useState('Updated just now');
  const [isPanelOpen, setIsPanelOpen] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [priorityFilter, setPriorityFilter] = useState<string>('All');
  const [tabFilter, setTabFilter] = useState<string>('All');
  const [selectedYear, setSelectedYear] = useState<'2024' | '2026'>('2026');
  const [mapError, setMapError] = useState(false);
  
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const popupRef = useRef<maplibregl.Popup | null>(null);
  const [mapReady, setMapReady] = useState(false);

  const mapToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;

  const loadEvents = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchEvents({ search: globalSearchQuery });
      setEvents(data);
      const now = new Date();
      setLastRefreshed(now);
      setTimeAgoText(getRelativeUpdatedTime(now));
    } catch (err) {
      console.error("Failed to load events for map", err);
    } finally {
      setIsLoading(false);
    }
  }, [globalSearchQuery]);

  // Initial load
  useEffect(() => {
    loadEvents();
  }, [loadEvents]);

  // Update "Updated Xm ago" timer text every 10 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeAgoText(getRelativeUpdatedTime(lastRefreshed));
    }, 10000);
    return () => clearInterval(timer);
  }, [lastRefreshed]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(loadEvents, 30000);
    return () => clearInterval(interval);
  }, [autoRefresh, loadEvents]);

  // Calculate priority counts
  const priorityCounts = useMemo(() => {
    const counts: Record<string, number> = { Critical: 0, High: 0, Medium: 0, Low: 0, Monitor: 0 };
    events.forEach(e => {
      if (counts[e.priority] !== undefined) {
        counts[e.priority]++;
      }
    });
    return counts;
  }, [events]);

  // Combined Filtered Events (filtered by priority index filter, tab filter, side search, and global search)
  const filteredEvents = useMemo(() => {
    return events.filter(event => {
      // 1. Priority index filter
      if (priorityFilter !== 'All' && event.priority !== priorityFilter) {
        return false;
      }
      // 2. Tab filter (All / High / Medium / Low)
      if (tabFilter !== 'All' && event.priority !== tabFilter) {
        return false;
      }
      // 3. Side search query
      if (sideSearchQuery.trim() !== '') {
        const q = sideSearchQuery.toLowerCase();
        const idMatch = event.event_id.toLowerCase().includes(q);
        const locMatch = (event.location || '').toLowerCase().includes(q);
        const classMatch = (event.classification || '').toLowerCase().includes(q);
        if (!idMatch && !locMatch && !classMatch) return false;
      }
      return true;
    });
  }, [events, priorityFilter, tabFilter, sideSearchQuery]);

  // Initialize Map
  const initMap = useCallback(() => {
    if (!mapToken) {
      setMapError(true);
      return;
    }
    if (map.current) return;
    if (!mapContainer.current) return;

    setMapError(false);

    try {
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

      map.current.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-left');
      map.current.addControl(new maplibregl.ScaleControl({ maxWidth: 200 }), 'bottom-left');

      map.current.on('error', (e) => {
        console.warn("Map rendering error:", e);
        setMapError(true);
      });

      map.current.on('load', () => {
        if (!map.current) return;

        // 1. Add Heatmap Source
        map.current.addSource('thermal-heat', {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: [] }
        });

        // 2. Add Inverted World Mask Source
        map.current.addSource('india-mask', {
          type: 'geojson',
          data: '/data/india-mask.json'
        });

        // 3. Add India Boundary Source
        map.current.addSource('india-boundary', {
          type: 'geojson',
          data: '/data/india-boundary.json'
        });

        // 4. Add Continuous Thermal Heatmap Layer
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
              0.05, 'rgba(129,140,248,0.25)',
              0.15, 'rgba(56,189,248,0.45)',
              0.30, 'rgba(250,204,21,0.65)',
              0.50, 'rgba(249,115,22,0.80)',
              0.70, 'rgba(239,68,68,0.90)',
              0.88, 'rgba(185,28,28,0.96)',
              1.0,  'rgba(127,29,29,1.0)'
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

        // 5. Add Outside India Dimming Mask
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

        // 8. Add Thermal Point Markers Layer for direct clicking & visibility
        map.current.addLayer({
          id: 'thermal-points',
          type: 'circle',
          source: 'thermal-heat',
          paint: {
            'circle-radius': [
              'interpolate', ['linear'], ['zoom'],
              3, 4,
              6, 7,
              10, 11
            ],
            'circle-color': [
              'match',
              ['get', 'priority'],
              'Critical', '#ef4444',
              'High', '#f97316',
              'Medium', '#eab308',
              'Low', '#3b82f6',
              '#64748b'
            ],
            'circle-stroke-width': 1.5,
            'circle-stroke-color': '#ffffff',
            'circle-opacity': 0.95
          }
        });

        map.current.on('click', 'thermal-points', (e: any) => {
          if (!e.features || e.features.length === 0) return;
          const clickedId = e.features[0].properties?.event_id;
          if (clickedId) {
            window.history.pushState({}, '', `/live-map/${clickedId}`);
          }
        });

        map.current.on('mouseenter', 'thermal-points', () => {
          if (map.current) map.current.getCanvas().style.cursor = 'pointer';
        });

        map.current.on('mouseleave', 'thermal-points', () => {
          if (map.current) map.current.getCanvas().style.cursor = '';
        });

        const fitIndia = () => {
          if (!map.current) return;
          map.current.resize();
          map.current.jumpTo({
            center: INDIA_CENTER,
            zoom: INDIA_DEFAULT_ZOOM
          });
        };

        if (!targetEventId) {
          fitIndia();
          setTimeout(fitIndia, 150);
          setTimeout(fitIndia, 600);
        }

        (window as any).agniMap = map.current;
        setMapReady(true);
      });
    } catch (err) {
      console.error("Map initialization failed", err);
      setMapError(true);
    }
  }, [mapToken, targetEventId]);

  useEffect(() => {
    initMap();
    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [initMap]);

  // Update Heatmap & City Markers when filteredEvents or mapReady changes
  useEffect(() => {
    if (!map.current || !mapReady) return;

    const heatSource = map.current.getSource('thermal-heat') as maplibregl.GeoJSONSource;
    if (heatSource) {
      // 1. Satellite thermal events matching priority & search filters
      const eventFeatures = filteredEvents
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

      heatSource.setData({
        type: 'FeatureCollection',
        features: eventFeatures
      });
    }

  }, [filteredEvents, mapReady]);

  const flyToEvent = useCallback((event: EventItem) => {
    setSelectedEvent(event);
    if (map.current && event.latitude != null && event.longitude != null) {
      map.current.flyTo({
        center: [event.longitude, event.latitude],
        zoom: 7.5,
        duration: 1000
      });

      if (popupRef.current) popupRef.current.remove();
      popupRef.current = new maplibregl.Popup({ closeButton: true, closeOnClick: false, offset: 15 })
        .setLngLat([event.longitude, event.latitude])
        .setHTML(`
          <div style="padding: 12px 16px; font-family: sans-serif; min-width: 210px;">
            <div style="font-size: 10px; font-weight: bold; color: #f97316; letter-spacing: 0.05em; text-transform: uppercase;">${event.event_id}</div>
            <div style="font-size: 13px; font-weight: bold; color: #ffffff; margin: 3px 0;">${event.classification || 'Thermal Anomaly'}</div>
            <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">${event.location || 'India'}</div>
            <div style="display: flex; gap: 8px; border-top: 1px solid #334155; padding-top: 6px; font-size: 10px;">
              <span style="color: #cbd5e1;">Risk: <b style="color: #f87171;">${event.risk_index != null ? event.risk_index.toFixed(0) : '--'}/100</b></span>
              <span style="color: #cbd5e1;">Priority: <b style="color: #fb923c;">${event.priority}</b></span>
            </div>
          </div>
        `)
        .addTo(map.current);
    }
  }, []);

  // When targetEventId changes or map is ready and events are loaded
  useEffect(() => {
    if (!mapReady || !map.current || events.length === 0) return;

    if (targetEventId) {
      const target = events.find(e => e.event_id === targetEventId);
      if (target && target.latitude != null && target.longitude != null) {
        flyToEvent(target);
      }
    }
  }, [mapReady, events, targetEventId, flyToEvent]);

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
      if (targetEventId) {
        window.history.pushState({}, '', '/live-map');
      }
    }
  };



  return (
    <div className="fixed inset-0 w-screen h-screen bg-[#0f172a] flex flex-col overflow-hidden">
      <Header searchQuery={globalSearchQuery} onSearchChange={setGlobalSearchQuery} />

      <style jsx global>{`
        @keyframes statusBlink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
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
        .maplibregl-ctrl-bottom-left {
          z-index: 30 !important;
        }
        .maplibregl-ctrl-group {
          background: #0f172a !important;
          border: 1px solid #334155 !important;
          border-radius: 8px !important;
          overflow: hidden !important;
          box-shadow: 0 4px 16px rgba(0,0,0,0.5) !important;
        }
        .maplibregl-ctrl-group button {
          background: #0f172a !important;
        }
        .maplibregl-ctrl-group button span {
          filter: invert(1) brightness(2) !important;
        }
      `}</style>

      <div className="flex-1 flex overflow-hidden min-h-0">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 flex flex-col overflow-hidden min-h-0">
          {/* Top Header Bar */}
          <div className="px-4 py-2.5 bg-[#0f172a] border-b border-slate-800 flex items-center justify-between shrink-0 gap-4">
            <div className="flex items-center gap-3 min-w-0 shrink">
              <Flame className="w-5 h-5 text-orange-400 shrink-0" />
              <h1 className="text-base font-bold text-white tracking-tight truncate">Thermal Event Monitoring</h1>
              {priorityFilter !== 'All' && (
                <span className="ml-2 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 flex items-center gap-1.5 shrink-0">
                  Filtered: {priorityFilter}
                  <button onClick={() => setPriorityFilter('All')} className="hover:text-white font-bold ml-1">✕</button>
                </span>
              )}
            </div>

            {/* Toolbar Group (Live, Updated, Focus India, City Labels) */}
            <div className="flex items-center gap-2.5 ml-auto shrink-0 flex-nowrap whitespace-nowrap">
              {/* Live / Pause status button with pulsing dot */}
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-800/90 border border-slate-700 text-xs font-semibold text-slate-200 hover:bg-slate-700 transition-all shrink-0"
                title={autoRefresh ? 'Click to Pause auto-refresh' : 'Click to Resume live refresh'}
              >
                <span className={`w-2.5 h-2.5 rounded-full ${autoRefresh ? 'bg-emerald-500' : 'bg-amber-400'}`} style={autoRefresh ? { animation: 'statusBlink 1.5s infinite' } : {}}></span>
                <span>{autoRefresh ? 'Live' : 'Paused'}</span>
              </button>

              {/* Merged Refresh + Last Updated Button */}
              <button
                onClick={loadEvents}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/90 border border-slate-700 text-xs font-semibold text-slate-200 hover:bg-slate-700 transition-all shrink-0"
                title="Click to Refresh immediately"
              >
                <RefreshCw className={`w-3 h-3 text-slate-400 ${isLoading ? 'animate-spin' : ''}`} />
                <span>{timeAgoText}</span>
              </button>

              {/* Focus India Button */}
              <button
                onClick={focusIndia}
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-orange-500/20 border border-orange-500/40 text-xs font-semibold text-orange-300 hover:bg-orange-500/30 transition-all shrink-0"
                title="Reset view to India"
              >
                <Compass className="w-3.5 h-3.5 text-orange-400" />
                <span>Focus India</span>
              </button>

            </div>
          </div>

          {/* Map + Side Panel */}
          <div className="flex-1 flex relative overflow-hidden min-h-0">
            {/* Map Area */}
            <div className="flex-1 relative min-h-0 h-full bg-[#090d16]">
              {mapError ? (
                <div className="absolute inset-0 flex items-center justify-center bg-[#0b1120] z-10 p-6">
                  <div className="text-center p-8 bg-[#0f172a]/90 backdrop-blur-md rounded-xl border border-slate-700/80 shadow-2xl max-w-md">
                    <AlertCircle className="w-12 h-12 text-amber-400 mx-auto mb-3" />
                    <p className="text-base font-bold text-slate-100">Unable to load live map graphics</p>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      Interactive map graphics are temporarily unavailable. Live thermal event monitoring and alerts list remain fully operational.
                    </p>
                    <button
                      onClick={() => { setMapError(false); initMap(); }}
                      className="mt-5 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-lg transition-all shadow-lg flex items-center gap-2 mx-auto"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      Retry Map
                    </button>
                  </div>
                </div>
              ) : (
                <div ref={mapContainer} className="w-full h-full" />
              )}

              {/* Hottest Regions Panel (Top Right, 16px offset) */}
              <div className="absolute top-4 right-4 z-10 w-64 bg-[#0f172a]/90 backdrop-blur-md border border-slate-700/80 rounded-xl px-4 py-3 shadow-2xl flex flex-col">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <span className="text-[11px] font-extrabold text-red-500 tracking-wider uppercase flex items-center gap-1.5">
                    <Flame className="w-3.5 h-3.5" />
                    MOST CRITICAL EVENTS
                  </span>
                  {/* Labeled Year Toggle */}
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] text-slate-400 font-medium mr-1">Year:</span>
                    <button
                      onClick={() => setSelectedYear('2024')}
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold transition-all ${
                        selectedYear === '2024'
                          ? 'bg-slate-700 text-white border border-slate-500'
                          : 'bg-slate-900 text-slate-500 border border-slate-800 hover:text-slate-300'
                      }`}
                    >
                      2024
                    </button>
                    <button
                      onClick={() => setSelectedYear('2026')}
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold transition-all ${
                        selectedYear === '2026'
                          ? 'bg-red-950 text-red-200 border border-red-600/70'
                          : 'bg-slate-900 text-slate-500 border border-slate-800 hover:text-slate-300'
                      }`}
                    >
                      2026
                    </button>
                  </div>
                </div>

                {/* Top 3 Events List */}
                <div className="flex flex-col gap-1.5 mt-2.5">
                  {filteredEvents
                    .filter(e => e.priority === 'Critical' || e.priority === 'High')
                    .sort((a, b) => b.risk_index - a.risk_index)
                    .slice(0, 3)
                    .map((st, idx) => (
                    <div key={st.event_id} className="flex flex-col py-1.5 px-2 rounded-lg bg-slate-800/40 border border-slate-800/80 text-xs hover:bg-slate-700/50 cursor-pointer" onClick={() => flyToEvent(st)}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-bold text-slate-500 font-mono">0{idx + 1}</span>
                          <span className="font-semibold text-slate-200">{st.event_id}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono font-bold text-red-400 text-[11px]">{st.risk_index}/100</span>
                        </div>
                      </div>
                      <div className="pl-6 text-[10px] text-slate-400 truncate">{st.location || 'Unknown Location'}</div>
                    </div>
                  ))}
                  {filteredEvents.filter(e => e.priority === 'Critical' || e.priority === 'High').length === 0 && (
                    <div className="text-center py-2 text-[10px] text-slate-500">No critical events currently active.</div>
                  )}
                </div>
                <span className="text-[9px] text-slate-400 mt-2 font-medium tracking-tight text-right">Realtime Event Anomaly</span>
              </div>

              {/* Thermal Priority Index (Top Left Floating Panel) */}
              <div className="absolute top-4 left-4 z-10 w-64 bg-[#0f172a]/90 backdrop-blur-md border border-slate-700/80 rounded-xl p-3 shadow-2xl">
                <div className="text-[10px] font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-orange-400" />
                    <span>Thermal Priority Index</span>
                  </div>
                  {priorityFilter !== 'All' && (
                    <button
                      onClick={() => setPriorityFilter('All')}
                      className="text-[9px] text-indigo-400 hover:underline lowercase font-medium"
                    >
                      reset
                    </button>
                  )}
                </div>
                <div className="flex flex-col gap-1">
                  {Object.entries(PRIORITY_CONFIG).map(([key, cfg]) => {
                    const count = priorityCounts[key] || 0;
                    const isSelected = priorityFilter === key;
                    const isDisabled = count === 0;
                    return (
                      <button
                        key={key}
                        disabled={isDisabled}
                        onClick={() => setPriorityFilter(isSelected ? 'All' : key)}
                        className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs transition-all ${
                          isDisabled
                            ? 'opacity-40 cursor-not-allowed bg-transparent'
                            : isSelected
                              ? 'bg-slate-800 border border-slate-600 shadow-sm text-white'
                              : 'hover:bg-slate-800/60 text-slate-300'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <div
                            className="w-2.5 h-2.5 rounded-full shrink-0"
                            style={{ background: cfg.color, boxShadow: `0 0 6px ${cfg.color}` }}
                          />
                          <span className={`text-[11px] ${isSelected ? 'font-bold text-white' : 'font-medium'}`}>
                            {cfg.label}
                          </span>
                        </div>
                        <span className={`text-[11px] font-mono px-1.5 py-0.5 rounded ${
                          isSelected ? 'bg-slate-700 text-white font-bold' : 'text-slate-400'
                        }`}>
                          {count}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Reference-Style Gradient Legend Bar (Bottom Right Floating Panel) */}
              <div className="absolute bottom-6 right-4 z-10 w-64 bg-[#0f172a]/90 backdrop-blur-md border border-slate-700/80 rounded-xl px-4 py-3 shadow-2xl">
                <div className="flex items-center justify-between text-xs font-black mb-1.5">
                  <span className="text-red-500 tracking-wider">HOT</span>
                  <span className="text-indigo-300 tracking-wider">COOL</span>
                </div>
                <div
                  className="w-full h-3.5 rounded-md border border-white/20 shadow-inner"
                  style={{
                    background: 'linear-gradient(to right, #7f1d1d 0%, #b91c1c 15%, #ea580c 35%, #facc15 65%, #38bdf8 85%, #818cf8 100%)'
                  }}
                />
                <div className="text-[9px] text-slate-400 uppercase tracking-widest text-center mt-2 font-semibold">
                  REPRESENTATIONAL PURPOSE ONLY
                </div>
              </div>
            </div>

            {/* Monitored Events Side Panel (Right) */}
            <div className={`bg-[#0f172a]/95 backdrop-blur-md border-l border-slate-800 transition-all duration-300 flex flex-col ${
              isPanelOpen ? 'w-[360px]' : 'w-0'
            } overflow-hidden shrink-0 h-full min-h-0 z-20`}>
              {/* Header */}
              <div className="p-3 border-b border-slate-800 flex items-center justify-between shrink-0">
                <h3 className="text-xs font-bold text-white flex items-center gap-2 uppercase tracking-wide">
                  <Eye className="w-4 h-4 text-indigo-400" />
                  Monitored Events ({filteredEvents.length})
                </h3>
                <button
                  onClick={() => setIsPanelOpen(false)}
                  className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              {/* Search Box & Priority Filter Tabs */}
              <div className="p-3 border-b border-slate-800/80 flex flex-col gap-2.5 shrink-0 bg-[#0c1322]">
                {/* Search Box */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
                  <input
                    type="text"
                    value={sideSearchQuery}
                    onChange={(e) => setSideSearchQuery(e.target.value)}
                    placeholder="Filter by ID, location, type..."
                    className="w-full bg-slate-800/90 border border-slate-700/80 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-indigo-500 transition-colors"
                  />
                  {sideSearchQuery && (
                    <button
                      onClick={() => setSideSearchQuery('')}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-white"
                    >
                      ✕
                    </button>
                  )}
                </div>

                {/* Filter Tabs (All / High / Medium / Low) */}
                <div className="flex items-center gap-1 bg-slate-900/90 p-1 rounded-lg border border-slate-800">
                  {['All', 'High', 'Medium', 'Low'].map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setTabFilter(tab)}
                      className={`flex-1 py-1 text-[11px] font-semibold rounded-md transition-all ${
                        tabFilter === tab
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                      }`}
                    >
                      {tab}
                    </button>
                  ))}
                </div>
              </div>

              {/* Events List */}
              <div className="flex-1 overflow-y-auto min-h-0 divide-y divide-slate-800/60">
                {isLoading ? (
                  <div className="p-8 text-center">
                    <div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin mx-auto"></div>
                    <p className="text-xs text-slate-400 mt-3 font-medium">Loading events...</p>
                  </div>
                ) : filteredEvents.length === 0 ? (
                  <div className="p-8 text-center">
                    <Radio className="w-8 h-8 text-slate-600 mx-auto mb-2" />
                    <p className="text-xs font-semibold text-slate-300">No thermal events match filter</p>
                    <p className="text-[11px] text-slate-500 mt-1">Try clearing your search or priority filter</p>
                    {(priorityFilter !== 'All' || tabFilter !== 'All' || sideSearchQuery) && (
                      <button
                        onClick={() => { setPriorityFilter('All'); setTabFilter('All'); setSideSearchQuery(''); }}
                        className="mt-3 px-3 py-1 bg-slate-800 border border-slate-700 rounded-lg text-xs font-semibold text-indigo-400 hover:text-white transition-colors"
                      >
                        Reset All Filters
                      </button>
                    )}
                  </div>
                ) : (
                  filteredEvents.map(event => {
                    const cfg = PRIORITY_CONFIG[event.priority] || PRIORITY_CONFIG['Monitor'];
                    const isSelected = selectedEvent?.event_id === event.event_id;
                    const isHovered = hoveredEventId === event.event_id;
                    const riskVal = event.risk_index != null ? Math.round(event.risk_index) : 50;

                    return (
                      <div
                        key={event.event_id}
                        onClick={() => flyToEvent(event)}
                        onMouseEnter={() => setHoveredEventId(event.event_id)}
                        onMouseLeave={() => setHoveredEventId(null)}
                        className={`p-3 cursor-pointer transition-all border-l-4 ${
                          isSelected
                            ? 'bg-slate-800/90 border-indigo-500 shadow-md'
                            : isHovered
                              ? 'bg-slate-800/50 border-slate-600'
                              : 'bg-transparent border-transparent hover:bg-slate-800/40'
                        }`}
                      >
                        {/* Row 1: Event ID + Priority Badge */}
                        <div className="flex items-center justify-between mb-1.5">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold font-mono text-white tracking-wide">
                              {event.event_id}
                            </span>
                          </div>
                          <span
                            className="text-[10px] font-extrabold px-2 py-0.5 rounded border"
                            style={{
                              background: `${cfg.color}18`,
                              borderColor: `${cfg.color}40`,
                              color: cfg.color
                            }}
                          >
                            {event.priority}
                          </span>
                        </div>

                        {/* Row 2: Type + Location */}
                        <div className="mb-2">
                          <p className="text-[12px] font-bold text-slate-200 truncate leading-tight">
                            {event.classification || 'Thermal Anomaly'}
                          </p>
                          <p className="text-[11px] text-slate-400 truncate flex items-center gap-1 mt-0.5 font-medium">
                            <MapPin className="w-3 h-3 text-slate-500 shrink-0" />
                            {event.location || 'India Sector'}
                          </p>
                        </div>

                        {/* Row 3: Risk Bar, FRP with ▲/▼, Right-Aligned Time */}
                        <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[11px]">
                          {/* Risk Bar */}
                          <div className="flex items-center gap-1.5">
                            <span className="text-[10px] font-semibold text-slate-400">Risk:</span>
                            <div className="w-14 h-1.5 bg-slate-800 rounded-full overflow-hidden border border-slate-700/80">
                              <div
                                className="h-full rounded-full transition-all duration-500"
                                style={{
                                  width: `${Math.min(100, Math.max(5, riskVal))}%`,
                                  background: riskVal >= 75 ? '#ef4444' : riskVal >= 50 ? '#f97316' : riskVal >= 25 ? '#eab308' : '#3b82f6'
                                }}
                              />
                            </div>
                            <span className="text-[10px] font-bold font-mono text-slate-200">{riskVal}</span>
                          </div>

                          {/* FRP Indicator */}
                          <div className="flex items-center gap-1 font-mono text-[11px]">
                            <span className="text-[10px] text-slate-400">FRP:</span>
                            {event.frp_change_pct != null ? (
                              <span className={`font-bold flex items-center ${
                                event.frp_change_pct > 0 ? 'text-red-400' : 'text-emerald-400'
                              }`}>
                                {event.frp_change_pct > 0 ? (
                                  <TrendingUp className="w-3 h-3 mr-0.5 inline" />
                                ) : (
                                  <TrendingDown className="w-3 h-3 mr-0.5 inline" />
                                )}
                                {event.frp_change_pct > 0 ? `+${event.frp_change_pct.toFixed(0)}%` : `${event.frp_change_pct.toFixed(0)}%`}
                              </span>
                            ) : (
                              <span className="text-slate-500">--</span>
                            )}
                          </div>

                          {/* Time / Date */}
                          <div className="text-[10px] text-slate-400 font-medium flex items-center gap-1">
                            <Clock className="w-3 h-3 text-slate-500" />
                            <span>{formatEventTime(event.last_seen)}</span>
                          </div>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Side Panel Toggle Button (when closed) */}
            {!isPanelOpen && (
              <button
                onClick={() => setIsPanelOpen(true)}
                className="absolute right-0 top-1/2 -translate-y-1/2 bg-[#0f172a] border border-slate-700 border-r-0 rounded-l-lg p-2.5 z-20 hover:bg-slate-800 transition-colors shadow-xl text-indigo-400"
                title="Open Monitored Events Panel"
              >
                <Eye className="w-5 h-5" />
              </button>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
