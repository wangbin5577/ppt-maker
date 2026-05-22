# PPT 提示词：AI 赋能船舶轴系较中——从理论研究到原型开发

## 演示信息
- 主题：一名船舶设计工程师如何使用 Microsoft Copilot + VS Code 完成轴系较中理论研究与软件原型开发
- 听众：船舶设计师（同事，对轴系较中工程问题熟悉，对 TMM 算法细节不感兴趣）
- 风格：专业工程汇报，图文并茂，深蓝+白色主色调
- 页数：20 页
- 语言：中文

## Slide 1 [cover]

title: AI 赋能船舶轴系较中计算
subtitle: 从理论研究到原型开发\nShaft Alignment Department | 2026

## Slide 2 [content]

title: 关于我——一名船舶设计工程师，不是程序员

- 本职工作：船舶推进轴系较中计算、LR 规范审图
- 编程基础：零
  - 项目开始前从未接触过 Python 与 ANSYS APDL
- 驱动力：对轴系技术的深入钻研 + 对 AI 新技术的好奇心
- 成果预告：独立完成与 LR 官方软件精度相当的程序，并在功能上超越它

## Slide 3 [content]

title: 项目背景——为什么要做这件事

- 现有 LR 官方软件的局限
  - 仅输出各支座**集中反力**，无法展示轴承内部压力分布
  - 多斜度尾轴承的斜镗设计缺乏可靠的验证手段
  - 计算过程是黑盒，看不到中间状态——出问题难定位
- 项目目标
  - 复现 LR 软件精度（刚性 + 柔性支座反力）
  - 扩展能力：计算轴承接触压力分布、支持多斜度轴承
  - 透明可审：理解算法后能更好审核第三方计算结果

## Slide 4 [comparison]

title: 我的 AI 工具链

left_title: Microsoft Copilot
left:
- 阅读规范与论文：Vulić 论文逐段拆解
- 推导公式与算法：解释 4×4 传递矩阵每个元素的物理含义
- 技术问答：单位换算、边界条件、参数标定
- 文档撰写：自动生成技术报告骨架

right_title: VS Code（IDE）
right:
- 原型开发：Python + ANSYS APDL 代码生成
- 调试与重构：断点、异常追踪
- 版本管理：Git 集成，迭代留痕

## Slide 5 [content]

title: 真实研究路线——三阶段（ANSYS 是关键调试工具）

- Phase 1：刚性支座 TMM + ANSYS 调试
  - Python 写完 TMM，与 LR 对比误差大；LR 是黑盒看不到中间结果
  - **转用 ANSYS APDL** —— 详细 log 让我能反向定位 TMM bug
  - 关键产出：TMM 与 LR 完全匹配（RMS < 1 kgf）
- Phase 2：柔性支座 + 影响系数矩阵法
  - 沿用 ANSYS 验证手法
  - 关键产出：柔性 RMS = 0.64 kgf
- Phase 3：扩展 ANSYS 接触分析（超越 LR）
  - 直筒轴承：压力分布 + 接触弧角
  - 多斜度轴承：LR 软件根本无法计算，本项目可算

→ ANSYS 不只是"第三方验证"——它是没有它就调不通 TMM 的**主力调试工具**

## Slide 6 [section]

title: Phase 1
subtitle: AI 辅助文献研究

## Slide 7 [content]

title: Phase 1 — AI 辅助文献阅读（精读 2 篇核心论文）

- ★ Vulić N., Šestan A., Cvitanić V. *Modelling of Propulsion Shaft Line and Basic Procedure of Shafting Alignment Calculation*. Brodogradnja, 2008, 59(3): 223–227.
  - §2.4 给出 4×4 传递矩阵公式；§2.5 给出影响系数矩阵 H = A⁻¹
  - 本项目 TMM 算法的直接公式来源
- Kozousek W. M., Davies P. G. *Analysis and Survey Procedures of Propulsion Systems: Shafting Alignment*. Lloyd's Register Technical Association, Paper No.5, London, 2000.
  - LR 工程师视角的实践综述（载荷、轴承、安装、测量）
  - 提供工程背景与术语，不含数值算法公式

