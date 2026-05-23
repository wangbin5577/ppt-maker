# PPT Prompt: AI-Empowered Ship Shaft Alignment — From Theory Research to Prototype Development

## Presentation Info
- Topic: How a marine engineer used Microsoft Copilot + VS Code to complete shaft alignment research and software development
- Audience: Ship designers (colleagues — familiar with engineering questions, not interested in TMM algorithm internals)
- Style: Professional engineering presentation, visual-rich, navy blue + white color scheme
- Language: English

## Slide 1 [cover]

title: AI-Empowered Ship Shaft Alignment Calculation
subtitle: From Theory Research to Prototype Development\nShaft Alignment Department | 2026

## Slide 2 [content]

title: What Is Shaft Alignment?

- Ship propulsion shafting consists of multiple shaft sections and bearings, spanning tens of meters
- Shaft alignment = determining optimal bearing height positions to ensure:
  - Bearing reactions within allowable limits (no overload, no lift-off)
  - Uniform contact pressure, avoiding localized wear
  - Crankshaft deflection within engine manufacturer limits
- Engineering purpose
  - Installation: guide bearing seat boring and shim adjustment
  - Operation: predict thermal deformation, assess wear impact on reactions
- Subject to classification society rule approval (LR Rules Pt5 Ch8 §5.4.2)

## Slide 3 [content]

title: Typical Calculation Methods for Shaft Alignment

- Three-Moment Equation Method
  - Classical continuous beam method based on moment continuity across three spans
  - Suitable for uniform cross-sections, simple supports; hand-calculable
  - Limitation: difficult for variable sections, concentrated masses, elastic supports
- Transfer Matrix Method (TMM)
  - State vector [y, θ, M, V] propagated segment by segment via 4×4 matrix multiplication
  - Handles variable sections, concentrated masses, elastic supports, Timoshenko shear
  - Core method adopted in this project
- Finite Element Method (FEM / FEA)
  - Most general: arbitrary BEAM / SHELL / SOLID element combinations
  - Can perform contact analysis, nonlinear, thermo-structural coupling
  - Used in this project as ANSYS APDL for verification and extension

## Slide 4 [content]

title: About Me — A Ship Designer, Not a Programmer

- Day job: ship propulsion shaft alignment calculation, LR rule compliance review
- Programming background: zero
  - No prior Python or ANSYS APDL experience before this project
- Motivation: deep curiosity about shaft alignment + eagerness to explore AI tools
- Outcome preview: built a tool matching LR official accuracy and exceeding its functional scope

## Slide 5 [content]

title: Why This Project — Limitations of Existing Tools

- LR official software limitations
  - Outputs only concentrated bearing reactions — no internal pressure distribution
  - No reliable verification method for slope-bored stern tube bearings
  - Black-box calculation: when something goes wrong, hard to locate
- Project goals
  - Reproduce LR software accuracy (rigid + elastic supports)
  - Extend capability: bearing contact pressure distribution + slope-bored bearings
  - Transparent and auditable: better third-party calculation review

## Slide 6 [comparison]

title: My AI Toolchain

left_title: Microsoft Copilot
left:
- Reading rules and papers: dissecting Vulić paper section by section
- Deriving formulas: explaining each element of the 4×4 transfer matrix
- Technical Q&A: unit conversions, boundary conditions, parameter calibration
- Documentation: auto-generating technical report skeletons

right_title: VS Code (IDE)
right:
- Prototyping: Python + ANSYS APDL code generation
- Debugging and refactoring: breakpoints, exception traces
- Version control: Git integration, full iteration history

## Slide 7 [content]

title: Real Research Path — 3 Phases (ANSYS Was the Key Debugging Tool)

- Phase 1: Rigid-support TMM + ANSYS reverse debugging
  - Wrote TMM in Python, found large error vs LR; LR is a black box, can't see intermediates
  - Switched to ANSYS APDL — detailed log let me reverse-locate TMM bugs
  - Outcome: TMM matches LR perfectly (RMS < 1 kgf)
- Phase 2: Elastic supports + Influence Coefficient Matrix
  - Continued the ANSYS-validation pattern
  - Outcome: elastic RMS = 0.64 kgf
