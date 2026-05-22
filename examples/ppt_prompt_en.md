# PPT Prompt: AI-Empowered Ship Shaft Alignment — From Theory Research to Prototype Development

## Presentation Info
- Topic: How a marine engineer used Microsoft Copilot + VS Code to complete shaft alignment research and software development
- Audience: Ship designers (colleagues — familiar with engineering questions, not interested in TMM algorithm internals)
- Style: Professional engineering presentation, visual-rich, navy blue + white color scheme
- Pages: 20 slides
- Language: English

## Slide 1 [cover]

title: AI-Empowered Ship Shaft Alignment Calculation
subtitle: From Theory Research to Prototype Development\nShaft Alignment Department | 2026

## Slide 2 [content]

title: About Me — A Ship Designer, Not a Programmer

- Day job: ship propulsion shaft alignment calculation, LR rule compliance review
- Programming background: zero
  - No prior Python or ANSYS APDL experience before this project
- Motivation: deep curiosity about shaft alignment + eagerness to explore AI tools
- Outcome preview: built a tool matching LR official accuracy and exceeding its functional scope

## Slide 3 [content]

title: Why This Project — Limitations of Existing Tools

- LR official software limitations
  - Outputs only **concentrated bearing reactions** — no internal pressure distribution
  - No reliable verification method for slope-bored stern tube bearings
  - Black-box calculation: when something goes wrong, hard to locate
- Project goals
  - Reproduce LR software accuracy (rigid + elastic supports)
  - Extend capability: bearing contact pressure distribution + slope-bored bearings
  - Transparent and auditable: better third-party calculation review

## Slide 4 [comparison]

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

## Slide 5 [content]

title: Real Research Path — 3 Phases (ANSYS Was the Key Debugging Tool)

- Phase 1: Rigid-support TMM + ANSYS reverse debugging
  - Wrote TMM in Python, found large error vs LR; LR is a black box, can't see intermediates
  - **Switched to ANSYS APDL** — detailed log let me reverse-locate TMM bugs
  - Outcome: TMM matches LR perfectly (RMS < 1 kgf)
- Phase 2: Elastic supports + Influence Coefficient Matrix
  - Continued the ANSYS-validation pattern
  - Outcome: elastic RMS = 0.64 kgf
- Phase 3: Extended ANSYS contact analysis (beyond LR)
  - Straight bearing: pressure distribution + contact arc
  - Slope-bored bearing: LR software cannot compute this; this project can

→ ANSYS is not "third-party validation" — it is the **primary debugging tool**, without which TMM could not have been calibrated

## Slide 6 [section]

title: Phase 1
subtitle: AI-Assisted Literature Review

## Slide 7 [content]

title: Phase 1 — AI-Assisted Literature Review (2 core papers)

- ★ Vulić N., Šestan A., Cvitanić V. *Modelling of Propulsion Shaft Line and Basic Procedure of Shafting Alignment Calculation*. Brodogradnja, 2008, 59(3): 223–227.
  - §2.4 derives the 4×4 transfer matrix; §2.5 gives the influence coefficient matrix H = A⁻¹
  - Direct formula source for our TMM algorithm
- Kozousek W. M., Davies P. G. *Analysis and Survey Procedures of Propulsion Systems: Shafting Alignment*. Lloyd's Register Technical Association, Paper No.5, London, 2000.
  - LR practitioner's overview (loads, bearings, installation, measurement)
  - Provides engineering context and terminology — no numerical formulas

Working method: used Microsoft Copilot to dissect Vulić's formulas paragraph-by-paragraph and cross-reference Kozousek's engineering context. **Two papers, deeply read** — AI makes depth-over-breadth practical without paper-stacking.

## Slide 8 [content]

title: Phase 1 — AI Helped Pinpoint the Core Method from 2 Papers

- Finding 1: full TMM derivation in Vulić et al. (2008) §2.4 — state vector [w, β, M, Q] + 4×4 transfer matrix + 4×1 load vector
- Finding 2: influence coefficient matrix (ICM) from the same paper §2.5 — equation R = R₀ + H·(p − p₀) maps directly to my code's `R = R0 + A·δ`
- Finding 3: LR Paper No.5 provides engineering context (loads, bearings, installation) — no numerical formulas, which prevented "looking for formulas in the wrong place"
- Finding 4: shear correction κ — Vulić recommends κ ∈ [1.11, 1.45], but a ~54 kgf gap remained vs LR official software
  - Engineer + AI calibration: locked κ = 1.0 by back-calibration to bring RMS below 1 kgf
  - Engineering insight neither paper nor rules state explicitly