工作方式：用 Microsoft Copilot 逐段拆解 Vulić 论文公式，与 Kozousek 综述里的工程语境对照——**精读 2 篇就吃透 TMM 算法**，AI 让"深读"成为可能，不需要论文堆砌。

## Slide 8 [content]

title: Phase 1 — AI 帮我从 2 篇论文中精准定位核心方法

- 关键发现 1：TMM 公式在 Vulić et al. (2008) §2.4 给出完整推导，状态向量 [w, β, M, Q] + 4×4 传递矩阵 + 4×1 载荷向量
- 关键发现 2：影响系数矩阵法 (ICM) 来自同篇 §2.5，公式 R = R₀ + H·(p − p₀) 直接对应我代码里的 `R = R0 + A·δ`
- 关键发现 3：LR Paper No.5 提供工程背景（载荷、轴承、安装），不含数值算法公式——避免了"在错的地方找公式"的误区
- 关键发现 4：剪切修正系数 κ —— Vulić 论文推荐 κ ∈ [1.11, 1.45]，但与 LR 官方软件比对仍有 ~54 kgf 误差
  - 工程师 + AI 调参：通过反向标定锁定 **κ = 1.0** 才使 RMS < 1 kgf
  - 这是论文+规范都没明说的工程经验
- 验证手段：让 Copilot 把 Vulić §2.4 公式 (3) 的每个矩阵元素逐个解释物理含义，与原文符号对照

## Slide 9 [section]

title: Phase 1
subtitle: 刚性支座 TMM + ANSYS 反向调试

## Slide 10 [content]

title: Phase 1 — 矩阵传递法求解器（核心代码）

- 输入：Excel 轴系数据（64 段梁 + 10 个支座 + 10 个集中质量）
- 算法：Timoshenko 梁 4×4 传递矩阵传播状态向量 [y, θ, M, V]
- 单位制：纯 SI（N, mm, MPa）

code:
```python
def build_transfer_matrix(E, L, D_out, D_in, density, start_x):
    """Timoshenko 梁段 4×4 传递矩阵 + 自重载荷向量"""
    I  = math.pi / 64.0 * (D_out**4 - D_in**4)        # mm^4
    EI = E * I                                          # N·mm^2
    A  = math.pi /  4.0 * (D_out**2 - D_in**2)        # mm^2
    kGA = _shear_kGA(D_out, D_in, E)                    # N
    w  = density * 1e-6 * A * G                         # N/mm

    T = np.array([
        [1, L, L**2/(2*EI), L**3/(6*EI) - L/kGA],   # ← Timoshenko 修正
        [0, 1, L/EI,         L**2/(2*EI)],
        [0, 0, 1,            L],
        [0, 0, 0,            1],
    ])
    return T, EI, w
```

## Slide 11 [table]

title: Phase 1 — 关键参数标定（工程经验 + AI 数值实验）

table:
| 参数 | 初始尝试 | 最终确定 | RMS 误差变化 |
| --- | --- | --- | --- |
| 梁理论 | Euler-Bernoulli | Timoshenko | 450 → 0.3 kgf |
| 剪切修正 κ | 1.11~1.45 (Vulić 推荐) | 1.0 (反向标定 LR) | 54 → 0.3 kgf |
| 弹性模量 E | 210,000 MPa | 206,843 kgf/cm² | 数百 → < 1 kgf |
| 单位制 | 工程混合单位 | 纯 SI (N/mm/MPa) | 减少口径误差 |

notes:
- 关键洞察：短粗轴段 L/D ≈ 1~2，剪切变形占总变形 10%~30%，必须用 Timoshenko
- 参数标定通过 ANSYS 详细 log 与 LR 结果反复对比完成

## Slide 12 [table]

title: Phase 1 — TMM 验证：程序 vs LR 官方（RMS < 1 kgf）

table:
| 支座 | 本程序 (kgf) | 支座 | 本程序 (kgf) |
| --- | --- | --- | --- |
| B1 | 20,671.1 | B6 | 9,267.9 |
| B2 | 4,607.6 | B7 | 9,400.9 |
| B3 | 1,285.0 | B8 | 8,969.3 |
| B4 | 4,157.0 | B9 | 10,990.2 |
| B5 | 9,500.2 | B10 | 3,286.2 |

