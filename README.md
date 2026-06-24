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

---

## 内容包自描述（`_meta`）约定（2026-06）

新增包可在 JSON 顶层放一个可选的 `_meta` 块，`build_manifest.py` 会据此自动生成 manifest 的双语标题/摘要/版本/contentTypes：

```json
{
  "_meta": {
    "version": 1,
    "title":   {"zh": "中文标题", "en": "English Title"},
    "summary": {"zh": "一句话简介", "en": "One-line summary"},
    "accessLevel": "free",
    "contentTypes": ["stories"]
  },
  "schemaVersion": 2,
  "payloads": { "...": [] }
}
```

App 端解码会忽略 `_meta`（未知键），不影响内容消费。既有无 `_meta` 的包沿用现有 manifest 中的标题。

## 内容类型覆盖状态（每类型 ≥5 个双语包，共 72 包）

全部 13 个内容类型均已补齐至 ≥5 个双语包，且经 App 端真实 `ContentPackDocument` 解码校验通过：

| contentType | 包数 |
|---|---|
| learning.categories | 12（festival×3, core×4, space, ocean, jobs, weather, body）|
| stories | 5（fables, fables-two, fairy/bedtime, animals, china）|
| great.figures | 5（world-plus, inventors, scientists, explorers, artists）|
| quiz.packs | 5（animals, colors, numbers, shapes, fruits）|
| voice.practice | 5（en-words, en-phrases, zh-words, zh-sentences, zh-animals）|
| stroke.order | 5（numbers, nature, body, people, basic — 取自内置真实笔顺数据的主题复习包）|
| writing.practice | 5（numbers-1/2, basic-1/2/3）|
| game.tracing | 5（letters×3, numbers, chinese）|
| game.numberConnect | 5（shapes-1/2, house, heart, boat）|
| game.storySorting | 5（对应 5 组故事 id）|
| game.coloring | 5（animals, nature, vehicles, food, festival）|
| game.dailyChallenge | 5（add-10, sub-10, add-20, mixed-20, mixed-50）|
| widget.dailyWords | 5（animals, nature, food, school, body）|

> `stroke.order` 复习包使用内置 `strokes_basic.json` 的真实 makemeahanzi 几何（渲染正确，但与内置 183 字重叠，主要作主题复习；要新增内置之外的字需引入 makemeahanzi 全量数据）。
> `quiz.packs` 标题为中英合并文本（QuizPack.title 为单字符串）；题目本体来自被引用的双语学习分类。

## 发布时序注意

- `great.figures` 内容类型需要支持它的 App 版本（v3.3+）。在该版本上架前，**暂不要**给只含 `great.figures` 的包打正式 tag 发布到 `main`，否则旧版本 App 下载会安装失败（静默回退，不影响其他功能）。
- 正式发布务必用 `CONTENT_REF=content-YYYY-MM-DD-N` 重新生成 manifest 后再 commit + 打同名 tag + 推送 GitHub/Gitee。
