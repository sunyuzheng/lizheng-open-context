#!/usr/bin/env python3
"""Dependency-free lexical search for the open context repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
HAN_RUN = re.compile(r"[\u3400-\u9fff]+")
WORD = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_+.-]+")
PROVENANCE_FIELDS = (
    "author", "publisher", "original_author", "original_source_url",
    "original_published_at", "content_origin", "generation_method", "evidence_role",
    "yuzheng_stance_weight", "attribution_note", "source_family", "source_context",
    "language", "license", "rights_scope",
    "source_video_id", "generated_at", "translation_publication_status", "original_language",
    "snapshot_at",
    "source_visibility", "text_access", "membership_platform", "membership_url",
    "membership_verified_at", "transcript_source_kind", "transcript_quality",
    "speaker_classification",
    "data_layer", "speaker_id", "speaker_name", "speaker_status", "fragment_id",
    "source_snapshot_sha256", "participant_names", "participant_entity_ids",
    "participant_aliases", "participant_metadata_basis", "speech_act",
)


@dataclass
class Document:
    id: str
    source_id: str
    title: str
    section: str
    source_type: str
    source_url: str
    published_at: str
    text: str
    path: str
    content_status: str = "current"
    author: str = ""
    publisher: str = ""
    original_author: str = ""
    original_source_url: str = ""
    original_published_at: str = ""
    content_origin: str = ""
    generation_method: str = ""
    evidence_role: str = ""
    yuzheng_stance_weight: str = "not-evidence"
    attribution_note: str = ""
    source_family: str = ""
    source_context: str = ""
    language: str = ""
    license: str = ""
    rights_scope: str = ""
    source_video_id: str = ""
    generated_at: str = ""
    translation_publication_status: str = ""
    original_language: str = ""
    snapshot_at: str = ""
    source_visibility: str = ""
    text_access: str = ""
    membership_platform: str = ""
    membership_url: str = ""
    membership_verified_at: str = ""
    transcript_source_kind: str = ""
    transcript_quality: str = ""
    speaker_classification: str = ""
    data_layer: str = "raw"
    speaker_id: str = ""
    speaker_name: str = ""
    speaker_status: str = ""
    fragment_id: str = ""
    source_snapshot_sha256: str = ""
    participant_names: str = ""
    participant_entity_ids: str = ""
    participant_aliases: str = ""
    participant_metadata_basis: str = ""
    speech_act: str = ""


def provenance_fields(meta: dict) -> dict[str, str]:
    """Carry attribution into every chunk; absent evidence never implies endorsement."""
    fields = {key: str(meta.get(key) or "") for key in PROVENANCE_FIELDS}
    participants = meta.get("participant_names") or meta.get("guest_names") or ""
    fields["participant_names"] = "；".join(participants) if isinstance(participants, list) else str(participants)
    for key in ("participant_entity_ids", "participant_aliases"):
        value = meta.get(key) or ""
        fields[key] = "；".join(value) if isinstance(value, list) else str(value)
    fields["yuzheng_stance_weight"] = str(meta.get("yuzheng_stance_weight") or "not-evidence")
    fields["source_family"] = str(
        meta.get("source_family") or meta.get("original_source_url")
        or meta.get("source_url") or meta.get("url") or meta.get("id") or ""
    )
    fields["data_layer"] = str(meta.get("data_layer") or (
        "derived" if str(meta.get("content_origin") or "").startswith("ai-")
        or meta.get("source_type") in {"context", "book-framework", "video-translation", "video-annotation"}
        else "raw"
    ))
    if not fields["speaker_id"] and meta.get("speaker_classification") in {"solo-yuzheng", "yuzheng-turns-reviewed"}:
        fields.update(speaker_id="yuzheng", speaker_name="立正", speaker_status="reviewed-source-attribution")
    elif not fields["speaker_id"] and meta.get("speaker_classification") in {"mixed-speakers", "mixed-or-unresolved"}:
        fields.update(speaker_id="unknown", speaker_status="unresolved")
    return fields


TIMED_CUE = re.compile(r"(?m)^\[(\d{2}:\d{2}:\d{2})\]\((https://www\.youtube\.com/watch\?v=[^)]+)\)\s+(.+)$")


def excerpt_blocks(body: str) -> list[tuple[str, str, str]]:
    """Separate reviewed verbatim quotations from AI headings and context lines."""
    blocks = []
    for section in re.split(r"(?m)(?=^##\s+)", body):
        heading = re.search(r"(?m)^##\s+(.+)$", section)
        if not heading:
            continue
        link = re.search(r"\[\d{2}:\d{2}:\d{2}\]\((https://www\.youtube\.com/watch\?v=[^)]+)\)", section)
        quotes = re.findall(r"(?m)^>\s?(.*)$", section)
        if not link or not quotes:
            raise ValueError("Reviewed excerpt lacks its timestamp or original quotation")
        quotation = "\n".join(quotes)
        annotation = re.sub(r"(?m)^>.*(?:\n|$)", "", section).strip()
        blocks.append((link.group(1), quotation, annotation))
    return blocks


def excerpt_documents(path: Path, meta: dict, body: str) -> list[Document]:
    documents = []
    source_id = str(meta.get("id") or path.stem)
    for index, (url, quotation, annotation) in enumerate(excerpt_blocks(body), 1):
        fragment = f"{source_id}#quote-{index}"
        raw_fields = provenance_fields(meta)
        raw_fields.update(data_layer="raw", fragment_id=fragment)
        # A timestamp is source metadata; AI-written headings are not speech.
        stamp = re.search(r"\[(\d{2}:\d{2}:\d{2})\]", annotation).group(1)
        common = dict(source_id=source_id, title=str(meta.get("title") or path.stem),
                      section="", source_url=url, published_at=str(meta.get("published_at") or ""),
                      path=str(path.relative_to(ROOT)), content_status=str(meta.get("content_status") or "current"))
        documents.append(Document(id=fragment, source_type="video-excerpt",
                                  text=f"[{stamp}]({url}) {quotation}", **common, **raw_fields))
        derived_fields = dict(raw_fields, data_layer="derived", author="AI", original_author="See referenced raw speech",
                              content_origin="ai-synthesis", generation_method="ai-written",
                              evidence_role="secondary-synthesis", yuzheng_stance_weight="secondary-only",
                              speaker_id="", speaker_name="", speaker_status="not-speech")
        documents.append(Document(id=f"{source_id}#annotation-{index}", source_type="video-annotation",
                                  text=annotation, **common, **derived_fields))
    return documents


def parse_scalar(value: str):
    value = value.strip()
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def chunk_markdown(body: str, source_type: str, target_chars: int = 3200) -> list[tuple[str, str]]:
    """Split long sources without losing headings or timestamp links."""
    if source_type in {"video-transcript", "video-translation"}:
        sections = [body]
    else:
        sections = [part for part in re.split(r"(?m)(?=^##\s+)", body) if part.strip()]
    chunks: list[tuple[str, str]] = []
    for section_text in sections:
        heading_match = re.search(r"(?m)^#{2,6}\s+(.+?)\s*$", section_text)
        section_name = heading_match.group(1).strip() if heading_match else ""
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", section_text) if part.strip()]
        current: list[str] = []
        current_size = 0
        for paragraph in paragraphs:
            if current and current_size + len(paragraph) > target_chars:
                chunks.append((section_name, "\n\n".join(current)))
                current = current[-1:] if source_type in {"video-transcript", "video-translation"} else []
                current_size = sum(len(part) for part in current)
            current.append(paragraph)
            current_size += len(paragraph)
        if current:
            chunks.append((section_name, "\n\n".join(current)))
    return chunks or [("", body)]


def published_section_records(root: Path) -> list[dict]:
    """Exact, source-bound classifications; never infer authorship from keywords."""
    policy = root / "config/source-section-layers.json"
    if (root / "config").is_symlink() or policy.is_symlink():
        raise ValueError("Published section policy cannot be a symlink")
    if not policy.exists():
        return []
    def unique_pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate published section JSON key")
            result[key] = value
        return result
    data = json.loads(policy.read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data.get("schema_version") != 1 or not isinstance(data.get("records"), list):
        raise ValueError("Invalid published section policy")
    records, seen = [], set()
    for row in data["records"]:
        if not isinstance(row, dict):
            raise ValueError("Invalid published section record")
        relative = row.get("path", "")
        if not isinstance(relative, str) or not relative.startswith("corpus/community-posts/") or not relative.endswith(".md"):
            raise ValueError("Published section path is outside the source corpus")
        parts = Path(relative).parts
        if len(parts) != 3 or any(part in {".", ".."} or part.startswith(".") for part in parts) or relative in seen:
            raise ValueError("Duplicate or unsafe published section path")
        if not isinstance(row.get("source_id"), str) or not row["source_id"] or not re.fullmatch(r"[a-f0-9]{64}", str(row.get("source_sha256", ""))):
            raise ValueError("Published section source identity is missing")
        marker, whole, end = row.get("start_marker"), row.get("whole_body"), row.get("end_marker")
        if not ((isinstance(marker, str) and marker.strip() and "\n" not in marker and whole is None
                 and (end is None or isinstance(end, str) and end.strip() and "\n" not in end))
                or (marker is None and whole is True and end is None)):
            raise ValueError("Published section boundary is not explicit")
        if row.get("layer") != "derived" or not isinstance(row.get("classification_basis"), str) or not row["classification_basis"].strip():
            raise ValueError("Published section classification lacks its source basis")
        allowed = {
            ("AI", "ai-synthesis", "source-declared-ai-written"),
            ("整理者（未确认）", "published-editorial-adaptation", "source-declared-editorial-adaptation"),
            ("AI与原发布者（逐段归属未核）", "ai-synthesis-of-mixed-sources", "source-declared-ai-with-editorial-notes"),
        }
        if (row.get("writer"), row.get("content_origin"), row.get("generation_method")) not in allowed:
            raise ValueError("Published section writer classification is unsupported")
        seen.add(relative)
        records.append(row)
    return records


def published_source_parts(path: Path, meta: dict, body: str):
    relative = str(path.relative_to(ROOT))
    row = next((row for row in published_section_records(ROOT) if row["path"] == relative), None)
    if row is None:
        return None
    if any((ROOT / Path(*Path(relative).parts[:depth])).is_symlink() for depth in range(1, len(Path(relative).parts) + 1)):
        raise ValueError("Published section source cannot be a symlink")
    if meta.get("id") != row["source_id"] or meta.get("source_snapshot_sha256") != row["source_sha256"]:
        raise ValueError("Published section source hash or identity changed")
    suffix = ""
    if row.get("whole_body"):
        prefix, derived = "", body
    else:
        marker = row["start_marker"]
        matches = list(re.finditer(r"(?m)^" + re.escape(marker) + r"[ \t]*$", body))
        if len(matches) != 1:
            raise ValueError("Published section boundary changed")
        boundary = matches[0].start()
        prefix, derived = body[:boundary], body[boundary:]
        if row.get("end_marker"):
            ends = list(re.finditer(r"(?m)^" + re.escape(row["end_marker"]) + r"[ \t]*$", body))
            if len(ends) != 1 or ends[0].start() <= boundary:
                raise ValueError("Published section end boundary changed")
            derived, suffix = body[boundary:ends[0].start()], body[ends[0].start():]
    if not derived.strip():
        raise ValueError("Published section body is empty")
    derived_meta = {
        "data_layer": "derived", "author": row["writer"], "original_author": row["writer"],
        "content_origin": row["content_origin"], "generation_method": row["generation_method"],
        "evidence_role": "secondary-synthesis", "yuzheng_stance_weight": "secondary-only",
        "speaker_id": "", "speaker_name": "", "speaker_status": "not-speech",
        "attribution_note": row["classification_basis"] + " 发布账号归属不等于整理者或发言者归属；整理稿中的引语须核对原始逐字稿，不能作为逐字原话。",
    }
    parts = [("raw", prefix, {"data_layer": "raw"})] if prefix.strip() else []
    tail = [("raw-suffix", suffix, {"data_layer": "raw"})] if suffix.strip() else []
    return [*parts, ("derived", derived, derived_meta), *tail]


def validate_published_sections(root: Path) -> None:
    """Verify every classified source even if it is not retrieved this time."""
    previous = ROOT
    try:
        globals()["ROOT"] = root
        for row in published_section_records(root):
            if not (root / row["path"]).is_file():
                raise ValueError("Published section source is missing")
            parse_markdown(root / row["path"])
    finally:
        globals()["ROOT"] = previous


def parse_markdown(path: Path) -> list[Document]:
    raw = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(raw)
    meta: dict[str, object] = {}
    body = raw
    if match:
        body = raw[match.end() :]
        for line in match.group(1).splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            meta[key.strip()] = parse_scalar(value)
    source_id = str(meta.get("id") or path.stem)
    source_type = str(meta.get("source_type") or "context")
    meta.setdefault("source_type", source_type)
    source_url = str(meta.get("source_url") or "")
    meta["source_snapshot_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    # Boilerplate attribution belongs in metadata, not in lexical relevance scores.
    body = re.sub(r"<!-- provenance:start -->.*?<!-- provenance:end -->", "", body, flags=re.S)
    if source_type in {"community-post", "knowledge-bank"} and meta.get("source_visibility") == "public":
        # This exact archive-added notice is not a paragraph from the publication.
        notice = (f'> 原文：[{meta.get("title", "")}]({source_url}) · 发布于 '
                  f'{str(meta.get("published_at", ""))[:10]} · 原始空间公开可见。'
                  '本文保留发表时语境；其中第三方引文、发言、链接与商标不随正文重新授权。')
        body = re.sub(r"(?m)^" + re.escape(notice) + r"[ \t]*(?:\n|$)", "", body, count=1)
    if source_type == "video-excerpt":
        return excerpt_documents(path, meta, body)
    parts = published_source_parts(path, meta, body)
    if parts is not None:
        documents = []
        for layer, part, overrides in parts:
            for index, (section, text) in enumerate(chunk_markdown(part, source_type), 1):
                fragment = f"{source_id}#{layer}-chunk-{index}"
                fields = provenance_fields({**meta, **overrides, "fragment_id": fragment})
                documents.append(Document(
                    id=fragment, source_id=source_id, title=str(meta.get("title") or path.stem),
                    section=section, source_type=source_type, source_url=source_url,
                    published_at=str(meta.get("published_at") or ""), text=text,
                    path=str(path.relative_to(ROOT)), content_status=str(meta.get("content_status") or "current"),
                    **fields,
                ))
        return documents
    if source_type == "video-transcript":
        # Introductory editorial notices are metadata, not transcribed words.
        timed = [match.group(0) for match in TIMED_CUE.finditer(body)]
        if timed:
            body = "\n\n".join(timed)
    documents = []
    for index, (section, text) in enumerate(chunk_markdown(body, source_type), 1):
        timestamp_link = re.search(
            r"\[\d{2}:\d{2}:\d{2}\]\((https://www\.youtube\.com/watch\?v=[^)]+)\)",
            text,
        )
        documents.append(
            Document(
                id=f"{source_id}#chunk-{index}",
                source_id=source_id,
                title=str(meta.get("title") or path.stem),
                section=section,
                source_type=source_type,
                source_url=timestamp_link.group(1) if timestamp_link else source_url,
                published_at=str(meta.get("published_at") or ""),
                text=text,
                path=str(path.relative_to(ROOT)),
                content_status=str(meta.get("content_status") or "current"),
                **provenance_fields(meta),
            )
        )
    return documents


def load_documents() -> list[Document]:
    docs: list[Document] = []
    full_ids: set[str] = set()
    structured = []
    for path in sorted(ROOT.glob("corpus/dialogues/*.json")):
        structured.extend(parse_raw_dialogue(path))
    structured_ids = {doc.source_id for doc in structured}
    for pattern in (
        "context/*.md",
        "examples/*.md",
        "corpus/community-posts/*.md",
        "corpus/community-comments/*.md",
        "corpus/videos/*.md",
        "corpus/english-community/*.md",
        "corpus/english-translations/*.md",
        "corpus/course-lessons/*.md",
        "corpus/book-chapters/*.md",
        "corpus/blog-posts/*.md",
        "corpus/conversation-excerpts/*.md",
    ):
        for path in sorted(ROOT.glob(pattern)):
            parsed = parse_markdown(path)
            if pattern == "corpus/videos/*.md" and any(doc.source_id in structured_ids for doc in parsed):
                continue
            docs.extend(parsed)
            full_ids.update(doc.source_id for doc in parsed)
    docs.extend(structured)
    full_ids.update(structured_ids)
    for catalog_name, source_type in (
        ("knowledge-bank.jsonl", "knowledge-bank-catalog"),
        ("videos.jsonl", "video-catalog"),
        ("english-community.jsonl", "english-community-catalog"),
        ("english-translations.jsonl", "video-translation-catalog"),
    ):
        path = ROOT / "catalog" / catalog_name
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["id"] in full_ids:
                continue
            docs.append(
                Document(
                    id=row["id"],
                    source_id=row["id"],
                    title=row["title"],
                    section="",
                    source_type=source_type,
                    source_url=row.get("url", ""),
                    published_at=row.get("published_at") or "",
                    text=" ".join(row.get("guest_names") or []),
                    path=str(path.relative_to(ROOT)),
                    content_status=str(row.get("content_status") or "current"),
                    **provenance_fields(row),
                )
            )
    return docs


def parse_raw_dialogue(path: Path) -> list[Document]:
    """Load an explicitly supplied structured source, preserving unknown speakers.

    This is not an admission or publication decision. Public callers still verify
    their release manifest; the offline candidate tool remains local-only.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("data_layer") != "raw":
        raise ValueError("Expected a versioned raw dialogue source")
    units = data.get("units")
    if not isinstance(units, list) or not units:
        raise ValueError("Raw dialogue has no source units")
    identity = str(data.get("id") or "")
    if not identity or not str(data.get("source_url") or "").startswith("https://www.youtube.com/watch?v="):
        raise ValueError("Raw dialogue source identity is missing")
    source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    documents = []
    seen = set()
    current = []
    speaker = None
    size = 0
    def emit():
        if not current:
            return
        # Keep placeholders in the canonical source units, but they are not
        # searchable speech. This does not establish silence in the media.
        if all(re.fullmatch(r"<\s*No Speech\s*>", unit["text"].strip(), flags=re.I) for unit in current):
            return
        first = current[0]
        start = int(first["start_seconds"])
        stamp = f"{start // 3600:02}:{start % 3600 // 60:02}:{start % 60:02}"
        url = str(data["source_url"]).split("&t=", 1)[0] + f"&t={start}s"
        fields = provenance_fields(data)
        known = first["speaker_id"] != "unknown"
        fields.update(data_layer="raw", speaker_id=first["speaker_id"], speaker_name=first.get("speaker_name", ""),
                      speaker_status=first.get("speaker_status", "unresolved"), source_snapshot_sha256=source_hash,
                      speech_act=first.get("speech_act", "unclassified"),
                      fragment_id=f"{identity}#{current[0]['id']}-{current[-1]['id']}")
        if known:
            fields.update(author=first.get("speaker_name") or first["speaker_id"], original_author=first.get("speaker_name") or first["speaker_id"])
        else:
            fields.update(author="说话人待核", original_author="说话人待核")
        if first["speaker_id"] == "yuzheng":
            fields.update(content_origin="yuzheng-spoken-source", evidence_role="primary-speech",
                          yuzheng_stance_weight="direct-with-quotation-boundaries", speaker_classification="yuzheng-turns-reviewed")
        if first["speaker_id"] != "yuzheng":
            fields.update(content_origin="mixed-or-unresolved-speech", evidence_role="speaker-attributed-speech",
                          yuzheng_stance_weight="not-evidence")
        if first.get("speech_act") in {"question", "introduction", "acknowledgement", "joke", "reported-other"}:
            fields["yuzheng_stance_weight"] = "not-evidence"
        texts = []
        for unit in current:
            t = int(unit["start_seconds"])
            timestamp = f"{t // 3600:02}:{t % 3600 // 60:02}:{t % 60:02}"
            link = str(data["source_url"]).split("&t=", 1)[0] + f"&t={t}s"
            texts.append(f"[{timestamp}]({link}) {unit['text']}")
        documents.append(Document(id=fields["fragment_id"], source_id=identity, title=str(data.get("title") or identity),
                                  section="", source_type="video-transcript", source_url=url,
                                  published_at=str(data.get("published_at") or ""), text="\n\n".join(texts),
                                  path=str(path.relative_to(ROOT)), **fields))
    for unit in units:
        if (not isinstance(unit, dict) or not isinstance(unit.get("text"), str) or not unit["text"].strip()
                or not isinstance(unit.get("id"), str) or unit["id"] in seen
                or not isinstance(unit.get("start_seconds"), (float, int)) or isinstance(unit["start_seconds"], bool)
                or unit["start_seconds"] < 0 or not math.isfinite(unit["start_seconds"])
                or not isinstance(unit.get("end_seconds"), (float, int)) or isinstance(unit["end_seconds"], bool)
                or not math.isfinite(unit["end_seconds"]) or unit["end_seconds"] < unit["start_seconds"]
                or not isinstance(unit.get("speaker_id"), str) or not unit["speaker_id"]):
            raise ValueError("Invalid raw dialogue source unit")
        if unit["speaker_id"] != "unknown" and unit.get("speaker_status") not in {"reviewed-source-attribution", "audio-anchor-reviewed"}:
            raise ValueError("Named raw speaker lacks reviewed attribution")
        seen.add(unit["id"])
        owner = (unit["speaker_id"], unit.get("speaker_name", ""), unit.get("speaker_status", "unresolved"), unit.get("speech_act", "unclassified"))
        if current and (owner != speaker or size + len(unit["text"]) > 2600):
            emit(); current = []; size = 0
        current.append(unit); size += len(unit["text"]); speaker = owner
    emit()
    return documents


