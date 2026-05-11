# 🔌 YXDB Python Loader for Power BI

> An open-source Python-based workflow for reading Alteryx `.yxdb` files directly inside Power BI using Python scripts — powered by Python and optimized with **Polars** for blazing-fast performance on large datasets.

![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python)
![Power BI](https://img.shields.io/badge/Power%20BI-Custom%20Connector-yellow?logo=powerbi)
![Polars](https://img.shields.io/badge/Polars-Optimized-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Beta-blue)

---

# 🚀 Why this project?

Thousands of companies use **Alteryx + Power BI** together, but there is currently **no native support** for loading `.yxdb` files directly into Power BI.

Without this connector, users typically must:

- Export `.yxdb` → CSV manually
- Lose metadata and data types
- Re-run exports every refresh
- Deal with performance limitations on large datasets

This project eliminates those issues using a lightweight Python workflow inside Power BI.

| Without this connector | With this connector |
|---|---|
| Export YXDB → CSV manually | Load `.yxdb` directly in Power BI |
| Lose metadata and field types | Preserve schema and data types |
| Slow CSV parsing | High-performance Polars engine |
| Memory crashes on large files | Streaming support for massive datasets |
| Manual refresh workflows | Direct refresh from Power BI |

---

# ⚡ Key Features

- ✅ Direct `.yxdb` ingestion inside Power BI Python scripts
- ✅ Powered by **Polars** for high-speed processing
- ✅ Streaming mode for large files (50M+ rows)
- ✅ Apache Parquet intermediate pipeline
- ✅ Schema and data type preservation
- ✅ Lazy execution support
- ✅ Open-source and extensible
- ✅ Automated testing included

---

# ⚡ Performance

Powered by **Polars** — significantly faster and more memory efficient than Pandas for large datasets.

| File Size | Pandas | Polars (this connector) |
|---|---|---|
| 100K rows | ~0.8s | ~0.1s |
| 1M rows | ~8s | ~0.9s |
| 10M rows | ~95s | ~8s |
| 50M+ rows | ❌ Out of memory | ✅ Streaming mode |

## Memory Usage Comparison

| Rows | Pandas RAM Usage | Polars RAM Usage |
|---|---|---|
| 1M | ~800MB | ~180MB |
| 10M | ~8GB | ~1.7GB |
| 50M | ❌ Often crashes | ✅ Streamed processing |

---

# ⚠️ Python Compatibility

## Supported Versions

- ✅ Python 3.11 (**recommended**)
- ✅ Python 3.12

## Unsupported Versions

- ❌ Python 3.13
- ❌ Python 3.14+

Power BI currently has compatibility issues with newer Python releases, which may cause:

```text
ADO.NET: Python script error.
<pi></pi>
```

For best stability, use **Python 3.11**.

---

# 📋 Requirements

- Windows 10 / 11
- Power BI Desktop
- Python 3.11 or 3.12
- Miniconda or Anaconda

---

# 🛠️ Installation

## Step 1 — Clone the repository

```bash
git clone https://github.com/mauromorales-dev/yxdb-powerbi-connector.git
cd yxdb-powerbi-connector
```

---

## Step 2 — Create Python environment

### Recommended (Python 3.11)

```bash
conda create -n powerbi python=3.11 -y
conda activate powerbi
pip install -r requirements.txt
```

---

## Step 3 — Configure Power BI

### Enable custom connectors

```text
File → Options and settings → Options
→ Security → Data Extensions
→ (Not Recommended) Allow any extension to load
→ OK
```

### Configure Python environment

```text
File → Options and settings → Options
→ Python scripting
→ Browse
→ Select:
C:\Users\YourUser\.conda\envs\powerbi
```

⚠️ Do NOT use:

- Python from Microsoft Store
- WindowsApps aliases
- Python 3.13+
- Python 3.14+

---

## Step 4 — Restart Power BI

Completely close and reopen Power BI Desktop.

---

## Step 6 — Connect to your YXDB file

```text
Home → Get Data → Other → Alteryx YXDB → Connect
→ Enter .yxdb file path
→ Load
```

---

# 📁 Project Structure

```text
yxdb-powerbi-connector/
│
├── requirements.txt
├── build.py
│
├── python_bridge/
│   ├── yxdb_reader.py
│   ├── streaming_reader.py
│   └── type_mapper.py
│
├── resources/
│   ├── Icon16.png
│   ├── Icon32.png
│   └── Icon64.png
│
├── tests/
│   └── test_reader.py
│
└── data/
```

---

# 🧠 How It Works

## Standard Pipeline

```text
.yxdb file
    ↓
YxdbReader (yxdb-py)
    ↓
Polars DataFrame
    ↓
JSON serialization
    ↓
Power Query M
    ↓
Power BI Table ✅
```

---

## Large File Streaming Pipeline

For files larger than ~200MB:

```text
.yxdb chunks (500K rows)
    ↓
Polars processing
    ↓
Apache Parquet (Snappy compression)
    ↓
Power BI native Parquet reader ✅
```

---

# 🔧 Supported Data Types

| YXDB Type | Polars Type | Power BI Type |
|---|---|---|
| Int16 / Int32 / Int64 | Int16 / Int32 / Int64 | Whole Number |
| Float / Double | Float32 / Float64 | Decimal Number |
| String / WString | Utf8 | Text |
| Bool | Boolean | True/False |
| Date | Date | Date |
| DateTime | Datetime | Date/Time |
| SpatialObj | Utf8 (GeoJSON) | Text |

---

# ⚠️ Known Limitations

- AMP engine `.yxdb` files are currently unsupported
  - Workaround:
    - Enable `18.1 compatibility` in Alteryx Output Tool
- Requires local Python installation
- Only local file paths supported (network paths planned for v1.1)

---

# 🧪 Running Tests

```bash
conda activate powerbi
python tests/test_reader.py
```

Expected output:

```text
==================================================
🧪 Running tests...
==================================================
✅ test_file_exists
✅ test_basic_read
✅ test_types_not_null
✅ test_schema_consistent
✅ test_df_to_json
✅ test_streaming_parquet
✅ test_lazy_parquet
✅ test_speed
==================================================
📊 Result: 8 passed — 0 failed
🎉 All tests passed!
==================================================
```

---

# 🗺️ Roadmap

```text
v1.0 — MVP ✅
  ✅ Read YXDB files
  ✅ Polars integration
  ✅ Streaming support
  ✅ Automated tests

v1.1 — Coming soon
  ⬜ File browser UI
  ⬜ Preview rows before loading
  ⬜ Column filtering
  ⬜ Network path support

v2.0 — Future
  ⬜ AMP engine support
  ⬜ Microsoft certification
  ⬜ Power BI Service support
```

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/my-feature
```

3. Commit changes

```bash
git commit -m "feat: add my feature"
```

4. Push to GitHub

```bash
git push origin feature/my-feature
```

5. Open a Pull Request

---

# 📄 License

MIT License — see `LICENSE` for details.

---

# 🧪 Example Power BI Python Script

Use this script inside a Power BI Python query:

```python
import sys

sys.path.insert(0, r"C:\Users\DELL\Documents\Portafolio GitHub\yxdb-powerbi-connector\python_bridge")

from yxdb_reader import read_yxdb

YXDB_FILE = r"C:\Users\DELL\Documents\Portafolio GitHub\yxdb-powerbi-connector\data\CO Store File - North.yxdb"

# Read YXDB with Polars
# Convert to Pandas for Power BI compatibility

df = read_yxdb(YXDB_FILE, verbose=False)
dataset = df.to_pandas()
```

---

# 👤 Author

**Mauro Morales**

GitHub:
https://github.com/mauromorales-dev

---

# ⭐ Support the Project

If this connector saved you time, consider giving the repository a ⭐ on GitHub.

It helps other Power BI and Alteryx users discover the project.

---

# 🔗 Related Projects

- https://github.com/tlarsendataguy-yxdb/yxdb-py
- https://github.com/pola-rs/polars
- https://marketplace.visualstudio.com/items?itemName=PowerQuery.vscode-powerquery-sdk

