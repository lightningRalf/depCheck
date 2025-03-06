#!/usr/bin/env python3

import subprocess
import shutil
import os
import time
import sys
import webbrowser
from pathlib import Path
from datetime import datetime
import json

# Print function for debugging
def debug_print(message):
    print(f"DEBUG: {message}")

# Get the directory where the script is located (for finding Sunshine)
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
debug_print(f"Script directory: {SCRIPT_DIR}")
SUNSHINE_DIR = SCRIPT_DIR / "Sunshine"
if not SUNSHINE_DIR.exists():
    raise RuntimeError(f"Sunshine directory not found at {SUNSHINE_DIR}")
sys.path.append(str(SUNSHINE_DIR))
import Sunshine

# Get the current working directory (for analyzing dependencies and output location)
WORK_DIR = Path.cwd()
debug_print(f"Working directory: {WORK_DIR}")
# Use the current directory name as project name
folder_name = WORK_DIR.name
debug_print(f"Project name: {folder_name}")

# Get current timestamp for filenames
timestamp = datetime.now().strftime("%Y-%m-%d")
# Create output in the current working directory
OUTPUT_DIR = WORK_DIR / "docs" / "sunshine_output"
SUNSHINE_SCRIPT = SUNSHINE_DIR / "sunshine.py"

SBOM_FILE = f"{folder_name}-sbom-{timestamp}.json"
VUL_FILE = f"{folder_name}-sbomVUL-{timestamp}.json"
HTML_OUTPUT = f"index-{timestamp}.html"

SBOM_FILE_LATEST = f"{folder_name}-sbom-latest.json"
VUL_FILE_LATEST = f"{folder_name}-sbomVUL-latest.json"
HTML_OUTPUT_LATEST = "index.html"

# Check prerequisites
if not SUNSHINE_SCRIPT.exists():
    raise RuntimeError(f"Sunshine script not found at {SUNSHINE_SCRIPT}")
if not shutil.which("grype"):
    raise RuntimeError("Grype is not installed...")
if not shutil.which("cyclonedx-py"):
    raise RuntimeError("cyclonedx-py is not installed... Install with `pip install cyclonedx-bom`")

# Create output directory
debug_print(f"Creating output directory: {OUTPUT_DIR}")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Function to detect dependency file and select cyclonedx-py command
def get_cyclonedx_command(work_dir, sbom_path):
    """Detect available dependency files and return the appropriate cyclonedx-py command."""
    # Check if uv is available in the system
    has_uv = shutil.which("uv") is not None
    debug_print(f"UV package manager available: {has_uv}")
    
    dependency_files = [
        ("pyproject.toml", ["cyclonedx-py", "poetry", str(work_dir), "-o", str(sbom_path)]),
        ("requirements.txt", ["cyclonedx-py", "requirements", "-r", str(work_dir / "requirements.txt"), "-o", str(sbom_path)]),
        ("Pipfile", ["cyclonedx-py", "pipenv", "--pipfile", str(work_dir / "Pipfile"), "-o", str(sbom_path)]),
        ("setup.py", ["cyclonedx-py", "environment", "-o", str(sbom_path)]),  # Fallback for setup.py
    ]
    
    # Check for uv-specific files if uv is available
    if has_uv:
        uv_cmd = ["uv", "tool", "run", "--from", "cyclonedx-bom", "cyclonedx-py", "environment"]
        
        # Try to get Python path from uv
        try:
            python_path = subprocess.check_output(["uv", "python", "find"], text=True).strip()
            debug_print(f"UV Python path: {python_path}")
            uv_cmd.append(python_path)
        except subprocess.SubprocessError:
            debug_print("Failed to get Python path from uv, using default")
        
        uv_cmd.extend(["--outfile", str(sbom_path)])
        debug_print(f"Using UV command: {' '.join(uv_cmd)}")
        return uv_cmd
    
    for file_name, cmd in dependency_files:
        if (work_dir / file_name).exists():
            debug_print(f"Found {file_name}, using command: {' '.join(cmd)}")
            return cmd
    
    
    # Fallback to environment if no dependency file is found
    debug_print("No dependency file found, falling back to environment scan")
    print("Warning: No dependency files (pyproject.toml, requirements.txt, Pipfile, setup.py) found. Falling back to environment scan.")
    return ["cyclonedx-py", "environment", "-o", str(sbom_path)]

# Generate SBOM for the current directory
sbom_path = OUTPUT_DIR / SBOM_FILE
cyclonedx_cmd = get_cyclonedx_command(WORK_DIR, sbom_path)
debug_print(f"Running SBOM generation: {' '.join(cyclonedx_cmd)}")
subprocess.run(cyclonedx_cmd, cwd=WORK_DIR, check=True)

# Print SBOM contents for debugging
with open(sbom_path, 'r') as f:
    sbom_data = json.load(f)
    components = sbom_data.get('components', [])
    debug_print(f"SBOM contains {len(components)} components")
    for component in components:
        debug_print(f" - {component.get('name')} {component.get('version')}")

# Also create latest SBOM copy
shutil.copy(sbom_path, OUTPUT_DIR / SBOM_FILE_LATEST)

# Check vulnerabilities with Grype
vul_path = OUTPUT_DIR / VUL_FILE
grype_cmd = ["grype", f"sbom:{sbom_path.absolute()}", "-o", "cyclonedx-json"]
debug_print(f"Running Grype: {' '.join(grype_cmd)}")
debug_print(f"Vulnerability output path: {vul_path}")
with open(vul_path, "w") as f:
    subprocess.run(grype_cmd, stdout=f, cwd=WORK_DIR, check=True)

# Also create latest vulnerabilities copy
shutil.copy(vul_path, OUTPUT_DIR / VUL_FILE_LATEST)

# Generate HTML visualization with Sunshine via CLI
html_path = OUTPUT_DIR / HTML_OUTPUT
sunshine_cmd = [sys.executable, str(SUNSHINE_SCRIPT), "-i", str(sbom_path.absolute()), "-o", str(html_path.absolute())]
debug_print(f"Running Sunshine: {' '.join(sunshine_cmd)}")
debug_print(f"HTML output path: {html_path}")
subprocess.run(sunshine_cmd, cwd=WORK_DIR, check=True)

# Also create latest HTML copy
shutil.copy(html_path, OUTPUT_DIR / HTML_OUTPUT_LATEST)
time.sleep(2)

# Open the generated HTML file in the default browser
html_file_absolute = (OUTPUT_DIR / HTML_OUTPUT_LATEST).resolve()
debug_print(f"Opening visualization in browser: {html_file_absolute}")
print(f"Opening visualization in browser: {html_file_absolute}")
print(f"Timestamped files created at: {timestamp}")
webbrowser.open(f"file://{html_file_absolute}")

# use the following command to execute it in different directories
# & uv run "C:\Users\mjpa\ProgrammierProjekte\depCheck\visualize_sbom_vul.py"