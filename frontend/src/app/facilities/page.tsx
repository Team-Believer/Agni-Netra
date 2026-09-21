'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import Link from 'next/link';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { fetchFacilities } from '../../lib/api';
import { 
  Building2, 
  LayoutGrid, 
  Layers, 
  ChevronDown, 
  ChevronRight, 
  ChevronsDown, 
  ChevronsUp, 
  Search, 
  X, 
  RotateCcw,
  AlertTriangle,
  MapPin
} from 'lucide-react';

const normalizeCategory = (type: string | undefined): string => {
  if (!type) return 'Other Infrastructure';
  const t = type.trim();
  if (t === 'Refinery' || t === 'Petroleum Refinery') return 'Petroleum Refinery';
  if (t === 'Steel' || t === 'Steel Plant') return 'Steel Plant';
  if (t === 'Power' || t === 'Power Plant') return 'Power Plant';
  if (t === 'Forest' || t === 'Forest Reserve') return 'Forest';
  if (t === 'Agriculture' || t === 'Agricultural') return 'Agriculture';
  if (t === 'Waste' || t === 'Waste Management') return 'Waste Management';
  if (t === 'Mining') return 'Mining';
  if (t === 'Port' || t === 'Industrial Port') return 'Industrial Port';
  if (t === 'Park' || t === 'Industrial Park') return 'Industrial Park';
  return t;
};

const getCategoryColor = (category: string): string => {
  switch (category) {
    case 'Petroleum Refinery':
      return 'text-amber-700 bg-amber-50 border-amber-200/80';
    case 'Steel Plant':
      return 'text-blue-700 bg-blue-50 border-blue-200/80';
    case 'Power Plant':
      return 'text-violet-700 bg-violet-50 border-violet-200/80';
    case 'Forest':
      return 'text-emerald-700 bg-emerald-50 border-emerald-200/80';
    case 'Agriculture':
      return 'text-lime-800 bg-lime-50 border-lime-200/80';
    case 'Waste Management':
      return 'text-slate-700 bg-slate-100 border-slate-200';
    case 'Mining':
      return 'text-amber-900 bg-amber-100/70 border-amber-300';
    case 'Industrial Port':
    case 'Industrial Park':
      return 'text-indigo-700 bg-indigo-50 border-indigo-200/80';
    default:
      return 'text-slate-700 bg-slate-50 border-slate-200';
  }
};

const getFacilityStatusBadge = (eventCount: number) => {
  if (eventCount >= 5) {
    return {
      label: 'Critical Risk',
      badge: 'bg-red-50 text-red-700 border-red-200/90 font-bold',
      dot: 'bg-red-600',
      borderAccent: 'border-l-4 border-l-red-500'
    };
  }
  if (eventCount >= 3) {
    return {
      label: 'High Priority',
      badge: 'bg-orange-50 text-orange-700 border-orange-200/90 font-bold',
      dot: 'bg-orange-500',
      borderAccent: 'border-l-4 border-l-orange-500'
    };
  }
  if (eventCount >= 1) {
    return {
      label: 'Monitored',
      badge: 'bg-slate-100/90 text-slate-700 border-slate-200 font-medium',
      dot: 'bg-amber-500',
      borderAccent: ''
    };
  }
  return {
    label: 'Operational',
    badge: 'bg-slate-50 text-slate-600 border-slate-200/90 font-medium',
    dot: 'bg-emerald-500',
    borderAccent: ''
  };
};

