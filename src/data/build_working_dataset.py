from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from preprocessing.email_cleaning import clean_text, read_email_file


MANIFEST_PATH = PROJECT_ROOT / "data" / "processed" / "raw_manifest.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "emails_dataset_raw.csv"
REPORT_PATH = PROJECT_ROOT / "data" / "processed" / "ingestion_report.md"
FIELDNAMES = ("id", "source", "subtype", "subject", "body", "text", "label", "generated", "raw_path")
SPAMASSASSIN_SUBTYPES = ("easy_ham", "hard_ham", "spam", "spam_2")
PHISHING_FILES = {
    "Nazario.csv": "nazario",
    "Nigerian_Fraud.csv": "nigerian_fraud",
}


@dataclass
class WorkingStats:
    selected: Counter = field(default_factory=Counter)
    written: Counter = field(default_factory=Counter)
    labels: Counter = field(default_factory=Counter)
    empty_removed: Counter = field(default_factory=Counter)
    duplicate_removed: Counter = field(default_factory=Counter)
    warnings: list[str] = field(default_factory=list)
    examples: dict[tuple[str, str], list[dict[str, str]]] = field(default_factory=lambda: defaultdict(list))
    id_counters: Counter = field(default_factory=Counter)


def rel(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def normalized_hash(text: str) -> str:
    return hashlib.sha256(clean_text(text).lower().encode("utf-8", errors="replace")).hexdigest()


def make_id(stats: WorkingStats, source: str, subtype: str) -> str:
    key = (source, subtype)
    stats.id_counters[key] += 1
    return f"{source}_{subtype}_{stats.id_counters[key]:07d}"


def remember_example(stats: WorkingStats, record: dict[str, object]) -> None:
    key = (str(record["source"]), str(record["subtype"]))
    if len(stats.examples[key]) >= 3:
        return
    stats.examples[key].append(
        {
            "id": str(record["id"]),
            "label": str(record["label"]),
            "raw_path": str(record["raw_path"]),
            "subject": str(record["subject"])[:100],
            "text": str(record["text"])[:160],
        }
    )


def write_record(
    writer: csv.writer,
    stats: WorkingStats,
    seen_text_hashes: set[str],
    *,
    source: str,
    subtype: str,
    subject: object,
    body: object,
    label: int,
    raw_path: str,
) -> None:
    key = (source, subtype)
    clean_subject = clean_text(subject)
    clean_body = clean_text(body)
    text = clean_text(f"{clean_subject} {clean_body}")
    if not text:
        stats.empty_removed[key] += 1
        return
    digest = normalized_hash(text)
    if digest in seen_text_hashes:
        stats.duplicate_removed[key] += 1
        return
    seen_text_hashes.add(digest)
    record = {
        "id": make_id(stats, source, subtype),
        "source": source,
        "subtype": subtype,
        "subject": clean_subject,
        "body": clean_body,
        "text": text,
        "label": label,
        "generated": "false",
        "raw_path": raw_path,
    }
    writer.writerow([record[field] for field in FIELDNAMES])
    stats.written[key] += 1
    stats.labels[label] += 1
    remember_example(stats, record)


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


def pick_body_column(df: pd.DataFrame) -> str | None:
    for column in ("body", "text", "message", "content", "email", "mail"):
        if column in df.columns:
            return column
    object_columns = [column for column in df.columns if df[column].dtype == "object"]
    if not object_columns:
        return None
    return max(object_columns, key=lambda column: df[column].fillna("").astype(str).str.len().mean())


def load_manifest() -> pd.DataFrame:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest fehlt: {rel(MANIFEST_PATH)}. Bitte zuerst build_manifest.py ausfuehren.")
    manifest = pd.read_csv(MANIFEST_PATH)
    for column in ("parseable", "duplicate_raw_hash", "has_subject"):
        manifest[column] = manifest[column].astype(str).str.lower().eq("true")
    return manifest


def parse_manifest_file_row(row: pd.Series) -> tuple[str, str]:
    path = PROJECT_ROOT / str(row["raw_path"])
    parsed = read_email_file(path)
    return str(parsed.get("subject", "")), str(parsed.get("body", ""))


def ingest_manifest_rows(
    writer: csv.writer,
    stats: WorkingStats,
    seen_text_hashes: set[str],
    rows: pd.DataFrame,
) -> None:
    for _, row in rows.iterrows():
        source = str(row["source"])
        subtype = str(row["subtype"])
        key = (source, subtype)
        stats.selected[key] += 1
        try:
            subject, body = parse_manifest_file_row(row)
        except Exception as exc:
            stats.empty_removed[key] += 1
            stats.warnings.append(f"{row['raw_path']}: Parsing fehlgeschlagen: {exc}")
            continue
        write_record(
            writer,
            stats,
            seen_text_hashes,
            source=source,
            subtype=subtype,
            subject=subject,
            body=body,
            label=int(row["label"]),
            raw_path=str(row["raw_path"]),
        )


def ingest_phishing_csv(
    writer: csv.writer,
    stats: WorkingStats,
    seen_text_hashes: set[str],
    *,
    path: Path,
    subtype: str,
) -> None:
    df, warning = read_csv_robust(path)
    if warning:
        stats.warnings.append(warning)
    if df is None:
        return
    subject_column = "subject" if "subject" in df.columns else None
    body_column = "body" if "body" in df.columns else pick_body_column(df)
    if body_column is None:
        body_column = subject_column
        stats.warnings.append(f"{rel(path)}: keine plausible Body-Spalte gefunden")

    for row_index, row in df.iterrows():
        key = ("phishing_curated", subtype)
        stats.selected[key] += 1
        subject = row.get(subject_column, "") if subject_column else ""
        body = row.get(body_column, "") if body_column else ""
        write_record(
            writer,
            stats,
            seen_text_hashes,
            source="phishing_curated",
            subtype=subtype,
            subject=subject,
            body=body,
            label=1,
            raw_path=f"{rel(path)}#row={row_index + 2}",
        )


def render_report(stats: WorkingStats, started_at: datetime, finished_at: datetime, sample_size: int, eligible: int) -> str:
    lines = [
        "# Ingestion Report",
        "",
        f"- Start: `{started_at.isoformat(timespec='seconds')}`",
        f"- Ende: `{finished_at.isoformat(timespec='seconds')}`",
        f"- Ausgabe: `{rel(OUTPUT_PATH)}`",
        f"- Gewaehlte Enron-Sample-Size: `{sample_size}`",
        f"- Enron-Kandidaten nach Filter: `{eligible}`",
        "",
        "## Methodische Begruendung der Enron-Stichprobe",
        "",
        "Enron wird nicht vollstaendig materialisiert, weil der Korpus mit 517401 Dateien die legitime Klasse "
        "massiv dominieren wuerde. Fuer das Arbeitsdataset wird deshalb eine reproduzierbare Stichprobe genutzt: "
        "nur parsebare, nicht rohduplizierte Dateien mit begrenzter Dateigroesse und begrenzter geschaetzter Textlaenge. "
        "Damit bleibt Enron als legitime Unternehmenskommunikation vertreten, ohne die kuratierten Phishing- und "
        "SpamAssassin-Daten methodisch zu ueberdecken.",
        "",
        "## Finale Anzahl je Source/Subtype",
        "",
        "| source | subtype | ausgewaehlt | leere Texte entfernt | Duplikate entfernt | final |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    keys = sorted(set(stats.selected) | set(stats.written) | set(stats.empty_removed) | set(stats.duplicate_removed))
    for source, subtype in keys:
        key = (source, subtype)
        lines.append(
            f"| {source} | {subtype} | {stats.selected[key]} | {stats.empty_removed[key]} | "
            f"{stats.duplicate_removed[key]} | {stats.written[key]} |"
        )

    lines.extend(["", "## Finale Anzahl je Label", ""])
    for label in sorted(stats.labels):
        lines.append(f"- Label `{label}`: {stats.labels[label]}")

    lines.extend(["", "## Beispielzeilen", ""])
    for source, subtype in sorted(stats.examples):
        lines.append(f"### {source}/{subtype}")
        for example in stats.examples[(source, subtype)]:
            lines.append(
                f"- `{example['id']}` label={example['label']} raw=`{example['raw_path']}` "
                f"subject=\"{example['subject']}\" text=\"{example['text']}\""
            )
        lines.append("")

    lines.extend(
        [
            "## Bekannte Limitationen",
            "",
            "- Enron ist keine kuratierte Anti-Phishing-Negativklasse, sondern reale Unternehmenskommunikation.",
            "- SpamAssassin-Spam wird gemaess Projektdefinition als label=1 gefuehrt, ist aber nicht deckungsgleich mit Phishing.",
            "- Die Enron-Stichprobe reduziert Klassendominanz, ersetzt aber keine spaetere experimentelle Validierung.",
            "- Duplikate werden anhand normalisierten Texts entfernt; semantisch gleiche, aber leicht veraenderte Mails koennen erhalten bleiben.",
            "",
            "## Warnungen",
            "",
        ]
    )
    if stats.warnings:
        for warning in stats.warnings[:200]:
            lines.append(f"- {warning}")
        if len(stats.warnings) > 200:
            lines.append(f"- Weitere Warnungen gekuerzt: {len(stats.warnings) - 200}")
    else:
        lines.append("- Keine Warnungen.")
    lines.append("")
    return "\n".join(lines)


def build_dataset(enron_sample_size: int) -> tuple[WorkingStats, int]:
    manifest = load_manifest()
    stats = WorkingStats()
    seen_text_hashes: set[str] = set()

    enron_candidates = manifest[
        (manifest["source"] == "enron")
        & (manifest["parseable"])
        & (~manifest["duplicate_raw_hash"])
        & (manifest["file_size"] <= 100_000)
        & (manifest["text_length_estimate"] > 0)
        & (manifest["text_length_estimate"] <= 50_000)
    ].copy()
    eligible = len(enron_candidates)
    enron_sample = enron_candidates.sample(
        n=min(enron_sample_size, eligible),
        random_state=42,
        replace=False,
    ).sort_values("raw_id")

    spam_rows = manifest[(manifest["source"] == "spamassassin") & (manifest["subtype"].isin(SPAMASSASSIN_SUBTYPES))]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(FIELDNAMES)
        print(f"Arbeitsdataset: Enron-Stichprobe {len(enron_sample)} aus {eligible} Kandidaten", flush=True)
        ingest_manifest_rows(writer, stats, seen_text_hashes, enron_sample)
        print("Arbeitsdataset: SpamAssassin vollstaendig", flush=True)
        ingest_manifest_rows(writer, stats, seen_text_hashes, spam_rows)
        phishing_base = PROJECT_ROOT / "data" / "raw" / "phishing_curated"
        for filename, subtype in PHISHING_FILES.items():
            print(f"Arbeitsdataset: phishing_curated/{subtype}", flush=True)
            ingest_phishing_csv(writer, stats, seen_text_hashes, path=phishing_base / filename, subtype=subtype)

    return stats, eligible


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build controlled raw working dataset.")
    parser.add_argument("--enron-sample-size", type=int, default=7500)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started_at = datetime.now()
    stats, eligible = build_dataset(args.enron_sample_size)
    finished_at = datetime.now()
    REPORT_PATH.write_text(render_report(stats, started_at, finished_at, args.enron_sample_size, eligible), encoding="utf-8")
    print(f"Arbeitsdataset geschrieben: {rel(OUTPUT_PATH)}", flush=True)
    print(f"Report geschrieben: {rel(REPORT_PATH)}", flush=True)
    print(f"Label-Verteilung: {dict(sorted(stats.labels.items()))}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
