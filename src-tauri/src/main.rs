
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod python_bridge;

use commands::*;

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            pick_file,
            save_output_file,
            inspect_excel,
            analyze_excel,
            analyze_word,
            analyze_pdf_template,
            generate_mappings,
            preview_conversion,
            execute_conversion,
            get_history
        ])
        .run(tauri::generate_context!())
        .expect("error while running Smart Document Converter desktop application");
}
