
import React, { useEffect, useState } from 'react';
import { ApiService } from '../services/api';
import { ConversionRun } from '../types';
import {
  FileSpreadsheet,
  FileText,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Layers,
  History,
} from 'lucide-react';

type ExampleKey =
  | 'medical'
  | 'shipping'
  | 'astronomy'
  | 'medical-pdf';

interface DashboardScreenProps {
  onStartNew: () => void;
  onViewHistory: () => void;
  onLoadExample: (exampleKey: ExampleKey) => void;
}

export const DashboardScreen: React.FC<DashboardScreenProps> = ({
  onStartNew,
  onViewHistory,
  onLoadExample,
}) => {
  const [recentRuns, setRecentRuns] = useState<ConversionRun[]>([]);

  useEffect(() => {
    ApiService.getHistory(5)
      .then((data) => setRecentRuns(data || []))
      .catch(() => {});
  }, []);

  return (
    <div className="w-full max-w-none py-7 px-4 sm:px-6 lg:px-10 2xl:px-14 space-y-6">

      {/* Hero */}
      <div className="bg-gradient-to-br from-[#2d333b] to-[#24292e] border border-[#444c56] rounded-xl p-6 sm:p-8 lg:p-10 shadow-sm relative overflow-hidden">
        <div className="relative z-10 max-w-4xl space-y-4">

          <div className="inline-flex items-center space-x-2 px-3 py-1 bg-[#539bf5]/10 border border-[#539bf5]/30 rounded-full text-[#539bf5] text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Autonomous Document Conversion</span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight leading-tight">
            Convert Excel Workbooks into Word Templates Automatically
          </h2>

          <p className="text-sm text-[#cdd9e5] leading-relaxed">
            The uploaded files define the schema. The engine dynamically extracts source and target structures,
            evaluates matches across 9 intelligent stages, preserves original Word styling, and validates output integrity.
            Digital PDF templates are also supported through placeholder replacement.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">

            <button
              type="button"
              onClick={onStartNew}
              className="flex items-center space-x-2 px-5 py-2.5 bg-[#347d39] hover:bg-[#46954a] text-white text-xs font-bold rounded-lg shadow-md transition"
            >
              <span>Start New Conversion</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              type="button"
              onClick={onViewHistory}
              className="flex items-center space-x-2 px-4 py-2.5 bg-[#2d333b] hover:bg-[#444c56] text-[#cdd9e5] text-xs font-semibold rounded-lg border border-[#444c56] transition"
            >
              <History className="w-4 h-4" />
              <span>Audit History</span>
            </button>

          </div>
        </div>
      </div>

      {/* Feature Highlights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">

        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-5 space-y-2 hover:border-[#545d68] transition-colors">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
            <Layers className="w-5 h-5" />
          </div>

          <h3 className="text-sm font-semibold text-white">
            Zero Hardcoded Parameters
          </h3>

          <p className="text-xs text-[#adbac7] leading-relaxed">
            Works out-of-the-box on unknown column names, offset header rows, formulas, and diverse scientific or business domains.
          </p>
        </div>

        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-5 space-y-2 hover:border-[#545d68] transition-colors">
          <div className="w-9 h-9 rounded-lg bg-[#539bf5]/15 text-[#539bf5] flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>

          <h3 className="text-sm font-semibold text-white">
            9-Stage Intelligent Matching
          </h3>

          <p className="text-xs text-[#adbac7] leading-relaxed">
            Combines exact matching, normalization, synonyms, token fuzzy scoring, type compatibility, and user memory.
          </p>
        </div>

        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-5 space-y-2 hover:border-[#545d68] transition-colors">
          <div className="w-9 h-9 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5" />
          </div>

          <h3 className="text-sm font-semibold text-white">
            Deep Formatting Preservation
          </h3>

          <p className="text-xs text-[#adbac7] leading-relaxed">
            Maintains font families, weights, borders, cell shading, headers, footers, and margins by cloning OOXML structures.
          </p>
        </div>

      </div>

      {/* Quick Test Domains */}
      <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-5 sm:p-6 space-y-4">

        <div>
          <h3 className="text-base font-semibold text-white">
            Try Example Multi-Domain Workflows
          </h3>

          <p className="text-xs text-[#adbac7] mt-0.5">
            Load synthetic test fixtures to observe schema discovery across unfamiliar domains:
          </p>
        </div>

        {/* 4 Example Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">

          {/* Clinical Cohort - Word */}
          <div
            role="button"
            tabIndex={0}
            onClick={() => onLoadExample('medical')}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                onLoadExample('medical');
              }
            }}
            className="p-4 rounded-lg border border-[#444c56] bg-[#1f2428]/70 hover:border-[#3fb950]/60 cursor-pointer transition space-y-2"
          >
            <div className="flex items-center space-x-2 text-emerald-400 text-xs font-semibold">
              <FileSpreadsheet className="w-4 h-4" />
              <span>Clinical Cohort</span>
            </div>

            <p className="text-xs text-[#adbac7]">
              Excel patient records mapped into a Word template. Blood pressure, condition classification, and visit dates.
            </p>
          </div>

          {/* Maritime Shipping */}
          <div
            role="button"
            tabIndex={0}
            onClick={() => onLoadExample('shipping')}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                onLoadExample('shipping');
              }
            }}
            className="p-4 rounded-lg border border-[#444c56] bg-[#1f2428]/70 hover:border-[#539bf5]/70 cursor-pointer transition space-y-2"
          >
            <div className="flex items-center space-x-2 text-[#539bf5] text-xs font-semibold">
              <FileSpreadsheet className="w-4 h-4" />
              <span>Maritime Container Cargo</span>
            </div>

            <p className="text-xs text-[#adbac7]">
              Vessel references, container tare/gross weight (KG), origin & destination ports.
            </p>
          </div>

          {/* Astronomy */}
          <div
            role="button"
            tabIndex={0}
            onClick={() => onLoadExample('astronomy')}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                onLoadExample('astronomy');
              }
            }}
            className="p-4 rounded-lg border border-[#444c56] bg-[#1f2428]/70 hover:border-purple-500/60 cursor-pointer transition space-y-2"
          >
            <div className="flex items-center space-x-2 text-purple-400 text-xs font-semibold">
              <FileSpreadsheet className="w-4 h-4" />
              <span>Astrophysics Telemetry</span>
            </div>

            <p className="text-xs text-[#adbac7]">
              Deep space radio signals, right ascension, declination, redshift metrics.
            </p>
          </div>

          {/* Medical PDF */}
          <div
            role="button"
            tabIndex={0}
            onClick={() => onLoadExample('medical-pdf')}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                onLoadExample('medical-pdf');
              }
            }}
            className="p-4 rounded-lg border border-rose-500/30 bg-[#1f2428]/70 hover:border-rose-500/70 cursor-pointer transition space-y-2"
          >
            <div className="flex items-center space-x-2 text-rose-400 text-xs font-semibold">
              <FileText className="w-4 h-4" />
              <span>Medical PDF Template</span>
            </div>

            <p className="text-xs text-[#adbac7]">
              Excel patient records mapped into a digital PDF template with seven placeholders. Generates merged PDF output.
            </p>
          </div>

        </div>
      </div>

      {/* Recent Conversions */}
      {recentRuns.length > 0 && (
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-5 space-y-3">

          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-[#adbac7]" />
            Recent Conversion Runs
          </h3>

          <div className="space-y-2">
            {recentRuns.map((r) => (
              <div
                key={r.id}
                className="bg-[#1f2428]/80 border border-[#444c56]/70 rounded-lg p-3 text-xs flex items-center justify-between"
              >
                <div className="space-y-0.5">

                  <span className="font-semibold text-[#cdd9e5]">
                    {r.output_path.split('\\').pop()?.split('/').pop()}
                  </span>

                  <div className="text-[11px] text-[#adbac7]">
                    {r.record_count} records converted • {new Date(r.created_at).toLocaleDateString()}
                  </div>

                </div>

                <span className="flex items-center space-x-1 text-emerald-400 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Success</span>
                </span>

              </div>
            ))}
          </div>

        </div>
      )}

    </div>
  );
};
