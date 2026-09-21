'use client';

import React, { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { Layers, ChevronDown, Plus, Minus, Compass, Crosshair } from 'lucide-react';
import { EventItem } from '../lib/types';

interface LiveEventMapProps {
  events: EventItem[];
  selectedEventId: string | null;
  onSelectEvent: (eventId: string) => void;
  filterType: string;
  onFilterChange: (type: string) => void;
  timeRange: string;
  onTimeRangeChange: (range: string) => void;
  dataMode: string;
  onDataModeChange: (mode: string) => void;
}

export const LiveEventMap: React.FC<LiveEventMapProps> = ({
  events,
  selectedEventId,
  onSelectEvent,
  filterType,
  onFilterChange,
  timeRange,
  onTimeRangeChange,
  dataMode,
  onDataModeChange,
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<any>(null);
  const markersRef = useRef<{ [id: string]: any }>({});
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    if (!mapContainer.current || mapInstance.current) return;

    // Dynamically import MapLibre GL JS to prevent SSR issues
    import('maplibre-gl').then((maplibregl) => {
      const map = new maplibregl.Map({
        container: mapContainer.current!,
        style: {
          version: 8,
          sources: {
            'esri-satellite': {
              type: 'raster',
              tiles: [
                'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
              ],
              tileSize: 256,
              attribution: '&copy; Esri &mdash; Earthstar Geographics',
            },
            'carto-labels': {
              type: 'raster',
              tiles: [
                'https://cartodb-basemaps-a.global.ssl.fastly.net/light_only_labels/{z}/{x}/{y}.png',
              ],
              tileSize: 256,
            }
          },
          layers: [
            {
              id: 'satellite-layer',
              type: 'raster',
              source: 'esri-satellite',
              minzoom: 0,
              maxzoom: 18,
            },
            {
              id: 'labels-layer',
              type: 'raster',
              source: 'carto-labels',
              minzoom: 3,
              maxzoom: 18,
            }
          ],
        },
        center: [78.9629, 21.5937], // Centered on India
        zoom: 4.4,
        maxZoom: 15,
        minZoom: 3.5,
        attributionControl: false,
      });

      map.on('load', () => {
        setMapLoaded(true);
      });

      mapInstance.current = map;
    });

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, []);

  // Update Markers when events change
  useEffect(() => {
    if (!mapLoaded || !mapInstance.current) return;

    import('maplibre-gl').then((maplibregl) => {
      // Clear existing markers
      Object.values(markersRef.current).forEach((m: any) => m.remove());
      markersRef.current = {};

      events.forEach((ev) => {
        const isSelected = ev.event_id === selectedEventId;
        const el = document.createElement('div');
        el.className = 'cursor-pointer transform transition-transform hover:scale-125';

        let markerColor = '#16A34A'; // Low (green)
        let ringColor = '#86EFAC';
        if (ev.priority === 'Critical' || ev.priority === 'High') {
          markerColor = '#DC2626'; // High (red)
          ringColor = '#FECACA';
        } else if (ev.priority === 'Medium') {
          markerColor = '#EA580C'; // Medium (orange)
          ringColor = '#FED7AA';
        } else if (ev.status === 'Needs Verification' || ev.status === 'Under Verification') {
          markerColor = '#2563EB'; // Blue
          ringColor = '#BFDBFE';
        }

        el.innerHTML = `
          <div style="
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            width: ${isSelected ? '28px' : '20px'};
            height: ${isSelected ? '28px' : '20px'};
          ">
            <div style="
              position: absolute;
              width: 100%;
              height: 100%;
              border-radius: 9999px;
              background-color: ${ringColor};
              opacity: 0.6;
              animation: ${isSelected ? 'ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite' : 'none'};
            "></div>
            <div style="
              width: ${isSelected ? '16px' : '12px'};
              height: ${isSelected ? '16px' : '12px'};
              border-radius: 9999px;
              background-color: ${markerColor};
              border: 2px solid #FFFFFF;
              box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            "></div>
          </div>
        `;

        el.addEventListener('click', () => {
          onSelectEvent(ev.event_id);
        });

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([ev.longitude, ev.latitude])
          .addTo(mapInstance.current);

        markersRef.current[ev.event_id] = marker;
      });

      // Fly to selected event if selected
      const selected = events.find((e) => e.event_id === selectedEventId);
      if (selected && mapInstance.current) {
        mapInstance.current.flyTo({
          center: [selected.longitude, selected.latitude],
          zoom: 5.5,
          speed: 1.2,
        });
      }
    });
  }, [events, selectedEventId, mapLoaded]);

  const selectedEvent = events.find((e) => e.event_id === selectedEventId);

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs flex flex-col h-[480px] relative">
      {/* Map Header Controls */}
      <div className="px-4 py-2.5 border-b border-slate-100 flex items-center justify-between z-10 bg-white/95 backdrop-blur-xs">
        <div>
          <h2 className="text-xs font-bold text-slate-900 leading-tight">Live Event Map</h2>
          <p className="text-[10px] text-slate-500">Satellite thermal events across India</p>
        </div>

        <div className="flex items-center gap-2">
          {/* Filter Dropdown */}
          <div className="relative">
            <select
              value={filterType}
              onChange={(e) => onFilterChange(e.target.value)}
              className="appearance-none bg-slate-50 border border-slate-200 rounded-md text-[11px] font-medium text-slate-700 py-1 pl-2.5 pr-6 cursor-pointer focus:outline-none focus:ring-1 focus:ring-slate-300"
            >
              <option>All Events</option>
              <option>High Priority Only</option>
              <option>Industrial Hypotheses</option>
              <option>Under Verification</option>
            </select>
            <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>



          {/* Time Range */}
          <div className="relative">
            <select
              value={timeRange}
              onChange={(e) => onTimeRangeChange(e.target.value)}
              className="appearance-none bg-slate-50 border border-slate-200 rounded-md text-[11px] font-medium text-slate-700 py-1 pl-2.5 pr-6 cursor-pointer focus:outline-none focus:ring-1 focus:ring-slate-300"
            >
              <option>Last 7 Days</option>
              <option>Last 24 Hours</option>
              <option>Last 30 Days</option>
            </select>
            <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
          </div>

          {/* Layers button */}
          <button className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-50/80 hover:bg-slate-100 border border-slate-200 rounded-lg text-[11px] font-semibold text-slate-700 transition-all shadow-sm">
            <Layers className="w-3 h-3 text-indigo-600" />
            <span>Layers</span>
          </button>
        </div>
      </div>

      {/* Map Container */}
      <div className="flex-1 w-full relative bg-slate-100">
        <div ref={mapContainer} className="w-full h-full" />

        {/* Selected Event Popup Card Overlay */}
        {selectedEvent && (
          <Link
            href={`/live-map/${selectedEvent.event_id}`}
            className="absolute top-4 left-1/2 transform -translate-x-1/2 z-20 bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-xl p-3.5 shadow-glass w-72 cursor-pointer hover:border-indigo-300 hover:shadow-card-hover transition-all block"
            title="Click to open this event in full Live Map"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                  <span className="text-indigo-600 font-mono">{selectedEvent.event_id}</span>
                </div>
                <div className="text-[11px] text-slate-700 font-semibold leading-tight mt-0.5 line-clamp-1">
                  {selectedEvent.title}
                </div>
              </div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full shrink-0 ${
                selectedEvent.priority === 'High' || selectedEvent.priority === 'Critical'
                  ? 'bg-red-50 text-red-600 border border-red-200/80'
                  : 'bg-amber-50 text-amber-700 border border-amber-200/80'
              }`}>
                {selectedEvent.priority} Priority
              </span>
            </div>
            <div className="mt-2 text-[10px] text-slate-500 border-t border-slate-100 pt-2 flex items-center justify-between font-mono">
              <span>LAT {selectedEvent.latitude != null ? selectedEvent.latitude.toFixed(2) : '--'}°</span>
              <span>LON {selectedEvent.longitude != null ? selectedEvent.longitude.toFixed(2) : '--'}°</span>
              <span className="text-indigo-600 font-sans font-semibold">{selectedEvent.observations_count} obs</span>
            </div>
          </Link>
        )}

        {/* Map Legend (Bottom Left) */}
        <div className="absolute bottom-3 left-3 bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-xl p-2.5 shadow-sm text-[10px] space-y-1.5 z-10">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-600 ring-2 ring-red-100"></span>
            <span className="font-semibold text-slate-700">High Priority</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500 ring-2 ring-orange-100"></span>
            <span className="font-semibold text-slate-700">Medium Priority</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 ring-2 ring-emerald-100"></span>
            <span className="font-semibold text-slate-700">Low Priority</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-indigo-600 ring-2 ring-indigo-100"></span>
            <span className="font-semibold text-slate-700">Under Verification</span>
          </div>
        </div>

        {/* Map Scale Bar (Bottom Right) */}
        <div className="absolute bottom-3 right-12 bg-white/90 backdrop-blur-md border border-slate-200 rounded-md px-2 py-0.5 shadow-sm text-[9px] font-bold text-slate-600 z-10">
          500 km
        </div>

        {/* Zoom Controls (Bottom Right) */}
        <div className="absolute bottom-3 right-3 flex flex-col gap-1 z-10">
          <button
            onClick={() => mapInstance.current?.zoomIn()}
            className="w-7 h-7 bg-white hover:bg-slate-50 border border-slate-200/90 rounded-lg flex items-center justify-center text-slate-700 shadow-sm transition-colors"
            title="Zoom In"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => mapInstance.current?.zoomOut()}
            className="w-7 h-7 bg-white hover:bg-slate-50 border border-slate-200/90 rounded-lg flex items-center justify-center text-slate-700 shadow-sm transition-colors"
            title="Zoom Out"
          >
            <Minus className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => mapInstance.current?.flyTo({ center: [78.9629, 21.5937], zoom: 4.4 })}
            className="w-7 h-7 bg-white hover:bg-slate-50 border border-slate-200/90 rounded-lg flex items-center justify-center text-slate-700 shadow-sm transition-colors"
            title="Reset View"
          >
            <Crosshair className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
