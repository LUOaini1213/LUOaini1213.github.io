"""Build the bilingual, source-linked engineering case studies. No dependencies."""
import argparse
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRIVING = "https://github.com/LUOaini1213/driving-3dgs/blob/6a584b45579c333e1d2461ff4d64ff15b056e775/"
MFG = "https://github.com/LUOaini1213/manufacturing-planning-agent/"
MFG_SOURCE = MFG + "blob/0db8f89b02262031a358686c43fcf7fc25995c03/"
IFC = "https://github.com/LUOaini1213/ifcsg-precheck/"
IFC_SOURCE = IFC + "blob/fd48ad5664be8903442a1b70db917a7059830999/"


def link(url, label):
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


CASES = {
    "manufacturing": {
        "tag": "01 · DECISION WORKFLOW",
        "en": {
            "title": "Replan the future. Keep the work already done.",
            "deck": "A machine outage becomes a proposed schedule, a fair comparison and an explicit operator decision. The solver and simulation carry the numbers; the workflow carries the state.",
            "name": "Manufacturing planning",
            "problem": "At hour 2, a machine fails while a job is partly fabricated. Replacing the entire schedule would erase completed work and move an operation that has already started. A useful planner must preserve both commitments before improving the remaining horizon.",
            "decisions": [
                ("One state, two futures", "SimPy resumes the original schedule and the HiGHS candidate from the same snapshot. Completed operations stay frozen; work in progress keeps its machine and remaining duration."),
                ("A proposal is not a dispatch", "Compare completion, unfinished units, overtime and the timeline before confirming. Advancing consumes the selected proposal, then a second outage starts a new comparison from the resulting state."),
                ("Failure keeps an explainable path", "The solver runs in an isolated process. A failed or timed-out solve publishes no proposal and does not advance execution. Infeasible or worse candidates keep the original recommendation; stale confirmations cannot apply a proposal to a different snapshot."),
            ],
            "demo": "The public page replays a recorded, authored scenario. To edit an outage and run the actual solver, start the local demo after installing the repository requirements:",
            "command": "python -m mpa.demo --port 8840",
            "steps": ["Compare the default M1 outage from hour 2 to 6.", "Inspect the frozen prefix and remaining work; confirm a choice and advance to hour 3.5.", "Compare the second M2 outage, advance again and download the transition trace."],
            "boundary": "This is a four-unit synthetic exercise on a bounded time grid. It establishes the state transition and comparison contract, not factory throughput gains or LLM planning quality. There is no connection to shop-floor equipment.",
            "evidence": [(MFG_SOURCE + "docs/BROWSER_DEMO.md", "Source-pinned setup, replay and limits"), (MFG_SOURCE + "mpa/demo.py", "Session, proposal and confirmed-transition implementation"), (MFG_SOURCE + "mpa/demo_worker.py", "Isolated solver worker"), (MFG + "actions/runs/38217806200", "Exact-source solver, simulation and workflow checks")],
            "demo_label": "Open the recorded replay", "demo_url": "https://luoaini1213.github.io/manufacturing-planning-agent/",
            "strip": [("Observe", "snapshot + outage"), ("Compare", "original / candidate"), ("Confirm", "explicit choice"), ("Continue", "new snapshot")],
        },
        "zh": {
            "title": "重排未来，保留已经发生的工作。",
            "deck": "把设备故障变成候选排程、公平对照与明确确认。求解器和仿真负责算数，工作流负责保留状态。",
            "name": "制造滚动规划",
            "problem": "第 2 小时，设备发生故障，一件任务已经加工了一部分。整份排程直接重写，会抹掉已完成的工作，还可能把已开工任务移到另一台设备。可用的重排必须先保留这两类承诺，再优化剩余时段。",
            "decisions": [
                ("同一状态，两条未来", "SimPy 从同一快照续算原排程与 HiGHS 候选排程。已完成工序被冻结；在制品保留原设备与剩余加工时间。"),
                ("提案经过确认才推进", "先比较完工、未完成、加班与时间线，再明确确认。推进会消费所选提案，第二次故障从真实续算后的新状态开始比较。"),
                ("失败仍有可解释的路径", "求解器在隔离进程中运行；失败或超时不会发布提案，也不会推进执行。不可行或更差的候选继续推荐原排程，过期确认不能把提案应用到另一份快照。"),
            ],
            "demo": "公开页面播放一个自编场景的录制结果。要修改故障并调用实际求解器，请安装仓库依赖后启动本地演练：",
            "command": "python -m mpa.demo --port 8840",
            "steps": ["比较默认 M1 在第 2 至 6 小时停机的结果。", "查看冻结前缀与剩余工作，确认选择并推进到第 3.5 小时。", "比较第二次 M2 故障，再次推进并下载状态转换记录。"],
            "boundary": "这是四件任务、有限时间网格上的合成演练。它验证状态转换和比较约束，不代表工厂产能增益或 LLM 排程能力。演练没有连接生产设备。",
            "evidence": [(MFG_SOURCE + "docs/BROWSER_DEMO.md", "固定源码的安装、回放与边界"), (MFG_SOURCE + "mpa/demo.py", "会话、提案与确认推进实现"), (MFG_SOURCE + "mpa/demo_worker.py", "隔离求解进程"), (MFG + "actions/runs/38217806200", "对应源码的求解、仿真与工作流检查")],
            "demo_label": "打开录制回放", "demo_url": "https://luoaini1213.github.io/manufacturing-planning-agent/",
            "strip": [("观察", "快照 + 故障"), ("比较", "原排程 / 候选"), ("确认", "明确选择"), ("续算", "形成新快照")],
        },
    },
    "ifc-review": {
        "tag": "02 · TYPED ENGINEERING DATA",
        "en": {
            "title": "A reported number needs a type and a unit.",
            "deck": "An IFC precheck that keeps the path from a model property to a finding visible, then separates safe enrichment from work that still needs a designer.",
            "name": "IFC review and enrichment",
            "problem": "The same numeric value can mean millimetres, metres or a dimensionless ratio. Treating every property name as a measurement produces plausible-looking but incorrect checks. A useful report must show what was read and why a conversion or derivation was allowed.",
            "decisions": [
                ("Read the IFC semantics", "Keep the original value, IFC measure type and explicit or project unit. A generic IfcReal with no explicit physical unit does not acquire a length dimension because of its property name. Unknown units remain unresolved."),
                ("Fill only with justified evidence", "Geometry-derived values are written as typed measures with units. Existing nonempty values are preserved, and shared property sets are separated before changing one element."),
                ("Make review navigable", "Filter findings by agency, severity, element identity, property and status. Inspect all findings, export the filtered view, and retain the complete report and derivation evidence."),
            ],
            "demo": "Open the authored three-slab example, compare the before/after reports, inspect a conversion and a deferred field, then download the findings. Rebuild it locally with:",
            "command": "python scripts/report_demo.py --output-dir demos/report-review",
            "steps": ["Start with the original report and locate a specific GlobalId or property.", "Compare the enriched report, including typed writes and unresolved items.", "Open the independent reopen evidence; export the selected findings without changing the original totals."],
            "boundary": "This static report replay uses a small self-authored IFC and illustrative rules; it processes no visitor files. It is not an official regulatory rulebook or an approval decision. Geometry assumptions, absent values and unknown units remain visible for human review.",
            "evidence": [(IFC_SOURCE + "docs/REPORT_REVIEW.md", "Source-pinned workflow, reproduction and limits"), (IFC_SOURCE + "src/ifcsg_precheck/report.py", "Report implementation"), (IFC_SOURCE + "scripts/verify_report_demo.py", "Independent typed STEP readback"), ("https://github.com/LUOaini1213/ifcsg-precheck/actions/runs/38215169532", "Exact-source checks and mutation verification")],
            "demo_label": "Open the report workflow", "demo_url": "https://luoaini1213.github.io/ifcsg-precheck/",
            "strip": [("Read", "value / type / unit"), ("Check", "normalized evidence"), ("Enrich", "typed write / defer"), ("Reopen", "independent readback")],
        },
        "zh": {
            "title": "报告里的数字，需要类型与单位。",
            "deck": "让 IFC 属性到检查结论的路径可见，再把有依据的补全与仍需设计人员处理的事项分开呈现。",
            "name": "IFC 检查与补全",
            "problem": "同一个数值可能表示毫米、米，或无量纲比值。仅靠属性名猜测尺寸，会生成看似合理却错误的检查。可用的报告必须说明读取了什么，以及为什么允许换算或推导。",
            "decisions": [
                ("读取 IFC 语义", "保留原始值、IFC 度量类型与显式或项目单位。未声明物理单位的通用 IfcReal 数值，不会因为属性名像长度就获得长度维度；未知单位继续保持未解决。"),
                ("依据足够才补全", "几何推导结果写为带单位的 typed measure。既有非空值被保留；共享属性集在修改单个构件前先分离。"),
                ("让审阅可以定位", "按机构、严重度、构件标识、属性与状态筛选，查看全部问题，导出当前筛选，同时保留完整报告与推导依据。"),
            ],
            "demo": "打开自编的三个楼板示例，对照补全前后，查看单位转换与暂缓项，再下载检查结果。本地重建命令：",
            "command": "python scripts/report_demo.py --output-dir demos/report-review",
            "steps": ["从原始报告按 GlobalId 或属性定位一项检查。", "对照补全后的报告，查看有类型的写入与未解决项。", "查看独立重新打开模型的复核，导出筛选结果并保留原始总指标。"],
            "boundary": "静态报告回放使用小型自编 IFC 与示意规则，不处理访客文件，也不是正式监管规则库或审批结论。几何假设、缺失值与未知单位会保留，交给人工复核。",
            "evidence": [(IFC_SOURCE + "docs/REPORT_REVIEW.md", "固定源码的流程、复现与边界"), (IFC_SOURCE + "src/ifcsg_precheck/report.py", "报告实现"), (IFC_SOURCE + "scripts/verify_report_demo.py", "独立 typed STEP 读取复核"), ("https://github.com/LUOaini1213/ifcsg-precheck/actions/runs/38215169532", "对应源码的检查与变异验证")],
            "demo_label": "打开报告流程", "demo_url": "https://luoaini1213.github.io/ifcsg-precheck/",
            "strip": [("读取", "数值 / 类型 / 单位"), ("检查", "归一化依据"), ("补全", "typed 写入 / 暂缓"), ("重开", "独立读取复核")],
        },
    },
    "driving": {
        "tag": "03 · RESEARCH TO BROWSER",
        "en": {
            "title": "From a reconstruction experiment to an inspectable scene.",
            "deck": "A small driving scene with reproducible offline evaluation and a browser viewer whose download, preparation, reset and resource lifetime can be inspected.",
            "name": "Driving-scene 3DGS",
            "problem": "A research export is only useful to a visitor if it loads reliably and its limits remain clear. This single eight-second Argoverse 2 clip pairs archived experiments with a separate, lightweight public viewer.",
            "decisions": [
                ("Keep evaluation provenance visible", "Deterministic held-out frames, image and depth baselines, strict sensor-input separation and archived ablations make the experiment inspectable. The original all-scan initialization is retained and labelled for its depth-evaluation leakage."),
                ("Own decoded bytes and lifetime", "HTTP compression can make the encoded Content-Length smaller than the decoded scene. The viewer loads a checked decoded buffer, holds its object URL until preparation finishes, then releases it. Returning to preview removes the renderer frame."),
                ("Let visitors choose the resource cost", "A recorded preview loads first. The scene and renderer load only after Explore in 3D. Download and preparation have distinct states; ready users can move, reset and return to the preview."),
            ],
            "demo": "The public page contains an actual interactive 3D scene. Open the viewer, choose Explore in 3D, drag the scene, reset the view, return to the preview and load it again.",
            "command": None,
            "steps": ["Load the 309,957-Gaussian, 9.9 MB export from the recorded preview.", "Move the camera, reset it and release the renderer by returning to preview.", "Read the source inventory and archived measurements alongside the rendering limits."],
            "boundary": "Single clip, single front camera, static scene representation: moving objects, blur, gaps and off-path floaters remain. The archived 26.56 dB result is offline gsplat evaluation of a selected subset before export quantization, not actual .splat or browser PSNR. Small-screen layout checks do not establish physical-phone performance. Data © 2021 Argo AI, LLC; AV2 derivatives are CC BY-NC-SA 4.0 for non-commercial technical demonstration.",
            "evidence": [(DRIVING + "docs/PUBLIC_VIEWER.md", "Source-pinned viewer and publishing contract"), (DRIVING + "README.md", "Archived experiment, baselines and limitations"), (DRIVING + "site/scene-promise.js", "Decoded-scene and lifetime implementation"), ("https://luoaini1213.github.io/driving-3dgs/source-index.json", "Published asset hash inventory")],
            "demo_label": "Explore the 3D scene", "demo_url": "https://luoaini1213.github.io/driving-3dgs/",
            "strip": [("Experiment", "held-out evidence"), ("Package", "fixed scene + hashes"), ("Explore", "move / reset"), ("Release", "return to preview")],
        },
        "zh": {
            "title": "从重建实验，走到可检查的三维场景。",
            "deck": "把可复现的离线评测与网页查看器连接起来，让下载、准备、恢复视角和资源释放都有可检查的行为。",
            "name": "驾驶场景 3DGS",
            "problem": "研究导出需要稳定加载，也需要把局限讲清楚，访客才能判断其价值。这个 Argoverse 2 单段八秒场景，将历史实验与独立的轻量公开查看器连接起来。",
            "decisions": [
                ("让评测来源可见", "确定性留出帧、图像与深度基线、严格传感器输入隔离和历史消融支持复查。原始使用全部扫描的初始化仍保留，并标明其对深度评测构成泄漏。"),
                ("管理解码字节与生命周期", "HTTP 压缩可能让编码 Content-Length 小于解码后的场景。查看器使用已校验的解码 buffer，准备完成后再释放 object URL；返回预览会移除渲染 iframe。"),
                ("由访客选择资源开销", "先显示录制预览，点击 Explore in 3D 后才加载场景和渲染器。下载与准备有独立状态；准备完成后可以移动、复位并返回预览。"),
            ],
            "demo": "公开页面提供实际可交互的三维场景。打开查看器，点击 Explore in 3D，拖动场景、恢复视角、返回预览，再次加载。",
            "command": None,
            "steps": ["从录制预览加载 309,957 个高斯、约 9.9 MB 的导出资产。", "移动相机、恢复视角，再通过返回预览释放渲染器。", "结合源码清单、历史评测与渲染局限判断结果。"],
            "boundary": "单段视频、单个前视相机、静态场景表示：动态物体、模糊、空洞和偏离轨迹的漂浮物仍存在。历史 26.56 dB 来自导出量化前筛选子集的离线 gsplat 评测，不是实际 .splat 或浏览器 PSNR。小屏布局检查不代表实体手机性能。Data © 2021 Argo AI, LLC；AV2 衍生物按 CC BY-NC-SA 4.0 提供，仅作非商业技术展示。",
            "evidence": [(DRIVING + "docs/PUBLIC_VIEWER.md", "固定源码的查看器与发布说明"), (DRIVING + "README.md", "历史实验、基线与局限"), (DRIVING + "site/scene-promise.js", "解码场景与生命周期实现"), ("https://luoaini1213.github.io/driving-3dgs/source-index.json", "已发布资产哈希清单")],
            "demo_label": "探索三维场景", "demo_url": "https://luoaini1213.github.io/driving-3dgs/",
            "strip": [("实验", "留出帧依据"), ("打包", "固定资产 + 哈希"), ("探索", "移动 / 复位"), ("释放", "返回预览")],
        },
    },
}

