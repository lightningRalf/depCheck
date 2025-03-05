# Dependency Vulnerability Visualization

This tool generates a Software Bill of Materials (SBOM) for your Python environment, scans it for vulnerabilities, and creates an interactive HTML visualization.

## Prerequisites

Before running the script, ensure you have the following installed:

1. **uv** - mightiest Python package manager
    ```
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

2. **Sunshine** - CycloneDX visualization tool
   ```
   git clone https://github.com/CycloneDX/Sunshine.git
   ```
3. **Grype** - Vulnerability scanner
   - **Windows** (via [Chocolatey](https://chocolatey.org/)):
     ```
     choco install grype
     ```
   - **Windows** (manual): Download binary from [Grype's GitHub releases](https://github.com/anchore/grype/releases) and add to PATH
   
## Setup

1. Clone this repository
2. Clone Sunshine as a subdirectory:
   ```
   git clone https://github.com/CycloneDX/Sunshine.git
   ```
3. Install dependencies via `uv`
    ```
    uv sync
    ```

## Usage

Run the visualization script:

```
uv run visualize_sbom_vul.py
```

The script will:
1. Generate an SBOM of your Python environment
2. Scan the SBOM for vulnerabilities using Grype
3. Create an HTML visualization with Sunshine
4. Open the visualization in your default web browser

## Output Files

All output files are stored in the `docs/sunshine_output` directory:

- **SBOM Files**:
  - `{folder_name}-sbom-{timestamp}.json` - Timestamped SBOM
  - `{folder_name}-sbom-latest.json` - Latest SBOM

- **Vulnerability Reports**:
  - `{folder_name}-sbomVUL-{timestamp}.json` - Timestamped vulnerability report
  - `{folder_name}-sbomVUL-latest.json` - Latest vulnerability report

- **HTML Visualizations**:
  - `index-{timestamp}.html` - Timestamped visualization
  - `index.html` - Latest visualization (this is what opens in your browser)

## Troubleshooting

If you encounter any issues:

1. Ensure all prerequisites are properly installed
2. Verify that Sunshine is cloned into the `Sunshine` subdirectory
3. Check that grype and cyclonedx-py are available in your PATH