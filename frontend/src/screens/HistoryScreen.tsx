import React, { useEffect, useState } from 'react';
import { ConversionRun } from '../types';
import { ApiService } from '../services/api';
import { History, CheckCircle2, AlertTriangle, FileSpreadsheet, FileText, Clock } from 'lucide-react';

export const HistoryScreen: React.FC = () => {
  const [runs, setRuns] = useState<ConversionRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    ApiService.getHistory(30)
      .then((data) => setRuns(data || []))
      .catch((err) => console.error('Failed to load history:', err))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 space-y-6">
      <div className="border-b border-[#444c56] pb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <History className="w-5 h-5 text-[#539bf5]" />
          Conversion History & SQLite Audit Log
        </h2>
        <p className="text-xs text-[#adbac7] mt-1">
          Historical record of executed document conversions, timestamps, and validation statuses.
        </p>
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-[#adbac7]">Loading conversion history...</div>
      ) : runs.length === 0 ? (
        <div className="bg-[#2d333b]/40 border border-[#444c56] rounded-xl p-12 text-center space-y-2">
          <Clock className="w-8 h-8 text-slate-600 mx-auto" />
          <h3 className="text-sm font-semibold text-[#cdd9e5]">No conversions recorded yet</h3>
          <p className="text-xs text-slate-500">Run your first conversion to see history and audit metrics here.</p>
        </div>
      ) : (
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl overflow-hidden shadow-sm">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-850 text-[#adbac7] border-b border-[#444c56] uppercase font-medium">
              <tr>
                <th className="py-2.5 px-4">Status</th>
                <th className="py-2.5 px-4">Date & Time</th>
                <th className="py-2.5 px-4">Records</th>
                <th className="py-2.5 px-4">Excel Source</th>
                <th className="py-2.5 px-4">Word Target</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/60 text-[#cdd9e5]">
              {runs.map((run) => (
                <tr key={run.id} className="hover:bg-slate-750 transition">
                  <td className="py-3 px-4">
                    {run.status === 'success' ? (
                      <span className="flex items-center space-x-1.5 text-emerald-400 font-semibold">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>Success</span>
                      </span>
                    ) : (
                      <span className="flex items-center space-x-1.5 text-amber-400 font-semibold">
                        <AlertTriangle className="w-4 h-4" />
                        <span>{run.status}</span>
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-[#adbac7] font-mono">
                    {new Date(run.created_at).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 font-semibold text-white">{run.record_count}</td>
                  <td className="py-3 px-4 font-mono text-[#cdd9e5] max-w-xs truncate" title={run.excel_path}>
                    {run.excel_path.split('\\').pop()?.split('/').pop()}
                  </td>
                  <td className="py-3 px-4 font-mono text-[#cdd9e5] max-w-xs truncate" title={run.output_path}>
                    {run.output_path.split('\\').pop()?.split('/').pop()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