const getCategoryStatusSummary = (items: any[]) => {
  const criticalCount = items.filter(f => (f.event_count || 0) >= 5).length;
  const highCount = items.filter(f => (f.event_count || 0) >= 3 && (f.event_count || 0) < 5).length;
  const totalEvents = items.reduce((sum, f) => sum + (f.event_count || 0), 0);

  if (criticalCount > 0) {
    return {
      text: `${criticalCount} Critical Asset${criticalCount > 1 ? 's' : ''}`,
      badge: 'bg-red-50 text-red-700 border-red-200/80 font-bold',
      dot: 'bg-red-600'
    };
  }
  if (highCount > 0) {
    return {
      text: `${highCount} High Priority`,
      badge: 'bg-orange-50 text-orange-700 border-orange-200/80 font-bold',
      dot: 'bg-orange-500'
    };
  }
  if (totalEvents > 0) {
    return {
      text: `${totalEvents} Active Event${totalEvents > 1 ? 's' : ''}`,
      badge: 'bg-amber-50 text-amber-700 border-amber-200/80 font-semibold',
      dot: 'bg-amber-500'
    };
  }
  return {
    text: 'All Operational',
    badge: 'bg-emerald-50 text-emerald-700 border-emerald-200/80 font-semibold',
    dot: 'bg-emerald-500'
  };
};

