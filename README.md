# Blog-Application-Design

一个基于 **Django** 的多用户博客系统：支持注册/登录、文章发布与草稿、标签体系、搜索+排序+分页组合查询、Markdown（含代码高亮）安全渲染、RSS 输出，以及深色/浅色主题切换。

> 设计重点：把“内容渲染安全边界”和“检索参数组合复杂度”做成可解释、可复用的工程结构。

---

## Screenshots / Diagrams

### System Workflow（工作流程图）
<p align="center">
  <img src="docsdocs/images/workflow_flowchart.png" width="950" alt="System Workflow">
</p>

### Project Structure（项目文件目录图）
<p align="center">
  <img src="docsdocs/images/project_structure.png" width="950" alt="Project Structure">
</p>

### Markdown Rendering + Sanitization（Markdown 渲染与安全清洗流程）
<p align="center">
  <img src="docsdocs/images/markdown_pipeline.png" width="950" alt="Markdown Pipeline">
</p>

---

## Features

- 用户系统：注册/登录/登出（Django 内置认证视图 + 自定义注册）
- 文章：创建/编辑/删除（仅作者可操作），支持草稿（`is_published`）
- 标签：逗号输入自动去重、自动创建 Tag，并用 slug 做可读 URL
- 列表检索：搜索（标题/正文）、最新/最旧排序切换、分页；参数可组合且不丢失
- 内容渲染：Markdown → HTML → Bleach 白名单清洗 → 安全输出；支持代码高亮（Pygments CSS）
- RSS：输出最近 20 篇已发布文章，item 描述为摘要
- UI：Bootstrap + 深色/浅色主题切换（localStorage 持久化，支持跟随系统）

---

## Quickstart

### 1) 环境准备
建议 Python 3.13
Django>=6.0
markdown
bleach
Pygments
