
use crate::python_bridge::PythonBridge;
use serde_json::Value;
use std::path::Path;
use tauri::AppHandle;

#[tauri::command]
pub async fn pick_file(kind: String) -> Result<Option<String>, String> {
    let dialog = rfd::FileDialog::new();

    let dialog = match kind.as_str() {
        "excel" => dialog.add_filter("Excel Workbook", &["xlsx"]),
        "word" => dialog.add_filter("Word Document", &["docx"]),
        "pdf" => dialog.add_filter("PDF Document", &["pdf"]),
        _ => return Err("Unsupported file type.".to_string()),
    };

    let selected = dialog.pick_file();

    Ok(selected.map(|path| path.to_string_lossy().to_string()))
}

#[tauri::command]
pub async fn save_output_file(
    source_path: String,
    suggested_name: String,
) -> Result<Option<String>, String> {
    let source = Path::new(&source_path);

    if !source.exists() {
        return Err(format!(
            "Output file does not exist: {}",
            source_path
        ));
    }

    if !source.is_file() {
        return Err("Output path is not a file.".to_string());
    }

    let extension = source
        .extension()
        .and_then(|ext| ext.to_str())
        .unwrap_or("file");

    let suggested_name = Path::new(&suggested_name)
        .file_name()
        .and_then(|name| name.to_str())
        .filter(|name| !name.is_empty())
        .unwrap_or("converted_document");

    let destination = rfd::FileDialog::new()
        .set_file_name(suggested_name)
        .add_filter("Converted Document", &[extension])
        .save_file();

    let Some(destination) = destination else {
        return Ok(None);
    };

    if source.canonicalize().ok() == destination.canonicalize().ok() {
        return Ok(Some(destination.to_string_lossy().to_string()));
    }

    std::fs::copy(source, &destination).map_err(|e| {
        format!("Failed to save output file: {}", e)
    })?;

    Ok(Some(destination.to_string_lossy().to_string()))
}

#[tauri::command]
pub async fn inspect_excel(
    app: AppHandle,
    payload: Value,
) -> Result<Value, String> {
    PythonBridge::execute(&app, "inspect_excel", payload)
}

#[tauri::command]
pub async fn analyze_excel(
    app: AppHandle,
    payload: Value,
) -> Result<Value, String> {
    PythonBridge::execute(&app, "analyze_excel", payload)
}

#[tauri::command]
pub async fn analyze_word(
    app: AppHandle,
    payload: Value,
) -> Result<Value, String> {
    PythonBridge::execute(&app, "analyze_word", payload)
}

#[tauri::command]
pub async fn analyze_pdf_template(
    app: AppHandle,
    payload: Value,
) -> Result<Value, String> {
    PythonBridge::execute(&app, "analyze_pdf_template", payload)
}

#[tauri::command]
pub async fn generate_mappings(
    app: AppHandle,
    payload: Value,
) -> Result<Value, String> {
    PythonBridge::execute(&app, "generate_mappings", payload)
}

#[tauri::command]
pub async fn preview_conversion(
    app: AppHandle,
    payload: Value,
) -> Result<Value, String> {
    PythonBridge::execute(&app, "preview_conversion", payload)
}

#[tauri::command]
pub async fn execute_conversion(
    app: AppHandle,
    payload: Value,
) -> Result<Value, String> {
    PythonBridge::execute(&app, "execute_conversion", payload)
}

#[tauri::command]
pub async fn get_history(
    app: AppHandle,
    payload: Value,
) -> Result<Value, String> {
    PythonBridge::execute(&app, "get_history", payload)
}
