"""
医学文献翻译 API 服务器
为 Zotero 插件提供翻译接口，共享 terms.csv / vocabulary.csv 词库
本地运行：python api_server.py
"""

from flask import Flask, request, jsonify
from openai import OpenAI
import csv
import os
import re
import sys

app = Flask(__name__)

# ============================================================
# 词库加载
# ============================================================
def _load_csv_safe(filename):
    results = []
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(filepath):
        return results
    for enc in ["utf-8-sig", "utf-8", "gbk", "gb2312", "gb18030"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        if "terms" in filename:
                            abbr = (row.get("缩写") or "").strip()
                            full_en = (row.get("英文全称") or "").strip()
                            full_cn = (row.get("中文译名") or "").strip()
                            if abbr:
                                results.append((abbr, (full_en, full_cn)))
                        else:
                            en = (row.get("英文术语") or "").strip().lower()
                            cn = (row.get("中文译名") or "").strip()
                            if en and cn:
                                results.append((en, cn))
                    except Exception:
                        pass
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception:
            continue
    return results

def load_terms():
    abbreviations = {}
    for abbr, (full_en, full_cn) in _load_csv_safe("terms.csv"):
        abbreviations[abbr] = (full_en, full_cn)
    cn_to_en = {}
    for abbr, (full_en, full_cn) in abbreviations.items():
        if full_cn and full_cn not in cn_to_en:
            cn_to_en[full_cn] = (abbr, full_en)
    return abbreviations, cn_to_en

def load_vocabulary():
    vocab = {}
    for en, cn in _load_csv_safe("vocabulary.csv"):
        vocab[en] = cn
    return vocab


MEDICAL_ABBREVIATIONS, CN_TO_EN = load_terms()
MEDICAL_VOCABULARY = load_vocabulary()
print(f"[OK] Loaded {len(MEDICAL_ABBREVIATIONS)} abbreviations + {len(MEDICAL_VOCABULARY)} vocabulary terms")

# ============================================================
# API Key & Client
# ============================================================
def get_api_key():
    return os.environ.get("DEEPSEEK_API_KEY", "")

def get_client():
    key = get_api_key()
    if not key:
        return None
    return OpenAI(api_key=key, base_url="https://api.deepseek.com")

# ============================================================
# 翻译核心
# ============================================================
def find_abbreviations(text):
    found = []
    text_upper = text.upper()
    for abbr, (full_en, full_cn) in MEDICAL_ABBREVIATIONS.items():
        pattern = r'\b' + re.escape(abbr.upper()) + r'\b'
        if re.search(pattern, text_upper):
            found.append({"abbr": abbr, "full_en": full_en, "cn": full_cn})
    found.sort(key=lambda x: x["abbr"])
    return found[:30]

def build_prompt():
    term_ref = "\n".join([
        f"{abbr}: {full_en} -> {full_cn}"
        for abbr, (full_en, full_cn) in sorted(MEDICAL_ABBREVIATIONS.items())[:300]
    ])
    vocab_ref = "\n".join([
        f"{en} -> {cn}"
        for en, cn in sorted(MEDICAL_VOCABULARY.items())[:300]
    ])
    return f"""You are a senior medical translation expert. Translate English medical literature into Chinese.

Rules:
1. Use MeSH/CMeSH standard terminology.
2. Mark abbreviations as [ABBR: full English, full Chinese].
3. Be academically rigorous - no additions, omissions, or distortions.
4. Mark rare terms as [reference translation].

Abbreviation reference:
{term_ref}

General term reference:
{vocab_ref}

Output the translation paragraph by paragraph, then list Key Term Notes at the end."""

# ============================================================
# API Endpoints
# ============================================================
@app.route("/api/translate", methods=["POST"])
def translate():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    client = get_client()
    if not client:
        return jsonify({"error": "API Key not configured"}), 500

    abbrs = find_abbreviations(text)

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": build_prompt()},
                {"role": "user", "content": f"Please translate the following English medical text:\n\n{text}"},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
        translation = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": f"Translation API error: {str(e)}"}), 500

    return jsonify({
        "original": text,
        "translation": translation,
        "abbreviations": abbrs,
        "term_count": len(MEDICAL_ABBREVIATIONS),
    })

@app.route("/api/lookup", methods=["POST"])
def lookup():
    data = request.get_json(force=True)
    query = (data.get("query") or "").strip()
    if not query:
        return jsonify({"error": "query is required"}), 400

    local = []
    query_upper = query.upper()

    if query_upper in MEDICAL_ABBREVIATIONS:
        full_en, full_cn = MEDICAL_ABBREVIATIONS[query_upper]
        local.append({"abbr": query_upper, "full_en": full_en, "cn": full_cn})

    for cn_name, (abbr, full_en) in CN_TO_EN.items():
        if query in cn_name or cn_name in query:
            local.append({"cn": cn_name, "full_en": full_en, "abbr": abbr})

    query_lower = query.lower()
    if query_lower in MEDICAL_VOCABULARY:
        local.append({"en": query, "cn": MEDICAL_VOCABULARY[query_lower]})

    # AI supplement
    client = get_client()
    ai_result = ""
    if client:
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a medical abbreviation lookup expert. Given a query term, determine if it's an abbreviation or a Chinese medical term, then provide the English full name and Chinese translation. If an abbreviation has multiple meanings, list all by clinical frequency."},
                    {"role": "user", "content": f"Lookup: {query}"},
                ],
                temperature=0.2,
                max_tokens=2048,
            )
            ai_result = response.choices[0].message.content
        except Exception as e:
            ai_result = f"AI lookup failed: {e}"

    return jsonify({
        "query": query,
        "local_results": local,
        "ai_result": ai_result,
    })

@app.route("/api/stats")
def stats():
    return jsonify({
        "abbreviations": len(MEDICAL_ABBREVIATIONS),
        "vocabulary": len(MEDICAL_VOCABULARY),
        "status": "running",
    })

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

# ============================================================
# 启动
# ============================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"[Medical Translator API] http://localhost:{port}")
    print(f"[Terms] {len(MEDICAL_ABBREVIATIONS)} abbreviations + {len(MEDICAL_VOCABULARY)} vocabulary")
    app.run(host="0.0.0.0", port=port, debug=False)
