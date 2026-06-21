"use client";
import { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { AnalyticsStatsResponse, QueryHistoryResponse, QueryHistoryItem } from '../../lib/types';
import { BarChart, Activity, FileText, Target, Clock, X, AlertTriangle, Calendar, Award } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '../../lib/utils';
import { CitationCard } from '../../components/CitationCard';

export default function Analytics() {
  const [stats, setStats] = useState<AnalyticsStatsResponse | null>(null);
  const [history, setHistory] = useState<QueryHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedQuery, setSelectedQuery] = useState<QueryHistoryItem | null>(null);

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

  const renderContent = (text: string) => {
    const parts = text.split(/(\[SOURCE_\d+\])/g);
    return parts.map((part, i) => {
      if (part.match(/\[SOURCE_\d+\]/)) {
        return <span key={i} className="text-primary font-bold">{part}</span>;
      }
      return <span key={i}>{part}</span>;
    });
  };

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
                  <tr 
                    key={item.query_id} 
                    onClick={() => setSelectedQuery(item)}
                    className="hover:bg-muted/30 transition-colors cursor-pointer"
                  >
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

      {/* Query Detail Modal */}
      {selectedQuery && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 transition-opacity animate-in fade-in duration-200"
          onClick={() => setSelectedQuery(null)}
        >
          <div 
            className="bg-card border border-border w-full max-w-3xl max-h-[85vh] overflow-y-auto rounded-2xl p-6 shadow-2xl relative flex flex-col text-foreground animate-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-start justify-between pb-4 border-b border-border/80 mb-5">
              <div>
                <h2 className="text-xl font-bold">Query Execution Report</h2>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 mt-2 text-xs text-muted-foreground">
                  <div className="flex items-center space-x-1.5">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{new Date(selectedQuery.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <Award className="w-3.5 h-3.5 text-primary" />
                    <span>Confidence Score: {selectedQuery.confidence_score}%</span>
                  </div>
                </div>
              </div>
              <button 
                onClick={() => setSelectedQuery(null)}
                className="p-1.5 hover:bg-muted text-muted-foreground hover:text-foreground rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Question */}
            <div className="mb-5">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Question</h3>
              <div className="p-4 bg-muted/20 border border-border/80 rounded-xl font-semibold text-foreground">
                "{selectedQuery.question}"
              </div>
            </div>

            {/* Answer */}
            {selectedQuery.answer ? (
              <div className="mb-6">
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Answer</h3>
                <div className="p-5 bg-card border border-border/80 rounded-xl leading-relaxed whitespace-pre-wrap text-sm text-foreground">
                  {renderContent(selectedQuery.answer)}
                </div>
              </div>
            ) : (
              <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 rounded-xl text-sm flex items-start space-x-2">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>This query log doesn't contain generated answer details. (Only new queries after update will show answers).</span>
              </div>
            )}

            {/* Citations / Sources */}
            {selectedQuery.citations && selectedQuery.citations.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Sources Cited</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {selectedQuery.citations.map((cit, idx) => (
                    <CitationCard key={cit.chunk_id || idx} citation={cit} index={idx} />
                  ))}
                </div>
              </div>
            )}

            {/* Pipeline Timing Breakdown */}
            {selectedQuery.timing && (
              <div>
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Performance Breakdown</h3>
                <div className="space-y-3.5 bg-muted/20 border border-border/80 rounded-xl p-5">
                  {[
                    { name: 'Query Expansion', val: selectedQuery.timing.expansion_ms, color: 'bg-purple-500' },
                    { name: 'Document Retrieval', val: selectedQuery.timing.retrieval_ms, color: 'bg-blue-500' },
                    { name: 'Cross-Reranking', val: selectedQuery.timing.reranking_ms, color: 'bg-amber-500' },
                    { name: 'LLM Generation', val: selectedQuery.timing.generation_ms, color: 'bg-rose-500' },
                  ].map((metric) => {
                    const pct = selectedQuery.timing!.total_ms > 0 ? (metric.val / selectedQuery.timing!.total_ms) * 100 : 0;
                    return (
                      <div key={metric.name} className="space-y-1.5">
                        <div className="flex justify-between text-xs">
                          <span className="font-medium text-foreground">{metric.name}</span>
                          <span className="text-muted-foreground font-mono">{metric.val.toFixed(1)} ms ({pct.toFixed(0)}%)</span>
                        </div>
                        <div className="w-full bg-muted/50 rounded-full h-1.5 overflow-hidden">
                          <div className={cn("h-full rounded-full animate-pulse", metric.color)} style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                  <div className="pt-2 border-t border-border flex justify-between items-center text-xs font-semibold">
                    <span className="text-foreground">Total Execution Time</span>
                    <span className="text-primary font-mono text-sm">{selectedQuery.timing.total_ms.toFixed(1)} ms</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
