#!/usr/bin/env python3
"""重新生成 manifest.json：扫描 packs/，计算 sha256/sizeBytes，保留 announcement 与各包 version/title/summary。

发布正式内容时使用 CONTENT_REF=<content-tag> 固化包 URL，例如：
CONTENT_REF=content-2026-06-15-1 python3 Scripts/build_manifest.py
"""
import json, hashlib, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GH_OWNER, GITEE_OWNER, REPO = "zhongaiyemaozi", "zhongaiyemaozi_admin", "clover-content"
CONTENT_REF = os.environ.get("CONTENT_REF", "main")

manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
known = {p["id"]: p for p in manifest["packs"]}

packs = []
for path in sorted((ROOT / "packs").glob("*.json")):
    pid = path.stem
    data = path.read_bytes()
    json.loads(data)  # schema sanity
    prev = known.get(pid, {})
    packs.append({
        "id": pid,
        "version": prev.get("version", 1),
        "title": prev.get("title", {"zh": pid, "en": pid}),
        "summary": prev.get("summary"),
        "sizeBytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "accessLevel": prev.get("accessLevel", "free"),
        "urls": {
            "cn": f"https://gitee.com/{GITEE_OWNER}/{REPO}/raw/{CONTENT_REF}/packs/{pid}.json",
            "global": f"https://raw.githubusercontent.com/{GH_OWNER}/{REPO}/{CONTENT_REF}/packs/{pid}.json",
            "cdn": f"https://fastly.jsdelivr.net/gh/{GH_OWNER}/{REPO}@{CONTENT_REF}/packs/{pid}.json",
            "gcore": f"https://gcore.jsdelivr.net/gh/{GH_OWNER}/{REPO}@{CONTENT_REF}/packs/{pid}.json",
        },
    })

manifest["packs"] = packs
(ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"manifest.json updated with {len(packs)} packs using CONTENT_REF={CONTENT_REF}")
