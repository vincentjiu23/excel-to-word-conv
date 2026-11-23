use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::io::Write;
use std::process::{Command, Stdio};

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
    pub fn execute(command: &str, payload: Value) -> Result<Value, String> {
        let request_id = format!("tauri_{}", uuid_simple());
        let request = IPCRequest {
            command: command.to_string(),
            request_id: request_id.clone(),
            payload,
            protocol_version: "1.0.0".to_string(),
        };

        let request_json = serde_json::to_string(&request)
            .map_err(|e| format!("Failed to serialize request: {}", e))?;

        // Locate python: check virtual environment first, then python3/python
        let python_bin = if cfg!(windows) {
            if std::path::Path::new(".venv\\Scripts\\python.exe").exists() {
                ".venv\\Scripts\\python.exe"
            } else {
                "python"
            }
        } else {
            if std::path::Path::new(".venv/bin/python").exists() {
                ".venv/bin/python"
            } else {
                "python3"
            }
        };

        let mut child = Command::new(python_bin)
            .args(["-m", "engine.cli"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| format!("Failed to spawn python engine ({}): {}", python_bin, e))?;

        if let Some(mut stdin) = child.stdin.take() {
            stdin
                .write_all(request_json.as_bytes())
                .map_err(|e| format!("Failed to write to python stdin: {}", e))?;
        }

        let output = child
            .wait_with_output()
            .map_err(|e| format!("Failed to read python process output: {}", e))?;

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr);
            return Err(format!("Python engine process error: {}", stderr));
        }

        let stdout = String::from_utf8_lossy(&output.stdout);
        let response: IPCResponse = serde_json::from_str(stdout.trim())
            .map_err(|e| format!("Failed to parse response JSON: {} (Output: {})", e, stdout))?;

        if response.success {
            Ok(response.data.unwrap_or(Value::Null))
        } else {
            Err(response.error.unwrap_or_else(|| "Unknown engine error".to_string()))
        }
    }
}

fn uuid_simple() -> u128 {
    use std::time::{SystemTime, UNIX_EPOCH};
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0)
}
