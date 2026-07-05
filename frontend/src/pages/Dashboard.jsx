import { useState, useEffect } from 'react';
import { fetchBrief } from '../services/api';
import { Activity, Users, ShieldCheck, HeartHandshake, Clock, AlertCircle } from 'lucide-react';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBrief()
      .then(setData)
      .catch((err) => {
        setError("We are having trouble accessing the local civic feeds. Please check back shortly.");
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse space-y-8 p-4 max-w-6xl mx-auto">
        <div className="h-10 bg-slate-100 rounded-xl w-1/3 mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="h-28 bg-slate-100 rounded-2xl"></div>
          <div className="h-28 bg-slate-100 rounded-2xl"></div>
          <div className="h-28 bg-slate-100 rounded-2xl"></div>
          <div className="h-28 bg-slate-100 rounded-2xl"></div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          <div className="lg:col-span-7 xl:col-span-8 h-96 bg-slate-100 rounded-2xl"></div>
          <div className="lg:col-span-5 xl:col-span-4 h-96 bg-slate-100 rounded-2xl"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-xl mx-auto mt-16 p-8 bg-white border border-slate-100 rounded-2xl shadow-sm flex flex-col items-center text-center space-y-4">
        <div className="p-3.5 bg-rose-50 text-rose-600 rounded-full border border-rose-100">
          <AlertCircle size={28} />
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-semibold text-slate-800">Connection Interrupted</h3>
          <p className="text-slate-500 text-sm leading-relaxed max-w-sm">
            {error}
          </p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const getSignalBadgeColor = (strength) => {
    switch (strength) {
      case 'High':
        return 'bg-rose-50 text-rose-700 border-rose-100';
      case 'Moderate':
        return 'bg-amber-50 text-amber-700 border-amber-100';
      case 'Low':
      default:
        return 'bg-slate-50 text-slate-600 border-slate-100';
    }
  };

  return (
    <div className="space-y-12 animate-in fade-in duration-700 pb-16">
      
      {/* Header Section */}
      <section className="space-y-3">
        <h2 className="text-4xl font-semibold tracking-tight text-slate-900">Community Overview</h2>
        <p className="text-slate-500 text-lg max-w-2xl leading-relaxed">
          A synthesis of resilience, friction, and mutual aid across Kolkata neighborhoods over the past 48 hours.
        </p>
      </section>

      {/* Top Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-start space-x-4">
          <div className="p-3 bg-teal-50 text-teal-600 rounded-xl">
            <Activity size={24} strokeWidth={2} />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 mb-1">Wellbeing Pulse</p>
            <p className="text-3xl font-semibold text-slate-900 tracking-tight">{data.pulseScore}<span className="text-lg text-slate-400 font-normal">/100</span></p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-start space-x-4">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
            <Users size={24} strokeWidth={2} />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 mb-1">Active Neighbors</p>
            <p className="text-3xl font-semibold text-slate-900 tracking-tight">{data.activeNeighbors}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-start space-x-4">
          <div className="p-3 bg-rose-50 text-rose-600 rounded-xl">
            <ShieldCheck size={24} strokeWidth={2} />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 mb-1">Resolved Issues</p>
            <p className="text-3xl font-semibold text-slate-900 tracking-tight">{data.momentum?.length || 0}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-start space-x-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
            <HeartHandshake size={24} strokeWidth={2} />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 mb-1">Open Missions</p>
            <p className="text-3xl font-semibold text-slate-900 tracking-tight">{data.openMissions}</p>
          </div>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        
        {/* Left Column: AI Insights */}
        <div className="lg:col-span-7 xl:col-span-8 space-y-8">
          <div className="flex items-center justify-between">
            <h3 className="text-2xl font-semibold tracking-tight text-slate-900">Emerging Signals</h3>
            <span className="text-sm font-medium text-slate-400">Past 48 hours</span>
          </div>
          
          <div className="space-y-6">
            {data.insights?.map((insight, idx) => (
              <div key={idx} className="bg-white rounded-2xl p-7 border border-slate-100 shadow-sm hover:shadow-md transition-shadow duration-300">
                <div className="flex justify-between items-start mb-4">
                  <h4 className="text-xl font-semibold text-slate-900 leading-snug">{insight.title}</h4>
                  <span className={`text-xs px-3 py-1 rounded-full border font-medium whitespace-nowrap ml-4 ${getSignalBadgeColor(insight.signalStrength)}`}>
                    {insight.signalStrength} Signal
                  </span>
                </div>
                
                <p className="text-slate-600 text-base leading-relaxed mb-6">{insight.description}</p>
                
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-slate-50 rounded-xl p-3 border border-slate-100/50">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Affected</span>
                    <span className="text-sm text-slate-700 font-medium">{insight.affectedGroups}</span>
                  </div>
                  <div className="bg-slate-50 rounded-xl p-3 border border-slate-100/50">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">Timeframe</span>
                    <span className="text-sm text-slate-700 font-medium capitalize">{insight.timeframe}</span>
                  </div>
                </div>

                <div className="bg-teal-50/50 p-4 rounded-xl border border-teal-100/30">
                  <span className="text-xs font-semibold text-teal-800 uppercase tracking-wider block mb-1.5">Reasoning Analysis</span>
                  <p className="text-sm text-teal-900/80 leading-relaxed">{insight.explainability}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Community Momentum */}
        <div className="lg:col-span-5 xl:col-span-4 space-y-8">
          <h3 className="text-2xl font-semibold tracking-tight text-slate-900">Community Momentum</h3>
          
          <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-teal-50 rounded-bl-full -z-10 opacity-50"></div>
            
            <div className="space-y-8 relative z-10">
              {data.momentum?.map((item, idx) => (
                <div key={idx} className="relative pl-6">
                  {idx !== data.momentum.length - 1 && (
                    <div className="absolute left-2.5 top-6 bottom-[-24px] w-px bg-slate-100"></div>
                  )}
                  <div className="absolute left-1.5 top-1.5 w-2 h-2 rounded-full bg-teal-500 ring-4 ring-teal-50"></div>
                  
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-slate-900 text-sm">{item.title}</h4>
                      <span className="flex items-center text-[10px] font-medium text-slate-400 uppercase tracking-wider">
                        <Clock size={10} className="mr-1" />
                        {item.timeframe}
                      </span>
                    </div>
                    <p className="text-sm text-slate-500 leading-relaxed">{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
