"""
PPT Maker Web UI
================
基于Streamlit的Web界面，用户上传提示词.md和PPT模板，一键生成PPT。

启动方式：
    streamlit run app.py
"""

import streamlit as st
import tempfile
import os
import re
from pptx import Presentation
from pptx.util import Inches, Pt


# ============================================================
# 解析器和生成器（从 md2ppt.py 整合）
# ============================================================

class SlideData:
    """一页幻灯片的解析数据"""
    def __init__(self, index, layout="content"):
        self.index = index
        self.layout = layout
        self.title = ""
        self.subtitle = ""
        self.bullets = []
        self.left_title = ""
        self.left_items = []
        self.right_title = ""
        self.right_items = []
        self.table_headers = []
        self.table_rows = []
        self.notes = []
        self.code_blocks = []


class MarkdownParser:
    """解析PPT提示词Markdown文件，支持标准格式和中文自由格式"""

    # 标准格式: ## Slide 1 [cover]
    LAYOUT_PATTERN = re.compile(r'##\s+Slide\s+(\d+)\s*\[(\w+)\]', re.IGNORECASE)
    LAYOUT_PATTERN_NO_TYPE = re.compile(r'##\s+Slide\s+(\d+)\s*$', re.IGNORECASE)
    # 中文格式: ## 第1页 封面  或  ## 第1页 描述文字
    CN_PATTERN = re.compile(r'##\s+第(\d+)页\s*(.*)', re.IGNORECASE)

    # 中文布局关键词映射
    CN_LAYOUT_KEYWORDS = {
        "封面": "cover",
        "结束": "end",
        "谢谢": "end",
        "章节": "section",
        "对比": "comparison",
        "比较": "comparison",
    }

    def __init__(self, md_content):
        self.content = md_content
        self.slides = []

    def parse(self):
        """解析Markdown内容，返回SlideData列表"""
        # 先尝试标准格式
        self.slides = self._parse_standard()
        if self.slides:
            return self.slides

        # 再尝试中文格式
        self.slides = self._parse_chinese()
        return self.slides

    def _parse_standard(self):
        """解析标准格式 (## Slide N [layout])"""
        slides = []
        sections = re.split(r'(?=^## Slide\s+\d+)', self.content, flags=re.MULTILINE)

        for section in sections:
            section = section.strip()
            if not section:
                continue

            match = self.LAYOUT_PATTERN.match(section)
            if match:
                index = int(match.group(1))
                layout = match.group(2).lower()
                body = section[match.end():].strip()
                slide = SlideData(index, layout)
                self._parse_slide_body(slide, body)
                slides.append(slide)
                continue

            match = self.LAYOUT_PATTERN_NO_TYPE.match(section)
            if match:
                index = int(match.group(1))
                body = section[match.end():].strip()
                slide = SlideData(index, "content")
                self._parse_slide_body(slide, body)
                slides.append(slide)
                continue

        return slides

    def _parse_chinese(self):
        """解析中文格式 (## 第N页 描述)"""
        slides = []
        sections = re.split(r'(?=^## 第\d+页)', self.content, flags=re.MULTILINE)

        for section in sections:
            section = section.strip()
            if not section:
                continue

            match = self.CN_PATTERN.match(section)
            if not match:
                continue

            index = int(match.group(1))
            description = match.group(2).strip()
            body = section[match.end():].strip()

            # 根据描述推断布局
            layout = self._infer_layout_from_cn(description, body, index)
            slide = SlideData(index, layout)
            self._parse_cn_body(slide, body, description)
            slides.append(slide)

        return slides

    def _infer_layout_from_cn(self, description, body, index):
        """从中文描述和内容推断布局类型"""
        # 检查关键词
        for keyword, layout in self.CN_LAYOUT_KEYWORDS.items():
            if keyword in description:
                return layout

        # 第1页通常是封面
        if index == 1:
            return "cover"

        # 包含"对比表"或"左右两列"的是comparison
        if "对比" in body or "左右两列" in body or "两列对比" in body:
            return "comparison"

        # 包含markdown表格的是table
        table_lines = [l for l in body.split('\n') if l.strip().startswith('|')]
        if len(table_lines) >= 3:
            return "table"

        return "content"

    def _parse_cn_body(self, slide, body, description):
        """解析中文格式的body内容"""
        lines = body.split('\n')
        current_section = None
        table_started = False

        for line in lines:
            stripped = line.strip()

            if not stripped or stripped == '---':
                continue

            # 标题：xxx 或 title: xxx
            if stripped.startswith('标题：') or stripped.startswith('标题:'):
                slide.title = stripped.split('：', 1)[-1].split(':', 1)[-1].strip()
                current_section = None
                continue

            if stripped.startswith('title:'):
                slide.title = stripped[6:].strip()
                current_section = None
                continue

            # 副标题
            if stripped.startswith('副标题：') or stripped.startswith('副标题:'):
                slide.subtitle = stripped.split('：', 1)[-1].split(':', 1)[-1].strip().replace('\\n', '\n')
                current_section = None
                continue

            if stripped.startswith('subtitle:'):
                slide.subtitle = stripped[9:].strip().replace('\\n', '\n')
                current_section = None
                continue

            # 要点：/ 核心理念：/ AI的作用：/ 设计思路：等 → 开始bullet区域
            if re.match(r'^(要点|核心理念|关键|AI的作用|设计思路|工作流程|解决方案|经验教训|适用场景|可视化面板|关键数字|关键结果|每个阶段|阅读的论文|核心结论表|验证数据表|三方交叉验证|AI使用心得).*[：:]', stripped):
                current_section = "bullets"
                # 如果冒号后面有内容，作为一个bullet
                after_colon = stripped.split('：', 1)[-1].split(':', 1)[-1].strip()
                if after_colon:
                    slide.bullets.append((after_colon, 0))
                continue

            # 对比表：开始表格
            if re.match(r'^(对比表|核心结论表|验证数据表|三方交叉验证结果)[：:]?', stripped):
                current_section = "table"
                table_started = False
                continue

            # 结论：/ 经验教训：→ 作为备注
            if stripped.startswith('结论：') or stripped.startswith('结论:'):
                text = stripped.split('：', 1)[-1].split(':', 1)[-1].strip()
                slide.notes.append(text)
                continue

            # 配图：/ 背景图：→ 跳过（程序不处理图片）
            if re.match(r'^(配图|背景图|布局|时间轴)[：:]', stripped):
                current_section = None
                continue

            # left_title / right_title (标准格式兼容)
            if stripped.startswith('left_title:'):
                slide.left_title = stripped[11:].strip()
                current_section = None
                continue
            if stripped.startswith('right_title:'):
                slide.right_title = stripped[12:].strip()
                current_section = None
                continue
            if stripped == 'left:':
                current_section = "left"
                continue
            if stripped == 'right:':
                current_section = "right"
                continue
            if stripped == 'table:':
                current_section = "table"
                table_started = False
                continue
            if stripped == 'notes:':
                current_section = "notes"
                continue

            # Markdown表格行
            if stripped.startswith('|'):
                cells = [c.strip() for c in stripped.split('|')[1:-1]]
                if not cells:
                    continue
                if all(re.match(r'^:?-+:?$', c) for c in cells):
                    table_started = True
                    continue
                if not slide.table_headers:
                    slide.table_headers = cells
                    current_section = "table"
                    table_started = False
                else:
                    slide.table_rows.append(cells)
                continue

            # bullet列表
            if stripped.startswith('- ') or stripped.startswith('* '):
                indent = len(line) - len(line.lstrip())
                level = indent // 2
                text = stripped[2:]

                if current_section == "left":
                    slide.left_items.append(text)
                elif current_section == "right":
                    slide.right_items.append(text)
                elif current_section == "notes":
                    slide.notes.append(text)
                else:
                    current_section = "bullets"
                    slide.bullets.append((text, level))
                continue

            # 有序列表 (1. xxx)
            num_match = re.match(r'^\d+[\.\)]\s*(.+)', stripped)
            if num_match:
                slide.bullets.append((num_match.group(1), 0))
                current_section = "bullets"
                continue

            # 其他文本 — 如果在bullets模式追加，否则作为新bullet
            if current_section == "bullets" and slide.bullets:
                last_text, last_level = slide.bullets[-1]
                slide.bullets[-1] = (last_text + " " + stripped, last_level)
            elif current_section == "left":
                slide.left_items.append(stripped)
            elif current_section == "right":
                slide.right_items.append(stripped)

        # 如果没有提取到标题，用description作为标题
        if not slide.title and description:
            slide.title = description

        # 自动判断：如果有表格数据但布局不是table，更新布局
        if slide.table_headers and slide.table_rows and slide.layout == "content":
            slide.layout = "table"

        # 如果是comparison但没有左右栏数据，降级为content
        if slide.layout == "comparison" and not slide.left_items and not slide.right_items:
            slide.layout = "content"

        # 封面页：如果没有副标题，把第一个bullet当副标题
        if slide.layout == "cover" and not slide.subtitle and slide.bullets:
            slide.subtitle = "\n".join([b[0] for b in slide.bullets[:2]])
            slide.bullets = []

    def _extract_code_blocks(self, body):
        """从body中提取代码块"""
        code_blocks = []
        pattern = re.compile(r'(?:code:\s*\n)?```\w*\n(.*?)```', re.DOTALL)
        for match in pattern.finditer(body):
            code = match.group(1).rstrip('\n')
            code_blocks.append(code)
        cleaned = pattern.sub('', body)
        cleaned = re.sub(r'^code:\s*$', '', cleaned, flags=re.MULTILINE)
        return cleaned, code_blocks

    def _parse_slide_body(self, slide, body):
        """解析标准格式的body内容"""
        body, code_blocks = self._extract_code_blocks(body)
        slide.code_blocks = code_blocks
        lines = body.split('\n')
        current_section = None
        table_started = False

        for line in lines:
            stripped = line.strip()

            if not stripped:
                continue

            if stripped.startswith('title:'):
                slide.title = stripped[6:].strip()
                current_section = None
                continue

            if stripped.startswith('subtitle:'):
                slide.subtitle = stripped[9:].strip().replace('\\n', '\n')
                current_section = None
                continue

            if stripped.startswith('left_title:'):
                slide.left_title = stripped[11:].strip()
                current_section = None
                continue

            if stripped.startswith('right_title:'):
                slide.right_title = stripped[12:].strip()
                current_section = None
                continue

            if stripped == 'left:':
                current_section = "left"
                continue

            if stripped == 'right:':
                current_section = "right"
                continue

            if stripped == 'table:':
                current_section = "table"
                table_started = False
                continue

            if stripped == 'notes:':
                current_section = "notes"
                continue

            if current_section == "table" and stripped.startswith('|'):
                cells = [c.strip() for c in stripped.split('|')[1:-1]]
                if all(re.match(r'^:?-+:?$', c) for c in cells):
                    table_started = True
                    continue
                if not table_started:
                    slide.table_headers = cells
                else:
                    slide.table_rows.append(cells)
                continue

            if stripped.startswith('- ') or stripped.startswith('* '):
                indent = len(line) - len(line.lstrip())
                level = indent // 2
                text = stripped[2:]

                if current_section == "left":
                    slide.left_items.append(text)
                elif current_section == "right":
                    slide.right_items.append(text)
                elif current_section == "notes":
                    slide.notes.append(text)
                else:
                    current_section = "bullets"
                    slide.bullets.append((text, level))
                continue

            if current_section == "bullets" and slide.bullets:
                last_text, last_level = slide.bullets[-1]
                slide.bullets[-1] = (last_text + " " + stripped, last_level)
            elif current_section == "left":
                slide.left_items.append(stripped)
            elif current_section == "right":
                slide.right_items.append(stripped)


