# Claude Code 使用指南

本文说明如何在 Claude Code 中使用 `math-modeling-solver`。

## 安装

从仓库根目录运行：

```bash
python3 scripts/install_skill.py --target claude
```

安装位置：

```text
~/.claude/skills/math-modeling-solver
```

如果你同时使用 Codex 和 Claude Code：

```bash
python3 scripts/install_skill.py --target both
```

## 推荐启动 Prompt

从零开始：

```text
使用 math-modeling-solver skill 帮我解这道数学建模题。请先初始化 CUMCM_Workspace，解析题目和附件，然后在模型路线选择处停下来让我确认。
```

继续已有项目：

```text
使用 math-modeling-solver skill 继续当前项目。请先读取 CUMCM_Workspace/state/pipeline.json 的状态，再告诉我当前阶段和我需要确认什么。
```

只做路线设计：

```text
使用 math-modeling-solver skill 先分析题目并给出 2-3 条建模路线。不要开始求解，等我确认路线。
```

论文前检查：

```text
使用 math-modeling-solver skill 检查当前论文草稿是否能进入 final_compile。请运行 verification gate 和 paper-audit，并列出阻塞项。
```

## Claude Code 下的使用习惯

- 把题目、附件和原始数据放在项目目录里，再让 Claude Code 初始化工作区。
- 不要直接要求“生成最终论文”；先让 skill 走 `model_route_review` 和 `assumption_review`。
- 到 `result_review` 时，只批准你确认可信的结果进入论文。
- 如果 `paper-audit` 失败，把失败信息贴给 Claude Code，让它修复对应阶段，不要手动绕过门禁。

## 常见问题

### Claude Code 没有自动使用这个 skill

明确在 prompt 里写：

```text
使用 math-modeling-solver skill ...
```

### 找不到工作区

在项目根目录运行或让 Claude Code 运行：

```bash
python3 ~/.claude/skills/math-modeling-solver/scripts/setup_workspace.py --project .
```

### 已经在 Codex 安装了，Claude Code 还需要安装吗？

需要。Codex 和 Claude Code 读取的 skills 目录不同。可以运行：

```bash
python3 ~/.codex/skills/math-modeling-solver/scripts/install_skill.py --target claude
```

### 会不会影响 Codex 版本？

不会。安装脚本只是把同一套 skill 文件复制到 Claude Code 的 skills 目录，核心脚本和工作区结构保持一致。
