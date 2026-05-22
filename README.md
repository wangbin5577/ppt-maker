# PPT Maker — 基于公司模板的PPT自动生成工具

将Markdown格式的提示词自动转换为基于公司模板的PowerPoint演示文稿。

## 核心思路

```
提示词.md  →  md2ppt.py  →  公司模板PPT
```

- 提示词可以自己写，也可以让AI（ChatGPT、Copilot等）按格式规范生成
- 程序纯本地运行，不需要联网，不调用任何API
- 支持任意 .pptx 模板，自动检测布局类型
- 支持中英文两种提示词格式

## 目录结构

```
PPT maker/
├── README.md                  项目说明
├── md2ppt.py                  核心程序（命令行）
├── app.py                     Web UI（Streamlit）
├── 启动Web UI.bat             双击启动Web界面
├── LR模板.pptx                默认模板
├── PPT提示词格式规范.md         格式约定（给AI看）
├── examples/                  示例提示词
│   ├── ppt_prompt_en.md       英文版
│   └── ppt_prompt_cn.md       中文版
├── output/                    生成的PPT输出
└── archive/                   旧文件归档
```

## 快速开始

### 1. 安装依赖

```bash
python -m pip install python-pptx streamlit
```

### 2. 准备提示词

按照 `PPT提示词格式规范.md` 的格式编写内容，或者把格式规范发给AI让它帮你生成。

### 3. 生成PPT

命令行方式：

```bash
# 使用默认模板（LR模板.pptx）
python md2ppt.py 提示词.md

# 指定输出路径
python md2ppt.py 提示词.md output/演示.pptx

# 使用其他模板
python md2ppt.py 提示词.md output/演示.pptx --template 其他模板.pptx
```

Web UI 方式：

```bash
streamlit run app.py
```

或双击 `启动Web UI.bat`，打开浏览器上传模板和提示词即可。

## 支持的页面布局

| 标记 | 用途 | 说明 |
|------|------|------|
| `[cover]` | 封面页 | 标题 + 副标题 |
| `[content]` | 标准正文页 | 标题 + bullet列表 |
| `[content_spacious]` | 大内容区正文页 | 内容多或有代码块时自动使用 |
| `[comparison]` | 双栏对比页 | 左右两栏对比 |
| `[table]` | 表格页 | Markdown表格 |
| `[section]` | 章节分隔页 | 章节过渡 |
| `[end]` | 结束页 | 最后一页 |

## 特性

### 支持任意模板

程序自动检测模板中的布局类型（封面、正文、双栏、章节等），无需手动配置。检测逻辑：
- 按布局名称关键词匹配（如 "cover"、"comparison"、"section"）
- 按占位符类型匹配（CENTER_TITLE → 封面，TITLE+OBJECT → 正文）
- 缺失的布局自动 fallback 到最接近的

### 自动字体缩放

根据每页内容量自动调整字体大小和行距，保证排版整齐：

| 内容量 | 一级字号 | 二级字号 |
|--------|---------|---------|
| ≤6条 且 <350字 | 20pt | 18pt |
| ≤10条 且 <600字 | 18pt | 16pt |
| ≤15条 且 <900字 | 16pt | 14pt |
| 更多内容 | 14pt | 13pt |

### 代码块

在提示词中使用 ` ``` ` 包裹代码，生成时渲染为独立文本框（Consolas等宽字体 + 浅灰背景 + 边框）：

```markdown
code:
​```python
def transfer_matrix(L, EI):
    T = np.eye(4)
    return T
​```
```

代码块特性：
- 位置根据正文内容量动态计算，紧跟正文下方
- 高度自适应代码行数
- 不超出页面底部
- 代码字号根据行数自动调整（≤8行11pt，≤12行10pt，更多9pt）

### 多格式提示词支持

同时支持三种提示词格式：

| 格式 | 示例 | 说明 |
|------|------|------|
| 标准格式 | `## Slide 1 [cover]` | 推荐，最精确 |
| 英文描述格式 | `## Slide 1 — Cover` | 兼容AI生成的英文提示词 |
| 中文格式 | `## 第1页 封面` | 兼容中文自由格式 |

### 统一标题栏样式

Comparison等缺少标题背景的布局，自动补充深蓝色标题栏，保持全局视觉一致。

## 推荐工作流

1. **确定PPT主题和大纲**
2. **让AI生成提示词** — 把 `PPT提示词格式规范.md` 发给AI，告诉它主题和要求
3. **保存为.md文件**
4. **运行生成** — `python md2ppt.py 提示词.md output/演示.pptx`
5. **打开PPT微调** — 调整措辞、添加图片

## 端到端自动化

本工具可以被AI Agent直接调用：

```
用户说"帮我做一个关于xxx的PPT"
    → AI生成符合格式规范的提示词.md
    → AI运行 python md2ppt.py
    → 输出.pptx
```

在Kiro中直接对话即可完成全流程。

## 注意事项

- 默认模板 `LR模板.pptx` 需和 `md2ppt.py` 在同一目录，或用 `--template` 指定路径
- 提示词中的页码必须连续（Slide 1, Slide 2, Slide 3...）
- 表格使用标准Markdown语法（`|` 分隔列）
- 正文缩进用2空格表示层级
- 代码块使用标准Markdown ` ``` ` 语法
- 程序不处理图片，需要在生成后手动插入

## 环境要求

- Python 3.8+
- python-pptx
- streamlit（仅Web UI需要）
