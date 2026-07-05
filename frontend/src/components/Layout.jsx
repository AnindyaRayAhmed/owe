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
    <div className="min-h-screen flex flex-col bg-owe-bg text-owe-text">
      {/* Header */}
      <header className="bg-owe-surface border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded bg-owe-accent text-white flex items-center justify-center font-bold text-xl">O</div>
            <div>
              <h1 className="text-xl font-semibold leading-tight">Owe</h1>
              <p className="text-xs text-owe-muted font-medium">What We Owe to Each Other</p>
            </div>
          </div>
          
          <nav className="hidden md:flex space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 text-sm font-medium transition-colors ${
                    isActive ? 'text-owe-accent border-b-2 border-owe-accent' : 'text-owe-muted hover:text-owe-text'
                  }`}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Mobile Nav (Basic) */}
      <nav className="md:hidden bg-owe-surface border-t border-slate-200 fixed bottom-0 w-full z-10 flex justify-around">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center py-3 px-4 ${
                isActive ? 'text-owe-accent' : 'text-owe-muted'
              }`}
            >
              <Icon size={20} />
              <span className="text-[10px] mt-1 font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
};

export default Layout;