- Phase 3: Extended ANSYS contact analysis (beyond LR)
  - Straight bearing: pressure distribution + contact arc
  - Slope-bored bearing: two-step method for analysis LR software cannot perform

→ ANSYS is not "third-party validation" — it is the primary debugging tool, without which TMM could not have been calibrated

## Slide 8 [section]

title: Phase 1
subtitle: AI-Assisted Literature Review + TMM Development

## Slide 9 [content]

title: AI-Assisted Literature Review (2 Core Papers)

- ★ Vulić N., Šestan A., Cvitanić V. *Modelling of Propulsion Shaft Line*. Brodogradnja, 2008.
  - §2.4 derives the 4×4 transfer matrix; §2.5 gives the influence coefficient matrix H = A⁻¹
  - Direct formula source for our TMM algorithm
- Kozousek W. M., Davies P. G. *Analysis and Survey Procedures of Propulsion Systems*. LR Paper No.5, 2000.
  - LR practitioner's overview (loads, bearings, installation, measurement)
  - Provides engineering context and terminology — no numerical formulas

Working method: used Microsoft Copilot to dissect Vulić's formulas paragraph-by-paragraph and cross-reference Kozousek's engineering context. Two papers, deeply read — AI makes depth-over-breadth practical.

## Slide 10 [content]

title: TMM Solver Core Code

- Input: Excel shaft data (64 beam segments + 10 bearings + 10 concentrated masses)
- Algorithm: Timoshenko 4×4 transfer matrix propagating state vector [y, θ, M, V]
- Units: pure SI (N, mm, MPa)

code:
```python
def build_transfer_matrix(E, L, D_out, D_in, density, start_x):
    """4x4 Timoshenko beam transfer matrix + self-weight load vector"""
    I  = math.pi / 64.0 * (D_out**4 - D_in**4)        # mm^4
    EI = E * I                                          # N*mm^2
    A  = math.pi /  4.0 * (D_out**2 - D_in**2)        # mm^2
    kGA = _shear_kGA(D_out, D_in, E)                    # N

    T = np.array([
        [1, L, L**2/(2*EI), L**3/(6*EI) - L/kGA],   # <- Timoshenko correction
        [0, 1, L/EI,         L**2/(2*EI)],
        [0, 0, 1,            L],
        [0, 0, 0,            1],
    ])
    return T, EI, w
```

## Slide 11 [table]

title: Critical Parameter Calibration

table:
| Parameter | Initial | Final | RMS Error Change |
| --- | --- | --- | --- |
| Beam theory | Euler-Bernoulli | Timoshenko | 450 -> 0.3 kgf |
| Shear correction κ | 1.11~1.45 (Vulić) | 1.0 (back-calibrated to LR) | 54 -> 0.3 kgf |
| Elastic modulus E | 210,000 MPa | 206,843 kgf/cm² | hundreds -> < 1 kgf |
| Unit system | mixed engineering | pure SI (N/mm/MPa) | reduced rounding |

notes:
- Insight: short/thick segments (L/D ~ 1-2) -> shear deformation contributes 10%-30%, Timoshenko mandatory
- Calibration done by repeatedly comparing ANSYS detailed log with LR results

## Slide 12 [table]

title: TMM Validation: Our Program vs LR Official (RMS < 1 kgf)

table:
| Bearing | Our Program (kgf) | Bearing | Our Program (kgf) |
| --- | --- | --- | --- |
| B1 | 20,671.1 | B6 | 9,267.9 |
| B2 | 4,607.6 | B7 | 9,400.9 |
| B3 | 1,285.0 | B8 | 8,969.3 |
| B4 | 4,157.0 | B9 | 10,990.2 |
| B5 | 9,500.2 | B10 | 3,286.2 |

notes:
- Test case: LR_Matric -03 standard rigid-support, 10 bearings
- Total: program 82,135 kgf vs LR reference 82,132 kgf, error -3.4 kgf = 0.004%

## Slide 13 [content]

title: ANSYS Helped Me Debug TMM — TMM Was Wrong, ANSYS Agreed with LR

- Starting point: TMM in Python, RMS = 450 kgf vs LR
  - LR is a black box — no intermediate states, no way to locate the bug
- Breakthrough: ANSYS BEAM3 model matched LR perfectly ✅
  - → ANSYS and LR are both right; TMM is the one with a bug
