'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { fetchFacilities } from '../../lib/api';
import { Building, MapPin, Activity, ArrowRight } from 'lucide-react';

export default function FacilitiesPage() {
  const [currentTab, setCurrentTab] = useState('facilities');
  const [searchQuery, setSearchQuery] = useState('');
  const [facilities, setFacilities] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadFacilities = async () => {
      try {
        const data = await fetchFacilities();
        setFacilities(data);
      } catch (err) {
        console.error('Error loading facilities:', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadFacilities();
  }, []);

  const filteredFacilities = facilities.filter(f => 
    f.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    f.location.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 overflow-y-auto max-w-[1720px] mx-auto w-full">
          <div className="mb-6 flex items-center justify-between border-b border-slate-200 pb-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900">Critical Infrastructure & Facilities</h1>
              <p className="text-sm text-slate-500 mt-1">Directory of monitored assets and their recent thermal event history</p>
            </div>
            <div className="text-sm font-medium text-slate-500 bg-white border border-slate-200 px-3 py-1.5 rounded-lg shadow-2xs">
              Total Monitored: <span className="font-bold text-slate-800">{facilities.length}</span>
            </div>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center h-64 text-slate-500">Loading facilities...</div>
          ) : filteredFacilities.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-xl p-10 flex flex-col items-center justify-center text-center shadow-xs">
              <Building className="w-10 h-10 text-slate-300 mb-3" />
              <h3 className="text-lg font-bold text-slate-800">No Facilities Found</h3>
              <p className="text-sm text-slate-500 mt-1">No facilities match your search criteria or the database is empty.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredFacilities.map((facility) => (
                <Link key={facility.id} href={`/facilities/${facility.id}`}>
                  <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs hover:shadow-md transition-shadow cursor-pointer group flex flex-col h-full">
                    <div className="flex items-start justify-between mb-3">
                      <div className="bg-blue-50 text-blue-600 p-2 rounded-lg">
                        <Building className="w-5 h-5" />
                      </div>
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider bg-slate-100 px-2 py-0.5 rounded">
                        {facility.type}
                      </span>
                    </div>
                    
                    <h3 className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors line-clamp-2">
                      {facility.name}
                    </h3>
                    
                    <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-2">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      <span className="truncate">{facility.location}</span>
                    </div>

                    <div className="mt-auto pt-4 border-t border-slate-100 flex items-center justify-between">
                      <div className="flex items-center gap-1.5 text-xs">
                        <Activity className="w-3.5 h-3.5 text-amber-500" />
                        <span className="font-semibold text-slate-700">{facility.event_count} Events</span>
                      </div>
                      <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-blue-500 transition-colors" />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
