#!/usr/bin/env python3

import subprocess
import shutil
import os
import time
import sys
import webbrowser
from pathlib import Path
from datetime import datetime

SUNSHINE_DIR = Path("Sunshine")
if not SUNSHINE_DIR.exists():
    raise RuntimeError(f"Sunshine directory not found at {SUNSHINE_DIR}. Please ensure you have cloned it.")
sys.path.append(str(SUNSHINE_DIR))
import Sunshine

# Get current timestamp for filenames
timestamp = datetime.now().strftime("%Y-%m-%d")
folder_name = os.path.basename(os.getcwd())
OUTPUT_DIR = "docs/sunshine_output"
SUNSHINE_SCRIPT = Path("Sunshine") / "sunshine.py"

SBOM_FILE = f"{folder_name}-sbom-{timestamp}.json"
VUL_FILE = f"{folder_name}-sbomVUL-{timestamp}.json"
HTML_OUTPUT = f"index-{timestamp}.html"

# Also create a "latest" version for easy access to most recent report
SBOM_FILE_LATEST = f"{folder_name}-sbom-latest.json"
VUL_FILE_LATEST = f"{folder_name}-sbomVUL-latest.json"
HTML_OUTPUT_LATEST = "index.html"

# Check prerequisites
if not SUNSHINE_SCRIPT.exists():
    raise RuntimeError(f"Sunshine script not found at {SUNSHINE_SCRIPT}. Please ensure it's in the Sunshine directory.")
if not shutil.which("grype"):
    raise RuntimeError("Grype is not installed...")
if not shutil.which("cyclonedx-py"):
    raise RuntimeError("cyclonedx-py is not installed... Install with `pip install cyclonedx-bom`")

# Create output directory
Path(OUTPUT_DIR).mkdir(exist_ok=True, parents=True)

# Generate SBOM
sbom_path = Path(OUTPUT_DIR) / SBOM_FILE
subprocess.run([
    "cyclonedx-py", "environment",
    "--outfile", str(sbom_path)
], check=True)

# Also create latest SBOM copy
shutil.copy(sbom_path, Path(OUTPUT_DIR) / SBOM_FILE_LATEST)

# Check vulnerabilities with Grype
vul_path = Path(OUTPUT_DIR) / VUL_FILE
with open(vul_path, "w") as f:
    subprocess.run([
        "grype", f"sbom:{sbom_path}", "-o", "cyclonedx-json"
    ], stdout=f, check=True)

# Also create latest vulnerabilities copy
shutil.copy(vul_path, Path(OUTPUT_DIR) / VUL_FILE_LATEST)

# Generate HTML visualization with Sunshine via CLI
html_path = Path(OUTPUT_DIR) / HTML_OUTPUT
subprocess.run([
    sys.executable, str(SUNSHINE_SCRIPT),
    "-i", str(sbom_path),
    "-o", str(html_path)
], check=True)

# Also create latest HTML copy
shutil.copy(html_path, Path(OUTPUT_DIR) / HTML_OUTPUT_LATEST)

# Wait briefly for the server to start
time.sleep(2)

# Open the generated HTML file in the default browser
html_file_absolute = (Path(OUTPUT_DIR) / HTML_OUTPUT_LATEST).resolve()
print(f"Opening visualization in browser: {html_file_absolute}")
print(f"Timestamped files created at: {timestamp}")
webbrowser.open(f"file://{html_file_absolute}")