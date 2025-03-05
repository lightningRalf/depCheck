#!/usr/bin/env python3

import subprocess
import shutil
import os
import time
import webbrowser
import sys
from pathlib import Path

SUNSHINE_DIR = Path("Sunshine")
if not SUNSHINE_DIR.exists():
    raise RuntimeError(f"Sunshine directory not found at {SUNSHINE_DIR}. Please ensure you have cloned it.")
sys.path.append(str(SUNSHINE_DIR))
import sunshine

folder_name = os.path.basename(os.getcwd())
SBOM_FILE = f"{folder_name}-sbom.json"
VUL_FILE = f"{folder_name}-sbomVUL.json"
OUTPUT_DIR = "sunshine_output"
HTML_OUTPUT = "index.html"

if not shutil.which("grype"):
    raise RuntimeError(
        "Grype is not installed. Please install it via Chocolatey (`choco install grype`) "
        "or download from https://github.com/anchore/grype/releases and add to PATH."
    )
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# Generate SBOM
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

# Start the Granian server
project_dir = Path(__file__).parent
server_process = subprocess.Popen([
    "granian", "--interface", "wsgi", 
    f"{project_dir / 'application'}:application"
], cwd=os.getcwd())

time.sleep(2)

webbrowser.open(f"http://127.0.0.1:8000/{OUTPUT_DIR}/{HTML_OUTPUT}")

try:
    server_process.wait()
except KeyboardInterrupt:
    server_process.terminate()