FACTS = {
    'manufacturing': {
        'en': [('2/4 → 4/4', 'First-outage comparison · synthetic units completed'), ('2 events', 'Confirmed transitions in the recorded exercise'), ('0 model calls', 'HiGHS and SimPy compute this example')],
        'zh': [('2/4 → 4/4', '首次故障对照 · 合成任务完工数'), ('2 次事件', '录制演练中的确认状态转换'), ('0 次模型调用', '本例由 HiGHS 与 SimPy 计算')],
    },
    'ifc-review': {
        'en': [('250 mm → 0.25 m', 'Normalized evidence; original 250 mm property retained'), ('9 writes', 'Traceable fills in the authored fixture'), ('1 deferred', 'Unknown unit kept for review')],
        'zh': [('250 mm → 0.25 m', '归一化结果；原 250 mm 属性被保留'), ('9 次写入', '自编示例中可追溯的补全'), ('1 项暂缓', '未知单位保留待复核')],
    },
    'driving': {
        'en': [('1 clip · ~8 s', 'Single front camera · Argoverse 2'), ('309,957', 'Gaussians in the published export'), ('9,918,624 bytes', 'Exact decoded scene size')],
        'zh': [('1 段 · 约 8 秒', '单前视相机 · Argoverse 2'), ('309,957', '公开导出中的高斯数'), ('9,918,624 字节', '场景解码后的精确大小')],
    },
}


