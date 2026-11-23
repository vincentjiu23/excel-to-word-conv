import React, { useState, useEffect } from 'react';
import { FieldMapping, SourceSchema, TargetSchema } from '../types';
import { ApiService } from '../services/api';
import { Eye, FileCheck, ArrowRight, ArrowLeft, Folder, Play } from 'lucide-react';

interface PreviewScreenProps {
  sourceSchema: SourceSchema | null;
  targetSchema: TargetSchema | null;
  mappings: FieldMapping[];
  selectedIndices: number[];
  outputPath: string;
  setOutputPath: (p: string) => void;
  onStartConversion: () => void;
  onBack: () => void;
}

export const PreviewScreen: React.FC<PreviewScreenProps> = ({
  sourceSchema,
  targetSchema,
  mappings,
  selectedIndices,
  outputPath,
  setOutputPath,
  onStartConversion,
  onBack,
}) => {
  const [previewRows, setPreviewRows] = useState<Record<string, any>[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (sourceSchema) {
      setIsLoading(true);
      ApiService.previewConversion(sourceSchema.preview_records, mappings, selectedIndices)
        .then((res) => {
          setPreviewRows(res.preview_records || []);
        })
        .catch((err) => {
          console.error('Failed to preview conversion:', err);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [sourceSchema, mappings, selectedIndices]);

  const activeMappings = mappings.filter((m) => m.status !== 'ignored');

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#444c56] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Eye className="w-5 h-5 text-[#539bf5]" />
            Conversion Preview
          </h2>
          <p className="text-xs text-[#adbac7] mt-1">
            Verify the exact mapped and formatted values before generating the final Word document.
          </p>
        </div>
      </div>

      {/* Output Destination Box */}
      <div className="bg-[#2d333b]/80 border border-[#444c56] rounded-xl p-4 space-y-2">
        <label className="text-xs font-semibold text-[#cdd9e5] flex items-center gap-2">
          <Folder className="w-4 h-4 text-emerald-400" />
          Output Word Document Location:
        </label>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={outputPath}
            onChange={(e) => setOutputPath(e.target.value)}
            placeholder="e.g. C:\output\converted_report.docx"
            className="flex-1 bg-[#24292e] border border-[#444c56] rounded-lg px-3 py-2 text-xs text-[#cdd9e5] focus:outline-none focus:border-emerald-500 font-mono"
          />
        </div>
        <p className="text-[11px] text-[#adbac7]">
          The original template is preserved without modification. A new validated DOCX file will be created.
        </p>
      </div>

      {/* Transformed Preview Table */}
      <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl overflow-hidden shadow-sm space-y-2">
        <div className="p-3 bg-[#2d333b] border-b border-[#444c56] flex items-center justify-between">
          <span className="text-xs font-semibold text-[#cdd9e5]">
            Target Mapped Values Preview ({selectedIndices.length} records selected)
          </span>
          {isLoading && <span className="text-xs text-[#539bf5] animate-pulse">Updating preview...</span>}
        </div>

        <div className="overflow-x-auto max-h-[380px]">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-850 text-[#adbac7] sticky top-0 border-b border-[#444c56] uppercase font-medium">
              <tr>
                <th className="py-2.5 px-4 w-12">#</th>
                {activeMappings.map((m) => (
                  <th key={m.target_field_id} className="py-2.5 px-4">
                    <div className="text-white font-semibold truncate">{m.target_name}</div>
                    <div className="text-[10px] text-[#adbac7] normal-case font-normal truncate">
                      from {m.source_name || (m.constant_value ? `"${m.constant_value}"` : 'blank')}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/60 text-[#cdd9e5]">
              {previewRows.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-750 transition">
                  <td className="py-2 px-4 font-mono text-slate-500">{idx + 1}</td>
                  {activeMappings.map((m) => (
                    <td key={m.target_field_id} className="py-2 px-4 max-w-xs truncate text-[#cdd9e5]">
                      {row[m.target_field_id] || (
                        <span className="text-slate-500 italic">empty</span>
                      )}
                    </td>
                  ))}
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
          <span>Back to Record Selection</span>
        </button>

        <button
          type="button"
          onClick={onStartConversion}
          className="flex items-center space-x-2 px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white text-xs font-bold rounded-lg shadow-lg cursor-pointer transition transform hover:scale-[1.01]"
        >
          <Play className="w-4 h-4 fill-white" />
          <span>Generate & Validate Word Document</span>
        </button>
      </div>
    </div>
  );
};
