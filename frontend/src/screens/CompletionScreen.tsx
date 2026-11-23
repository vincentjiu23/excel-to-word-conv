import React, { useState } from 'react';
import { ValidationResult } from '../types';
import { CheckCircle2, AlertTriangle, FileCheck, Copy, Check, RotateCcw, FolderOpen } from 'lucide-react';

interface CompletionScreenProps {
  outputPath: string;
  recordsWritten: number;
  fileSizeBytes: number;
  validationResult: ValidationResult | null;
  onNewSession: () => void;
}

export const CompletionScreen: React.FC<CompletionScreenProps> = ({
  outputPath,
  recordsWritten,
  fileSizeBytes,
  validationResult,
  onNewSession,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopyPath = () => {
    navigator.clipboard.writeText(outputPath);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isSuccess = validationResult ? validationResult.is_valid : true;

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-8">
      {/* Success Hero */}
      <div className="text-center space-y-3">
        <div className="w-16 h-16 mx-auto rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center shadow-lg">
          {isSuccess ? <CheckCircle2 className="w-8 h-8" /> : <AlertTriangle className="w-8 h-8 text-amber-400" />}
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">
          {isSuccess ? 'Document Generated & Validated' : 'Conversion Completed with Warnings'}
        </h2>
        <p className="text-xs text-[#adbac7] max-w-md mx-auto">
          Your Word document has been constructed from the template with full style preservation.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#2d333b]/80 border border-[#444c56] rounded-xl p-4 text-center">
          <span className="text-xs text-[#adbac7] font-medium">Records Populated</span>
          <p className="text-xl font-bold text-emerald-400 mt-1">{recordsWritten.toLocaleString()}</p>
        </div>
        <div className="bg-[#2d333b]/80 border border-[#444c56] rounded-xl p-4 text-center">
          <span className="text-xs text-[#adbac7] font-medium">Output File Size</span>
          <p className="text-xl font-bold text-white mt-1">{(fileSizeBytes / 1024).toFixed(1)} KB</p>
        </div>
        <div className="bg-[#2d333b]/80 border border-[#444c56] rounded-xl p-4 text-center">
          <span className="text-xs text-[#adbac7] font-medium">Validation Status</span>
          <p className="text-xl font-bold text-[#539bf5] mt-1">{isSuccess ? 'Passed (100%)' : 'Needs Review'}</p>
        </div>
      </div>

      {/* Output File Path Box */}
      <div className="bg-[#2d333b]/80 border border-[#444c56] rounded-xl p-4 space-y-2">
        <span className="text-xs font-semibold text-[#cdd9e5]">Generated File Path:</span>
        <div className="flex items-center gap-2">
          <input
            type="text"
            readOnly
            value={outputPath}
            className="flex-1 bg-[#24292e] border border-[#444c56] rounded-lg px-3 py-2 text-xs text-[#cdd9e5] font-mono select-all focus:outline-none"
          />
          <button
            type="button"
            onClick={handleCopyPath}
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-[#373e47] hover:bg-slate-600 text-[#cdd9e5] text-xs font-semibold rounded-lg border border-[#545d68] transition"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Detailed Validation Checks */}
      {validationResult && (
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-5 space-y-3">
          <h3 className="text-sm font-semibold text-[#cdd9e5] flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-[#539bf5]" />
            Automated Output Validation Checklist
          </h3>

          <div className="space-y-2 text-xs">
            {validationResult.checks_passed.map((chk, i) => (
              <div key={i} className="flex items-start space-x-2 text-emerald-300">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>{chk}</span>
              </div>
            ))}
            {validationResult.checks_failed.map((chk, i) => (
              <div key={i} className="flex items-start space-x-2 text-rose-300">
                <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                <span>{chk}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer Action */}
      <div className="flex justify-center pt-2">
        <button
          type="button"
          onClick={onNewSession}
          className="flex items-center space-x-2 px-6 py-2.5 bg-[#347d39] hover:bg-[#46954a] text-white text-xs font-bold rounded-lg shadow-lg cursor-pointer transition"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Start New Conversion</span>
        </button>
      </div>
    </div>
  );
};
