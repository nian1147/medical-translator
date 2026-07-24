"""
一次性写入全学科医学术语库 — 覆盖所有医学领域的缩写和文献常用术语
直接写入 terms.csv 末尾，自动去重
"""
import csv
import os

CSV_FILE = r"C:\Users\年年\medical-translator\terms.csv"

# ============================================================
# 全学科医学缩写 + 文献通用术语
# ============================================================
TERMS = """
缩写,英文全称,中文译名,学科
ABCD2,Age Blood Pressure Clinical features Duration of symptoms Diabetes,ABCD2评分（短暂性脑缺血发作风险评分）,神经
ABCD3-I,ABCD2 plus Diffusion-weighted imaging and Ipsilateral carotid stenosis,ABCD3-I评分,神经
ABG,Arterial Blood Gas,动脉血气分析,检验
ABI,Ankle-Brachial Index,踝肱指数,心血管
ABPA,Allergic Bronchopulmonary Aspergillosis,变应性支气管肺曲霉病,呼吸
ABVD,Doxorubicin Bleomycin Vinblastine Dacarbazine,ABVD化疗方案（霍奇金淋巴瘤）,肿瘤
ACA,Anterior Cerebral Artery,大脑前动脉,神经
ACD,Anemia of Chronic Disease,慢性病贫血,血液
ACE,Angiotensin-Converting Enzyme,血管紧张素转化酶,心血管
ACG,American College of Gastroenterology,美国胃肠病学会,消化
ACPA,Anti-Citrullinated Protein Antibody,抗瓜氨酸蛋白抗体,风湿免疫
ACS,Acute Coronary Syndrome,急性冠脉综合征,心血管
ACTH,Adrenocorticotropic Hormone,促肾上腺皮质激素,内分泌
AD,Alzheimer's Disease,阿尔茨海默病,神经
ADA,Adenosine Deaminase,腺苷脱氨酶,检验
ADC,Apparent Diffusion Coefficient,表观扩散系数,影像
ADEM,Acute Disseminated Encephalomyelitis,急性播散性脑脊髓炎,神经
ADH,Antidiuretic Hormone,抗利尿激素,内分泌
ADHD,Attention-Deficit Hyperactivity Disorder,注意缺陷多动障碍,精神
ADL,Activities of Daily Living,日常生活活动能力,康复
ADPKD,Autosomal Dominant Polycystic Kidney Disease,常染色体显性多囊肾病,肾病
ADR,Adverse Drug Reaction,药物不良反应,药理
AE,Adverse Event,不良事件,临床研究
AED,Antiepileptic Drug,抗癫痫药物,神经
AF,Atrial Fibrillation,心房颤动,心血管
AFB,Acid-Fast Bacillus,抗酸杆菌,感染
AFP,Alpha-Fetoprotein,甲胎蛋白,检验
AG,Anion Gap,阴离子间隙,检验
AGA,American Gastroenterological Association,美国胃肠病协会,消化
AHA,American Heart Association,美国心脏协会,心血管
AICD,Activation-Induced Cell Death,活化诱导的细胞死亡,免疫
AIDP,Acute Inflammatory Demyelinating Polyradiculoneuropathy,急性炎症性脱髓鞘性多发性神经根神经病,神经
AIDS,Acquired Immunodeficiency Syndrome,获得性免疫缺陷综合征,感染
AIHA,Autoimmune Hemolytic Anemia,自身免疫性溶血性贫血,血液
AIH,Autoimmune Hepatitis,自身免疫性肝炎,消化
AKI,Acute Kidney Injury,急性肾损伤,肾病
AKT,Protein Kinase B,蛋白激酶B,分子生物学
ALARA,As Low As Reasonably Achievable,合理最低剂量原则,影像
ALB,Albumin,白蛋白,检验
ALCAPA,Anomalous Left Coronary Artery from the Pulmonary Artery,左冠状动脉异常起源于肺动脉,心血管
ALF,Acute Liver Failure,急性肝衰竭,消化
ALI,Acute Lung Injury,急性肺损伤,呼吸
ALK,Anaplastic Lymphoma Kinase,间变性淋巴瘤激酶,肿瘤
ALL,Acute Lymphoblastic Leukemia,急性淋巴细胞白血病,血液
ALP,Alkaline Phosphatase,碱性磷酸酶,检验
ALS,Amyotrophic Lateral Sclerosis,肌萎缩侧索硬化,神经
ALT,Alanine Aminotransferase,丙氨酸氨基转移酶,检验
AMA,Anti-Mitochondrial Antibody,抗线粒体抗体,免疫
AMI,Acute Myocardial Infarction,急性心肌梗死,心血管
AML,Acute Myeloid Leukemia,急性髓系白血病,血液
AMPA,Alpha-Amino-3-hydroxy-5-Methyl-4-isoxazolePropionic Acid,α-氨基-3-羟基-5-甲基-4-异恶唑丙酸,神经
AMR,Antimicrobial Resistance,抗微生物药物耐药性,感染
AMY,Amylase,淀粉酶,检验
ANA,Antinuclear Antibody,抗核抗体,风湿免疫
ANCA,Anti-Neutrophil Cytoplasmic Antibody,抗中性粒细胞胞质抗体,风湿免疫
ANP,Atrial Natriuretic Peptide,心房利钠肽,心血管
AP,Anteroposterior,前后位,影像
APACHE,Acute Physiology and Chronic Health Evaluation,急性生理与慢性健康状况评分,重症
APC,Adenomatous Polyposis Coli,腺瘤性结肠息肉病,消化
APL,Acute Promyelocytic Leukemia,急性早幼粒细胞白血病,血液
APLS,Antiphospholipid Syndrome,抗磷脂综合征,风湿免疫
APP,Amyloid Precursor Protein,淀粉样前体蛋白,神经
aPTT,Activated Partial Thromboplastin Time,活化部分凝血活酶时间,检验
APUD,Amine Precursor Uptake and Decarboxylation,胺前体摄取脱羧系统,生理
AR,Androgen Receptor,雄激素受体,内分泌
ARB,Angiotensin Receptor Blocker,血管紧张素受体阻滞剂,心血管
ARF,Acute Renal Failure,急性肾功能衰竭,肾病
ARDS,Acute Respiratory Distress Syndrome,急性呼吸窘迫综合征,呼吸
ARMD,Age-Related Macular Degeneration,年龄相关性黄斑变性,眼科
ARVC,Arrhythmogenic Right Ventricular Cardiomyopathy,致心律失常性右室心肌病,心血管
AS,Ankylosing Spondylitis,强直性脊柱炎,风湿免疫
AS,Atrial Septal,房间隔,心血管
ASA,American Society of Anesthesiologists,美国麻醉医师学会,麻醉
ASC,Apoptosis-Associated Speck-like protein containing CARD,凋亡相关斑点样蛋白,免疫
ASCA,Anti-Saccharomyces Cerevisiae Antibody,抗酿酒酵母抗体,消化
ASD,Atrial Septal Defect,房间隔缺损,心血管
ASCO,American Society of Clinical Oncology,美国临床肿瘤学会,肿瘤
ASH,American Society of Hematology,美国血液学会,血液
ASIA,American Spinal Injury Association,美国脊髓损伤协会,骨科
ASO,Anti-Streptolysin O,抗链球菌溶血素O,检验
ASO,Allele-Specific Oligonucleotide,等位基因特异性寡核苷酸,遗传
ASS,Acetylsalicylic Acid,乙酰水杨酸（阿司匹林）,药理
AST,Aspartate Aminotransferase,天冬氨酸氨基转移酶,检验
AT1,Angiotensin II Type 1 Receptor,血管紧张素II 1型受体,心血管
ATG,Anti-Thymocyte Globulin,抗胸腺细胞球蛋白,免疫
ATLS,Advanced Trauma Life Support,高级创伤生命支持,急诊
ATN,Acute Tubular Necrosis,急性肾小管坏死,肾病
ATP,Adenosine Triphosphate,三磷酸腺苷,生化
ATRA,All-Trans Retinoic Acid,全反式维甲酸,肿瘤
ATS,American Thoracic Society,美国胸科学会,呼吸
AUB,Abnormal Uterine Bleeding,异常子宫出血,妇产科
AUC,Area Under the Curve,曲线下面积,临床研究
AV,Atrioventricular,房室的,心血管
AVF,Arteriovenous Fistula,动静脉瘘,肾病
AVM,Arteriovenous Malformation,动静脉畸形,神经
AVNRT,Atrioventricular Nodal Reentrant Tachycardia,房室结折返性心动过速,心血管
AVRT,Atrioventricular Reentrant Tachycardia,房室折返性心动过速,心血管
AWS,Alcohol Withdrawal Syndrome,酒精戒断综合征,精神
AZA,Azathioprine,硫唑嘌呤,免疫
BAC,Bacterial Artificial Chromosome,细菌人工染色体,分子生物学
BAEP,Brainstem Auditory Evoked Potential,脑干听觉诱发电位,神经
BAL,Bronchoalveolar Lavage,支气管肺泡灌洗,呼吸
BALF,Bronchoalveolar Lavage Fluid,支气管肺泡灌洗液,呼吸
BARR,Blood-Brain Barrier,血脑屏障,神经
BCC,Basal Cell Carcinoma,基底细胞癌,皮肤
BCG,Bacillus Calmette-Guerin,卡介苗,免疫
BCL-2,B-cell Lymphoma 2,B细胞淋巴瘤2,肿瘤
BCR,B Cell Receptor,B细胞受体,免疫
BCR-ABL,Breakpoint Cluster Region-Abelson,BCR-ABL融合基因,肿瘤
BE,Base Excess,碱剩余,检验
BEAM,BEAM chemotherapy protocol,BEAM化疗方案,肿瘤
BET,Benign Essential Tremor,良性特发性震颤,神经
BHS,Beta-Hemolytic Streptococcus,β溶血性链球菌,感染
BIPAP,Bilevel Positive Airway Pressure,双水平气道正压通气,呼吸
BK,BK Polyomavirus,BK多瘤病毒,感染
BLS,Basic Life Support,基础生命支持,急诊
BMI,Body Mass Index,体重指数,公卫
BMP,Bone Morphogenetic Protein,骨形态发生蛋白,骨科
BMR,Basal Metabolic Rate,基础代谢率,生理
BMS,Bare-Metal Stent,裸金属支架,心血管
BNCT,Boron Neutron Capture Therapy,硼中子俘获治疗,肿瘤
BNP,Brain Natriuretic Peptide,脑钠肽,心血管
BOLD,Blood Oxygenation Level Dependent,血氧水平依赖,影像
BP,Blood Pressure,血压,公卫
BPAD,Bipolar Affective Disorder,双相情感障碍,精神
BPH,Benign Prostatic Hyperplasia,良性前列腺增生,泌尿
BRAF,v-Raf murine sarcoma viral oncogene homolog B,BRAF原癌基因,肿瘤
BRAT,Benign Recurrent Aphtous Stomatitis,良性复发性阿弗他口炎,消化
BRCA,Breast Cancer susceptibility gene,乳腺癌易感基因,肿瘤
BSA,Body Surface Area,体表面积,临床
BSE,Bovine Spongiform Encephalopathy,牛海绵状脑病,神经
BUN,Blood Urea Nitrogen,血尿素氮,检验
BWS,Beckwith-Wiedemann Syndrome,Beckwith-Wiedemann综合征,遗传
C-peptide,Connecting Peptide,C肽,内分泌
CA,Cancer Antigen,癌抗原,肿瘤
CA-125,Cancer Antigen 125,癌抗原125,肿瘤
CA-15-3,Cancer Antigen 15-3,癌抗原15-3,肿瘤
CA-19-9,Carbohydrate Antigen 19-9,糖类抗原19-9,肿瘤
CAA,Cerebral Amyloid Angiopathy,脑淀粉样血管病,神经
CABG,Coronary Artery Bypass Grafting,冠状动脉旁路移植术,心血管
CAD,Coronary Artery Disease,冠状动脉疾病,心血管
CADASIL,Cerebral Autosomal Dominant Arteriopathy with Subcortical Infarcts and Leukoencephalopathy,伴皮质下梗死和白质脑病的常染色体显性遗传性脑动脉病,神经
CAG,Coronary Angiography,冠状动脉造影,心血管
CAM,Confusion Assessment Method,谵妄评估方法,重症
CAMP,Cyclic Adenosine Monophosphate,环磷酸腺苷,生化
CAP,Community-Acquired Pneumonia,社区获得性肺炎,呼吸
CART,Chimeric Antigen Receptor T-cell,嵌合抗原受体T细胞,肿瘤
CBC,Complete Blood Count,全血细胞计数,检验
CBD,Common Bile Duct,胆总管,消化
CBF,Cerebral Blood Flow,脑血流量,神经
CBG,Corticosteroid-Binding Globulin,皮质类固醇结合球蛋白,内分泌
CBT,Cognitive Behavioral Therapy,认知行为疗法,精神
CCB,Calcium Channel Blocker,钙通道阻滞剂,心血管
CCC,Cholangiocarcinoma,胆管癌,消化
CCF,Congestive Cardiac Failure,充血性心力衰竭,心血管
CCK,Cholecystokinin,胆囊收缩素,消化
CCN,Community Care Network,社区护理网络,公卫
CCP,Cyclic Citrullinated Peptide,环瓜氨酸肽,风湿免疫
CCR,Chemokine Receptor,趋化因子受体,免疫
CCS,Canadian Cardiovascular Society,加拿大心血管学会,心血管
CCU,Coronary Care Unit,冠心病监护病房,心血管
CD,Cluster of Differentiation,分化簇,免疫
CD,Crohn's Disease,克罗恩病,消化
CDAI,Crohn's Disease Activity Index,克罗恩病活动指数,消化
CDC,Centers for Disease Control and Prevention,疾病控制与预防中心,公卫
CDH,Congenital Diaphragmatic Hernia,先天性膈疝,儿科
CDK,Cyclin-Dependent Kinase,细胞周期蛋白依赖性激酶,肿瘤
CDP,Cytidine Diphosphate,胞苷二磷酸,生化
CEA,Carcinoembryonic Antigen,癌胚抗原,检验
CEAP,Clinical Etiology Anatomy Pathophysiology,CEAP分级（慢性静脉疾病）,血管外科
CED,Clinical Endpoint Determination,临床终点判定,临床研究
CEM,Contrast-Enhanced Mammography,对比增强乳腺摄影,影像
CEP,Congenital Erythropoietic Porphyria,先天性红细胞生成性卟啉病,血液
CETP,Cholesteryl Ester Transfer Protein,胆固醇酯转运蛋白,检验
CF,Cystic Fibrosis,囊性纤维化,呼吸
CFS,Chronic Fatigue Syndrome,慢性疲劳综合征,全科
CFU,Colony-Forming Unit,菌落形成单位,微生物
CG,Chronic Glomerulonephritis,慢性肾小球肾炎,肾病
CGA,Comprehensive Geriatric Assessment,老年综合评估,老年医学
CGB,Chorionic Gonadotropin Beta,绒毛膜促性腺激素β亚基,妇产科
CGH,Comparative Genomic Hybridization,比较基因组杂交,遗传
cGMP,Cyclic Guanosine Monophosphate,环磷酸鸟苷,生化
CH50,50% Hemolytic Complement,50%溶血补体,免疫
CHAD,Coronary Heart Disease,冠心病,心血管
CHADS2,CHF Hypertension Age Diabetes Stroke,CHADS2评分（房颤卒中风险）,心血管
CHAOS,Congenital High Airway Obstruction Syndrome,先天性高位气道梗阻综合征,儿科
CHD,Congenital Heart Disease,先天性心脏病,心血管
CHE,Cholinesterase,胆碱酯酶,检验
CHF,Congestive Heart Failure,充血性心力衰竭,心血管
CHOP,Cyclophosphamide Hydroxydaunorubicin Oncovin Prednisone,CHOP化疗方案,肿瘤
CI,Cardiac Index,心脏指数,重症
CI,Confidence Interval,置信区间,统计
CIC,Clean Intermittent Catheterization,清洁间歇导尿,泌尿
CIDP,Chronic Inflammatory Demyelinating Polyneuropathy,慢性炎症性脱髓鞘性多发性神经病,神经
CIN,Cervical Intraepithelial Neoplasia,宫颈上皮内瘤变,妇产科
CIP,Critical Illness Polyneuropathy,危重病多发性神经病,重症
CIS,Carcinoma In Situ,原位癌,肿瘤
CJD,Creutzfeldt-Jakob Disease,克雅病,神经
CK,Creatine Kinase,肌酸激酶,检验
CK-MB,Creatine Kinase Myocardial Band,肌酸激酶同工酶,检验
CKD,Chronic Kidney Disease,慢性肾脏病,肾病
CKRT,Continuous Kidney Replacement Therapy,连续性肾脏替代治疗,重症
CLABSI,Central Line-Associated Bloodstream Infection,中心静脉导管相关血流感染,感染
CLL,Chronic Lymphocytic Leukemia,慢性淋巴细胞白血病,血液
CMC,Carpometacarpal,腕掌关节,骨科
CME,Continuing Medical Education,继续医学教育,教育
CMG,Cystometrogram,膀胱压力容积测定,泌尿
CML,Chronic Myeloid Leukemia,慢性髓系白血病,血液
CMML,Chronic Myelomonocytic Leukemia,慢性粒单核细胞白血病,血液
CMR,Cardiac Magnetic Resonance,心脏磁共振,影像
CMV,Cytomegalovirus,巨细胞病毒,感染
CNS,Central Nervous System,中枢神经系统,神经
CO,Cardiac Output,心输出量,生理
COMT,Catechol-O-Methyltransferase,儿茶酚氧位甲基转移酶,遗传
COP,Cryptogenic Organizing Pneumonia,隐源性机化性肺炎,呼吸
COPD,Chronic Obstructive Pulmonary Disease,慢性阻塞性肺疾病,呼吸
COX,Cyclooxygenase,环氧合酶,药理
CP,Cerebral Palsy,脑性瘫痪,儿科
CP,Chest Pain,胸痛,症状
CPA,Cardiopulmonary Arrest,心脏骤停,急诊
CPAP,Continuous Positive Airway Pressure,持续气道正压通气,呼吸
CPC,Clinical Pathological Conference,临床病理讨论会,教育
CPET,Cardiopulmonary Exercise Testing,心肺运动试验,心血管
CPK,Creatine Phosphokinase,肌酸磷酸激酶,检验
CPOE,Computerized Physician Order Entry,计算机化医嘱录入,信息
CPP,Cerebral Perfusion Pressure,脑灌注压,重症
CPR,Cardiopulmonary Resuscitation,心肺复苏,急诊
Cr,Creatinine,肌酐,检验
CR,Complete Response,完全缓解,肿瘤
CRAB,Cytogenetic Risk Assessment in B-ALL,B-ALL细胞遗传学风险评估,血液
CRC,Colorectal Cancer,结直肠癌,肿瘤
CREST,Calcinosis Raynaud Esophageal dysmotility Sclerodactyly Telangiectasia,CREST综合征,风湿免疫
CRH,Corticotropin-Releasing Hormone,促肾上腺皮质激素释放激素,内分泌
CRP,C-Reactive Protein,C反应蛋白,检验
CRPS,Complex Regional Pain Syndrome,复杂性局部疼痛综合征,疼痛
CRRT,Continuous Renal Replacement Therapy,连续性肾脏替代治疗,重症
CRT,Cardiac Resynchronization Therapy,心脏再同步化治疗,心血管
CS,Cesarean Section,剖宫产,妇产科
CS,Cushing Syndrome,库欣综合征,内分泌
CSA,Central Sleep Apnea,中枢性睡眠呼吸暂停,呼吸
CSF,Cerebrospinal Fluid,脑脊液,神经
CSII,Continuous Subcutaneous Insulin Infusion,持续皮下胰岛素输注,内分泌
CSOM,Chronic Suppurative Otitis Media,慢性化脓性中耳炎,耳鼻喉
CSP,Cerebrospinal Fluid,脑脊液,神经
CSS,Churg-Strauss Syndrome,Churg-Strauss综合征,风湿免疫
CT,Computed Tomography,计算机断层扫描,影像
CTA,CT Angiography,CT血管成像,影像
CTD,Connective Tissue Disease,结缔组织病,风湿免疫
CTEPH,Chronic Thromboembolic Pulmonary Hypertension,慢性血栓栓塞性肺动脉高压,呼吸
CTLA-4,Cytotoxic T-Lymphocyte-Associated Protein 4,细胞毒性T淋巴细胞相关蛋白4,免疫
cTnI,Cardiac Troponin I,心肌肌钙蛋白I,检验
cTnT,Cardiac Troponin T,心肌肌钙蛋白T,检验
CTPA,CT Pulmonary Angiography,CT肺动脉造影,影像
CTS,Carpal Tunnel Syndrome,腕管综合征,骨科
CUP,Cancer of Unknown Primary,原发灶不明癌,肿瘤
CVA,Cerebrovascular Accident,脑血管意外,神经
CVC,Central Venous Catheter,中心静脉导管,护理
CVID,Common Variable Immunodeficiency,普通变异型免疫缺陷,免疫
CVP,Central Venous Pressure,中心静脉压,重症
CXR,Chest X-Ray,胸部X线片,影像
CY,Cyanosis,发绀,症状
CYC,Cyclophosphamide,环磷酰胺,药理
CYP,Cytochrome P450,细胞色素P450,药理
CysC,Cystatin C,胱抑素C,检验
DAPT,Dual Antiplatelet Therapy,双联抗血小板治疗,心血管
DAT,Direct Antiglobulin Test,直接抗人球蛋白试验,血液
DBP,Diastolic Blood Pressure,舒张压,心血管
DC,Direct Current,直流电,生理
DCBE,Double Contrast Barium Enema,双对比钡灌肠,影像
DCM,Dilated Cardiomyopathy,扩张型心肌病,心血管
DCS,Damage Control Surgery,损伤控制外科,外科
DCT,Distal Convoluted Tubule,远曲小管,生理
DDx,Differential Diagnosis,鉴别诊断,临床
DES,Drug-Eluting Stent,药物洗脱支架,心血管
DFSP,Dermatofibrosarcoma Protuberans,隆突性皮肤纤维肉瘤,皮肤
DEXA,Dual-Energy X-ray Absorptiometry,双能X线吸收法,影像
DFS,Disease-Free Survival,无病生存期,肿瘤
DGI,Disseminated Gonococcal Infection,播散性淋球菌感染,感染
DGP,Deamidated Gliadin Peptide,脱酰胺基麦胶蛋白肽,消化
DHEA,Dehydroepiandrosterone,脱氢表雄酮,内分泌
DHP,District Health Plan,地区卫生计划,公卫
DHR,Delayed Hypersensitivity Reaction,迟发性超敏反应,免疫
DI,Diabetes Insipidus,尿崩症,内分泌
DIC,Disseminated Intravascular Coagulation,弥散性血管内凝血,血液
DILI,Drug-Induced Liver Injury,药物性肝损伤,消化
DIP,Distal Interphalangeal,远端指间关节,骨科
DKA,Diabetic Ketoacidosis,糖尿病酮症酸中毒,内分泌
DLBCL,Diffuse Large B-Cell Lymphoma,弥漫大B细胞淋巴瘤,血液
DLCO,Diffusing capacity of Lung for Carbon monoxide,肺一氧化碳弥散量,呼吸
DM,Diabetes Mellitus,糖尿病,内分泌
DMD,Duchenne Muscular Dystrophy,Duchenne型肌营养不良,神经
DMSA,Dimercaptosuccinic Acid,二巯基丁二酸,影像
DNA,Deoxyribonucleic Acid,脱氧核糖核酸,分子生物学
DNAR,Do Not Attempt Resuscitation,不尝试心肺复苏,伦理
DNR,Do Not Resuscitate,不进行心肺复苏,伦理
DOAC,Direct Oral Anticoagulant,直接口服抗凝药,心血管
DOE,Dyspnea on Exertion,劳力性呼吸困难,症状
DPP-4,Dipeptidyl Peptidase-4,二肽基肽酶-4,内分泌
DR,Diabetic Retinopathy,糖尿病视网膜病变,眼科
DRESS,Drug Reaction with Eosinophilia and Systemic Symptoms,伴嗜酸性粒细胞增多和全身症状的药物反应,皮肤
DSA,Digital Subtraction Angiography,数字减影血管造影,影像
DSE,Dobutamine Stress Echocardiography,多巴酚丁胺负荷超声心动图,心血管
DSM,Diagnostic and Statistical Manual of Mental Disorders,精神疾病诊断与统计手册,精神
DT,Delirium Tremens,震颤谵妄,精神
DTC,Direct-to-Consumer,直接面向消费者,伦理
DTP,Deep Tendon Reflex,深腱反射,神经
DU,Duodenal Ulcer,十二指肠溃疡,消化
DUB,Dysfunctional Uterine Bleeding,功能失调性子宫出血,妇产科
DVT,Deep Vein Thrombosis,深静脉血栓,血管外科
DWI,Diffusion-Weighted Imaging,弥散加权成像,影像
Dx,Diagnosis,诊断,临床
EBL,Estimated Blood Loss,估计失血量,外科
EBM,Evidence-Based Medicine,循证医学,临床
EBNA,EBV Nuclear Antigen,EB病毒核抗原,感染
EBUS,Endobronchial Ultrasound,支气管内超声,呼吸
EBV,Epstein-Barr Virus,EB病毒,感染
EC,Enteric-Coated,肠溶包衣,药理
ECC,Extracorporeal Circulation,体外循环,麻醉
ECD,Early Coronary Disease,早期冠心病,心血管
ECE,Extracapsular Extension,包膜外侵犯,肿瘤
ECF,Extracellular Fluid,细胞外液,生理
ECG,Electrocardiogram,心电图,心血管
ECL,Enterochromaffin-Like,肠嗜铬细胞样,消化
ECMO,Extracorporeal Membrane Oxygenation,体外膜肺氧合,重症
ECS,Electrocerebral Silence,脑电静息,神经
ECT,Electroconvulsive Therapy,电休克治疗,精神
ECV,External Cephalic Version,外侧转术,妇产科
ED,Emergency Department,急诊科,急诊
EDC,Estimated Date of Confinement,预产期,妇产科
EDD,Estimated Date of Delivery,预产期,妇产科
EDH,Extradural Hematoma,硬膜外血肿,神经外科
EDTA,Ethylenediaminetetraacetic Acid,乙二胺四乙酸,检验
EEG,Electroencephalography,脑电图,神经
EENT,Eye Ear Nose Throat,眼耳鼻喉,耳鼻喉
EF,Ejection Fraction,射血分数,心血管
EFA,Essential Fatty Acid,必需脂肪酸,营养
EGC,Early Gastric Cancer,早期胃癌,消化
EGD,Esophagogastroduodenoscopy,食管胃十二指肠镜检查,消化
EGFR,Epidermal Growth Factor Receptor,表皮生长因子受体,肿瘤
eGFR,estimated Glomerular Filtration Rate,估算肾小球滤过率,检验
EH,Essential Hypertension,原发性高血压,心血管
EIA,Enzyme Immunoassay,酶免疫分析,检验
EKG,Electrocardiogram,心电图,心血管
ELISA,Enzyme-Linked Immunosorbent Assay,酶联免疫吸附试验,检验
EM,Erythema Multiforme,多形红斑,皮肤
EMA,Epithelial Membrane Antigen,上皮膜抗原,病理
EMB,Endomyocardial Biopsy,心内膜心肌活检,心血管
EMG,Electromyography,肌电图,神经
EMLA,Eutectic Mixture of Local Anesthetics,局部麻醉药低共熔混合物,麻醉
EMS,Emergency Medical Services,紧急医疗服务,急诊
EMT,Epithelial-Mesenchymal Transition,上皮间质转化,肿瘤
EN,Enteral Nutrition,肠内营养,营养
ENBD,Endoscopic Nasobiliary Drainage,内镜鼻胆管引流,消化
ENT,Ear Nose Throat,耳鼻喉,耳鼻喉
EORTC,European Organisation for Research and Treatment of Cancer,欧洲癌症研究与治疗组织,肿瘤
EP,Evoked Potential,诱发电位,神经
EPA,Eicosapentaenoic Acid,二十碳五烯酸,营养
EPO,Erythropoietin,促红细胞生成素,血液
EPS,Electrophysiology Study,电生理检查,心血管
ER,Endoplasmic Reticulum,内质网,细胞生物学
ER,Estrogen Receptor,雌激素受体,肿瘤
ERAS,Enhanced Recovery After Surgery,加速康复外科,外科
ERCP,Endoscopic Retrograde Cholangiopancreatography,内镜逆行胰胆管造影,消化
ERG,Electroretinogram,视网膜电图,眼科
ERPF,Effective Renal Plasma Flow,有效肾血浆流量,生理
ERS,European Respiratory Society,欧洲呼吸学会,呼吸
ESBL,Extended-Spectrum Beta-Lactamase,超广谱β-内酰胺酶,感染
ESD,Endoscopic Submucosal Dissection,内镜黏膜下剥离术,消化
ESLD,End-Stage Liver Disease,终末期肝病,消化
ESNO,European Society of Neuro-Oncology,欧洲神经肿瘤学会,肿瘤
ESR,Erythrocyte Sedimentation Rate,红细胞沉降率,检验
ESRD,End-Stage Renal Disease,终末期肾病,肾病
ESRF,End-Stage Renal Failure,终末期肾功能衰竭,肾病
ESBL,Escherichia coli F-A Beta Lactamase,大肠杆菌超广谱β内酰胺酶,感染
ESS,Epworth Sleepiness Scale,Epworth嗜睡量表,呼吸
ET,Endotracheal Tube,气管导管,麻醉
ET,Essential Thrombocythemia,原发性血小板增多症,血液
ETA,Endotracheal Aspirate,气管内吸出物,呼吸
ETEC,Enterotoxigenic Escherichia Coli,产肠毒素性大肠杆菌,感染
ETT,Exercise Tolerance Test,运动耐量试验,心血管
EUA,Examination Under Anesthesia,麻醉下检查,外科
EUS,Endoscopic Ultrasound,超声内镜,消化
EV,Esophageal Varices,食管静脉曲张,消化
EVAR,Endovascular Aneurysm Repair,血管内动脉瘤修复术,血管外科
EVL,Endoscopic Variceal Ligation,内镜下静脉曲张套扎术,消化
EWS,Early Warning Score,早期预警评分,重症
FAB,French American British,法美英分类（白血病）,血液
FACE,Flow cytometry Analysis of Cell surface Expression,流式细胞术细胞表面表达分析,检验
FAP,Familial Adenomatous Polyposis,家族性腺瘤性息肉病,消化
FBG,Fasting Blood Glucose,空腹血糖,检验
FBS,Fasting Blood Sugar,空腹血糖,检验
FCU,Flexor Carpi Ulnaris,尺侧腕屈肌,解剖
FDA,Food and Drug Administration,美国食品药品监督管理局,机构
FDP,Fibrin Degradation Product,纤维蛋白降解产物,检验
FENa,Fractional Excretion of Sodium,钠排泄分数,检验
FEV1,Forced Expiratory Volume in 1 second,第1秒用力呼气容积,呼吸
FFA,Free Fatty Acid,游离脂肪酸,检验
FFP,Fresh Frozen Plasma,新鲜冰冻血浆,血液
FGFR,Fibroblast Growth Factor Receptor,成纤维细胞生长因子受体,肿瘤
FHR,Fetal Heart Rate,胎心率,妇产科
FIM,Functional Independence Measure,功能独立性评定,康复
FISH,Fluorescence In Situ Hybridization,荧光原位杂交,遗传
FLAIR,Fluid-Attenuated Inversion Recovery,液体衰减反转恢复,影像
FLT3,Fms-Like Tyrosine Kinase 3,FMS样酪氨酸激酶3,肿瘤
FMF,Familial Mediterranean Fever,家族性地中海热,风湿免疫
FNA,Fine Needle Aspiration,细针穿刺抽吸,病理
FNAC,Fine Needle Aspiration Cytology,细针穿刺抽吸细胞学,病理
FOBT,Fecal Occult Blood Test,粪便隐血试验,检验
FPG,Fasting Plasma Glucose,空腹血浆葡萄糖,检验
FRC,Functional Residual Capacity,功能残气量,呼吸
FSGS,Focal Segmental Glomerulosclerosis,局灶节段性肾小球硬化,肾病
FSH,Follicle-Stimulating Hormone,卵泡刺激素,内分泌
FT3,Free Triiodothyronine,游离三碘甲状腺原氨酸,检验
FT4,Free Thyroxine,游离甲状腺素,检验
FTA-ABS,Fluorescent Treponemal Antibody Absorption,荧光梅毒螺旋体抗体吸收试验,检验
FTC,Falls Team Conference,跌倒评估会议,老年医学
FVC,Forced Vital Capacity,用力肺活量,呼吸
G-CSF,Granulocyte Colony-Stimulating Factor,粒细胞集落刺激因子,血液
G-tube,Gastrostomy Tube,胃造瘘管,外科
GA,General Anesthesia,全身麻醉,麻醉
GABA,Gamma-Aminobutyric Acid,γ-氨基丁酸,神经
GAD,Glutamic Acid Decarboxylase,谷氨酸脱羧酶,检验
GAD,Generalized Anxiety Disorder,广泛性焦虑障碍,精神
GCS,Glasgow Coma Scale,格拉斯哥昏迷评分,急诊
GC,Gonorrhea,淋病,感染
GDM,Gestational Diabetes Mellitus,妊娠期糖尿病,妇产科
GDP,Guanosine Diphosphate,鸟苷二磷酸,生化
GERD,Gastroesophageal Reflux Disease,胃食管反流病,消化
GES,Gastric Emptying Scintigraphy,胃排空显像,消化
GFAP,Glial Fibrillary Acidic Protein,胶质纤维酸性蛋白,病理
GFR,Glomerular Filtration Rate,肾小球滤过率,肾病
GGT,Gamma-Glutamyl Transferase,γ-谷氨酰转移酶,检验
GH,Growth Hormone,生长激素,内分泌
GGO,Ground-Glass Opacity,磨玻璃影,影像
GI,Gastrointestinal,胃肠道的,消化
GIST,Gastrointestinal Stromal Tumor,胃肠道间质瘤,消化
GITT,Gut Transit Time,肠道传输时间,消化
GLP-1,Glucagon-Like Peptide-1,胰高血糖素样肽-1,内分泌
GLUT,Glucose Transporter,葡萄糖转运蛋白,内分泌
GM-CSF,Granulocyte-Macrophage Colony-Stimulating Factor,粒细胞-巨噬细胞集落刺激因子,血液
GN,Glomerulonephritis,肾小球肾炎,肾病
GNRH,Gonadotropin-Releasing Hormone,促性腺激素释放激素,内分泌
GOLD,Global Initiative for Chronic Obstructive Lung Disease,慢性阻塞性肺疾病全球倡议,呼吸
GOS,Glasgow Outcome Scale,格拉斯哥预后评分,神经外科
GP,General Practitioner,全科医师,全科
GPA,Granulomatosis with Polyangiitis,肉芽肿性多血管炎,风湿免疫
GRADE,Grading of Recommendations Assessment Development and Evaluation,推荐分级评估制定与评价,临床研究
GTT,Glucose Tolerance Test,葡萄糖耐量试验,内分泌
GU,Genitourinary,泌尿生殖的,泌尿
GVHD,Graft-Versus-Host Disease,移植物抗宿主病,血液
GXT,Graded Exercise Test,分级运动试验,心血管
H&E,Hematoxylin and Eosin,苏木精-伊红染色,病理
H2RA,Histamine-2 Receptor Antagonist,H2受体拮抗剂,消化
HA,Headache,头痛,症状
HA,Hyaluronic Acid,透明质酸,骨科
HAP,Hospital-Acquired Pneumonia,医院获得性肺炎,呼吸
HAV,Hepatitis A Virus,甲型肝炎病毒,感染
Hb,Hemoglobin,血红蛋白,检验
HbA1c,Glycated Hemoglobin,糖化血红蛋白,检验
HBeAg,Hepatitis B e Antigen,乙型肝炎e抗原,感染
HBIG,Hepatitis B Immune Globulin,乙肝免疫球蛋白,感染
HBsAg,Hepatitis B surface Antigen,乙型肝炎表面抗原,感染
HBV,Hepatitis B Virus,乙型肝炎病毒,感染
HCC,Hepatocellular Carcinoma,肝细胞癌,消化
hCG,human Chorionic Gonadotropin,人绒毛膜促性腺激素,检验
Hct,Hematocrit,血细胞比容,检验
HCV,Hepatitis C Virus,丙型肝炎病毒,感染
HD,Hemodialysis,血液透析,肾病
HDL,High-Density Lipoprotein,高密度脂蛋白,检验
HDL-C,HDL Cholesterol,高密度脂蛋白胆固醇,检验
HE,His bundle Electrogram,希氏束电图,心血管
HELLP,Hemolysis Elevated Liver enzymes Low Platelets,HELLP综合征,妇产科
HER2,Human Epidermal growth factor Receptor 2,人表皮生长因子受体2,肿瘤
HF,Heart Failure,心力衰竭,心血管
HFNC,High Flow Nasal Cannula,高流量鼻导管,呼吸
HFpEF,HF with preserved Ejection Fraction,射血分数保留的心力衰竭,心血管
HFrEF,HF with reduced Ejection Fraction,射血分数降低的心力衰竭,心血管
HGPRT,Hypoxanthine-Guanine Phosphoribosyltransferase,次黄嘌呤-鸟嘌呤磷酸核糖转移酶,遗传
HHS,Hyperosmolar Hyperglycemic State,高渗性高血糖状态,内分泌
HHT,Hereditary Hemorrhagic Telangiectasia,遗传性出血性毛细血管扩张症,血液
HI,Head Injury,头部损伤,神经外科
HIDA,Hepatobiliary Iminodiacetic Acid,肝胆亚氨基二乙酸,影像
HIV,Human Immunodeficiency Virus,人类免疫缺陷病毒,感染
HK,Hexokinase,己糖激酶,生化
HL,Hodgkin Lymphoma,霍奇金淋巴瘤,血液
HLA,Human Leukocyte Antigen,人类白细胞抗原,免疫
HLH,Hemophagocytic Lymphohistiocytosis,噬血细胞性淋巴组织细胞增多症,血液
HMB,Heavy Menstrual Bleeding,月经量过多,妇产科
HNPCC,Hereditary Nonpolyposis Colorectal Cancer,遗传性非息肉病性结直肠癌,消化
HOCM,Hypertrophic Obstructive Cardiomyopathy,肥厚型梗阻性心肌病,心血管
HOPE,HOPE study,HOPE研究,心血管
HP,Helicobacter Pylori,幽门螺杆菌,消化
HPV,Human Papillomavirus,人乳头瘤病毒,感染
HR,Hazard Ratio,风险比,统计
HR,Heart Rate,心率,生理
HRS,Hepatorenal Syndrome,肝肾综合征,消化
HRT,Hormone Replacement Therapy,激素替代治疗,妇产科
HS,Heart Sounds,心音,心血管
HSC,Hematopoietic Stem Cell,造血干细胞,血液
HSCT,Hematopoietic Stem Cell Transplantation,造血干细胞移植,血液
HSD,Hydroxysteroid Dehydrogenase,羟基类固醇脱氢酶,内分泌
HSE,Herpes Simplex Encephalitis,单纯疱疹病毒性脑炎,感染
HSG,Hysterosalpingography,子宫输卵管造影,妇产科
HSP,Henoch-Schonlein Purpura,过敏性紫癜,风湿免疫
HSS,Health Systems Strengthening,卫生系统强化,公卫
HSV,Herpes Simplex Virus,单纯疱疹病毒,感染
HTN,Hypertension,高血压,心血管
HUS,Hemolytic Uremic Syndrome,溶血尿毒综合征,肾病
HVA,Homovanillic Acid,高香草酸,检验
Hx,History,病史,临床
I&D,Incision and Drainage,切开引流,外科
IA,Intra-Arterial,动脉内,临床
IAB,Induced Abortion,人工流产,妇产科
IABP,Intra-Aortic Balloon Pump,主动脉内球囊反搏,心血管
IBS,Irritable Bowel Syndrome,肠易激综合征,消化
IBW,Ideal Body Weight,理想体重,营养
IC,Informed Consent,知情同意,伦理
ICA,Internal Carotid Artery,颈内动脉,神经
ICD,Implantable Cardioverter Defibrillator,植入式心律转复除颤器,心血管
ICF,Intracellular Fluid,细胞内液,生理
ICH,Intracerebral Hemorrhage,脑出血,神经
ICHD,International Classification of Headache Disorders,国际头痛分类,神经
ICM,Ischemic Cardiomyopathy,缺血性心肌病,心血管
ICP,Intracranial Pressure,颅内压,神经外科
ICS,Inhaled Corticosteroid,吸入性糖皮质激素,呼吸
ICSI,Intracytoplasmic Sperm Injection,卵胞浆内单精子注射,生殖
ICU,Intensive Care Unit,重症监护病房,重症
ID,Infectious Disease,感染性疾病,感染
IDDM,Insulin-Dependent Diabetes Mellitus,胰岛素依赖型糖尿病,内分泌
IE,Infective Endocarditis,感染性心内膜炎,感染
IEF,Isoelectric Focusing,等电聚焦,分子生物学
Ig,Immunoglobulin,免疫球蛋白,免疫
IGF,Insulin-like Growth Factor,胰岛素样生长因子,内分泌
IGT,Impaired Glucose Tolerance,糖耐量减低,内分泌
IHC,Immunohistochemistry,免疫组织化学,病理
IL,Interleukin,白细胞介素,免疫
ILD,Interstitial Lung Disease,间质性肺疾病,呼吸
IM,Intramuscular,肌肉内,临床
IM,Internal Medicine,内科学,临床
IMA,Internal Mammary Artery,乳内动脉,心血管
INH,Isoniazid,异烟肼,感染
INR,International Normalized Ratio,国际标准化比值,检验
IO,Intraosseous,骨内的,急诊
IOL,Intraocular Lens,人工晶状体,眼科
IP,Intraperitoneal,腹膜内,临床
IPF,Idiopathic Pulmonary Fibrosis,特发性肺纤维化,呼吸
IPPV,Intermittent Positive Pressure Ventilation,间歇正压通气,呼吸
IR,Insulin Resistance,胰岛素抵抗,内分泌
IRB,Institutional Review Board,机构审查委员会,伦理
IRIS,Immune Reconstitution Inflammatory Syndrome,免疫重建炎症综合征,感染
IS,Incentive Spirometry,激励性肺量测定,呼吸
SIL,Squamous Intraepithelial Lesion,鳞状上皮内病变,病理
IST,Inappropriate Sinus Tachycardia,不适当窦性心动过速,心血管
IT,Intrathecal,鞘内,临床
ITP,Immune Thrombocytopenia,免疫性血小板减少症,血液
ITT,Intention-to-Treat,意向性治疗,临床研究
IUI,Intrauterine Insemination,宫腔内人工授精,生殖
IV,Intravenous,静脉内,临床
IVC,Inferior Vena Cava,下腔静脉,解剖
IVF,In Vitro Fertilization,体外受精,生殖
IVIG,Intravenous Immunoglobulin,静脉注射免疫球蛋白,免疫
IVUS,Intravascular Ultrasound,血管内超声,影像
JCV,JC Virus,JC病毒,感染
JDM,Juvenile Dermatomyositis,幼年型皮肌炎,风湿免疫
JIA,Juvenile Idiopathic Arthritis,幼年特发性关节炎,风湿免疫
JNC,Joint National Committee,联合国家委员会,心血管
JVD,Jugular Venous Distention,颈静脉怒张,心血管
JVP,Jugular Venous Pressure,颈静脉压,心血管
K,Potassium,钾,检验
KUB,Kidney Ureter Bladder,肾输尿管膀胱,影像
KPS,Karnofsky Performance Status,卡氏功能状态评分,肿瘤
KS,Kaposi's Sarcoma,卡波西肉瘤,肿瘤
L-DOPA,Levodopa,左旋多巴,神经
LA,Left Atrium,左心房,心血管
LA,Local Anesthesia,局部麻醉,麻醉
LABA,Long-Acting Beta Agonist,长效β受体激动剂,呼吸
LAD,Left Anterior Descending,左前降支,心血管
LAE,Left Atrial Enlargement,左心房扩大,心血管
LAM,Leukocyte Adhesion Molecule,白细胞黏附分子,免疫
LAMA,Long-Acting Muscarinic Antagonist,长效毒蕈碱受体拮抗剂,呼吸
Lap,Exploratory Laparotomy,剖腹探查术,外科
LBBB,Left Bundle Branch Block,左束支传导阻滞,心血管
LBW,Low Birth Weight,低出生体重,儿科
LC,Laparoscopic Cholecystectomy,腹腔镜胆囊切除术,外科
LCIS,Lobular Carcinoma In Situ,小叶原位癌,肿瘤
LCM,Left Costal Margin,左肋缘,体检
LDH,Lactate Dehydrogenase,乳酸脱氢酶,检验
LDL,Low-Density Lipoprotein,低密度脂蛋白,检验
LDL-C,LDL Cholesterol,低密度脂蛋白胆固醇,检验
LEC,Low Energy Cardioversion,低能量电复律,心血管
LES,Lower Esophageal Sphincter,食管下括约肌,消化
LFT,Liver Function Test,肝功能检查,检验
LGA,Large for Gestational Age,大于胎龄儿,儿科
LH,Luteinizing Hormone,黄体生成素,内分泌
LIF,Leukemia Inhibitory Factor,白血病抑制因子,血液
LIMA,Left Internal Mammary Artery,左乳内动脉,心血管
LIP,Lymphocytic Interstitial Pneumonia,淋巴细胞性间质性肺炎,呼吸
LMCA,Left Main Coronary Artery,左主干冠状动脉,心血管
LMN,Lower Motor Neuron,下运动神经元,神经
LMWH,Low Molecular Weight Heparin,低分子肝素,心血管
LN,Lymph Node,淋巴结,解剖
LND,Lymph Node Dissection,淋巴结清扫,外科
LOC,Loss of Consciousness,意识丧失,症状
LOS,Length of Stay,住院天数,管理
LP,Lumbar Puncture,腰椎穿刺,神经
LPS,Lipopolysaccharide,脂多糖,微生物
LT,Leukotriene,白三烯,免疫
LTBI,Latent Tuberculosis Infection,潜伏性结核感染,感染
LTR,Long Terminal Repeat,长末端重复序列,分子生物学
LUSCS,Lower Uterine Segment Cesarean Section,子宫下段剖宫产,妇产科
LV,Left Ventricle,左心室,心血管
LVAD,Left Ventricular Assist Device,左心室辅助装置,心血管
LVEDP,LV End-Diastolic Pressure,左室舒张末压,心血管
LVEF,Left Ventricular Ejection Fraction,左心室射血分数,心血管
LVH,Left Ventricular Hypertrophy,左心室肥厚,心血管
MALT,Mucosa-Associated Lymphoid Tissue,黏膜相关淋巴组织,免疫
MAO,Monoamine Oxidase,单胺氧化酶,神经
MAOI,MAO Inhibitor,单胺氧化酶抑制剂,精神
MARS,Molecular Adsorbent Recirculating System,分子吸附再循环系统,重症
MAS,Meconium Aspiration Syndrome,胎粪吸入综合征,儿科
MBC,Maximum Breathing Capacity,最大通气量,呼吸
MCH,Mean Corpuscular Hemoglobin,平均红细胞血红蛋白量,检验
MCHC,MCH Concentration,平均红细胞血红蛋白浓度,检验
MCV,Mean Corpuscular Volume,平均红细胞体积,检验
MD,Doctor of Medicine,医学博士,教育
MDR,Multidrug-Resistant,多重耐药的,感染
MDS,Myelodysplastic Syndrome,骨髓增生异常综合征,血液
MDT,Multidisciplinary Team,多学科团队,管理
MEN,Multiple Endocrine Neoplasia,多发性内分泌腺瘤,内分泌
MERS,Middle East Respiratory Syndrome,中东呼吸综合征,感染
MET,Metabolic Equivalent,代谢当量,康复
MG,Myasthenia Gravis,重症肌无力,神经
MGUS,Monoclonal Gammopathy of Undetermined Significance,意义未明的单克隆丙种球蛋白病,血液
MH,Malignant Hyperthermia,恶性高热,麻醉
MHC,Major Histocompatibility Complex,主要组织相容性复合体,免疫
MI,Myocardial Infarction,心肌梗死,心血管
MICU,Medical Intensive Care Unit,内科重症监护病房,重症
MIP,Maximum Inspiratory Pressure,最大吸气压,呼吸
MIS,Minimally Invasive Surgery,微创外科,外科
MM,Multiple Myeloma,多发性骨髓瘤,血液
MMF,Mycophenolate Mofetil,霉酚酸酯,免疫
MMR,Measles Mumps Rubella,麻疹流行性腮腺炎风疹疫苗,免疫
MMR,Mismatch Repair,错配修复,肿瘤
MN,Membranous Nephropathy,膜性肾病,肾病
MODS,Multiple Organ Dysfunction Syndrome,多器官功能障碍综合征,重症
MPGN,Membranoproliferative Glomerulonephritis,膜增生性肾小球肾炎,肾病
MPN,Myeloproliferative Neoplasm,骨髓增殖性肿瘤,血液
MPV,Mean Platelet Volume,平均血小板体积,检验
MR,Magnetic Resonance,磁共振,影像
MR,Mental Retardation,智力障碍,儿科
MRA,Magnetic Resonance Angiography,磁共振血管成像,影像
MRCP,Magnetic Resonance Cholangiopancreatography,磁共振胰胆管成像,影像
MRCS,Magnetic Resonance Cholangioscopy,磁共振胆管镜检查,影像
MRI,Magnetic Resonance Imaging,磁共振成像,影像
MRM,Modified Radical Mastectomy,改良根治性乳房切除术,外科
MRSA,Methicillin-Resistant Staphylococcus Aureus,耐甲氧西林金黄色葡萄球菌,感染
MS,Multiple Sclerosis,多发性硬化,神经
MSAFP,Maternal Serum Alpha-Fetoprotein,母血清甲胎蛋白,妇产科
MSE,Mental Status Examination,精神状态检查,精神
MSI,Microsatellite Instability,微卫星不稳定性,肿瘤
MSS,Microsatellite Stable,微卫星稳定,肿瘤
MSU,Midstream Urine,中段尿,检验
MTB,Mycobacterium Tuberculosis,结核分枝杆菌,感染
mTICI,modified Thrombolysis in Cerebral Infarction,改良脑梗死溶栓分级,神经
MTX,Methotrexate,甲氨蝶呤,肿瘤
MUGA,Multiple Gated Acquisition,多门控采集,影像
MUST,Malnutrition Universal Screening Tool,营养不良通用筛查工具,营养
MV,Mitral Valve,二尖瓣,心血管
MVP,Mitral Valve Prolapse,二尖瓣脱垂,心血管
MVR,Mitral Valve Replacement,二尖瓣置换术,心血管
'''You can get information on this topic for your research from: 1. '''NA,Sodium,钠,检验
NAC,N-Acetylcysteine,N-乙酰半胱氨酸,急诊
NAFLD,Nonalcoholic Fatty Liver Disease,非酒精性脂肪性肝病,消化
NASH,Nonalcoholic Steatohepatitis,非酒精性脂肪性肝炎,消化
NCCN,National Comprehensive Cancer Network,美国国家综合癌症网络,肿瘤
NCS,Nerve Conduction Study,神经传导研究,神经
NCSE,Non-Convulsive Status Epilepticus,非惊厥性癫痫持续状态,神经
ND,YAG,Neodymium-Doped Yttrium Aluminum Garnet,掺钕钇铝石榴石激光器,眼科
NEC,Necrotizing Enterocolitis,坏死性小肠结肠炎,儿科
NG,Nasogastric,鼻胃的,护理
NHL,Non-Hodgkin Lymphoma,非霍奇金淋巴瘤,血液
NICU,Neonatal Intensive Care Unit,新生儿重症监护病房,儿科
NIDDM,Non-Insulin-Dependent Diabetes Mellitus,非胰岛素依赖型糖尿病,内分泌
NIH,NIHSS,美国国立卫生研究院卒中量表,神经
NK,Natural Killer,自然杀伤细胞,免疫
NKA,No Known Allergies,无已知过敏史,病史
NMR,Nuclear Magnetic Resonance,核磁共振,影像
NNT,Number Needed to Treat,需要治疗的人数,统计
NO,Nitric Oxide,一氧化氮,生化
NOAC,Novel Oral Anticoagulant,新型口服抗凝药,心血管
NPO,Nil Per Os,禁食,临床
NREM,Non-Rapid Eye Movement,非快动眼,神经
NRS,Nutritional Risk Screening,营养风险筛查,营养
NS,Normal Saline,生理盐水,药理
NSAID,Non-Steroidal Anti-Inflammatory Drug,非甾体抗炎药,药理
NSCLC,Non-Small Cell Lung Cancer,非小细胞肺癌,肿瘤
NSIP,Nonspecific Interstitial Pneumonia,非特异性间质性肺炎,呼吸
NST,Non-Stress Test,无应激试验,妇产科
NT-proBNP,N-terminal pro-Brain Natriuretic Peptide,N末端脑钠肽前体,检验
NTD,Neural Tube Defect,神经管缺陷,儿科
NTRK,Neurotrophic Tyrosine Receptor Kinase,神经营养性酪氨酸受体激酶,肿瘤
NYHA,New York Heart Association,纽约心脏协会,心血管
O&G,Obstetrics and Gynecology,妇产科学,妇产科
OA,Osteoarthritis,骨关节炎,骨科
OAB,Overactive Bladder,膀胱过度活动症,泌尿
OAG,Open Angle Glaucoma,开角型青光眼,眼科
OAT,Ovarian-Adnexal Reporting and Data System O-RADS,卵巢附件报告和数据系统,妇产科
OCD,Obsessive-Compulsive Disorder,强迫症,精神
OCP,Oral Contraceptive Pill,口服避孕药,妇产科
OCT,Optical Coherence Tomography,光学相干断层扫描,眼科
OD,Right Eye,右眼,眼科
OGTT,Oral Glucose Tolerance Test,口服葡萄糖耐量试验,内分泌
OHS,Obesity Hypoventilation Syndrome,肥胖低通气综合征,呼吸
OHT,Ocular Hypertension,高眼压,眼科
OI,Osteogenesis Imperfecta,成骨不全,骨科
OLD,Obstructive Lung Disease,阻塞性肺疾病,呼吸
OM,Otitis Media,中耳炎,耳鼻喉
OP,Organophosphorus,有机磷,急诊
OPD,Outpatient Department,门诊部,管理
OR,Odds Ratio,比值比,统计
ORIF,Open Reduction Internal Fixation,切开复位内固定,骨科
ORL,Otorhinolaryngology,耳鼻喉科学,耳鼻喉
OS,Overall Survival,总生存期,肿瘤
OSA,Obstructive Sleep Apnea,阻塞性睡眠呼吸暂停,呼吸
OT,Occupational Therapy,作业治疗,康复
OTC,Over The Counter,非处方药,药理
P-ANCA,Perinuclear ANCA,核周型ANCA,风湿免疫
P-gp,P-glycoprotein,P-糖蛋白,药理
PA,Pulmonary Artery,肺动脉,心血管
PA,Posteroanterior,后前位,影像
PAC,Premature Atrial Contraction,房性期前收缩,心血管
PACU,Post-Anesthesia Care Unit,麻醉后恢复室,麻醉
PAD,Peripheral Arterial Disease,外周动脉疾病,血管外科
PAF,Paroxysmal Atrial Fibrillation,阵发性心房颤动,心血管
PAH,Pulmonary Arterial Hypertension,肺动脉高压,呼吸
PALS,Pediatric Advanced Life Support,儿科高级生命支持,儿科
PAN,Polyarteritis Nodosa,结节性多动脉炎,风湿免疫
PaO2,Partial pressure of Oxygen in arterial blood,动脉血氧分压,检验
PaCO2,Partial pressure of Carbon dioxide in arterial blood,动脉血二氧化碳分压,检验
PAP,Pulmonary Artery Pressure,肺动脉压,心血管
PAP,Prostatic Acid Phosphatase,前列腺酸性磷酸酶,检验
PAS,Periodic Acid-Schiff,过碘酸雪夫染色,病理
PAT,Paroxysmal Atrial Tachycardia,阵发性房性心动过速,心血管
PBC,Primary Biliary Cholangitis,原发性胆汁性胆管炎,消化
PBM,Patient Blood Management,患者血液管理,血液
PC,Platelet Concentrate,浓缩血小板,血液
PCA,Patient-Controlled Analgesia,患者自控镇痛,疼痛
PCa,Prostate Cancer,前列腺癌,泌尿
PCEA,Patient-Controlled Epidural Analgesia,患者自控硬膜外镇痛,疼痛
PCI,Percutaneous Coronary Intervention,经皮冠状动脉介入治疗,心血管
PCL,Posterior Cruciate Ligament,后交叉韧带,骨科
PCOS,Polycystic Ovary Syndrome,多囊卵巢综合征,妇产科
PCP,Pneumocystis pneumonia,肺孢子菌肺炎,感染
PCR,Polymerase Chain Reaction,聚合酶链反应,分子生物学
PCS,Post-Concussion Syndrome,脑震荡后综合征,神经
PCT,Procalcitonin,降钙素原,检验
PCV,Packed Cell Volume,红细胞压积,检验
PCWP,Pulmonary Capillary Wedge Pressure,肺毛细血管楔压,心血管
PD,Peritoneal Dialysis,腹膜透析,肾病
PD,Parkinson's Disease,帕金森病,神经
PD-1,Programmed Death-1,程序性死亡受体1,肿瘤
PD-L1,Programmed Death-Ligand 1,程序性死亡配体1,肿瘤
PDA,Patent Ductus Arteriosus,动脉导管未闭,儿科
PDGF,Platelet-Derived Growth Factor,血小板衍生生长因子,血液
PE,Pulmonary Embolism,肺栓塞,呼吸
PE,Physical Examination,体格检查,临床
PEA,Pulseless Electrical Activity,无脉电活动,急诊
PEEP,Positive End-Expiratory Pressure,呼气末正压,呼吸
PEF,Peak Expiratory Flow,呼气峰流量,呼吸
PEG,Percutaneous Endoscopic Gastrostomy,经皮内镜下胃造瘘术,外科
PERRLA,Pupils Equal Round Reactive to Light and Accommodation,瞳孔等大等圆对光调节反射正常,神经
PET,Positron Emission Tomography,正电子发射断层扫描,影像
PFT,Pulmonary Function Test,肺功能检查,呼吸
PG,Prostaglandin,前列腺素,药理
pH,potential of Hydrogen,氢离子浓度指数,检验
PH,Prolyl Hydroxylase,脯氨酸羟化酶,生化
PICC,Peripherally Inserted Central Catheter,经外周静脉置入中心静脉导管,护理
PICU,Pediatric Intensive Care Unit,儿科重症监护病房,儿科
PID,Pelvic Inflammatory Disease,盆腔炎性疾病,妇产科
PIP,Proximal Interphalangeal,近端指间关节,骨科
PIOPED,Prospective Investigation of Pulmonary Embolism Diagnosis,肺栓塞诊断前瞻性研究,呼吸
PKD,Polycystic Kidney Disease,多囊肾病,肾病
PLT,Platelet,血小板,检验
PM,Polymyositis,多发性肌炎,风湿免疫
PMH,Past Medical History,既往史,病历
PMI,Point of Maximal Impulse,最强搏动点,心血管
PMN,Polymorphonuclear Leukocyte,多形核白细胞,血液
PMS,Pre-Menstrual Syndrome,经前期综合征,妇产科
PN,Parenteral Nutrition,肠外营养,营养
PND,Paroxysmal Nocturnal Dyspnea,阵发性夜间呼吸困难,心血管
PNH,Paroxysmal Nocturnal Hemoglobinuria,阵发性睡眠性血红蛋白尿,血液
PO,Per Os,经口,临床
POD,Postoperative Day,术后天数,外科
POISE,PeriOperative ISchemic Evaluation,围手术期缺血评估,麻醉
PP,Per-Protocol,符合方案集,临床研究
PPD,Purified Protein Derivative,纯蛋白衍化物,感染
PPI,Proton Pump Inhibitor,质子泵抑制剂,消化
PPV,Positive Predictive Value,阳性预测值,统计
PR,Progesterone Receptor,孕激素受体,肿瘤
PR,Partial Response,部分缓解,肿瘤
p.r.n.,pro re nata,必要时,临床
PROM,Patient-Reported Outcome Measure,患者报告结局指标,临床研究
PS,Performance Status,功能状态,肿瘤
PSA,Prostate-Specific Antigen,前列腺特异性抗原,检验
PSC,Primary Sclerosing Cholangitis,原发性硬化性胆管炎,消化
PSG,Polysomnography,多导睡眠图,呼吸
PSGN,Poststreptococcal Glomerulonephritis,链球菌感染后肾小球肾炎,肾病
PSP,Progressive Supranuclear Palsy,进行性核上性麻痹,神经
PSS,Primary Sjogren's Syndrome,原发性干燥综合征,风湿免疫
PT,Prothrombin Time,凝血酶原时间,检验
PT,Physical Therapy,物理治疗,康复
PTA,Percutaneous Transluminal Angioplasty,经皮腔内血管成形术,血管外科
PTCA,Percutaneous Transluminal Coronary Angioplasty,经皮腔内冠状动脉成形术,心血管
PTE,Pulmonary Thromboembolism,肺血栓栓塞,呼吸
PTH,Parathyroid Hormone,甲状旁腺激素,内分泌
PTSD,Post-Traumatic Stress Disorder,创伤后应激障碍,精神
PTT,Partial Thromboplastin Time,部分凝血活酶时间,检验
PU,Pregnancy Urine test,尿妊娠试验,检验
PUD,Peptic Ulcer Disease,消化性溃疡,消化
PV,Polycythemia Vera,真性红细胞增多症,血液
PVC,Premature Ventricular Contraction,室性期前收缩,心血管
PVD,Peripheral Vascular Disease,周围血管疾病,血管外科
PVR,Pulmonary Vascular Resistance,肺血管阻力,心血管
PVR,Post-Void Residual,排尿后残余尿量,泌尿
q.d.,quaque die,每日一次,临床
q.i.d.,quater in die,每日四次,临床
QALY,Quality-Adjusted Life Year,质量调整生命年,公卫
QOL,Quality of Life,生活质量,临床研究
RA,Rheumatoid Arthritis,类风湿关节炎,风湿免疫
RA,Right Atrium,右心房,心血管
RAAA,Ruptured Abdominal Aortic Aneurysm,破裂腹主动脉瘤,血管外科
RAC,Rapid Access Chest pain clinic,快速胸痛门诊,心血管
RAD,Right Axis Deviation,电轴右偏,心血管
RANKL,Receptor Activator of NF-kB Ligand,NF-kB受体活化因子配体,骨科
RAS,Renal Artery Stenosis,肾动脉狭窄,心血管
RAS,Renin-Angiotensin System,肾素-血管紧张素系统,生理
RASS,Richmond Agitation-Sedation Scale,Richmond镇静-躁动评分,重症
RBBB,Right Bundle Branch Block,右束支传导阻滞,心血管
RBC,Red Blood Cell,红细胞,血液
RCC,Renal Cell Carcinoma,肾细胞癌,泌尿
RCT,Randomized Controlled Trial,随机对照试验,临床研究
RDW,Red cell Distribution Width,红细胞分布宽度,检验
REM,Rapid Eye Movement,快动眼睡眠,神经
RFA,Radiofrequency Ablation,射频消融,心血管
Rh,Rhesus factor,Rh因子,血液
RHC,Right Heart Catheterization,右心导管检查,心血管
RIA,Radioimmunoassay,放射免疫测定,检验
RIF,Right Iliac Fossa,右髂窝,体检
RLS,Restless Legs Syndrome,不宁腿综合征,神经
RNA,Ribonucleic Acid,核糖核酸,分子生物学
ROSC,Return of Spontaneous Circulation,自主循环恢复,急诊
ROS,Review of Systems,系统回顾,病历
Roux-en-Y,Roux-en-Y gastric bypass,Roux-en-Y胃旁路术,外科
RPD,Rapidly Progressive Dementia,快速进展性痴呆,神经
RPGN,Rapidly Progressive Glomerulonephritis,急进性肾小球肾炎,肾病
RQ,Respiratory Quotient,呼吸商,生理
RR,Relative Risk,相对危险度,统计
RR,Respiratory Rate,呼吸频率,生理
RRT,Renal Replacement Therapy,肾脏替代治疗,肾病
RS,Reiter's Syndrome,Reiter综合征,风湿免疫
RSA,Recurrent Spontaneous Abortion,复发性自然流产,妇产科
RSI,Rapid Sequence Intubation,快速序贯诱导插管,麻醉
RSV,Respiratory Syncytial Virus,呼吸道合胞病毒,感染
RT,Radiotherapy,放射治疗,肿瘤
rtPA,recombinant tissue Plasminogen Activator,重组组织型纤溶酶原激活物,神经
RTS,Revised Trauma Score,修订创伤评分,急诊
RUQ,Right Upper Quadrant,右上腹,体检
RV,Right Ventricle,右心室,心血管
RVD,Right Ventricular Dysfunction,右心室功能障碍,心血管
RVI,Right Ventricular Infarction,右心室梗死,心血管
RVOT,Right Ventricular Outflow Tract,右心室流出道,心血管
S1,First Heart Sound,第一心音,心血管
S2,Second Heart Sound,第二心音,心血管
SABA,Short-Acting Beta Agonist,短效β受体激动剂,呼吸
SAC,Spontaneous Abortion Complete,完全自然流产,妇产科
SAD,Seasonal Affective Disorder,季节性情感障碍,精神
SAH,Subarachnoid Hemorrhage,蛛网膜下腔出血,神经
SAID,Steroid Anti-Inflammatory Drug,甾体抗炎药,药理
SALT,Skin-Associated Lymphoid Tissue,皮肤相关淋巴组织,免疫
SAM,S-adenosylmethionine,S-腺苷甲硫氨酸,生化
SAPS,Simplified Acute Physiology Score,简化急性生理评分,重症
SARS,Severe Acute Respiratory Syndrome,严重急性呼吸综合征,感染
SB,Spontaneous Breathing,自主呼吸,麻醉
SBP,Systolic Blood Pressure,收缩压,心血管
SBRT,Stereotactic Body Radiotherapy,立体定向放射治疗,肿瘤
SCC,Squamous Cell Carcinoma,鳞状细胞癌,肿瘤
SCD,Sudden Cardiac Death,心脏性猝死,心血管
SCD,Sickle Cell Disease,镰状细胞病,血液
SCFE,Slipped Capital Femoral Epiphysis,股骨头骨骺滑脱,骨科
SCI,Spinal Cord Injury,脊髓损伤,神经外科
SCLC,Small Cell Lung Cancer,小细胞肺癌,肿瘤
SCP,Single-Chain Protein,单链蛋白,分子生物学
SD,Standard Deviation,标准差,统计
SDH,Subdural Hematoma,硬膜下血肿,神经外科
SE,Status Epilepticus,癫痫持续状态,神经
SEER,Surveillance Epidemiology and End Results,监测流行病学与最终结果,肿瘤
SEM,Standard Error of Mean,标准误,统计
SERM,Selective Estrogen Receptor Modulator,选择性雌激素受体调节剂,肿瘤
SF-36,Short Form 36,36项简明健康状况调查表,临床研究
SGA,Small for Gestational Age,小于胎龄儿,儿科
SGOT,Serum Glutamic-Oxaloacetic Transaminase,血清谷草转氨酶,检验
SGPT,Serum Glutamic-Pyruvic Transaminase,血清谷丙转氨酶,检验
SIADH,Syndrome of Inappropriate ADH secretion,抗利尿激素不适当分泌综合征,内分泌
SIDS,Sudden Infant Death Syndrome,婴儿猝死综合征,儿科
SIMV,Synchronized Intermittent Mandatory Ventilation,同步间歇指令通气,呼吸
SIRS,Systemic Inflammatory Response Syndrome,全身炎症反应综合征,重症
SJS,Stevens-Johnson Syndrome,Stevens-Johnson综合征,皮肤
SLE,Systemic Lupus Erythematosus,系统性红斑狼疮,风湿免疫
SMA,Spinal Muscular Atrophy,脊髓性肌萎缩,神经
SMA,Superior Mesenteric Artery,肠系膜上动脉,解剖
SMV,Superior Mesenteric Vein,肠系膜上静脉,解剖
SNB,Sentinel Node Biopsy,前哨淋巴结活检,肿瘤
SNP,Single Nucleotide Polymorphism,单核苷酸多态性,遗传
SNRI,Serotonin-Norepinephrine Reuptake Inhibitor,5-羟色胺去甲肾上腺素再摄取抑制剂,精神
SOB,Shortness of Breath,气促,症状
SOFA,Sequential Organ Failure Assessment,序贯器官衰竭评分,重症
SOL,Space-Occupying Lesion,占位性病变,神经
SOT,Solid Organ Transplantation,实体器官移植,外科
SP,Sublobar Resection,亚肺叶切除,肿瘤
SPECT,Single Photon Emission Computed Tomography,单光子发射计算机断层扫描,影像
SpO2,Peripheral Oxygen Saturation,经皮血氧饱和度,生理
SQ,Subcutaneous,皮下,临床
SR,Sinus Rhythm,窦性心律,心血管
SRS,Stereotactic Radiosurgery,立体定向放射外科,肿瘤
SS,Serum Sickness,血清病,免疫
SSc,Systemic Sclerosis,系统性硬化症,风湿免疫
SSP,Surgical Site Preparation,手术部位准备,外科
SSRI,Selective Serotonin Reuptake Inhibitor,选择性5-羟色胺再摄取抑制剂,精神
ST,Speech Therapy,语言治疗,康复
STAT,statim,立即,临床
STEMI,ST-Segment Elevation Myocardial Infarction,ST段抬高型心肌梗死,心血管
STI,Sexually Transmitted Infection,性传播感染,感染
SVC,Superior Vena Cava,上腔静脉,解剖
SVCS,SVC Syndrome,上腔静脉综合征,肿瘤
SVT,Supraventricular Tachycardia,室上性心动过速,心血管
T1DM,Type 1 Diabetes Mellitus,1型糖尿病,内分泌
T2DM,Type 2 Diabetes Mellitus,2型糖尿病,内分泌
T3,Triiodothyronine,三碘甲状腺原氨酸,检验
T4,Thyroxine,甲状腺素,检验
TA,Tricuspid Annulus,三尖瓣环,心血管
TAA,Thoracic Aortic Aneurysm,胸主动脉瘤,血管外科
TAC,Thoracic Aortic Calcification,胸主动脉钙化,心血管
TACE,Transcatheter Arterial Chemoembolization,经导管动脉化疗栓塞,肿瘤
TAH,Total Abdominal Hysterectomy,经腹全子宫切除术,妇产科
TAVI,Transcatheter Aortic Valve Implantation,经导管主动脉瓣植入术,心血管
TB,Tuberculosis,结核病,感染
TBI,Traumatic Brain Injury,创伤性脑损伤,神经外科
TBil,Total Bilirubin,总胆红素,检验
TCA,Tricyclic Antidepressant,三环类抗抑郁药,精神
TCH,Total Cholesterol,总胆固醇,检验
TCM,Traditional Chinese Medicine,中医,传统医学
Td,Tetanus diphtheria,破伤风白喉疫苗,免疫
Tdap,Tetanus diphtheria acellular pertussis,破伤风白喉无细胞百日咳疫苗,免疫
TEE,Transesophageal Echocardiography,经食管超声心动图,心血管
TEN,Toxic Epidermal Necrolysis,中毒性表皮坏死松解症,皮肤
TENS,Transcutaneous Electrical Nerve Stimulation,经皮电神经刺激,疼痛
TF,Transferrin,转铁蛋白,检验
TG,Triglycerides,甘油三酯,检验
TGA,Transient Global Amnesia,一过性全面遗忘症,神经
TIA,Transient Ischemic Attack,短暂性脑缺血发作,神经
TIBC,Total Iron Binding Capacity,总铁结合力,检验
TIPS,Transjugular Intrahepatic Portosystemic Shunt,经颈静脉肝内门体分流术,消化
TKI,Tyrosine Kinase Inhibitor,酪氨酸激酶抑制剂,肿瘤
TLC,Total Lung Capacity,肺总量,呼吸
TLC,Total Lymphocyte Count,淋巴细胞计数,检验
TLR,Toll-Like Receptor,Toll样受体,免疫
TLS,Tumor Lysis Syndrome,肿瘤溶解综合征,肿瘤
TM,Tympanic Membrane,鼓膜,耳鼻喉
TMP-SMX,Trimethoprim-Sulfamethoxazole,甲氧苄啶-磺胺甲恶唑,感染
TNF,Tumor Necrosis Factor,肿瘤坏死因子,免疫
TNM,Tumor Nodes Metastasis,肿瘤淋巴结转移分期,肿瘤
tPA,tissue Plasminogen Activator,组织型纤溶酶原激活物,神经
TPN,Total Parenteral Nutrition,全胃肠外营养,营养
TPO,Thyroid Peroxidase,甲状腺过氧化物酶,检验
TR,Tricuspid Regurgitation,三尖瓣反流,心血管
TRA,Transradial Access,经桡动脉途径,心血管
TRALI,Transfusion-Related Acute Lung Injury,输血相关急性肺损伤,血液
TRH,Thyrotropin-Releasing Hormone,促甲状腺激素释放激素,内分泌
TSH,Thyroid-Stimulating Hormone,促甲状腺激素,检验
TT,Thrombin Time,凝血酶时间,检验
TTE,Transthoracic Echocardiography,经胸超声心动图,心血管
TTP,Thrombotic Thrombocytopenic Purpura,血栓性血小板减少性紫癜,血液
TURBT,Transurethral Resection of Bladder Tumor,经尿道膀胱肿瘤切除术,泌尿
TURP,Transurethral Resection of Prostate,经尿道前列腺切除术,泌尿
TV,Tricuspid Valve,三尖瓣,心血管
UA,Unstable Angina,不稳定型心绞痛,心血管
UA,Uric Acid,尿酸,检验
UAC,Umbilical Artery Catheter,脐动脉导管,儿科
UC,Ulcerative Colitis,溃疡性结肠炎,消化
U&E,Urea and Electrolytes,尿素和电解质,检验
UFH,Unfractionated Heparin,普通肝素,心血管
UGI,Upper Gastrointestinal,上消化道的,消化
UMN,Upper Motor Neuron,上运动神经元,神经
URTI,Upper Respiratory Tract Infection,上呼吸道感染,感染
US,Ultrasound,超声检查,影像
USPSTF,US Preventive Services Task Force,美国预防服务工作组,公卫
UTI,Urinary Tract Infection,泌尿系感染,感染
UV,Ultraviolet,紫外线,皮肤
V/Q,Ventilation/Perfusion,通气/灌注,呼吸
VA,Veterans Affairs,退伍军人事务部,机构
VAD,Ventricular Assist Device,心室辅助装置,心血管
VAP,Ventilator-Associated Pneumonia,呼吸机相关性肺炎,呼吸
VATS,Video-Assisted Thoracoscopic Surgery,电视辅助胸腔镜手术,外科
VC,Vital Capacity,肺活量,呼吸
VCT,Voluntary Counseling and Testing,自愿咨询检测,公卫
VDRL,Venereal Disease Research Laboratory,性病研究实验室试验,检验
VEGF,Vascular Endothelial Growth Factor,血管内皮生长因子,肿瘤
VF,Ventricular Fibrillation,心室颤动,心血管
VHD,Valvular Heart Disease,心脏瓣膜病,心血管
VIN,Vulvar Intraepithelial Neoplasia,外阴上皮内瘤变,妇产科
VKA,Vitamin K Antagonist,维生素K拮抗剂,心血管
VLDL,Very Low-Density Lipoprotein,极低密度脂蛋白,检验
VMA,Vanillylmandelic Acid,香草扁桃酸,检验
VRE,Vancomycin-Resistant Enterococcus,耐万古霉素肠球菌,感染
VSD,Ventricular Septal Defect,室间隔缺损,心血管
VSS,Vital Signs Stable,生命体征稳定,临床
VT,Ventricular Tachycardia,室性心动过速,心血管
VTE,Venous Thromboembolism,静脉血栓栓塞症,血管外科
vWF,von Willebrand Factor,血管性血友病因子,血液
VZV,Varicella Zoster Virus,水痘-带状疱疹病毒,感染
WBC,White Blood Cell,白细胞,血液
WBRT,Whole Brain Radiotherapy,全脑放射治疗,肿瘤
WFNS,World Federation of Neurosurgical Societies,世界神经外科学会联合会,神经外科
WHO,World Health Organization,世界卫生组织,公卫
WPW,Wolff-Parkinson-White,Wolff-Parkinson-White综合征,心血管
XDR,Extensively Drug-Resistant,广泛耐药的,感染
YAC,Yeast Artificial Chromosome,酵母人工染色体,分子生物学
ZES,Zollinger-Ellison Syndrome,佐林格-埃利森综合征,消化
""".strip()

def main():
    # 加载已有
    existing = {}
    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            abbr = (row.get("缩写") or "").strip().upper()
            if abbr and abbr not in existing:
                existing[abbr] = [
                    row.get("缩写", "").strip(),
                    row.get("英文全称", "").strip(),
                    row.get("中文译名", "").strip(),
                    row.get("学科", "").strip(),
                ]

    print(f"已有 {len(existing)} 条术语")

    # 解析新术语
    new_count = 0
    for line in TERMS.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",", 3)]
        if len(parts) >= 4:
            abbr = parts[0].upper()
            if abbr and abbr not in existing:
                existing[abbr] = parts
                new_count += 1

    print(f"新增 {new_count} 条")

    # 写回完整文件
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["缩写", "英文全称", "中文译名", "学科"])
        for row in existing.values():
            writer.writerow(row)

    print(f"→ 术语库总量: {len(existing)} 条")
    print("→ 已保存到 terms.csv")

if __name__ == "__main__":
    main()
