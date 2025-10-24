from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from jinja2 import Template
from typing import Dict, Any
import markdown
import os
from datetime import datetime

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.darkblue,
            alignment=1,
            spaceAfter=30
        ))

        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.darkblue,
            spaceBefore=20,
            spaceAfter=10
        ))

    def generate_pdf_report(self, analysis_data: Dict[str, Any], output_path: str) -> str:
        """Generate a PDF report from analysis data."""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []

        # Title
        title = Paragraph("🧾 PROJECT FEASIBILITY REPORT", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))

        # Executive Summary
        if 'summary' in analysis_data and 'executive_summary' in analysis_data['summary']:
            story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
            exec_summary = analysis_data['summary']['executive_summary']
            story.append(Paragraph(exec_summary.get('project_overview', ''), self.styles['Normal']))
            story.append(Spacer(1, 10))

        # Project Highlights
        if 'summary' in analysis_data and 'project_highlights' in analysis_data['summary']:
            story.append(Paragraph("Project Highlights", self.styles['SectionHeader']))
            highlights = analysis_data['summary']['project_highlights']

            highlights_data = [
                ['Metric', 'Value'],
                ['Technology Stack', highlights.get('primary_technology_stack', 'N/A')],
                ['Estimated Timeline', highlights.get('estimated_timeline', 'N/A')],
                ['Estimated Cost', highlights.get('estimated_cost', 'N/A')],
                ['Team Size', str(highlights.get('team_size', 'N/A'))],
                ['Complexity Level', highlights.get('complexity_level', 'N/A')]
            ]

            table = Table(highlights_data, colWidths=[2*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(table)
            story.append(Spacer(1, 20))

        # Technical Recommendations
        if 'technical_analysis' in analysis_data and 'recommended_tech_stack' in analysis_data['technical_analysis']:
            story.append(Paragraph("Recommended Technology Stack", self.styles['SectionHeader']))
            tech_stack = analysis_data['technical_analysis']['recommended_tech_stack']

            for category, details in tech_stack.items():
                if isinstance(details, dict) and 'primary' in details:
                    story.append(Paragraph(f"<b>{category.title()}:</b> {details['primary']}", self.styles['Normal']))
                    if 'reasoning' in details:
                        story.append(Paragraph(f"<i>Reasoning:</i> {details['reasoning']}", self.styles['Normal']))
                    story.append(Spacer(1, 5))

        # Cost Breakdown
        if 'estimation_analysis' in analysis_data and 'cost_breakdown' in analysis_data['estimation_analysis']:
            story.append(Paragraph("Cost Breakdown", self.styles['SectionHeader']))
            cost_data = analysis_data['estimation_analysis']['cost_breakdown']

            cost_table_data = [['Cost Category', 'Amount']]
            for key, value in cost_data.items():
                if key != 'cost_range' and isinstance(value, (int, float)):
                    cost_table_data.append([key.replace('_', ' ').title(), f"${value:,.2f}"])

            cost_table = Table(cost_table_data, colWidths=[3*inch, 2*inch])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(cost_table)
            story.append(Spacer(1, 20))

        # Risks
        if 'summary' in analysis_data and 'major_risks' in analysis_data['summary']:
            story.append(Paragraph("Major Risks", self.styles['SectionHeader']))
            risks = analysis_data['summary']['major_risks']

            for risk in risks[:5]:  # Limit to top 5 risks
                if isinstance(risk, dict):
                    story.append(Paragraph(f"<b>{risk.get('risk', 'Unknown Risk')}</b>", self.styles['Normal']))
                    story.append(Paragraph(f"Impact: {risk.get('impact', 'N/A')}", self.styles['Normal']))
                    story.append(Paragraph(f"Mitigation: {risk.get('mitigation', 'N/A')}", self.styles['Normal']))
                    story.append(Spacer(1, 10))

        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"Generated by ProjectPilot on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, self.styles['Normal']))

        doc.build(story)
        return output_path

    def generate_markdown_report(self, analysis_data: Dict[str, Any]) -> str:
        """Generate a Markdown report from analysis data."""
        template_str = """
# 🧾 PROJECT FEASIBILITY REPORT

**Generated on:** {{ generation_date }}

## Executive Summary

{{ executive_summary.project_overview }}

### Key Findings
{% for finding in executive_summary.key_findings %}
- {{ finding }}
{% endfor %}

## Project Highlights

| Metric | Value |
|--------|-------|
| **Technology Stack** | {{ project_highlights.primary_technology_stack }} |
| **Estimated Timeline** | {{ project_highlights.estimated_timeline }} |
| **Estimated Cost** | {{ project_highlights.estimated_cost }} |
| **Team Size** | {{ project_highlights.team_size }} people |
| **Complexity Level** | {{ project_highlights.complexity_level }} |

## Recommended Technology Stack

{% for category, details in tech_stack.items() %}
### {{ category.title() }}
**Primary Choice:** {{ details.primary }}
**Reasoning:** {{ details.reasoning }}
{% if details.alternatives %}
**Alternatives:** {{ details.alternatives | join(', ') }}
{% endif %}

{% endfor %}

## Team Composition

{% for member in team_composition %}
- **{{ member.role }}** ({{ member.seniority }})
  - Duration: {{ member.duration_weeks }} weeks
  - Cost: ${{ member.total_cost }}
{% endfor %}

## Cost Breakdown

| Category | Amount |
|----------|--------|
{% for key, value in cost_breakdown.items() %}
{% if key != 'cost_range' %}
| {{ key.replace('_', ' ').title() }} | ${{ "{:,.2f}".format(value) }} |
{% endif %}
{% endfor %}

**Cost Range:** ${{ cost_breakdown.cost_range.minimum }} - ${{ cost_breakdown.cost_range.maximum }}

## Timeline Breakdown

{% for phase, details in timeline_breakdown.items() %}
{% if phase != 'total_duration_weeks' %}
### {{ phase.replace('_', ' ').title() }}
- **Duration:** {{ details.duration_weeks }} weeks
- **Activities:** {{ details.activities | join(', ') }}
{% endif %}
{% endfor %}

**Total Duration:** {{ timeline_breakdown.total_duration_weeks }} weeks

## Major Risks

{% for risk in major_risks %}
### {{ risk.risk }}
- **Impact:** {{ risk.impact }}
- **Mitigation:** {{ risk.mitigation }}
- **Priority:** {{ risk.priority }}

{% endfor %}

## Key Recommendations

{% for rec in key_recommendations %}
### {{ rec.recommendation }}
**Category:** {{ rec.category }}
**Rationale:** {{ rec.rationale }}
**Priority:** {{ rec.priority }}

{% endfor %}

## Next Steps

{% for step in next_steps %}
1. **{{ step.step }}**
   - Owner: {{ step.owner }}
   - Timeline: {{ step.timeline }}
   - Importance: {{ step.importance }}
{% endfor %}

---

*This report was generated by ProjectPilot AI Analysis System*
"""

        template = Template(template_str)

        # Extract data safely
        summary = analysis_data.get('summary', {})
        technical = analysis_data.get('technical_analysis', {})
        estimation = analysis_data.get('estimation_analysis', {})

        context = {
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'executive_summary': summary.get('executive_summary', {}),
            'project_highlights': summary.get('project_highlights', {}),
            'tech_stack': technical.get('recommended_tech_stack', {}),
            'team_composition': estimation.get('team_composition', []),
            'cost_breakdown': estimation.get('cost_breakdown', {}),
            'timeline_breakdown': estimation.get('timeline_breakdown', {}),
            'major_risks': summary.get('major_risks', []),
            'key_recommendations': summary.get('key_recommendations', []),
            'next_steps': summary.get('next_steps', [])
        }

        return template.render(**context)