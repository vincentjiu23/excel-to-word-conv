
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

import {
  FieldMapping,
  SourceSchema,
  TargetSchema,
  ValidationResult,
  OutputFormat,
  TemplateType,
} from './types';

import { AlertCircle, X } from 'lucide-react';

type ExampleKey =
  | 'medical'
  | 'shipping'
  | 'astronomy'
  | 'medical-pdf';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<
    'dashboard' | 'session' | 'history' | 'settings'
  >('dashboard');

  const [currentStep, setCurrentStep] = useState<StepId>('upload');
  const [maxAccessibleStepIndex, setMaxAccessibleStepIndex] = useState(0);

  // Conversion session state
  const [excelPath, setExcelPath] = useState('');
  const [wordPath, setWordPath] = useState('');

  const [templateType, setTemplateType] =
    useState<TemplateType>('word');

  const [outputPath, setOutputPath] = useState('');
  const [outputFormat, setOutputFormat] =
    useState<OutputFormat>('docx');

  const [selectedSheet, setSelectedSheet] = useState('');
  const [headerOverride, setHeaderOverride] =
    useState<number | undefined>(undefined);

  const [selectedTableIndex, setSelectedTableIndex] = useState(0);
  const [selectedStrategy, setSelectedStrategy] = useState('');

  const [sourceSchema, setSourceSchema] =
    useState<SourceSchema | null>(null);

  const [targetSchema, setTargetSchema] =
    useState<TargetSchema | null>(null);

  const [mappings, setMappings] = useState<FieldMapping[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);

  // Processing & Results
  const [processingStage, setProcessingStage] = useState('');
  const [recordsWritten, setRecordsWritten] = useState(0);
  const [fileSizeBytes, setFileSizeBytes] = useState(0);

  const [validationResult, setValidationResult] =
    useState<ValidationResult | null>(null);

  const [errorMessage, setErrorMessage] =
    useState<string | null>(null);

  // Reset session
  const resetSession = () => {
    setExcelPath('');
    setWordPath('');
    setTemplateType('word');

    setOutputPath('');
    setOutputFormat('docx');

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

    setProcessingStage('');
    setRecordsWritten(0);
    setFileSizeBytes(0);

    setCurrentStep('upload');
    setMaxAccessibleStepIndex(0);
  };

  // Error handler
  const handleError = (err: any) => {
    console.error('Workflow error:', err);
    setErrorMessage(err?.message || String(err));
  };

  // Step 1: Analyze Excel
  const handleAnalyzeDocuments = async () => {
    try {
      setErrorMessage(null);

      if (!excelPath.trim()) {
        throw new Error('Please select an Excel source file.');
      }

      if (!wordPath.trim()) {
        throw new Error('Please select a target template file.');
      }

      const effectiveFormat: OutputFormat =
        templateType === 'pdf' ? 'pdf' : outputFormat;

      setOutputFormat(effectiveFormat);

      const src = await ApiService.analyzeExcel(
        excelPath,
        selectedSheet || undefined,
        headerOverride
      );

      setSourceSchema(src);
      setSelectedSheet(src.sheet_name);
      setHeaderOverride(src.header_row_index);

      setSelectedIndices(
        src.preview_records.map((_, i) => i)
      );

      // Generate output filename
      const base = wordPath.replace(/\.(docx|pdf)$/i, '');

      setOutputPath(
        `${base}_converted_${Date.now()}.${effectiveFormat}`
      );

      setCurrentStep('excel_analysis');
      setMaxAccessibleStepIndex(1);

    } catch (err: any) {
      handleError(err);
    }
  };

  // Step 2: Analyze Word or PDF template
  const handleContinueToWord = async () => {
    try {
      setErrorMessage(null);

      let tgt: TargetSchema;

      if (templateType === 'pdf') {
        // Analyze digital PDF template
        tgt = await ApiService.analyzePdfTemplate(wordPath);

        setSelectedStrategy('replace_placeholders');
        setOutputFormat('pdf');

        // Ensure output filename uses PDF extension
        setOutputPath((previousPath) => {
          if (!previousPath) return previousPath;

          return previousPath.replace(/\.(docx|pdf)$/i, '.pdf');
        });

      } else {
        // Analyze DOCX template
        tgt = await ApiService.analyzeWord(wordPath);

        setSelectedStrategy(tgt.recommended_strategy);
      }

      setTargetSchema(tgt);

      setCurrentStep('word_analysis');
      setMaxAccessibleStepIndex(2);

    } catch (err: any) {
      handleError(err);
    }
  };

  // Step 3: Generate field mappings
  const handleContinueToMapping = async () => {
    if (!sourceSchema || !targetSchema) return;

    try {
      setErrorMessage(null);

      const maps = await ApiService.generateMappings(
        sourceSchema.fields,
        targetSchema.fields
      );

      setMappings(maps);

      setCurrentStep('mapping');
      setMaxAccessibleStepIndex(3);

    } catch (err: any) {
      handleError(err);
    }
  };

  // Reset mappings
  const handleResetMappings = async () => {
    if (!sourceSchema || !targetSchema) return;

    try {
      const maps = await ApiService.generateMappings(
        sourceSchema.fields,
        targetSchema.fields
      );

      setMappings(maps);

    } catch (err: any) {
      handleError(err);
    }
  };

  // Step 4: Execute conversion
  const handleExecuteConversion = async () => {
    if (!sourceSchema || !targetSchema) return;

    try {
      setErrorMessage(null);
      setCurrentStep('processing');

      const effectiveFormat: OutputFormat =
        templateType === 'pdf' ? 'pdf' : outputFormat;

      if (templateType === 'pdf') {
        setProcessingStage(
          'Replacing PDF template placeholders and generating PDF documents...'
        );
      } else if (effectiveFormat === 'pdf') {
        setProcessingStage(
          'Generating Word document and converting to PDF...'
        );
      } else {
        setProcessingStage(
          'Reading Excel records and generating Word document...'
        );
      }

      const result = await ApiService.executeConversion({
        excelPath,
        wordPath,
        templateType,
        outputPath,
        outputFormat: effectiveFormat,
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

  // Load example files
  const handleLoadExample = (exampleKey: ExampleKey) => {
    const rootPath =
      'C:\\Users\\ASUS Vivobook\\.gemini\\antigravity-ide\\scratch\\excel to doc converter';

    const fixturePath =
      `${rootPath}\\tests\\fixtures\\generated`;

    // PDF example
    if (exampleKey === 'medical-pdf') {
      setTemplateType('pdf');
      setOutputFormat('pdf');

      setExcelPath(
        `${fixturePath}\\medical_records.xlsx`
      );

      setWordPath(
        `${fixturePath}\\medical_pdf_template.pdf`
      );

      setOutputPath(
        `${fixturePath}\\medical_pdf_converted.pdf`
      );

    } else {
      // Existing Word examples
      setTemplateType('word');
      setOutputFormat('docx');

      if (exampleKey === 'medical') {
        setExcelPath(
          `${fixturePath}\\medical_records.xlsx`
        );

        setWordPath(
          `${fixturePath}\\medical_template.docx`
        );

        setOutputPath(
          `${fixturePath}\\medical_converted.docx`
        );

      } else if (exampleKey === 'shipping') {
        setExcelPath(
          `${fixturePath}\\shipping_containers.xlsx`
        );

        setWordPath(
          `${fixturePath}\\shipping_template.docx`
        );

        setOutputPath(
          `${fixturePath}\\shipping_converted.docx`
        );

      } else {
        setExcelPath(
          `${fixturePath}\\astronomy_telemetry.xlsx`
        );

        setWordPath(
          `${fixturePath}\\astronomy_template.docx`
        );

        setOutputPath(
          `${fixturePath}\\astronomy_converted.docx`
        );
      }
    }

    // Reset previous analysis state
    setSourceSchema(null);
    setTargetSchema(null);
    setMappings([]);
    setSelectedIndices([]);
    setSelectedSheet('');
    setHeaderOverride(undefined);
    setSelectedTableIndex(0);
    setSelectedStrategy('');
    setValidationResult(null);
    setErrorMessage(null);

    setCurrentTab('session');
    setCurrentStep('upload');
    setMaxAccessibleStepIndex(0);
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

          <button
            onClick={() => setErrorMessage(null)}
            className="text-rose-300 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>

        </div>
      )}

      {/* Main Content */}
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

        {currentTab === 'history' && (
          <HistoryScreen />
        )}

        {currentTab === 'settings' && (
          <SettingsScreen />
        )}

        {currentTab === 'session' && (
          <>
            <Stepper
              currentStep={currentStep}
              onStepClick={(step) => setCurrentStep(step)}
              maxAccessibleIndex={maxAccessibleStepIndex}
            />

            {/* Upload */}
            {currentStep === 'upload' && (
              <UploadScreen
                excelPath={excelPath}
                wordPath={wordPath}
                setExcelPath={setExcelPath}
                setWordPath={setWordPath}
                templateType={templateType}
                setTemplateType={(type) => {
                  setTemplateType(type);

                  setOutputFormat(
                    type === 'pdf' ? 'pdf' : 'docx'
                  );

                  setOutputPath('');
                }}
                onContinue={handleAnalyzeDocuments}
                onLoadExample={handleLoadExample}
              />
            )}

            {/* Excel Analysis */}
            {currentStep === 'excel_analysis' && (
              <ExcelAnalysisScreen
                sourceSchema={sourceSchema}
                selectedSheet={selectedSheet}
                onSheetChange={(s) => {
                  setSelectedSheet(s);

                  ApiService.analyzeExcel(
                    excelPath,
                    s,
                    headerOverride
                  ).then(setSourceSchema).catch(handleError);
                }}
                headerOverride={headerOverride}
                setHeaderOverride={setHeaderOverride}
                onReanalyze={() => {
                  ApiService.analyzeExcel(
                    excelPath,
                    selectedSheet,
                    headerOverride
                  ).then(setSourceSchema).catch(handleError);
                }}
                onContinue={handleContinueToWord}
                onBack={() => setCurrentStep('upload')}
              />
            )}

            {/* Word / PDF Template Analysis */}
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

            {/* Field Mapping */}
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

            {/* Record Selection */}
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

            {/* Preview */}
            {currentStep === 'preview' && (
              <PreviewScreen
                sourceSchema={sourceSchema}
                targetSchema={targetSchema}
                mappings={mappings}
                selectedIndices={selectedIndices}
                outputPath={outputPath}
                setOutputPath={setOutputPath}
                outputFormat={outputFormat}
                setOutputFormat={(format) => {
                  setOutputFormat(
                    templateType === 'pdf' ? 'pdf' : format
                  );
                }}
                templateType={templateType}
                onStartConversion={handleExecuteConversion}
                onBack={() => setCurrentStep('record_selection')}
              />
            )}

            {/* Processing */}
            {currentStep === 'processing' && (
              <ProcessingScreen
                currentStage={processingStage}
              />
            )}

            {/* Completion */}
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
