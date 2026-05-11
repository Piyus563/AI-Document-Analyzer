"""
pdf_exporter.py
Generates a downloadable PDF report from analysis results.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER
import io


def generate_report_pdf(filename: str, analysis: dict) -> bytes:
    """Generate a formatted PDF report from analysis results."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)

    styles = getSampleStyleSheet()
    title_style   = ParagraphStyle("Title",   parent=styles["Title"],   fontSize=20, textColor=colors.HexColor("#4F46E5"), spaceAfter=6, alignment=TA_CENTER)
    heading_style = ParagraphStyle("Heading", parent=styles["Heading2"],fontSize=13, textColor=colors.HexColor("#1E293B"), spaceBefore=14, spaceAfter=4)
    body_style    = ParagraphStyle("Body",    parent=styles["Normal"],  fontSize=10, leading=16, textColor=colors.HexColor("#334155"))
    tag_style     = ParagraphStyle("Tag",     parent=styles["Normal"],  fontSize=9,  textColor=colors.HexColor("#4F46E5"), backColor=colors.HexColor("#EEF2FF"), borderPadding=3)
    score_style   = ParagraphStyle("Score",   parent=styles["Normal"],  fontSize=11, textColor=colors.HexColor("#1E293B"), spaceBefore=4)

    story = []

    # Title
    doc_type = analysis.get("doc_type", {}).get("type", "General")
    story.append(Paragraph("AI Document Analysis Report", title_style))
    story.append(Paragraph(f"File: {filename} &nbsp;&nbsp;|&nbsp;&nbsp; Type: {doc_type}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0")))
    story.append(Spacer(1, 0.1 * inch))

    # Overall Scores
    scores = analysis.get("scores", {})
    if scores:
        story.append(Paragraph("Overall AI Score", heading_style))
        story.append(Paragraph(f"<b>Grammar Score:</b> {scores.get('grammar', 'N/A')}/100", score_style))
        story.append(Paragraph(f"<b>Readability Score:</b> {scores.get('readability', 'N/A')}/100", score_style))
        story.append(Paragraph(f"<b>Content Quality Score:</b> {scores.get('content_quality', 'N/A')}/100", score_style))
        story.append(Paragraph(f"<b>Overall AI Score:</b> {scores.get('overall', 'N/A')}/100", score_style))
        story.append(Spacer(1, 0.1 * inch))

    # Short Summary
    story.append(Paragraph("Short Summary", heading_style))
    story.append(Paragraph(analysis.get("short_summary", "N/A"), body_style))
    story.append(Spacer(1, 0.1 * inch))

    # Detailed Summary
    story.append(Paragraph("Detailed Summary", heading_style))
    story.append(Paragraph(analysis.get("summary", "N/A"), body_style))
    story.append(Spacer(1, 0.1 * inch))

    # Readability
    readability = analysis.get("readability", {})
    if readability:
        story.append(Paragraph("Readability Analysis", heading_style))
        story.append(Paragraph(f"<b>Level:</b> {readability.get('level', 'N/A')} &nbsp;|&nbsp; <b>Flesch Score:</b> {readability.get('flesch_score', 'N/A')}/100", body_style))
        story.append(Paragraph(f"<b>Avg Sentence Length:</b> {readability.get('avg_sentence_length', 'N/A')} words &nbsp;|&nbsp; <b>Reading Time:</b> {readability.get('reading_time', 'N/A')}", body_style))
        story.append(Paragraph(f"<b>Passive Voice:</b> {readability.get('passive_voice_pct', 0)}% of sentences", body_style))
        if readability.get("difficult_words"):
            story.append(Paragraph(f"<b>Difficult Words:</b> {', '.join(readability['difficult_words'][:10])}", body_style))
        story.append(Spacer(1, 0.1 * inch))

    # Keywords
    story.append(Paragraph("Top Keywords", heading_style))
    keywords = analysis.get("keywords", [])
    if keywords:
        story.append(Paragraph("  •  ".join(keywords), tag_style))
    story.append(Spacer(1, 0.1 * inch))

    # Sentiment
    sentiment = analysis.get("sentiment", {})
    story.append(Paragraph("Sentiment Analysis", heading_style))
    story.append(Paragraph(f"<b>Sentiment:</b> {sentiment.get('sentiment', 'N/A')} | <b>Confidence:</b> {sentiment.get('confidence', 'N/A')}", body_style))
    if sentiment.get("explanation"):
        story.append(Paragraph(sentiment["explanation"], body_style))
    story.append(Spacer(1, 0.1 * inch))

    # AI Feedback
    ai_feedback = analysis.get("ai_feedback", [])
    if ai_feedback:
        story.append(Paragraph("AI Feedback & Suggestions", heading_style))
        for fb in ai_feedback:
            story.append(Paragraph(f"<b>{fb.get('icon','')} {fb.get('title','')}</b>", body_style))
            story.append(Paragraph(fb.get("detail", ""), body_style))
            story.append(Spacer(1, 0.05 * inch))

    # Q&A
    qa_pairs = analysis.get("qa_pairs", [])
    if qa_pairs:
        story.append(Paragraph("Questions & Answers", heading_style))
        for i, qa in enumerate(qa_pairs, 1):
            story.append(Paragraph(f"<b>Q{i}: {qa['question']}</b>", body_style))
            story.append(Paragraph(f"A: {qa['answer']}", body_style))
            story.append(Spacer(1, 0.05 * inch))

    # Section Insights
    section_insights = analysis.get("section_insights", [])
    if section_insights:
        story.append(Paragraph("Section Insights", heading_style))
        for item in section_insights:
            story.append(Paragraph(f"<b>Section {item['section']}:</b> {item['insight']}", body_style))
            story.append(Spacer(1, 0.05 * inch))

    # Errors
    errors = analysis.get("errors", {})
    if errors and errors.get("summary", {}).get("total", 0) > 0:
        story.append(Paragraph("Grammar & Writing Issues", heading_style))
        summary = errors["summary"]
        story.append(Paragraph(f"<b>Total Issues Found:</b> {summary['total']}", body_style))
        if errors.get("spelling"):
            spellings = ", ".join([f"{e['word']} → {e['suggestion']}" for e in errors["spelling"][:10]])
            story.append(Paragraph(f"<b>Spelling:</b> {spellings}", body_style))
        if errors.get("passive_voice"):
            story.append(Paragraph(f"<b>Passive Voice:</b> {summary['passive_voice_count']} instances. Use active voice.", body_style))
        if errors.get("long_sentences"):
            story.append(Paragraph(f"<b>Long Sentences:</b> {summary['long_sentences_count']} sentences exceed 40 words.", body_style))
        story.append(Spacer(1, 0.05 * inch))

    doc.build(story)
    return buffer.getvalue()
