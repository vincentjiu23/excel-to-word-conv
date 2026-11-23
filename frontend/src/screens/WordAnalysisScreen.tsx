import React from 'react';
import { TargetSchema } from '../types';
import { FileText, Table, Tag, ArrowRight, ArrowLeft, CheckCircle2, AlertCircle } from 'lucide-react';

interface WordAnalysisScreenProps {
  targetSchema: TargetSchema | null;
  selectedTableIndex: number;
  setSelectedTableIndex: (idx: number) => void;
  selectedStrategy: string;
  setSelectedStrategy: (s: string) => void;
  onContinue: () => void;
  onBack: () => void;
}

export const WordAnalysisScreen: React.FC<WordAnalysisScreenProps> = ({
  targetSchema,
  selectedTableIndex,
  setSelectedTableIndex,
  selectedStrategy,
  setSelectedStrategy,
  onContinue,
  onBack,
}) => {
  if (!targetSchema) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center text-[#adbac7]">
        Loading Word template structure...
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#444c56] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-[#539bf5]" />
            Word Template Structure Analysis
          </h2>
          <p className="text-xs text-[#adbac7] mt-1">
            Template: <span className="text-[#cdd9e5] font-mono">{targetSchema.file_path}</span>
          </p>
        </div>

        {/* Strategy Selector */}
        <div className="flex items-center space-x-2">
          <label className="text-xs font-semibold text-[#cdd9e5]">Insertion Strategy:</label>
          <select
            value={selectedStrategy || targetSchema.recommended_strategy}
            onChange={(e) => setSelectedStrategy(e.target.value)}
            className="bg-[#2d333b] border border-[#444c56] rounded-lg px-2.5 py-1.5 text-xs text-[#cdd9e5] focus:outline-none focus:border-sky-500 font-semibold"
          >
            {targetSchema.candidate_strategies.map((strat) => (
              <option key={strat} value={strat}>
                {strat.replace(/_/g, ' ').toUpperCase()} {strat === targetSchema.recommended_strategy ? '(Recommended)' : ''}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Structure Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-3.5">
          <span className="text-xs text-[#adbac7]">Tables Detected</span>
          <p className="text-lg font-bold text-white mt-1">{targetSchema.structure.table_count}</p>
        </div>
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-3.5">
          <span className="text-xs text-[#adbac7]">Placeholders Discovered</span>
          <p className="text-lg font-bold text-[#539bf5] mt-1">{targetSchema.structure.placeholder_count}</p>
        </div>
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-3.5">
          <span className="text-xs text-[#adbac7]">Target Fields</span>
          <p className="text-lg font-bold text-white mt-1">{targetSchema.fields.length}</p>
        </div>
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-3.5">
          <span className="text-xs text-[#adbac7]">Headers & Footers</span>
          <p className="text-lg font-bold text-white mt-1">{targetSchema.structure.has_headers_footers ? 'Preserved' : 'None'}</p>
        </div>
      </div>

      {/* Discovered Tables & Placeholders */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Tables Card */}
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-4 space-y-3">
          <h3 className="text-sm font-semibold text-[#cdd9e5] flex items-center gap-2">
            <Table className="w-4 h-4 text-[#539bf5]" />
            Detected Tables ({targetSchema.tables.length})
          </h3>
          {targetSchema.tables.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No tables detected in template.</p>
          ) : (
            <div className="space-y-2">
              {targetSchema.tables.map((t, idx) => (
                <div
                  key={idx}
                  onClick={() => setSelectedTableIndex(idx)}
                  className={`p-3 rounded-lg border text-xs cursor-pointer transition ${
                    selectedTableIndex === idx
                      ? 'border-sky-500 bg-[#539bf5]/10 text-white'
                      : 'border-[#444c56] bg-[#1f2428]/70 text-[#cdd9e5] hover:border-[#545d68]'
                  }`}
                >
                  <div className="flex items-center justify-between font-semibold">
                    <span>Table {idx + 1}</span>
                    <span className="font-mono text-[#adbac7]">
                      {t.row_count} rows × {t.col_count} cols
                    </span>
                  </div>
                  {t.sample_headers.length > 0 && (
                    <div className="mt-1 text-[#adbac7] truncate">
                      Headers: {t.sample_headers.slice(0, 4).join(', ')}...
                    </div>
                  )}
                  {t.has_merged_cells && (
                    <div className="mt-1 text-amber-400 flex items-center gap-1 text-[11px]">
                      <AlertCircle className="w-3 h-3" />
                      <span>Contains merged cells (preserved during cloning)</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Target Fields Card */}
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-4 space-y-3">
          <h3 className="text-sm font-semibold text-[#cdd9e5] flex items-center gap-2">
            <Tag className="w-4 h-4 text-emerald-400" />
            Extracted Insertion Targets ({targetSchema.fields.length})
          </h3>
          <div className="space-y-1.5 max-h-64 overflow-y-auto pr-1">
            {targetSchema.fields.map((f) => (
              <div
                key={f.field_id}
                className="bg-[#1f2428]/80 border border-[#444c56]/70 rounded px-2.5 py-1.5 text-xs flex items-center justify-between"
              >
                <span className="font-medium text-[#cdd9e5]">{f.original_name}</span>
                <span className="text-[10px] uppercase font-semibold text-[#539bf5] bg-[#539bf5]/10 px-2 py-0.5 rounded border border-sky-500/20">
                  {f.location.type || 'field'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer Navigation */}
      <div className="flex items-center justify-between pt-2">
        <button
          type="button"
          onClick={onBack}
          className="flex items-center space-x-1.5 px-4 py-2 bg-[#2d333b] hover:bg-[#444c56] text-[#cdd9e5] text-xs font-semibold rounded-lg border border-[#444c56] transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Excel</span>
        </button>

        <button
          type="button"
          onClick={onContinue}
          className="flex items-center space-x-1.5 px-5 py-2 bg-[#347d39] hover:bg-[#46954a] text-white text-xs font-semibold rounded-lg shadow transition"
        >
          <span>Continue to Mapping</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
