'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { fetchFacilities } from '../../lib/api';
import { 
  Building, 
  MapPin, 
  Activity, 
  ArrowRight, 
  LayoutGrid, 
  Layers, 
  ChevronDown, 
  ChevronRight, 
  ChevronsDown, 
  ChevronsUp, 
  Flame, 
  Zap, 
  Factory, 
  ShieldAlert, 
  Cpu 
} from 'lucide-react';

const normalizeCategory = (type: string | undefined): string => {
  if (!type) return 'Other Infrastructure';
  const t = type.trim();
  if (t === 'Refinery' || t === 'Petroleum Refinery') return 'Petroleum Refinery';
  return t;
};

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'Petroleum Refinery':
      return Flame;
    case 'Chemical Plant':
      return Factory;
    case 'Steel Plant':
      return ShieldAlert;
    case 'Power Plant':
      return Zap;
    case 'Substation':
      return Cpu;
    default:
      return Building;
  }
};

const getFacilitySeverity = (eventCount: number) => {
  if (eventCount >= 5) {
    return { label: 'Critical Risk', badge: 'bg-red-50 text-red-700 border-red-200/80 font-bold', dot: 'bg-red-600 animate-pulse' };
  }
  if (eventCount >= 3) {
    return { label: 'High Priority', badge: 'bg-orange-50 text-orange-700 border-orange-200/80 font-bold', dot: 'bg-orange-500' };
  }
  if (eventCount >= 1) {
    return { label: 'Monitored', badge: 'bg-amber-50 text-amber-700 border-amber-200/80 font-bold', dot: 'bg-amber-500' };
  }
  return { label: 'Operational', badge: 'bg-emerald-50 text-emerald-700 border-emerald-200/80 font-bold', dot: 'bg-emerald-500' };
};

