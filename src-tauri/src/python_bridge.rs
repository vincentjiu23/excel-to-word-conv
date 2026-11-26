
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::io::Write;
use std::path::PathBuf;
use std::process::{Command, Stdio};
use tauri::{AppHandle, Manager};

#[derive(Serialize, Deserialize, Debug)]
pub struct IPCRequest {
    pub command: String,
    pub request_id: String,
    pub payload: Value,
    pub protocol_version: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct IPCResponse {
    pub success: bool,
    pub request_id: String,
    pub data: Option<Value>,
    pub error: Option<String>,
    pub warnings: Vec<String>,
    pub protocol_version: String,
}

pub struct PythonBridge;

impl PythonBridge {
    pub fn execute(
        app: &AppHandle,
        command_name: &str,
        payload: Value,
    ) -> Result<Value, String> {
        let request_id = format!("tauri_{}", uuid_simple());

        let request = IPCRequest {
            command: command_name.to_string(),
            request_id: request_id.clone(),
            payload,
            protocol_version: "1.0.0".to_string(),
        };

        let request_json = serde_json::to_string(&request)
            .map_err(|e| format!("Failed to serialize request: {}", e))?;

        // =====================================================
        // APPLICATION DATA DIRECTORY
        // =====================================================

        let data_dir = app
            .path()
            .app_data_dir()
            .map_err(|e| format!("Failed to resolve application data directory: {}", e))?;

        std::fs::create_dir_all(&data_dir)
            .map_err(|e| format!("Failed to create application data directory: {}", e))?;

        // =====================================================
        // SELECT ENGINE
        // =====================================================

        let (program, args, working_dir): (PathBuf, Vec<String>, PathBuf) =
            if cfg!(debug_assertions) {
                // DEVELOPMENT MODE

                let project_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
                    .parent()
                    .ok_or("Failed to locate project root directory")?
                    .to_path_buf();

                let python_bin = if cfg!(windows) {
                    let venv_python = project_root
                        .join(".venv")
                        .join("Scripts")
                        .join("python.exe");

                    if venv_python.exists() {
                        venv_python
                    } else {
                        PathBuf::from("python")
                    }
                } else {
                    let venv_python = project_root
                        .join(".venv")
                        .join("bin")
                        .join("python");

                    if venv_python.exists() {
                        venv_python
                    } else {
                        PathBuf::from("python3")
                    }
                };

                (
                    python_bin,
                    vec!["-m".to_string(), "engine.cli".to_string()],
                    project_root,
                )
            } else {
                // PRODUCTION MODE

                if !cfg!(windows) {
                    return Err(
                        "Packaged Python Engine currently supports Windows only.".to_string()
                    );
                }

                let resource_dir = app
                    .path()
                    .resource_dir()
                    .map_err(|e| format!("Failed to resolve resource directory: {}", e))?;

                let engine_dir = resource_dir.join("engine");

                let engine_exe =
                    engine_dir.join("SmartDocumentConverterEngine.exe");

                if !engine_exe.exists() {
                    return Err(format!(
                        "Packaged Python Engine not found: {}",
                        engine_exe.display()
                    ));
                }

                (
                    engine_exe,
                    Vec::new(),
                    engine_dir,
                )
            };

        // =====================================================
        // START PYTHON ENGINE
        // =====================================================

        let mut process = Command::new(&program);

        process
            .args(&args)
            .current_dir(&working_dir)
            .env("SMART_CONVERTER_DATA_DIR", &data_dir)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());

        // Prevent a console window from appearing on Windows.
        #[cfg(windows)]
        {
            use std::os::windows::process::CommandExt;
            process.creation_flags(0x08000000);
        }

        let mut child = process.spawn().map_err(|e| {
            format!(
                "Failed to start Python Engine ({}): {}",
                program.display(),
                e
            )
        })?;

        // =====================================================
        // SEND IPC REQUEST
        // =====================================================

        if let Some(mut stdin) = child.stdin.take() {
            stdin
                .write_all(request_json.as_bytes())
                .map_err(|e| format!("Failed to write IPC request: {}", e))?;
        }

        // =====================================================
        // RECEIVE IPC RESPONSE
        // =====================================================

        let output = child
            .wait_with_output()
            .map_err(|e| format!("Failed to read engine output: {}", e))?;

        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);

        if !output.status.success() {
            return Err(format!(
                "Python Engine exited with status {}.\nSTDERR: {}\nSTDOUT: {}",
                output.status,
                stderr,
                stdout
            ));
        }

        let response: IPCResponse = serde_json::from_str(stdout.trim())
            .map_err(|e| {
                format!(
                    "Failed to parse engine JSON response: {}\nOutput: {}\nSTDERR: {}",
                    e,
                    stdout,
                    stderr
                )
            })?;

        // =====================================================
        // VALIDATE RESPONSE
        // =====================================================

        if response.request_id != request_id {
            return Err(format!(
                "IPC request ID mismatch. Expected: {}, Received: {}",
                request_id,
                response.request_id
            ));
        }

        if response.protocol_version != "1.0.0" {
            return Err(format!(
                "Unsupported IPC protocol version: {}",
                response.protocol_version
            ));
        }

        if response.success {
            Ok(response.data.unwrap_or(Value::Null))
        } else {
            Err(response
                .error
                .unwrap_or_else(|| "Unknown Python Engine error".to_string()))
        }
    }
}

// =============================================================
// SIMPLE REQUEST ID GENERATOR
// =============================================================

fn uuid_simple() -> u128 {
    use std::time::{SystemTime, UNIX_EPOCH};

    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0)
}
