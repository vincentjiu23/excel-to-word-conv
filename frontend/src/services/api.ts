import {
  FieldMapping,
  FieldModel,
  SourceSchema,
  TargetSchema,
  ValidationResult,
  ConversionRun,
} from '../types';

export class ApiService {
  private static isTauri(): boolean {
    return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window;
  }

  static async executeCommand<T>(command: string, payload: Record<string, any> = {}): Promise<T> {
    const requestId = `req_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;

    // Tauri 2 IPC
    if (this.isTauri()) {
      try {
        const tauriCore = (window as any).__TAURI__?.core;
        if (tauriCore && typeof tauriCore.invoke === 'function') {
          return await tauriCore.invoke(command, payload);
        }
      } catch (err) {
        console.warn('Tauri invoke failed, falling back to HTTP IPC:', err);
      }
    }

    // HTTP IPC Fallback
    const response = await fetch('/api/ipc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        command,
        request_id: requestId,
        payload,
        protocol_version: '1.0.0',
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`IPC Request failed (${response.status}): ${errText}`);
    }

    const json = await response.json();
    if (!json.success) {
      throw new Error(json.error || 'Unknown IPC Engine Error');
    }

    return json.data as T;
  }

  static async inspectExcel(filePath: string) {
    return this.executeCommand<{ sheets: any[] }>('inspect_excel', { file_path: filePath });
  }

  static async analyzeExcel(filePath: string, sheetName?: string, headerOverride?: number) {
    const res = await this.executeCommand<{ source_schema: SourceSchema }>('analyze_excel', {
      file_path: filePath,
      sheet_name: sheetName,
      header_row_override: headerOverride,
    });
    return res.source_schema;
  }

  static async analyzeWord(filePath: string) {
    const res = await this.executeCommand<{ target_schema: TargetSchema }>('analyze_word', {
      file_path: filePath,
    });
    return res.target_schema;
  }

  static async generateMappings(sourceFields: FieldModel[], targetFields: FieldModel[]) {
    const res = await this.executeCommand<{ mappings: FieldMapping[] }>('generate_mappings', {
      source_fields: sourceFields,
      target_fields: targetFields,
    });
    return res.mappings;
  }

  static async previewConversion(
    records: Record<string, any>[],
    mappings: FieldMapping[],
    recordIndices?: number[],
    searchQuery?: string
  ) {
    return this.executeCommand<{ total_filtered: number; preview_records: Record<string, any>[] }>(
      'preview_conversion',
      {
        records,
        mappings,
        record_indices: recordIndices,
        search_query: searchQuery,
      }
    );
  }

  static async executeConversion(params: {
    excelPath: string;
    wordPath: string;
    outputPath?: string;
    sheetName?: string;
    headerOverride?: number;
    tableIndex?: number;
    strategyOverride?: string;
    recordIndices?: number[];
    mappings: FieldMapping[];
    sessionId?: string;
  }) {
    return this.executeCommand<{
      generation: { output_path: string; records_written: number; strategy_used: string; file_size_bytes: number };
      validation: ValidationResult;
      session_id: string;
    }>('execute_conversion', {
      excel_path: params.excelPath,
      word_path: params.wordPath,
      output_path: params.outputPath,
      sheet_name: params.sheetName,
      header_row_override: params.headerOverride,
      table_index: params.tableIndex || 0,
      strategy_override: params.strategyOverride,
      record_indices: params.recordIndices,
      mappings: params.mappings,
      session_id: params.sessionId,
    });
  }

  static async getHistory(limit = 20) {
    const res = await this.executeCommand<{ runs: ConversionRun[] }>('get_history', { limit });
    return res.runs;
  }
}