- Verification: had Copilot explain every matrix element in Vulić §2.4 eq.(3) against the original notation, element-by-element

## Slide 9 [section]

title: Phase 1
subtitle: Rigid-Support TMM + ANSYS Reverse Debugging

## Slide 10 [content]

title: Phase 1 — TMM Solver (Core Code)

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
    w  = density * 1e-6 * A * G                         # N/mm

    T = np.array([
        [1, L, L**2/(2*EI), L**3/(6*EI) - L/kGA],   # <- Timoshenko correction
        [0, 1, L/EI,         L**2/(2*EI)],
        [0, 0, 1,            L],
        [0, 0, 0,            1],
    ])
    return T, EI, w
```

## Slide 11 [table]

title: Phase 1 — Critical Parameter Calibration

table:
| Parameter | Initial | Final | RMS Error Change |
| --- | --- | --- | --- |
| Beam theory | Euler-Bernoulli | Timoshenko | 450 -> 0.3 kgf |
| Shear correction κ | 1.11~1.45 (Vulić recommended) | 1.0 (back-calibrated to LR) | 54 -> 0.3 kgf |
| Elastic modulus E | 210,000 MPa | 206,843 kgf/cm² | hundreds -> < 1 kgf |
| Unit system | mixed engineering | pure SI (N/mm/MPa) | reduced rounding |

notes:
- Insight: short/thick segments (L/D ~ 1-2) -> shear deformation contributes 10%-30%, Timoshenko mandatory
- Calibration done by repeatedly comparing ANSYS detailed log with LR results

## Slide 12 [table]

title: Phase 1 — TMM Validation: Our Program vs LR Official (RMS < 1 kgf)

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
- Total: program 82,135 kgf vs LR reference 82,132 kgf, **error -3.4 kgf** = 0.004%
- Per-bearing maximum deviation < 1 kgf — fully matches LR official

## Slide 13 [section]

title: The Real Role of ANSYS
subtitle: Not Post-Hoc Validation — The Primary Tool for Debugging TMM

## Slide 14 [content]

title: APDL Auto-Generator — Unified Excel, One-Click for Both Models

- **Unified input**: a single Excel (table-06 format)
  - Engineers don't switch files, don't model manually
  - Program auto-detects support types → selects model type
- **Two outputs, one click**
  - All L0 supports → 2D BEAM3 simplified model (for rigid/elastic reaction calc)
  - Any L2 support → 3D contact model (BEAM188 + SHELL181 + CONTA174)
- **Core engineering value**
  - LR is a black box, intermediate states invisible — hard to debug
  - ANSYS log exposes TMM intermediate states → reverse-locate bugs
  - Powers both Phase 1 algorithm debugging AND Phase 3 beyond-LR contact analysis

code:
```python
# gen_apdl_L2_3D_contact.py — Auto-detect + dual-mode generation
support_kinds = read_excel_row7(xlsx)        # Row7: "L0" / "L2"

if all(k == "L0" for k in support_kinds):
    # Mode A: 2D BEAM3 (equivalent to Phase 1 algorithm validation)
    w("ET,1,BEAM3")
    for nid, x_pos in nodes:  w(f"N,{nid},{x_pos}")
    for sup_nid, ky in supports:  w(f"D,{sup_nid},UY,0")
else:
    # Mode B: 3D contact (BEAM188 + SHELL181 + CONTA174)
    w("ET,1,BEAM188")           # 3D Timoshenko beam
    w("ET,3,SHELL181")           # Composite shell: white metal + steel
    w("ET,4,TARGE170")           # Shadow ring
    w("ET,5,CONTA174")           # Surface contact
    # ...auto-generate CERIG rigid coupling, composite layup, contact params
