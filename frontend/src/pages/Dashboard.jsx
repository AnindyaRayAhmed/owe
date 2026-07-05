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
        return 'bg-rose-50 text-owe-danger border-rose-100/50';
      case 'Moderate':
        return 'bg-amber-50 text-owe-warning border-amber-100/50';
      case 'Low':
      default:
        return 'bg-owe-cyan/20 text-owe-primary border-owe-border/40';
    }
  };

  return (
    <div className="space-y-10 animate-page-transition pb-16">
      
      {/* Header Section */}
      <section className="space-y-3 bg-glow-glow py-4 rounded-2xl relative overflow-hidden">
        <div className="relative z-10">
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-owe-textPrimary">Community Overview</h2>
          <p className="text-owe-textSecondary text-base sm:text-lg max-w-2xl leading-relaxed mt-2">
            A synthesis of resilience, friction, and mutual aid across Kolkata neighborhoods over the past 48 hours.
          </p>
        </div>
      </section>

      {/* Top Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card flex items-start space-x-4 p-5 hover:scale-[1.01]">
          <div className="p-3 bg-owe-cyan/50 text-owe-primary rounded-xl">
            <Activity size={22} strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-xs font-semibold text-owe-textSecondary uppercase tracking-wider mb-1">Wellbeing Pulse</p>
            <p className="text-3xl font-bold text-owe-textPrimary tracking-tight">{data.pulseScore}<span className="text-base text-owe-textMuted font-normal">/100</span></p>
          </div>
        </div>
        
        <div className="card flex items-start space-x-4 p-5 hover:scale-[1.01]">
          <div className="p-3 bg-owe-aqua/40 text-owe-secondary rounded-xl">
            <Users size={22} strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-xs font-semibold text-owe-textSecondary uppercase tracking-wider mb-1">Active Neighbors</p>
            <p className="text-3xl font-bold text-owe-textPrimary tracking-tight">{data.activeNeighbors}</p>
          </div>
        </div>

        <div className="card flex items-start space-x-4 p-5 hover:scale-[1.01]">
          <div className="p-3 bg-rose-50 text-owe-danger border border-rose-100/50 rounded-xl">
            <ShieldCheck size={22} strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-xs font-semibold text-owe-textSecondary uppercase tracking-wider mb-1">Resolved Issues</p>
            <p className="text-3xl font-bold text-owe-textPrimary tracking-tight">{data.momentum?.length || 0}</p>
          </div>
        </div>

        <div className="card flex items-start space-x-4 p-5 hover:scale-[1.01]">
          <div className="p-3 bg-emerald-50 text-emerald-600 border border-emerald-100/50 rounded-xl">
            <HeartHandshake size={22} strokeWidth={2.5} />
          </div>
          <div>
            <p className="text-xs font-semibold text-owe-textSecondary uppercase tracking-wider mb-1">Open Missions</p>
            <p className="text-3xl font-bold text-owe-textPrimary tracking-tight">{data.openMissions}</p>
          </div>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 md:gap-10">
        
        {/* Left Column: AI Insights */}
        <div className="lg:col-span-7 xl:col-span-8 space-y-6 md:space-y-8">
          <div className="flex items-center justify-between">
            <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-owe-textPrimary">Emerging Signals</h3>
            <span className="text-xs sm:text-sm font-semibold text-owe-textMuted uppercase tracking-wider">Past 48 hours</span>
          </div>
          
          <div className="space-y-6">
            {data.insights?.map((insight, idx) => (
              <div key={idx} className="card p-6 md:p-7 hover:scale-[1.01] hover:border-owe-primary/20">
                <div className="flex flex-col sm:flex-row justify-between items-start gap-2 mb-4">
                  <h4 className="text-lg sm:text-xl font-bold text-owe-textPrimary leading-snug">{insight.title}</h4>
                  <span className={`text-xs px-2.5 py-1 rounded-full border font-semibold whitespace-nowrap ${getSignalBadgeColor(insight.signalStrength)}`}>
                    {insight.signalStrength} Signal
                  </span>
                </div>
                
                <p className="text-owe-textSecondary text-sm sm:text-base leading-relaxed mb-6">{insight.description}</p>
                
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-owe-bg rounded-xl p-3 border border-owe-border/40">
                    <span className="text-[10px] font-semibold text-owe-textMuted uppercase tracking-wider block mb-1">Affected</span>
                    <span className="text-xs sm:text-sm text-owe-textSecondary font-semibold">{insight.affectedGroups}</span>
                  </div>
                  <div className="bg-owe-bg rounded-xl p-3 border border-owe-border/40">
                    <span className="text-[10px] font-semibold text-owe-textMuted uppercase tracking-wider block mb-1">Timeframe</span>
                    <span className="text-xs sm:text-sm text-owe-textSecondary font-semibold capitalize">{insight.timeframe}</span>
                  </div>
                </div>

                <div className="bg-owe-cyan/20 border-l-4 border-owe-primary p-4 rounded-r-xl rounded-l-sm">
                  <span className="text-xs font-bold text-owe-primary uppercase tracking-wider block mb-1.5">Reasoning Analysis</span>
                  <p className="text-sm text-owe-textSecondary leading-relaxed">{insight.explainability}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Community Momentum */}
        <div className="lg:col-span-5 xl:col-span-4 space-y-6 md:space-y-8">
          <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-owe-textPrimary">Community Momentum</h3>
          
          <div className="card p-5 sm:p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-owe-cyan/30 rounded-bl-full -z-10 opacity-30"></div>
            
            <div className="space-y-6 relative z-10">
              {data.momentum?.map((item, idx) => (
                <div key={idx} className="relative pl-6">
                  {idx !== data.momentum.length - 1 && (
                    <div className="absolute left-2.5 top-6 bottom-[-24px] w-px bg-owe-border"></div>
                  )}
                  <div className="absolute left-1.5 top-1.5 w-2.5 h-2.5 rounded-full bg-owe-primary ring-4 ring-owe-cyan/40"></div>
                  
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="font-bold text-owe-textPrimary text-sm leading-snug">{item.title}</h4>
                      <span className="flex items-center text-[9px] font-bold text-owe-textMuted uppercase tracking-wider shrink-0">
                        <Clock size={10} className="mr-1 text-owe-textMuted" />
                        {item.timeframe}
                      </span>
                    </div>
                    <p className="text-xs sm:text-sm text-owe-textSecondary leading-relaxed">{item.description}</p>
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
