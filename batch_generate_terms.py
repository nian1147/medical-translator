"""
批量生成医学术语 — 逐科调用 DeepSeek API，自动去重保存到 terms.csv
"""

import csv
import os
import sys
import time

# ============================================================
# 配置：把你的 API Key 填在这里
# ============================================================
API_KEY = "sk-85756af1062b458c8dd230c8abc8d91e"  # <--- 改这里！
API_BASE = "https://api.deepseek.com"

if API_KEY == "你的DeepSeek-API-Key":
    print("❌ 请先打开 batch_generate_terms.py，把 API_KEY 改成你的真实 Key！")
    sys.exit(1)

# ============================================================
# 学科列表 + 每科生成条数
# ============================================================
SUBJECTS = [
    "心血管内科", "呼吸内科", "消化内科", "神经内科", "内分泌科",
    "肾脏内科", "血液科", "肿瘤内科", "感染科", "急诊医学",
    "麻醉科", "妇产科", "儿科", "眼科", "耳鼻喉科",
    "皮肤科", "骨科", "泌尿外科", "精神病学", "影像医学",
    "病理学", "药理学", "免疫学", "遗传学", "分子生物学",
    "解剖学", "生理学", "生物化学", "微生物学", "公共卫生与流行病学",
]

TERMS_PER_SUBJECT = 50  # 每科要多少条（50条×30科=1500条）

CSV_FILE = "terms.csv"

# ============================================================
# 加载已有术语（用于去重）
# ============================================================
def load_existing_abbrs(filepath: str) -> set:
    """读取已有 CSV 中所有缩写（自动检测编码）"""
    existing = set()
    if os.path.exists(filepath):
        for encoding in ["utf-8-sig", "utf-8", "gbk", "gb2312", "gb18030"]:
            try:
                with open(filepath, "r", encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        abbr = (row.get("缩写") or "").strip()
                        if abbr:
                            existing.add(abbr.upper())
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
    return existing

# ============================================================
# 调用 DeepSeek 生成一个学科的术语
# ============================================================
def generate_terms_for_subject(subject: str, existing: set, count: int) -> list:
    """调用 DeepSeek 生成一个学科的术语表，排除已有缩写"""
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY, base_url=API_BASE)

    existing_list = ", ".join(sorted(existing)) if existing else "无"
    if len(existing_list) > 3000:
        existing_list = existing_list[:3000] + "..."  # 防止 prompt 过长

    prompt = f"""你是医学专家。请为「{subject}」这个学科生成 {count} 条最常见的英文医学缩写及其标准中文译名。

要求：
1. 每条包含：缩写,英文全称,中文译名,{subject}
2. 缩写必须是该学科论文和临床中最常出现的
3. 中文译名使用中国《医学主题词表》标准译名
4. 每个缩写只给一条记录

已存在的缩写（请不要重复这些）：{existing_list}

请直接输出 CSV 数据，每行一条，用逗号分隔，第一条从数据开始（不要表头），格式如：
STEMI,ST-segment Elevation Myocardial Infarction,ST段抬高型心肌梗死,{subject}

只输出数据行，不要任何解释文字。"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4096,
    )

    text = response.choices[0].message.content.strip()

    new_terms = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("```") or line.startswith("缩写"):
            continue
        parts = [p.strip() for p in line.split(",", 3)]
        if len(parts) >= 4:
            abbr = parts[0]
            if abbr.upper() not in existing:
                new_terms.append(parts)
                existing.add(abbr.upper())

    return new_terms

# ============================================================
# 主流程
# ============================================================
def main():
    existing_abbrs = load_existing_abbrs(CSV_FILE)
    print(f"📚 已有 {len(existing_abbrs)} 个术语")

    all_new = []
    for i, subject in enumerate(SUBJECTS, 1):
        print(f"\n[{i}/{len(SUBJECTS)}] 正在生成 {subject} 术语...", end=" ", flush=True)
        try:
            new_terms = generate_terms_for_subject(subject, existing_abbrs, TERMS_PER_SUBJECT)
            all_new.extend(new_terms)
            print(f"✅ 新增 {len(new_terms)} 条")
        except Exception as e:
            print(f"❌ 失败：{e}")

        time.sleep(1)  # 避免 API 限速

    # 追加写入 CSV
    if all_new:
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, "a", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            for row in all_new:
                writer.writerow(row)

        print(f"\n🎉 完成！共新增 {len(all_new)} 个术语，已追加到 {CSV_FILE}")
    else:
        print("\n⚠️ 没有生成新术语")

    # 统计
    final_count = len(load_existing_abbrs(CSV_FILE))
    print(f"📊 术语库总量：{final_count} 条")

if __name__ == "__main__":
    main()
