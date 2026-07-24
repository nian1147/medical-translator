"""
批量生成医学术语 v2 — 细分子专题，每专题独立生成，最大化词汇覆盖
"""

import csv
import os
import sys
import time

# ============================================================
# 配置
# ============================================================
API_KEY = "sk-85756af1062b458c8dd230c8abc8d91e"
API_BASE = "https://api.deepseek.com"

CSV_FILE = "terms.csv"
TERMS_PER_TOPIC = 30  # 每个子专题生成条数，不需要太多，关键是专题要细

# ============================================================
# 细分子专题列表（越细，词条越不重复）
# ============================================================
SUB_TOPICS = [
    # 心血管内科
    "冠心病与心肌梗死", "心力衰竭与心肌病", "心律失常与电生理", "高血压病",
    "心脏瓣膜病", "先天性心脏病", "心包疾病", "外周血管疾病",
    "心脏影像学（超声、CT、MRI）", "心脏介入治疗",
    # 呼吸内科
    "慢性阻塞性肺疾病", "支气管哮喘", "肺部感染与肺炎", "肺结核与非结核分枝杆菌",
    "间质性肺疾病", "肺栓塞与肺血管病", "呼吸衰竭与机械通气", "肺癌筛查与诊断",
    "睡眠呼吸障碍", "胸腔积液与气胸",
    # 消化内科
    "胃食管反流与食管疾病", "消化性溃疡与胃炎", "炎症性肠病（克罗恩/溃结）",
    "功能性胃肠病", "肝脏疾病（肝炎、肝硬化）", "胰腺疾病", "胆道疾病",
    "消化道肿瘤", "消化道内镜诊断与治疗", "肠道菌群与消化健康",
    # 神经内科
    "脑血管疾病（卒中）", "癫痫", "帕金森病与运动障碍", "多发性硬化与脱髓鞘",
    "阿尔茨海默病与痴呆", "头痛与偏头痛", "周围神经病", "肌肉疾病（肌无力等）",
    "中枢神经系统感染", "睡眠障碍",
    # 内分泌科
    "糖尿病及其并发症", "甲状腺疾病", "肾上腺疾病", "垂体疾病",
    "性腺疾病", "钙磷代谢与骨质疏松", "肥胖与代谢综合征", "内分泌高血压",
    "神经内分泌肿瘤", "脂代谢异常",
    # 肾脏内科
    "急性肾损伤", "慢性肾脏病", "肾小球疾病（肾炎/肾病综合征）", "糖尿病肾病",
    "高血压肾损害", "肾小管间质疾病", "透析与血液净化", "肾移植",
    "水电解质酸碱平衡", "遗传性肾病",
    # 血液科
    "贫血", "白血病（急淋/急髓/慢粒）", "淋巴瘤（霍奇金/非霍奇金）", "多发性骨髓瘤",
    "骨髓增生异常综合征", "骨髓增殖性肿瘤", "出凝血疾病", "输血医学",
    "造血干细胞移植", "噬血细胞综合征",
    # 肿瘤内科
    "肺癌", "乳腺癌", "结直肠癌", "胃癌与食管癌", "肝癌与胆管癌",
    "胰腺癌", "前列腺癌", "卵巢癌与宫颈癌", "黑色素瘤", "靶向治疗与免疫治疗",
    # 感染科
    "细菌感染与抗生素", "病毒感染（流感/新冠/艾滋）", "真菌感染", "寄生虫病",
    "脓毒症与感染性休克", "院内感染与多重耐药菌", "疫苗与免疫预防",
    "发热待查", "人畜共患病", "新发传染病",
    # 急诊医学
    "心肺复苏", "急性中毒", "多发伤与创伤急救", "急性腹痛",
    "急性胸痛", "急性呼吸困难", "过敏性休克", "热射病与低体温",
    "急诊气道管理", "灾难医学与院前急救",
    # 妇产科
    "正常妊娠与产前保健", "高危妊娠", "妊娠期合并症（糖尿病/高血压）",
    "分娩与产程管理", "产后出血与产科急诊", "妇科肿瘤（宫颈/内膜/卵巢）",
    "月经失调与内分泌", "子宫内膜异位症", "盆底功能障碍", "辅助生殖技术",
    # 儿科
    "新生儿疾病", "儿童呼吸系统疾病", "儿童消化系统疾病", "儿童感染性疾病",
    "儿童生长发育与营养", "儿童神经系统疾病", "先天性遗传代谢病", "儿童免疫与过敏",
    "儿童心血管疾病", "儿童急救与重症",
    # 骨科
    "骨折与创伤骨科", "脊柱外科（椎间盘/椎管狭窄）", "关节外科（髋/膝关节置换）",
    "运动医学与关节镜", "骨肿瘤", "手外科与显微外科", "足踝外科",
    "骨质疏松性骨折", "骨科康复", "小儿骨科",
    # 其他重要领域
    "药理学总论与药代动力学", "药物不良反应与警戒", "抗生素合理用药",
    "免疫学基础与自身免疫", "移植免疫与免疫缺陷", "分子生物学技术（PCR/测序/CRISPR）",
    "遗传病与基因诊断", "病理学诊断技术", "影像医学（CT/MRI/PET）",
    "麻醉药物与麻醉管理", "疼痛管理", "重症监护（ICU）",
    "临床流行病学", "循证医学与Meta分析", "医学统计学方法",
    "生物标志物与精准医学", "临床营养支持", "老年医学与肌少症",
]

# ============================================================
# 加载已有术语
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
# 调用 DeepSeek
# ============================================================
def generate_terms_for_topic(topic: str, existing: set, count: int) -> list:
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY, base_url=API_BASE)

    existing_sample = ", ".join(sorted(existing)[-500:]) if existing else "无"

    prompt = f"""你是医学专家。请为专题「{topic}」生成 {count} 条最常见的英文医学缩写及其标准中文译名。

要求：
1. 格式：缩写,英文全称,中文译名,{topic}
2. 缩写必须是该专题论文和临床中最常出现的
3. 中文译名使用中国《医学主题词表》标准译名
4. 只给新缩写，不要重复以下已有缩写（部分列表）：{existing_sample}
5. 每个缩写一行

直接输出CSV数据（不要表头），不要任何解释文字。"""

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
        if not line or line.startswith("```"):
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
    print(f"🔬 {len(SUB_TOPICS)} 个子专题，每专题最多 {TERMS_PER_TOPIC} 条\n")

    total_new = 0
    for i, topic in enumerate(SUB_TOPICS, 1):
        print(f"[{i}/{len(SUB_TOPICS)}] {topic} ...", end=" ", flush=True)
        try:
            new_terms = generate_terms_for_topic(topic, existing_abbrs, TERMS_PER_TOPIC)
            total_new += len(new_terms)

            # 即时追加写入
            if new_terms:
                with open(CSV_FILE, "a", encoding="utf-8-sig", newline="") as f:
                    writer = csv.writer(f)
                    for row in new_terms:
                        writer.writerow(row)

            print(f"+{len(new_terms)} 条")
        except Exception as e:
            print(f"❌ {e}")

        time.sleep(1.5)

    final = len(load_existing_abbrs(CSV_FILE))
    print(f"\n─────────────────────")
    print(f"🎉 完成！新增 {total_new} 条，术语库总量：{final} 条")

if __name__ == "__main__":
    main()