const getCategoryStatusSummary = (items: any[]) => {
  const criticalCount = items.filter(f => (f.event_count || 0) >= 5).length;
  const highCount = items.filter(f => (f.event_count || 0) >= 3 && (f.event_count || 0) < 5).length;
  const totalEvents = items.reduce((sum, f) => sum + (f.event_count || 0), 0);

  if (criticalCount > 0) {
    return {
      text: `${criticalCount} Critical Asset${criticalCount > 1 ? 's' : ''}`,
      badge: 'bg-red-50 text-red-700 border-red-200/80 font-bold',
      dot: 'bg-red-600 animate-pulse'
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
      text: `${totalEvents} Total Event${totalEvents > 1 ? 's' : ''}`,
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

  // Filters & Controls State
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [sortBy, setSortBy] = useState<'events-desc' | 'name-asc' | 'location-asc'>('events-desc');
  const [viewMode, setViewMode] = useState<'grid' | 'category'>('grid');
  const [collapsedCategories, setCollapsedCategories] = useState<Record<string, boolean>>({});

  // Load facilities & URL / localStorage view mode on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchFacilities();
        setFacilities(data);
      } catch (err) {
        console.error('Error loading facilities:', err);
      } finally {
        setIsLoading(false);
      }
    };
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
  }, []);

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

  // Filter & Sort facilities without resetting view
  const filteredAndSortedFacilities = useMemo(() => {
    return facilities
      .map(f => ({
        ...f,
        normalizedCategory: normalizeCategory(f.type)
      }))
      .filter(f => {
        // Search Filter
        const query = searchQuery.toLowerCase();
        const matchesSearch = 
          !query || 
          f.name.toLowerCase().includes(query) || 
          f.location.toLowerCase().includes(query) ||
          f.normalizedCategory.toLowerCase().includes(query);
        
        // Category Filter
        const matchesCategory = categoryFilter === 'All' || f.normalizedCategory === categoryFilter;

        return matchesSearch && matchesCategory;
      })
      .sort((a, b) => {
        if (sortBy === 'events-desc') {
          return (b.event_count || 0) - (a.event_count || 0);
        }
        if (sortBy === 'name-asc') {
          return a.name.localeCompare(b.name);
        }
        if (sortBy === 'location-asc') {
          return a.location.localeCompare(b.location);
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
        const maxEvents = Math.max(...items.map(f => f.event_count || 0));
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

  // Reusable Facility Card Component conforming strictly to 4 fixed rows spec
  const renderFacilityCard = (facility: any, categoryName?: string) => {
    const category = categoryName || facility.normalizedCategory;
    const CategoryIcon = getCategoryIcon(category);
    const severity = getFacilitySeverity(facility.event_count || 0);
    const titleText = facility.location || facility.name;
    const locationText = facility.name || facility.location;
    const eventCount = facility.event_count || 0;
    const eventLabel = eventCount === 1 ? '1 thermal event' : `${eventCount} thermal events`;

    return (
      <Link key={facility.id} href={`/facilities/${facility.id}`}>
        <div className="bg-white border border-slate-200 rounded-[16px] p-[18px] shadow-2xs hover:shadow-card-hover hover:border-indigo-300 transition-all duration-200 cursor-pointer group flex flex-col justify-between h-full min-h-[220px]">
          {/* Row 1: Icon Left + Badge Right */}
          <div className="flex items-center justify-between gap-2 mb-3 shrink-0">
            <div className="w-10 h-10 rounded-xl bg-indigo-50/90 border border-indigo-100 text-indigo-600 flex items-center justify-center shrink-0">
              <CategoryIcon className="w-5 h-5" />
            </div>
            <span className={`text-xs font-bold px-2.5 py-1 rounded-full border flex items-center gap-1.5 ${severity.badge}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${severity.dot}`}></span>
              {severity.label}
            </span>
          </div>
          
          {/* Row 2: Location as Title + Small Uppercase Category Tag */}
          <div className="mb-3 shrink-0">
            <h3 className="text-sm font-bold text-slate-900 group-hover:text-indigo-600 transition-colors line-clamp-2 leading-snug">
              {titleText}
            </h3>
            <div className="mt-1 text-[11px] font-extrabold text-slate-500 uppercase tracking-wider">
              {category}
            </div>
          </div>
          
          {/* Row 3: Facility Name / Location with Pin Icon */}
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 mb-4 shrink-0">
            <MapPin className="w-4 h-4 text-slate-400 shrink-0" />
            <span className="truncate">{locationText}</span>
          </div>

          {/* Row 4: Pinned Footer with Divider (Singular / Plural Event Count) */}
          <div className="mt-auto pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-bold shrink-0">
            <div className="flex items-center gap-1.5 text-slate-800">
              <Activity className="w-4 h-4 text-amber-500 shrink-0" />
              <span>{eventLabel}</span>
            </div>
            <span className="text-indigo-600 group-hover:translate-x-0.5 transition-transform flex items-center gap-1">
              Inspect <ArrowRight className="w-3.5 h-3.5" />
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

        <main className="flex-1 p-6 overflow-y-auto max-w-[1720px] mx-auto w-full">
          {/* Header Title Section */}
          <div className="mb-6 flex items-center justify-between border-b border-slate-200 pb-4">
            <div>
              <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Critical Infrastructure & Facilities</h1>
              <p className="text-sm text-slate-600 mt-1 font-medium">Directory of monitored industrial assets and thermal event intelligence</p>
            </div>
            <div className="text-sm font-bold text-slate-700 bg-white border border-slate-200 px-4 py-2 rounded-xl shadow-2xs flex items-center gap-2">
              <Building className="w-4.5 h-4.5 text-indigo-600" />
              <span>Total Monitored: <strong className="text-slate-900 font-extrabold">{facilities.length}</strong></span>
            </div>
          </div>

          {/* Filter Bar (Single row, ~56px tall, controls vertically centered, view toggle right) */}
          <div className="mb-6 bg-white border border-slate-200/90 rounded-2xl px-5 h-[56px] min-h-[56px] flex items-center justify-between shadow-2xs gap-4 overflow-x-auto">
            {/* Left Controls: Category Filter & Sort */}
            <div className="flex items-center gap-3 shrink-0">
              {/* Category Filter */}
              <div className="relative">
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="appearance-none bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl px-3.5 py-2 pr-9 text-sm font-bold text-slate-800 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition-all"
                >
                  <option value="All">All Categories ({uniqueCategories.length})</option>
                  {uniqueCategories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
                <ChevronDown className="w-4 h-4 text-slate-500 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>

              {/* Sort Dropdown */}
              <div className="relative">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="appearance-none bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl px-3.5 py-2 pr-9 text-sm font-bold text-slate-800 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition-all"
                >
                  <option value="events-desc">Sort: Most Events</option>
                  <option value="name-asc">Sort: Name (A-Z)</option>
                  <option value="location-asc">Sort: Location (A-Z)</option>
                </select>
                <ChevronDown className="w-4 h-4 text-slate-500 absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              </div>
            </div>

            {/* Right Controls: View Toggle (Grid | By Category) */}
            <div className="flex items-center gap-2 shrink-0">
              <div className="bg-slate-100/90 p-1 rounded-xl flex items-center gap-1 border border-slate-200/80">
                <button
                  onClick={() => handleViewModeChange('grid')}
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-bold transition-all ${
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
                  className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-bold transition-all ${
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

          {/* Expand All / Collapse All Toolbar for By Category View */}
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

          {/* Main Body Content */}
          {isLoading ? (
            <div className="flex items-center justify-center h-64 text-slate-600 text-sm font-bold">Loading facilities...</div>
          ) : filteredAndSortedFacilities.length === 0 ? (
            <div className="bg-white border border-slate-200/90 rounded-2xl p-12 flex flex-col items-center justify-center text-center shadow-2xs">
              <Building className="w-12 h-12 text-slate-300 mb-3" />
              <h3 className="text-lg font-bold text-slate-900">No Facilities Found</h3>
              <p className="text-sm text-slate-600 mt-1 max-w-sm font-medium">No infrastructure assets match your search or filter criteria.</p>
            </div>
          ) : viewMode === 'grid' ? (
            /* 1. GRID VIEW: Solid white card, 1px border, 16px radius, 18px padding, min 260px columns, 20px gap */
            <div className="grid grid-cols-[repeat(auto-fill,minmax(260px,1fr))] gap-[20px]">
              {filteredAndSortedFacilities.map((facility) => renderFacilityCard(facility))}
            </div>
          ) : (
            /* 2. BY CATEGORY VIEW (Collapsible Sections) */
            <div className="space-y-6">
              {categoryGroups.map((group) => {
                const isCollapsed = collapsedCategories[group.category] || false;
                const CategoryIcon = getCategoryIcon(group.category);
                const statusSummary = getCategoryStatusSummary(group.facilities);

                return (
                  <div key={group.category} className="bg-slate-50/50 border border-slate-200/80 rounded-2xl p-4 shadow-2xs">
                    {/* Sticky Category Section Header */}
                    <div 
                      className="sticky top-0 z-20 bg-white/95 backdrop-blur-md border border-slate-200/90 rounded-xl p-4 shadow-2xs flex items-center justify-between cursor-pointer hover:border-indigo-300 transition-all select-none"
                      onClick={() => toggleCategoryCollapse(group.category)}
                    >
                      <div className="flex items-center gap-3">
                        <button className="text-slate-400 hover:text-slate-700 transition-colors">
                          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                        <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-100 text-indigo-600 flex items-center justify-center shrink-0">
                          <CategoryIcon className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h2 className="text-base font-extrabold text-slate-900">{group.category}</h2>
                            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                              {group.facilities.length} Asset{group.facilities.length > 1 ? 's' : ''}
                            </span>
                          </div>
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

                    {/* Section Facilities Grid: Solid white cards, 16px radius, 18px padding, min 260px cols, 20px gap */}
                    {!isCollapsed && (
                      <div className="grid grid-cols-[repeat(auto-fill,minmax(260px,1fr))] gap-[20px] mt-4">
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
