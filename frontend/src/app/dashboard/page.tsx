'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { KpiCards } from '../../components/KpiCards';
import { LiveEventMap } from '../../components/LiveEventMap';
import { RecentEventsTable } from '../../components/RecentEventsTable';
import { UnderVerificationQueue } from '../../components/UnderVerificationQueue';
import { EventDetailPanel } from '../../components/EventDetailPanel';
import { EventItem, EventDetail, DashboardSummary, TimelinePoint } from '../../lib/types';
import { fetchDashboardSummary, fetchEvents, fetchEventDetail, fetchEventTimeline } from '../../lib/api';

export default function DashboardPage() {
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

  // Load summary and events on mount
  const loadData = async () => {
    try {
      const [sumData, evsData] = await Promise.all([
        fetchDashboardSummary(),
        fetchEvents({ search: searchQuery, data_mode: dataMode !== 'All' ? dataMode : undefined }),
      ]);
      setSummary(sumData);
      setEvents(evsData);

      // If selectedEventId exists, load its detail
      let targetId = selectedEventId;
      if (!targetId && evsData.length > 0) {
        const jamnagarEvent = evsData.find(e => e.event_id === 'EVENT-SEED-005');
        targetId = jamnagarEvent ? jamnagarEvent.event_id : evsData[0].event_id;
      }

      if (targetId) {
        if (!selectedEventId) {
          setSelectedEventId(targetId);
        }
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
  };

  useEffect(() => {
    loadData();
  }, [searchQuery, dataMode]);

  // When selected event changes
  const handleSelectEvent = async (eventId: string) => {
    setSelectedEventId(eventId);
    const [det, tl] = await Promise.all([
      fetchEventDetail(eventId),
      fetchEventTimeline(eventId),
    ]);
    setSelectedEventDetail(det);
    setTimeline(tl);
  };

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

          {/* 2-Column Grid: Left (Map + Recent Events Table) vs Right (Event Detail Panel) */}
          <div className="grid grid-cols-12 gap-5">
            {/* Left Main (7 of 12 columns) */}
            <div className="col-span-12 lg:col-span-7 flex flex-col">
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
                  onSelectEvent={handleSelectEvent}
                />
              </div>
              <RecentEventsTable
                events={filteredEvents}
                selectedEventId={selectedEventId}
                onSelectEvent={handleSelectEvent}
              />
            </div>

            {/* Right Panel (5 of 12 columns) */}
            <div className="col-span-12 lg:col-span-5">
              <EventDetailPanel
                event={selectedEventDetail}
                timeline={timeline}
                onEventUpdated={loadData}
              />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
