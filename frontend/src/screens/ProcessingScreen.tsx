import React from 'react';
import { Loader2, FileSpreadsheet, GitMerge, FileCheck } from 'lucide-react';

interface ProcessingScreenProps {
  currentStage: string;
}

export const ProcessingScreen: React.FC<ProcessingScreenProps> = ({ currentStage }) => {
  return (
    <div className="max-w-xl mx-auto py-20 px-4 text-center space-y-6">
      <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
        <div className="absolute inset-0 rounded-full border-4 border-sky-500/20 animate-ping" />
        <div className="w-16 h-16 rounded-full bg-[#2d333b] border-2 border-sky-500 flex items-center justify-center shadow-lg">
          <Loader2 className="w-8 h-8 text-[#539bf5] animate-spin" />
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="text-xl font-bold text-white tracking-tight">Generating Document</h3>
        <p className="text-xs text-[#539bf5] font-mono animate-pulse">{currentStage || 'Processing conversion...'}</p>
        <p className="text-xs text-[#adbac7] max-w-sm mx-auto">
          The engine is cloning formatted template elements, injecting data values, and running validation checks.
        </p>
      </div>

      <div className="bg-[#2d333b]/75 border border-[#444c56] rounded-xl p-4 text-left text-xs space-y-2 max-w-sm mx-auto">
        <div className="flex items-center space-x-2 text-[#cdd9e5]">
          <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
          <span>Extracting Excel records & values</span>
        </div>
        <div className="flex items-center space-x-2 text-[#cdd9e5]">
          <GitMerge className="w-4 h-4 text-[#539bf5]" />
          <span>Applying formatters & transforms</span>
        </div>
        <div className="flex items-center space-x-2 text-[#cdd9e5]">
          <FileCheck className="w-4 h-4 text-teal-400" />
          <span>Validating DOCX package integrity</span>
        </div>
      </div>
    </div>
  );
};