def filename(slug, lang):
    return slug + ("-zh" if lang == "zh" else "") + ".html"


def shell(title, description, lang, paired, filename_, body):
    zh = lang == "zh"
    home = "../index.html" if zh else "../en.html"
    hub = "index.html" if zh else "en.html"
    return f'''<!doctype html>
<html lang="{'zh-CN' if zh else 'en'}">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} | Wenjie Luo</title><meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="https://luoaini1213.github.io/cases/{filename_}">
<link rel="alternate" hreflang="{'en' if zh else 'zh-CN'}" href="https://luoaini1213.github.io/cases/{paired}">
<link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="case.css">
<script src="case.js" defer></script>
</head>
<body class="case-page">
<a class="skip-link" href="#content">{'跳到主要内容' if zh else 'Skip to content'}</a>
<nav class="case-nav" aria-label="{'主导航' if zh else 'Main navigation'}"><div>
<a class="case-logo" href="{home}"><span class="logo-mark" aria-hidden="true"></span>Wenjie Luo</a>
<span class="case-nav-links"><a href="{hub}">{'工程案例' if zh else 'Engineering cases'}</a><a href="../resumes/">{'简历' if zh else 'CVs'}</a><a class="case-language" href="{paired}" hreflang="{'en' if zh else 'zh-CN'}">{'EN' if zh else '中文'}</a>
<button class="case-theme" type="button" aria-label="{'切换主题' if zh else 'Switch theme'}" aria-pressed="false">{'主题' if zh else 'Theme'} <span aria-hidden="true">◐</span></button></span>
</div></nav>
<main id="content" class="case-main">{body}</main>
<footer class="case-footer"><span>Wenjie Luo · {'个人工程项目' if zh else 'Personal engineering projects'}</span><a href="{home}#contact">{'联系我' if zh else 'Contact'}</a><span>{'案例更新' if zh else 'Case update'} · 2026-10-12</span></footer>
</body></html>
'''


