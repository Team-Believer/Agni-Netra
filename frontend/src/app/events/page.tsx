'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { Flame, ShieldAlert, CheckCircle, Clock, ChevronRight, Activity, Calendar } from 'lucide-react';
import Link from 'next/link';
import { fetchEvents } from '../../lib/api';
import { EventItem } from '../../lib/types';
import { formatDistanceToNow } from 'date-fns';

export default function EventsPage() {
  const [currentTab, setCurrentTab] = useState('events');
  const [searchQuery, setSearchQuery] = useState('');
  const [events, setEvents] = useState<EventItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState('All');
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [dataModeFilter, setDataModeFilter] = useState('All');

  useEffect(() => {
    const loadEvents = async () => {
      setIsLoading(true);
      try {
        const data = await fetchEvents({
          status: statusFilter !== 'All' ? statusFilter : undefined,
          priority: priorityFilter !== 'All' ? priorityFilter : undefined,
          search: searchQuery || undefined,
          data_mode: dataModeFilter !== 'All' ? dataModeFilter : undefined
        });
        setEvents(data);
      } catch (err) {
        console.error('Failed to fetch events:', err);
      } finally {
        setIsLoading(false);
      }
    };
    
    // Add small debounce for search
    const timer = setTimeout(loadEvents, 300);
    return () => clearTimeout(timer);
  }, [statusFilter, priorityFilter, searchQuery, dataModeFilter]);

  const getPriorityColor = (prio: string) => {
    if (prio === 'Critical') return 'bg-red-500/20 text-red-700 border-red-200';
    if (prio === 'High') return 'bg-orange-500/20 text-orange-700 border-orange-200';
    if (prio === 'Medium') return 'bg-amber-500/20 text-amber-700 border-amber-200';
    return 'bg-blue-500/20 text-blue-700 border-blue-200';
  };

  const getStatusIcon = (status: string) => {
    if (status === 'Verified Active') return <CheckCircle className="w-3.5 h-3.5 text-green-600" />;
    if (status === 'Needs Verification' || status === 'Under Verification') return <Clock className="w-3.5 h-3.5 text-amber-500" />;
    return <Activity className="w-3.5 h-3.5 text-slate-400" />;
  };

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 overflow-y-auto max-w-[1720px] mx-auto w-full flex flex-col">
          <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between border-b border-slate-200 pb-4 gap-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900">Events Directory</h1>
              <p className="text-sm text-slate-500 mt-1">Comprehensive list of all tracked thermal anomalies</p>
            </div>
            
            <div className="flex items-center gap-3">
              <select 
                value={priorityFilter} 
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="bg-white border border-slate-300 rounded-lg py-1.5 px-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="All">All Priorities</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>

              <select 
                value={statusFilter} 
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-white border border-slate-300 rounded-lg py-1.5 px-3 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="All">All Statuses</option>
                <option value="Needs Verification">Needs Verification</option>
                <option value="Under Verification">Under Verification</option>
                <option value="Verified Active">Verified Active</option>
                <option value="Verified False Alarm">Verified False Alarm</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>
          </div>

          <div className="flex-1 bg-white border border-slate-200 rounded-xl shadow-xs flex flex-col overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Event ID</th>
                    <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Location</th>
                    <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Priority</th>
                    <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Classification</th>
                    <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Last Observed</th>
                    <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {isLoading ? (
                    <tr>
                      <td colSpan={7} className="px-6 py-12 text-center text-slate-500">Loading events...</td>
                    </tr>
                  ) : events.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                        <ShieldAlert className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                        No events found matching current filters.
                      </td>
                    </tr>
                  ) : (
                    events.map(event => (
                      <tr key={event.event_id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-mono text-sm font-semibold text-slate-900">{event.event_id}</div>
                          <div className="text-xs text-slate-500">{event.current_state}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-slate-900">{event.location || 'Unknown Location'}</div>
                          <div className="text-xs text-slate-500">{event.district || 'Unknown District'}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${getPriorityColor(event.priority)}`}>
                            {event.priority}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-1.5 text-sm font-medium text-slate-700">
                            {getStatusIcon(event.verification_status)}
                            {event.verification_status}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-slate-700 flex items-center gap-1.5">
                            <Flame className="w-3.5 h-3.5 text-red-500" />
                            {event.classification || 'Unclassified'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 flex items-center gap-1.5">
                          <Calendar className="w-3.5 h-3.5" />
                          {event.last_observed ? formatDistanceToNow(new Date(event.last_observed), { addSuffix: true }) : 'Unknown'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <Link href={`/events/${event.event_id}`} className="inline-flex items-center gap-1 text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg">
                            View Details <ChevronRight className="w-4 h-4" />
                          </Link>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
