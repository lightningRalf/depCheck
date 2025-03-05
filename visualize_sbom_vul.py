#!/usr/bin/env python3

import subprocess
import shutil
import os
import time
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
SUNSHINE_SCRIPT = Path("Sunshine") / "sunshine.py"

# Check prerequisites
if not SUNSHINE_SCRIPT.exists():
    raise RuntimeError(f"Sunshine script not found at {SUNSHINE_SCRIPT}. Please ensure it's in the Sunshine directory.")
if not shutil.which("grype"):
    raise RuntimeError("Grype is not installed...")
if not shutil.which("cyclonedx-py"):
    raise RuntimeError("cyclonedx-py is not installed... Install with `pip install cyclonedx-bom`")

# Create output directory
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

# Generate HTML visualization with Sunshine via CLI
# Note: This only processes the SBOM file, as per the provided sunshine.py
subprocess.run([
    sys.executable, str(SUNSHINE_SCRIPT),
    "-i", str(Path(OUTPUT_DIR) / SBOM_FILE),
    "-o", str(Path(OUTPUT_DIR) / HTML_OUTPUT)
], check=True)

# Wait briefly for the server to start
time.sleep(2)
