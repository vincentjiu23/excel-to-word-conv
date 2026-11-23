import React from 'react';
import { SourceSchema } from '../types';
import { FileSpreadsheet, AlertTriangle, ArrowRight, ArrowLeft, Hash, Layers } from 'lucide-react';

interface ExcelAnalysisScreenProps {
  sourceSchema: SourceSchema | null;
  selectedSheet: string;
  onSheetChange: (sheet: string) => void;
  headerOverride: number | undefined;
  setHeaderOverride: (row: number | undefined) => void;
  onReanalyze: () => void;
  onContinue: () => void;
  onBack: () => void;
}

export const ExcelAnalysisScreen: React.FC<ExcelAnalysisScreenProps> = ({
  sourceSchema,
  selectedSheet,
  onSheetChange,
  headerOverride,
  setHeaderOverride,
  onReanalyze,
  onContinue,
  onBack,
}) => {
  if (!sourceSchema) {
    return (
      <div className="max-w-4xl mx-auto py-12 text-center text-[#adbac7]">
        Loading Excel workbook schema...
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-6 px-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#444c56] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-emerald-400" />
            Excel Dynamic Schema Discovery
          </h2>
          <p className="text-xs text-[#adbac7] mt-1">
            Workbook: <span className="text-[#cdd9e5] font-mono">{sourceSchema.file_path}</span>
          </p>
        </div>

        {/* Sheet and Header Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {sourceSchema.available_sheets.length > 1 && (
            <div className="flex items-center space-x-2">
              <label className="text-xs font-semibold text-[#cdd9e5]">Sheet:</label>
              <select
                value={selectedSheet || sourceSchema.sheet_name}
                onChange={(e) => onSheetChange(e.target.value)}
                className="bg-[#2d333b] border border-[#444c56] rounded-lg px-2.5 py-1.5 text-xs text-[#cdd9e5] focus:outline-none focus:border-emerald-500"
              >
                {sourceSchema.available_sheets.map((s) => (
                  <option key={s.name} value={s.name}>
                    {s.name} {s.is_hidden ? '(Hidden)' : ''}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="flex items-center space-x-2">
            <label className="text-xs font-semibold text-[#cdd9e5]">Header Row:</label>
            <input
              type="number"
              min={1}
              value={headerOverride !== undefined ? headerOverride : sourceSchema.header_row_index}
              onChange={(e) => {
                const val = parseInt(e.target.value, 10);
                setHeaderOverride(isNaN(val) ? undefined : val);
              }}
              className="w-16 bg-[#2d333b] border border-[#444c56] rounded-lg px-2 py-1.5 text-xs text-center text-[#cdd9e5] focus:outline-none focus:border-emerald-500"
            />
            <button
              type="button"
              onClick={onReanalyze}
              className="px-2.5 py-1.5 bg-[#373e47] hover:bg-slate-600 text-[#cdd9e5] text-xs font-semibold rounded-lg border border-[#545d68] transition"
            >
              Apply
            </button>
          </div>
        </div>
      </div>

      {/* Warnings & Metrics */}
      {sourceSchema.warnings.length > 0 && (
        <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-3.5 space-y-1">
          <div className="flex items-center space-x-2 text-amber-400 font-semibold text-xs">
            <AlertTriangle className="w-4 h-4" />
            <span>Detection Warnings ({sourceSchema.warnings.length})</span>
          </div>
          <ul className="text-xs text-amber-200/90 list-disc list-inside space-y-0.5">
            {sourceSchema.warnings.map((w, idx) => (
              <li key={idx}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-3.5">
          <span className="text-xs text-[#adbac7]">Total Records</span>
          <p className="text-lg font-bold text-white mt-1">{sourceSchema.total_rows.toLocaleString()}</p>
        </div>
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-3.5">
          <span className="text-xs text-[#adbac7]">Discovered Columns</span>
          <p className="text-lg font-bold text-white mt-1">{sourceSchema.total_cols}</p>
        </div>
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-3.5">
          <span className="text-xs text-[#adbac7]">Header Location</span>
          <p className="text-lg font-bold text-emerald-400 mt-1">Row {sourceSchema.header_row_index}</p>
        </div>
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-3.5">
          <span className="text-xs text-[#adbac7]">Formulas Handled</span>
          <p className="text-lg font-bold text-white mt-1">{sourceSchema.has_formulas ? `${sourceSchema.formula_count} cached` : 'None'}</p>
        </div>
      </div>

      {/* Discovered Dynamic Fields Table */}
      <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl overflow-hidden shadow-sm">
        <div className="p-3.5 bg-[#2d333b] border-b border-[#444c56] flex items-center justify-between">
          <h3 className="text-sm font-semibold text-[#cdd9e5] flex items-center gap-2">
            <Layers className="w-4 h-4 text-emerald-400" />
            Dynamic Schema Fields ({sourceSchema.fields.length})
          </h3>
          <span className="text-xs text-[#adbac7]">All fields dynamically inferred from content</span>
        </div>

        <div className="overflow-x-auto max-h-96">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-850 text-[#adbac7] sticky top-0 border-b border-[#444c56] uppercase font-medium">
              <tr>
                <th className="py-2.5 px-4">Col</th>
                <th className="py-2.5 px-4">Original Header</th>
                <th className="py-2.5 px-4">Normalized</th>
                <th className="py-2.5 px-4">Inferred Type</th>
                <th className="py-2.5 px-4">Sample Values</th>
                <th className="py-2.5 px-4">Nulls</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/60 text-[#cdd9e5]">
              {sourceSchema.fields.map((field) => (
                <tr key={field.field_id} className="hover:bg-slate-750 transition">
                  <td className="py-2 px-4 font-mono text-[#adbac7]">{field.location.column_letter || '-'}</td>
                  <td className="py-2 px-4 font-semibold text-white">{field.original_name}</td>
                  <td className="py-2 px-4 font-mono text-[#adbac7]">{field.normalized_name}</td>
                  <td className="py-2 px-4">
                    <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      {field.data_type}
                    </span>
                  </td>
                  <td className="py-2 px-4 max-w-xs truncate text-[#cdd9e5]">
                    {field.sample_values.slice(0, 3).map((s, i) => (
                      <span key={i} className="inline-block bg-[#24292e] px-1.5 py-0.5 rounded mr-1 text-[#cdd9e5]">
                        {String(s)}
                      </span>
                    ))}
                  </td>
                  <td className="py-2 px-4 text-[#adbac7]">{field.null_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
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
          <span>Change Documents</span>
        </button>

        <button
          type="button"
          onClick={onContinue}
          className="flex items-center space-x-1.5 px-5 py-2 bg-[#347d39] hover:bg-[#46954a] text-white text-xs font-semibold rounded-lg shadow transition"
        >
          <span>Continue to Word Analysis</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
