"""
医学文献智能翻译助手
面向：医学院学生、临床规培医师、科研初学者
功能：专业术语翻译 + 缩写全称互查
"""

import streamlit as st
from openai import OpenAI
import PyPDF2
import docx
import io
import os
import csv
import re

# ============================================================
# 页面设置
# ============================================================
st.set_page_config(
    page_title="医学文献翻译助手",
    page_icon="🩺",
    layout="wide",
)

# ============================================================
# 自定义样式 — 现代化设计系统
# ============================================================
st.markdown("""
<style>
    /* ── 全局 ── */
    .stApp {
        background: linear-gradient(180deg, #F0F4F8 0%, #F8FAFC 100%);
    }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .block-container {
        padding-top: 2rem !important;
        max-width: 1400px !important;
    }

    /* ── 顶部 Header ── */
    .app-header {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 40%, #00838F 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 24px rgba(13,71,161,0.15);
    }
    .app-header-title {
        font-size: 2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .app-header-sub {
        font-size: 0.95rem;
        color: rgba(255,255,255,0.85);
        margin-top: 0.5rem;
        font-weight: 400;
    }

    /* ── 统计小卡片 ── */
    .stat-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        border: 1px solid #E8ECF0;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .stat-card-icon { font-size: 1.5rem; margin-bottom: 0.25rem; }
    .stat-card-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0D47A1;
    }
    .stat-card-label {
        font-size: 0.8rem;
        color: #6B7280;
        margin-top: 0.15rem;
    }

    /* ── Tab 样式覆盖 ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #FFFFFF;
        border-radius: 12px;
        padding: 0.4rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        border: 1px solid #E8ECF0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 0.55rem 1.25rem !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #F0F4FF !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0D47A1, #1565C0) !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(13,71,161,0.25);
    }

    /* ── 卡片容器 ── */
    .card {
        background: #FFFFFF;
        border: 1px solid #E8ECF0;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .card-header {
        font-size: 1.05rem;
        font-weight: 600;
        color: #1A1A2E;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ── 结果容器 ── */
    .result-box {
        background: #FFFFFF;
        border: 1px solid #E0E7EF;
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1rem 0;
        line-height: 1.8;
        font-size: 0.95rem;
        color: #1E293B;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border-left: 4px solid #1565C0;
    }

    /* ── 缩写标签 ── */
    .abbr-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        color: #E65100;
        padding: 0.3rem 0.7rem;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 0.2rem 0.3rem;
        border: 1px solid #FFCC80;
        transition: transform 0.15s;
    }
    .abbr-chip:hover { transform: scale(1.04); }
    .abbr-chip .arrow { color: #BF360C; font-weight: 400; }

    /* ── 按钮 ── */
    .stButton > button {
        background: linear-gradient(135deg, #0D47A1, #1565C0) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-size: 0.92rem !important;
        transition: all 0.2s !important;
        box-shadow: 0 2px 8px rgba(13,71,161,0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(13,71,161,0.3) !important;
    }
    .stButton > button:active { transform: translateY(0); }

    /* ── 下载按钮 ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00695C, #00897B) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.25rem !important;
        box-shadow: 0 2px 8px rgba(0,105,92,0.2) !important;
        transition: all 0.2s !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(0,105,92,0.3) !important;
    }

    /* ── 文件上传区 ── */
    [data-testid="stFileUploader"] section {
        border: 2px dashed #B0BEC5 !important;
        border-radius: 16px !important;
        background: #FAFBFD !important;
        padding: 1.5rem !important;
        transition: border-color 0.2s, background 0.2s;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #1565C0 !important;
        background: #F0F4FF !important;
    }

    /* ── 速查表卡片 ── */
    .ref-card {
        background: #FFFFFF;
        border: 1px solid #E8ECF0;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.6rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: box-shadow 0.15s;
    }
    .ref-card:hover { box-shadow: 0 3px 10px rgba(0,0,0,0.07); }
    .ref-card-cat {
        font-size: 0.8rem;
        font-weight: 700;
        color: #1565C0;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid #E3F2FD;
    }
    .ref-card-item {
        font-size: 0.82rem;
        color: #37474F;
        padding: 0.2rem 0;
        display: flex;
        align-items: baseline;
        gap: 0.35rem;
    }
    .ref-card-item .abbr-name {
        font-weight: 700;
        color: #0D47A1;
        min-width: 55px;
    }

    /* ── 侧边栏 ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8FAFD 0%, #EEF2F7 100%) !important;
        border-right: 1px solid #DEE2E8 !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding: 1.5rem 1.2rem !important;
    }
    .sidebar-section {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        border: 1px solid #E8ECF0;
    }

    /* ── Textarea ── */
    textarea {
        border: 1px solid #DEE2E8 !important;
        border-radius: 12px !important;
        font-size: 0.92rem !important;
        line-height: 1.7 !important;
        padding: 1rem !important;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    textarea:focus {
        border-color: #1565C0 !important;
        box-shadow: 0 0 0 3px rgba(21,101,192,0.1) !important;
    }

    /* ── Text input ── */
    input[type="text"] {
        border-radius: 10px !important;
        border: 1px solid #DEE2E8 !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.92rem !important;
    }
    input[type="text"]:focus {
        border-color: #1565C0 !important;
        box-shadow: 0 0 0 3px rgba(21,101,192,0.1) !important;
    }

    /* ── Select box ── */
    [data-baseweb="select"] { border-radius: 10px !important; }

    /* ── Expander ── */
    [data-testid="stExpander"] {
        border: 1px solid #E8ECF0 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }

    /* ── Alert ── */
    .stAlert { border-radius: 10px !important; }

    /* ── 页脚 ── */
    .app-footer {
        text-align: center;
        padding: 1.5rem 0 1rem;
        color: #94A3B8;
        font-size: 0.82rem;
        border-top: 1px solid #E8ECF0;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 核心函数
# ============================================================

def get_client():
    """获取 OpenAI 兼容客户端（连接 DeepSeek）"""
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )


def load_terms_from_csv(filepath: str):
    abbreviations = {}
    cn_to_en = {}
    for encoding in ["utf-8-sig", "utf-8", "gbk", "gb2312", "gb18030"]:
        try:
            with open(filepath, "r", encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        abbr = (row.get("缩写") or "").strip()
                        full_en = (row.get("英文全称") or "").strip()
                        full_cn = (row.get("中文译名") or "").strip()
                        if abbr:
                            abbreviations[abbr] = (full_en, full_cn)
                        if full_cn and full_cn not in cn_to_en:
                            cn_to_en[full_cn] = (abbr, full_en)
                    except Exception:
                        pass
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception:
            continue
    return abbreviations, cn_to_en

MEDICAL_ABBREVIATIONS, CN_TO_EN = {}, {}
try:
    MEDICAL_ABBREVIATIONS, CN_TO_EN = load_terms_from_csv(
        os.path.join(os.path.dirname(__file__), "terms.csv")
    )
except Exception:
    pass

def load_vocabulary(filepath: str) -> dict:
    vocab = {}
    for enc in ["utf-8-sig", "utf-8", "gbk", "gb2312", "gb18030"]:
        try:
            with open(filepath, "r", encoding=enc) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        en = (row.get("英文术语") or "").strip().lower()
                        cn = (row.get("中文译名") or "").strip()
                        if en and cn and en not in vocab:
                            vocab[en] = cn
                    except Exception:
                        pass
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception:
            continue
    return vocab

MEDICAL_VOCABULARY = {}
try:
    MEDICAL_VOCABULARY = load_vocabulary(
        os.path.join(os.path.dirname(__file__), "vocabulary.csv")
    )
except Exception:
    pass

_extra_cn = {
    "高血压": ("HTN", "Hypertension"),
    "糖尿病": ("DM", "Diabetes Mellitus"),
    "心肌梗死": ("MI", "Myocardial Infarction"),
    "心力衰竭": ("HF", "Heart Failure"),
    "脑卒中": ("CVA", "Cerebrovascular Accident"),
    "慢性阻塞性肺疾病": ("COPD", "Chronic Obstructive Pulmonary Disease"),
    "磁共振成像": ("MRI", "Magnetic Resonance Imaging"),
    "计算机断层扫描": ("CT", "Computed Tomography"),
    "经皮冠状动脉介入治疗": ("PCI", "Percutaneous Coronary Intervention"),
    "随机对照试验": ("RCT", "Randomized Controlled Trial"),
    "总生存期": ("OS", "Overall Survival"),
    "无进展生存期": ("PFS", "Progression-Free Survival"),
    "急性冠脉综合征": ("ACS", "Acute Coronary Syndrome"),
    "心房颤动": ("AF", "Atrial Fibrillation"),
    "胃食管反流病": ("GERD", "Gastroesophageal Reflux Disease"),
    "非小细胞肺癌": ("NSCLC", "Non-Small Cell Lung Cancer"),
    "急性呼吸窘迫综合征": ("ARDS", "Acute Respiratory Distress Syndrome"),
    "慢性肾脏病": ("CKD", "Chronic Kidney Disease"),
    "炎症性肠病": ("IBD", "Inflammatory Bowel Disease"),
}
for cn, (abbr, en) in _extra_cn.items():
    if cn not in CN_TO_EN:
        CN_TO_EN[cn] = (abbr, en)


def find_abbreviations_in_text(text: str) -> list:
    abbr_list = MEDICAL_ABBREVIATIONS if isinstance(MEDICAL_ABBREVIATIONS, dict) else {}
    found = []
    text_upper = text.upper()
    for abbr, (full_en, full_cn) in abbr_list.items():
        pattern = r'\b' + re.escape(abbr.upper()) + r'\b'
        if re.search(pattern, text_upper):
            found.append((abbr, full_en, full_cn))
    seen = set()
    result = []
    for item in found:
        if item[0] not in seen:
            seen.add(item[0])
            result.append(item)
    result.sort(key=lambda x: x[0])
    return result


def translate_text(client: OpenAI, text: str, target_lang: str = "中文") -> str:
    abbr_list = MEDICAL_ABBREVIATIONS if isinstance(MEDICAL_ABBREVIATIONS, dict) else {}
    vocab_list = MEDICAL_VOCABULARY if isinstance(MEDICAL_VOCABULARY, dict) else {}

    term_ref = "\n".join([
        f"{abbr}: {full_en} -> {full_cn}"
        for abbr, (full_en, full_cn) in sorted(abbr_list.items())
    ])
    vocab_items = list(vocab_list.items())[:500]
    vocab_ref = "\n".join([
        f"{en} -> {cn}"
        for en, cn in sorted(vocab_items)
    ])

    system_prompt = f"""你是一位资深医学翻译专家，专门为医学院校学生、临床规培医师和科研初学者服务。

你的核心任务：将英文医学文献翻译为{target_lang}，严格遵循以下规则：

1. **术语标准化**：优先使用《医学主题词表》(MeSH/CMeSH)中的标准译名。

以下是常见医学缩写对照参考：
{term_ref}

以下是通用医学术语对照参考：
{vocab_ref}

2. **缩写处理**：翻译中遇到的医学缩写，使用格式【缩写：英文全称，中文全称】标注。

3. **学术严谨性**：
   - 不添加原文没有的信息
   - 不删减原文内容
   - 不曲解原文含义
   - 保持段落的逻辑结构

4. **首次出现术语**：对专业术语首次出现时，在括号中附简要中文解释。

5. **罕见术语**：对于新的或罕见的术语，给出参考译名并标注「译名供参考」。

6. 输出格式：逐段翻译，段落之间用空行分隔。先给出翻译结果，再在末尾列出「关键术语注释」部分。
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请翻译以下英文医学文献段落：\n\n{text}"},
        ],
        temperature=0.3,
        max_tokens=4096,
    )
    return response.choices[0].message.content