notes:
- 算例：LR_Matric -03 标准刚性支座工况，10 个支座
- 总和：本程序 82,135 kgf vs LR 参考 82,132 kgf，**误差 -3.4 kgf** = 0.004%
- 单个支座最大偏差 < 1 kgf，与 LR 官方答案完全一致

## Slide 13 [section]

title: ANSYS 的真实角色
subtitle: 不是事后验证——是调试 TMM 的主力工具

## Slide 14 [content]

title: APDL 自动生成器——统一 Excel 一键生成两种模型

- **统一输入**：一份 Excel 表-06 格式
  - 工程师不需要切换文件、不需要手动建模
  - 程序自动判断支座类型 → 自动选择模型类型
- **两种输出，一键生成**
  - 全 L0 支座 → 2D BEAM3 简化模型（用于刚性/柔性反力计算）
  - 含 L2 支座 → 3D 接触模型（BEAM188 + SHELL181 + CONTA174）
- **核心工程价值**
  - LR 黑盒看不到中间状态，调试困难
  - ANSYS log 让 TMM 中间状态可见 → 反向定位 bug
  - 同时支撑了 Phase 1 算法调试 + Phase 3 超越 LR 的接触分析

code:
```python
# gen_apdl_L2_3D_contact.py — 自动判断 + 双模式生成
support_kinds = read_excel_row7(xlsx)        # 读 Row7 "L0" / "L2"

if all(k == "L0" for k in support_kinds):
    # 模式 A: 2D BEAM3（与 Phase 1 算法验证完全等价）
    w("ET,1,BEAM3")
    for nid, x_pos in nodes:  w(f"N,{nid},{x_pos}")
    for sup_nid, ky in supports:  w(f"D,{sup_nid},UY,0")
else:
    # 模式 B: 3D 接触（BEAM188 + SHELL181 + CONTA174）
    w("ET,1,BEAM188")           # 3D Timoshenko 梁
    w("ET,3,SHELL181")           # 复合壳：白合金+钢背
    w("ET,4,TARGE170")           # 影子圈
    w("ET,5,CONTA174")           # 面接触
    # ...自动生成 CERIG 刚性耦合、复合层定义、接触参数
w("SOLVE")
w(f"*GET,RB1,NODE,{nid_b1},RF,FY")
```

## Slide 15 [content]

title: ANSYS 帮我调试 TMM —— TMM 错了，但 ANSYS 与 LR 一致

- **起点**：Python 写完 TMM，与 LR 对比 RMS = 450 kgf
  - LR 是黑盒，看不到中间状态，无从定位错在哪
- **关键转机**：ANSYS BEAM3 模型与 LR 完全一致 ✅
  - → ANSYS 与 LR 都对，是 TMM 算错了
- **借助 ANSYS 详细 log 反推 TMM 的错**
  - 逐节点对比挠度、转角、弯矩
  - 发现 TMM 用了 Euler-Bernoulli，ANSYS 用了 Timoshenko → 加修正后 RMS 降到 54 kgf
  - 继续比对，发现剪切修正 κ 不同：Vulić 给 [1.11, 1.45]，ANSYS BEAM3 内部用 1.0 → 锁定 κ=1.0 后 RMS = 0.33 kgf
- **最终三方一致**：TMM = LR = ANSYS

→ 没有 ANSYS 的详细 log，TMM 这两个 bug 不可能定位

## Slide 16 [content]

title: Phase 2 — 柔性支座求解（影响系数矩阵法）

- 物理问题：轴承座有刚度 K，反力 R 让座下沉 R/K，与 R 耦合
- 解耦方法：n_sup 次 TMM 求解构建影响矩阵 A，再叠加位移项

