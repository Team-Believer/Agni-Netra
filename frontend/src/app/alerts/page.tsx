'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../../components/Header';
import { Sidebar } from '../../components/Sidebar';
import { Bell, AlertTriangle, Info, CheckCircle } from 'lucide-react';

interface AlertItem {
  id: number;
  event_id: string;
  alert_type: string;
  severity: string;
  title: string;
  message: string;
  status: string;
  created_at: string;
}

export default function AlertsPage() {
  const [currentTab, setCurrentTab] = useState('alerts');
  const [searchQuery, setSearchQuery] = useState('');
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/alerts');
        const data = await response.json();
        setAlerts(data);
      } catch (error) {
        console.error('Error fetching alerts:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAlerts();
  }, []);

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case 'medium':
        return <Info className="w-5 h-5 text-amber-500" />;
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-[#F4F6F9] flex flex-col">
      <Header searchQuery={searchQuery} onSearchChange={setSearchQuery} />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar currentTab={currentTab} onTabChange={setCurrentTab} />
        <main className="flex-1 p-6 overflow-y-auto max-w-[1200px] mx-auto w-full">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
              <Bell className="w-6 h-6 text-blue-600" />
              Active Alerts
            </h1>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            {isLoading ? (
              <div className="p-8 text-center text-slate-500">Loading alerts...</div>
            ) : alerts.length === 0 ? (
              <div className="p-8 text-center text-slate-500 flex flex-col items-center">
                <CheckCircle className="w-10 h-10 text-green-500 mb-3" />
                <p className="text-lg font-medium">All clear</p>
                <p className="text-sm">No active alerts to display.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {alerts.map((alert) => (
                  <div key={alert.id} className="p-4 flex gap-4 hover:bg-slate-50 transition-colors">
                    <div className="pt-1">{getSeverityIcon(alert.severity)}</div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-slate-800 text-sm">
                          {alert.title}
                        </h3>
                        <span className="text-xs text-slate-500">
                          {new Date(alert.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-slate-600 mt-1">{alert.message}</p>
                      <div className="mt-3 flex items-center gap-3 text-xs">
                        <span className={`px-2 py-1 rounded-md font-medium ${
                          alert.severity.toLowerCase() === 'critical' ? 'bg-red-50 text-red-700' :
                          alert.severity.toLowerCase() === 'high' ? 'bg-orange-50 text-orange-700' :
                          'bg-blue-50 text-blue-700'
                        }`}>
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className="text-slate-500 font-medium">Event: {alert.event_id}</span>
                        <span className="text-slate-400 capitalize">Status: {alert.status}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
