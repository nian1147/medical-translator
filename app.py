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
# 自定义样式
# ============================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1A5276;
    }
    .sub-title {
        font-size: 1rem;
        color: #5D6D7E;
        margin-bottom: 1.5rem;
    }
    .result-box {
        background-color: #F8F9FA;
        border-left: 4px solid #2E86C1;
        padding: 20px;
        border-radius: 8px;
        margin: 15px 0;
    }
    .term-highlight {
        background-color: #D4EFDF;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
    }
    .abbr-tag {
        background-color: #FADBD8;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #922B21;
    }
    .stButton button {
        background-color: #2E86C1;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 24px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 标题区
# ============================================================
st.markdown('<div class="main-title">🩺 医学文献智能翻译助手</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">'
    '面向医学院学生 · 临床规培医师 · 科研初学者 | '
    '精准专业术语翻译 · 缩写全称互查'
    '</div>',
    unsafe_allow_html=True,
)

# ============================================================
# 侧边栏 — API 配置
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ 设置")

    # API Key — Cloud 端用 Secrets 配置，本地可手动输入
    has_secret = "DEEPSEEK_API_KEY" in st.secrets and st.secrets["DEEPSEEK_API_KEY"]
    saved_key = st.secrets.get("DEEPSEEK_API_KEY", "") or os.environ.get("DEEPSEEK_API_KEY", "")

    if has_secret:
        # Cloud 端：Key 已在后台配置，不展示给用户
        api_key = saved_key
        st.success("✅ API Key 已配置，可直接使用")
    else:
        # 本地端：需要用户手动输入
        api_key = st.text_input(
            "🔑 DeepSeek API Key",
            type="password",
            value=saved_key,
            help="从 platform.deepseek.com 获取，形如 sk-xxxxxxxx",
            placeholder="sk-xxxxxxxxxxxxxxxx",
        )

    # 保存 API Key（仅本地端无 secrets 时显示）
    if not has_secret and api_key and st.button("💾 记住 API Key（下次不用重新输）"):
            try:
                secrets_dir = os.path.join(os.path.dirname(__file__), ".streamlit")
                os.makedirs(secrets_dir, exist_ok=True)
                with open(os.path.join(secrets_dir, "secrets.toml"), "w") as f:
                    f.write(f'DEEPSEEK_API_KEY = "{api_key}"\n')
                st.success("已保存！下次打开自动加载 ✅")
            except OSError:
                st.info("💡 你在 Cloud 端运行，请在「Settings → Secrets」中配置 API Key")

    st.markdown("---")

    # 词库统计
    try:
        abbr_count = len(MEDICAL_ABBREVIATIONS)
    except Exception:
        abbr_count = 0
    try:
        vocab_count = len(MEDICAL_VOCABULARY)
    except Exception:
        vocab_count = 0
    st.markdown(f"## 📚 术语库")
    st.caption(f"已加载 {abbr_count} 个缩写术语 + {vocab_count} 个通用术语")

    st.markdown("---")

    # 使用说明
    st.markdown("## 📖 使用说明")
    st.markdown("""
    **三大功能：**
    1. 📝 **文献翻译** — 粘贴英文段落，获得专业翻译
    2. 🔍 **缩写互查** — 缩写↔全称 中文↔英文缩写
    3. 📄 **文件上传** — 支持 PDF / Word / TXT

    **术语标准：**
    - 优先匹配 MeSH / CMeSH 标准译名
    - 罕见术语标注「待确认」
    - 自动识别并展开缩写

    **隐私说明：**
    你的内容只会发送给 DeepSeek API，
    不会被用于其他用途。
    """)

# ============================================================
# 核心函数
# ============================================================

def get_client():
    """获取 OpenAI 兼容客户端（连接 DeepSeek）"""
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )


# ============ 医学术语库 — 从 CSV 文件加载 ============
# CSV 文件路径：terms.csv，格式：缩写,英文全称,中文译名,学科
# 用 Excel 打开 terms.csv 即可编辑，保存后重启应用生效

def load_terms_from_csv(filepath: str):
    """从 CSV 文件加载医学术语库（自动检测编码，容错所有异常）"""
    abbreviations = {}
    cn_to_en = {}

    for encoding in ["utf-8-sig", "utf-8", "gbk", "gb2312", "gb18030"]:
        try:
            with open(filepath, "r", encoding=encoding) as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, start=2):  # 从第2行开始（第1行是表头）
                    try:
                        abbr = (row.get("缩写") or "").strip()
                        full_en = (row.get("英文全称") or "").strip()
                        full_cn = (row.get("中文译名") or "").strip()
                        if abbr:
                            abbreviations[abbr] = (full_en, full_cn)
                        if full_cn and full_cn not in cn_to_en:
                            cn_to_en[full_cn] = (abbr, full_en)
                    except Exception:
                        pass  # 跳过坏行
            break  # 读取成功
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception as e:
            # 其他异常（如文件损坏），跳过该编码尝试下一个
            continue

    return abbreviations, cn_to_en

