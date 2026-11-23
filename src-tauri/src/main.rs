// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod python_bridge;

use commands::*;

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            inspect_excel,
            analyze_excel,
            analyze_word,
            generate_mappings,
            preview_conversion,
            execute_conversion,
            get_history
        ])
        .run(tauri::generate_context!())
        .expect("error while running Smart Document Converter desktop application");
}
