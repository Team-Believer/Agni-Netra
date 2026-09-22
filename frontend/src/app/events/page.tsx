'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { 
  ShieldAlert, 
  ArrowRight, 
  Search, 
  X, 
  RotateCcw, 
  ArrowUpDown, 
  ChevronUp, 
  ChevronDown
} from 'lucide-react';
import Link from 'next/link';
import { fetchEvents } from '../../lib/api';
import { EventItem } from '../../lib/types';
import { formatDistanceToNow, format, parseISO, isValid } from 'date-fns';

type SortField = 'event_id' | 'location' | 'priority' | 'status' | 'classification' | 'last_observed';
type SortOrder = 'asc' | 'desc';

export default function EventsPage() {
  const [currentTab, setCurrentTab] = useState('events');
  const [globalSearchQuery, setGlobalSearchQuery] = useState('');
  const [localSearchQuery, setLocalSearchQuery] = useState('');
  
  const [allEvents, setAllEvents] = useState<EventItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [classificationFilter, setClassificationFilter] = useState('All');
  const [stateFilter, setStateFilter] = useState('All');

  // Sorting
  const [sortField, setSortField] = useState<SortField>('last_observed');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const loadEventsData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchEvents();
      setAllEvents(data || []);
    } catch (err: any) {
      console.error('Failed to fetch events:', err);
      setError(err?.message || 'Unable to retrieve event directory data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEventsData();
  }, []);

  // Compute live summary counts directly from the loaded dataset
  const metrics = useMemo(() => {
    const total = allEvents.length;
    const active = allEvents.filter(e => {
      const state = (e.behavior || '').toLowerCase();
      const status = (e.status || '').toLowerCase();
      return state !== 'resolved' && status !== 'resolved' && status !== 'verified false alarm';
    }).length;
    
    const highPriority = allEvents.filter(e => 
      e.priority === 'High' || e.priority === 'Critical'
    ).length;
    
    const underVerification = allEvents.filter(e => 
      e.status === 'Needs Verification' || e.status === 'Under Verification'
    ).length;

    return { total, active, highPriority, underVerification };
  }, [allEvents]);

  // Combined search term from global header or local search input
  const activeSearch = (localSearchQuery || globalSearchQuery).trim().toLowerCase();

  // Filter events client-side for immediate responsive experience
  const filteredEvents = useMemo(() => {
    return allEvents.filter(item => {
      if (activeSearch) {
        const idMatch = (item.event_id || '').toLowerCase().includes(activeSearch);
        const locMatch = (item.location || '').toLowerCase().includes(activeSearch);
        const distMatch = (item.district || '').toLowerCase().includes(activeSearch);
        const stateMatch = (item.state || '').toLowerCase().includes(activeSearch);
        const facMatch = (item.nearby_facility || '').toLowerCase().includes(activeSearch);
        const classMatch = (item.classification || '').toLowerCase().includes(activeSearch);
        const titleMatch = (item.title || '').toLowerCase().includes(activeSearch);
        if (!idMatch && !locMatch && !distMatch && !stateMatch && !facMatch && !classMatch && !titleMatch) {
          return false;
        }
      }

      if (priorityFilter !== 'All' && item.priority !== priorityFilter) {
        return false;
      }

      if (statusFilter !== 'All' && item.status !== statusFilter) {
        return false;
      }

      if (classificationFilter !== 'All' && item.classification !== classificationFilter) {
        return false;
      }

      if (stateFilter !== 'All' && (item.behavior || '') !== stateFilter) {
        return false;
      }

      return true;
    });
  }, [allEvents, activeSearch, priorityFilter, statusFilter, classificationFilter, stateFilter]);

  // Sort events
  const sortedEvents = useMemo(() => {
    const priorityWeight: Record<string, number> = {
      Critical: 4,
      High: 3,
      Medium: 2,
      Low: 1
    };

    return [...filteredEvents].sort((a, b) => {
      let comparison = 0;

      switch (sortField) {
        case 'event_id':
          comparison = (a.event_id || '').localeCompare(b.event_id || '');
          break;
        case 'location':
          comparison = (a.location || a.district || '').localeCompare(b.location || b.district || '');
          break;
        case 'priority':
          comparison = (priorityWeight[a.priority] || 0) - (priorityWeight[b.priority] || 0);
          break;
        case 'status':
          comparison = (a.status || '').localeCompare(b.status || '');
          break;
        case 'classification':
          comparison = (a.classification || '').localeCompare(b.classification || '');
          break;
        case 'last_observed': {
          const timeA = a.last_seen ? new Date(a.last_seen).getTime() : (a.first_seen ? new Date(a.first_seen).getTime() : 0);
          const timeB = b.last_seen ? new Date(b.last_seen).getTime() : (b.first_seen ? new Date(b.first_seen).getTime() : 0);
          comparison = timeA - timeB;
          break;
        }
        default:
          comparison = 0;
      }

      return sortOrder === 'asc' ? comparison : -comparison;
    });
  }, [filteredEvents, sortField, sortOrder]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const handleResetFilters = () => {
    setLocalSearchQuery('');
    setGlobalSearchQuery('');
    setPriorityFilter('All');
    setStatusFilter('All');
    setClassificationFilter('All');
    setStateFilter('All');
  };

  const hasActiveFilters = 
    Boolean(activeSearch) || 
    priorityFilter !== 'All' || 
    statusFilter !== 'All' || 
    classificationFilter !== 'All' || 
    stateFilter !== 'All';

  // Helper formatting functions (Clean, icon-free semantic tags)
  const getPriorityBadge = (prio: string) => {
    switch (prio) {
      case 'Critical':
        return (
          <span className="inline-flex items-center justify-center px-3 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200 shadow-2xs h-[28px] whitespace-nowrap">
            Critical
          </span>
        );
      case 'High':
        return (
          <span className="inline-flex items-center justify-center px-3 py-1 rounded-full text-xs font-semibold bg-orange-50 text-orange-700 border border-orange-200 shadow-2xs h-[28px] whitespace-nowrap">
            High
          </span>
        );
      case 'Medium':
        return (
          <span className="inline-flex items-center justify-center px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200 shadow-2xs h-[28px] whitespace-nowrap">
            Medium
          </span>
        );
      case 'Low':
      default:
        return (
          <span className="inline-flex items-center justify-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 shadow-2xs h-[28px] whitespace-nowrap">
            Low
          </span>
        );
    }
  };

  const getLifecycleStateDisplay = (behavior?: string) => {
    const b = (behavior || 'Active').trim();
    if (b === 'Escalating' || b === 'Sudden Spike') {
      return (
        <span className="text-sm font-semibold text-red-700 whitespace-nowrap">
          {b}
        </span>
      );
    }
    if (b === 'Spreading') {
      return (
        <span className="text-sm font-semibold text-orange-700 whitespace-nowrap">
          Spreading
        </span>
      );
    }
    if (b === 'Persistent' || b === 'Smoldering') {
      return (
        <span className="text-sm font-semibold text-amber-700 whitespace-nowrap">
          {b}
        </span>
      );
    }
    if (b === 'Declining' || b === 'Declined and Quenched') {
      return (
        <span className="text-sm font-semibold text-emerald-700 whitespace-nowrap">
          {b}
        </span>
      );
    }
    if (b === 'Resolved') {
      return (
        <span className="text-sm font-semibold text-slate-500 whitespace-nowrap">
          Resolved
        </span>
      );
    }
    return (
      <span className="text-sm font-semibold text-slate-900 whitespace-nowrap">
        {b || 'Active'}
      </span>
    );
  };

  const getVerificationStatusBadge = (status: string) => {
    switch (status) {
      case 'Verified Active':
      case 'Confirmed':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 whitespace-nowrap">
            Verified Active
          </span>
        );
      case 'Needs Verification':
      case 'Under Verification':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-800 border border-amber-200 whitespace-nowrap">
            {status}
          </span>
        );
      case 'Verified False Alarm':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600 border border-slate-200 whitespace-nowrap">
            False Alarm
          </span>
        );
      case 'Resolved':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-medium bg-slate-50 text-slate-600 border border-slate-200 whitespace-nowrap">
            Resolved
          </span>
        );
      case 'Monitoring':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-medium bg-blue-50 text-blue-700 border border-blue-200 whitespace-nowrap">
            Monitoring
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded text-[11px] font-medium bg-slate-50 text-slate-600 border border-slate-200 whitespace-nowrap">
            {status || 'Unverified'}
          </span>
        );
    }
  };

  const getClassificationTag = (classification: string) => {
    switch (classification) {
      case 'Forest Fire':
        return (
          <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 whitespace-nowrap">
            Forest Fire
          </span>
        );
      case 'Industrial Fire':
        return (
          <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-semibold text-red-800 bg-red-50 border border-red-200 whitespace-nowrap">
            Industrial Fire
          </span>
        );
      case 'Routine Flare':
        return (
          <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-semibold text-amber-800 bg-amber-50 border border-amber-200 whitespace-nowrap">
            Routine Flare
          </span>
        );
      case 'Agricultural Burn':
        return (
          <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-semibold text-lime-800 bg-lime-50 border border-lime-200 whitespace-nowrap">
            Agricultural Burn
          </span>
        );
      case 'Coal Mine Fire':
        return (
          <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-semibold text-stone-800 bg-stone-100 border border-stone-200 whitespace-nowrap">
            Coal Mine Fire
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium text-slate-700 bg-slate-50 border border-slate-200 whitespace-nowrap">
            {classification || 'Unknown'}
          </span>
        );
    }
  };

  const formatLastObserved = (dateStr?: string) => {
    if (!dateStr) {
      return {
        relative: 'Not recorded',
        exact: 'No timestamp available',
        isUnknown: true
      };
    }
    try {
      const parsed = parseISO(dateStr);
      if (!isValid(parsed)) {
        return { relative: 'Unknown', exact: dateStr, isUnknown: true };
      }
      const relative = formatDistanceToNow(parsed, { addSuffix: true });
      const exact = format(parsed, 'dd MMM yyyy • HH:mm:ss');
      return { relative, exact, isUnknown: false };
    } catch {
      return { relative: 'Unknown', exact: dateStr, isUnknown: true };
    }
  };

  const formatLocationHierarchy = (item: EventItem) => {
    const rawLoc = (item.location || '').trim();
    const district = (item.district || '').trim();
    const state = (item.state || '').trim();
    const facility = (item.nearby_facility || '').trim();

    let primary = rawLoc;
    let secondary = '';

    if (primary.includes(',')) {
      const parts = primary.split(',').map(s => s.trim());
      primary = parts[0];
    }
    if (!primary) primary = district || 'Unassigned Location';

    const secParts: string[] = [];
    if (district && district !== primary) secParts.push(district);
    if (state && !primary.includes(state)) secParts.push(state);
    
    secondary = secParts.join(', ');

    return { primary, secondary, facility };
  };

  return (
    <div className="h-screen bg-[#F4F6F9] flex flex-col font-sans">
      <Header searchQuery={globalSearchQuery} onSearchChange={setGlobalSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 md:p-8 overflow-y-auto w-full flex flex-col items-center">
          <div className="max-w-[1480px] w-full flex flex-col gap-6">
            
            {/* 1. HEADER CARD */}
            <div className="bg-white border border-slate-200/90 rounded-2xl px-6 py-6 shadow-2xs flex flex-col lg:flex-row lg:items-center justify-between gap-5 min-h-[104px]">
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-2xl lg:text-[28px] font-bold text-slate-900 tracking-tight leading-tight">
                    Events Directory
                  </h1>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                    Live Feed
                  </span>
                </div>
                <p className="text-sm md:text-[15px] text-slate-500 mt-1">
                  Monitor, investigate, and verify tracked thermal events
                </p>
              </div>

              {/* KPI Chips Group */}
              <div className="flex flex-wrap items-center gap-3">
                <div className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs md:text-sm font-medium text-slate-700 shadow-2xs h-[42px]">
                  <span className="font-extrabold text-slate-900 text-sm md:text-base">{isLoading ? '—' : metrics.total}</span>
                  <span className="text-slate-500">Events</span>
                </div>

                <div className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-50/70 border border-blue-200 text-xs md:text-sm font-medium text-blue-900 shadow-2xs h-[42px]">
                  <span className="font-extrabold text-blue-900 text-sm md:text-base">{isLoading ? '—' : metrics.active}</span>
                  <span>Active</span>
                </div>

                <div className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-red-50/70 border border-red-200 text-xs md:text-sm font-medium text-red-900 shadow-2xs h-[42px]">
                  <span className="font-extrabold text-red-900 text-sm md:text-base">{isLoading ? '—' : metrics.highPriority}</span>
                  <span>High Priority</span>
                </div>

                <div className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-50/70 border border-amber-200 text-xs md:text-sm font-medium text-amber-900 shadow-2xs h-[42px]">
                  <span className="font-extrabold text-amber-900 text-sm md:text-base">{isLoading ? '—' : metrics.underVerification}</span>
                  <span>Under Verification</span>
                </div>
              </div>
            </div>

            {/* 2. FILTER TOOLBAR */}
            <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-2xs flex flex-col gap-4">
              <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-3.5">
                {/* Search Box */}
                <div className="relative flex-1 min-w-[280px]">
                  <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={localSearchQuery}
                    onChange={(e) => setLocalSearchQuery(e.target.value)}
                    placeholder="Search events by ID, location, facility, or classification..."
                    className="w-full h-[46px] bg-slate-50/70 hover:bg-slate-50 focus:bg-white border border-slate-200 rounded-xl pl-10 pr-9 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-colors"
                  />
                  {localSearchQuery && (
                    <button
                      onClick={() => setLocalSearchQuery('')}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
                      aria-label="Clear search"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>

                {/* Filter Dropdowns */}
                <div className="flex flex-wrap items-center gap-3">
                  <select
                    value={priorityFilter}
                    onChange={(e) => setPriorityFilter(e.target.value)}
                    className="h-[46px] bg-slate-50/80 hover:bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-colors cursor-pointer"
                    aria-label="Filter by priority"
                  >
                    <option value="All">Priority: All</option>
                    <option value="Critical">Critical</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                  </select>

                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="h-[46px] bg-slate-50/80 hover:bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-colors cursor-pointer"
                    aria-label="Filter by verification status"
                  >
                    <option value="All">Status: All</option>
                    <option value="Needs Verification">Needs Verification</option>
                    <option value="Under Verification">Under Verification</option>
                    <option value="Verified Active">Verified Active</option>
                    <option value="Monitoring">Monitoring</option>
                    <option value="Verified False Alarm">Verified False Alarm</option>
                    <option value="Resolved">Resolved</option>
                  </select>

                  <select
                    value={classificationFilter}
                    onChange={(e) => setClassificationFilter(e.target.value)}
                    className="h-[46px] bg-slate-50/80 hover:bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-colors cursor-pointer"
                    aria-label="Filter by source classification"
                  >
                    <option value="All">Source: All</option>
                    <option value="Forest Fire">Forest Fire</option>
                    <option value="Industrial Fire">Industrial Fire</option>
                    <option value="Routine Flare">Routine Flare</option>
                    <option value="Agricultural Burn">Agricultural Burn</option>
                    <option value="Coal Mine Fire">Coal Mine Fire</option>
                    <option value="Unknown">Unknown</option>
                  </select>

                  <select
                    value={stateFilter}
                    onChange={(e) => setStateFilter(e.target.value)}
                    className="h-[46px] bg-slate-50/80 hover:bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm text-slate-700 font-medium focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-colors cursor-pointer"
                    aria-label="Filter by lifecycle state"
                  >
                    <option value="All">State: All</option>
                    <option value="Active">Active</option>
                    <option value="Escalating">Escalating</option>
                    <option value="Sudden Spike">Sudden Spike</option>
                    <option value="Spreading">Spreading</option>
                    <option value="Persistent">Persistent</option>
                    <option value="Declining">Declining</option>
                    <option value="Resolved">Resolved</option>
                  </select>

                  {hasActiveFilters && (
                    <button
                      onClick={handleResetFilters}
                      className="h-[46px] inline-flex items-center gap-2 px-4 rounded-xl text-sm font-semibold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 transition-colors"
                    >
                      <RotateCcw className="w-4 h-4" />
                      Reset
                    </button>
                  )}
                </div>
              </div>

              {/* Active Filter Chips */}
              {hasActiveFilters && (
                <div className="flex flex-wrap items-center gap-2.5 pt-3 border-t border-slate-100">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Filters:</span>
                  
                  {activeSearch && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
                      Search: "{activeSearch}"
                      <button onClick={() => { setLocalSearchQuery(''); setGlobalSearchQuery(''); }} className="hover:text-blue-900">
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  )}

                  {priorityFilter !== 'All' && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                      Priority: {priorityFilter}
                      <button onClick={() => setPriorityFilter('All')} className="hover:text-slate-900">
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  )}

                  {statusFilter !== 'All' && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                      Status: {statusFilter}
                      <button onClick={() => setStatusFilter('All')} className="hover:text-slate-900">
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  )}

                  {classificationFilter !== 'All' && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                      Source: {classificationFilter}
                      <button onClick={() => setClassificationFilter('All')} className="hover:text-slate-900">
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  )}

                  {stateFilter !== 'All' && (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
                      State: {stateFilter}
                      <button onClick={() => setStateFilter('All')} className="hover:text-slate-900">
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  )}

                  <button
                    onClick={handleResetFilters}
                    className="text-xs text-blue-600 hover:text-blue-800 font-bold underline underline-offset-2 ml-1"
                  >
                    Clear all
                  </button>
                </div>
              )}
            </div>

            {/* 3. EVENT TABLE CONTAINER */}
            <div className="bg-white border border-slate-200/90 rounded-2xl shadow-2xs flex flex-col overflow-hidden">
              <div className="overflow-x-auto w-full">
                <table className="w-full text-left border-collapse table-auto">
                  {/* Proportional column widths */}
                  <colgroup>
                    <col style={{ width: '16%' }} />
                    <col style={{ width: '23%' }} />
                    <col style={{ width: '11%' }} />
                    <col style={{ width: '18%' }} />
                    <col style={{ width: '13%' }} />
                    <col style={{ width: '10%' }} />
                    <col style={{ width: '9%' }} />
                  </colgroup>

                  {/* Table Header */}
                  <thead className="bg-slate-50/90 border-b border-slate-200">
                    <tr className="h-[54px]">
                      <th 
                        onClick={() => handleSort('event_id')}
                        className="px-4 lg:px-5 py-3 text-xs font-semibold text-slate-600 uppercase tracking-[0.05em] cursor-pointer hover:bg-slate-100/80 transition-colors select-none whitespace-nowrap"
                      >
                        <div className="flex items-center gap-1.5">
                          <span>EVENT</span>
                          {sortField === 'event_id' ? (
                            sortOrder === 'asc' ? <ChevronUp className="w-3.5 h-3.5 text-blue-600" /> : <ChevronDown className="w-3.5 h-3.5 text-blue-600" />
                          ) : (
                            <ArrowUpDown className="w-3.5 h-3.5 text-slate-400 opacity-50" />
                          )}
                        </div>
                      </th>

                      <th 
                        onClick={() => handleSort('location')}
                        className="px-4 lg:px-5 py-3 text-xs font-semibold text-slate-600 uppercase tracking-[0.05em] cursor-pointer hover:bg-slate-100/80 transition-colors select-none whitespace-nowrap"
                      >
                        <div className="flex items-center gap-1.5">
                          <span>LOCATION</span>
                          {sortField === 'location' ? (
                            sortOrder === 'asc' ? <ChevronUp className="w-3.5 h-3.5 text-blue-600" /> : <ChevronDown className="w-3.5 h-3.5 text-blue-600" />
                          ) : (
                            <ArrowUpDown className="w-3.5 h-3.5 text-slate-400 opacity-50" />
                          )}
                        </div>
                      </th>

                      <th 
                        onClick={() => handleSort('priority')}
                        className="px-4 lg:px-5 py-3 text-xs font-semibold text-slate-600 uppercase tracking-[0.05em] cursor-pointer hover:bg-slate-100/80 transition-colors select-none whitespace-nowrap"
                      >
                        <div className="flex items-center gap-1.5">
                          <span>PRIORITY</span>
                          {sortField === 'priority' ? (
                            sortOrder === 'asc' ? <ChevronUp className="w-3.5 h-3.5 text-blue-600" /> : <ChevronDown className="w-3.5 h-3.5 text-blue-600" />
                          ) : (
                            <ArrowUpDown className="w-3.5 h-3.5 text-slate-400 opacity-50" />
                          )}
                        </div>
                      </th>

                      <th 
                        onClick={() => handleSort('status')}
                        className="px-4 lg:px-5 py-3 text-xs font-semibold text-slate-600 uppercase tracking-[0.05em] cursor-pointer hover:bg-slate-100/80 transition-colors select-none whitespace-nowrap"
                      >
                        <div className="flex items-center gap-1.5">
                          <span>STATE & STATUS</span>
                          {sortField === 'status' ? (
                            sortOrder === 'asc' ? <ChevronUp className="w-3.5 h-3.5 text-blue-600" /> : <ChevronDown className="w-3.5 h-3.5 text-blue-600" />
                          ) : (
                            <ArrowUpDown className="w-3.5 h-3.5 text-slate-400 opacity-50" />
                          )}
                        </div>
                      </th>

                      <th 
                        onClick={() => handleSort('classification')}
                        className="px-4 lg:px-5 py-3 text-xs font-semibold text-slate-600 uppercase tracking-[0.05em] cursor-pointer hover:bg-slate-100/80 transition-colors select-none whitespace-nowrap"
                      >
                        <div className="flex items-center gap-1.5">
                          <span>SOURCE</span>
                          {sortField === 'classification' ? (
                            sortOrder === 'asc' ? <ChevronUp className="w-3.5 h-3.5 text-blue-600" /> : <ChevronDown className="w-3.5 h-3.5 text-blue-600" />
                          ) : (
                            <ArrowUpDown className="w-3.5 h-3.5 text-slate-400 opacity-50" />
                          )}
                        </div>
                      </th>

                      <th 
                        onClick={() => handleSort('last_observed')}
                        className="px-4 lg:px-5 py-3 text-xs font-semibold text-slate-600 uppercase tracking-[0.05em] cursor-pointer hover:bg-slate-100/80 transition-colors select-none whitespace-nowrap"
                      >
                        <div className="flex items-center gap-1.5">
                          <span>LAST OBSERVED</span>
                          {sortField === 'last_observed' ? (
                            sortOrder === 'asc' ? <ChevronUp className="w-3.5 h-3.5 text-blue-600" /> : <ChevronDown className="w-3.5 h-3.5 text-blue-600" />
                          ) : (
                            <ArrowUpDown className="w-3.5 h-3.5 text-slate-400 opacity-50" />
                          )}
                        </div>
                      </th>

                      <th className="px-4 lg:px-5 py-3 text-xs font-semibold text-slate-600 uppercase tracking-[0.05em] text-right whitespace-nowrap">
                        ACTION
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-100">
                    {/* Skeleton Loading State */}
                    {isLoading ? (
                      Array.from({ length: 5 }).map((_, idx) => (
                        <tr key={idx} className="h-[90px] animate-pulse">
                          <td className="px-4 lg:px-5 py-3">
                            <div className="h-4 bg-slate-200 rounded w-28 mb-2"></div>
                            <div className="h-3 bg-slate-100 rounded w-20"></div>
                          </td>
                          <td className="px-4 lg:px-5 py-3">
                            <div className="h-4 bg-slate-200 rounded w-36 mb-2"></div>
                            <div className="h-3 bg-slate-100 rounded w-24"></div>
                          </td>
                          <td className="px-4 lg:px-5 py-3">
                            <div className="h-7 bg-slate-200 rounded-full w-20"></div>
                          </td>
                          <td className="px-4 lg:px-5 py-3">
                            <div className="h-4 bg-slate-200 rounded w-28 mb-2"></div>
                            <div className="h-3 bg-slate-100 rounded w-24"></div>
                          </td>
                          <td className="px-4 lg:px-5 py-3">
                            <div className="h-7 bg-slate-100 rounded-md w-32"></div>
                          </td>
                          <td className="px-4 lg:px-5 py-3">
                            <div className="h-4 bg-slate-200 rounded w-24"></div>
                          </td>
                          <td className="px-4 lg:px-5 py-3 text-right">
                            <div className="h-9 bg-slate-100 rounded-xl w-28 ml-auto"></div>
                          </td>
                        </tr>
                      ))
                    ) : error ? (
                      <tr>
                        <td colSpan={7} className="px-6 py-16 text-center">
                          <div className="max-w-md mx-auto flex flex-col items-center">
                            <div className="w-12 h-12 rounded-full bg-red-50 text-red-600 flex items-center justify-center mb-3">
                              <ShieldAlert className="w-6 h-6" />
                            </div>
                            <h3 className="text-base font-bold text-slate-900">Unable to load events</h3>
                            <p className="text-sm text-slate-500 mt-1 mb-4">
                              We couldn't retrieve the event directory right now. {error}
                            </p>
                            <button
                              onClick={loadEventsData}
                              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-2xs transition-colors"
                            >
                              <RotateCcw className="w-4 h-4" />
                              Retry
                            </button>
                          </div>
                        </td>
                      </tr>
                    ) : sortedEvents.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="px-6 py-16 text-center">
                          <div className="max-w-md mx-auto flex flex-col items-center">
                            <div className="w-12 h-12 rounded-full bg-slate-100 text-slate-400 flex items-center justify-center mb-3">
                              <Search className="w-6 h-6" />
                            </div>
                            <h3 className="text-base font-bold text-slate-900">No events found</h3>
                            <p className="text-sm text-slate-500 mt-1 mb-4">
                              {hasActiveFilters 
                                ? "No thermal events match your current filter and search criteria. Try adjusting or clearing your filters."
                                : "No events are currently registered in the system."}
                            </p>
                            {hasActiveFilters && (
                              <button
                                onClick={handleResetFilters}
                                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition-colors"
                              >
                                <RotateCcw className="w-4 h-4" />
                                Clear Filters
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ) : (
                      /* Clean, Balanced Rows */
                      sortedEvents.map(event => {
                        const locInfo = formatLocationHierarchy(event);
                        const timeInfo = formatLastObserved(event.last_seen || event.first_seen);

                        return (
                          <tr 
                            key={event.event_id} 
                            className="group transition-colors duration-150 hover:bg-slate-50/90 h-[90px]"
                          >
                            {/* 1. EVENT ID COLUMN */}
                            <td className="px-4 lg:px-5 py-3 align-middle whitespace-nowrap">
                              <Link 
                                href={`/events/${event.event_id}`}
                                className="font-mono text-[14px] font-bold text-slate-900 hover:underline transition-colors whitespace-nowrap block"
                              >
                                {event.event_id}
                              </Link>
                              <div className="text-[12px] text-slate-500 font-medium mt-1 whitespace-nowrap">
                                {event.observations_count ? `${event.observations_count} observations` : '1 observation'}
                                {event.risk_level ? ` • ${event.risk_level} risk` : ''}
                              </div>
                            </td>

                            {/* 2. LOCATION COLUMN */}
                            <td className="px-4 lg:px-5 py-3 align-middle">
                              <div className="text-[14px] font-semibold text-slate-900 leading-tight">
                                {locInfo.primary}
                              </div>
                              {locInfo.secondary && (
                                <div className="text-[12px] text-slate-500 mt-1 leading-tight">
                                  {locInfo.secondary}
                                </div>
                              )}
                              {locInfo.facility && (
                                <div className="mt-1.5">
                                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium text-slate-700 bg-slate-100 border border-slate-200 whitespace-nowrap max-w-[240px] truncate">
                                    <span className="truncate">{locInfo.facility}</span>
                                  </span>
                                </div>
                              )}
                            </td>

                            {/* 3. PRIORITY BADGE */}
                            <td className="px-4 lg:px-5 py-3 align-middle whitespace-nowrap">
                              {getPriorityBadge(event.priority)}
                            </td>

                            {/* 4. STATE & STATUS */}
                            <td className="px-4 lg:px-5 py-3 align-middle whitespace-nowrap">
                              <div>{getLifecycleStateDisplay(event.behavior)}</div>
                              <div className="mt-1.5">{getVerificationStatusBadge(event.status)}</div>
                            </td>

                            {/* 5. SOURCE / CLASSIFICATION */}
                            <td className="px-4 lg:px-5 py-3 align-middle whitespace-nowrap">
                              {getClassificationTag(event.classification)}
                            </td>

                            {/* 6. LAST OBSERVED */}
                            <td className="px-4 lg:px-5 py-3 align-middle whitespace-nowrap">
                              {timeInfo.isUnknown ? (
                                <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-slate-100 text-slate-400 border border-slate-200 whitespace-nowrap">
                                  Unknown
                                </span>
                              ) : (
                                <div title={`Recorded overpass: ${timeInfo.exact}`}>
                                  <div className="text-[13px] font-medium text-slate-700 whitespace-nowrap">
                                    {timeInfo.relative}
                                  </div>
                                  <div className="text-[11px] text-slate-400 mt-1 whitespace-nowrap">
                                    {timeInfo.exact}
                                  </div>
                                </div>
                              )}
                            </td>

                            {/* 7. VIEW DETAILS ACTION */}
                            <td className="px-4 lg:px-5 py-3 align-middle whitespace-nowrap text-right">
                              <Link 
                                href={`/events/${event.event_id}`} 
                                className="h-[36px] px-3.5 rounded-xl text-xs font-semibold text-blue-700 hover:text-white bg-blue-50 hover:bg-blue-600 border border-blue-200 hover:border-blue-600 shadow-2xs transition-all duration-150 group/btn inline-flex items-center gap-1.5 whitespace-nowrap"
                              >
                                <span>View Details</span>
                                <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover/btn:translate-x-0.5" />
                              </Link>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>

              {/* Table Footer */}
              {!isLoading && !error && sortedEvents.length > 0 && (
                <div className="px-6 py-3.5 bg-slate-50/80 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
                  <span>
                    Showing <strong className="text-slate-700 font-semibold">{sortedEvents.length}</strong> of <strong className="text-slate-700 font-semibold">{allEvents.length}</strong> total events
                  </span>
                  <span className="text-slate-400">
                    Sorted by: <strong className="text-slate-700 uppercase">{sortField.replace('_', ' ')}</strong> ({sortOrder.toUpperCase()})
                  </span>
                </div>
              )}
            </div>

          </div>
        </main>
      </div>
    </div>
  );
}