class PPTGenerator:
    """基于模板生成PPT"""

    # 默认LR模板布局索引（可通过自动检测覆盖）
    DEFAULT_LAYOUTS = {
        "cover": 7,
        "content": 9,
        "content_spacious": 10,
        "comparison": 15,
        "section": 14,
        "end": 7,
        "table": 10,
    }

    def __init__(self, template_path):
        self.prs = Presentation(template_path)
        self.layouts = self._detect_layouts()
        self._clear_existing_slides()

    def _detect_layouts(self):
        """自动检测模板中的布局类型，优先使用布局名称匹配"""
        layouts = {}
        
        # 第一轮：按名称精确匹配（适用于LR模板等已知模板）
        name_mapping = {
            "marine gtc": "cover",
            "marine turbine": "cover",
            "marine compass": "cover",
            "marine propeller": "cover",
            "marine newbuilding": "cover",
            "marine engine room": "cover",
            "marine safety": "cover",
            "marine waves": "cover",
            "new cover": "cover",
            "white standard": "content",
            "white spacious": "content_spacious",
            "grey standard": "content",
            "grey spacous": "content_spacious",
            "comparison": "comparison",
            "section header": "section",
            "end slide": "end",
            "title only": "title_only",
            "blank": "blank",
        }
        
        for i, layout in enumerate(self.prs.slide_layouts):
            name_lower = layout.name.lower()
            for pattern, layout_type in name_mapping.items():
                if pattern in name_lower:
                    # 只保留第一个匹配的（除了cover，保留最后一个以匹配Marine GTC）
                    if layout_type == "cover":
                        layouts["cover"] = i  # 会被后面的覆盖，最终取最后一个cover布局
                    elif layout_type not in layouts:
                        layouts[layout_type] = i
                    break
        
        # 对于cover，优先选择 "Marine GTC" 或 "New Cover"
        for i, layout in enumerate(self.prs.slide_layouts):
            name_lower = layout.name.lower()
            if "gtc" in name_lower or "new cover" in name_lower:
                layouts["cover"] = i
                break
        
        # 第二轮：如果名称匹配不够，用占位符类型检测补充
        if "content" not in layouts or "comparison" not in layouts:
            for i, layout in enumerate(self.prs.slide_layouts):
                placeholders = list(layout.placeholders)
                has_center_title = any(ph.placeholder_format.type == 3 for ph in placeholders)
                has_title = any(ph.placeholder_format.type == 1 for ph in placeholders)
                has_object = any(ph.placeholder_format.type == 7 for ph in placeholders)
                has_body = any(ph.placeholder_format.type == 2 for ph in placeholders)
                n_placeholders = len(placeholders)

                if has_title and has_object and n_placeholders == 2:
                    if "content" not in layouts:
                        layouts["content"] = i
                    elif "content_spacious" not in layouts:
                        layouts["content_spacious"] = i
                if n_placeholders >= 5 and has_title and "comparison" not in layouts:
                    layouts["comparison"] = i
                if has_title and has_body and n_placeholders == 2 and not has_object:
                    if "section" not in layouts:
                        layouts["section"] = i

        # 用默认值填充缺失的
        for key, val in self.DEFAULT_LAYOUTS.items():
            if key not in layouts:
                if val < len(self.prs.slide_layouts):
                    layouts[key] = val
                else:
                    layouts[key] = layouts.get("content", 0)

        if "end" not in layouts:
            layouts["end"] = layouts.get("cover", 0)
        if "table" not in layouts:
            layouts["table"] = layouts.get("content_spacious", layouts.get("content", 0))

        return layouts

    def _clear_existing_slides(self):
        """清除模板中已有的幻灯片"""
        while len(self.prs.slides) > 0:
            rId = self.prs.slides._sldIdLst[0].rId
            self.prs.part.drop_rel(rId)
            self.prs.slides._sldIdLst.remove(self.prs.slides._sldIdLst[0])

    def generate(self, slides_data):
        """根据解析数据生成所有幻灯片"""
        for sd in slides_data:
            if sd.layout in ("cover", "end"):
                self._add_cover(sd)
            elif sd.layout == "comparison":
                self._add_comparison(sd)
            elif sd.layout == "table":
                self._add_table(sd)
            elif sd.layout == "section":
                self._add_section(sd)
            elif sd.layout == "content_spacious":
                self._add_content(sd, spacious=True)
            else:
                self._add_content(sd, spacious=False)

    def _add_title_background(self, slide):
        """为缺少标题背景的布局添加深蓝色标题栏和蓝色横线"""
        from pptx.dml.color import RGBColor
        from pptx.enum.shapes import MSO_SHAPE
        
        # 深蓝色标题背景 (accent2 = #003C71)
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(0),
            Inches(12), Inches(1.28)
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = RGBColor(0x00, 0x3C, 0x71)
        bg_shape.line.fill.background()
        slide.shapes._spTree.remove(bg_shape._element)
        slide.shapes._spTree.insert(2, bg_shape._element)
        
        # 蓝色横线 (accent1 = #3B8EDE)
        line_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0), Inches(1.28),
            Inches(12), Inches(0.19)
        )
        line_shape.fill.solid()
        line_shape.fill.fore_color.rgb = RGBColor(0x3B, 0x8E, 0xDE)
        line_shape.line.fill.background()
        slide.shapes._spTree.remove(line_shape._element)
        slide.shapes._spTree.insert(3, line_shape._element)

    def _add_cover(self, sd):
        layout = self.prs.slide_layouts[self.layouts["cover"]]
        slide = self.prs.slides.add_slide(layout)
        if 0 in [ph.placeholder_format.idx for ph in slide.placeholders]:
            slide.placeholders[0].text = sd.title
        if 1 in [ph.placeholder_format.idx for ph in slide.placeholders]:
            slide.placeholders[1].text = sd.subtitle

    def _calc_font_size(self, bullets, has_code=False):
        """根据内容量自动计算字体大小和行距"""
        n_bullets = len(bullets)
        total_chars = sum(len(text) for text, _ in bullets)

        if has_code:
            if n_bullets <= 4:
                return Pt(18), Pt(16), Pt(6), Pt(3)
            else:
                return Pt(16), Pt(14), Pt(4), Pt(2)

        if n_bullets <= 6 and total_chars < 350:
            return Pt(20), Pt(18), Pt(8), Pt(4)
        elif n_bullets <= 10 and total_chars < 600:
            return Pt(18), Pt(16), Pt(6), Pt(3)
        elif n_bullets <= 15 and total_chars < 900:
            return Pt(16), Pt(14), Pt(4), Pt(2)
        else:
            return Pt(14), Pt(13), Pt(3), Pt(1)

    def _add_content(self, sd, spacious=False):
        if sd.code_blocks:
            spacious = True
        layout_key = "content_spacious" if spacious else "content"
        layout = self.prs.slide_layouts[self.layouts[layout_key]]
        slide = self.prs.slides.add_slide(layout)

        if 0 in [ph.placeholder_format.idx for ph in slide.placeholders]:
            slide.placeholders[0].text = sd.title

        size_l0, size_l1, space_after, space_before = self._calc_font_size(
            sd.bullets, has_code=bool(sd.code_blocks)
        )

        if 1 in [ph.placeholder_format.idx for ph in slide.placeholders]:
            tf = slide.placeholders[1].text_frame
            tf.clear()

            first_para = True
            for text, level in sd.bullets:
                if first_para:
                    p = tf.paragraphs[0]
                    first_para = False
                else:
                    p = tf.add_paragraph()
                p.text = text
                p.level = level
                p.font.size = size_l0 if level == 0 else size_l1
                p.space_after = space_after
                p.space_before = space_before

            # 代码块追加到同一个text_frame中
            if sd.code_blocks:
                from pptx.dml.color import RGBColor
                for code in sd.code_blocks:
                    p = tf.add_paragraph()
                    p.space_after = Pt(2)
                    for code_line in code.split('\n'):
                        p = tf.add_paragraph()
                        run = p.add_run()
                        run.text = code_line
                        run.font.name = 'Consolas'
                        run.font.size = Pt(11)
                        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
                        p.space_after = Pt(0)
                        p.space_before = Pt(0)
                        p.level = 0

    def _add_code_blocks(self, slide, code_blocks, n_bullets=0):
        """在幻灯片上添加代码块文本框"""
        from pptx.dml.color import RGBColor
        # 动态计算起始位置
        top_start = 1.8 + n_bullets * 0.35
        top_start = max(top_start, 2.5)
        top_start = min(top_start, 4.5)
        top = Inches(top_start)
        page_bottom = Inches(6.8)

        for code in code_blocks:
            lines = code.split('\n')
            n_lines = len(lines)
            height = Inches(n_lines * 0.22 + 0.3)
            max_height = page_bottom - top
            if max_height < Inches(0.5):
                break
            height = min(height, max_height)
            txBox = slide.shapes.add_textbox(Inches(0.8), top, Inches(10.4), height)
            tf = txBox.text_frame
            tf.word_wrap = True
            fill = txBox.fill
            fill.solid()
            fill.fore_color.rgb = RGBColor(0xF2, 0xF2, 0xF2)
            txBox.line.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)
            txBox.line.width = Pt(0.5)
            code_font_size = Pt(11) if n_lines <= 10 else Pt(10)
            for i, code_line in enumerate(lines):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.text = code_line
                p.font.name = 'Consolas'
                p.font.size = code_font_size
                p.font.color.rgb = RGBColor(0x2D, 0x2D, 0x2D)
                p.space_after = Pt(0)
                p.space_before = Pt(0)
            top += height + Inches(0.15)

    def _add_comparison(self, sd):
        layout = self.prs.slide_layouts[self.layouts["comparison"]]
        slide = self.prs.slides.add_slide(layout)

        # 添加标题背景色块（Comparison布局缺少这些装饰元素）
        self._add_title_background(slide)

        ph_indices = [ph.placeholder_format.idx for ph in slide.placeholders]

        if 0 in ph_indices:
            slide.placeholders[0].text = sd.title
        if 1 in ph_indices:
            slide.placeholders[1].text = sd.left_title
        if 3 in ph_indices:
            slide.placeholders[3].text = sd.right_title

        if 2 in ph_indices:
            tf_left = slide.placeholders[2].text_frame
            tf_left.clear()
            for i, item in enumerate(sd.left_items):
                p = tf_left.paragraphs[0] if i == 0 else tf_left.add_paragraph()
                p.text = item
                p.font.size = Pt(18)
                p.space_after = Pt(8)

        if 4 in ph_indices:
            tf_right = slide.placeholders[4].text_frame
            tf_right.clear()
            for i, item in enumerate(sd.right_items):
                p = tf_right.paragraphs[0] if i == 0 else tf_right.add_paragraph()
                p.text = item
                p.font.size = Pt(18)
                p.space_after = Pt(8)

    def _add_table(self, sd):
        layout = self.prs.slide_layouts[self.layouts["table"]]
        slide = self.prs.slides.add_slide(layout)

        if 0 in [ph.placeholder_format.idx for ph in slide.placeholders]:
            slide.placeholders[0].text = sd.title

        if sd.table_headers and sd.table_rows:
            n_cols = len(sd.table_headers)
            n_rows = len(sd.table_rows) + 1

            left = Inches(0.8)
            top = Inches(1.8)
            width = Inches(10.4)
            row_height = 0.45
            height = Inches(min(row_height * n_rows, 4.5))

            table_shape = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
            table = table_shape.table

            for i, header in enumerate(sd.table_headers):
                cell = table.cell(0, i)
                cell.text = header
                for paragraph in cell.text_frame.paragraphs:
                    paragraph.font.bold = True
                    paragraph.font.size = Pt(11)

            for row_idx, row_data in enumerate(sd.table_rows, 1):
                for col_idx in range(min(len(row_data), n_cols)):
                    cell = table.cell(row_idx, col_idx)
                    cell.text = row_data[col_idx]
                    for paragraph in cell.text_frame.paragraphs:
                        paragraph.font.size = Pt(10)

        if sd.notes:
            n_rows_total = (len(sd.table_rows) + 1) if sd.table_headers else 0
            note_top = Inches(1.8 + 0.45 * n_rows_total + 0.3)
            txBox = slide.shapes.add_textbox(Inches(0.8), note_top, Inches(10.4), Inches(1.5))
            tf = txBox.text_frame
            tf.word_wrap = True
            for i, note in enumerate(sd.notes):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.text = note

    def _add_section(self, sd):
        layout = self.prs.slide_layouts[self.layouts["section"]]
        slide = self.prs.slides.add_slide(layout)
        ph_indices = [ph.placeholder_format.idx for ph in slide.placeholders]
        if 0 in ph_indices:
            slide.placeholders[0].text = sd.title
        if 1 in ph_indices and sd.subtitle:
            slide.placeholders[1].text = sd.subtitle

    def save(self, output_path):
        self.prs.save(output_path)
        return output_path


