# PPT 提示词：AI 赋能船舶轴系较中——从理论研究到原型开发

## 演示信息
- 主题：一名船舶设计工程师如何使用 Microsoft Copilot + VS Code 完成轴系较中理论研究与软件原型开发
- 听众：船舶设计师（同事，对轴系较中工程问题熟悉，对 TMM 算法细节不感兴趣）
- 风格：专业工程汇报，图文并茂，深蓝+白色主色调
- 语言：中文

## Slide 1 [cover]

title: AI 赋能船舶轴系较中计算
subtitle: 从理论研究到原型开发\nShaft Alignment Department | 2026

## Slide 2 [content]

title: 什么是轴系较中？

- 船舶推进轴系由多段轴、多个支撑轴承组成，全长可达数十米
- 轴系较中 = 确定各轴承的最佳高度位置，使：
  - 各轴承反力在许用范围内（不过载、不抬起）
  - 轴承接触压力均匀，避免局部磨损
  - 曲轴偏转在发动机厂许用范围内
- 工程目的
  - 安装阶段：指导轴承座镗孔与垫片调整
  - 运营阶段：预测热态变形、评估磨损对反力的影响
- 涉及船级社规范审批（LR Rules Pt5 Ch8 §5.4.2）

## Slide 3 [content]

title: 轴系较中的典型计算方法

- 三弯矩法（Three-Moment Equation）
  - 经典连续梁方法，基于相邻三跨的弯矩连续条件
  - 适用于均匀截面、简单支座，手算可行
  - 局限：难以处理变截面、集中质量、弹性支座
- 迁移矩阵法（Transfer Matrix Method, TMM）
  - 状态向量 [y, θ, M, V] 逐段传递，4×4 矩阵乘法
  - 可处理变截面、集中质量、弹性支座、Timoshenko 剪切
  - 本项目采用的核心方法
- 有限元法（FEM / FEA）
  - 最通用：BEAM / SHELL / SOLID 单元任意组合
  - 可做接触分析、非线性、热-结构耦合
  - 本项目用 ANSYS APDL 作为验证与扩展工具

## Slide 4 [content]

title: 关于我——一名船舶设计工程师，不是程序员

- 本职工作：船舶推进轴系较中计算、LR 规范审图
- 编程基础：零
  - 项目开始前从未接触过 Python 与 ANSYS APDL
- 驱动力：对轴系技术的深入钻研 + 对 AI 新技术的好奇心
- 成果预告：独立完成与 LR 官方软件精度相当的程序，并在功能上超越它

## Slide 5 [content]

title: 项目背景——为什么要做这件事

- 现有 LR 官方软件的局限
  - 仅输出各支座集中反力，无法展示轴承内部压力分布
  - 多斜度尾轴承的斜镗设计缺乏可靠的验证手段
  - 计算过程是黑盒，看不到中间状态——出问题难定位
- 项目目标
  - 复现 LR 软件精度（刚性 + 柔性支座反力）
  - 扩展能力：计算轴承接触压力分布、支持多斜度轴承
  - 透明可审：理解算法后能更好审核第三方计算结果

## Slide 6 [comparison]

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

## Slide 7 [content]

title: 真实研究路线——三阶段（ANSYS 是关键调试工具）

- Phase 1：刚性支座 TMM + ANSYS 调试
  - Python 写完 TMM，与 LR 对比误差大；LR 是黑盒看不到中间结果
  - 转用 ANSYS APDL —— 详细 log 让我能反向定位 TMM bug
  - 关键产出：TMM 与 LR 完全匹配（RMS < 1 kgf）
- Phase 2：柔性支座 + 影响系数矩阵法
  - 沿用 ANSYS 验证手法
  - 关键产出：柔性 RMS = 0.64 kgf
- Phase 3：扩展 ANSYS 接触分析（超越 LR）
  - 直筒轴承：压力分布 + 接触弧角
  - 多斜度轴承：两步法实现 LR 软件根本无法计算的分析

→ ANSYS 不只是"第三方验证"——它是没有它就调不通 TMM 的主力调试工具

## Slide 8 [section]

title: Phase 1
subtitle: AI 辅助文献研究 + TMM 开发

## Slide 9 [content]

title: AI 辅助文献阅读（精读 2 篇核心论文）

- ★ Vulić N., Šestan A., Cvitanić V. *Modelling of Propulsion Shaft Line*. Brodogradnja, 2008.
  - §2.4 给出 4×4 传递矩阵公式；§2.5 给出影响系数矩阵 H = A⁻¹
  - 本项目 TMM 算法的直接公式来源
- Kozousek W. M., Davies P. G. *Analysis and Survey Procedures of Propulsion Systems*. LR Paper No.5, 2000.
  - LR 工程师视角的实践综述（载荷、轴承、安装、测量）
  - 提供工程背景与术语，不含数值算法公式

