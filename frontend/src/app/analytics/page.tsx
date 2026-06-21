"use client";
import { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { AnalyticsStatsResponse, QueryHistoryResponse } from '../../lib/types';
import { BarChart, Activity, FileText, Target, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '../../lib/utils';

export default function Analytics() {
  const [stats, setStats] = useState<AnalyticsStatsResponse | null>(null);
  const [history, setHistory] = useState<QueryHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [s, h] = await Promise.all([
          api.analytics.getStats(),
          api.analytics.getHistory()
        ]);
        setStats(s);
        setHistory(h);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  if (isLoading) {
    return <div className="p-8 max-w-6xl mx-auto animate-pulse flex space-x-4">Loading analytics...</div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8 flex items-center space-x-3">
        <div className="p-3 bg-primary/10 rounded-xl text-primary">
          <BarChart className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">System Analytics</h1>
          <p className="text-muted-foreground">Performance and usage metrics</p>
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-between">
            <div className="flex items-center justify-between text-muted-foreground mb-4">
              <span className="font-medium text-sm">Total Documents</span>
              <FileText className="w-5 h-5" />
            </div>
            <div className="text-4xl font-bold text-foreground">{stats.total_documents}</div>
          </div>
          
          <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-between">
            <div className="flex items-center justify-between text-muted-foreground mb-4">
              <span className="font-medium text-sm">Total Queries</span>
              <Activity className="w-5 h-5" />
            </div>
            <div className="text-4xl font-bold text-foreground">{stats.total_queries}</div>
          </div>

          <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-between">
            <div className="flex items-center justify-between text-muted-foreground mb-4">
              <span className="font-medium text-sm">Avg Confidence</span>
              <Target className="w-5 h-5" />
            </div>
            <div className="text-4xl font-bold text-foreground">
              {stats.avg_confidence > 0 ? stats.avg_confidence.toFixed(1) : 0}<span className="text-xl text-muted-foreground ml-1">/ 100</span>
            </div>
          </div>
        </div>
      )}

      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Queries</h2>
        {history?.items && history.items.length > 0 ? (
          <div className="bg-card border border-border rounded-xl overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead className="bg-muted/50 border-b border-border">
                <tr>
                  <th className="px-6 py-4 font-medium text-muted-foreground">Query</th>
                  <th className="px-6 py-4 font-medium text-muted-foreground w-32">Confidence</th>
                  <th className="px-6 py-4 font-medium text-muted-foreground w-48">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {history.items.map((item) => (
                  <tr key={item.query_id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-6 py-4 text-foreground font-medium">{item.question}</td>
                    <td className="px-6 py-4">
                      <span className={cn(
                        "px-2.5 py-1 rounded-full text-xs font-semibold",
                        item.confidence_score >= 80 ? "bg-green-500/10 text-green-500" :
                        item.confidence_score >= 50 ? "bg-yellow-500/10 text-yellow-500" :
                        "bg-destructive/10 text-destructive"
                      )}>
                        {item.confidence_score}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-muted-foreground flex items-center space-x-1.5">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{formatDistanceToNow(new Date(item.timestamp))} ago</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-8 text-center text-muted-foreground border border-border rounded-xl bg-card">
            No queries have been made yet.
          </div>
        )}
      </div>
    </div>
  );
}
