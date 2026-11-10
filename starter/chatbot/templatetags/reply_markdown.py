"""Render the small Markdown subset used in assistant replies."""
import re

from django import template
from django.utils.html import escape, format_html, format_html_join

register = template.Library()


def inline_text(text):
    parts = re.split(r"\*\*([^*]+)\*\*", text)
    return format_html_join("", "{}", (
        (format_html("<strong>{}</strong>", part) if index % 2 else escape(part),)
        for index, part in enumerate(parts)
    ))


@register.filter
def reply_markdown(text):
    blocks = []
    bullets = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(("- ", "* ")):
            bullets.append(inline_text(line[2:]))
            continue
        if bullets:
            blocks.append(format_html("<ul>{}</ul>", format_html_join("", "<li>{}</li>", ((item,) for item in bullets))))
            bullets = []
        if line:
            blocks.append(format_html("<p>{}</p>", inline_text(line)))
    if bullets:
        blocks.append(format_html("<ul>{}</ul>", format_html_join("", "<li>{}</li>", ((item,) for item in bullets))))
    return format_html_join("", "{}", ((block,) for block in blocks))
