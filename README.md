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
├── 启动Web UI.bat             双击启动Web界面（端口8503）
├── LR模板.pptx                默认模板
├── PPT提示词格式规范.md         格式约定（给AI看）
├── examples/                  示例提示词
│   ├── ppt_prompt_en.md       英文版
│   └── ppt_prompt_cn.md       中文版
├── output/                    生成的PPT输出（文件名含时间戳）
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

**命令行方式：**

```bash
# 使用默认模板（LR模板.pptx）
python md2ppt.py 提示词.md

# 指定输出路径
python md2ppt.py 提示词.md output/演示.pptx

# 使用其他模板
python md2ppt.py 提示词.md output/演示.pptx --template 其他模板.pptx
```

**Web UI 方式：**

```bash
streamlit run app.py --server.port 8503
```

或双击 `启动Web UI.bat`，打开浏览器 http://localhost:8503 即可。

Web UI 功能：
- LR模板为默认，上传模板是可选项
- 支持上传 .md 文件或直接粘贴提示词
- 生成后自动保存到 `output/` 目录，文件名含时间戳防覆盖
- 页面提供下载按钮
- 底部提供提示词格式规范下载

## 支持的页面布局

| 标记 | 用途 | 说明 |
|------|------|------|
| `[cover]` | 封面页 | 标题 + 副标题 |
| `[content]` | 标准正文页 | 标题 + bullet列表 |
| `[content_spacious]` | 大内容区正文页 | 内容多时自动使用 |
| `[comparison]` | 双栏对比页 | 左右两栏对比 |
| `[table]` | 表格页 | Markdown表格，自动删除空占位符 |
| `[section]` | 章节分隔页 | 章节过渡 |
| `[end]` | 结束页 | 最后一页 |

## 特性

### 支持任意模板

程序自动检测模板中的布局类型，无需手动配置。检测优先级：
1. 按布局名称关键词匹配（Marine GTC → 封面，White standard → 正文等）
2. 按占位符类型匹配（CENTER_TITLE → 封面，TITLE+OBJECT → 正文）
3. 缺失的布局自动 fallback 到最接近的

### 自动字体缩放

根据每页内容量自动调整字体大小和行距：

| 内容量 | 一级字号 | 二级字号 |
|--------|---------|---------|
| ≤6条 且 <350字 | 20pt | 18pt |
| ≤10条 且 <600字 | 18pt | 16pt |
| ≤15条 且 <900字 | 16pt | 14pt |
| 更多内容 | 14pt | 13pt |

### 代码块（左文右代码布局）

在提示词中使用 ` ``` ` 包裹代码，生成时自动采用**左文右代码**分栏布局：
- 左侧40%：正文 bullet 列表
- 右侧55%：代码块（Consolas等宽字体 + 浅灰背景 + 边框）
- 代码字号根据行数自动调整

```markdown
## Slide 5 [content]

title: TMM核心代码

- 传递矩阵法的Python实现

code:
​```python
def transfer_matrix(L, EI):
    T = np.eye(4)
    T[0,1] = L
    return T
​```
```

### 图片占位符（左文右图布局）

用 `image:` 标记预留图片位置，生成时自动采用**左文右图**分栏布局：
- 左侧42%：正文 bullet 列表
- 右侧53%：虚线边框占位框（浅蓝背景 + 说明文字）
- 多个图片时右侧垂直均分

```markdown
## Slide 6 [content]

title: 接触压力分析结果

- 峰值压力 3.1 MPa，裕度 >2×
- 接触弧角：aft端 180°，fore端 0°

image: 接触压力热力图 p(x,θ)
```

中文提示词中的 `配图：xxx` 也会自动转为图片占位框。

### 统一标题栏样式

所有布局（Comparison、Table、代码块页、图片页）自动补充深蓝色标题栏 + 白色标题文字，保持全局视觉一致。

### 多格式提示词支持

| 格式 | 示例 | 说明 |
|------|------|------|
| 标准格式 | `## Slide 1 [cover]` | 推荐，最精确 |
| 英文描述格式 | `## Slide 1 — Cover` | 兼容AI生成的英文提示词 |
| 中文格式 | `## 第1页 封面` | 兼容中文自由格式 |

## 推荐工作流

1. **确定PPT主题和大纲**
2. **让AI生成提示词** — 把 `PPT提示词格式规范.md` 发给AI，告诉它主题和要求
3. **保存为.md文件**
4. **运行生成** — 命令行或Web UI
5. **打开PPT微调** — 调整措辞、插入真实图片（替换占位框）

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
- 代码块使用标准Markdown ` ``` ` 语法，可选加 `code:` 标记
- 图片占位用 `image: 说明文字`，后期在PPT中手动替换为真实图片

## 环境要求

- Python 3.8+
- python-pptx
- streamlit（仅Web UI需要）
