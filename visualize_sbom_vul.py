#!/usr/bin/env python3

import subprocess
import shutil
import os
import time
import webbrowser
import sys
from pathlib import Path

# Add Sunshine directory to Python path
SUNSHINE_DIR = Path("Sunshine")  # Path to the cloned Sunshine repository
if not SUNSHINE_DIR.exists():
    raise RuntimeError(f"Sunshine directory not found at {SUNSHINE_DIR}. Please ensure you have cloned it.")

sys.path.append(str(SUNSHINE_DIR))
import sunshine  # Import sunshine from the cloned repository

# Derive filenames from the current working directory
folder_name = os.path.basename(os.getcwd())
SBOM_FILE = f"{folder_name}-sbom.json"
VUL_FILE = f"{folder_name}-sbomVUL.json"
OUTPUT_DIR = "sunshine_output"  # Changed from SUNSHINE_DIR to avoid confusion
HTML_OUTPUT = "index.html"

# Check if Grype is installed
if not shutil.which("grype"):
    raise RuntimeError(
        "Grype is not installed. Please install it via Chocolatey (`choco install grype`) "
        "or download from https://github.com/anchore/grype/releases and add to PATH."
    )

# Create output directory in the current working directory
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Generate SBOM for the current environment
subprocess.run([
    "cyclonedx-py", "environment",
    "--outfile", str(Path(OUTPUT_DIR) / SBOM_FILE)
], check=True)

# Check vulnerabilities with Grype
vul_path = Path(OUTPUT_DIR) / VUL_FILE
with open(vul_path, "w") as f:
    subprocess.run([
        "grype", f"sbom:{Path(OUTPUT_DIR) / SBOM_FILE}", "-o", "cyclonedx-json"
    ], stdout=f, check=True)

# Generate HTML visualization with Sunshine
sunshine.visualize(
    sbom=str(Path(OUTPUT_DIR) / SBOM_FILE),
    vulns=str(vul_path),
    output=str(Path(OUTPUT_DIR) / HTML_OUTPUT)
)

# Start the Granian server from the project directory, serving from the current directory
project_dir = Path(__file__).parent
server_process = subprocess.Popen([str(project_dir / "granian_server.exe")], cwd=os.getcwd())

# Wait briefly for the server to start
time.sleep(2)

# Open the HTML output in the browser
webbrowser.open(f"http://127.0.0.1:8000/{OUTPUT_DIR}/{HTML_OUTPUT}")

# Keep the script running until interrupted
try:
    server_process.wait()
except KeyboardInterrupt:
    server_process.terminate()