工作方式：用 Microsoft Copilot 逐段拆解 Vulić 论文公式，与 Kozousek 综述里的工程语境对照——精读 2 篇就吃透 TMM 算法。

## Slide 10 [content]

title: TMM 求解器核心代码

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

    T = np.array([
        [1, L, L**2/(2*EI), L**3/(6*EI) - L/kGA],   # ← Timoshenko 修正
        [0, 1, L/EI,         L**2/(2*EI)],
        [0, 0, 1,            L],
        [0, 0, 0,            1],
    ])
    return T, EI, w
```

## Slide 11 [table]

title: 关键参数标定（工程经验 + AI 数值实验）

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

title: TMM 验证：程序 vs LR 官方（RMS < 1 kgf）

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
- 总和：本程序 82,135 kgf vs LR 参考 82,132 kgf，误差 -3.4 kgf = 0.004%

## Slide 13 [content]

title: ANSYS 帮我调试 TMM —— TMM 错了，但 ANSYS 与 LR 一致

- 起点：Python 写完 TMM，与 LR 对比 RMS = 450 kgf
  - LR 是黑盒，看不到中间状态，无从定位错在哪
- 关键转机：ANSYS BEAM3 模型与 LR 完全一致 ✅
  - → ANSYS 与 LR 都对，是 TMM 算错了
- 借助 ANSYS 详细 log 反推 TMM 的错
  - 逐节点对比挠度、转角、弯矩
  - 发现 TMM 用了 Euler-Bernoulli，ANSYS 用了 Timoshenko → 修正后 RMS 降到 54 kgf
  - 继续比对，锁定 κ=1.0 后 RMS = 0.33 kgf
- 最终三方一致：TMM = LR = ANSYS

→ 没有 ANSYS 的详细 log，TMM 这两个 bug 不可能定位

## Slide 14 [content]

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

## Slide 15 [section]

title: Phase 3
subtitle: ANSYS 接触分析——超越 LR

## Slide 16 [content]

title: 接触模型架构（自动从 Excel 生成）

- 模型构成
  - BEAM188 轴（65 节点，3D Timoshenko 梁）
  - SHELL181 复合壳：白合金 3mm (E=75GPa) + 钢背 25mm (E=210GPa)
  - TARGE170 影子圈（轴表面）+ CONTA174 面接触
  - CERIG 把影子圈刚性耦合到 BEAM188 节点（UXYZ 三向）
- 核心工程价值
  - 统一 Excel 输入，一键生成两种模型（2D BEAM3 / 3D 接触）
  - LR 黑盒看不到中间状态 → ANSYS log 让 bug 可见

code:
```apdl
ET,1,BEAM188              ! 3D Timoshenko 梁（轴）
ET,3,SHELL181             ! 轴承复合壳（白合金 + 钢背）
ET,4,TARGE170             ! 轴表面"影子圈"
ET,5,CONTA174             ! 面-面接触
KEYOPT,5,2,0              ! 增广拉格朗日法
KEYOPT,5,10,2             ! 每次迭代更新接触刚度

*DO,i,1,n_axial
  CERIG,beam_nid(i),target_ring(i),UXYZ
