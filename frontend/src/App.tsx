import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Stepper, StepId } from './components/Stepper';
import { DashboardScreen } from './screens/DashboardScreen';
import { UploadScreen } from './screens/UploadScreen';
import { ExcelAnalysisScreen } from './screens/ExcelAnalysisScreen';
import { WordAnalysisScreen } from './screens/WordAnalysisScreen';
import { MappingScreen } from './screens/MappingScreen';
import { RecordSelectionScreen } from './screens/RecordSelectionScreen';
import { PreviewScreen } from './screens/PreviewScreen';
import { ProcessingScreen } from './screens/ProcessingScreen';
import { CompletionScreen } from './screens/CompletionScreen';
import { HistoryScreen } from './screens/HistoryScreen';
import { SettingsScreen } from './screens/SettingsScreen';
import { ApiService } from './services/api';
import { FieldMapping, SourceSchema, TargetSchema, ValidationResult } from './types';
import { AlertCircle, X } from 'lucide-react';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'session' | 'history' | 'settings'>('dashboard');
  const [currentStep, setCurrentStep] = useState<StepId>('upload');
  const [maxAccessibleStepIndex, setMaxAccessibleStepIndex] = useState(0);

  // Conversion session state
  const [excelPath, setExcelPath] = useState('');
  const [wordPath, setWordPath] = useState('');
  const [outputPath, setOutputPath] = useState('');
  const [selectedSheet, setSelectedSheet] = useState('');
  const [headerOverride, setHeaderOverride] = useState<number | undefined>(undefined);
  const [selectedTableIndex, setSelectedTableIndex] = useState(0);
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [sourceSchema, setSourceSchema] = useState<SourceSchema | null>(null);
  const [targetSchema, setTargetSchema] = useState<TargetSchema | null>(null);
  const [mappings, setMappings] = useState<FieldMapping[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);

  // Processing & Results
  const [processingStage, setProcessingStage] = useState('');
  const [recordsWritten, setRecordsWritten] = useState(0);
  const [fileSizeBytes, setFileSizeBytes] = useState(0);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const resetSession = () => {
    setExcelPath('');
    setWordPath('');
    setOutputPath('');
    setSelectedSheet('');
    setHeaderOverride(undefined);
    setSelectedTableIndex(0);
    setSelectedStrategy('');
    setSourceSchema(null);
    setTargetSchema(null);
    setMappings([]);
    setSelectedIndices([]);
    setValidationResult(null);
    setErrorMessage(null);
    setCurrentStep('upload');
    setMaxAccessibleStepIndex(0);
  };

  const handleError = (err: any) => {
    console.error('Workflow error:', err);
    setErrorMessage(err.message || String(err));
  };

  // Step transitions
  const handleAnalyzeDocuments = async () => {
    try {
      setErrorMessage(null);
      // 1. Analyze Excel
      const src = await ApiService.analyzeExcel(excelPath, selectedSheet || undefined, headerOverride);
      setSourceSchema(src);
      setSelectedSheet(src.sheet_name);
      setHeaderOverride(src.header_row_index);
      setSelectedIndices(src.preview_records.map((_, i) => i));

      // Suggest default output path if not specified
      if (!outputPath) {
        const base = wordPath.replace(/\.docx$/i, '');
        setOutputPath(`${base}_converted_${Date.now()}.docx`);
      }

      setCurrentStep('excel_analysis');
      setMaxAccessibleStepIndex(1);
    } catch (err: any) {
      handleError(err);
    }
  };

  const handleContinueToWord = async () => {
    try {
      setErrorMessage(null);
      const tgt = await ApiService.analyzeWord(wordPath);
      setTargetSchema(tgt);
      setSelectedStrategy(tgt.recommended_strategy);

      setCurrentStep('word_analysis');
      setMaxAccessibleStepIndex(2);
    } catch (err: any) {
      handleError(err);
    }
  };

  const handleContinueToMapping = async () => {
    if (!sourceSchema || !targetSchema) return;
    try {
      setErrorMessage(null);
      const maps = await ApiService.generateMappings(sourceSchema.fields, targetSchema.fields);
      setMappings(maps);

      setCurrentStep('mapping');
      setMaxAccessibleStepIndex(3);
    } catch (err: any) {
      handleError(err);
    }
  };

  const handleResetMappings = async () => {
    if (!sourceSchema || !targetSchema) return;
    try {
      const maps = await ApiService.generateMappings(sourceSchema.fields, targetSchema.fields);
      setMappings(maps);
    } catch (err: any) {
      handleError(err);
    }
  };

  const handleExecuteConversion = async () => {
    if (!sourceSchema || !targetSchema) return;
    try {
      setErrorMessage(null);
      setCurrentStep('processing');
      setProcessingStage('Reading Excel records and initializing template...');

      const result = await ApiService.executeConversion({
        excelPath,
        wordPath,
        outputPath,
        sheetName: selectedSheet,
        headerOverride,
        tableIndex: selectedTableIndex,
        strategyOverride: selectedStrategy,
        recordIndices: selectedIndices,
        mappings,
      });

      setRecordsWritten(result.generation.records_written);
      setFileSizeBytes(result.generation.file_size_bytes);
      setOutputPath(result.generation.output_path);
      setValidationResult(result.validation);

      setCurrentStep('completion');
      setMaxAccessibleStepIndex(6);
    } catch (err: any) {
      handleError(err);
      setCurrentStep('preview');
    }
  };

  const handleLoadExample = (exampleKey: 'medical' | 'shipping' | 'astronomy') => {
    // Relative paths to fixtures created in tests/fixtures
    const rootPath = 'C:\\Users\\ASUS Vivobook\\.gemini\\antigravity-ide\\scratch\\excel to doc converter';
    if (exampleKey === 'medical') {
      setExcelPath(`${rootPath}\\tests\\fixtures\\generated\\medical_records.xlsx`);
      setWordPath(`${rootPath}\\tests\\fixtures\\generated\\medical_template.docx`);
      setOutputPath(`${rootPath}\\tests\\fixtures\\generated\\medical_converted.docx`);
    } else if (exampleKey === 'shipping') {
      setExcelPath(`${rootPath}\\tests\\fixtures\\generated\\shipping_containers.xlsx`);
      setWordPath(`${rootPath}\\tests\\fixtures\\generated\\shipping_template.docx`);
      setOutputPath(`${rootPath}\\tests\\fixtures\\generated\\shipping_converted.docx`);
    } else {
      setExcelPath(`${rootPath}\\tests\\fixtures\\generated\\astronomy_telemetry.xlsx`);
      setWordPath(`${rootPath}\\tests\\fixtures\\generated\\astronomy_template.docx`);
      setOutputPath(`${rootPath}\\tests\\fixtures\\generated\\astronomy_converted.docx`);
    }
    setCurrentTab('session');
    setCurrentStep('upload');
  };

  return (
    <div className="min-h-screen bg-[#24292e] text-[#e6edf3] flex flex-col">
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        resetSession={resetSession}
      />

      {/* Error Toast */}
      {errorMessage && (
        <div className="bg-rose-500/20 border-b border-rose-500/40 text-rose-200 px-6 py-2.5 text-xs flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-400" />
            <span className="font-semibold">Error:</span>
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-rose-300 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Body Content */}
      <main className="flex-1 pb-16">
        {currentTab === 'dashboard' && (
          <DashboardScreen
            onStartNew={() => {
              resetSession();
              setCurrentTab('session');
            }}
            onViewHistory={() => setCurrentTab('history')}
            onLoadExample={handleLoadExample}
          />
        )}

        {currentTab === 'history' && <HistoryScreen />}

        {currentTab === 'settings' && <SettingsScreen />}

        {currentTab === 'session' && (
          <>
            <Stepper
              currentStep={currentStep}
              onStepClick={(step) => setCurrentStep(step)}
              maxAccessibleIndex={maxAccessibleStepIndex}
            />

            {currentStep === 'upload' && (
              <UploadScreen
                excelPath={excelPath}
                wordPath={wordPath}
                setExcelPath={setExcelPath}
                setWordPath={setWordPath}
                onContinue={handleAnalyzeDocuments}
                onLoadExample={handleLoadExample}
              />
            )}

            {currentStep === 'excel_analysis' && (
              <ExcelAnalysisScreen
                sourceSchema={sourceSchema}
                selectedSheet={selectedSheet}
                onSheetChange={(s) => {
                  setSelectedSheet(s);
                  ApiService.analyzeExcel(excelPath, s, headerOverride).then(setSourceSchema);
                }}
                headerOverride={headerOverride}
                setHeaderOverride={setHeaderOverride}
                onReanalyze={() => {
                  ApiService.analyzeExcel(excelPath, selectedSheet, headerOverride).then(setSourceSchema);
                }}
                onContinue={handleContinueToWord}
                onBack={() => setCurrentStep('upload')}
              />
            )}

            {currentStep === 'word_analysis' && (
              <WordAnalysisScreen
                targetSchema={targetSchema}
                selectedTableIndex={selectedTableIndex}
                setSelectedTableIndex={setSelectedTableIndex}
                selectedStrategy={selectedStrategy}
                setSelectedStrategy={setSelectedStrategy}
                onContinue={handleContinueToMapping}
                onBack={() => setCurrentStep('excel_analysis')}
              />
            )}

            {currentStep === 'mapping' && (
              <MappingScreen
                sourceFields={sourceSchema?.fields || []}
                targetFields={targetSchema?.fields || []}
                mappings={mappings}
                setMappings={setMappings}
                onResetMappings={handleResetMappings}
                onContinue={() => {
                  setCurrentStep('record_selection');
                  setMaxAccessibleStepIndex(4);
                }}
                onBack={() => setCurrentStep('word_analysis')}
              />
            )}

            {currentStep === 'record_selection' && (
              <RecordSelectionScreen
                sourceSchema={sourceSchema}
                selectedIndices={selectedIndices}
                setSelectedIndices={setSelectedIndices}
                onContinue={() => {
                  setCurrentStep('preview');
                  setMaxAccessibleStepIndex(5);
                }}
                onBack={() => setCurrentStep('mapping')}
              />
            )}

            {currentStep === 'preview' && (
              <PreviewScreen
                sourceSchema={sourceSchema}
                targetSchema={targetSchema}
                mappings={mappings}
                selectedIndices={selectedIndices}
                outputPath={outputPath}
                setOutputPath={setOutputPath}
                onStartConversion={handleExecuteConversion}
                onBack={() => setCurrentStep('record_selection')}
              />
            )}

            {currentStep === 'processing' && (
              <ProcessingScreen currentStage={processingStage} />
            )}

            {currentStep === 'completion' && (
              <CompletionScreen
                outputPath={outputPath}
                recordsWritten={recordsWritten}
                fileSizeBytes={fileSizeBytes}
                validationResult={validationResult}
                onNewSession={resetSession}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
};
