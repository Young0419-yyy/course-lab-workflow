# course-lab-workflow

按照课程 PDF、实验数据与原有报告模板完成实验的 Codex skill。

## 支持的任务

- 按 PDF 的代码与中文注释风格生成简洁的 Jupyter Notebook。
- 从已完成 Notebook 的真实输出填写实验报告。
- 完整完成 Notebook 和报告，并在实验步骤中为用户留出截图空白。
- 根据新实验选择分类、回归、聚类或关联规则等方法，避免沿用上一实验的字段和参数。

## 默认要求

- 实验依赖放在由本机 Python 创建的实验虚拟环境中。
- 默认不额外安装 Jupyter 服务或内核包来保存 Notebook 输出。
- 使用命令及文件核验 VS Code 相关配置；确需额外检查时可委派给可用的 `gpt-6.1-terra`。
- 实验报告保留原模板格式，内容简洁，不粘贴代码和环境安装过程。
- 按实际步骤预留截图位置；结果没有改善时如实说明。

## 安装

将本仓库下载或克隆到个人技能目录，目录结构应为：

```text
~/.codex/skills/course-lab-workflow/SKILL.md
```

例如：

```sh
git clone https://github.com/Young0419-yyy/course-lab-workflow.git ~/.codex/skills/course-lab-workflow
```

## 使用

在 Codex 中提供实验文件夹，并说明需要的成果，例如：

> 使用 $course-lab-workflow 完成实验8文件夹，按照 PDF 生成 Notebook，并填写原格式实验报告。

> 使用 $course-lab-workflow，只根据实验9的 Notebook 填写报告，保留截图空间。

## 文件结构

```text
SKILL.md
references/
  notebook.md
  report-template.md
scripts/
  execute_notebook.py
evals/
  evals.json
```

`execute_notebook.py` 是保存普通 Python Notebook 真实输出的辅助工具，支持文本、表格和 Matplotlib 图像；执行失败时保留原文件。它不支持 IPython 魔法命令、Shell 单元格、顶层异步或交互控件。

`evals/evals.json` 包含三种流程适配情景，属于方案检查，不代表这些示例实验已完成端到端运行。
