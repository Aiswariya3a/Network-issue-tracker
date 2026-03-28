from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models.status import STATUS_ACKNOWLEDGED, STATUS_NOT_RESOLVED, STATUS_RESOLVED


def generate_pie_chart(status_counts: dict[str, int], output_path: str = "status_chart.png") -> str:
    labels = []
    values = []
    for label in [STATUS_RESOLVED, STATUS_ACKNOWLEDGED, STATUS_NOT_RESOLVED]:
        count = int(status_counts.get(label, 0))
        if count > 0:
            labels.append(label)
            values.append(count)

    if not values:
        labels = ["No Issues"]
        values = [1]

    fig, ax = plt.subplots(figsize=(6, 4))
    colors_palette = {
        STATUS_RESOLVED: "#10b981",
        STATUS_ACKNOWLEDGED: "#f59e0b",
        STATUS_NOT_RESOLVED: "#ef4444",
    }
    colors_list = [colors_palette.get(label, "#94a3b8") for label in labels] if len(values) > 1 else ["#94a3b8"]
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=120, colors=colors_list)
    ax.set_title("Status Distribution")
    ax.axis("equal")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    return output_path


def generate_pdf_report(data: dict[str, Any], chart_path: str, output_path: str = "daily_report.pdf") -> str:
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story: list[Any] = []

    story.append(Paragraph("Daily Network Report", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Section 1: Summary", styles["Heading2"]))
    summary_rows = [
        ["Metric", "Value"],
        ["Total Issues", str(data["total_issues"])],
        [STATUS_RESOLVED, str(data["resolved_count"])],
        [STATUS_ACKNOWLEDGED, str(data.get("acknowledged_count", 0))],
        [STATUS_NOT_RESOLVED, str(data["not_resolved_count"])],
        ["Resolution %", f"{data['resolution_rate']:.2f}%"],
    ]
    summary_table = Table(summary_rows, colWidths=[200, 250])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Section 2: Key Insights", styles["Heading2"]))
    story.append(Paragraph(f"Top Issue Type: {data['top_issue_type']}", styles["BodyText"]))
    story.append(Paragraph(f"Most Affected Location: {data['most_affected_location']}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Section 3: Breakdown", styles["Heading2"]))
    issue_rows = [["Issue Type", "Count"]]
    for issue_type, count in data["issue_types"].items():
        issue_rows.append([issue_type, str(count)])
    if len(issue_rows) == 1:
        issue_rows.append(["None", "0"])

    status_rows = [["Status", "Count"]]
    for status in [STATUS_RESOLVED, STATUS_ACKNOWLEDGED, STATUS_NOT_RESOLVED]:
        status_rows.append([status, str(data["status_summary"].get(status, 0))])

    issue_table = Table(issue_rows, colWidths=[300, 150])
    issue_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ]
        )
    )
    story.append(issue_table)
    story.append(Spacer(1, 10))

    status_table = Table(status_rows, colWidths=[300, 150])
    status_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ]
        )
    )
    story.append(status_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Section 4: Chart", styles["Heading2"]))
    if Path(chart_path).exists():
        story.append(Image(chart_path, width=420, height=280))

    doc.build(story)
    return output_path
