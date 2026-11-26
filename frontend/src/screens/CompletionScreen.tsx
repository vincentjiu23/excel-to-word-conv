
import React, { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { ValidationResult } from '../types';
import {
  CheckCircle2,
  AlertTriangle,
  FileCheck,
  Copy,
  Check,
  RotateCcw,
  Download,
  Loader2,
} from 'lucide-react';

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
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState('');
  const [savedPath, setSavedPath] = useState('');

  const isTauri =
    typeof window !== 'undefined' &&
    '__TAURI_INTERNALS__' in window;

  const checksPassed = validationResult?.checks_passed ?? [];
  const checksFailed = validationResult?.checks_failed ?? [];

  const isSuccess = validationResult
    ? validationResult.is_valid
    : true;

  const fileExtension =
    outputPath.split('.').pop()?.toUpperCase() || 'FILE';

  const fileType =
    fileExtension === 'PDF'
      ? 'PDF document'
      : fileExtension === 'DOCX'
        ? 'Word document'
        : `${fileExtension} document`;

  const fileName =
    outputPath.split(/[\\/]/).pop() || 'converted_document';

  const handleCopyPath = async () => {
    try {
      await navigator.clipboard.writeText(outputPath);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy output path:', error);
    }
  };

  const handleDownload = async () => {
    if (!outputPath || downloading) return;

    setDownloading(true);
    setDownloadError('');
    setSavedPath('');

    try {
      // ================================================
      // TAURI DESKTOP: NATIVE WINDOWS SAVE DIALOG
      // ================================================

      if (isTauri) {
        const destination = await invoke<string | null>(
          'save_output_file',
          {
            sourcePath: outputPath,
            suggestedName: fileName,
          }
        );

        // User cancelled the Save As dialog.
        if (!destination) {
          return;
        }

        setSavedPath(destination);
        return;
      }

      // ================================================
      // BROWSER: FASTAPI DOWNLOAD
      // ================================================

      const downloadUrl =
        `http://127.0.0.1:8000/api/download?file_path=${encodeURIComponent(outputPath)}`;

      const response = await fetch(downloadUrl);

      if (!response.ok) {
        const errorText = await response.text();

        throw new Error(
          errorText || `Download failed (${response.status})`
        );
      }

      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = fileName;

      document.body.appendChild(link);
      link.click();
      link.remove();

      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      console.error('Download failed:', error);

      setDownloadError(
        error instanceof Error
          ? error.message
          : 'Failed to save file. Please try again.'
      );
    } finally {
      setDownloading(false);
    }
  };

  const formattedFileSize = Number.isFinite(fileSizeBytes)
    ? (fileSizeBytes / 1024).toFixed(1)
    : '0.0';

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 space-y-8">

      {/* Success Hero */}
      <div className="text-center space-y-3">
        <div className="w-16 h-16 mx-auto rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center shadow-lg">
          {isSuccess ? (
            <CheckCircle2 className="w-8 h-8" />
          ) : (
            <AlertTriangle className="w-8 h-8 text-amber-400" />
          )}
        </div>

        <h2 className="text-2xl font-bold text-white tracking-tight">
          {validationResult
            ? isSuccess
              ? 'Document Generated & Validated'
              : 'Conversion Completed with Warnings'
            : 'Document Generated Successfully'}
        </h2>

        <p className="text-xs text-[#adbac7] max-w-md mx-auto">
          Your {fileType} has been generated successfully from your template.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        <div className="bg-[#2d333b]/80 border border-[#444c56] rounded-xl p-4 text-center">
          <span className="text-xs text-[#adbac7] font-medium">
            Records Populated
          </span>
          <p className="text-xl font-bold text-emerald-400 mt-1">
            {(recordsWritten ?? 0).toLocaleString()}
          </p>
        </div>

        <div className="bg-[#2d333b]/80 border border-[#444c56] rounded-xl p-4 text-center">
          <span className="text-xs text-[#adbac7] font-medium">
            Output File Size
          </span>
          <p className="text-xl font-bold text-white mt-1">
            {formattedFileSize} KB
          </p>
        </div>

        <div className="bg-[#2d333b]/80 border border-[#444c56] rounded-xl p-4 text-center">
          <span className="text-xs text-[#adbac7] font-medium">
            Validation Status
          </span>
          <p className="text-xl font-bold text-[#539bf5] mt-1">
            {validationResult
              ? isSuccess
                ? 'Passed'
                : 'Needs Review'
              : 'Generated'}
          </p>
        </div>
      </div>

      {/* Output File Path */}
      <div className="bg-[#2d333b]/80 border border-[#444c56] rounded-xl p-4 space-y-2">
        <span className="text-xs font-semibold text-[#cdd9e5]">
          Generated File Path:
        </span>

        <div className="flex items-center gap-2">
          <input
            type="text"
            readOnly
            value={outputPath ?? ''}
            className="flex-1 min-w-0 bg-[#24292e] border border-[#444c56] rounded-lg px-3 py-2 text-xs text-[#cdd9e5] font-mono select-all focus:outline-none"
          />

          <button
            type="button"
            onClick={handleCopyPath}
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-[#373e47] hover:bg-slate-600 text-[#cdd9e5] text-xs font-semibold rounded-lg border border-[#545d68] transition"
          >
            {copied ? (
              <Check className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <Copy className="w-3.5 h-3.5" />
            )}

            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Download File */}
      <div className="bg-[#2d333b]/80 border border-[#444c56] rounded-xl p-5 space-y-3">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="text-center sm:text-left">
            <h3 className="text-sm font-semibold text-white">
              Your converted file is ready
            </h3>
            <p className="text-xs text-[#adbac7] mt-1 break-all">
              {fileName}
            </p>
          </div>

          <button
            type="button"
            onClick={handleDownload}
            disabled={downloading || !outputPath}
            className="flex items-center justify-center gap-2 px-6 py-3 min-w-[180px] bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 disabled:opacity-60 disabled:cursor-not-allowed text-white text-sm font-bold rounded-lg shadow-lg transition"
          >
            {downloading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>{isTauri ? 'Saving...' : 'Downloading...'}</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>{isTauri ? 'Save As...' : `Download ${fileExtension}`}</span>
              </>
            )}
          </button>
        </div>

        {savedPath && (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-300 text-xs">
            <div className="flex items-center gap-2 font-semibold">
              <CheckCircle2 className="w-4 h-4" />
              File saved successfully
            </div>
            <p className="mt-1 break-all">{savedPath}</p>
          </div>
        )}

        {downloadError && (
          <div className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-300 text-xs">
            <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Save failed</p>
              <p className="mt-1 break-words">{downloadError}</p>
              <p className="mt-1">
                Please check that the output file is accessible and try again.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Validation Checks */}
      {validationResult && (
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-5 space-y-3">

          <h3 className="text-sm font-semibold text-[#cdd9e5] flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-[#539bf5]" />
            Automated Output Validation Checklist
          </h3>

          <div className="space-y-2 text-xs">

            {checksPassed.map((chk, i) => (
              <div
                key={`passed-${i}`}
                className="flex items-start space-x-2 text-emerald-300"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>{chk}</span>
              </div>
            ))}

            {checksFailed.map((chk, i) => (
              <div
                key={`failed-${i}`}
                className="flex items-start space-x-2 text-rose-300"
              >
                <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0 mt-0.5" />
                <span>{chk}</span>
              </div>
            ))}

            {checksPassed.length === 0 &&
              checksFailed.length === 0 && (
                <p className="text-[#adbac7]">
                  Validation details are not available for this conversion.
                  The generated file is available at the path above.
                </p>
              )}
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
