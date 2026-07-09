from __future__ import annotations

import csv
import hashlib
import os
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Iterator

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from preprocessing.email_cleaning import clean_text, estimate_email_metadata


OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "raw_manifest.csv"
REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "manifest_report.md"
FIELDNAMES = (
    "raw_id",
    "source",
    "subtype",
    "label",
    "raw_path",
    "file_size",
    "sha256",
    "parseable",
    "has_subject",
    "text_length_estimate",
    "duplicate_raw_hash",
)
SPAMASSASSIN_SUBTYPES = {
    "easy_ham": 0,
    "hard_ham": 0,
    "spam": 1,
    "spam_2": 1,
}
PHISHING_FILES = {
    "Nazario.csv": "nazario",
    "Nigerian_Fraud.csv": "nigerian_fraud",
}


@dataclass
class ManifestStats:
    counts: Counter = field(default_factory=Counter)
    duplicates: Counter = field(default_factory=Counter)
    not_parseable: Counter = field(default_factory=Counter)
    file_sizes: dict[tuple[str, str], list[int]] = field(default_factory=lambda: defaultdict(list))
    text_lengths: dict[tuple[str, str], list[int]] = field(default_factory=lambda: defaultdict(list))
    warnings: list[str] = field(default_factory=list)


def rel(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def iter_files(path: Path) -> Iterator[Path]:
    if not path.exists():
        return
    for root, dirs, files in os.walk(path):
        dirs.sort()
        for filename in sorted(files):
            yield Path(root) / filename


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_id(source: str, subtype: str, index: int) -> str:
    return f"{source}_{subtype}_{index:07d}"


def update_stats(stats: ManifestStats, row: dict[str, object]) -> None:
    key = (str(row["source"]), str(row["subtype"]))
    stats.counts[key] += 1
    stats.file_sizes[key].append(int(row["file_size"]))
    stats.text_lengths[key].append(int(row["text_length_estimate"]))
    if str(row["duplicate_raw_hash"]).lower() == "true":
        stats.duplicates[key] += 1
    if str(row["parseable"]).lower() != "true":
        stats.not_parseable[key] += 1


def read_csv_robust(path: Path) -> tuple[pd.DataFrame | None, str | None]:
    try:
        return pd.read_csv(path), None
    except Exception as exc:
        try:
            return pd.read_csv(path, engine="python", on_bad_lines="skip"), (
                f"{rel(path)}: Standard-Parser fehlgeschlagen, Fallback mit on_bad_lines='skip' genutzt: {exc}"
            )
        except Exception as fallback_exc:
            return None, f"{rel(path)} nicht lesbar: {fallback_exc}"


def build_email_manifest_row(args: tuple[int, Path, str, str, int]) -> tuple[dict[str, object], str | None]:
    index, path, source, subtype, label = args
    warning = None
    try:
        raw_bytes = path.read_bytes()
        digest = sha256_bytes(raw_bytes)
        metadata = estimate_email_metadata(raw_bytes)
        parseable = bool(metadata["parseable"])
        has_subject = bool(metadata["has_subject"])
        text_length = int(metadata["text_length_estimate"])
        file_size = path.stat().st_size
    except OSError as exc:
        digest = ""
        parseable = False
        has_subject = False
        text_length = 0
        file_size = 0
        warning = f"{rel(path)}: Lesefehler: {exc}"

    row = {
        "raw_id": stable_id(source, subtype, index),
        "source": source,
        "subtype": subtype,
        "label": label,
        "raw_path": rel(path),
        "file_size": file_size,
        "sha256": digest,
        "parseable": str(parseable).lower(),
        "has_subject": str(has_subject).lower(),
        "text_length_estimate": text_length,
        "duplicate_raw_hash": "false",
    }
    return row, warning


def write_email_manifest_rows(
    writer: csv.writer,
    stats: ManifestStats,
    seen_hashes: set[str],
    *,
    base_dir: Path,
    source: str,
    subtype: str,
    label: int,
) -> None:
    if not base_dir.exists():
        stats.warnings.append(f"Fehlender Ordner: {rel(base_dir)}")
        return

    print(f"Manifest: {source}/{subtype}", flush=True)
    files = list(iter_files(base_dir))
    jobs = ((index, path, source, subtype, label) for index, path in enumerate(files, start=1))
    with ThreadPoolExecutor(max_workers=8) as executor:
        for index, (row, warning) in enumerate(executor.map(build_email_manifest_row, jobs), start=1):
            if warning:
                stats.warnings.append(warning)
            digest = str(row["sha256"])
            duplicate = bool(digest and digest in seen_hashes)
            if digest:
                seen_hashes.add(digest)
            row["duplicate_raw_hash"] = str(duplicate).lower()
            writer.writerow([row[field] for field in FIELDNAMES])
            update_stats(stats, row)
            if index % 50000 == 0:
                print(f"  {source}/{subtype}: {index} Dateien", flush=True)


def pick_body_column(df: pd.DataFrame) -> str | None:
    for column in ("body", "text", "message", "content", "email", "mail"):
        if column in df.columns:
            return column
    object_columns = [column for column in df.columns if df[column].dtype == "object"]
    if not object_columns:
        return None
    return max(object_columns, key=lambda column: df[column].fillna("").astype(str).str.len().mean())


def write_phishing_manifest_rows(
    writer: csv.writer,
    stats: ManifestStats,
    seen_hashes: set[str],
    *,
    path: Path,
    subtype: str,
) -> None:
    if not path.exists():
        stats.warnings.append(f"Fehlende CSV: {rel(path)}")
        return

    print(f"Manifest: phishing_curated/{subtype}", flush=True)
    df, warning = read_csv_robust(path)
    if warning:
        stats.warnings.append(warning)
    if df is None:
        return

    subject_column = "subject" if "subject" in df.columns else None
    body_column = "body" if "body" in df.columns else pick_body_column(df)
    if body_column is None:
        stats.warnings.append(f"{rel(path)}: keine plausible Textspalte gefunden")
        body_column = subject_column

    for index, row_data in df.iterrows():
        subject = clean_text(row_data.get(subject_column, "")) if subject_column else ""
        body = clean_text(row_data.get(body_column, "")) if body_column else ""
        text = clean_text(f"{subject} {body}")
        raw_ref = f"{rel(path)}#row={index + 2}"
        digest = sha256_bytes(f"{subtype}\n{raw_ref}\n{text}".encode("utf-8", errors="replace"))
        duplicate = digest in seen_hashes
        seen_hashes.add(digest)
        row = {
            "raw_id": stable_id("phishing_curated", subtype, index + 1),
            "source": "phishing_curated",
            "subtype": subtype,
            "label": 1,
            "raw_path": raw_ref,
            "file_size": len(text.encode("utf-8", errors="replace")),
            "sha256": digest,
            "parseable": str(bool(text)).lower(),
            "has_subject": str(bool(subject)).lower(),
            "text_length_estimate": len(text),
            "duplicate_raw_hash": str(duplicate).lower(),
        }
        writer.writerow([row[field] for field in FIELDNAMES])
        update_stats(stats, row)


def describe(values: list[int]) -> str:
    if not values:
        return "n=0"
    values_sorted = sorted(values)
    return (
        f"n={len(values)}, min={values_sorted[0]}, mean={mean(values_sorted):.1f}, "
        f"median={values_sorted[len(values_sorted)//2]}, max={values_sorted[-1]}"
    )


def render_report(stats: ManifestStats, started_at: datetime, finished_at: datetime) -> str:
    lines = [
        "# Manifest Report",
        "",
        f"- Start: `{started_at.isoformat(timespec='seconds')}`",
        f"- Ende: `{finished_at.isoformat(timespec='seconds')}`",
        f"- Manifest: `{rel(OUTPUT_PATH)}`",
        "",
        "## Anzahl pro Quelle/Subtype",
        "",
        "| source | subtype | anzahl | duplikate | nicht parsebar |",
        "|---|---:|---:|---:|---:|",
    ]
    keys = sorted(set(stats.counts) | set(stats.duplicates) | set(stats.not_parseable))
    for source, subtype in keys:
        key = (source, subtype)
        lines.append(
            f"| {source} | {subtype} | {stats.counts[key]} | {stats.duplicates[key]} | {stats.not_parseable[key]} |"
        )

    lines.extend(["", "## Groessenstatistiken", ""])
    for key in keys:
        lines.append(f"- {key[0]}/{key[1]}: {describe(stats.file_sizes[key])}")

    lines.extend(["", "## Textlaengenstatistiken", ""])
    for key in keys:
        lines.append(f"- {key[0]}/{key[1]}: {describe(stats.text_lengths[key])}")

    lines.extend(["", "## Warnungen", ""])
    if stats.warnings:
        for warning in stats.warnings[:200]:
            lines.append(f"- {warning}")
        if len(stats.warnings) > 200:
            lines.append(f"- Weitere Warnungen gekuerzt: {len(stats.warnings) - 200}")
    else:
        lines.append("- Keine Warnungen.")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    started_at = datetime.now()
    stats = ManifestStats()
    seen_hashes: set[str] = set()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(FIELDNAMES)
        write_email_manifest_rows(
            writer,
            stats,
            seen_hashes,
            base_dir=PROJECT_ROOT / "data" / "raw" / "enron" / "maildir",
            source="enron",
            subtype="enron",
            label=0,
        )
        spam_base = PROJECT_ROOT / "data" / "raw" / "spamassassin"
        for subtype, label in SPAMASSASSIN_SUBTYPES.items():
            write_email_manifest_rows(
                writer,
                stats,
                seen_hashes,
                base_dir=spam_base / subtype,
                source="spamassassin",
                subtype=subtype,
                label=label,
            )
        phishing_base = PROJECT_ROOT / "data" / "raw" / "phishing_curated"
        for filename, subtype in PHISHING_FILES.items():
            write_phishing_manifest_rows(writer, stats, seen_hashes, path=phishing_base / filename, subtype=subtype)

    finished_at = datetime.now()
    REPORT_PATH.write_text(render_report(stats, started_at, finished_at), encoding="utf-8")
    print(f"Manifest geschrieben: {rel(OUTPUT_PATH)}", flush=True)
    print(f"Report geschrieben: {rel(REPORT_PATH)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