def query_terms(query: str) -> list[str]:
    lowered = query.lower().strip()
    terms = set(WORD.findall(lowered))
    for run in HAN_RUN.findall(lowered):
        if len(run) == 1:
            terms.add(run)
        else:
            terms.update(run[i : i + 2] for i in range(len(run) - 1))
    return sorted((term for term in terms if term), key=len, reverse=True)


def score(
    doc: Document,
    query: str,
    terms: list[str],
    document_frequency: dict[str, int],
    document_count: int,
    average_length: float,
) -> float:
    title = (doc.title + "\n" + doc.section + "\n" + doc.participant_names + "\n" + doc.participant_aliases + "\n" + doc.source_context).lower()
    body = re.sub(r"\]\([^)]+\)", "]", doc.text).lower()
    query_lower = query.lower().strip()
    value = 0.0
    if query_lower and query_lower in title:
        value += 40
    if query_lower and query_lower in body:
        value += 10
    length = max(1, len(body))
    k1 = 1.35
    b = 0.78
    for term in terms:
        df = document_frequency.get(term, 0)
        inverse_frequency = math.log(1 + (document_count - df + 0.5) / (df + 0.5))
        if term in title:
            value += inverse_frequency * 5.5
        frequency = body.count(term)
        if frequency:
            normalized = frequency * (k1 + 1) / (
                frequency + k1 * (1 - b + b * length / average_length)
            )
            value += inverse_frequency * normalized
    status_weight = {"current": 1.0, "archived": 0.55, "test": 0.2}.get(
        doc.content_status, 1.0
    )
    # Relevance is not authority: authorship and stance labels never boost this score.
    return value * status_weight