def lookup_abbreviation(client: OpenAI, query: str) -> str:
    local_results = []
    query_upper = query.strip().upper()
    abbr_list = MEDICAL_ABBREVIATIONS if isinstance(MEDICAL_ABBREVIATIONS, dict) else {}
    if query_upper in abbr_list:
        full_en, full_cn = abbr_list[query_upper]
        local_results.append(f"【本地词库匹配】\n📌 {query_upper}\n→ {full_en}\n→ {full_cn}")
    for cn_name, (abbr, full_en) in CN_TO_EN.items():
        if query.strip() in cn_name or cn_name in query.strip():
            local_results.append(f"【本地词库匹配】\n📌 {cn_name}\n→ {full_en}\n→ 缩写: {abbr}")

    system_prompt = """你是一个医学缩写查询专家。根据用户输入，判断查询方向并回答：

规则：
1. 如果用户输入的是英文缩写，请展开全称并给出中文翻译
2. 如果用户输入的是中文术语，请给出对应的英文全称和常用缩写
3. 如果对应多个缩写，列出所有常见含义并按临床使用频率排序
4. 标注每个术语所属的学科领域

输出格式：
查询词：XXX
类型：缩写展开 / 中文查英文 / ...
结果：
  - 全称（英文）
  - 中文译名
  - 所属学科
  - （如有多种含义，逐条列出）
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"查询：{query}"},
        ],
        temperature=0.2,
        max_tokens=2048,
    )
    api_result = response.choices[0].message.content
    parts = []
    if local_results:
        parts.extend(local_results)
        parts.append("\n---\n📡 **AI 补充查询结果：**\n")
    parts.append(api_result)
    return "\n".join(parts)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    temp_path = os.path.join(os.path.dirname(__file__), "_temp_upload.pdf")
    try:
        with open(temp_path, "wb") as f:
            f.write(file_bytes)
        reader = PyPDF2.PdfReader(temp_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        try:
            os.remove(temp_path)
        except Exception:
            pass
        if text.strip():
            return text.strip()
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    pt = page.extract_text()
                    if pt:
                        text += pt + "\n"
                return text.strip() or "[No extractable text found in PDF]"
        except ImportError:
            return "[PDF text extraction failed. Try converting PDF to TXT first.]"
    except Exception:
        try:
            os.remove(temp_path)
        except Exception:
            pass
        return "[PDF text extraction failed. Try converting PDF to TXT first.]"


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()


# ============================================================
# 侧边栏 — API 配置 + 词库状态
# ============================================================
with st.sidebar:
    st.markdown("### 🔑 API 配置")
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)

    has_secret = "DEEPSEEK_API_KEY" in st.secrets and st.secrets["DEEPSEEK_API_KEY"]
    saved_key = st.secrets.get("DEEPSEEK_API_KEY", "") or os.environ.get("DEEPSEEK_API_KEY", "")

    if has_secret:
        api_key = saved_key
        st.success("✅ 已连接 DeepSeek API")
    else:
        api_key = st.text_input(
            "DeepSeek API Key",
            type="password",
            value=saved_key,
            help="从 platform.deepseek.com 获取",
            placeholder="sk-xxxxxxxxxxxxxxxx",
        )
        if api_key and st.button("💾 记住密钥", use_container_width=True):
            try:
                secrets_dir = os.path.join(os.path.dirname(__file__), ".streamlit")
                os.makedirs(secrets_dir, exist_ok=True)
                with open(os.path.join(secrets_dir, "secrets.toml"), "w") as f:
                    f.write(f'DEEPSEEK_API_KEY = "{api_key}"\n')
                st.success("已保存 ✅")
            except OSError:
                st.info("Cloud 端请在 Settings → Secrets 中配置")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── 词库状态 ──
    st.markdown("### 📊 词库状态")
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    abbr_count = len(MEDICAL_ABBREVIATIONS) if isinstance(MEDICAL_ABBREVIATIONS, dict) else 0
    vocab_count = len(MEDICAL_VOCABULARY) if isinstance(MEDICAL_VOCABULARY, dict) else 0
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem;">
      <span style="color:#6B7280;">📋 缩写术语</span>
      <span style="font-weight:700;color:#0D47A1;">{abbr_count:,} 条</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:0.4rem;">
      <span style="color:#6B7280;">📖 通用词汇</span>
      <span style="font-weight:700;color:#1565C0;">{vocab_count:,} 条</span>
    </div>
    <div style="display:flex;justify-content:space-between;">
      <span style="color:#6B7280;">🔤 中文术语</span>
      <span style="font-weight:700;color:#00838F;">{len(CN_TO_EN):,} 条</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 使用说明 ──
    with st.expander("📖 使用说明"):
        st.markdown("""
        **三大功能**
        - 📝 **文献翻译**：粘贴段落 → 专业翻译
        - 🔍 **缩写互查**：缩写 ↔ 全称 ↔ 中文
        - 📄 **文件翻译**：上传 PDF/Word/TXT

        **特色**
        - 优先匹配 MeSH 标准译名
        - 自动识别医学缩写并展开
        - 罕见术语标注「待确认」

        **隐私**
        内容仅发送至 DeepSeek API，不作他用。
        """)

# ============================================================
# 标题区
# ============================================================
st.markdown(f"""
<div class="app-header">
    <div class="app-header-title">🩺 医学文献智能翻译助手</div>
    <div class="app-header-sub">
        面向医学院学生 · 临床规培医师 · 科研初学者 ｜ 精准专业术语翻译 · 缩写全称互查
    </div>
