export type DataType =
  | 'string'
  | 'integer'
  | 'float'
  | 'date'
  | 'datetime'
  | 'boolean'
  | 'currency'
  | 'percentage'
  | 'unknown';

export type MappingStatus =
  | 'exact_match'
  | 'recommended'
  | 'high_confidence'
  | 'needs_review'
  | 'ambiguous'
  | 'unmatched'
  | 'ignored'
  | 'manually_assigned';

export interface FieldModel {
  field_id: string;
  original_name: string;
  normalized_name: string;
  data_type: DataType;
  source_type: 'excel' | 'word';
  location: Record<string, any>;
  sample_values: any[];
  null_count: number;
  unique_count: number;
  confidence: number;
  metadata: Record<string, any>;
}

export interface ExcelSheetInfo {
  name: string;
  is_hidden: boolean;
  max_row: number;
  max_col: number;
  detected_header_row: number;
  header_candidates: number[];
}

export interface SourceSchema {
  file_path: string;
  sheet_name: string;
  total_rows: number;
  total_cols: number;
  header_row_index: number;
  data_start_row: number;
  fields: FieldModel[];
  warnings: string[];
  has_formulas: boolean;
  formula_count: number;
  available_sheets: ExcelSheetInfo[];
  preview_records: Record<string, any>[];
}

export interface TargetTableInfo {
  table_index: number;
  row_count: number;
  col_count: number;
  header_row_index?: number;
  has_repeating_pattern: boolean;
  sample_headers: string[];
  has_merged_cells: boolean;
  is_nested: boolean;
}

export interface TargetDocumentStructure {
  has_tables: boolean;
  table_count: number;
  paragraph_count: number;
  placeholder_count: number;
  has_headers_footers: boolean;
  sections_count: number;
  unsupported_features_detected: string[];
}

export interface TargetSchema {
  file_path: string;
  structure: TargetDocumentStructure;
  tables: TargetTableInfo[];
  fields: FieldModel[];
  candidate_strategies: string[];
  recommended_strategy: string;
  warnings: string[];
}

export interface FieldTransformation {
  transform_type: string;
  parameters: Record<string, any>;
}

export interface FieldMapping {
  mapping_id: string;
  target_field_id: string;
  target_name: string;
  source_field_id?: string | null;
  source_name?: string | null;
  confidence: number;
  status: MappingStatus;
  reason: string;
  stage: string;
  transformations: FieldTransformation[];
  constant_value?: any;
  default_value?: any;
  user_override: boolean;
  metadata?: Record<string, any>;
}

export interface ValidationResult {
  is_valid: boolean;
  checks_passed: string[];
  checks_failed: string[];
  details: Record<string, any>;
}

export interface ConversionRun {
  id: number;
  session_id: string;
  excel_path: string;
  word_path: string;
  output_path: string;
  record_count: number;
  status: string;
  created_at: string;
}
