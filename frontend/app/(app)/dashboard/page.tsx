'use client';
import { Bell, Plus, FileText, Bot, Clock, BarChart2 } from "lucide-react";
import Link from 'next/link';

const DashboardPage = () => {

  return (
    <>
      <div className="p-8 animate-in">
        {/* Header */}
        <header className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-3xl font-bold text-white">Dashboard</h1>
            <p className="text-gray-400">Tuesday, November 18, 2025</p>
          </div>
          <div className="flex items-center space-x-4">
            <button className="relative text-gray-400 hover:text-white transition-colors">
              <Bell size={24} />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-primary"></span>
              </span>
            </button>
            <button 
              className="flex items-center space-x-2 bg-primary hover:bg-primary-hover text-white font-semibold px-4 py-2.5 rounded-lg transition-colors shadow-lg shadow-primary/20"
            >
              <Plus size={20} />
              <span>New Project</span>
            </button>
          </div>
        </header>

        {/* Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          <StatCard icon={<FileText />} title="Total Projects" value="12" />
          <StatCard icon={<Bot />} title="Docs Generated" value="1,240" />
          <StatCard icon={<Clock />} title="Agent Hours" value="450h" />
          <StatCard icon={<BarChart2 />} title="Avg. Quality" value="98%" />
            </div>

        {/* Recent Projects */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white">Recent Projects</h2>
            <button className="text-sm text-gray-400 bg-card px-3 py-1.5 rounded-md hover:bg-border transition-colors">
              Sorted by Activity
                    </button>
                  </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <ProjectCard
              initial="Q"
              name="Quantum Ledger"
              status="Complete"
              lastUpdated="2h ago"
              fileCount={12}
              agents={['architect', 'writer', 'critic']}
            />
            <ProjectCard
              initial="N"
              name="Neural Net API"
              status="Generating"
              lastUpdated="Just now"
              fileCount={4}
              agents={['architect', 'writer']}
            />
            <ProjectCard
              initial="M"
              name="Mars Colony OS"
              status="Draft"
              lastUpdated="1d ago"
              fileCount={1}
              agents={['architect']}
            />
          </div>
        </div>
        
        {/* Floating Action Button for smaller screens */}
                    <button 
          className="lg:hidden fixed bottom-6 right-6 bg-primary hover:bg-primary-hover text-white rounded-full p-4 shadow-lg shadow-primary/30"
        >
          <Plus size={24} />
                    </button>
                  </div>
    </>
  );
};

// StatCard Component
const StatCard = ({ icon, title, value }: { icon: React.ReactNode; title: string; value: string }) => (
  <div className="bg-card p-6 rounded-xl flex items-center space-x-4 border border-border/50">
    <div className="bg-primary/10 text-primary p-3 rounded-lg">
      {icon}
    </div>
    <div>
      <p className="text-sm text-gray-400">{title}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
                    </div>
              </div>
);

// ProjectCard Component
import { AgentAvatar, AgentRole } from '@/components/ui/AgentAvatar';

const ProjectCard = ({
  initial, name, status, lastUpdated, fileCount, agents
}: {
  initial: string; name: string; status: "Complete" | "Generating" | "Draft";
  lastUpdated: string; fileCount: number; agents: AgentRole[];
}) => {
  const statusConfig = {
    Complete: 'bg-accent-green/10 text-accent-green',
    Generating: 'bg-accent-yellow/10 text-accent-yellow animate-pulse',
    Draft: 'bg-gray-500/10 text-gray-400',
  };

  return (
    <div className="bg-card p-6 rounded-xl border border-transparent hover:border-primary transition-all duration-300 group">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 rounded-lg bg-primary/20 text-white flex items-center justify-center text-xl font-bold">
            {initial}
          </div>
          <h3 className="text-lg font-bold text-white group-hover:text-primary transition-colors">{name}</h3>
        </div>
        <span className={`px-3 py-1 text-xs font-semibold rounded-full ${statusConfig[status]}`}>
          {status}
        </span>
      </div>
      <p className="text-sm text-gray-500 mb-6">Last updated {lastUpdated}</p>
      <div className="flex items-center justify-between">
        <div className="flex -space-x-2">
          {agents.map(role => <AgentAvatar key={role} role={role} size="sm" />)}
        </div>
        <div className="text-sm text-gray-400 flex items-center space-x-2">
          <FileText size={16} />
          <span>{fileCount} Files</span>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