- Used ANSYS detailed log to reverse-locate TMM's bugs
  - Compared deflection, slope, bending moment node-by-node
  - Found TMM used Euler-Bernoulli, ANSYS used Timoshenko → after correction, RMS down to 54 kgf
  - Continued comparing, locked κ=1.0 → RMS = 0.33 kgf
- Final three-way agreement: TMM = LR = ANSYS

→ Without ANSYS detailed log, these two TMM bugs could not have been located

## Slide 14 [content]

title: Phase 2 — Elastic Support Solution (Influence Coefficient Matrix)

- Physics: bearing foundation has stiffness K — reaction R causes settlement R/K, coupled with R itself
- Decoupling method: n_sup TMM solutions build influence matrix A, then superpose displacement term

code:
```python
def solve_with_icm(params, rows):
    """Influence coefficient matrix method — elastic support decoupling"""
    R0_kgf, A = build_influence_matrix(params, rows)  # n_sup TMM solves
    delta_mm  = np.array(params.support_disp)         # support disp (mm)
    R0        = np.array(R0_kgf)
    R_kgf     = list(R0 + A @ delta_mm)               # R = R0 + A.delta
    return R_kgf, A, R0_kgf

# Validation (LR_Matric -04, 10 elastic supports):
#   RMS = 0.64 kgf vs LR reference, relative error < 0.02%
```

## Slide 15 [section]

title: Phase 3
subtitle: ANSYS Contact Analysis — Beyond LR

## Slide 16 [content]

title: Contact Model Architecture (Auto-Generated from Excel)

- Model components
  - BEAM188 shaft (65 nodes, 3D Timoshenko beam)
  - SHELL181 composite shell: white metal 3mm (E=75 GPa) + steel backing 25mm (E=210 GPa)
  - TARGE170 shadow ring (shaft surface) + CONTA174 surface contact
  - CERIG rigidly couples shadow rings to BEAM188 nodes (UX/UY/UZ)
- Core engineering value
  - Unified Excel input, one-click generation of two model types (2D BEAM3 / 3D contact)
  - LR black box hides intermediate states → ANSYS log makes bugs visible

code:
```apdl
ET,1,BEAM188              ! 3D Timoshenko beam (shaft)
ET,3,SHELL181             ! Composite bearing shell (white metal + steel)
ET,4,TARGE170             ! "Shadow ring" on shaft surface
ET,5,CONTA174             ! Surface-to-surface contact
KEYOPT,5,2,0              ! Augmented Lagrangian
KEYOPT,5,10,2             ! Update contact stiffness each iteration

*DO,i,1,n_axial
  CERIG,beam_nid(i),target_ring(i),UXYZ
*ENDDO
```

## Slide 17 [table]

title: Straight Bearing Contact Analysis Results

table:
| Metric | Value | Assessment |
| --- | --- | --- |
| L2 total reaction | 19,786 kgf | vs TMM 20,155, -1.8% ✅ |
| Peak pressure | 3.1 MPa | allowable 7-10 MPa, margin 2× ✅ |
| Contact arc (aft) | 180° | physically correct ✅ |
| Contact arc (fore) | 0° | aft→fore gradual narrowing ✅ |
| Bearing size | Φ470 × L920mm | standard case table-07 |

notes:
- Straight bearing = 2 pivots (shell concentric with shaft, h_center=0)
- Contact arc narrows from aft 180° to fore 0°, consistent with beam bending

## Slide 18 [content]

title: Slope-Bored Bearing — Why Contact Analysis Is Essential

- TMM's dilemma with slope-bored bearings (3 pivots)
  - Expands 3 pivots into 3 independent point supports with forced displacements
  - 3 non-collinear points → massive internal force oscillation: R1=-125,086 / R2=+204,729 / R3=-31,407 kgf
  - These ±100,000 kgf reactions are mathematical artifacts (condition number 6.75e+12)
  - But the resultant +48,236 kgf is correct
- LR official software also cannot provide pressure distribution for slope-bored bearings
- This is precisely why contact analysis is essential — the project's core engineering value

## Slide 19 [content]

title: Slope-Bored Bearing — Two-Step Method (New Progress)

- Problem: how to correctly position shaft and shell initially in ANSYS?
  - Tried 3 direct modelling approaches — all failed (shell offset, target offset combinations)
  - Root cause: target ring bound to beam node at y=0; h values cannot take effect directly
