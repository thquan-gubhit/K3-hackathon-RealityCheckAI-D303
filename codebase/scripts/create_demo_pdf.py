"""Generate the stable Machine Learning PDF used by Phase 2 tests and demos."""

from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "tests" / "fixtures" / "demo_machine_learning.pdf"

SECTIONS = (
    (
        "1. Generalization and Data Splits",
        (
            "Generalization is a model's ability to perform well on examples "
            "that were not used during training. Training error measures fit "
            "on observed data, while validation error estimates behavior on "
            "held-out data.",
            "A training set is used to fit parameters. A validation set helps "
            "compare choices such as model complexity and regularization. A "
            "test set should remain untouched until the final evaluation.",
            "If decisions repeatedly use the test set, the test result becomes "
            "optimistic. The separation between training, validation, and test "
            "data protects the credibility of the final estimate.",
        ),
    ),
    (
        "2. Overfitting and Its Evidence",
        (
            "Overfitting occurs when a model captures details or noise that do "
            "not generalize. The model may achieve very low training error but "
            "substantially higher validation error.",
            "A widening training-validation gap is evidence of overfitting. "
            "Learning curves can reveal this gap as training continues or as "
            "model capacity increases.",
            "High training accuracy alone does not prove that a model is good. "
            "Performance must be checked on unseen data, and data leakage must "
            "be ruled out before interpreting the result.",
        ),
    ),
    (
        "3. Regularization and Early Stopping",
        (
            "Regularization discourages unnecessarily complex solutions. L1 "
            "and L2 penalties add a cost for large parameter values, while "
            "dropout reduces reliance on individual activations.",
            "Early stopping monitors validation performance and stops training "
            "when further optimization begins to reduce generalization. It is "
            "a practical control for iterative learning algorithms.",
            "A mitigation should match the evidence. Teams can simplify the "
            "model, collect more representative data, add regularization, or "
            "improve the validation procedure. No single technique guarantees "
            "better generalization in every setting.",
        ),
    ),
)


def _draw_page_chrome(canvas, document) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.line(24 * mm, height - 18 * mm, width - 24 * mm, height - 18 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(24 * mm, 12 * mm, "Adaptive Learning System - Demo Fixture")
    canvas.drawRightString(
        width - 24 * mm,
        12 * mm,
        f"Page {document.page}",
    )
    canvas.restoreState()


def build_demo_pdf(output_path: Path) -> Path:
    """Build the deterministic three-page demo PDF."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DemoTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=10 * mm,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=23,
        textColor=colors.HexColor("#1D4ED8"),
        spaceAfter=7 * mm,
    )
    body_style = ParagraphStyle(
        "DemoBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=17,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5 * mm,
    )
    note_style = ParagraphStyle(
        "DemoNote",
        parent=styles["BodyText"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#475569"),
    )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=24 * mm,
        leftMargin=24 * mm,
        topMargin=28 * mm,
        bottomMargin=22 * mm,
        title="Machine Learning Generalization",
        author="Adaptive Learning System",
        subject="Phase 2 parser and Knowledge Unit demo fixture",
    )

    story = []
    for index, (heading, paragraphs) in enumerate(SECTIONS):
        if index == 0:
            story.append(Paragraph("Machine Learning Generalization", title_style))
            story.append(
                Paragraph(
                    "A short source for PDF parsing and Knowledge Map tests.",
                    note_style,
                )
            )
            story.append(Spacer(1, 12 * mm))
        story.append(Paragraph(heading, heading_style))
        for paragraph in paragraphs:
            story.append(Paragraph(paragraph, body_style))
        if index < len(SECTIONS) - 1:
            story.append(PageBreak())

    document.build(
        story,
        onFirstPage=_draw_page_chrome,
        onLaterPages=_draw_page_chrome,
    )
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination PDF path.",
    )
    args = parser.parse_args()
    result = build_demo_pdf(args.output.resolve())
    print(f"Created demo PDF: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
