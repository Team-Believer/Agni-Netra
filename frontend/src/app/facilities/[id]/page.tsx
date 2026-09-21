'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '../../../components/Header';
import { Sidebar } from '../../../components/Sidebar';
import { fetchFacilityDetails } from '../../../lib/api';
import { Building, MapPin, ArrowLeft, Calendar, AlertTriangle } from 'lucide-react';
import Link from 'next/link';

export default function FacilityDetailPage({ params }: { params: { id: string } }) {
  const [currentTab, setCurrentTab] = useState('facilities');
  const [searchQuery, setSearchQuery] = useState('');
  const [facility, setFacility] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const loadFacility = async () => {
      try {
        const decodedId = decodeURIComponent(params.id);
        const data = await fetchFacilityDetails(decodedId);
        if (!data) {
          router.push('/facilities');
          return;
        }
        setFacility(data);
      } catch (err) {
        console.error('Error loading facility:', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadFacility();
  }, [params.id, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
        <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />
        <div className="flex-1 flex overflow-hidden">
          <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />
          <main className="flex-1 flex items-center justify-center text-slate-500">
            Loading facility details...
          </main>
        </div>
      </div>
    );
  }

  if (!facility) return null;

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 overflow-y-auto max-w-[1720px] mx-auto w-full">
          <div className="mb-4">
            <Link href="/facilities" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-blue-600 transition-colors">
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Facilities
            </Link>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs mb-6">
            <div className="p-6 md:p-8 flex items-start md:items-center justify-between flex-col md:flex-row gap-4 border-b border-slate-100">
              <div className="flex items-center gap-4">
                <div className="bg-blue-50 text-blue-600 p-4 rounded-xl">
                  <Building className="w-8 h-8" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-900">{facility.name}</h1>
                  <div className="flex items-center gap-3 text-sm text-slate-500 mt-1">
                    <span className="flex items-center gap-1"><MapPin className="w-4 h-4" /> {facility.location}</span>
                    <span className="text-slate-300">|</span>
                    <span className="font-semibold">{facility.type}</span>
                  </div>
                </div>
              </div>
              
              <div className="bg-slate-50 border border-slate-200 px-4 py-3 rounded-lg text-center min-w-[150px]">
                <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Total Events</div>
                <div className="text-2xl font-bold text-slate-900 mt-0.5">{facility.event_count}</div>
              </div>
            </div>

            <div className="p-6 md:p-8">
              <h2 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                Event History
              </h2>
              
              {facility.events && facility.events.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500">
                        <th className="py-3 px-4">Event ID</th>
                        <th className="py-3 px-4">Title</th>
                        <th className="py-3 px-4">Priority</th>
                        <th className="py-3 px-4">Status</th>
                        <th className="py-3 px-4">Last Seen</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {facility.events.map((ev: any) => (
                        <tr key={ev.event_id} className="hover:bg-slate-50 transition-colors">
                          <td className="py-3 px-4 font-semibold text-blue-600">
                            <Link href={`/dashboard?eventId=${ev.event_id}`} className="hover:underline">
                              {ev.event_id}
                            </Link>
                          </td>
                          <td className="py-3 px-4 font-medium text-slate-800">{ev.title}</td>
                          <td className="py-3 px-4">
                            <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                              ev.priority === 'Critical' || ev.priority === 'High' ? 'bg-red-50 text-red-600 border border-red-100' :
                              ev.priority === 'Medium' ? 'bg-amber-50 text-amber-700 border border-amber-100' :
                              'bg-emerald-50 text-emerald-700 border border-emerald-100'
                            }`}>
                              {ev.priority}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-slate-600 text-xs font-medium">{ev.status}</td>
                          <td className="py-3 px-4 text-slate-500 text-xs flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5" />
                            {ev.last_seen ? new Date(ev.last_seen).toLocaleDateString() : 'Unknown'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-slate-500 text-sm bg-slate-50 rounded-lg border border-slate-200">
                  No historical events recorded for this facility.
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