export default function FacilitiesPage() {
  const [currentTab, setCurrentTab] = useState('facilities');
  const [searchQuery, setSearchQuery] = useState('');
  const [facilities, setFacilities] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  // Filters & Controls State
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [sortBy, setSortBy] = useState<'events-desc' | 'location-asc' | 'name-asc'>('events-desc');
  const [viewMode, setViewMode] = useState<'grid' | 'category'>('grid');
  const [collapsedCategories, setCollapsedCategories] = useState<Record<string, boolean>>({});

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setIsError(false);
    try {
      const data = await fetchFacilities();
      setFacilities(data || []);
    } catch (err) {
      console.error('Error loading facilities:', err);
      setIsError(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();

    // Handle view mode persistence & URL parameter ?view=category
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const viewParam = params.get('view');
      if (viewParam === 'category' || viewParam === 'grid') {
        setViewMode(viewParam as 'grid' | 'category');
      } else {
        const stored = localStorage.getItem('facilities_view_mode');
        if (stored === 'category' || stored === 'grid') {
          setViewMode(stored as 'grid' | 'category');
        }
      }
    }
  }, [loadData]);

  const handleViewModeChange = (mode: 'grid' | 'category') => {
    setViewMode(mode);
    if (typeof window !== 'undefined') {
      localStorage.setItem('facilities_view_mode', mode);
      const url = new URL(window.location.href);
      url.searchParams.set('view', mode);
      window.history.replaceState({}, '', url.toString());
    }
  };

  // Extract unique normalized categories
  const uniqueCategories = useMemo(() => {
    const set = new Set<string>();
    facilities.forEach(f => {
      set.add(normalizeCategory(f.type));
    });
    return Array.from(set).sort();
  }, [facilities]);

  // Derived Facility Summary Metrics from loaded application state
  const metrics = useMemo(() => {
    const totalFacilities = facilities.length;
    const withEvents = facilities.filter(f => (f.event_count || 0) > 0).length;
    const highPriority = facilities.filter(f => (f.event_count || 0) >= 3).length;
    const categoriesCount = uniqueCategories.length;
    return {
      totalFacilities,
      withEvents,
      highPriority,
      categoriesCount
    };
  }, [facilities, uniqueCategories]);

  // Filter & Sort facilities without mutating backend
  const filteredAndSortedFacilities = useMemo(() => {
    return facilities
      .map(f => ({
        ...f,
        normalizedCategory: normalizeCategory(f.type)
      }))
      .filter(f => {
        // Search Filter: match location, name, or category
        const query = searchQuery.trim().toLowerCase();
        const matchesSearch = 
          !query || 
          (f.name && f.name.toLowerCase().includes(query)) || 
          (f.location && f.location.toLowerCase().includes(query)) ||
          (f.normalizedCategory && f.normalizedCategory.toLowerCase().includes(query));
        
        // Category Filter
        const matchesCategory = categoryFilter === 'All' || f.normalizedCategory === categoryFilter;

        return matchesSearch && matchesCategory;
      })
      .sort((a, b) => {
        if (sortBy === 'events-desc') {
          return (b.event_count || 0) - (a.event_count || 0);
        }
        if (sortBy === 'location-asc') {
          return (a.location || '').localeCompare(b.location || '');
        }
        if (sortBy === 'name-asc') {
          return (a.name || '').localeCompare(b.name || '');
        }
        return 0;
      });
  }, [facilities, searchQuery, categoryFilter, sortBy]);

  // Group facilities by category for By Category View
  const categoryGroups = useMemo(() => {
    const map: Record<string, any[]> = {};
    filteredAndSortedFacilities.forEach(f => {
      const cat = f.normalizedCategory;
      if (!map[cat]) map[cat] = [];
      map[cat].push(f);
    });

    return Object.keys(map)
      .map(cat => {
        const items = map[cat];
        const criticalCount = items.filter(f => (f.event_count || 0) >= 5).length;
        const highCount = items.filter(f => (f.event_count || 0) >= 3).length;
        const maxEvents = Math.max(...items.map(f => f.event_count || 0), 0);
        const totalEvents = items.reduce((sum, f) => sum + (f.event_count || 0), 0);

        // Sections with critical/high assets appear first
        const priorityScore = criticalCount * 1000 + highCount * 100 + maxEvents * 10 + totalEvents;

        return {
          category: cat,
          facilities: items,
          priorityScore
        };
      })
      .sort((a, b) => b.priorityScore - a.priorityScore || a.category.localeCompare(b.category));
  }, [filteredAndSortedFacilities]);

  const toggleCategoryCollapse = (cat: string) => {
    setCollapsedCategories(prev => ({
      ...prev,
      [cat]: !prev[cat]
    }));
  };

  const handleExpandAll = (cats: string[]) => {
    const next: Record<string, boolean> = {};
    cats.forEach(c => { next[c] = false; });
    setCollapsedCategories(next);
  };

  const handleCollapseAll = (cats: string[]) => {
    const next: Record<string, boolean> = {};
    cats.forEach(c => { next[c] = true; });
    setCollapsedCategories(next);
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setCategoryFilter('All');
    setSortBy('events-desc');
  };

  // Facility Card Component - Clean, icon-free, no hover animations
  const renderFacilityCard = (facility: any, categoryName?: string) => {
    const category = categoryName || facility.normalizedCategory;
    const categoryColorClass = getCategoryColor(category);
    const statusObj = getFacilityStatusBadge(facility.event_count || 0);
    const titleText = facility.location || facility.name;
    const facilityNameText = facility.name || facility.location;
    const eventCount = facility.event_count || 0;
    const eventLabel = eventCount === 1 ? '1 Thermal Event' : `${eventCount} Thermal Events`;

    return (
      <Link key={facility.id} href={`/facilities/${encodeURIComponent(facility.id)}`} className="block group h-full">
        <div className={`bg-white border rounded-[16px] p-5 sm:p-5.5 shadow-2xs hover:border-slate-300 transition-colors flex flex-col justify-between h-full min-h-[200px] ${statusObj.borderAccent ? statusObj.borderAccent + ' border-slate-200/90' : 'border-slate-200/90'}`}>
          
          {/* TOP LAYER: Category Pill Left + Status Badge Right */}
          <div className="flex items-center justify-between gap-2 mb-3.5 shrink-0">
            <span className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md border ${categoryColorClass}`}>
              {category}
            </span>
            <span className={`text-[12px] h-[28px] px-2.5 rounded-full border inline-flex items-center gap-1.5 shrink-0 ${statusObj.badge}`}>
              <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${statusObj.dot}`}></span>
              <span>{statusObj.label}</span>
            </span>
          </div>
          
          {/* MIDDLE LAYER: Location Title with MapPin + Monitored Facility Identity */}
          <div className="flex-1 flex flex-col justify-start">
            {/* Primary Heading: City / Location */}
            <div className="flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-slate-400 shrink-0" />
              <h3 className="text-[17px] font-bold text-slate-900 leading-snug line-clamp-2">
                {titleText}
              </h3>
            </div>

            {/* Monitored Facility Name */}
            <div className="mt-1.5 pl-5.5 text-[13px] font-medium text-slate-600 line-clamp-2">
              {facilityNameText}
            </div>
          </div>

          {/* BOTTOM LAYER: Divider + Thermal Event Summary + Inspect Action */}
          <div className="mt-4 pt-3.5 border-t border-slate-100 flex items-center justify-between text-xs shrink-0">
            {/* Thermal Event Summary */}
            <div className="flex items-center gap-1.5">
              {eventCount > 0 ? (
                <div className="flex items-center gap-1.5">
                  <span className="font-bold text-slate-800">
                    {eventLabel}
                  </span>
                  {eventCount >= 3 && (
                    <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-orange-100 text-orange-800 border border-orange-200">
                      Elevated
                    </span>
                  )}
                </div>
              ) : (
                <span className="text-slate-500 font-medium flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  No Active Events
                </span>
              )}
            </div>

            {/* Inspect Action Link */}
            <span className="inline-flex items-center text-[13px] font-semibold text-indigo-600 group-hover:text-indigo-700">
              Inspect &rarr;
            </span>
          </div>

        </div>
      </Link>
    );
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col text-slate-800">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 md:p-8 overflow-y-auto max-w-[1720px] mx-auto w-full">
          
          {/* 1. PAGE HEADER SECTION */}
          <div className="py-2 mb-6 border-b border-slate-200 pb-5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl sm:text-[26px] font-extrabold text-slate-900 tracking-tight leading-tight">
                  Critical Infrastructure & Facilities
                </h1>
                <p className="text-sm text-slate-600 mt-1.5 font-medium">
                  Monitor industrial assets, facilities, and associated thermal activity
                </p>
              </div>

              {/* Redesigned Compact KPI */}
              <div className="flex items-center gap-3.5 bg-white border border-slate-200/90 rounded-2xl px-4 py-2.5 shadow-2xs self-start md:self-auto shrink-0">
                <div className="flex items-center justify-center shrink-0 text-indigo-600">
                  <Building2 className="w-6 h-6" />
                </div>
                <div className="flex flex-col">
                  <span className="text-2xl font-black text-slate-900 leading-none tracking-tight">
                    {metrics.totalFacilities}
                  </span>
                  <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mt-1">
                    Total Monitored
                  </span>
                </div>
              </div>
            </div>

            {/* 2. FACILITY SUMMARY METRICS ROW */}
            {!isLoading && !isError && facilities.length > 0 && (
              <div className="mt-5 pt-4 border-t border-slate-100 flex flex-wrap items-center gap-2.5">
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100/90 border border-slate-200 text-xs font-semibold text-slate-700">
                  <span className="font-extrabold text-slate-900">{metrics.totalFacilities}</span>
                  <span>Total Facilities</span>
                </div>
                
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-amber-50/80 border border-amber-200/80 text-xs font-semibold text-amber-900">
                  <span className="font-extrabold text-amber-900">{metrics.withEvents}</span>
                  <span>With Thermal Events</span>
                </div>

                {metrics.highPriority > 0 && (
                  <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-orange-50/80 border border-orange-200/80 text-xs font-semibold text-orange-900">
                    <span className="font-extrabold text-orange-900">{metrics.highPriority}</span>
                    <span>High Priority</span>
                  </div>
                )}

                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-indigo-50/80 border border-indigo-200/80 text-xs font-semibold text-indigo-900">
                  <span className="font-extrabold text-indigo-900">{metrics.categoriesCount}</span>
                  <span>Categories Monitored</span>
                </div>
              </div>
            )}
          </div>

          {/* 3. FILTER TOOLBAR (Compact Coherent Workspace Bar) */}
          <div className="mb-6 bg-white border border-slate-200/90 rounded-2xl px-4 py-3 sm:px-5 sm:py-3.5 flex flex-col md:flex-row items-stretch md:items-center justify-between shadow-2xs gap-3.5">
            
            {/* Left Controls: Search + Category + Sort */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 flex-1">
              {/* Client-Side Facility Search */}
              <div className="relative flex-1 min-w-[200px] max-w-full sm:max-w-xs">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search facilities..."
                  className="w-full h-[42px] bg-slate-50 hover:bg-slate-100/80 focus:bg-white border border-slate-200 rounded-xl pl-9 pr-8 text-sm font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition-all"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 p-1"
                    title="Clear search"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {/* Category Filter Dropdown */}
              <div className="relative shrink-0">
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="w-full sm:w-auto h-[42px] appearance-none bg-slate-50 hover:bg-slate-100/80 border border-slate-200 rounded-xl px-3.5 pr-9 text-sm font-bold text-slate-800 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition-all"
                >
                  <option value="All">All Categories ({uniqueCategories.length})</option>
                  {uniqueCategories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
                <ChevronDown className="w-4 h-4 text-slate-500 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>

              {/* Sort Dropdown */}
              <div className="relative shrink-0">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="w-full sm:w-auto h-[42px] appearance-none bg-slate-50 hover:bg-slate-100/80 border border-slate-200 rounded-xl px-3.5 pr-9 text-sm font-bold text-slate-800 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition-all"
                >
                  <option value="events-desc">Sort: Most Events</option>
                  <option value="location-asc">Sort: Location (A-Z)</option>
                  <option value="name-asc">Sort: Facility Name (A-Z)</option>
                </select>
                <ChevronDown className="w-4 h-4 text-slate-500 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>

            {/* Right Controls: Grid / By Category Segmented Toggle */}
            <div className="flex items-center justify-end shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-100">
              <div className="h-[42px] bg-slate-100/90 p-1 rounded-xl flex items-center gap-1 border border-slate-200/80">
                <button
                  onClick={() => handleViewModeChange('grid')}
                  className={`flex items-center gap-2 px-3.5 h-full rounded-lg text-sm font-bold transition-all ${
                    viewMode === 'grid'
                      ? 'bg-white text-indigo-700 shadow-2xs border border-slate-200/60'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title="Grid View"
                >
                  <LayoutGrid className="w-4 h-4" />
                  <span>Grid</span>
                </button>

                <button
                  onClick={() => handleViewModeChange('category')}
                  className={`flex items-center gap-2 px-3.5 h-full rounded-lg text-sm font-bold transition-all ${
                    viewMode === 'category'
                      ? 'bg-white text-indigo-700 shadow-2xs border border-slate-200/60'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title="By Category View"
                >
                  <Layers className="w-4 h-4" />
                  <span>By Category</span>
                </button>
              </div>
            </div>

          </div>

          {/* 4. EXPAND / COLLAPSE TOOLBAR (Only shown in Category Mode) */}
          {viewMode === 'category' && categoryGroups.length > 0 && (
            <div className="flex items-center justify-between mb-4 px-1">
              <div className="text-sm font-bold text-slate-600">
                Grouped into <span className="text-slate-900 font-extrabold">{categoryGroups.length}</span> Categories ({filteredAndSortedFacilities.length} Monitored Assets)
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleExpandAll(categoryGroups.map(g => g.category))}
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-700 hover:text-indigo-900 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200/80 px-3 py-1.5 rounded-xl transition-colors"
                >
                  <ChevronsDown className="w-4 h-4" />
                  <span>Expand All</span>
                </button>
                <button
                  onClick={() => handleCollapseAll(categoryGroups.map(g => g.category))}
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-700 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 border border-slate-200 px-3 py-1.5 rounded-xl transition-colors"
                >
                  <ChevronsUp className="w-4 h-4" />
                  <span>Collapse All</span>
                </button>
              </div>
            </div>
          )}

          {/* 5. MAIN CONTENT AREA */}
          {isLoading ? (
            /* Loading State with Facility Card Skeletons */
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 sm:gap-6 animate-pulse">
              {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
                <div key={i} className="bg-white border border-slate-200 rounded-[16px] p-5 sm:p-5.5 min-h-[200px] flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-3.5">
                      <div className="w-24 h-5 bg-slate-100 rounded-md"></div>
                      <div className="w-20 h-6 bg-slate-100 rounded-full"></div>
                    </div>
                    <div className="h-5 bg-slate-100 rounded w-3/4 mb-2"></div>
                    <div className="h-4 bg-slate-100 rounded w-1/2"></div>
                  </div>
                  <div className="pt-3.5 border-t border-slate-100 flex items-center justify-between">
                    <div className="w-24 h-4 bg-slate-100 rounded"></div>
                    <div className="w-16 h-4 bg-slate-100 rounded"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : isError ? (
            /* Error State with Retry Button */
            <div className="bg-white border border-red-200 rounded-2xl p-12 flex flex-col items-center justify-center text-center shadow-2xs">
              <div className="w-12 h-12 rounded-2xl bg-red-50 text-red-600 flex items-center justify-center mb-3">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">Unable to load facilities</h3>
              <p className="text-sm text-slate-600 mt-1 max-w-sm font-medium">
                We couldn&apos;t retrieve the monitored facility directory.
              </p>
              <button
                onClick={loadData}
                className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-bold shadow-2xs transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Retry</span>
              </button>
            </div>
          ) : filteredAndSortedFacilities.length === 0 ? (
            /* Empty State with Reset Filters */
            <div className="bg-white border border-slate-200/90 rounded-2xl p-12 flex flex-col items-center justify-center text-center shadow-2xs">
              <div className="w-12 h-12 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mb-3">
                <Building2 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-900">No facilities found</h3>
              <p className="text-sm text-slate-600 mt-1 max-w-sm font-medium">
                Try changing your category or search filter.
              </p>
              {(searchQuery || categoryFilter !== 'All') && (
                <button
                  onClick={handleResetFilters}
                  className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-bold transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Clear Filters</span>
                </button>
              )}
            </div>
          ) : viewMode === 'grid' ? (
            /* 1. GRID VIEW: 4 columns desktop, 3 tablet-lg, 2 tablet, 1 mobile; 20-24px gap */
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 sm:gap-6">
              {filteredAndSortedFacilities.map((facility) => renderFacilityCard(facility))}
            </div>
          ) : (
            /* 2. BY CATEGORY VIEW (Grouped with Clean Category Headings) */
            <div className="space-y-6">
              {categoryGroups.map((group) => {
                const isCollapsed = collapsedCategories[group.category] || false;
                const statusSummary = getCategoryStatusSummary(group.facilities);

                return (
                  <div key={group.category} className="bg-slate-50/50 border border-slate-200/80 rounded-2xl p-4 sm:p-5 shadow-2xs">
                    {/* Sticky Category Section Header without icon box */}
                    <div 
                      className="sticky top-0 z-20 bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-xl p-3.5 sm:p-4 shadow-2xs flex items-center justify-between cursor-pointer hover:border-slate-300 transition-colors select-none"
                      onClick={() => toggleCategoryCollapse(group.category)}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-slate-400 hover:text-slate-700 transition-colors p-1">
                          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </span>
                        <div className="flex items-center gap-2.5">
                          <h2 className="text-base font-extrabold text-slate-900 tracking-tight">{group.category}</h2>
                          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                            {group.facilities.length} {group.facilities.length === 1 ? 'facility' : 'facilities'}
                          </span>
                        </div>
                      </div>

                      {/* Status Summary Pill */}
                      <div className="flex items-center gap-2">
                        <span className={`text-xs px-3 py-1 rounded-full border flex items-center gap-1.5 ${statusSummary.badge}`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${statusSummary.dot}`}></span>
                          {statusSummary.text}
                        </span>
                      </div>
                    </div>

                    {/* Section Facilities Grid */}
                    {!isCollapsed && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 sm:gap-6 mt-4">
                        {group.facilities.map((facility) => renderFacilityCard(facility, group.category))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

        </main>
      </div>
    </div>
  );
}
