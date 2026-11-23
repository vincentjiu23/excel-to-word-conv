use crate::python_bridge::PythonBridge;
use serde_json::Value;

#[tauri::command]
pub async fn inspect_excel(payload: Value) -> Result<Value, String> {
    PythonBridge::execute("inspect_excel", payload)
}

#[tauri::command]
pub async fn analyze_excel(payload: Value) -> Result<Value, String> {
    PythonBridge::execute("analyze_excel", payload)
}

#[tauri::command]
pub async fn analyze_word(payload: Value) -> Result<Value, String> {
    PythonBridge::execute("analyze_word", payload)
}

#[tauri::command]
pub async fn generate_mappings(payload: Value) -> Result<Value, String> {
    PythonBridge::execute("generate_mappings", payload)
}

#[tauri::command]
pub async fn preview_conversion(payload: Value) -> Result<Value, String> {
    PythonBridge::execute("preview_conversion", payload)
}

#[tauri::command]
pub async fn execute_conversion(payload: Value) -> Result<Value, String> {
    PythonBridge::execute("execute_conversion", payload)
}

#[tauri::command]
pub async fn get_history(payload: Value) -> Result<Value, String> {
    PythonBridge::execute("get_history", payload)
}
