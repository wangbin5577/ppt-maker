# PPT 提示词格式规范

## 说明

本文档定义了PPT提示词的标准格式。按此格式编写的 .md 文件可被程序自动解析并生成基于公司模板的PPT。

程序同时支持两种格式：
1. **标准格式**（推荐）：`## Slide N [布局类型]`
2. **中文格式**：`## 第N页 描述`

---

## 格式规则

### 1. 文件结构

```
# 标题（仅作文档说明，不会出现在PPT中）

## 演示信息（可选，仅作参考）

## Slide 1 [cover]
...

## Slide 2 [content]
...
```

### 2. 每页幻灯片的格式

每页以 `## Slide N [布局类型]` 开头。

#### 布局类型标记

| 标记 | 含义 | 适用场景 |
|------|------|---------|
| `[cover]` | 封面页 | 第一页 |
| `[content]` | 标准正文页 | 大部分内容页 |
| `[content_spacious]` | 大内容区正文页 | 内容较多时 |
| `[comparison]` | 双栏对比页 | 左右对比 |
| `[table]` | 表格页 | 数据展示 |
| `[section]` | 章节分隔页 | 章节过渡 |
| `[end]` | 结束页 | 最后一页 |

如果不写标记，默认为 `[content]`。

---

### 3. 各布局的内容格式

#### [cover] 封面页

```markdown
## Slide 1 [cover]

title: 主标题文字
subtitle: 副标题文字（支持 \n 换行）
```

---

#### [content] / [content_spacious] 正文页

```markdown
## Slide 3 [content]

title: 页面标题

- 第一级要点
  - 第二级要点（缩进2空格表示下一级）
- 另一个第一级要点
  - 二级
    - 三级（再缩进2空格）
```

**自动字体缩放**：程序会根据内容量自动调整字体大小：

| 内容量 | 一级字号 | 二级字号 | 行距 |
|--------|---------|---------|------|
| ≤5条 且 <200字 | 20pt | 18pt | 宽松 |
| ≤8条 且 <400字 | 18pt | 16pt | 适中 |
| ≤12条 且 <600字 | 16pt | 14pt | 紧凑 |
| 更多内容 | 14pt | 12pt | 最紧凑 |

---

#### [content] 带代码块

在正文页中插入代码块，使用标准Markdown代码围栏语法。可以加 `code:` 标记（可选）：

```markdown
## Slide 5 [content]

title: TMM核心代码

- 传递矩阵法的Python实现（10行核心逻辑）
- 状态向量传播: [y, θ, M, V]

code:
​```python
def transfer_matrix(L, EI, kGA):
    """Build 4x4 transfer matrix"""
    T = np.eye(4)
    T[0,1] = L
    T[0,2] = L**2 / (2*EI)
    T[1,2] = L / EI
    return T
​```
```

代码块渲染效果：
- Consolas 等宽字体，12pt
- 浅灰背景（#F2F2F2）+ 细边框
- 自动放置在正文要点下方

也可以省略 `code:` 标记，直接写代码围栏，程序同样能识别。

---

#### [content] 带图片占位符

在正文页中用 `image:` 标记预留图片位置，程序会生成一个虚线占位框，后期手工插入真实图片：

```markdown
## Slide 6 [content]

title: 轴承接触压力分析结果

- 峰值压力 3.1 MPa，许用值 7~10 MPa，裕度 >2×
- 接触弧角：aft端 180°，fore端 0°

image: 接触压力热力图 p(x,θ)
```

`image:` 后面的文字是图片说明，会显示在占位框内，提醒后期插入什么图。

**占位框特性：**
- 虚线边框，浅蓝背景
- 显示图片说明文字
- 自动放置在正文要点下方
- 可以和代码块同时使用（先代码后图片）

**支持多个图片占位符：**

```markdown
image: 左图：点支座模型示意图
image: 右图：接触模型压力分布
```

---

#### [comparison] 双栏对比页

```markdown
## Slide 4 [comparison]

title: 页面标题

left_title: 左栏标题
left:
- 左栏第一条
- 左栏第二条

right_title: 右栏标题
right:
- 右栏第一条
- 右栏第二条
```

