import React from 'react';
import { Settings, Shield, Cpu, Database, Sparkles } from 'lucide-react';

export const SettingsScreen: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
      <div className="border-b border-[#444c56] pb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Settings className="w-5 h-5 text-[#539bf5]" />
          Application Settings & Architecture
        </h2>
        <p className="text-xs text-[#adbac7] mt-1">
          Engine parameters, security controls, and intelligent matching configuration.
        </p>
      </div>

      <div className="space-y-4">
        {/* Security & Local First Card */}
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-5 space-y-3">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            Local-First & Data Security Guarantee
          </h3>
          <p className="text-xs text-[#cdd9e5] leading-relaxed">
            All document parsing, schema discovery, field matching, and file generation execute 100% locally on your machine.
            No document contents, client data, or generated files are ever sent to external cloud servers.
          </p>
          <div className="flex flex-wrap gap-2 text-[11px] text-emerald-400">
            <span className="bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">No Cloud Uploads</span>
            <span className="bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">No Formula Execution</span>
            <span className="bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded">Safe Temporary Storage</span>
          </div>
        </div>

        {/* 9-Stage Hybrid Matching Engine */}
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-5 space-y-3">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-[#539bf5]" />
            9-Stage Hybrid Matching Engine Pipeline
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
            <div className="bg-[#1f2428]/70 border border-[#444c56]/70 rounded p-3">
              <span className="font-semibold text-sky-300">Stages 1 - 3: Deterministic</span>
              <p className="text-[#adbac7] mt-1">Exact name match, case & symbol normalization, and generic synonym thesaurus.</p>
            </div>
            <div className="bg-[#1f2428]/70 border border-[#444c56]/70 rounded p-3">
              <span className="font-semibold text-sky-300">Stages 4 - 6: Algorithmic</span>
              <p className="text-[#adbac7] mt-1">Token set ratio fuzzy similarity, data type compatibility matrix, sample regex patterns.</p>
            </div>
            <div className="bg-[#1f2428]/70 border border-[#444c56]/70 rounded p-3">
              <span className="font-semibold text-sky-300">Stages 7 - 9: Context & Memory</span>
              <p className="text-[#adbac7] mt-1">Character n-gram semantic similarity, table layout alignment, and SQLite user feedback boost.</p>
            </div>
          </div>
        </div>

        {/* Database & Learning Card */}
        <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-5 space-y-3">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-teal-400" />
            Persistent Feedback Learning Store
          </h3>
          <p className="text-xs text-[#cdd9e5] leading-relaxed">
            When you manually assign or correct a mapping, the engine saves your confirmation to a local SQLite database
            (<span className="font-mono text-[#cdd9e5]">conversion_history.db</span>). Future sessions automatically reward your preferred mappings!
          </p>
        </div>
      </div>
    </div>
  );
};
