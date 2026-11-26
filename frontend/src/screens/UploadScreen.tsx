
import React, { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import {
  FileSpreadsheet,
  FileText,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  FileType,
  FolderOpen,
  Loader2,
} from 'lucide-react';

type ExampleKey =
  | 'medical'
  | 'shipping'
  | 'astronomy'
  | 'medical-pdf';

type FileKind = 'excel' | 'word' | 'pdf';

interface UploadScreenProps {
  excelPath: string;
  wordPath: string;
  setExcelPath: (p: string) => void;
  setWordPath: (p: string) => void;
  templateType: 'word' | 'pdf';
  setTemplateType: (type: 'word' | 'pdf') => void;
  onContinue: () => void;
  onLoadExample: (exampleKey: ExampleKey) => void;
}

export const UploadScreen: React.FC<UploadScreenProps> = ({
  excelPath,
  wordPath,
  setExcelPath,
  setWordPath,
  templateType,
  setTemplateType,
  onContinue,
  onLoadExample,
}) => {
  const [templateError, setTemplateError] = useState('');
  const [excelError, setExcelError] = useState('');
  const [pickerError, setPickerError] = useState('');
  const [loadingPicker, setLoadingPicker] = useState<FileKind | null>(null);

  const canProceed =
    excelPath.trim().length > 0 &&
    wordPath.trim().length > 0 &&
    !templateError &&
    !excelError;

  const validateExcel = (path: string) => {
    if (!path.trim()) {
      setExcelError('');
      return;
    }

    const extension = path.split(/[\\/]/).pop()?.split('.').pop()?.toLowerCase();

    setExcelError(
      extension === 'xlsx'
        ? ''
        : 'File Excel harus menggunakan format .xlsx'
    );
  };

  const validateTemplate = (
    path: string,
    type: 'word' | 'pdf'
  ) => {
    if (!path.trim()) {
      setTemplateError('');
      return;
    }

    const extension = path.split(/[\\/]/).pop()?.split('.').pop()?.toLowerCase();

    if (type === 'word' && extension !== 'docx') {
      setTemplateError('Word template harus menggunakan file .docx');
      return;
    }

    if (type === 'pdf' && extension !== 'pdf') {
      setTemplateError('PDF template harus menggunakan file .pdf');
      return;
    }

    setTemplateError('');
  };

  const handlePickFile = async (kind: FileKind) => {
    setPickerError('');
    setLoadingPicker(kind);

    try {
      const selectedPath = await invoke<string | null>('pick_file', {
        kind,
      });

      // User menekan Cancel pada dialog Windows.
      if (!selectedPath) {
        return;
      }

      if (kind === 'excel') {
        setExcelPath(selectedPath);
        validateExcel(selectedPath);
      } else {
        setWordPath(selectedPath);
        validateTemplate(selectedPath, kind);
      }
    } catch (error) {
      console.error('File picker error:', error);
      setPickerError(
        `Tidak dapat membuka file picker: ${String(error)}`
      );
    } finally {
      setLoadingPicker(null);
    }
  };

  const handleTemplateChange = (path: string) => {
    setWordPath(path);
    validateTemplate(path, templateType);
  };

  const handleTemplateTypeChange = (type: 'word' | 'pdf') => {
    setTemplateType(type);
    setWordPath('');
    setTemplateError('');
    setPickerError('');
  };

  const handleQuickLoad = (exampleKey: ExampleKey) => {
    setTemplateError('');
    setExcelError('');
    setPickerError('');
    onLoadExample(exampleKey);
  };

  const BrowseButton = ({
    kind,
    label,
  }: {
    kind: FileKind;
    label: string;
  }) => (
    <button
      type="button"
      onClick={() => handlePickFile(kind)}
      disabled={loadingPicker !== null}
      className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg
        bg-[#373e47] hover:bg-slate-600 border border-[#545d68]
        text-[#cdd9e5] text-xs font-semibold transition
        disabled:opacity-50 disabled:cursor-wait"
    >
      {loadingPicker === kind ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <FolderOpen className="w-4 h-4" />
      )}
      {loadingPicker === kind ? 'Opening...' : label}
    </button>
  );

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-8">

      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white tracking-tight">
          Select Input Documents
        </h2>

        <p className="text-sm text-[#adbac7] max-w-xl mx-auto">
          Upload an Excel workbook and select your target document template.
          The application dynamically discovers document fields.
        </p>
      </div>

      {/* Example Presets */}
      <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-4
        flex flex-col md:flex-row items-center justify-between gap-3">

        <div className="flex items-center space-x-2 text-[#539bf5] text-sm font-medium">
          <Sparkles className="w-4 h-4" />
          <span>Quick Load Test Domains:</span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => handleQuickLoad('medical')}
            className="px-3 py-1 bg-[#373e47] hover:bg-slate-600
              text-[#cdd9e5] text-xs font-semibold rounded-lg
              border border-[#545d68] transition"
          >
            Clinical Patients (.xlsx + .docx)
          </button>

          <button
            type="button"
            onClick={() => handleQuickLoad('shipping')}
            className="px-3 py-1 bg-[#373e47] hover:bg-slate-600
              text-[#cdd9e5] text-xs font-semibold rounded-lg
              border border-[#545d68] transition"
          >
            Maritime Cargo (.xlsx + .docx)
          </button>

          <button
            type="button"
            onClick={() => handleQuickLoad('astronomy')}
            className="px-3 py-1 bg-[#373e47] hover:bg-slate-600
              text-[#cdd9e5] text-xs font-semibold rounded-lg
              border border-[#545d68] transition"
          >
            Astrophysics Telemetry (.xlsx + .docx)
          </button>

          <button
            type="button"
            onClick={() => handleQuickLoad('medical-pdf')}
            className="px-3 py-1 bg-rose-500/10 hover:bg-rose-500/20
              text-rose-300 text-xs font-semibold rounded-lg
              border border-rose-500/40 transition"
          >
            Medical PDF Template (.xlsx + .pdf)
          </button>
        </div>
      </div>

      {/* Upload Areas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Excel Upload */}
        <div className={`border-2 border-dashed rounded-xl p-6
          flex flex-col items-center text-center space-y-4
          ${excelPath && !excelError
            ? 'border-emerald-500/50 bg-[#2d333b]/80'
            : 'border-[#444c56] bg-[#2d333b]/40'
          }`}>

          <div className="w-12 h-12 rounded-full bg-emerald-500/20
            text-emerald-400 flex items-center justify-center">
            <FileSpreadsheet className="w-6 h-6" />
          </div>

          <div>
            <h3 className="text-base font-semibold text-white">
              Source Excel File
            </h3>

            <p className="text-xs text-[#adbac7] mt-1">
              Supports .xlsx with multiple sheets and formulas
            </p>
          </div>

          <div className="w-full space-y-2">
            <input
              type="text"
              value={excelPath}
              onChange={(e) => {
                setExcelPath(e.target.value);
                validateExcel(e.target.value);
              }}
              placeholder="Full path to Excel file"
              className="w-full bg-[#24292e] border border-[#444c56]
                rounded-lg px-3 py-2.5 text-xs text-[#cdd9e5]
                placeholder-slate-500 focus:outline-none
                focus:border-emerald-500"
            />

            <div className="flex justify-center">
              <BrowseButton kind="excel" label="Browse Excel File" />
            </div>
          </div>

          {excelError && (
            <p className="text-xs text-red-400 font-medium">
              {excelError}
            </p>
          )}

          {excelPath && !excelError && (
            <div className="flex items-center space-x-1.5
              text-xs text-emerald-400 font-medium">
              <CheckCircle2 className="w-4 h-4" />
              <span>Excel file selected</span>
            </div>
          )}
        </div>

        {/* Template Upload */}
        <div className={`border-2 border-dashed rounded-xl p-6
          flex flex-col items-center text-center space-y-4
          ${wordPath && !templateError
            ? 'border-sky-500/50 bg-[#2d333b]/80'
            : 'border-[#444c56] bg-[#2d333b]/40'
          }`}>

          <div className="w-12 h-12 rounded-full bg-[#539bf5]/15
            text-[#539bf5] flex items-center justify-center">
            <FileText className="w-6 h-6" />
          </div>

          <div>
            <h3 className="text-base font-semibold text-white">
              Target Document Template
            </h3>

            <p className="text-xs text-[#adbac7] mt-1">
              Select your template format
            </p>
          </div>

          {/* Template Type Selector */}
          <div className="grid grid-cols-2 gap-2 w-full">
            <button
              type="button"
              onClick={() => handleTemplateTypeChange('word')}
              className={`flex items-center justify-center gap-2 px-3 py-3
                rounded-lg border text-sm font-semibold transition
                ${templateType === 'word'
                  ? 'bg-[#539bf5]/20 border-[#539bf5] text-[#79c0ff]'
                  : 'bg-[#24292e] border-[#444c56] text-[#adbac7]'
                }`}
            >
              <FileText className="w-4 h-4" />
              Word DOCX
            </button>

            <button
              type="button"
              onClick={() => handleTemplateTypeChange('pdf')}
              className={`flex items-center justify-center gap-2 px-3 py-3
                rounded-lg border text-sm font-semibold transition
                ${templateType === 'pdf'
                  ? 'bg-[#539bf5]/20 border-[#539bf5] text-[#79c0ff]'
                  : 'bg-[#24292e] border-[#444c56] text-[#adbac7]'
                }`}
            >
              <FileType className="w-4 h-4" />
              PDF Digital
            </button>
          </div>

          {/* Format Description */}
          <p className="text-xs text-[#adbac7]">
            {templateType === 'word'
              ? 'Word supports tables, placeholders, and form layouts.'
              : 'PDF supports digital text templates. Scanned PDF OCR is not yet supported.'}
          </p>

          {/* Template Path */}
          <div className="w-full space-y-2">
            <input
              type="text"
              value={wordPath}
              onChange={(e) => handleTemplateChange(e.target.value)}
              placeholder={
                templateType === 'word'
                  ? 'Full path to .docx file'
                  : 'Full path to .pdf file'
              }
              className="w-full bg-[#24292e] border border-[#444c56]
                rounded-lg px-3 py-2.5 text-xs text-[#cdd9e5]
                placeholder-slate-500 focus:outline-none
                focus:border-sky-500"
            />

            <div className="flex justify-center">
              <BrowseButton
                kind={templateType}
                label={`Browse ${templateType === 'word' ? 'Word' : 'PDF'} File`}
              />
            </div>
          </div>

          {templateError && (
            <p className="text-xs text-red-400 font-medium">
              {templateError}
            </p>
          )}

          {wordPath && !templateError && (
            <div className="flex items-center space-x-1.5
              text-xs text-[#539bf5] font-medium">
              <CheckCircle2 className="w-4 h-4" />
              <span>Template selected</span>
            </div>
          )}
        </div>
      </div>

      {/* Picker Error */}
      {pickerError && (
        <div className="bg-red-500/10 border border-red-500/30
          rounded-xl p-3 text-sm text-red-300">
          {pickerError}
        </div>
      )}

      {/* PDF Notice */}
      {templateType === 'pdf' && (
        <div className="bg-[#539bf5]/10 border border-[#539bf5]/30
          rounded-xl p-4">
          <div className="flex items-start gap-3">
            <FileType className="w-5 h-5 text-[#79c0ff] mt-0.5" />

            <div className="space-y-1">
              <h4 className="text-sm font-semibold text-[#79c0ff]">
                Digital PDF Template
              </h4>

              <p className="text-xs text-[#adbac7] leading-relaxed">
                PDF digital dengan placeholder dapat digunakan.
                PDF hasil scan yang hanya berupa gambar belum didukung
                karena OCR belum tersedia.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex justify-end pt-4">
        <button
          type="button"
          disabled={!canProceed || loadingPicker !== null}
          onClick={onContinue}
          className={`flex items-center space-x-2 px-6 py-2.5
            rounded-lg text-sm font-semibold transition shadow-lg
            ${canProceed && loadingPicker === null
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
