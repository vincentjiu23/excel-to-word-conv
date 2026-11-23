import React, { useState } from 'react';
import { FieldMapping, FieldModel, MappingStatus } from '../types';
import {
  GitMerge,
  RotateCcw,
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Settings2,
  Check,
  Ban,
  Sliders,
  HelpCircle,
  AlertTriangle,
} from 'lucide-react';

interface MappingScreenProps {
  sourceFields: FieldModel[];
  targetFields: FieldModel[];
  mappings: FieldMapping[];
  setMappings: React.Dispatch<React.SetStateAction<FieldMapping[]>>;
  onResetMappings: () => void;
  onContinue: () => void;
  onBack: () => void;
}

export const MappingScreen: React.FC<MappingScreenProps> = ({
  sourceFields,
  targetFields,
  mappings,
  setMappings,
  onResetMappings,
  onContinue,
  onBack,
}) => {
  const [editingMappingId, setEditingMappingId] = useState<string | null>(null);

  // Status badge styling
  const getStatusBadge = (status: MappingStatus) => {
    switch (status) {
      case 'exact_match':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            Exact Match
          </span>
        );
      case 'high_confidence':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-teal-500/20 text-teal-400 border border-teal-500/30">
            High Confidence
          </span>
        );
      case 'recommended':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-[#539bf5]/15 text-[#539bf5] border border-[#539bf5]/30">
            Recommended
          </span>
        );
      case 'needs_review':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-500/20 text-amber-400 border border-amber-500/30">
            Needs Review
          </span>
        );
      case 'ambiguous':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-rose-500/20 text-rose-400 border border-rose-500/30">
            Ambiguous
          </span>
        );
      case 'manually_assigned':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-purple-500/20 text-purple-400 border border-purple-500/30">
            Manual
          </span>
        );
      case 'ignored':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-600/30 text-[#adbac7] border border-[#545d68]/40">
            Ignored
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-500/20 text-red-400 border border-red-500/30">
            Unmapped
          </span>
        );
    }
  };

  const handleSourceChange = (mappingId: string, newSourceId: string) => {
    setMappings((prev) =>
      prev.map((m) => {
        if (m.mapping_id !== mappingId) return m;

        if (newSourceId === '__NONE__') {
          return {
            ...m,
            source_field_id: null,
            source_name: null,
            status: 'ignored',
            confidence: 0,
            reason: 'Ignored by user',
            user_override: true,
          };
        }

        const src = sourceFields.find((s) => s.field_id === newSourceId);
        return {
          ...m,
          source_field_id: newSourceId,
          source_name: src ? src.original_name : newSourceId,
          status: 'manually_assigned',
          confidence: 1.0,
          reason: 'Manually assigned by user',
          user_override: true,
        };
      })
    );
  };

  const handleSetConstant = (mappingId: string, val: string) => {
    setMappings((prev) =>
      prev.map((m) => {
        if (m.mapping_id !== mappingId) return m;
        return {
          ...m,
          constant_value: val,
          status: 'manually_assigned',
          confidence: 1.0,
          reason: `Constant value: "${val}"`,
          user_override: true,
        };
      })
    );
  };

  const handleSetDefault = (mappingId: string, val: string) => {
    setMappings((prev) =>
      prev.map((m) => {
        if (m.mapping_id !== mappingId) return m;
        return {
          ...m,
          default_value: val,
        };
      })
    );
  };

  const handleToggleTransform = (mappingId: string, transformType: string, params: Record<string, any> = {}) => {
    setMappings((prev) =>
      prev.map((m) => {
        if (m.mapping_id !== mappingId) return m;
        const exists = m.transformations.some((t) => t.transform_type === transformType);
        const updated = exists
          ? m.transformations.filter((t) => t.transform_type !== transformType)
          : [...m.transformations, { transform_type: transformType, parameters: params }];
        return { ...m, transformations: updated };
      })
    );
  };

  // Conflict detection: Multiple target fields mapped to the same source field
  const sourceUsageCount: Record<string, number> = {};
  mappings.forEach((m) => {
    if (m.source_field_id && m.status !== 'ignored') {
      sourceUsageCount[m.source_field_id] = (sourceUsageCount[m.source_field_id] || 0) + 1;
    }
  });

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#444c56] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <GitMerge className="w-5 h-5 text-[#539bf5]" />
            Dynamic Schema Mapping Engine
          </h2>
          <p className="text-xs text-[#adbac7] mt-1">
            Review and adjust AI-suggested dynamic field mappings. Every field is discovered from your uploaded files.
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={onResetMappings}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-[#2d333b] hover:bg-[#444c56] text-[#cdd9e5] text-xs font-semibold rounded-lg border border-[#444c56] transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Auto-Map / Reset</span>
          </button>
        </div>
      </div>

      {/* Mapping Table */}
      <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-850 text-[#adbac7] border-b border-[#444c56] uppercase font-medium">
              <tr>
                <th className="py-2.5 px-4">Target Field (Word)</th>
                <th className="py-2.5 px-4">Source Field (Excel)</th>
                <th className="py-2.5 px-4">Sample Values</th>
                <th className="py-2.5 px-4">Confidence</th>
                <th className="py-2.5 px-4">Status & Reason</th>
                <th className="py-2.5 px-4 text-center">Transform</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/60 text-[#cdd9e5]">
              {mappings.map((m) => {
                const matchedSource = sourceFields.find((s) => s.field_id === m.source_field_id);
                const hasConflict = m.source_field_id && sourceUsageCount[m.source_field_id] > 1;
                const isEditing = editingMappingId === m.mapping_id;

                return (
                  <React.Fragment key={m.mapping_id}>
                    <tr className={`hover:bg-slate-750 transition ${hasConflict ? 'bg-amber-500/5' : ''}`}>
                      {/* Target Field */}
                      <td className="py-3 px-4">
                        <div className="font-semibold text-white">{m.target_name}</div>
                        <div className="text-[10px] text-[#adbac7] font-mono mt-0.5">{m.target_field_id}</div>
                      </td>

                      {/* Source Field Dropdown */}
                      <td className="py-3 px-4">
                        <select
                          value={m.source_field_id || (m.status === 'ignored' ? '__NONE__' : '')}
                          onChange={(e) => handleSourceChange(m.mapping_id, e.target.value)}
                          className="w-48 bg-[#24292e] border border-[#444c56] rounded-md px-2 py-1 text-xs text-[#cdd9e5] focus:outline-none focus:border-sky-500"
                        >
                          <option value="">-- Select Source Field --</option>
                          <option value="__NONE__">🚫 &lt;Ignore Field&gt;</option>
                          {sourceFields.map((s) => (
                            <option key={s.field_id} value={s.field_id}>
                              {s.original_name} ({s.data_type})
                            </option>
                          ))}
                        </select>
                        {hasConflict && (
                          <div className="flex items-center space-x-1 text-amber-400 text-[10px] mt-1">
                            <AlertTriangle className="w-3 h-3" />
                            <span>Source field mapped multiple times</span>
                          </div>
                        )}
                      </td>

                      {/* Sample Values */}
                      <td className="py-3 px-4 text-[#cdd9e5] max-w-xs truncate">
                        {matchedSource && matchedSource.sample_values.length > 0 ? (
                          matchedSource.sample_values.slice(0, 2).map((s, idx) => (
                            <span key={idx} className="inline-block bg-[#24292e] px-1.5 py-0.5 rounded text-[11px] mr-1">
                              {String(s)}
                            </span>
                          ))
                        ) : (
                          <span className="text-slate-500 italic">No samples</span>
                        )}
                      </td>

                      {/* Confidence Bar */}
                      <td className="py-3 px-4 w-32">
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 bg-[#373e47] h-1.5 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                m.confidence >= 0.85
                                  ? 'bg-emerald-500'
                                  : m.confidence >= 0.65
                                  ? 'bg-sky-500'
                                  : 'bg-amber-500'
                              }`}
                              style={{ width: `${Math.round(m.confidence * 100)}%` }}
                            />
                          </div>
                          <span className="text-[11px] font-mono font-semibold text-[#cdd9e5]">
                            {Math.round(m.confidence * 100)}%
                          </span>
                        </div>
                      </td>

                      {/* Status & Reason */}
                      <td className="py-3 px-4 max-w-xs">
                        <div className="flex items-center space-x-2">
                          {getStatusBadge(m.status)}
                        </div>
                        <div className="text-[11px] text-[#adbac7] mt-1 truncate" title={m.reason}>
                          {m.reason}
                        </div>
                      </td>

                      {/* Transform Action */}
                      <td className="py-3 px-4 text-center">
                        <button
                          type="button"
                          onClick={() => setEditingMappingId(isEditing ? null : m.mapping_id)}
                          className={`p-1.5 rounded-lg border transition ${
                            m.transformations.length > 0 || m.constant_value || m.default_value
                              ? 'border-sky-500 bg-[#539bf5]/15 text-[#539bf5]'
                              : 'border-[#444c56] hover:border-[#545d68] text-[#adbac7] hover:text-[#cdd9e5]'
                          }`}
                          title="Configure transformations, default value, or constant"
                        >
                          <Sliders className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>

                    {/* Transform Edit Drawer */}
                    {isEditing && (
                      <tr className="bg-slate-850 border-y border-[#444c56]">
                        <td colSpan={6} className="py-3 px-6 space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-[#cdd9e5] flex items-center gap-1.5">
                              <Sliders className="w-3.5 h-3.5 text-[#539bf5]" />
                              Transformations & Overrides for &quot;{m.target_name}&quot;
                            </span>
                            <button
                              type="button"
                              onClick={() => setEditingMappingId(null)}
                              className="text-xs text-[#539bf5] hover:underline"
                            >
                              Done
                            </button>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                            {/* Transformations Checkboxes */}
                            <div className="space-y-1.5">
                              <label className="font-semibold text-[#adbac7]">Text & Case Formatting:</label>
                              <div className="flex flex-wrap gap-2">
                                {['trim', 'uppercase', 'lowercase', 'titlecase'].map((t) => {
                                  const active = m.transformations.some((x) => x.transform_type === t);
                                  return (
                                    <button
                                      key={t}
                                      type="button"
                                      onClick={() => handleToggleTransform(m.mapping_id, t)}
                                      className={`px-2.5 py-1 rounded text-xs font-medium border capitalize ${
                                        active
                                          ? 'border-sky-500 bg-[#539bf5]/15 text-sky-300'
                                          : 'border-[#444c56] bg-[#2d333b] text-[#adbac7]'
                                      }`}
                                    >
                                      {t}
                                    </button>
                                  );
                                })}
                              </div>
                            </div>

                            {/* Default Value */}
                            <div className="space-y-1">
                              <label className="font-semibold text-[#adbac7]">Fallback / Default Value:</label>
                              <input
                                type="text"
                                value={m.default_value || ''}
                                onChange={(e) => handleSetDefault(m.mapping_id, e.target.value)}
                                placeholder="Value if cell is blank"
                                className="w-full bg-[#24292e] border border-[#444c56] rounded px-2.5 py-1 text-xs text-[#cdd9e5]"
                              />
                            </div>

                            {/* Constant Override */}
                            <div className="space-y-1">
                              <label className="font-semibold text-[#adbac7]">Constant Value (Override All):</label>
                              <input
                                type="text"
                                value={m.constant_value || ''}
                                onChange={(e) => handleSetConstant(m.mapping_id, e.target.value)}
                                placeholder="Static constant value"
                                className="w-full bg-[#24292e] border border-[#444c56] rounded px-2.5 py-1 text-xs text-[#cdd9e5]"
                              />
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
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
          <span>Back to Word Analysis</span>
        </button>

        <button
          type="button"
          onClick={onContinue}
          className="flex items-center space-x-1.5 px-5 py-2 bg-[#347d39] hover:bg-[#46954a] text-white text-xs font-semibold rounded-lg shadow transition"
        >
          <span>Select Records & Filter</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
