
import React, { useState, useEffect } from 'react';

import {
  FieldMapping,
  SourceSchema,
  TargetSchema,
  OutputFormat,
  TemplateType,
} from '../types';

import { ApiService } from '../services/api';

import {
  Eye,
  ArrowLeft,
  Folder,
  Play,
  FileText,
  FileType,
  Lock,
  Info,
} from 'lucide-react';

interface PreviewScreenProps {
  sourceSchema: SourceSchema | null;
  targetSchema: TargetSchema | null;
  mappings: FieldMapping[];
  selectedIndices: number[];

  outputPath: string;
  setOutputPath: (p: string) => void;

  outputFormat: OutputFormat;
  setOutputFormat: (format: OutputFormat) => void;

  templateType: TemplateType;

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

  outputFormat,
  setOutputFormat,

  templateType,

  onStartConversion,
  onBack,
}) => {
  const [previewRows, setPreviewRows] = useState<Record<string, any>[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Ensure PDF template always uses PDF output
  useEffect(() => {
    if (templateType === 'pdf' && outputFormat !== 'pdf') {
      setOutputFormat('pdf');
    }
  }, [templateType, outputFormat, setOutputFormat]);

  // Preview mapped values
  useEffect(() => {
    if (sourceSchema) {
      setIsLoading(true);

      ApiService.previewConversion(
        sourceSchema.preview_records,
        mappings,
        selectedIndices
      )
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

  const activeMappings = mappings.filter(
    (m) => m.status !== 'ignored'
  );

  const isPdfTemplate = templateType === 'pdf';

  const handleFormatChange = (format: OutputFormat) => {
    // PDF template cannot generate DOCX
    if (isPdfTemplate && format !== 'pdf') {
      return;
    }

    setOutputFormat(format);

    if (outputPath) {
      const basePath = outputPath.replace(/\.(docx|pdf)$/i, '');
      setOutputPath(`${basePath}.${format}`);
    }
  };

  const getOutputDescription = () => {
    if (isPdfTemplate) {
      return 'The digital PDF template will be used directly. Placeholder values such as {{nama_field}} will be replaced using the mapped Excel data. One PDF page/document will be generated for each selected record and combined into a single PDF file. The original PDF template remains unchanged.';
    }

    if (outputFormat === 'pdf') {
      return 'A Word document will be generated from the original DOCX template and converted to PDF using LibreOffice. The original Word template remains unchanged.';
    }

    return 'A new Word document will be generated using the original DOCX template. The original template remains unchanged.';
  };

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
            Verify the mapped values before generating the final document.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] text-[#adbac7] uppercase font-semibold">
            Template:
          </span>

          <span className={`px-3 py-1 rounded-full text-[10px] font-bold border ${
            isPdfTemplate
              ? 'bg-red-500/10 border-red-500/40 text-red-300'
              : 'bg-blue-500/10 border-blue-500/40 text-blue-300'
          }`}>
            {isPdfTemplate ? 'PDF DIGITAL' : 'WORD DOCX'}
          </span>
        </div>

      </div>

      {/* Output Destination Box */}
      <div className="bg-[#2d333b]/80 border border-[#444c56] rounded-xl p-4 space-y-4">

        <div>
          <label className="text-xs font-semibold text-[#cdd9e5] flex items-center gap-2 mb-2">
            <Folder className="w-4 h-4 text-emerald-400" />
            Output Format:
          </label>

          {isPdfTemplate ? (

            // PDF template: locked PDF output
            <div className="flex items-center justify-between gap-3 bg-red-500/10 border border-red-500/30 rounded-lg p-3">

              <div className="flex items-center gap-3">
                <FileType className="w-5 h-5 text-red-300" />

                <div>
                  <div className="text-xs font-bold text-red-200">
                    PDF (.pdf)
                  </div>

                  <div className="text-[10px] text-[#adbac7]">
                    Output format is fixed because the source template is PDF.
                  </div>
                </div>
              </div>

              <Lock className="w-4 h-4 text-red-300" />

            </div>

          ) : (

            // Word template: DOCX or PDF
            <div className="flex flex-wrap gap-3">

              <button
                type="button"
                onClick={() => handleFormatChange('docx')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-xs font-semibold transition ${
                  outputFormat === 'docx'
                    ? 'bg-blue-600/20 border-blue-500 text-blue-300'
                    : 'bg-[#24292e] border-[#444c56] text-[#adbac7] hover:border-blue-500'
                }`}
              >
                <FileText className="w-4 h-4" />
                Word (.docx)
              </button>

              <button
                type="button"
                onClick={() => handleFormatChange('pdf')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-xs font-semibold transition ${
                  outputFormat === 'pdf'
                    ? 'bg-red-600/20 border-red-500 text-red-300'
                    : 'bg-[#24292e] border-[#444c56] text-[#adbac7] hover:border-red-500'
                }`}
              >
                <FileType className="w-4 h-4" />
                PDF (.pdf)
              </button>

            </div>
          )}
        </div>

        {/* Output File Location */}
        <div>
          <label className="text-xs font-semibold text-[#cdd9e5] flex items-center gap-2 mb-2">
            <Folder className="w-4 h-4 text-emerald-400" />
            Output File Location:
          </label>

          <input
            type="text"
            value={outputPath}
            onChange={(e) => setOutputPath(e.target.value)}
            placeholder={
              outputFormat === 'pdf'
                ? 'e.g. C:\\output\\converted_report.pdf'
                : 'e.g. C:\\output\\converted_report.docx'
            }
            className="w-full bg-[#24292e] border border-[#444c56] rounded-lg px-3 py-2 text-xs text-[#cdd9e5] focus:outline-none focus:border-emerald-500 font-mono"
          />
        </div>

        {/* Output Explanation */}
        <div className={`flex gap-2 p-3 rounded-lg border ${
          isPdfTemplate
            ? 'bg-red-500/5 border-red-500/20'
            : 'bg-blue-500/5 border-blue-500/20'
        }`}>

          <Info className={`w-4 h-4 shrink-0 mt-0.5 ${
            isPdfTemplate ? 'text-red-300' : 'text-blue-300'
          }`} />

          <p className="text-[11px] text-[#adbac7] leading-relaxed">
            {getOutputDescription()}
          </p>

        </div>

      </div>

      {/* Transformed Preview Table */}
      <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl overflow-hidden shadow-sm space-y-2">

        <div className="p-3 bg-[#2d333b] border-b border-[#444c56] flex items-center justify-between">

          <span className="text-xs font-semibold text-[#cdd9e5]">
            Target Mapped Values Preview ({selectedIndices.length} records selected)
          </span>

          {isLoading && (
            <span className="text-xs text-[#539bf5] animate-pulse">
              Updating preview...
            </span>
          )}

        </div>

        <div className="overflow-x-auto max-h-[380px]">

          <table className="w-full text-left text-xs">

            <thead className="bg-slate-850 text-[#adbac7] sticky top-0 border-b border-[#444c56] uppercase font-medium">

              <tr>
                <th className="py-2.5 px-4 w-12">#</th>

                {activeMappings.map((m) => (
                  <th
                    key={m.target_field_id}
                    className="py-2.5 px-4"
                  >
                    <div className="text-white font-semibold truncate">
                      {m.target_name}
                    </div>

                    <div className="text-[10px] text-[#adbac7] normal-case font-normal truncate">
                      from {
                        m.source_name ||
                        (m.constant_value ? `"${m.constant_value}"` : 'blank')
                      }
                    </div>
                  </th>
                ))}

              </tr>

            </thead>

            <tbody className="divide-y divide-slate-700/60 text-[#cdd9e5]">

              {previewRows.map((row, idx) => (
                <tr
                  key={idx}
                  className="hover:bg-slate-750 transition"
                >

                  <td className="py-2 px-4 font-mono text-slate-500">
                    {idx + 1}
                  </td>

                  {activeMappings.map((m) => (
                    <td
                      key={m.target_field_id}
                      className="py-2 px-4 max-w-xs truncate text-[#cdd9e5]"
                    >
                      {row[m.target_field_id] || (
                        <span className="text-slate-500 italic">
                          empty
                        </span>
                      )}
                    </td>
                  ))}

                </tr>
              ))}

              {!isLoading && previewRows.length === 0 && (
                <tr>
                  <td
                    colSpan={Math.max(activeMappings.length + 1, 1)}
                    className="text-center py-8 text-[#768390]"
                  >
                    No preview data available.
                  </td>
                </tr>
              )}

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
          disabled={
            selectedIndices.length === 0 ||
            !outputPath.trim() ||
            isLoading
          }
          className="flex items-center space-x-2 px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold rounded-lg shadow-lg cursor-pointer transition transform hover:scale-[1.01]"
        >
          <Play className="w-4 h-4 fill-white" />

          <span>
            {isPdfTemplate
              ? 'Generate PDF from Template'
              : outputFormat === 'pdf'
                ? 'Generate PDF Document'
                : 'Generate Word Document'}
          </span>

        </button>

      </div>

    </div>
  );
};
