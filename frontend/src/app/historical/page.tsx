'use client';

import React, { useState } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { Calendar, Search, Database } from 'lucide-react';

export default function HistoricalPage() {
  const [currentTab, setCurrentTab] = useState('historical');
  const [searchQuery, setSearchQuery] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
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
                  placeholder="e.g. Jamnagar Refinery"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm text-slate-700 focus:outline-none focus:border-blue-500 placeholder-slate-400" 
                />
              </div>

              <button className="bg-slate-900 text-white font-semibold py-2 px-4 rounded-lg text-sm hover:bg-slate-800 transition-colors h-[38px]">
                Run Query
              </button>
            </div>
          </div>

          <div className="flex-1 bg-white border border-slate-200 rounded-xl p-10 flex flex-col items-center justify-center text-center shadow-xs">
            <Database className="w-12 h-12 text-slate-300 mb-4" />
            <h3 className="text-lg font-bold text-slate-800">No Historical Data Available</h3>
            <p className="text-sm text-slate-500 mt-2 max-w-md">
              There is currently no data available for the selected timeframe. Adjust your query parameters or ensure the data ingestion pipeline has processed historical archives.
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}