code:
```python
def solve_with_icm(params, rows):
    """影响系数矩阵法 — 柔性支座解耦"""
    R0_kgf, A = build_influence_matrix(params, rows)  # n_sup 次 TMM
    delta_mm  = np.array(params.support_disp)         # 支座位移 (mm)
    R0        = np.array(R0_kgf)
    R_kgf     = list(R0 + A @ delta_mm)               # R = R0 + A·δ
    return R_kgf, A, R0_kgf

# 验证（LR_Matric -04，10 个柔性支座）：
#   RMS = 0.64 kgf vs LR 参考，相对误差 < 0.02%
```

## Slide 17 [content]

title: Phase 3 — 接触模型架构与关键代码（超越 LR）

- 模型构成（自动从 Excel 生成）
  - BEAM188 轴（65 节点，3D Timoshenko 梁）
  - SHELL181 复合壳：白合金 3mm (E=75GPa) + 钢背 25mm (E=210GPa)
  - TARGE170 影子圈（轴表面）+ CONTA174 面接触
  - CERIG 把影子圈刚性耦合到 BEAM188 节点（UXYZ 三向）

code:
```apdl
ET,1,BEAM188              ! 3D Timoshenko 梁（轴）
ET,3,SHELL181             ! 轴承复合壳（白合金 + 钢背）
ET,4,TARGE170             ! 轴表面"影子圈"
ET,5,CONTA174             ! 面-面接触
KEYOPT,5,2,0              ! 增广拉格朗日法
KEYOPT,5,10,2             ! 每次迭代更新接触刚度

! 关键：BEAM188 无物理表面 → 用 CERIG 把 13 节点目标圈
!       刚性耦合到梁节点（UX/UY/UZ 三向）
*DO,i,1,n_axial
  CERIG,beam_nid(i),target_ring(i),UXYZ
*ENDDO
```

## Slide 18 [table]

title: Phase 3 — 接触分析结果（直筒 + 多斜度轴承）

table:
| 工况 | 指标 | 数值 | 评价 |
| --- | --- | --- | --- |
| 直筒轴承 (Φ470, L=920mm) | L2 总反力 | 19,786 kgf | vs TMM 20,155，−1.8% ✅ |
| 直筒轴承 | 峰值压力 | 3.1 MPa | 许用 7~10 MPa，裕度 2× ✅ |
| 直筒轴承 | 接触弧角 | aft 180° → fore 0° | 物理合理 ✅ |
| 多斜度 (3 pivots, L=1410mm) | 总反力 | 48,893 kgf | vs MTM 48,236，+1.4% ✅ |
| 多斜度 | 峰值压力 | 3.75 MPa | 许用内 ✅ |
| 多斜度 | 接触长度 | 617 mm (44%) | LR 软件**无法计算** |

notes:
- 多斜度轴承 3 个相邻刚性点条件数 6.75e+12，TMM 单点反力震荡 ±10万 kgf（数学伪象）
- 这正是"为什么必须做接触分析"的工程依据 → 项目核心价值

## Slide 19 [table]

title: 项目成果——一张表看全部能力

table:
| 能力 | LR 官方软件 | 本项目 |
| --- | --- | --- |
| 刚性支座反力 | ✅ | ✅ RMS < 1 kgf |
| 柔性支座反力 | ✅ | ✅ RMS = 0.64 kgf |
| ANSYS 交叉验证 | ❌ | ✅ 自动生成 APDL |
| 轴承接触压力分布 | ❌ | ✅ p_max + 弧角 + 分布 |
| 多斜度轴承分析 | ❌ | ✅ 3 pivots 验证通过 |
| Web 图形界面 | 有 | ✅ Streamlit |
| 代码开放可定制 | ❌ | ✅ Python + APDL |

notes:
- 0 编程基础 → 独立完成约 11,000 行 Python（含测试）+ 自动生成 APDL
- 与 LR 偏差 < 0.02%，与 ANSYS 偏差 < 2%
- AI 工具链：Microsoft Copilot（论文 + 算法）+ VS Code（开发 + 调试）
- ANSYS 是关键调试主力：LR 黑盒看不到内部，ANSYS log 让 TMM bug 可见可定位
- 工程师领域知识 + AI 编码能力 + ANSYS 详细 log = 超越现有工具的可能

## Slide 20 [end]

title: 谢谢！
subtitle: 技术钻研 + AI 探索 = 超越现有工具的可能
Q&A
