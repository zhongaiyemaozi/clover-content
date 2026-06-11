# clover-content

四叶草乐园（Clover Early Learning）官方内容仓库 — 通过多源 CDN 向 App 分发免费学习内容包。

## 结构

```
manifest.json      # 内容清单：包列表 + sha256 + 版本公告（App 多源拉取）
packs/<id>.json    # 内容包本体（LearningCatalog Schema，双语）
Scripts/           # manifest 生成脚本
```

## 发布流程

1. 编辑/新增 `packs/*.json`（包内容变更必须把 manifest 中对应 `version` +1）
2. 运行 `python3 Scripts/build_manifest.py` 重新生成 manifest（自动计算 sha256/sizeBytes）
3. `git push origin main` 并同步推送 Gitee 镜像：`git push gitee main`

## 分发源

- 大陆：`fastly.jsdelivr.net/gh/...` → `gitee.com/.../raw/main/...`
- 海外：`raw.githubusercontent.com/.../main/...`

所有内容为开发者自审静态学习内容（App Store 儿童类目合规），无 UGC、无外链、无统计。