*ENDDO
```

## Slide 17 [table]

title: 直筒轴承接触分析结果

table:
| 指标 | 数值 | 评价 |
| --- | --- | --- |
| L2 总反力 | 19,786 kgf | vs TMM 20,155，−1.8% ✅ |
| 峰值压力 | 3.1 MPa | 许用 7~10 MPa，裕度 2× ✅ |
| 接触弧角 (aft) | 180° | 物理合理 ✅ |
| 接触弧角 (fore) | 0° | aft→fore 逐渐收窄 ✅ |
| 轴承尺寸 | Φ470 × L920mm | 标准算例 表-07 |

notes:
- 直筒轴承 = 普通 2 pivots（壳与轴同心，h_center=0）
- 接触弧从 aft 180° 到 fore 0°，符合梁弯曲效应

## Slide 18 [content]

title: 多斜度轴承——为什么需要接触分析？

- TMM 处理多斜度轴承（3 pivots）的困境
  - 将 3 个 pivot 展开为 3 个独立点支座，强制施加位移
  - 3 点不共线 → 产生巨大内力震荡：R1=-125,086 / R2=+204,729 / R3=-31,407 kgf
  - 这些 ±10 万级的反力是数学产物（条件数 6.75e+12），不代表真实物理
  - 但合力 +48,236 kgf 是正确的
- LR 官方软件同样无法给出多斜度的压力分布
- 这正是"为什么必须做接触分析"的核心工程依据

## Slide 19 [content]

title: 多斜度轴承——两步法（本项目新进展）

- 问题：如何在 ANSYS 中正确定位轴和壳的初始位置？
  - 直接建模试过 3 种方案均不成功（壳偏移、target 偏移组合）
  - 根本原因：target ring 绑定 beam 节点，beam 初始在 y=0，h 值无法直接生效
- 两步法原理
  - 第一步（TMM 弹性支座）：将 L2 轴承替换为 N=11 个等距弹性支座 (K=55621 kgf/mm)，TMM 求解得到轴的真实挠度
  - 第二步（ANSYS 接触）：壳中心按 h(x) 定位 = 轴承孔位置；Target ring 按第一步挠度定位 = 轴实际位置
  - 两者差值 = 初始穿透量 → aft 端穿透大 → aft 端反力大 → 与 LR 趋势一致

## Slide 20 [table]

title: 多斜度轴承验证结果（表-09，3 pivots）

table:
| 指标 | 数值 | 评价 |
| --- | --- | --- |
| 轴承长度 | 1410 mm | 轴径 Φ670 |
| L2 总反力 | 48,893 kgf | vs MTM 48,236，+1.4% ✅ |
| 峰值压力 | 3.75 MPa | 许用 7~10 MPa ✅ |
| 接触长度 | 617 mm (44%) | LR 软件无法计算 |
| 载荷分布 | aft 端最大，向 fore 递减 | 与 LR 趋势一致 ✅ |
| 远端支座 R7~R11 偏差 | < 0.1% | 全局平衡 ✅ |

notes:
- 第一步 TMM 挠度与 LR 偏差 < 0.0013mm（1.3 微米）
- 表-10 验证：抬高 fore 端 5mm → 载荷正确向 fore 转移（99% 反力在 fore 端）
- 轴向分布：aft 端 28,769 kgf (180°) → 递减 → fore 端完全脱开（0°）

## Slide 21 [content]

title: 两步法的已知局限与改进方向

- 已知局限
  - fore 端脱开：壳有弯曲刚度（钢背 25mm），端弧 D,ALL 锁死 → 类跷跷板效应
  - LR 独立弹簧模型显示全长接触，因为不存在壳的弯曲耦合
  - 接触面积偏小（约 40%），峰值压力可能偏高
  - K=55621 硬编码，不同轴承设计需要可配置
- 短期改进方案
  - 方案 A：弹性壳座（K_floor）——壳底接径向 COMBIN14 弹簧，只压不拉
  - 方案 B：实体轴段（SOLID185）——轴外径 < 壳内径（真实间隙），梁-实体 MPC 过渡
  - 方案 B 可得到间隙分布云图，物理最真实

## Slide 22 [section]

title: 后续研究方向
subtitle: 从接触模型到多物理场耦合

## Slide 23 [content]

title: 后续研究方向

- 短期（解决 fore 端脱开）
  - SOLID185 实体轴段 + 真实间隙 → 全长接触 + 间隙分布图
  - 弹性壳座 K_floor 敏感性扫描 → 量化船体刚度影响
- 中期
  - 完整圆柱壳（360°）：看到上半部分间隙
  - 真实间隙 GAP=0.3~0.5mm：分析间隙对弧角和压力的影响
  - 斜镗角度优化：自动迭代找到使压力最均匀的 h 值组合
- 长期
  - EHL 油膜耦合：考虑润滑油膜的流体动压效应
  - 热-结构耦合：温度场对间隙和压力的影响
  - 磨损预测：基于接触压力的白合金磨损寿命评估

## Slide 24 [table]

title: 项目成果——能力对比总览

table:
| 能力 | LR 官方软件 | 本项目 |
| --- | --- | --- |
| 刚性支座反力 | ✅ | ✅ RMS < 1 kgf |
| 柔性支座反力 | ✅ | ✅ RMS = 0.64 kgf |
| ANSYS 交叉验证 | ❌ | ✅ 自动生成 APDL |
| 直筒轴承接触压力 | ❌ | ✅ p_max + 弧角 + 分布 |
| 多斜度轴承分析 | ❌ | ✅ 两步法，3 pivots 验证 |
| 多斜度 h 值灵敏度 | ❌ | ✅ 表-10 验证 |
| Web 图形界面 | ❌ | ✅ Streamlit |
| 代码开放可定制 | ❌ | ✅ Python + APDL |

notes:
- 0 编程基础 → 独立完成约 11,000 行 Python + 自动生成 APDL
- 与 LR 偏差 < 0.02%，与 ANSYS 偏差 < 2%
- AI 工具链：Microsoft Copilot + VS Code
- ANSYS 是关键调试主力：LR 黑盒看不到内部，ANSYS log 让 TMM bug 可见可定位

## Slide 25 [end]

title: 谢谢！
subtitle: 技术钻研 + AI 探索 = 超越现有工具的可能\nQ&A

