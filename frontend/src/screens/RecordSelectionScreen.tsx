import React, { useState } from 'react';
import { SourceSchema } from '../types';
import { CheckSquare, Square, Search, ArrowRight, ArrowLeft, Filter } from 'lucide-react';

interface RecordSelectionScreenProps {
  sourceSchema: SourceSchema | null;
  selectedIndices: number[];
  setSelectedIndices: React.Dispatch<React.SetStateAction<number[]>>;
  onContinue: () => void;
  onBack: () => void;
}

export const RecordSelectionScreen: React.FC<RecordSelectionScreenProps> = ({
  sourceSchema,
  selectedIndices,
  setSelectedIndices,
  onContinue,
  onBack,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  if (!sourceSchema) {
    return <div className="text-center py-12 text-[#adbac7]">Loading records...</div>;
  }

  const records = sourceSchema.preview_records;
  const fields = sourceSchema.fields;

  // Filter records based on search query
  const filteredRecords = records.filter((rec, idx) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return Object.values(rec).some((val) => String(val || '').toLowerCase().includes(q));
  });

  const handleSelectAll = () => {
    const allFilteredIndices = filteredRecords.map((_, idx) => idx);
    setSelectedIndices(allFilteredIndices);
  };

  const handleDeselectAll = () => {
    setSelectedIndices([]);
  };

  const toggleRecord = (index: number) => {
    setSelectedIndices((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );
  };

  return (
    <div className="max-w-6xl mx-auto py-6 px-4 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#444c56] pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-[#539bf5]" />
            Record Selection & Filtering
          </h2>
          <p className="text-xs text-[#adbac7] mt-1">
            Choose which Excel records to convert into your Word template.
          </p>
        </div>

        {/* Search Bar & Bulk Actions */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-[#adbac7] absolute left-2.5 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search in records..."
              className="bg-[#24292e] border border-[#444c56] rounded-lg pl-8 pr-3 py-1.5 text-xs text-[#cdd9e5] placeholder-slate-500 focus:outline-none focus:border-sky-500 w-48"
            />
          </div>

          <button
            type="button"
            onClick={handleSelectAll}
            className="px-3 py-1.5 bg-[#2d333b] hover:bg-[#444c56] text-[#cdd9e5] text-xs font-semibold rounded-lg border border-[#444c56] transition"
          >
            Select All
          </button>
          <button
            type="button"
            onClick={handleDeselectAll}
            className="px-3 py-1.5 bg-[#2d333b] hover:bg-[#444c56] text-[#adbac7] text-xs font-semibold rounded-lg border border-[#444c56] transition"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Selection Stats */}
      <div className="flex items-center justify-between text-xs text-[#adbac7] px-1">
        <span>
          Selected <strong className="text-white">{selectedIndices.length}</strong> of{' '}
          <strong className="text-white">{records.length}</strong> available records
        </span>
        {searchQuery && (
          <span className="text-[#539bf5]">
            Showing {filteredRecords.length} records matching &quot;{searchQuery}&quot;
          </span>
        )}
      </div>

      {/* Table */}
      <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto max-h-[420px]">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-850 text-[#adbac7] sticky top-0 border-b border-[#444c56] uppercase font-medium z-10">
              <tr>
                <th className="py-2.5 px-4 w-12 text-center">Select</th>
                <th className="py-2.5 px-4 w-12">#</th>
                {fields.slice(0, 7).map((f) => (
                  <th key={f.field_id} className="py-2.5 px-4 truncate max-w-xs">
                    {f.original_name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/60 text-[#cdd9e5]">
              {filteredRecords.map((rec, idx) => {
                const isSelected = selectedIndices.includes(idx);
                return (
                  <tr
                    key={idx}
                    onClick={() => toggleRecord(idx)}
                    className={`cursor-pointer transition ${
                      isSelected ? 'bg-[#539bf5]/10 hover:bg-[#46954a]/15' : 'hover:bg-slate-750'
                    }`}
                  >
                    <td className="py-2 px-4 text-center">
                      {isSelected ? (
                        <CheckSquare className="w-4 h-4 text-[#539bf5] inline" />
                      ) : (
                        <Square className="w-4 h-4 text-slate-600 inline" />
                      )}
                    </td>
                    <td className="py-2 px-4 font-mono text-slate-500">{idx + 1}</td>
                    {fields.slice(0, 7).map((f) => (
                      <td key={f.field_id} className="py-2 px-4 max-w-xs truncate text-[#cdd9e5]">
                        {rec[f.field_id] !== undefined && rec[f.field_id] !== null
                          ? String(rec[f.field_id])
                          : '-'}
                      </td>
                    ))}
                  </tr>
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
          <span>Back to Mapping</span>
        </button>

        <button
          type="button"
          disabled={selectedIndices.length === 0}
          onClick={onContinue}
          className={`flex items-center space-x-1.5 px-5 py-2 text-xs font-semibold rounded-lg shadow transition ${
            selectedIndices.length > 0
              ? 'bg-[#347d39] hover:bg-[#46954a] text-white cursor-pointer'
              : 'bg-[#2d333b] text-slate-500 cursor-not-allowed border border-[#444c56]'
          }`}
        >
          <span>Preview Output ({selectedIndices.length})</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
