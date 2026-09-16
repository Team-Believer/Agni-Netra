'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { fetchEvents } from '../../lib/api';
import { EventItem } from '../../lib/types';

export default function LiveMapPage() {
  const [currentTab, setCurrentTab] = useState('live-map');
  const [searchQuery, setSearchQuery] = useState('');
  const [events, setEvents] = useState<EventItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);

  const mapToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN;

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const data = await fetchEvents({ search: searchQuery });
        setEvents(data);
      } catch (err) {
        console.error("Failed to load events for map", err);
      } finally {
        setIsLoading(false);
      }
    };
    loadEvents();
  }, [searchQuery]);

  useEffect(() => {
    if (!mapToken) return;
    if (map.current) return; // Initialize map only once
    if (!mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: `https://api.mapbox.com/styles/v1/mapbox/dark-v11/tiles/256/{z}/{x}/{y}@2x?access_token=${mapToken}`,
      center: [78.9629, 20.5937], // India center
      zoom: 4,
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
  }, [mapToken]);

  // Update markers when events change
  useEffect(() => {
    if (!map.current) return;

    // Remove existing markers (clean up by removing all elements with a specific class)
    const existingMarkers = document.querySelectorAll('.custom-map-marker');
    existingMarkers.forEach(el => el.remove());

    events.forEach(event => {
      // Create custom marker element
      const el = document.createElement('div');
      el.className = 'custom-map-marker';
      
      const priorityColors: Record<string, string> = {
        'Critical': '#ef4444',
        'High': '#f97316',
        'Medium': '#eab308',
        'Low': '#3b82f6',
        'Monitor': '#64748b'
      };
      
      const color = priorityColors[event.priority] || '#64748b';
      
      el.style.backgroundColor = color;
      el.style.width = '12px';
      el.style.height = '12px';
      el.style.borderRadius = '50%';
      el.style.border = '2px solid white';
      el.style.boxShadow = '0 0 4px rgba(0,0,0,0.3)';
      el.style.cursor = 'pointer';

      // Create popup
      const popup = new maplibregl.Popup({ offset: 25 }).setHTML(
        `<div class="p-2">
          <div class="text-xs text-slate-500 font-bold mb-1">${event.event_id}</div>
          <h3 class="text-sm font-semibold text-slate-800 mb-1">${event.classification}</h3>
          <div class="text-xs mb-2">
            <span class="font-semibold" style="color: ${color}">${event.priority} Priority</span>
          </div>
          <div class="text-[10px] text-slate-500 mb-2">
            Multi-Sensor Observations: ${event.observations_count}<br/>
            Lat: ${event.latitude.toFixed(2)}, Lon: ${event.longitude.toFixed(2)}<br/>
            Last observed: ${new Date(event.last_seen || Date.now()).toLocaleString()}
          </div>
          <a href="/events/${event.event_id}" class="text-xs text-blue-600 hover:underline">View Details →</a>
        </div>`
      );

      // Add to map
      new maplibregl.Marker({ element: el })
        .setLngLat([event.longitude, event.latitude])
        .setPopup(popup)
        .addTo(map.current!);
    });
  }, [events]);

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 overflow-y-auto max-w-[1720px] mx-auto w-full flex flex-col">
          <div className="mb-6 flex items-center justify-between border-b border-slate-200 pb-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900">Live Map</h1>
              <p className="text-sm text-slate-500 mt-1">Real-time geographical thermal monitoring</p>
            </div>
          </div>

          <div className="flex-1 relative bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs min-h-[600px]">
            {!mapToken ? (
              <div className="absolute inset-0 flex items-center justify-center bg-slate-100 z-10">
                <div className="text-center">
                  <p className="text-slate-600 font-medium">Map provider is not configured.</p>
                  <p className="text-xs text-slate-400 mt-2">Please set NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN.</p>
                </div>
              </div>
            ) : (
              <div ref={mapContainer} className="w-full h-full absolute inset-0" />
            )}

            {!isLoading && events.length === 0 && mapToken && (
              <div className="absolute inset-0 flex items-center justify-center bg-white/70 backdrop-blur-sm z-10 pointer-events-none">
                <div className="bg-white p-6 rounded-xl shadow-lg border border-slate-200 text-center">
                  <h3 className="text-lg font-bold text-slate-800">No real thermal events available.</h3>
                  <p className="text-sm text-slate-500 mt-2 max-w-sm">
                    The live map currently has no active real data to display. Ensure satellite data ingestion is active.
                  </p>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
