'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { Calendar, Search, Database, ShieldAlert, CheckCircle, Clock, Activity, ChevronRight, Flame } from 'lucide-react';
import Link from 'next/link';
import { fetchEvents } from '../../lib/api';
import { EventItem } from '../../lib/types';
import { formatDistanceToNow } from 'date-fns';

export default function HistoricalPage() {
  const [currentTab, setCurrentTab] = useState('historical');
  const [searchQuery, setSearchQuery] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [events, setEvents] = useState<EventItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasQueried, setHasQueried] = useState(false);

  const handleQuery = async () => {
    setIsLoading(true);
    setHasQueried(true);
    try {
      const data = await fetchEvents({
        search: searchQuery || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        data_mode: 'All'
      });
      setEvents(data);
    } catch (err) {
      console.error('Failed to fetch historical events:', err);
    } finally {
      setIsLoading(false);
    }
  };

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
    <div className="h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 overflow-y-auto max-w-[1720px] mx-auto w-full flex flex-col">
          <div className="mb-6 flex items-center justify-between border-b border-slate-200 pb-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900">Historical Analysis</h1>
              <p className="text-sm text-slate-500 mt-1">Query past thermal events, footprint expansions, and FRP baseline deviations</p>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs mb-6">
            <h2 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
              <Search className="w-4 h-4 text-blue-600" /> Query Parameters
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Start Date</label>
                <div className="relative">
                  <input 
                    type="date" 
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg py-2 pl-3 pr-4 text-sm text-slate-700 focus:outline-none focus:border-blue-500" 
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">End Date</label>
                <div className="relative">
                  <input 
                    type="date" 
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg py-2 pl-3 pr-4 text-sm text-slate-700 focus:outline-none focus:border-blue-500" 
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Facility / District</label>
                <input 
                  type="text" 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="e.g. Jamnagar Refinery"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm text-slate-700 focus:outline-none focus:border-blue-500 placeholder-slate-400" 
                />
              </div>

              <button 
                onClick={handleQuery}
                disabled={isLoading}
                className="bg-slate-900 text-white font-semibold py-2 px-4 rounded-lg text-sm hover:bg-slate-800 transition-colors h-[38px] disabled:opacity-50"
              >
                {isLoading ? 'Querying...' : 'Run Query'}
              </button>
            </div>
          </div>

          {!hasQueried ? (
            <div className="flex-1 bg-white border border-slate-200 rounded-xl p-10 flex flex-col items-center justify-center text-center shadow-xs">
              <Database className="w-12 h-12 text-slate-300 mb-4" />
              <h3 className="text-lg font-bold text-slate-800">Historical Query Builder</h3>
              <p className="text-sm text-slate-500 mt-2 max-w-md">
                Enter parameters above to search through the historical thermal archive.
              </p>
            </div>
          ) : events.length === 0 ? (
            <div className="flex-1 bg-white border border-slate-200 rounded-xl p-10 flex flex-col items-center justify-center text-center shadow-xs">
              <Database className="w-12 h-12 text-slate-300 mb-4" />
              <h3 className="text-lg font-bold text-slate-800">No Historical Data Found</h3>
              <p className="text-sm text-slate-500 mt-2 max-w-md">
                There is currently no data available for the selected timeframe and filters.
              </p>
            </div>
          ) : (
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
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">First Seen</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {events.map(event => (
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
                            {getStatusIcon(event.status)}
                            {event.status}
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
                          {event.first_seen ? new Date(event.first_seen).toLocaleDateString() : 'Unknown'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <Link href={`/events/${event.event_id}`} className="inline-flex items-center gap-1 text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg">
                            View Details <ChevronRight className="w-4 h-4" />
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
