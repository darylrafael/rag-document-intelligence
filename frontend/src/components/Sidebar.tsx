'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, MessageSquare, BarChart3, Database } from 'lucide-react';
import { cn } from '../lib/utils';

export function Sidebar() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Documents', icon: Database },
    { href: '/chat', label: 'Chat', icon: MessageSquare },
    { href: '/analytics', label: 'Analytics', icon: BarChart3 },
  ];

  return (
    <div className="w-64 border-r border-border bg-card/50 flex flex-col h-screen p-4">
      <div className="flex items-center space-x-2 px-2 mb-8 mt-2">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <LayoutDashboard className="w-5 h-5 text-primary-foreground" />
        </div>
        <span className="font-bold text-lg tracking-tight">RAG Intel</span>
      </div>
      
      <nav className="flex-1 space-y-1.5">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href;
          
          return (
            <Link 
              key={link.href} 
              href={link.href}
              className={cn(
                "flex items-center space-x-3 px-3 py-2.5 rounded-md transition-colors",
                isActive 
                  ? "bg-primary/10 text-primary font-medium" 
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon className={cn("w-5 h-5", isActive ? "text-primary" : "opacity-70")} />
              <span>{link.label}</span>
            </Link>
          );
        })}
      </nav>
      
      <div className="mt-auto p-4 bg-muted/30 rounded-lg text-xs text-muted-foreground text-center">
        Powered by DeepSeek V4 & ChromaDB
      </div>
    </div>
  );
}
