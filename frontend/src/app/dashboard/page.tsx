'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { KpiCards } from '../../components/KpiCards';
import { LiveEventMap } from '../../components/LiveEventMap';
import { RecentEventsTable } from '../../components/RecentEventsTable';
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

  // Load summary and events on mount
  const loadData = async () => {
    try {
      const [sumData, evsData] = await Promise.all([
        fetchDashboardSummary(),
        fetchEvents({ search: searchQuery }),
      ]);
      setSummary(sumData);
      setEvents(evsData);

      // If selectedEventId exists, load its detail
      const targetId = selectedEventId || (evsData.length > 0 ? evsData[0].event_id : '');
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
  }, [searchQuery]);

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
                events={events}
                selectedEventId={selectedEventId}
                onSelectEvent={handleSelectEvent}
              />
              <RecentEventsTable
                events={events}
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
