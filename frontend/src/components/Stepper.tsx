import React from 'react';
import { CheckCircle2, Circle } from 'lucide-react';

export type StepId =
  | 'upload'
  | 'excel_analysis'
  | 'word_analysis'
  | 'mapping'
  | 'record_selection'
  | 'preview'
  | 'processing'
  | 'completion';

interface Step {
  id: StepId;
  label: string;
}

const STEPS: Step[] = [
  { id: 'upload', label: '1. Upload' },
  { id: 'excel_analysis', label: '2. Excel' },
  { id: 'word_analysis', label: '3. Word' },
  { id: 'mapping', label: '4. Mapping' },
  { id: 'record_selection', label: '5. Select' },
  { id: 'preview', label: '6. Preview' },
  { id: 'completion', label: '7. Output' },
];

interface StepperProps {
  currentStep: StepId;
  onStepClick: (step: StepId) => void;
  maxAccessibleIndex: number;
}

export const Stepper: React.FC<StepperProps> = ({ currentStep, onStepClick, maxAccessibleIndex }) => {
  const currentIndex = STEPS.findIndex((s) => s.id === currentStep);

  return (
    <div className="bg-[#2d333b]/80 border-b border-[#444c56] px-6 py-2.5">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        {STEPS.map((step, idx) => {
          const isDone = idx < currentIndex;
          const isCurrent = step.id === currentStep;
          const isAccessible = idx <= maxAccessibleIndex;

          return (
            <React.Fragment key={step.id}>
              <button
                disabled={!isAccessible}
                onClick={() => onStepClick(step.id)}
                className={`flex items-center space-x-1.5 text-xs font-semibold px-2 py-1 rounded transition ${
                  isCurrent
                    ? 'text-[#539bf5] bg-[#539bf5]/10 border border-[#539bf5]/30'
                    : isDone
                    ? 'text-emerald-400 hover:text-emerald-300'
                    : isAccessible
                    ? 'text-[#adbac7] hover:text-[#cdd9e5]'
                    : 'text-slate-600 cursor-not-allowed'
                }`}
              >
                {isDone ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <Circle className={`w-3.5 h-3.5 ${isCurrent ? 'text-[#539bf5] fill-sky-400/30' : 'text-slate-600'}`} />
                )}
                <span>{step.label}</span>
              </button>
              {idx < STEPS.length - 1 && (
                <div
                  className={`h-0.5 flex-1 mx-2 transition ${
                    idx < currentIndex ? 'bg-emerald-500/50' : 'bg-[#373e47]'
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
