"""

# Medical Translator - Zotero Plugin Setup

## 1. Start the API Server

```bash
cd medical-translator
set DEEPSEEK_API_KEY=your-api-key-here
python api_server.py
```

Keep the terminal open. You should see:
```
[OK] Loaded 3375 abbreviations + 801 vocabulary terms
[Medical Translator API] http://localhost:8765
```

## 2. Pack the Plugin

Inside the `zotero-plugin/` folder, select `manifest.json` AND `bootstrap.js`:
  - Right-click -> Send to -> Compressed (zipped) folder
  - Rename the .zip to `medical-translator.xpi`

## 3. Install in Zotero

  - Open Zotero 7
  - Tools -> Add-ons -> Gear icon -> Install Add-on From File
  - Select `medical-translator.xpi`
  - Restart Zotero

## 4. Use

  - Open a PDF in Zotero
  - Select English text
  - Press Ctrl+Shift+T or click the "Translate" button
  - Translation appears in a popup

## 5. Deploy API to the Cloud (Optional)

Deploy api_server.py, terms.csv, vocabulary.csv, and requirements.txt to Render:
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `gunicorn api_server:app --bind 0.0.0.0:$PORT`
  - Add environment variable: `DEEPSEEK_API_KEY`
  - Then change `API_BASE` in bootstrap.js to your Render URL
"""

