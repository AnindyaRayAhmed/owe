import { useState, useEffect } from 'react';
import { fetchMissions } from '../services/api';
import { Users, Heart, ArrowRight, MapPin, Tag, AlertCircle } from 'lucide-react';

const Missions = () => {
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('All');

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
      <div className="max-w-xl mx-auto mt-16 p-8 bg-white border border-owe-border rounded-2xl shadow-soft flex flex-col items-center text-center space-y-4">
        <div className="p-3.5 bg-rose-50 text-owe-danger rounded-full border border-rose-100">
          <AlertCircle size={28} />
        </div>
        <div className="space-y-2">
          <h3 className="text-lg font-bold text-owe-textPrimary">Connection Interrupted</h3>
          <p className="text-owe-textSecondary text-sm leading-relaxed max-w-sm">
            {error}
          </p>
        </div>
      </div>
    );
  }

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Community Care':
        return 'text-rose-700 bg-rose-50/70 border-rose-100/50';
      case 'Public Space':
        return 'text-indigo-700 bg-indigo-50/70 border-indigo-100/50';
      case 'Accessibility':
        return 'text-owe-primary bg-owe-cyan/40 border-owe-border/50';
      case 'Environment':
        return 'text-emerald-700 bg-emerald-50/70 border-emerald-100/50';
      case 'Mobility':
        return 'text-amber-700 bg-amber-50/70 border-amber-100/50';
      default:
        return 'text-owe-textSecondary bg-owe-bg border-owe-border';
    }
  };

  const filteredMissions = selectedCategory === 'All'
    ? missions
    : missions.filter(m => m.category === selectedCategory);

  return (
    <div className="space-y-10 animate-page-transition pb-16">
      
      <section className="space-y-3">
        <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-owe-textPrimary">Community Missions</h2>
        <p className="text-owe-textSecondary text-base sm:text-lg max-w-2xl leading-relaxed mt-2">
          Meaningful acts of mutual support. Step in to assist your neighbors based on emerging civic needs across Kolkata.
        </p>
      </section>

      {/* Category Filter Pills */}
      <div className="flex flex-wrap gap-2 md:gap-3 py-1">
        {['All', 'Community Care', 'Public Space', 'Accessibility', 'Environment', 'Mobility'].map((category) => {
          const isActive = selectedCategory === category;
          return (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-semibold border transition-all duration-200 focus:outline-none ${
                isActive 
                  ? 'bg-owe-primary text-white border-owe-primary shadow-sm' 
                  : 'bg-white text-owe-textSecondary border-owe-border hover:bg-owe-cyan/20 hover:text-owe-primary'
              }`}
            >
              {category}
            </button>
          );
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
        {filteredMissions.map((mission, idx) => (
          <div key={idx} className="card p-6 md:p-7 hover:scale-[1.01] hover:border-owe-primary/20 flex flex-col justify-between h-full group">
            <div className="space-y-5">
              
              {/* Top Meta */}
              <div className="flex justify-between items-center gap-2">
                <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${getCategoryColor(mission.category)}`}>
                  <Tag size={10} className="mr-1.5" />
                  {mission.category || 'Civic'}
                </span>
                <span className="text-xs text-owe-textSecondary flex items-center space-x-1 font-semibold bg-owe-bg px-2.5 py-1 rounded-full border border-owe-border">
                  <MapPin size={12} className="text-owe-textMuted" />
                  <span>{mission.locality}</span>
                </span>
              </div>
              
              {/* Content */}
              <div className="space-y-4">
                <h3 className="text-lg sm:text-xl font-bold text-owe-textPrimary leading-snug group-hover:text-owe-primary transition-colors">{mission.title}</h3>
                
                <div className="bg-owe-bg rounded-xl p-4 border border-owe-border/40">
                  <span className="text-[10px] font-bold text-owe-textMuted uppercase tracking-wider block mb-1">Why It Matters</span>
                  <p className="text-owe-textSecondary text-xs sm:text-sm leading-relaxed">{mission.whyItMatters}</p>
                </div>

                <div className="flex items-center space-x-2 text-xs sm:text-sm text-owe-textSecondary font-semibold">
                  <Users size={15} className="text-owe-textMuted" />
                  <span>Affecting <span className="text-owe-textPrimary">{mission.affectedGroup}</span></span>
                </div>
              </div>
            </div>

            {/* CTA */}
            <div className="mt-6 pt-4 border-t border-owe-border/60 flex items-center justify-between gap-2">
              <span className="text-xs text-owe-textSecondary flex items-center space-x-1.5 font-semibold">
                <Heart size={14} className="text-rose-400" />
                <span>{mission.volunteersNeeded} neighbors needed</span>
              </span>
              
              <button className="bg-owe-cyan/40 hover:bg-owe-primary text-owe-primary hover:text-white px-3.5 py-2 rounded-xl font-bold text-xs sm:text-sm flex items-center space-x-1 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-owe-primary/20 hover:shadow-sm">
                <span>Offer Help</span>
                <ArrowRight size={14} className="ml-1 opacity-70 transition-transform group-hover:translate-x-0.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Missions;
