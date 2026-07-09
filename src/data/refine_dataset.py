from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from transformers import AutoTokenizer


@dataclass(frozen=True)
class RefinementConfig:
    project_root: Path
    input_csv: Path
    output_csv: Path
    report_path: Path
    tokenizer_name: str
    top_n_quality_review: int
    token_candidate_pool: int
    max_text_length: int


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_Keine Daten._"
    table = df.copy()
    table.columns = [str(column) for column in table.columns]
    rows = [
        "| " + " | ".join(table.columns) + " |",
        "| " + " | ".join("---" for _ in table.columns) + " |",
    ]
    for _, row in table.iterrows():
        values = [str(row[column]).replace("\n", " ").replace("|", "\\|") for column in table.columns]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def count_tokens_for_texts(texts: pd.Series, tokenizer_name: str) -> list[int]:
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    return [
        len(tokenizer.encode(str(text), add_special_tokens=True, truncation=False, verbose=False))
        for text in texts.fillna("")
    ]


def infer_quality_issue(row: pd.Series) -> str:
    text = str(row.get("text", ""))
    subject = str(row.get("subject", ""))
    raw_path = str(row.get("raw_path", ""))
    lower = f"{subject} {text}".lower()

    if raw_path.replace("\\", "/").endswith("/cmds") or re.match(r"^\s*mv\s+\d+\s+", text):
        return "SpamAssassin-Steuerdatei, keine eigentliche E-Mail"
    if "don't delete this message -- folder internal data" in lower:
        return "Mailbox-/Folder-Artefakt, keine eigentliche Nachricht"
    if re.search(r"[A-Za-z0-9+/]{300,}={0,2}", text):
        return "vermuteter Base64-/MIME-Block oder eingebetteter Anhang"
    if lower.count("-----original message-----") >= 5 or lower.count("forwarded by") >= 5:
        return "sehr langer Mailthread/Weiterleitungskette"
    if any(marker in lower for marker in ("unsubscribe", "newsletter", "weblogs", "commentary")):
        return "sehr lange Newsletter-/Webseitenstruktur"
    if int(row.get("text_length", 0)) > 100_000:
        return "extremer Laengenausreisser mit ungewoehnlicher Struktur"
    return "langer, aber plausibler Mailtext"


def apply_filter_rules(df: pd.DataFrame, config: RefinementConfig) -> pd.Series:
    raw_path = df["raw_path"].fillna("").astype(str).str.replace("\\", "/", regex=False)
    subject = df["subject"].fillna("").astype(str)
    text = df["text"].fillna("").astype(str)

    rule_non_email_cmds = raw_path.str.endswith("/cmds") | text.str.match(r"^\s*mv\s+\d+\s+", na=False)
    rule_folder_artifact = subject.str.contains(
        "DON'T DELETE THIS MESSAGE -- FOLDER INTERNAL DATA",
        case=False,
        regex=False,
        na=False,
    )
    rule_extreme_length = df["text_length"] > config.max_text_length

    return rule_non_email_cmds | rule_folder_artifact | rule_extreme_length


def label_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df["label"]
        .value_counts()
        .sort_index()
        .rename_axis("label")
        .reset_index(name="anzahl")
    )


def source_impact(removed: pd.DataFrame) -> pd.DataFrame:
    if removed.empty:
        return pd.DataFrame(columns=["source", "subtype", "label", "removed"])
    return (
        removed.groupby(["source", "subtype", "label"])
        .size()
        .reset_index(name="removed")
        .sort_values(["source", "subtype", "label"])
    )


def build_quality_review(df: pd.DataFrame, config: RefinementConfig) -> pd.DataFrame:
    longest = df.nlargest(config.top_n_quality_review, "text_length").copy()
    token_pool = df.nlargest(config.token_candidate_pool, "text_length").copy()
    token_pool["token_count_review"] = count_tokens_for_texts(token_pool["text"], config.tokenizer_name)
    top_tokens = token_pool.nlargest(config.top_n_quality_review, "token_count_review")[
        ["id", "token_count_review"]
    ]

    review = longest.merge(top_tokens, on="id", how="left")
    review["token_count_review"] = review["token_count_review"].fillna("").astype(str)
    review["vermutete_ursache"] = review.apply(infer_quality_issue, axis=1)
    return review[
        [
            "id",
            "source",
            "subtype",
            "label",
            "text_length",
            "token_count_review",
            "subject",
            "raw_path",
            "vermutete_ursache",
        ]
    ]


