# Logging Documentation

## Overview

All operations are logged to both **console** and **log files** in the `logs/` directory.

## Log File Location

```
logs/conversion_YYYYMMDD_HHMMSS.log
```

Example: `logs/conversion_20241029_231045.log`

## What Gets Logged

### ✅ Console Output (INFO level)
- Processing start/end
- PDF detection results
- Conversion strategy decisions
- Success/failure status
- Token usage and costs (OpenAI)
- Summary statistics

### 📝 File Output (DEBUG level)
Everything from console **PLUS**:
- Detailed timestamps
- File paths (input/output)
- Character counts
- Extraction details
- Error stack traces
- API call details

## Log Format

### Console
```
📝 Logging to: logs/conversion_20241029_231045.log
============================================================
📂 Found 2 PDF file(s)
============================================================

============================================================
📄 Processing: document.pdf
============================================================
🔍 Analyzing document...
📊 Real tables found: 0
🎯 Strategy: DOCLING
⚙️  Using: Docling
🔄 Converting...
✅ Success: document.md
```

### Log File
```
2024-10-29 23:10:45 | INFO     | 📝 Logging to: logs/conversion_20241029_231045.log
2024-10-29 23:10:45 | INFO     | ============================================================
2024-10-29 23:10:45 | INFO     | 📂 Found 2 PDF file(s)
2024-10-29 23:10:45 | DEBUG    | PDF path: /app/data/raw_docs/document.pdf
2024-10-29 23:10:45 | DEBUG    | Output path: /app/data/output/document.md
2024-10-29 23:10:46 | DEBUG    | Initializing Docling converter
2024-10-29 23:10:48 | DEBUG    | Wrote 1543 characters to /app/data/output/document.md
2024-10-29 23:10:48 | INFO     | ✅ Success: document.md
```

## OpenAI Conversion Logs

When using OpenAI, additional details are logged:

```
🔄 Converting...
📊 Tokens: 4250 in, 3120 out
💰 Cost: $0.0024
✅ Success: document.md
```

**Log file also includes:**
```
2024-10-29 23:15:32 | DEBUG    | Extracting text with pymupdf4llm
2024-10-29 23:15:33 | DEBUG    | Extracted 12543 characters
2024-10-29 23:15:33 | DEBUG    | Calling OpenAI API with model: gpt-4o-mini
2024-10-29 23:15:45 | INFO     | 📊 Tokens: 4250 in, 3120 out
2024-10-29 23:15:45 | INFO     | 💰 Cost: $0.0024
```

## Summary Section

At the end of processing:

```
############################################################
📋 PROCESSING SUMMARY
############################################################
✅ document1.pdf
   Tables: 0 | Converter: Docling
✅ document2.pdf
   Tables: 5 | Converter: OpenAI (gpt-4o-mini)
❌ document3.pdf
   Tables: 0 | Converter: Docling

────────────────────────────────────────────────────────────
Total: 3 | Success: 2 | Failed: 1
############################################################

✅ All done! Check logs: logs/conversion_20241029_231045.log
```

## Error Logging

Errors include full context:

```
❌ Docling conversion failed: Unable to parse PDF structure
```

**In log file:**
```
2024-10-29 23:20:15 | ERROR    | ❌ Docling conversion failed: Unable to parse PDF structure
```

## Accessing Logs in Docker

```bash
# View latest log
docker-compose run --rm pdf-converter tail -f logs/conversion_*.log

# Copy logs to host
docker cp pdf-to-md:/app/logs ./logs
```

## Log Retention

- Logs are **never automatically deleted**
- Each run creates a **new timestamped log file**
- Manually clean old logs when needed:
  ```bash
  rm logs/conversion_*.log
  ```
