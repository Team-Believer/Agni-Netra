'use client';

import React, { useState } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { Flame } from 'lucide-react';
import Link from 'next/link';

export default function EventsPage() {
  const [currentTab, setCurrentTab] = useState('events');
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 overflow-y-auto max-w-[1720px] mx-auto w-full flex flex-col">
          <div className="mb-6 flex items-center justify-between border-b border-slate-200 pb-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900">Events</h1>
              <p className="text-sm text-slate-500 mt-1">Directory of all thermal anomaly events</p>
            </div>
          </div>

          <div className="flex-1 bg-white border border-slate-200 rounded-xl p-10 flex flex-col items-center justify-center text-center shadow-xs">
            <Flame className="w-12 h-12 text-slate-300 mb-4" />
            <h3 className="text-lg font-bold text-slate-800">No real events found.</h3>
            <p className="text-sm text-slate-500 mt-2 max-w-md">
              There are currently no active thermal events in the database.
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