def snippet(doc: Document, query: str, terms: list[str], width: int = 220) -> str:
    plain = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1 (\2)", doc.text)
    plain = re.sub(r"[#>*`]", "", plain)
    plain = re.sub(r"\s+", " ", plain).strip()
    lowered = plain.lower()
    needles = [query.lower().strip(), *terms]
    positions = [lowered.find(term) for term in needles if term and lowered.find(term) >= 0]
    start = max(0, (min(positions) if positions else 0) - width // 3)
    end = min(len(plain), start + width)
    prefix = "…" if start else ""
    suffix = "…" if end < len(plain) else ""
    return prefix + plain[start:end] + suffix


def type_matches(doc: Document, requested: str) -> bool:
    if requested == "all":
        return True
    if requested == "video":
        return doc.source_type in {"video-transcript", "video-excerpt", "video-annotation", "video-catalog", "video-translation", "video-translation-catalog"}
    if requested == "knowledge-bank":
        return doc.source_type in {"knowledge-bank", "knowledge-bank-catalog"}
    if requested == "community":
        return doc.source_type in {"knowledge-bank", "community-post", "community-comment", "english-community", "english-community-catalog"}
    if requested == "english":
        return doc.language == "en" or doc.source_type in {"english-community", "english-community-catalog"}
    if requested == "comment":
        return doc.source_type == "community-comment"
    if requested == "context":
        return doc.source_type in {"context", "book-framework"}
    if requested == "course":
        return doc.source_type == "course-lesson"
    if requested == "book":
        return doc.source_type == "book-chapter"
    if requested == "blog":
        return doc.source_type == "blog-post"
    if requested == "excerpt":
        return doc.source_type == "video-excerpt"
    return doc.source_type == requested


def license_matches(doc: Document, requested: str) -> bool:
    """`open` keeps only material anyone may reuse, including commercially: CC BY text and CC0 catalog entries."""
    if requested == "all":
        return True
    return doc.license == "CC-BY-4.0" or doc.source_type.endswith("-catalog")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument(
        "--type",
        choices=["all", "context", "knowledge-bank", "community", "comment", "video", "excerpt", "english", "course", "book", "blog"],
        default="all",
    )
    parser.add_argument(
        "--license",
        choices=["all", "open"],
        default="all",
        help="open: only CC BY 4.0 text and CC0 catalog entries, for products that charge or need free reuse",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--layer", choices=["all", "raw", "derived"], default="all")
    return parser.parse_args()


def search_documents(documents: list[Document], query: str, top: int = 8) -> list[dict]:
    terms = query_terms(query)
    document_count = max(1, len(documents))
    average_length = sum(max(1, len(doc.text)) for doc in documents) / document_count
    document_frequency = {
        term: sum(term in (doc.title + "\n" + doc.participant_names + "\n" + doc.participant_aliases + "\n" + doc.source_context + "\n" + doc.text).lower() for doc in documents)
        for term in terms
    }
    ranked = []
    for doc in documents:
        value = score(
            doc,
            query,
            terms,
            document_frequency,
            document_count,
            average_length,
        )
        if value > 0:
            ranked.append((value, doc))
    ranked.sort(key=lambda item: (-item[0], item[1].published_at, item[1].title))
    results = []
    named_families = {
        doc.source_family or doc.source_id for _, doc in ranked
        if doc.data_layer == "raw" and doc.speaker_id not in {"", "unknown"}
    }
    seen_sources: dict[str, set[str]] = {}
    selected_raw: dict[str, list[Document]] = {}
    for value, doc in ranked:
        family = doc.source_family or doc.source_id
        if family in seen_sources:
            owners = seen_sources[family]
            if doc.data_layer != "raw" or not doc.speaker_id or len(selected_raw.get(family, [])) >= 3:
                continue
            if doc.speaker_id in owners:
                # Unknown does not mean one person. A conversation with no
                # attributed turns may need several distinct source windows.
                # Once named turns exist, preserve the participant diversity.
                if family in named_families or doc.speaker_id != "unknown":
                    continue
                prior = selected_raw.get(family, [])
                if not doc.fragment_id or any(raw_windows_overlap(doc, old) for old in prior):
                    continue
        seen_sources.setdefault(family, set()).add(doc.speaker_id if doc.data_layer == "raw" else "")
        if doc.data_layer == "raw":
            selected_raw.setdefault(family, []).append(doc)
        results.append(
            {
                "score": round(value, 1),
                "relevance_score": round(value, 1),
                "id": doc.id,
                "source_id": doc.source_id,
                "title": doc.title,
                "section": doc.section,
                "source_type": doc.source_type,
                "published_at": doc.published_at,
                "url": doc.source_url,
                "path": doc.path,
                "content_status": doc.content_status,
                "snippet": snippet(doc, query, terms),
                **{key: getattr(doc, key) for key in PROVENANCE_FIELDS},
            }
        )
        if len(results) >= max(1, top):
            break
    return results


def raw_windows_overlap(left: Document, right: Document) -> bool:
    """Deduplicate source windows without treating unknown as a real speaker."""
    if left.text == right.text or left.fragment_id == right.fragment_id:
        return True
    if left.source_snapshot_sha256 != right.source_snapshot_sha256:
        return True  # No verified cross-edition time map is available here.
    def interval(fragment):
        # Actual corpus unit IDs are namespaced, e.g.
        # episode#episode#cue-1-episode#cue-40; synthetic IDs may be shorter.
        values = re.findall(r"(?:^|#)cue-(\d+)(?=-|$)", fragment)
        if len(values) == 2:
            return tuple(map(int, values))
        match = re.search(r"#(?:cue-)?(\d+)-(?:cue-)?(\d+)$", fragment)
        return tuple(map(int, match.groups())) if match else None
    a, b = interval(left.fragment_id), interval(right.fragment_id)
    if not a or not b or a[0] > a[1] or b[0] > b[1]:
        return True
    alo, ahi = a; blo, bhi = b
    return max(alo, blo) <= min(ahi, bhi)


def print_results(results: list[dict]) -> None:
    if not results:
        print("No matching public sources found.")
        return
    for index, result in enumerate(results, 1):
        print(f"{index}. {result['title']}  [{result['source_type']}]  relevance={result['relevance_score']}")
        if result["section"]:
            print(f"   section: {result['section']}")
        if result["published_at"]:
            print(f"   date: {result['published_at'][:10]}")
        if result["url"]:
            print(f"   source: {result['url']}")
        for key in PROVENANCE_FIELDS:
            print(f"   {key}: {result[key] or 'not established'}")
        print(f"   {result['snippet']}")


def main() -> None:
    args = parse_args()
    documents = [doc for doc in load_documents() if type_matches(doc, args.type) and license_matches(doc, args.license)
                 and (args.layer == "all" or doc.data_layer == args.layer)]
    results = search_documents(documents, args.query, args.top)
    if args.as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    print_results(results)


if __name__ == "__main__":
    main()
