#!/usr/bin/env python3
"""重新生成 manifest.json：扫描 packs/，计算 sha256/sizeBytes。

每个 pack 可在文件顶层带一个可选的 `_meta` 块来自描述清单信息：
    "_meta": {
      "version": 1,
      "title":   {"zh": "中文标题", "en": "English Title"},
      "summary": {"zh": "一句话简介", "en": "One-line summary"},
      "accessLevel": "free",
      "contentTypes": ["stories"]
    }
App 端 ContentPackDocument 会忽略未知的 `_meta` 字段（Codable 默认忽略未知键），
因此 `_meta` 既能让 manifest 自动获得双语标题，又不影响内容包本体被 App 消费。

元数据优先级：pack 内 `_meta` > 现有 manifest 中同 id 的条目 > 默认值。
这样既能给新包自动生成双语标题，也不会破坏既有已发布包（它们无 `_meta`，沿用现有 manifest 值）。

发布正式内容时用 CONTENT_REF=<content-tag> 固化包 URL，例如：
    CONTENT_REF=content-2026-06-24-1 python3 Scripts/build_manifest.py
"""
import json, hashlib, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GH_OWNER, GITEE_OWNER, REPO = "zhongaiyemaozi", "zhongaiyemaozi_admin", "clover-content"
CONTENT_REF = os.environ.get("CONTENT_REF", "main")

# App 当前接受的内容类型白名单（与 ContentPackContentType 对齐）。
ACCEPTED_CONTENT_TYPES = {
    "learning.categories", "quiz.packs", "stroke.order", "stories",
    "voice.practice", "writing.practice", "game.tracing", "game.numberConnect",
    "game.storySorting", "game.coloring", "game.dailyChallenge",
    "widget.dailyWords", "great.figures",
}

# payload 键 -> contentType，用于在缺省时从包体推断 contentTypes。
PAYLOAD_KEY_TO_TYPE = {
    "quizPacks": "quiz.packs",
    "strokeOrderCharacters": "stroke.order",
    "stories": "stories",
    "voicePracticeItems": "voice.practice",
    "writingPracticeItems": "writing.practice",
    "tracePrompts": "game.tracing",
    "numberConnectBoards": "game.numberConnect",
    "storySortingStoryIDs": "game.storySorting",
    "coloringPages": "game.coloring",
    "dailyChallengeSets": "game.dailyChallenge",
    "widgetDailyWords": "widget.dailyWords",
    "greatFigures": "great.figures",
    "learningCategories": "learning.categories",
}


def infer_content_types(doc):
    types = []
    if doc.get("categories"):
        types.append("learning.categories")
    payloads = doc.get("payloads") or {}
    for key, value in payloads.items():
        if value and key in PAYLOAD_KEY_TO_TYPE:
            t = PAYLOAD_KEY_TO_TYPE[key]
            if t not in types:
                types.append(t)
    return types


manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
known = {p["id"]: p for p in manifest.get("packs", [])}

packs = []
for path in sorted((ROOT / "packs").glob("*.json")):
    pid = path.stem
    raw = path.read_bytes()
    doc = json.loads(raw)  # schema sanity
    meta = doc.get("_meta", {})
    prev = known.get(pid, {})

    content_types = (
        meta.get("contentTypes")
        or doc.get("contentTypes")
        or prev.get("contentTypes")
        or infer_content_types(doc)
    )
    unsupported = [t for t in content_types if t not in ACCEPTED_CONTENT_TYPES]
    if unsupported:
        raise SystemExit(f"[{pid}] unsupported contentTypes: {unsupported}")

    entry = {
        "id": pid,
        "version": meta.get("version") or prev.get("version", 1),
        "title": meta.get("title") or prev.get("title") or {"zh": pid, "en": pid},
        "summary": meta.get("summary") if meta.get("summary") is not None else prev.get("summary"),
        "sizeBytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "accessLevel": meta.get("accessLevel") or prev.get("accessLevel", "free"),
        "contentTypes": content_types,
        "urls": {
            "cn": f"https://gitee.com/{GITEE_OWNER}/{REPO}/raw/{CONTENT_REF}/packs/{pid}.json",
            "global": f"https://raw.githubusercontent.com/{GH_OWNER}/{REPO}/{CONTENT_REF}/packs/{pid}.json",
            "cdn": f"https://fastly.jsdelivr.net/gh/{GH_OWNER}/{REPO}@{CONTENT_REF}/packs/{pid}.json",
            "gcore": f"https://gcore.jsdelivr.net/gh/{GH_OWNER}/{REPO}@{CONTENT_REF}/packs/{pid}.json",
        },
    }
    packs.append(entry)

manifest["packs"] = packs
(ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"manifest.json updated with {len(packs)} packs using CONTENT_REF={CONTENT_REF}")
for p in packs:
    print(f"  - {p['id']}: v{p['version']} {p['contentTypes']} ({p['sizeBytes']}B)")
