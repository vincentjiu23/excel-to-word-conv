import React, { useState } from 'react';
import { UploadCloud, FileSpreadsheet, FileText, ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react';

interface UploadScreenProps {
  excelPath: string;
  wordPath: string;
  setExcelPath: (p: string) => void;
  setWordPath: (p: string) => void;
  onContinue: () => void;
  onLoadExample: (exampleKey: 'medical' | 'shipping' | 'astronomy') => void;
}

export const UploadScreen: React.FC<UploadScreenProps> = ({
  excelPath,
  wordPath,
  setExcelPath,
  setWordPath,
  onContinue,
  onLoadExample,
}) => {
  const [dragOverExcel, setDragOverExcel] = useState(false);
  const [dragOverWord, setDragOverWord] = useState(false);

  const canProceed = excelPath.trim().length > 0 && wordPath.trim().length > 0;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white tracking-tight">Select Input Documents</h2>
        <p className="text-sm text-[#adbac7] max-w-xl mx-auto">
          Upload any Excel workbook and Word template. The application will dynamically discover their schemas with zero
          hardcoded assumptions.
        </p>
      </div>

      {/* Example Presets Bar */}
      <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="flex items-center space-x-2 text-[#539bf5] text-sm font-medium">
          <Sparkles className="w-4 h-4" />
          <span>Quick Load Test Domains:</span>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => onLoadExample('medical')}
            className="px-3 py-1 bg-[#373e47] hover:bg-slate-600 text-[#cdd9e5] text-xs font-semibold rounded-lg border border-[#545d68] transition"
          >
            Clinical Patients (.xlsx + .docx)
          </button>
          <button
            type="button"
            onClick={() => onLoadExample('shipping')}
            className="px-3 py-1 bg-[#373e47] hover:bg-slate-600 text-[#cdd9e5] text-xs font-semibold rounded-lg border border-[#545d68] transition"
          >
            Maritime Cargo (.xlsx + .docx)
          </button>
          <button
            type="button"
            onClick={() => onLoadExample('astronomy')}
            className="px-3 py-1 bg-[#373e47] hover:bg-slate-600 text-[#cdd9e5] text-xs font-semibold rounded-lg border border-[#545d68] transition"
          >
            Astrophysics Telemetry (.xlsx + .docx)
          </button>
        </div>
      </div>

      {/* Upload Boxes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Excel Box */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOverExcel(true);
          }}
          onDragLeave={() => setDragOverExcel(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOverExcel(false);
            if (e.dataTransfer.files.length > 0) {
              const f = e.dataTransfer.files[0];
              setExcelPath((f as any).path || f.name);
            }
          }}
          className={`border-2 border-dashed rounded-xl p-6 transition flex flex-col items-center justify-center text-center space-y-3 ${
            dragOverExcel
              ? 'border-emerald-500 bg-emerald-500/10'
              : excelPath
              ? 'border-emerald-500/50 bg-[#2d333b]/80'
              : 'border-[#444c56] bg-[#2d333b]/40 hover:border-[#545d68]'
          }`}
        >
          <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
            <FileSpreadsheet className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">Source Excel File</h3>
            <p className="text-xs text-[#adbac7] mt-1">Supports .xlsx with multiple sheets and formulas</p>
          </div>

          <div className="w-full mt-2">
            <input
              type="text"
              value={excelPath}
              onChange={(e) => setExcelPath(e.target.value)}
              placeholder="e.g. C:\data\records.xlsx"
              className="w-full bg-[#24292e] border border-[#444c56] rounded-lg px-3 py-2 text-xs text-[#cdd9e5] placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          {excelPath && (
            <div className="flex items-center space-x-1.5 text-xs text-emerald-400 font-medium">
              <CheckCircle2 className="w-4 h-4" />
              <span>Ready for dynamic analysis</span>
            </div>
          )}
        </div>

        {/* Word Box */}
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOverWord(true);
          }}
          onDragLeave={() => setDragOverWord(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOverWord(false);
            if (e.dataTransfer.files.length > 0) {
              const f = e.dataTransfer.files[0];
              setWordPath((f as any).path || f.name);
            }
          }}
          className={`border-2 border-dashed rounded-xl p-6 transition flex flex-col items-center justify-center text-center space-y-3 ${
            dragOverWord
              ? 'border-sky-500 bg-[#539bf5]/10'
              : wordPath
              ? 'border-sky-500/50 bg-[#2d333b]/80'
              : 'border-[#444c56] bg-[#2d333b]/40 hover:border-[#545d68]'
          }`}
        >
          <div className="w-12 h-12 rounded-full bg-[#539bf5]/15 text-[#539bf5] flex items-center justify-center">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">Target Word Template</h3>
            <p className="text-xs text-[#adbac7] mt-1">Supports tables, placeholders, and form layouts</p>
          </div>

          <div className="w-full mt-2">
            <input
              type="text"
              value={wordPath}
              onChange={(e) => setWordPath(e.target.value)}
              placeholder="e.g. C:\templates\report.docx"
              className="w-full bg-[#24292e] border border-[#444c56] rounded-lg px-3 py-2 text-xs text-[#cdd9e5] placeholder-slate-500 focus:outline-none focus:border-sky-500"
            />
          </div>

          {wordPath && (
            <div className="flex items-center space-x-1.5 text-xs text-[#539bf5] font-medium">
              <CheckCircle2 className="w-4 h-4" />
              <span>Ready for structure inspection</span>
            </div>
          )}
        </div>
      </div>

      {/* Action Footer */}
      <div className="flex justify-end pt-4">
        <button
          type="button"
          disabled={!canProceed}
          onClick={onContinue}
          className={`flex items-center space-x-2 px-6 py-2.5 rounded-lg text-sm font-semibold transition shadow-lg ${
            canProceed
              ? 'bg-[#347d39] hover:bg-[#46954a] text-white cursor-pointer'
              : 'bg-[#2d333b] text-slate-500 cursor-not-allowed border border-[#444c56]'
          }`}
        >
          <span>Analyze Documents</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
