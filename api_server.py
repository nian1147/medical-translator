"""
Medical Translation API Server
Uses plain requests to call DeepSeek API (avoids httpx encoding bug on CJK Windows)
Usage: python api_server.py
"""
import sys, io, os, csv, re, json, requests

# Force UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from flask import Flask, request, Response

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

# ============================================================
# Load term libraries
# ============================================================
def _load_csv(filename):
    rows = []
    path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(path):
        return rows
    for enc in ["utf-8-sig", "utf-8", "gbk", "gb18030"]:
        try:
            with open(path, "r", encoding=enc) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        if "terms" in filename:
                            a = (row.get("缩写") or "").strip()
                            e = (row.get("英文全称") or "").strip()
                            c = (row.get("中文译名") or "").strip()
                            if a: rows.append(("abbr", a, e, c))
                        else:
                            e = (row.get("英文术语") or "").strip().lower()
                            c = (row.get("中文译名") or "").strip()
                            if e and c: rows.append(("vocab", e, c))
                    except Exception:
                        pass
            break
        except Exception:
            continue
    return rows

abbr_dict = {}
cn_to_en = {}
vocab_dict = {}

for row in _load_csv("terms.csv"):
    _, a, e, c = row
    abbr_dict[a] = (e, c)
    if c and c not in cn_to_en:
        cn_to_en[c] = (a, e)

for row in _load_csv("vocabulary.csv"):
    _, e, c = row
    vocab_dict[e] = c

print(f"[OK] {len(abbr_dict)} abbreviations + {len(vocab_dict)} vocabulary loaded")

# ============================================================
# API Key
# ============================================================
def get_key():
    k = os.environ.get("DEEPSEEK_API_KEY", "")
    if k: return k
    sp = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    if os.path.exists(sp):
        with open(sp, "r") as f:
            for line in f:
                if "=" in line and "DEEPSEEK_API_KEY" in line:
                    k = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if k: return k
    return k

# ============================================================
# Call DeepSeek via plain HTTP requests (no openai/httpx)
# ============================================================
def deepseek_chat(messages, temperature=0.3, max_tokens=4096):
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {get_key()}",
    }
    body = {
        "model": "deepseek-v4-flash",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    # Use data= with explicit UTF-8 bytes to avoid latin-1 encoding issues
    body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
    resp = requests.post(DEEPSEEK_URL, headers=headers, data=body_bytes, timeout=60)
    if resp.status_code != 200:
        raise Exception(f"DeepSeek returned {resp.status_code}: {resp.text[:300]}")
    return resp.json()["choices"][0]["message"]["content"]

# ============================================================
# Translate
# ============================================================
@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    if not text:
        return _json_err("text is required", 400)

    key = get_key()
    if not key:
        return _json_err("API Key not configured", 500)

    # Find abbreviations in text
    found = []
    for a, (e, c) in sorted(abbr_dict.items()):
        if re.search(r'\b' + re.escape(a.upper()) + r'\b', text.upper()):
            found.append({"abbr": a, "en": e, "cn": c})
            if len(found) >= 30:
                break

    # Find matched vocabulary in text
    found_vocab = []
    text_lower = text.lower()
    for e, c in sorted(vocab_dict.items()):
        if e and (" " in e or len(e) > 4):
            if re.search(r'\b' + re.escape(e) + r'\b', text_lower):
                found_vocab.append(f"{e} -> {c}")
                if len(found_vocab) >= 20:
                    break

    # Build system prompt using only matched terms (not the whole dictionary)
    sample = "\n".join([
        f"{f['abbr']}: {f['en']} -> {f['cn']}" for f in found
    ])
    vocab_sample = "\n".join(found_vocab)
    system = (
        "You are an expert medical translator. Translate the following English medical text into Simplified Chinese.\n"
        "Use standard MeSH/CMeSH terminology and the references below.\n"
        "Output only the translation. Do not add any annotations, explanations, or terminology lists.\n"
        "Standard abbreviations:\n" + sample +
        "\n\nMedical vocabulary:\n" + vocab_sample
    )

    try:
        result = deepseek_chat([
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ])
    except Exception as e:
        return _json_err(f"DeepSeek API error: {e}", 500)

    return _json_ok({
        "original": text,
        "translation": result,
        "abbreviations": found,
        "term_count": len(abbr_dict),
    })

# ============================================================
# Lookup
# ============================================================
@app.route("/api/lookup", methods=["POST"])
def lookup():
    data = request.get_json(force=True)
    query = (data.get("query") or "").strip()
    if not query:
        return _json_err("query is required", 400)

    local = []
    qu = query.upper()
    if qu in abbr_dict:
        e, c = abbr_dict[qu]
        local.append({"type": "abbr", "abbr": qu, "en": e, "cn": c})
    for cn, (a, e) in cn_to_en.items():
        if query in cn or cn in query:
            local.append({"type": "cn2en", "cn": cn, "en": e, "abbr": a})
            if len(local) >= 5:
                break
    ql = query.lower()
    if ql in vocab_dict:
        local.append({"type": "vocab", "en": query, "cn": vocab_dict[ql]})

    key = get_key()
    ai_text = ""
    if key:
        try:
            ai_text = deepseek_chat(
                [
                    {"role": "system", "content": "You are a medical abbreviation expert. Given a query, determine if it is an abbreviation or Chinese medical term. Provide English full name and Chinese translation."},
                    {"role": "user", "content": f"Lookup: {query}"},
                ],
                temperature=0.2, max_tokens=2048,
            )
        except Exception as e:
            ai_text = f"AI lookup failed: {e}"

    return _json_ok({"query": query, "local": local, "ai_result": ai_text})

# ============================================================
# Stats / Health
# ============================================================
@app.route("/api/stats")
def stats():
    return _json_ok({"abbreviations": len(abbr_dict), "vocabulary": len(vocab_dict), "status": "running"})

@app.route("/api/health")
def health():
    return _json_ok({"status": "ok"})

# ============================================================
# JSON helpers
# ============================================================
def _json_ok(data):
    return Response(
        json.dumps(data, ensure_ascii=False, indent=None),
        status=200, mimetype="application/json; charset=utf-8",
    )

def _json_err(msg, code):
    return Response(
        json.dumps({"error": msg}, ensure_ascii=False, indent=None),
        status=code, mimetype="application/json; charset=utf-8",
    )

# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"[API] http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
