from __future__ import annotations

import html
import re

SCRIPT_BLOCK_RE = re.compile(r"<\s*script\b[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL)
SCRIPT_RE = re.compile(r"<\s*/?\s*script\b[^>]*>", re.IGNORECASE)
EVENT_HANDLER_RE = re.compile(r"\son[a-z]+\s*=\s*(['\"]).*?\1", re.IGNORECASE)
JAVASCRIPT_URL_RE = re.compile(r"javascript\s*:", re.IGNORECASE)


def sanitize_message_content(value: str) -> str:
    without_script_blocks = SCRIPT_BLOCK_RE.sub("", value)
    without_scripts = SCRIPT_RE.sub("", without_script_blocks)
    without_handlers = EVENT_HANDLER_RE.sub("", without_scripts)
    without_js_urls = JAVASCRIPT_URL_RE.sub("", without_handlers)
    return html.escape(without_js_urls.strip(), quote=False)
