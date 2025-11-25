from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from pathlib import Path
import re

md_file = Path("Architecture_Documentation.md")
md_content = md_file.read_text(encoding='utf-8')

output_file = "Digital_Twin_Architecture_Documentation.pdf"
doc = SimpleDocTemplate(output_file, pagesize=A4,
                        rightMargin=72, leftMargin=72,
                        topMargin=72, bottomMargin=18)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CustomTitle',
                          parent=styles['Heading1'],
                          fontSize=24,
                          textColor=colors.HexColor('#667eea'),
                          spaceAfter=30,
                          alignment=TA_CENTER))
styles.add(ParagraphStyle(name='CustomHeading1',
                          parent=styles['Heading1'],
                          fontSize=18,
                          textColor=colors.HexColor('#667eea'),
                          spaceAfter=12,
                          spaceBefore=12))
styles.add(ParagraphStyle(name='CustomHeading2',
                          parent=styles['Heading2'],
                          fontSize=14,
                          textColor=colors.HexColor('#764ba2'),
                          spaceAfter=10,
                          spaceBefore=10))
styles.add(ParagraphStyle(name='CustomHeading3',
                          parent=styles['Heading3'],
                          fontSize=12,
                          textColor=colors.HexColor('#667eea'),
                          spaceAfter=8,
                          spaceBefore=8))
styles.add(ParagraphStyle(name='CustomCode',
                          parent=styles['Normal'],
                          fontName='Courier',
                          fontSize=9,
                          leftIndent=20,
                          textColor=colors.black,
                          backColor=colors.HexColor('#f4f4f4')))

story = []
lines = md_content.split('\n')
i = 0
in_code_block = False
code_lines = []

while i < len(lines):
    line = lines[i]
    
    if line.startswith('```'):
        if not in_code_block:
            in_code_block = True
            code_lines = []
        else:
            in_code_block = False
            code_text = '\n'.join(code_lines)
            story.append(Preformatted(code_text, styles['CustomCode']))
            story.append(Spacer(1, 0.2*inch))
        i += 1
        continue
    
    if in_code_block:
        code_lines.append(line)
        i += 1
        continue
    
    if line.startswith('# '):
        if len(story) > 0:
            story.append(PageBreak())
        title = line[2:].strip()
        story.append(Paragraph(title, styles['CustomTitle'] if i == 0 else styles['CustomHeading1']))
        story.append(Spacer(1, 0.2*inch))
    elif line.startswith('## '):
        story.append(Paragraph(line[3:].strip(), styles['CustomHeading2']))
        story.append(Spacer(1, 0.15*inch))
    elif line.startswith('### '):
        story.append(Paragraph(line[4:].strip(), styles['CustomHeading3']))
        story.append(Spacer(1, 0.1*inch))
    elif line.startswith('- ') or line.startswith('* '):
        text = line[2:].strip()
        story.append(Paragraph(f"• {text}", styles['Normal']))
    elif re.match(r'^\d+\.\s', line):
        text = re.sub(r'^\d+\.\s', '', line)
        story.append(Paragraph(text, styles['Normal']))
    elif line.strip():
        line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
        line = re.sub(r'`(.*?)`', r'<font name="Courier" color="#667eea">\1</font>', line)
        story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 0.05*inch))
    else:
        if story and not isinstance(story[-1], Spacer):
            story.append(Spacer(1, 0.1*inch))
    
    i += 1

doc.build(story)

print(f"✓ PDF generated successfully: {output_file}")
print(f"✓ File size: {Path(output_file).stat().st_size / 1024:.2f} KB")
