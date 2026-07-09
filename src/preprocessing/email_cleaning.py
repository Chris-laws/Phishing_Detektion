from __future__ import annotations

import html
import base64
import quopri
import re
from email import policy
from email.header import decode_header, make_header
from email.parser import BytesHeaderParser
from pathlib import Path


HTML_TAG_RE = re.compile(r"<[^>]+>")
HTML_LIKE_RE = re.compile(r"</?[a-zA-Z][^>]*>")
WHITESPACE_RE = re.compile(r"\s+")
HEADER_BODY_SPLIT_RE = re.compile(rb"\r?\n\r?\n", re.MULTILINE)


def normalize_whitespace(value: object) -> str:
    """Collapse whitespace and return a clean string."""
    if value is None:
        return ""
    return WHITESPACE_RE.sub(" ", str(value).replace("\x00", " ")).strip()


def strip_html(value: object) -> str:
    """Remove simple HTML markup and normalize HTML entities."""
    text = "" if value is None else str(value)
    if HTML_LIKE_RE.search(text):
        text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
        text = re.sub(r"(?i)<br\s*/?>", " ", text)
        text = re.sub(r"(?i)</p\s*>", " ", text)
        text = HTML_TAG_RE.sub(" ", text)
    return html.unescape(text)


def clean_text(value: object) -> str:
    return normalize_whitespace(strip_html(value))


def decode_subject(value: object) -> str:
    if value is None:
        return ""
    try:
        return clean_text(str(make_header(decode_header(str(value)))))
    except Exception:
        return clean_text(value)


def _payload_to_text(part) -> str:
    try:
        payload = part.get_payload(decode=True)
    except Exception:
        payload = None

    if isinstance(payload, bytes):
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")

    try:
        payload = part.get_payload()
    except Exception:
        return ""
    if isinstance(payload, list):
        return ""
    return "" if payload is None else str(payload)


def extract_body(message) -> str:
    plain_parts: list[str] = []
    html_parts: list[str] = []

    if message.is_multipart():
        for part in message.walk():
            if part.is_multipart():
                continue
            disposition = (part.get_content_disposition() or "").lower()
            if disposition == "attachment":
                continue
            content_type = (part.get_content_type() or "").lower()
            payload = _payload_to_text(part)
            if not payload:
                continue
            if content_type == "text/plain":
                plain_parts.append(payload)
            elif content_type == "text/html":
                html_parts.append(payload)
    else:
        content_type = (message.get_content_type() or "").lower()
        payload = _payload_to_text(message)
        if content_type == "text/html":
            html_parts.append(payload)
        else:
            plain_parts.append(payload)

    if plain_parts:
        return clean_text("\n".join(plain_parts))
    if html_parts:
        return clean_text("\n".join(html_parts))
    return ""


def parse_email_bytes(raw_bytes: bytes) -> dict[str, str | bool]:
    try:
        split = HEADER_BODY_SPLIT_RE.split(raw_bytes, maxsplit=1)
        header_bytes = split[0]
        body_bytes = split[1] if len(split) > 1 else b""
        headers = BytesHeaderParser(policy=policy.compat32).parsebytes(header_bytes)
        subject = decode_subject(headers.get("Subject", ""))

        content_type = (headers.get_content_type() or "").lower()
        if content_type.startswith("multipart/"):
            body = extract_multipart_body_fast(body_bytes, headers)
        else:
            body = decode_body_bytes(body_bytes, headers)
        parse_error = ""
    except Exception as exc:
        subject = ""
        body = raw_bytes.decode("utf-8", errors="replace")
        parse_error = str(exc)

    body = clean_text(body)
    subject = clean_text(subject)
    text = normalize_whitespace(f"{subject} {body}")
    return {
        "subject": subject,
        "body": body,
        "text": text,
        "parse_error": parse_error,
    }


def estimate_email_metadata(raw_bytes: bytes, sample_size: int = 20000) -> dict[str, object]:
    """Fast metadata extraction for manifest creation without full body parsing."""
    try:
        split = HEADER_BODY_SPLIT_RE.split(raw_bytes, maxsplit=1)
        header_bytes = split[0]
        body_bytes = split[1] if len(split) > 1 else b""
        headers = BytesHeaderParser(policy=policy.compat32).parsebytes(header_bytes)
        subject = decode_subject(headers.get("Subject", ""))
        sample = body_bytes[:sample_size]
        estimated_length = len(sample.strip())
        if len(body_bytes) > sample_size and sample_size > 0:
            estimated_length = int(estimated_length * (len(body_bytes) / sample_size))
        return {
            "parseable": True,
            "has_subject": bool(subject),
            "text_length_estimate": estimated_length,
        }
    except Exception:
        return {
            "parseable": bool(raw_bytes.strip()),
            "has_subject": False,
            "text_length_estimate": min(len(raw_bytes.strip()), sample_size),
        }


def extract_multipart_body_fast(body_bytes: bytes, headers) -> str:
    boundary = headers.get_boundary()
    if not boundary:
        return body_bytes.decode("utf-8", errors="replace")

    boundary_bytes = ("--" + boundary).encode("utf-8", errors="replace")
    plain_parts: list[str] = []
    html_parts: list[str] = []

    for raw_part in body_bytes.split(boundary_bytes):
        raw_part = raw_part.strip()
        if not raw_part or raw_part == b"--":
            continue
        if raw_part.endswith(b"--"):
            raw_part = raw_part[:-2].strip()

        split = HEADER_BODY_SPLIT_RE.split(raw_part, maxsplit=1)
        if len(split) < 2:
            continue
        part_header_bytes, part_body_bytes = split
        try:
            part_headers = BytesHeaderParser(policy=policy.compat32).parsebytes(part_header_bytes)
        except Exception:
            continue

        disposition = str(part_headers.get("Content-Disposition", "")).lower()
        if "attachment" in disposition:
            continue

        part_type = (part_headers.get_content_type() or "").lower()
        decoded = decode_body_bytes(part_body_bytes, part_headers)
        if not decoded:
            continue
        if part_type == "text/plain":
            plain_parts.append(decoded)
        elif part_type == "text/html":
            html_parts.append(decoded)

    if plain_parts:
        return "\n".join(plain_parts)
    if html_parts:
        return "\n".join(html_parts)
    return body_bytes.decode("utf-8", errors="replace")


def decode_body_bytes(body_bytes: bytes, headers) -> str:
    transfer_encoding = str(headers.get("Content-Transfer-Encoding", "")).lower()
    payload = body_bytes
    try:
        if "quoted-printable" in transfer_encoding:
            payload = quopri.decodestring(payload)
        elif "base64" in transfer_encoding:
            payload = base64.b64decode(payload, validate=False)
    except Exception:
        payload = body_bytes

    charset = headers.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except LookupError:
        return payload.decode("utf-8", errors="replace")


def read_email_file(path: Path) -> dict[str, str | bool]:
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        return {
            "subject": "",
            "body": "",
            "text": "",
            "parse_error": f"read_error: {exc}",
        }

    parsed = parse_email_bytes(raw_bytes)
    if not parsed["text"]:
        fallback = clean_text(raw_bytes.decode("utf-8", errors="replace"))
        parsed["body"] = fallback
        parsed["text"] = fallback
        if not parsed["parse_error"]:
            parsed["parse_error"] = "empty_after_email_parse_fallback_used"
    return parsed