w("SOLVE")
w(f"*GET,RB1,NODE,{nid_b1},RF,FY")
```

## Slide 15 [content]

title: ANSYS Helped Me Debug TMM — TMM Was Wrong, ANSYS Agreed with LR

- **Starting point**: TMM in Python, RMS = 450 kgf vs LR
  - LR is a black box — no intermediate states, no way to locate the bug
- **Breakthrough**: ANSYS BEAM3 model matched LR perfectly ✅
  - → ANSYS and LR are both right; TMM is the one with a bug
- **Used ANSYS detailed log to reverse-locate TMM's bugs**
  - Compared deflection, slope, bending moment node-by-node
  - Found TMM used Euler-Bernoulli, ANSYS used Timoshenko → after correction, RMS down to 54 kgf
  - Continued comparing, found shear factor κ differs: Vulić paper [1.11, 1.45], ANSYS BEAM3 internal 1.0 → locked κ=1.0 → RMS = 0.33 kgf
- **Final three-way agreement**: TMM = LR = ANSYS

→ Without ANSYS detailed log, these two TMM bugs could not have been located

## Slide 16 [content]

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

## Slide 17 [content]

title: Phase 3 — Contact Model Architecture (Beyond LR)

- Model components (auto-generated from Excel)
  - BEAM188 shaft (65 nodes, 3D Timoshenko beam)
  - SHELL181 composite shell: white metal 3mm (E=75 GPa) + steel backing 25mm (E=210 GPa)
  - TARGE170 shadow ring (shaft surface) + CONTA174 surface contact
  - CERIG rigidly couples shadow rings to BEAM188 nodes (UX/UY/UZ)

code:
```apdl
ET,1,BEAM188              ! 3D Timoshenko beam (shaft)
ET,3,SHELL181             ! Composite bearing shell (white metal + steel)
ET,4,TARGE170             ! "Shadow ring" on shaft surface
ET,5,CONTA174             ! Surface-to-surface contact
KEYOPT,5,2,0              ! Augmented Lagrangian
KEYOPT,5,10,2             ! Update contact stiffness each iteration

! Key trick: BEAM188 has no physical surface ->
!           use CERIG to rigidly couple 13-node target ring to beam node
*DO,i,1,n_axial
  CERIG,beam_nid(i),target_ring(i),UXYZ
*ENDDO
```

## Slide 18 [table]

title: Phase 3 — Contact Analysis Results (Straight + Slope-Bored Bearings)

table:
| Case | Metric | Value | Assessment |
| --- | --- | --- | --- |
| Straight (Φ470, L=920mm) | L2 total reaction | 19,786 kgf | vs TMM 20,155, -1.8% ✅ |
| Straight | Peak pressure | 3.1 MPa | allowable 7-10 MPa, margin 2× ✅ |
| Straight | Contact arc | aft 180° -> fore 0° | physically correct ✅ |
| Slope-bored (3 pivots, L=1410mm) | Total reaction | 48,893 kgf | vs MTM 48,236, +1.4% ✅ |
| Slope-bored | Peak pressure | 3.75 MPa | within allowable ✅ |
| Slope-bored | Contact length | 617 mm (44%) | LR software **cannot compute** |

notes:
- Slope-bored bearing with 3 adjacent rigid pivots: condition number 6.75e+12, point reactions oscillate ±100,000 kgf (mathematical artifact)
- This is exactly why contact analysis is essential -> the project's core engineering value

## Slide 19 [table]

title: Project Achievement — Capability Comparison

table:
| Capability | LR Official | This Project |
| --- | --- | --- |
| Rigid support reactions | ✅ | ✅ RMS < 1 kgf |
| Elastic support reactions | ✅ | ✅ RMS = 0.64 kgf |
| ANSYS cross-verification | ❌ | ✅ auto-generated APDL |
| Bearing contact pressure | ❌ | ✅ p_max + arc + distribution |
| Slope-bored bearing analysis | ❌ | ✅ 3-pivot verified |
| Web GUI | yes | ✅ Streamlit |
| Open & customizable code | ❌ | ✅ Python + APDL |

notes:
- Zero programming background → ~11,000 lines of Python (incl. tests) + auto-generated APDL
- Deviation vs LR < 0.02%, vs ANSYS < 2%
- AI toolchain: Microsoft Copilot (papers + algorithms) + VS Code (development + debugging)
- ANSYS as the key debugging tool: LR is a black box, ANSYS log makes TMM bugs visible and locatable
- Engineer's domain expertise + AI's coding capability + ANSYS detailed log = exceeding existing tools

## Slide 20 [end]

title: Thank You!
subtitle: Engineering Curiosity + AI Exploration = Beyond Existing Tools
Q&A