MEDICAL_ABBREVIATIONS, CN_TO_EN = {}, {}
try:
    MEDICAL_ABBREVIATIONS, CN_TO_EN = load_terms_from_csv(
        os.path.join(os.path.dirname(__file__), "terms.csv")
    )
except Exception:
    pass

# 加载通用医学词汇（无缩写，仅中英文对照，翻译时作为术语参考）
def load_vocabulary(filepath: str) -> dict:
    """加载通用医学词汇表（英文术语→中文译名，容错所有异常）"""
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

# 额外中文术语（CSV 中可能没有的标准中文别名）
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
    """扫描文本中与内置术语库匹配的缩写，返回 (缩写, 全称, 中文) 列表"""
    found = []
    text_upper = text.upper()
    for abbr, (full_en, full_cn) in MEDICAL_ABBREVIATIONS.items():
        pattern = r'\b' + re.escape(abbr.upper()) + r'\b'
        if re.search(pattern, text_upper):
            found.append((abbr, full_en, full_cn))
    # 去重并按缩写排序
    seen = set()
    result = []
    for item in found:
        if item[0] not in seen:
            seen.add(item[0])
            result.append(item)
    result.sort(key=lambda x: x[0])
    return result


def translate_text(client: OpenAI, text: str, target_lang: str = "中文") -> str:
    """调用 DeepSeek API 翻译医学文献"""

    # 构建医学术语参考表
    # 1. 缩写对照表
    term_ref = "\n".join([
        f"{abbr}: {full_en} → {full_cn}"
        for abbr, (full_en, full_cn) in sorted(MEDICAL_ABBREVIATIONS.items())
    ])

    # 2. 通用词汇表（抽样防止prompt过长，最多取500条）
    vocab_sample = dict(list(MEDICAL_VOCABULARY.items())[:500])
    vocab_ref = "\n".join([
        f"{en} → {cn}"
        for en, cn in sorted(vocab_sample.items())
    ])

    system_prompt = f"""你是一位资深医学翻译专家，专门为医学院校学生、临床规培医师和科研初学者服务。

你的核心任务：将英文医学文献翻译为{target_lang}，严格遵循以下规则：

1. **术语标准化**：优先使用《医学主题词表》(MeSH/CMeSH)中的标准译名。

以下是常见医学缩写对照参考：
{term_ref}

以下是通用医学术语对照参考：
{vocab_ref}

2. **缩写处理**：翻译中遇到的医学缩写，使用格式【缩写：英文全称，中文全称】标注。例如：The patient underwent PCI → 患者接受了【PCI：Percutaneous Coronary Intervention，经皮冠状动脉介入治疗】。

3. **学术严谨性**：
   - 不添加原文没有的信息
   - 不删减原文内容
   - 不曲解原文含义
   - 保持段落的逻辑结构

4. **首次出现术语**：对专业术语首次出现时，在括号中附简要中文解释。例如：患者出现心肌顿抑（myocardial stunning，心肌短暂缺血后收缩功能障碍，再灌注后可恢复）。

5. **罕见术语**：对于新的或罕见的术语，给出参考译名并标注「译名供参考」，格式：罕见术语（参考译名，译名供参考）。

6. 输出格式：逐段翻译，段落之间用空行分隔。先给出翻译结果，再在末尾列出「关键术语注释」部分。
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请翻译以下英文医学文献段落：\n\n{text}"},
        ],
        temperature=0.3,  # 低温度保证翻译一致性和准确性
        max_tokens=4096,
    )

    return response.choices[0].message.content


def lookup_abbreviation(client: OpenAI, query: str, direction: str = "auto") -> str:
    """缩写/全称互查
    direction: "auto"自动检测 / "abbr2full"缩写→全称 / "zh2en"中文→英文缩写
    """

    # 先查本地词库
    local_results = []

    # 尝试直接匹配缩写
    query_upper = query.strip().upper()
    if query_upper in MEDICAL_ABBREVIATIONS:
        full_en, full_cn = MEDICAL_ABBREVIATIONS[query_upper]
        local_results.append(f"【本地词库匹配】\n📌 {query_upper}\n→ {full_en}\n→ {full_cn}")

    # 尝试中文模糊匹配
    for cn_name, (abbr, full_en) in CN_TO_EN.items():
        if query.strip() in cn_name or cn_name in query.strip():
            local_results.append(f"【本地词库匹配】\n📌 {cn_name}\n→ {full_en}\n→ 缩写: {abbr}")

    # 调用大模型补充
    system_prompt = """你是一个医学缩写查询专家。根据用户输入，判断查询方向并回答：

