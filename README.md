# 悉尼资讯小红书自动化（第0阶段：每周新鲜事周报）

这套代码把“采集、选题、写稿、配图、核实、出图、审核、改稿、发布包”串成一条流水线。主编只需要看审核页、写批注、手机发布。

所有生成的内容都是草稿，默认需要主编审核和修改；系统的设计重点是让修改方便，而不是假设一次就对。

## 每周怎么用

```
python run.py collect            # 每天跑一次：抓信息源，更新线索库
python run.py plan --dry         # 先看看本周会入选哪些线索
python run.py plan               # 选题、写稿、配图、核实、出图，生成审核页
```

然后打开 `data/issues/001/review.html` 看卡片和核实结果，在 `data/issues/001/comments.yaml` 里写批注：

```yaml
条目:
  0: {名称: 封面、标题与正文, 状态: 通过, 批注: ""}
  3: {名称: Enmore 街头广场拟永久保留, 状态: 需修改, 批注: "标题太长，改成两行"}
  7: {名称: Kiddo Coffee, 状态: 撤下, 批注: ""}
```

```
python run.py revise --issue 1   # 按批注改稿并重新出图（旧版本自动保留为 issue.v1.json）
python run.py publish --issue 1 --title 0   # 生成手机发布包：图片按顺序编号，post.txt 里是标题、正文、标签
```

想直接改字，也可以打开 `data/issues/001/issue.json` 手动改，再运行 `python run.py render --issue 1` 重新出图。

用 Notion 审核的话，把 `review` 和 `revise` 加上 `--notion` 即可（需要先建好数据库，见下文）。

## 想改什么，改哪里

| 想改的东西 | 文件 |
| --- | --- |
| 覆盖哪些街区、片区 | `config/regions.yaml` |
| 地图上街区的位置 | `config/suburb_coords.yaml` |
| 信息源、开关某个来源 | `config/sources.yaml` |
| 时效窗口（60天、14天）、每期条数、发布日 | `config/settings.yaml` |
| 选图偏好、模型名、字体位置 | `config/settings.yaml` |
| 语气、禁用词、写作规范 | `prompts/style_guide.md` |
| 主编沉淀下来的规则 | `prompts/editor_rules.md` |
| 写稿、抽取、核实、改稿的具体指令 | `prompts/write_weekly.md` 等 |
| 某张卡片的版式 | 在 `issue.json` 里给那一条加 `"layout": "photo_poster"` |
| 版式的样子 | `src/xhs/render/layouts.py` |
| 版式怎么分配、轮换 | `src/xhs/render/planner.py` |

改稿时系统会把“以后每期都适用”的批注提炼成规则，放进 `editor_rules.md` 的“待确认”。你确认后把它挪到“已生效”，下一期写稿就会遵守。

## 版式

| 名称 | 用在什么内容 |
| --- | --- |
| cover | 封面，杂志目录式 |
| map | 本期地图，以 CBD 为中心画距离圈 |
| clipping | 报纸剪报，有生效日期的社区动态 |
| before_after | 前后对比，“某些地方变了”的消息 |
| number_poster | 大数字海报，有关键数字的内容 |
| qa_cards | 问答卡，政策和意见征集 |
| photo_poster | 照片海报，有照片的新店 |
| band_poster | 色带海报，没有照片但有背景故事的新店 |
| polaroids | 拍立得拼贴，最多三家小店合在一张 |
| editor | 编辑判断 |

同一版式每期最多出现两次，相邻两张不会是同一版式。

## 第一次运行

```
pip install -r requirements.txt
cp .env.example .env      # 填 ANTHROPIC_API_KEY
python run.py demo        # 不联网、不调用模型，用第一期数据测试出图
python -m pytest tests    # 离线跑通整条流水线
```

字体：需要 Noto Sans CJK、Noto Serif CJK、Inter Display、Lora。在 Mac 上可以用 `brew install --cask font-noto-sans-cjk font-noto-serif-cjk font-inter font-lora` 安装，再把 `config/settings.yaml` 里的字体路径改成实际位置。

## Notion 审核数据库

新建一个数据库，属性如下，然后把集成（Integration）加到这个数据库，并在 `.env` 里填 `NOTION_TOKEN` 和数据库 ID：

名称（标题）、期数（数字）、编号（数字）、状态（单选：待审、通过、需修改、撤下）、批注（文本）、卡片文字（文本）、核实问题（文本）

## 定时运行

在一台一直开着的电脑或小服务器上用 cron：

```
0 7 * * *   cd /path/to/sydney_xhs && python run.py collect >> data/collect.log 2>&1
0 7 * * 1   cd /path/to/sydney_xhs && python run.py plan >> data/plan.log 2>&1
```

每天早上采集，周一早上出当周的周报，主编周二审稿。

## 目前的状态（需要你知道的）

- 已验证：出图引擎、版式分配、片区判断、时效筛选、规则检查，以及用假数据跑通的整条流水线（`tests/`）
- 还没在真实环境跑过：
  - 真实网站的采集。开发环境的网络不能访问这些网站，`config/sources.yaml` 里标了 `verify_url: true` 的链接是按网站结构推测的，第一次运行前请在浏览器里确认，并看一下 `collect` 的输出是否正常
  - 真实模型的写稿效果。提示词写好了，但第一期用真实数据跑出来，大概率需要你按批注调几轮
  - Notion 同步。代码按 Notion 公开接口写的，需要你建好数据库后实测
- 规划数据（开发申请）接口默认关闭，第2阶段再接