# ============================================================
# Streamlit Web UI
# ============================================================

def main():
    st.set_page_config(
        page_title="PPT Maker",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 PPT Maker")
    st.markdown("上传提示词和PPT模板，一键生成演示文稿")

    st.divider()

    # 两列布局
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1️⃣ 上传PPT模板")
        template_file = st.file_uploader(
            "选择 .pptx 模板文件",
            type=["pptx"],
            help="上传公司PPT模板，生成的PPT将使用该模板的样式"
        )
        if template_file:
            st.success(f"✅ 模板已上传: {template_file.name}")

    with col2:
        st.subheader("2️⃣ 提供提示词")
        input_method = st.radio(
            "选择输入方式",
            ["上传.md文件", "直接粘贴"],
            horizontal=True
        )

        md_content = None

        if input_method == "上传.md文件":
            md_file = st.file_uploader(
                "选择提示词 .md 文件",
                type=["md", "txt"],
                help="按照格式规范编写的Markdown提示词文件"
            )
            if md_file:
                md_content = md_file.read().decode("utf-8")
                st.success(f"✅ 提示词已上传: {md_file.name}")
        else:
            md_content = st.text_area(
                "粘贴提示词内容",
                height=400,
                placeholder="## Slide 1 [cover]\n\ntitle: 我的演示\nsubtitle: 副标题\n\n## Slide 2 [content]\n\ntitle: 第一页\n\n- 要点1\n- 要点2"
            )
            if md_content:
                st.success("✅ 提示词已输入")

    st.divider()

    # 预览解析结果
    if md_content:
        with st.expander("📋 预览解析结果", expanded=False):
            parser = MarkdownParser(md_content)
            slides = parser.parse()
            if slides:
                for sd in slides:
                    st.markdown(f"**Slide {sd.index}** `[{sd.layout}]` — {sd.title}")
            else:
                st.warning("⚠️ 未解析到任何幻灯片，请检查格式是否正确")

    # 生成按钮
    st.subheader("3️⃣ 生成PPT")

    if st.button("🚀 生成PPT", type="primary", use_container_width=True):
        if not template_file:
            st.error("❌ 请先上传PPT模板")
            return
        if not md_content:
            st.error("❌ 请先提供提示词内容")
            return

        with st.spinner("正在生成PPT..."):
            try:
                # 解析提示词
                parser = MarkdownParser(md_content)
                slides_data = parser.parse()

                if not slides_data:
                    st.error("❌ 提示词解析失败，未找到任何 `## Slide N` 格式的内容")
                    return

                # 保存模板到临时文件
                template_file.seek(0)  # 确保从头读取
                with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp_template:
                    tmp_template.write(template_file.read())
                    tmp_template_path = tmp_template.name

                # 生成PPT
                gen = PPTGenerator(tmp_template_path)
                gen.generate(slides_data)

                # 保存输出到临时文件
                with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp_output:
                    tmp_output_path = tmp_output.name

                gen.save(tmp_output_path)

                # 读取生成的文件
                with open(tmp_output_path, "rb") as f:
                    pptx_bytes = f.read()

                # 清理临时文件
                os.unlink(tmp_template_path)
                os.unlink(tmp_output_path)

                # 显示成功信息
                st.success(f"✅ PPT生成成功！共 {len(slides_data)} 页")

                # 下载按钮
                st.download_button(
                    label="📥 下载PPT",
                    data=pptx_bytes,
                    file_name="generated_presentation.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"❌ 生成失败: {str(e)}")
                st.exception(e)

    # 底部帮助信息
    st.divider()
    with st.expander("❓ 格式帮助"):
        st.markdown("""
### 支持的布局类型

| 标记 | 用途 |
|------|------|
| `[cover]` | 封面页 |
| `[content]` | 标准正文页 |
| `[content_spacious]` | 大内容区正文页 |
| `[comparison]` | 双栏对比页 |
| `[table]` | 表格页 |
| `[section]` | 章节分隔页 |
| `[end]` | 结束页 |

### 快速示例

```markdown
## Slide 1 [cover]

title: 演示标题
subtitle: 副标题

## Slide 2 [content]

title: 页面标题

- 第一个要点
  - 子要点
- 第二个要点

## Slide 3 [comparison]

title: 对比页标题

left_title: 左栏
left:
- 左边内容1
- 左边内容2

right_title: 右栏
right:
- 右边内容1
- 右边内容2

## Slide 4 [table]

title: 表格页标题

table:
| 列A | 列B | 列C |
| --- | --- | --- |
| 数据1 | 数据2 | 数据3 |

## Slide 5 [end]

title: 谢谢！
subtitle: Q&A
```
        """)


if __name__ == "__main__":
    main()