def case_page(slug, lang):
    d = CASES[slug][lang]
    zh = lang == "zh"
    headings = ["问题", "实现决策", "亲自检查", "适用边界", "来源与验证"] if zh else ["The problem", "Implementation decisions", "Inspect it yourself", "Scope and limits", "Sources and verification"]
    strip = ''.join(f'<li><b>{escape(a)}</b><span>{escape(b)}</span></li>' for a, b in d['strip'])
    decisions = ''.join(f'<article class="decision"><span class="decision-number">0{i}</span><div><h3>{escape(a)}</h3><p>{escape(b)}</p></div></article>' for i, (a, b) in enumerate(d['decisions'], 1))
    steps = ''.join(f'<li>{escape(s)}</li>' for s in d['steps'])
    evidence = ''.join(f'<li>{link(u, label)}<span aria-hidden="true"> ↗</span></li>' for u, label in d['evidence'])
    facts = ''.join(f'<div><strong>{escape(value)}</strong><span>{escape(label)}</span></div>' for value, label in FACTS[slug][lang])
    command = f'<pre><code>{escape(d["command"])}</code></pre>' if d['command'] else ''
    picture = '''<figure class="scene-preview"><img src="https://luoaini1213.github.io/driving-3dgs/assets/preview.jpg" width="960" height="540" loading="lazy" alt="Recorded 3DGS scene preview from the archived driving reconstruction"><figcaption>Recorded preview · Data © 2021 Argo AI, LLC · <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a> · <a href="https://luoaini1213.github.io/driving-3dgs/NOTICES.txt">Asset attribution</a></figcaption></figure>''' if slug == 'driving' else ''
    body = f'''<header class="case-hero"><p class="case-kicker">{CASES[slug]['tag']}</p><h1>{escape(d['title'])}</h1><p class="case-deck">{escape(d['deck'])}</p><div class="case-actions">{link(d['demo_url'], d['demo_label'])}{link('#evidence', '查看源码依据' if zh else 'Read the evidence')}</div></header>
<ol class="flow-strip" aria-label="{'处理流程' if zh else 'Workflow'}">{strip}</ol>
<div class="case-facts" aria-label="{'示例范围与记录' if zh else 'Example scope and recorded evidence'}">{facts}</div>
{picture}
<div class="case-layout"><aside class="case-toc" aria-label="{'本页导航' if zh else 'On this page'}">{''.join(link('#'+key,label) for key,label in zip(['problem','decisions','demo','limits','evidence'],headings))}</aside><div>
<section id="problem" class="case-section"><h2>{headings[0]}</h2><p>{escape(d['problem'])}</p></section>
<section id="decisions" class="case-section"><h2>{headings[1]}</h2>{decisions}</section>
<section id="demo" class="case-section"><h2>{headings[2]}</h2><p>{escape(d['demo'])}</p>{command}<ol class="inspection-steps">{steps}</ol><p>{link(d['demo_url'], d['demo_label']+' →')}</p></section>
<section id="limits" class="case-section case-limits"><h2>{headings[3]}</h2><p>{escape(d['boundary'])}</p></section>
<section id="evidence" class="case-section"><h2>{headings[4]}</h2><ul class="evidence-links">{evidence}</ul><p class="source-note">{'源码和 CI 链接用于检查实现与复现状态；测试通过不等于部署成功或实际业务收益。' if zh else 'Source and CI links let you inspect the implementation and reproducibility. Passing checks do not establish deployment success or business gains.'}</p></section>
</div></div>
<nav class="next-cases" aria-label="{'其他案例' if zh else 'Other cases'}">{''.join(link(filename(key,lang), CASES[key][lang]['name']+' →') for key in CASES if key!=slug)}</nav>'''
    return shell(d['name'], d['deck'], lang, filename(slug, 'en' if zh else 'zh'), filename(slug, lang), body)