</div>
""", unsafe_allow_html=True)

# ── 统计卡片 ──
cols_stats = st.columns(4)
stat_items = [
    ("📋", f"{abbr_count:,}", "医学缩写术语"),
    ("📖", f"{vocab_count:,}", "通用医学词汇"),
    ("🔤", f"{len(CN_TO_EN):,}", "中文索引条目"),
    ("🤖", "DeepSeek", "翻译引擎"),
]
for idx, (icon, value, label) in enumerate(stat_items):
    with cols_stats[idx]:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-card-icon">{icon}</div>
            <div class="stat-card-value">{value}</div>
            <div class="stat-card-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# 主界面 — 功能标签页
# ============================================================
tab1, tab2, tab3 = st.tabs([
    "📝 文献翻译",
    "🔍 缩写互查",
    "📄 文件上传翻译",
])

# ============ Tab 1: 文献翻译 ============
with tab1:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">📥 输入英文文献段落</div>
        """, unsafe_allow_html=True)

        input_text = st.text_area(
            "英文原文",
            height=320,
            placeholder="在此粘贴英文医学文献段落...\n\n示例：\nPatients with ST-segment elevation myocardial infarction (STEMI) who underwent primary PCI within 12 hours of symptom onset showed significantly improved LVEF at 6-month follow-up...",
            label_visibility="collapsed",
        )

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1.2, 1.5])
        with col_btn1:
            translate_btn = st.button("🔄 开始翻译", use_container_width=True, type="primary")
        with col_btn2:
            target_lang = st.selectbox("目标语言", ["中文", "英文"], label_visibility="collapsed")
        with col_btn3:
            char_count = len(input_text.strip()) if input_text else 0
            if char_count:
                st.caption(f"📊 已输入 {char_count} 字符")

        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("💡 测试例句"):
            st.code("""Patients with ST-segment elevation myocardial infarction (STEMI)
who underwent primary PCI within 12 hours of symptom onset
showed significantly improved LVEF at 6-month follow-up
compared to those receiving thrombolytic therapy.
The incidence of major adverse cardiovascular events (MACE)
was also lower in the PCI group (8.3% vs 15.7%, p<0.001).""", language=None)

    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">📤 翻译结果</div>
        """, unsafe_allow_html=True)

        if translate_btn:
            if not api_key:
                st.error("⚠️ 请先在左侧边栏输入 DeepSeek API Key")
                st.markdown("没有？→ [点此获取](https://platform.deepseek.com)")
            elif not input_text.strip():
                st.warning("⚠️ 请先输入要翻译的英文文献段落")
            else:
                with st.spinner("🩺 翻译中，正在匹配医学术语标准译名..."):
                    try:
                        client = get_client()
                        result = translate_text(client, input_text, target_lang)

                        abbreviations = find_abbreviations_in_text(input_text)
                        if abbreviations:
                            st.markdown("##### 🔬 识别的医学缩写")
                            chips_html = ""
                            for abbr, full_en, full_cn in abbreviations:
                                chips_html += (
                                    f'<span class="abbr-chip">'
                                    f'<strong>{abbr}</strong>'
                                    f'<span class="arrow">→</span>'
                                    f'{full_cn}'
                                    f'</span> '
                                )
                            st.markdown(chips_html, unsafe_allow_html=True)

                        st.markdown("##### 📝 翻译正文")
                        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"翻译失败：{str(e)}")
                        st.caption("常见原因：API Key 无效、网络不通、或余额不足")

        st.markdown("</div>", unsafe_allow_html=True)


# ============ Tab 2: 缩写互查 ============
with tab2:
    st.markdown("""
    <div class="card">
        <div class="card-header">🔍 医学缩写 / 术语互查</div>
    """, unsafe_allow_html=True)

    col_q1, col_q2 = st.columns([4, 1])
    with col_q1:
        query_term = st.text_input(
            "输入要查询的术语",
            placeholder="例如：PCI  /  经皮冠状动脉介入治疗  /  myocardial infarction",
            label_visibility="collapsed",
        )
    with col_q2:
        search_btn = st.button("🔍 查询", use_container_width=True, type="primary")

    if search_btn:
        if not api_key:
            st.error("⚠️ 请先在左侧边栏输入 DeepSeek API Key")
        elif not query_term.strip():
            st.warning("⚠️ 请输入要查询的术语")
        else:
            with st.spinner("查询中..."):
                try:
                    client = get_client()
                    result = lookup_abbreviation(client, query_term)
                    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"查询失败：{str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── 常用缩写速查表 ──
    with st.expander("📚 常用医学缩写速查表", expanded=False):
        abbr_dict = MEDICAL_ABBREVIATIONS if isinstance(MEDICAL_ABBREVIATIONS, dict) else {}
        categories = {
            "🫀 心血管系统": ["STEMI", "NSTEMI", "PCI", "CABG", "ACS", "HF", "AF", "LVEF", "HTN", "CAD", "MI", "MACE"],
            "🫁 呼吸系统": ["COPD", "ARDS", "PE", "OSA", "FEV1", "FVC"],
            "🧠 神经精神": ["CVA", "TIA", "AD", "PD", "MS", "EEG"],
            "📷 影像检查": ["MRI", "CT", "PET", "SPECT", "US"],
            "🩸 内分泌代谢": ["DM", "T2DM", "HbA1c", "TSH", "PCOS", "DKA"],
            "🎗️ 肿瘤学": ["NSCLC", "CRC", "HCC", "OS", "PFS", "CR", "PR"],
            "📊 临床研究": ["RCT", "OR", "RR", "HR", "CI", "ITT", "PP", "AE", "SAE"],
            "🔬 实验室检查": ["RBC", "WBC", "PLT", "Hb", "INR", "PT", "APTT"],
            "🍽️ 消化系统": ["GERD", "IBD", "UC", "CD", "IBS", "NAFLD"],
            "💊 给药方式": ["q.d.", "b.i.d.", "t.i.d.", "p.r.n.", "NPO", "STAT"],
        }

        cols = st.columns(2)
        cat_list = list(categories.items())
        half = (len(cat_list) + 1) // 2

        for col_idx, start in enumerate([0, half]):
            with cols[col_idx]:
                for cat_name, abbrs in cat_list[start:start + half]:
                    items_html = ""
                    for a in abbrs:
                        if a in abbr_dict:
                            _, full_cn = abbr_dict[a]
                            items_html += (
                                f'<div class="ref-card-item">'
                                f'<span class="abbr-name">{a}</span>'
                                f'<span>{full_cn}</span>'
                                f'</div>'
                            )
                    if items_html:
                        st.markdown(f"""
                        <div class="ref-card">
                            <div class="ref-card-cat">{cat_name}</div>
                            {items_html}
                        </div>
                        """, unsafe_allow_html=True)


# ============ Tab 3: 文件上传翻译 ============
with tab3:
    st.markdown("""
    <div class="card">
        <div class="card-header">📄 上传文献文件，自动翻译</div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "拖拽或点击上传 PDF / Word / TXT 文件",
        type=["pdf", "docx", "txt"],
        help="单文件不超过 10MB",
        label_visibility="collapsed",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file:
        file_bytes = uploaded_file.read()
        file_type = uploaded_file.name.split(".")[-1].lower()

        with st.spinner(f"📄 正在提取文件内容（{file_type.upper()}）..."):
            try:
                if file_type == "pdf":
                    extracted_text = extract_text_from_pdf(file_bytes)
                elif file_type == "docx":
                    extracted_text = extract_text_from_docx(file_bytes)
                else:
                    extracted_text = file_bytes.decode("utf-8", errors="replace")
            except Exception as e:
                st.error(f"提取文件内容失败：{str(e)}")
                extracted_text = ""

        if extracted_text:
            st.success(f"✅ 成功提取 {len(extracted_text):,} 个字符")

            with st.expander("📄 原文预览"):
                preview_len = min(2500, len(extracted_text))
                st.text_area(
                    "原文内容",
                    value=extracted_text[:preview_len],
                    height=200,
                    disabled=True,
                    label_visibility="collapsed",
                )
                if len(extracted_text) > preview_len:
                    st.caption(f"仅显示前 {preview_len:,} 字符，全文共 {len(extracted_text):,} 字符")

            # 缩写识别结果
            abbreviations = find_abbreviations_in_text(extracted_text)
            if abbreviations:
                with st.expander(f"🔬 文献中识别的医学缩写（{len(abbreviations)} 个）", expanded=False):
                    chips_html = ""
                    for abbr, full_en, full_cn in abbreviations:
                        chips_html += (
                            f'<span class="abbr-chip">'
                            f'<strong>{abbr}</strong>'
                            f'<span class="arrow">→</span>'
                            f'{full_cn}'
                            f'</span> '
                        )
                    st.markdown(chips_html, unsafe_allow_html=True)

            # 翻译按钮
                if not api_key:
                    st.error("⚠️ 请先在左侧边栏输入 DeepSeek API Key")
                else:
                    MAX_CHUNK = 2000
                    chunks = []
                    paragraphs = extracted_text.split("\n")
                    current_chunk = ""
                    for para in paragraphs:
                        if len(current_chunk) + len(para) < MAX_CHUNK:
                            current_chunk += para + "\n"
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = para + "\n"
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())

                    st.info(f"📑 文档共 {len(chunks)} 段，正在分段翻译...")

                    full_result = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        client = get_client()
                        for i, chunk in enumerate(chunks):
                            status_text.text(f"正在翻译第 {i+1}/{len(chunks)} 段...")
                            result = translate_text(client, chunk)
                            full_result.append(result)
                            progress_bar.progress((i + 1) / len(chunks))

                        status_text.text("✅ 翻译完成！")
                        combined = "\n\n---\n\n".join(full_result)

                        st.markdown("##### 📝 翻译结果")
                        st.markdown(f'<div class="result-box">{combined}</div>', unsafe_allow_html=True)

                        col_dl1, col_dl2 = st.columns([1, 3])
                        with col_dl1:
                            st.download_button(
                                label="📥 下载翻译结果",
                                data=combined,
                                file_name=f"翻译_{uploaded_file.name.rsplit('.', 1)[0]}.txt",
                                mime="text/plain",
                                use_container_width=True,
                            )

                    except Exception as e:
                        st.error(f"翻译失败：{str(e)}")

# ============================================================
# 页脚
# ============================================================
st.markdown("""
<div class="app-footer">
    🩺 医学文献智能翻译助手 &nbsp;|&nbsp;
    基于 DeepSeek 大模型 + 内置医学标准术语库 &nbsp;|&nbsp;
    翻译结果仅供学习参考，临床决策请以原文为准
</div>
""", unsafe_allow_html=True)
