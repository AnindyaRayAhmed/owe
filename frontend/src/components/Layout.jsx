import { Link, Outlet, useLocation } from 'react-router-dom';
import { Home, CheckSquare, MessageSquare } from 'lucide-react';

const Layout = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Overview', icon: Home },
    { path: '/missions', label: 'Missions', icon: CheckSquare },
    { path: '/chat', label: 'Civic AI', icon: MessageSquare },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-owe-bg text-owe-textPrimary">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-md border-b border-owe-border sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2.5 hover:opacity-90 transition-opacity">
            <img src="/logo.svg" alt="Owe Logo" className="w-8 h-8 object-contain shrink-0" />
            <span className="text-xl sm:text-2xl font-bold tracking-tight text-owe-primary">Owe</span>
          </Link>
          
          <nav className="hidden md:flex items-center space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${
                    isActive 
                      ? 'bg-owe-cyan/50 text-owe-primary shadow-sm border border-owe-border/40 font-semibold' 
                      : 'text-owe-textSecondary hover:text-owe-primary hover:bg-owe-cyan/20'
                  }`}
                >
                  <Icon size={16} className={isActive ? 'text-owe-primary' : 'text-owe-textMuted'} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 md:py-8 z-10 relative">
        <Outlet />
      </main>

      {/* Cityscape Environmental visual grounding */}
      <div className="w-full mt-auto relative pointer-events-none select-none z-0 border-t border-owe-border/10 overflow-hidden bg-gradient-to-t from-owe-cyan/10 to-transparent pt-6 pb-20 md:pb-6">
        <svg
          className="w-full h-16 sm:h-24 md:h-28 text-owe-cyan/35 fill-current"
          viewBox="0 0 1200 120"
          preserveAspectRatio="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M 0 120 L 0 95 L 20 95 L 20 70 L 40 70 L 40 95 L 55 95 L 55 120 M 70 120 L 70 45 L 105 45 L 105 120 M 120 120 L 120 85 Q 165 55 210 85 L 210 120 M 140 100 Q 165 75 190 100 M 230 120 L 230 55 L 245 35 L 260 55 L 260 120 M 275 120 L 275 75 L 315 75 L 315 120 M 330 120 A 35 35 0 0 1 400 120 M 415 120 L 415 95 C 415 85 445 85 445 95 L 445 120 M 465 120 L 465 30 L 495 30 L 495 120 M 510 120 L 510 85 L 535 85 L 535 120 M 550 120 L 550 95 L 610 95 L 610 120 M 630 120 L 630 105 Q 730 65 830 105 L 830 120 M 660 110 L 660 120 M 690 107 L 690 120 M 720 105 L 720 120 M 750 105 L 750 120 M 780 107 L 780 120 M 800 110 L 800 120 M 850 120 C 850 110 860 100 870 100 C 880 100 890 110 890 120 M 905 120 L 905 55 L 945 55 L 945 120 M 960 120 L 960 80 L 975 65 L 990 80 L 990 120 M 1010 120 L 1010 20 L 1025 10 L 1040 20 L 1040 120 M 1060 120 Q 1095 90 1130 120 M 1150 120 L 1150 90 L 1190 90 L 1190 120 L 1200 120 L 1200 120 Z" />
        </svg>
      </div>

      {/* Mobile Nav (Basic) */}
      <nav className="md:hidden bg-white/95 backdrop-blur-md border-t border-owe-border fixed bottom-0 w-full z-20 flex justify-around py-2 px-2 shadow-lg">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center justify-center py-1.5 px-3 rounded-xl transition-all duration-300 ${
                isActive 
                  ? 'text-owe-primary bg-owe-cyan/40 font-semibold shadow-sm border border-owe-border/20' 
                  : 'text-owe-textSecondary hover:text-owe-primary'
              }`}
            >
              <Icon size={18} />
              <span className="text-[10px] mt-0.5 font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
};

export default Layout;