规则：
1. 如果用户输入的是英文缩写（如 PCI, STEMI, COPD），请展开全称并给出中文翻译
2. 如果用户输入的是中文术语，请给出对应的英文全称和常用缩写
3. 如果对应多个缩写（如 "MI" 可能指心肌梗死或二尖瓣关闭不全），列出所有常见含义并按临床使用频率排序
4. 标注每个术语所属的学科领域

输出格式：
🔤 查询词：XXX
📋 类型：缩写展开 / 中文查英文 / ...
📖 结果：
  • 全称（英文）
  • 中文译名
  • 所属学科
  • （如有多种含义，逐条列出）
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

    # 合并结果
    parts = []
    if local_results:
        parts.extend(local_results)
        parts.append("\n---\n📡 **AI 补充查询结果：**\n")
    parts.append(api_result)

    return "\n".join(parts)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """从 PDF 文件中提取文字"""
    text = ""
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """从 Word 文件中提取文字"""
    doc = docx.Document(io.BytesIO(file_bytes))
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()


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
        st.markdown("### 📥 输入英文文献段落")
        st.caption("支持直接粘贴或逐句输入，建议每次不超过 2000 词")

        input_text = st.text_area(
            "英文原文",
            height=350,
            placeholder="在此粘贴英文医学文献段落...\n\n示例：\nPatients with ST-segment elevation myocardial infarction (STEMI) who underwent primary PCI within 12 hours of symptom onset showed significantly improved LVEF at 6-month follow-up compared to those receiving thrombolytic therapy.",
            label_visibility="collapsed",
        )

        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            translate_btn = st.button("🔄 翻译", use_container_width=True, type="primary")
        with col_btn2:
            target_lang = st.selectbox("目标语言", ["中文", "英文"], label_visibility="collapsed")

    with col2:
        st.markdown("### 📤 翻译结果")

        if translate_btn:
            if not api_key:
                st.error("⚠️ 请先在左侧边栏输入 DeepSeek API Key！")
                st.markdown("没有？→ [点此获取](https://platform.deepseek.com)")
            elif not input_text.strip():
                st.warning("⚠️ 请先输入要翻译的英文文献段落")
            else:
                with st.spinner("翻译中，正在匹配医学术语标准译名..."):
                    try:
                        client = get_client()
                        result = translate_text(client, input_text, target_lang)

                        # 扫描并显示识别到的缩写
                        abbreviations = find_abbreviations_in_text(input_text)
                        st.markdown("#### 📋 自动识别的医学缩写")
                        if abbreviations:
                            for abbr, full_en, full_cn in abbreviations:
                                st.markdown(
                                    f'<span class="abbr-tag">{abbr}</span> '
                                    f'→ {full_en}（{full_cn}）',
                                    unsafe_allow_html=True,
                                )
                        else:
                            st.caption("未识别到内置词库中的缩写")

                        # 显示翻译结果
                        st.markdown("#### 📝 翻译正文")
                        st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"翻译出错了：{str(e)}")
                        st.caption("常见原因：API Key 无效、网络不通、或 DeepSeek 余额不足")

    # 快捷示例
    with st.expander("💡 点击查看测试例句"):
        st.code("""Patients with ST-segment elevation myocardial infarction (STEMI) who underwent primary PCI within 12 hours of symptom onset showed significantly improved LVEF at 6-month follow-up compared to those receiving thrombolytic therapy. The incidence of major adverse cardiovascular events (MACE) was also lower in the PCI group (8.3% vs 15.7%, p<0.001).""", language=None)