def render_report(
    config: RefinementConfig,
    original: pd.DataFrame,
    filtered: pd.DataFrame,
    removed: pd.DataFrame,
    review: pd.DataFrame,
) -> str:
    before_labels = label_distribution(original)
    after_labels = label_distribution(filtered)
    removed_by_source = source_impact(removed)

    lines = [
        "# Dataset Refinement Report",
        "",
        "## Ziel",
        "",
        "Dieser Schritt erzeugt eine finale Trainingsgrundlage aus `emails_dataset_raw.csv`, ohne die Rohdaten oder "
        "Version 1.0 des Arbeitsdatensatzes zu veraendern. Die Filterung basiert ausschliesslich auf den bereits "
        "dokumentierten EDA-Erkenntnissen zu extremen Laengenausreissern.",
        "",
        "## Manuelle Qualitaetsanalyse der 20 laengsten Dokumente",
        "",
        markdown_table(review),
        "",
        "## Angewendete Filterregeln",
        "",
        f"1. Entferne technische SpamAssassin-Steuerdateien (`cmds` oder Zeilenmuster `mv <nummer> ...`).",
        "   Begruendung: Diese Dateien sind keine E-Mails und enthalten keine natuerliche Nachricht.",
        f"2. Entferne Mailbox-/Folder-Artefakte mit Subject `DON'T DELETE THIS MESSAGE -- FOLDER INTERNAL DATA`.",
        "   Begruendung: Diese Zeilen repraesentieren internes Mailboxformat, nicht den Inhalt einer E-Mail.",
        f"3. Entferne Dokumente mit `text_length > {config.max_text_length}` Zeichen.",
        "   Begruendung: Die manuelle Sichtung zeigt, dass diese extremen Laengenausreisser durch Artefakte, "
        "MIME-/Base64-Bloecke, Steuerdateien oder sehr untypische Dokumentstrukturen dominiert werden. Die Regel ist "
        "datenqualitaetsbezogen und nicht leistungsbezogen.",
        "",
        "## Entfernte Dokumente",
        "",
        f"- Anzahl vor Filterung: {len(original)}",
        f"- Anzahl entfernt: {len(removed)}",
        f"- Finale Datensatzgroesse: {len(filtered)}",
        "",
        "### Betroffene Quellen/Subtypes",
        "",
        markdown_table(removed_by_source),
        "",
        "## Labelverteilung vorher",
        "",
        markdown_table(before_labels),
        "",
        "## Labelverteilung nachher",
        "",
        markdown_table(after_labels),
        "",
        "## Wissenschaftliche Einordnung",
        "",
        "Die Filterregeln entfernen nur dokumentierte Datenqualitaetsprobleme. Es werden keine Split-Entscheidungen, "
        "keine Modellannahmen und keine leistungsorientierten Optimierungen vorgenommen. Der Rohdatensatz bleibt erhalten; "
        "`emails_dataset_filtered.csv` ist die daraus abgeleitete finale Trainingsgrundlage.",
        "",
    ]
    return "\n".join(lines)


def run_refinement(config: RefinementConfig) -> dict[str, Any]:
    if not config.input_csv.exists():
        raise FileNotFoundError(f"Input dataset not found: {config.input_csv}")

    df = pd.read_csv(config.input_csv)
    df["text"] = df["text"].fillna("").astype(str)
    df["subject"] = df["subject"].fillna("").astype(str)
    df["text_length"] = df["text"].str.len()

    review = build_quality_review(df, config)
    remove_mask = apply_filter_rules(df, config)
    removed = df[remove_mask].copy()
    filtered = df[~remove_mask].drop(columns=["text_length"]).copy()

    config.output_csv.parent.mkdir(parents=True, exist_ok=True)
    filtered.to_csv(config.output_csv, index=False)
    config.report_path.write_text(render_report(config, df, filtered, removed, review), encoding="utf-8")

    return {
        "removed_count": len(removed),
        "final_count": len(filtered),
        "labels_before": label_distribution(df).set_index("label")["anzahl"].to_dict(),
        "labels_after": label_distribution(filtered).set_index("label")["anzahl"].to_dict(),
    }


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    config = RefinementConfig(
        project_root=project_root,
        input_csv=project_root / "data" / "processed" / "emails_dataset_raw.csv",
        output_csv=project_root / "data" / "processed" / "emails_dataset_filtered.csv",
        report_path=project_root / "data" / "processed" / "filter_report.md",
        tokenizer_name="distilbert-base-uncased",
        top_n_quality_review=20,
        token_candidate_pool=100,
        max_text_length=100_000,
    )
    result = run_refinement(config)
    print("Dataset Refinement abgeschlossen", flush=True)
    print(f"Entfernte Dokumente: {result['removed_count']}", flush=True)
    print(f"Finale Datensatzgroesse: {result['final_count']}", flush=True)
    print(f"Labelverteilung vorher: {result['labels_before']}", flush=True)
    print(f"Labelverteilung nachher: {result['labels_after']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
