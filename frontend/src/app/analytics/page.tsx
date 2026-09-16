'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { fetchAnalyticsEventsOverTime, fetchAnalyticsClassifications, fetchAnalyticsPriorities, fetchAnalyticsStatus, fetchAnalyticsEvidenceSources } from '../../lib/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line, Legend } from 'recharts';

export default function AnalyticsPage() {
  const [currentTab, setCurrentTab] = useState('analytics');
  const [searchQuery, setSearchQuery] = useState('');
  
  const [eventsOverTime, setEventsOverTime] = useState<any[]>([]);
  const [classifications, setClassifications] = useState<any[]>([]);
  const [priorities, setPriorities] = useState<any[]>([]);
  const [statusCounts, setStatusCounts] = useState<any[]>([]);
  const [evidenceSources, setEvidenceSources] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [timeRes, classRes, prioRes, statusRes, evidenceRes] = await Promise.all([
          fetchAnalyticsEventsOverTime(),
          fetchAnalyticsClassifications(),
          fetchAnalyticsPriorities(),
          fetchAnalyticsStatus(),
          fetchAnalyticsEvidenceSources(),
        ]);
        
        setEventsOverTime(timeRes);
        setClassifications(classRes);
        setPriorities(prioRes);
        setStatusCounts(statusRes);
        setEvidenceSources(evidenceRes);
      } catch (err) {
        console.error('Error loading analytics:', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, []);

  const COLORS = ['#16A34A', '#F59E0B', '#DC2626', '#3B82F6', '#8B5CF6'];

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />

        <main className="flex-1 p-6 overflow-y-auto max-w-[1720px] mx-auto w-full">
          <div className="mb-6 flex items-center justify-between border-b border-slate-200 pb-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900">System Analytics</h1>
              <p className="text-sm text-slate-500 mt-1">Real-time statistics and historical event trends</p>
            </div>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center h-64 text-slate-500">Loading analytics...</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Trend Chart */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
                <h3 className="text-sm font-bold text-slate-800 mb-4">Event Frequency Over Time</h3>
                {eventsOverTime.length > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={eventsOverTime}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                        <XAxis dataKey="date" tick={{fontSize: 12, fill: '#64748b'}} tickLine={false} axisLine={{stroke: '#cbd5e1'}} />
                        <YAxis tick={{fontSize: 12, fill: '#64748b'}} tickLine={false} axisLine={false} />
                        <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                        <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={3} dot={{r: 4, fill: '#3b82f6'}} activeDot={{r: 6}} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-slate-400 text-sm">No trend data available</div>
                )}
              </div>

              {/* Classifications Chart */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
                <h3 className="text-sm font-bold text-slate-800 mb-4">Event Hypotheses (Classifications)</h3>
                {classifications.length > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={classifications} layout="vertical" margin={{ left: 40 }}>
                        <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#E2E8F0" />
                        <XAxis type="number" tick={{fontSize: 12, fill: '#64748b'}} tickLine={false} axisLine={false} />
                        <YAxis dataKey="classification" type="category" tick={{fontSize: 11, fill: '#475569'}} tickLine={false} axisLine={{stroke: '#cbd5e1'}} />
                        <Tooltip cursor={{fill: '#f1f5f9'}} contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                        <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-slate-400 text-sm">No classification data available</div>
                )}
              </div>

              {/* Priority Chart */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
                <h3 className="text-sm font-bold text-slate-800 mb-4">Events by Priority</h3>
                {priorities.length > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={priorities}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={90}
                          paddingAngle={5}
                          dataKey="count"
                          nameKey="priority"
                          labelLine={false}
                        >
                          {priorities.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                        <Legend wrapperStyle={{fontSize: '12px', paddingTop: '20px'}} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-slate-400 text-sm">No priority data available</div>
                )}
              </div>

              {/* Verification Status */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
                <h3 className="text-sm font-bold text-slate-800 mb-4">Verification Status Distribution</h3>
                {statusCounts.length > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={statusCounts}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={90}
                          paddingAngle={5}
                          dataKey="count"
                          nameKey="status"
                        >
                          {statusCounts.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                        <Legend wrapperStyle={{fontSize: '12px', paddingTop: '20px'}} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-slate-400 text-sm">No status data available</div>
                )}
              </div>

            </div>
            
            <div className="grid grid-cols-1 mt-6">
              {/* Evidence Sources Chart */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
                <h3 className="text-sm font-bold text-slate-800 mb-4">Multi-Sensor Evidence Contribution</h3>
                {evidenceSources.length > 0 ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={evidenceSources} margin={{ left: 40 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                        <XAxis dataKey="source" tick={{fontSize: 12, fill: '#64748b'}} tickLine={false} axisLine={false} />
                        <YAxis type="number" tick={{fontSize: 12, fill: '#64748b'}} tickLine={false} axisLine={{stroke: '#cbd5e1'}} />
                        <Tooltip cursor={{fill: '#f1f5f9'}} contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                        <Bar dataKey="count" fill="#10b981" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-64 flex items-center justify-center text-slate-400 text-sm">No evidence sources data available</div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
