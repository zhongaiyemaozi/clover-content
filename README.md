# clover-content

四叶草乐园（Clover Early Learning）官方内容仓库 — 通过多源 CDN 向 App 分发免费学习内容包。

## 结构

```
manifest.json      # 内容清单：包列表 + sha256 + 版本公告（App 多源拉取）
packs/<id>.json    # 内容包本体（LearningCatalog Schema，双语）
Scripts/           # manifest 生成脚本
```

## 发布流程

1. 选定内容 tag，例如 `content-2026-06-15-1`；同一天多次发布递增最后一位。
2. 编辑/新增 `packs/*.json`（已有包内容变更必须把 manifest 中对应 `version` +1）。
3. 运行 `CONTENT_REF=content-2026-06-15-1 python3 Scripts/build_manifest.py` 重新生成 manifest（自动计算 sha256/sizeBytes，并把包 URL 固化到该 tag）。
4. 提交变更：`git commit -m "feat: ..."`。
5. 在同一个提交上打 tag：`git tag content-2026-06-15-1`。
6. 推送 GitHub 和 Gitee：`git push origin main --tags`、`git push gitee main --tags`。
7. 验证远端 `manifest.json` 可见新包，并抽查至少一个 tag URL 可下载。

说明：`manifest.json` 保持在 `main` 作为最新索引，App 进入内容中心会重新拉取；`packs/*.json` 的下载 URL 使用内容 tag，保证包文件不可变、可校验、可回滚。

## 分发源

- manifest：`fastly.jsdelivr.net/gh/...@main/manifest.json` → `gitee.com/.../raw/main/manifest.json` → `raw.githubusercontent.com/.../main/manifest.json`
- 内容包：manifest 内的 `cn/global/cdn/gcore` URL 指向同一个内容 tag

所有内容为开发者自审静态学习内容（App Store 儿童类目合规），无 UGC、无外链、无统计。
