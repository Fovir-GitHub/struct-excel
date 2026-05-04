# Struct Excel

This repository stores script for structuring Excel data file provided by MCMC and BlackBerry Cybersecurity Centre of Excellence (CCOE).

## Installation & Usage

### From Release

Access [GitHub Release](https://github.com/Fovir-GitHub/struct-excel/releases/latest) and download the binary matches your OS.

| OS      | Binary                      |
| ------- | --------------------------- |
| Windows | `struct-excel-windows.exe ` |
| Linux   | `struct-excel-linux`        |
| macOS   | `struct-excel-macos`        |

For Windows users, launch `cmd` or `powershell` and switch to the directory of `struct-excel-windows.exe`.

```ps1
.\struct-excel-windows.exe --src /path/to/source/excel
```

This will create a `dist/` directory and output results in it. There will be a `dist/err.xlsx` storing data that require further investigation due to missing values.

### From Source

1. Clone the repository

   ```bash
   git clone https://github.com/Fovir-GitHub/struct-excel.git
   cd struct-excel
   ```

2. Create and activate virtual environment (Python >= `3.13`)

   ```bash
   python -m venv .venv

   # Linux
   source .venv/bin/activate

   # Windows
   .venv/bin/Activate.ps1
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Execute the script

   ```bash
   python struct_excel/main.py --src /path/to/source/excel
   ```

## Documentation

All documentations are available under the [`docs/`](docs/) folder.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md)