# ============ Tab 2: 缩写互查 ============
with tab2:
    st.markdown("### 🔍 医学缩写 / 术语互查")
    st.caption("支持：英文缩写查全称 · 中文查英文缩写 · 全称查缩写")

    col_q1, col_q2 = st.columns([3, 1])

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
            st.error("⚠️ 请先在左侧边栏输入 DeepSeek API Key！")
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

    # 常用缩写速查
    with st.expander("📚 常用医学缩写速查表"):
        categories = {
            "心血管系统": ["STEMI", "NSTEMI", "PCI", "CABG", "ACS", "HF", "AF", "LVEF", "HTN", "CAD"],
            "呼吸系统": ["COPD", "ARDS", "PE", "OSA", "FEV1", "FVC"],
            "神经精神": ["CVA", "TIA", "AD", "PD", "MS", "EEG"],
            "影像检查": ["MRI", "CT", "PET", "SPECT", "US"],
            "内分泌代谢": ["DM", "T2DM", "HbA1c", "TSH", "PCOS", "DKA"],
            "肿瘤学": ["NSCLC", "CRC", "HCC", "OS", "PFS", "CR", "PR"],
            "临床研究": ["RCT", "OR", "RR", "HR", "CI", "ITT", "PP", "AE", "SAE"],
            "实验室检查": ["RBC", "WBC", "PLT", "Hb", "INR", "PT", "APTT"],
            "消化系统": ["GERD", "IBD", "UC", "CD", "IBS", "NAFLD"],
            "给药方式": ["q.d.", "b.i.d.", "t.i.d.", "p.r.n.", "NPO", "STAT"],
        }

        cols = st.columns(3)
        col_idx = 0
        for cat_name, abbrs in categories.items():
            with cols[col_idx % 3]:
                st.markdown(f"**{cat_name}**")
                for a in abbrs:
                    if a in MEDICAL_ABBREVIATIONS:
                        full_en, full_cn = MEDICAL_ABBREVIATIONS[a]
                        st.caption(f"• **{a}** — {full_cn}")
            col_idx += 1

# ============ Tab 3: 文件上传翻译 ============
with tab3:
    st.markdown("### 📄 上传文献文件，自动翻译")
    st.caption("支持 PDF、Word (.docx)、纯文本 (.txt) 文件")

    uploaded_file = st.file_uploader(
        "拖拽或点击上传文件",
        type=["pdf", "docx", "txt"],
        help="单文件不超过 10MB",
    )

    if uploaded_file:
        file_bytes = uploaded_file.read()

        # 根据文件类型提取文字
        file_type = uploaded_file.name.split(".")[-1].lower()
        with st.spinner(f"正在提取文件内容（{file_type.upper()}）..."):
            try:
                if file_type == "pdf":
                    extracted_text = extract_text_from_pdf(file_bytes)
                elif file_type == "docx":
                    extracted_text = extract_text_from_docx(file_bytes)
                else:  # txt
                    extracted_text = file_bytes.decode("utf-8", errors="replace")
            except Exception as e:
                st.error(f"提取文件内容失败：{str(e)}")
                extracted_text = ""

        if extracted_text:
            st.success(f"✅ 成功提取 {len(extracted_text)} 个字符")

            # 显示原文预览
            with st.expander("📄 原文预览"):
                preview_len = min(3000, len(extracted_text))
                st.text(extracted_text[:preview_len])
                if len(extracted_text) > preview_len:
                    st.caption(f"... (共 {len(extracted_text)} 字符，仅显示前 {preview_len} 字符)")

            # 缩写识别
            abbreviations = find_abbreviations_in_text(extracted_text)
            if abbreviations:
                st.markdown("#### 🔬 文献中识别的医学缩写")
                cols = st.columns(2)
                for i, (abbr, full_en, full_cn) in enumerate(abbreviations):
                    with cols[i % 2]:
                        st.markdown(f"• **{abbr}** → {full_en}（{full_cn}）")

            # 翻译按钮
            if st.button("🔄 翻译全文", type="primary"):
                if not api_key:
                    st.error("⚠️ 请先在左侧边栏输入 DeepSeek API Key！")
                else:
                    # 分段翻译（每段不超过2000字符，避免API限制）
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

                    st.info(f"文档较长，将分段翻译（共 {len(chunks)} 段）...")

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

                        status_text.text("翻译完成！")
                        combined = "\n\n---\n\n".join(full_result)

                        st.markdown("### 📝 翻译结果")
                        st.markdown(f'<div class="result-box">{combined}</div>', unsafe_allow_html=True)

                        # 下载按钮
                        st.download_button(
                            label="📥 下载翻译结果 (TXT)",
                            data=combined,
                            file_name=f"翻译_{uploaded_file.name.rsplit('.', 1)[0]}.txt",
                            mime="text/plain",
                        )

                    except Exception as e:
                        st.error(f"翻译失败：{str(e)}")

# ============================================================
# 页脚
# ============================================================
st.markdown("---")
st.caption(
    "🩺 医学文献智能翻译助手 | "
    "基于 DeepSeek 大模型 + 内置医学标准术语库 | "
    "翻译结果仅供学习参考，临床决策请以原文为准"
)