- Two-step method principle
  - Step 1 (TMM elastic supports): replace L2 bearing with N=11 equally-spaced elastic supports (K=55621 kgf/mm), TMM solve → shaft's true deflection curve
  - Step 2 (ANSYS contact): shell centre at y=-h(x) = bearing bore position; target ring at TMM deflection = shaft's actual position
  - Difference = initial penetration → aft penetration large → aft reaction large → consistent with LR trend

## Slide 20 [table]

title: Slope-Bored Bearing Validation (Table-09, 3 Pivots)

table:
| Metric | Value | Assessment |
| --- | --- | --- |
| Bearing length | 1410 mm | shaft Φ670 |
| L2 total reaction | 48,893 kgf | vs MTM 48,236, +1.4% ✅ |
| Peak pressure | 3.75 MPa | allowable 7-10 MPa ✅ |
| Contact length | 617 mm (44%) | LR software cannot compute |
| Load distribution | max at aft, decreasing toward fore | consistent with LR ✅ |
| Far-end bearings R7-R11 | < 0.1% deviation | global equilibrium ✅ |

notes:
- Step 1 TMM deflection vs LR deviation < 0.0013mm (1.3 microns)
- Table-10 validation: raised fore end 5mm → load correctly shifts to fore (99% at fore)
- Axial distribution: aft 28,769 kgf (180°) → decreasing → fore fully detached (0°)

## Slide 21 [content]

title: Two-Step Method — Known Limitations and Improvements

- Known limitations
  - Fore-end detachment: shell bending stiffness (25mm steel back) + fixed end arcs → seesaw effect
  - LR independent spring model shows full-length contact (no bending coupling)
  - Contact area undersized (~40%), peak pressure may be overestimated
  - K=55621 hardcoded; different bearing designs need configurable K
- Short-term improvement options
  - Option A: elastic shell foundation (K_floor) — radial COMBIN14 springs, compression-only
  - Option B: solid shaft segment (SOLID185) — shaft OD < shell ID (real clearance), beam-solid MPC transition
  - Option B yields clearance distribution map, most physically realistic

## Slide 22 [section]

title: Future Research Directions
subtitle: From Contact Model to Multi-Physics Coupling

## Slide 23 [content]

title: Future Research Directions

- Short-term (resolve fore-end detachment)
  - SOLID185 solid shaft segment + real clearance → full-length contact + clearance map
  - K_floor sensitivity sweep → quantify hull local stiffness impact
- Medium-term
  - Full cylindrical shell (360°): visualize upper-half clearance
  - Real clearance GAP=0.3~0.5mm: analyze gap effect on arc and pressure
  - Slope-bore angle optimization: auto-iterate to find h-values for most uniform pressure
- Long-term
  - EHL oil film coupling: hydrodynamic pressure effects from lubricant film
  - Thermo-structural coupling: temperature field effect on clearance and pressure
  - Wear prediction: white metal wear life assessment based on contact pressure

## Slide 24 [table]

title: Project Achievement — Capability Comparison

table:
| Capability | LR Official | This Project |
| --- | --- | --- |
| Rigid support reactions | ✅ | ✅ RMS < 1 kgf |
| Elastic support reactions | ✅ | ✅ RMS = 0.64 kgf |
| ANSYS cross-verification | ❌ | ✅ auto-generated APDL |
| Straight bearing contact pressure | ❌ | ✅ p_max + arc + distribution |
| Slope-bored bearing analysis | ❌ | ✅ two-step, 3-pivot verified |
| Slope-bore h-value sensitivity | ❌ | ✅ table-10 verified |
| Web GUI | ❌ | ✅ Streamlit |
| Open and customizable code | ❌ | ✅ Python + APDL |

notes:
- Zero programming background → ~11,000 lines of Python + auto-generated APDL
- Deviation vs LR < 0.02%, vs ANSYS < 2%
- AI toolchain: Microsoft Copilot + VS Code
- ANSYS as the key debugging tool: LR is a black box, ANSYS log makes TMM bugs visible and locatable

## Slide 25 [end]

title: Thank You!
subtitle: Engineering Curiosity + AI Exploration = Beyond Existing Tools\nQ&A
