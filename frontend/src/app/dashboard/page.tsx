'use client';

import React, { useState, useEffect, Suspense, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { KpiCards } from '../../components/KpiCards';
import { LiveEventMap } from '../../components/LiveEventMap';
import { RecentEventsTable } from '../../components/RecentEventsTable';
import { UnderVerificationQueue } from '../../components/UnderVerificationQueue';
import { EventDetailPanel } from '../../components/EventDetailPanel';
import { EventItem, EventDetail, DashboardSummary, TimelinePoint } from '../../lib/types';
import { fetchDashboardSummary, fetchEvents, fetchEventDetail, fetchEventTimeline } from '../../lib/api';

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const urlEventId = searchParams ? searchParams.get('eventId') : null;

  const [currentTab, setCurrentTab] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string>('');
  const [selectedEventDetail, setSelectedEventDetail] = useState<EventDetail | null>(null);
  const [timeline, setTimeline] = useState<TimelinePoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterType, setFilterType] = useState('All Events');
  const [timeRange, setTimeRange] = useState('Last 7 Days');
  const [dataMode, setDataMode] = useState('SEED');

  const filteredEvents = React.useMemo(() => {
    let filtered = events;
    
    // Status / Priority filter
    if (filterType === 'High Priority Only') {
      filtered = filtered.filter(e => e.priority === 'High' || e.priority === 'Critical');
    } else if (filterType === 'Under Verification') {
      filtered = filtered.filter(e => e.status === 'Needs Verification' || e.status === 'Under Verification');
    } else if (filterType === 'Industrial Hypotheses') {
      filtered = filtered.filter(e => e.classification?.includes('Industrial') || e.classification?.includes('Factory'));
    }

    // Time filter
    const now = new Date();
    if (timeRange === 'Last 24 Hours') {
      filtered = filtered.filter(e => e.last_seen && (now.getTime() - new Date(e.last_seen).getTime() < 24 * 60 * 60 * 1000));
    } else if (timeRange === 'Last 7 Days') {
      filtered = filtered.filter(e => e.last_seen && (now.getTime() - new Date(e.last_seen).getTime() < 7 * 24 * 60 * 60 * 1000));
    }
    
    return filtered;
  }, [events, filterType, timeRange]);

  // Unified event selection handler for Map click, Table click, and URL sync
  const handleSelectEvent = useCallback(async (eventId: string) => {
    if (!eventId) return;
    setSelectedEventId(eventId);

    // Synchronize URL query parameter without full page reload
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href);
      if (url.searchParams.get('eventId') !== eventId) {
        url.searchParams.set('eventId', eventId);
        window.history.replaceState({}, '', url.toString());
      }
    }

    try {
      const [det, tl] = await Promise.all([
        fetchEventDetail(eventId),
        fetchEventTimeline(eventId),
      ]);
      setSelectedEventDetail(det);
      setTimeline(tl);
    } catch (err) {
      console.error('Error fetching event details for', eventId, err);
    }
  }, []);

  // Load summary and events on mount or filter change
  const loadData = useCallback(async () => {
    try {
      const [sumData, evsData] = await Promise.all([
        fetchDashboardSummary(),
        fetchEvents({ search: searchQuery, data_mode: dataMode !== 'All' ? dataMode : undefined }),
      ]);
      setSummary(sumData);
      setEvents(evsData);

      // Determine initial targetId: URL parameter has highest priority if found
      let currentParamEventId: string | null = null;
      if (typeof window !== 'undefined') {
        currentParamEventId = new URLSearchParams(window.location.search).get('eventId');
      }

      let targetId = '';
      if (currentParamEventId && evsData.length > 0) {
        const found = evsData.find(e => e.event_id === currentParamEventId);
        if (found) {
          targetId = found.event_id;
        }
      }

      // If no valid URL eventId, preserve existing selectedEventId or default to Jamnagar
      if (!targetId) {
        if (selectedEventId && evsData.some(e => e.event_id === selectedEventId)) {
          targetId = selectedEventId;
        } else if (evsData.length > 0) {
          const jamnagarEvent = evsData.find(e => e.event_id === 'EVENT-SEED-005');
          targetId = jamnagarEvent ? jamnagarEvent.event_id : evsData[0].event_id;
        }
      }

      if (targetId) {
        setSelectedEventId(targetId);
        const [det, tl] = await Promise.all([
          fetchEventDetail(targetId),
          fetchEventTimeline(targetId),
        ]);
        setSelectedEventDetail(det);
        setTimeline(tl);
      } else {
        setSelectedEventDetail(null);
        setTimeline([]);
      }
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, dataMode, selectedEventId]);

  useEffect(() => {
    loadData();
  }, [searchQuery, dataMode]);

  // Listen to browser popstate to synchronize back/forward navigation
  useEffect(() => {
    const handlePopState = () => {
      if (typeof window !== 'undefined') {
        const params = new URLSearchParams(window.location.search);
        const evId = params.get('eventId');
        if (evId && evId !== selectedEventId) {
          handleSelectEvent(evId);
        }
      }
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [selectedEventId, handleSelectEvent]);

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      {/* Top Bar */}
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      {/* Main App Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Navigation Sidebar */}
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        {/* Content Area */}
        <main className="flex-1 p-5 overflow-y-auto max-w-[1720px] mx-auto w-full">
          {/* Top KPI Metric Cards */}
          <KpiCards summary={summary} />

          {/* 2-Column Grid: Left (Map + Action Required) vs Right (Event Detail Panel) */}
          <div className="grid grid-cols-12 gap-5">
            {/* Left Main (7 of 12 columns) */}
            <div className="col-span-12 lg:col-span-7 flex flex-col min-w-0">
              <LiveEventMap
                events={filteredEvents}
                selectedEventId={selectedEventId}
                onSelectEvent={handleSelectEvent}
                filterType={filterType}
                onFilterChange={setFilterType}
                timeRange={timeRange}
                onTimeRangeChange={setTimeRange}
                dataMode={dataMode}
                onDataModeChange={setDataMode}
              />
              <div className="mt-4">
                <UnderVerificationQueue
                  events={filteredEvents}
                  selectedEvent={selectedEventDetail || filteredEvents.find(e => e.event_id === selectedEventId) || null}
                  onSelectEvent={handleSelectEvent}
                  onEventUpdated={loadData}
                />
              </div>
            </div>

            {/* Right Panel (5 of 12 columns) */}
            <div className="col-span-12 lg:col-span-5 min-w-0">
              <EventDetailPanel
                event={selectedEventDetail}
                timeline={timeline}
                onEventUpdated={loadData}
              />
            </div>
          </div>

          {/* Full-Width Recent Events Section (Spans Full Dashboard Width) */}
          <div className="w-full min-w-0 mt-5">
            <RecentEventsTable
              events={filteredEvents}
              selectedEventId={selectedEventId}
              onSelectEvent={handleSelectEvent}
            />
          </div>
        </main>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#F4F6F9] flex items-center justify-center text-slate-500 font-semibold">Loading Dashboard...</div>}>
      <DashboardContent />
    </Suspense>
  );
}
