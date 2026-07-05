import { useState, useEffect } from 'react';
import { fetchMissions } from '../services/api';
import { Users, Heart, ArrowRight, MapPin, Tag, AlertCircle } from 'lucide-react';

const Missions = () => {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMissions()
      .then(setMissions)
      .catch((err) => {
        setError("We are having trouble accessing open community missions. Please check back shortly.");
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="animate-pulse space-y-8 p-4 max-w-6xl mx-auto">
        <div className="h-10 bg-slate-100 rounded-xl w-1/3 mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div className="h-64 bg-slate-100 rounded-2xl"></div>
          <div className="h-64 bg-slate-100 rounded-2xl"></div>
          <div className="h-64 bg-slate-100 rounded-2xl"></div>
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

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Community Care':
        return 'text-rose-600 bg-rose-50 border-rose-100';
      case 'Public Space':
        return 'text-indigo-600 bg-indigo-50 border-indigo-100';
      case 'Accessibility':
        return 'text-teal-600 bg-teal-50 border-teal-100';
      case 'Environment':
        return 'text-emerald-600 bg-emerald-50 border-emerald-100';
      case 'Mobility':
        return 'text-amber-600 bg-amber-50 border-amber-100';
      default:
        return 'text-slate-600 bg-slate-50 border-slate-100';
    }
  };

  return (
    <div className="space-y-12 animate-in fade-in duration-700 pb-16">
      
      <section className="space-y-3">
        <h2 className="text-4xl font-semibold tracking-tight text-slate-900">Community Missions</h2>
        <p className="text-slate-500 text-lg max-w-2xl leading-relaxed">
          Meaningful acts of mutual support. Step in to assist your neighbors based on emerging civic needs across Kolkata.
        </p>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {missions.map((mission, idx) => (
          <div key={idx} className="bg-white rounded-2xl p-7 border border-slate-100 shadow-sm hover:shadow-md hover:border-slate-200 transition-all duration-300 flex flex-col justify-between h-full group">
            <div className="space-y-6">
              
              {/* Top Meta */}
              <div className="flex justify-between items-center">
                <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${getCategoryColor(mission.category)}`}>
                  <Tag size={10} className="mr-1.5" />
                  {mission.category || 'Civic'}
                </span>
                <span className="text-xs text-slate-400 flex items-center space-x-1 font-medium bg-slate-50 px-2.5 py-1 rounded-full border border-slate-100">
                  <MapPin size={12} className="text-slate-400" />
                  <span>{mission.locality}</span>
                </span>
              </div>
              
              {/* Content */}
              <div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3 leading-snug group-hover:text-teal-700 transition-colors">{mission.title}</h3>
                
                <div className="bg-slate-50 rounded-xl p-4 border border-slate-100/60 mb-4">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">Why It Matters</span>
                  <p className="text-slate-600 text-sm leading-relaxed">{mission.whyItMatters}</p>
                </div>

                <div className="flex items-center space-x-2 text-sm text-slate-500 font-medium">
                  <Users size={16} className="text-slate-400" />
                  <span>Affecting <span className="text-slate-700">{mission.affectedGroup}</span></span>
                </div>
              </div>
            </div>

            {/* CTA */}
            <div className="mt-8 pt-5 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs text-slate-500 flex items-center space-x-1.5 font-medium">
                <Heart size={14} className="text-rose-400" />
                <span>{mission.volunteersNeeded} neighbors needed</span>
              </span>
              
              <button className="bg-teal-50 hover:bg-teal-600 text-teal-700 hover:text-white px-4 py-2 rounded-lg font-semibold text-sm flex items-center space-x-1 transition-colors duration-200">
                <span>Offer Help</span>
                <ArrowRight size={14} className="ml-1 opacity-70" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Missions;