---

#### [table] 表格页

```markdown
## Slide 9 [table]

title: 页面标题

table:
| 列1标题 | 列2标题 | 列3标题 |
| --- | --- | --- |
| 数据1 | 数据2 | 数据3 |
| 数据4 | 数据5 | 数据6 |

notes:
- 表格下方的补充说明（可选）
- 第二条说明
```

---

#### [section] 章节分隔页

```markdown
## Slide 5 [section]

title: 章节标题
subtitle: 章节副标题或说明
```

---

#### [end] 结束页

```markdown
## Slide 20 [end]

title: Thank You!
subtitle: 副标题或联系方式
```

---

## 4. 完整示例

```markdown
# 我的技术分享PPT

## 演示信息
- 主题：示例演示
- 语言：English

## Slide 1 [cover]

title: AI-Empowered Ship Shaft Alignment
subtitle: From Theory to Prototype\nShaft Analysis Department | 2025

## Slide 2 [content]

title: About Me

- Day job: Shaft alignment calculation, LR rule compliance review
- Programming background: Zero
  - No Python or ANSYS APDL experience before this project
- Motivation: Deep curiosity about shaft alignment theory
- Outcome: Built a tool matching LR official software accuracy

## Slide 3 [comparison]

title: My AI Toolkit

left_title: Microsoft Copilot
left:
- Paper reading & analysis
- Algorithm understanding
- Technical Q&A

right_title: VS Code (IDE)
right:
- Prototype development
- Debugging & refactoring
- Code generation

## Slide 4 [content]

title: Core Algorithm

- Transfer Matrix Method implementation

code:
​```python
def transfer_matrix(L, EI):
    T = np.eye(4)
    T[0,1] = L
    T[0,2] = L**2 / (2*EI)
    return T
​```

## Slide 5 [table]

title: Parameter Calibration Results

table:
| Parameter | Initial | Final | Error Change |
| --- | --- | --- | --- |
| Beam theory | Euler-Bernoulli | Timoshenko | 450 → 0.3 kgf |
| Shear correction κ | 0.886 | 1.0 (LR) | 54 → 0.3 kgf |

notes:
- Short/thick shaft segments: shear deformation contributes 10%~30%

## Slide 6 [section]

title: Phase 2
subtitle: TMM Rigid Solver Development

## Slide 7 [end]

title: Thank You!
subtitle: Q&A\nContact: xxx@lr.org
```

---

## 5. 中文格式（兼容）

程序也支持中文自由格式，自动识别布局类型：

```markdown
## 第1页 封面

标题：AI赋能船舶轴系较中计算
副标题：一名工程师的AI探索之路

## 第2页 个人定位

标题：关于我

要点：
- 本职工作：轴系较中计算
- 编程基础：零
- 成果：完成了与LR官方精度相当的程序

## 第3页 结束页

标题：谢谢！
副标题：Q&A
```

中文格式的布局自动推断规则：
- 第1页 → 封面
- 包含"封面"关键词 → 封面
- 包含"结束/谢谢" → 结束页
- 包含Markdown表格（≥3行 `|`）→ 表格页
- 其他 → 正文页

---

## 6. 注意事项

1. **页码必须连续**：Slide 1, Slide 2, Slide 3...
2. **布局标记可选**：不写默认为 `[content]`
3. **表格必须用标准Markdown表格语法**：用 `|` 分隔列，第二行用 `---`
4. **换行**：subtitle 中用 `\n` 表示换行
5. **缩进**：正文要点用 2 空格缩进表示层级
6. **代码块**：用 ` ``` ` 包裹，可选加 `code:` 标记
7. **图片占位**：用 `image: 说明文字` 预留图片位置，后期手工替换
8. **`## 演示信息` 部分可选**：程序会跳过，仅供人阅读参考
9. **每页之间用空行分隔**，保持可读性
10. **内容量建议**：每页正文不超过8条要点效果最佳，超过会自动缩小字体