def hub_page(lang):
    zh = lang == 'zh'
    title = '把技术实现变成可检查的工作流。' if zh else 'Engineering work you can inspect.'
    deck = '三个个人项目，分别展示状态续算、有类型的工程数据，以及研究结果的浏览器交付。每项都有演示、源码与适用边界。' if zh else 'Three personal projects: stateful replanning, typed engineering data and a research result delivered to the browser. Each connects a demonstration to its implementation and limits.'
    labels = [('状态与决策', 'State and decisions'), ('语义与复核', 'Semantics and readback'), ('研究与交付', 'Research and delivery')]
    rows = ''
    for i, (slug, d) in enumerate(CASES.items()):
        text = d[lang]
        process = ' → '.join(a for a, _ in text['strip'])
        rows += f'''<article class="case-row"><div class="case-row-label"><span>0{i+1}</span><p>{labels[i][0 if zh else 1]}</p></div><div><h2>{link(filename(slug,lang), text['name'])}</h2><p>{escape(text['deck'])}</p><p class="row-flow">{escape(process)}</p><a class="row-open" href="{filename(slug,lang)}">{'阅读案例' if zh else 'Read the case'} <span aria-hidden="true">↗</span></a></div></article>'''
    body = f'''<header class="case-hero hub-hero"><p class="case-kicker">SELECTED ENGINEERING CASES</p><h1>{title}</h1><p class="case-deck">{deck}</p></header><div class="case-rows">{rows}</div><section class="hub-note"><h2>{'从演示走到依据' if zh else 'From demonstration to evidence'}</h2><p>{'制造公开页是录制回放，本地演练才调用实际求解器；IFC 公开页使用自编示例；3DGS 页面加载实际场景。案例各自说明输入、验证方式和限制，历史简历与实验记录保持原样。' if zh else 'Manufacturing offers a recorded public replay and an actual local solver. IFC uses an authored example. The 3DGS viewer loads the actual scene. Each case explains its inputs, verification and limits; existing CVs and archived experiments remain intact.'}</p><a href="../resumes/">{'按岗位查看简历与项目证据' if zh else 'Choose a role-specific CV and its evidence'} →</a></section>'''
    name, paired = ('index.html', 'en.html') if zh else ('en.html', 'index.html')
    return shell('工程案例' if zh else 'Engineering cases', deck, lang, paired, name, body)


def build(check=False):
    outputs = {'index.html': hub_page('zh'), 'en.html': hub_page('en')}
    outputs.update({filename(slug, lang): case_page(slug, lang) for slug in CASES for lang in ('en', 'zh')})
    folder = ROOT / 'cases'
    folder.mkdir(exist_ok=True)
    for name, content in outputs.items():
        target = folder / name
        if check:
            if not target.exists() or target.read_text(encoding='utf-8') != content:
                raise SystemExit(f'Generated case differs: {name}; run python scripts/build_cases.py')
        else:
            target.write_text(content, encoding='utf-8', newline='\n')
    print(f'{"Verified" if check else "Built"} {len(outputs)} bilingual case pages')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
