from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from transformers import AutoTokenizer


matplotlib.use("Agg")


@dataclass(frozen=True)
class EdaConfig:
    project_root: Path
    input_csv: Path
    report_path: Path
    figures_dir: Path
    tokenizer_name: str
    random_state: int


def clean_series(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str)


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def ensure_dirs(config: EdaConfig) -> None:
    config.report_path.parent.mkdir(parents=True, exist_ok=True)
    config.figures_dir.mkdir(parents=True, exist_ok=True)


def load_dataset(config: EdaConfig) -> pd.DataFrame:
    if not config.input_csv.exists():
        raise FileNotFoundError(f"Input dataset not found: {config.input_csv}")
    df = pd.read_csv(config.input_csv)
    expected = {"id", "source", "subtype", "subject", "body", "text", "label", "generated", "raw_path"}
    missing = expected.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    return df


def missing_values(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    rows = []
    for column in df.columns:
        missing = int(df[column].isna().sum())
        rows.append(
            {
                "column": column,
                "missing": missing,
                "missing_percent": round((missing / total) * 100, 2) if total else 0.0,
            }
        )
    return pd.DataFrame(rows)


def describe_numeric(series: pd.Series) -> dict[str, float]:
    numeric = pd.to_numeric(series, errors="coerce")
    return {
        "mean": float(numeric.mean()),
        "median": float(numeric.median()),
        "std": float(numeric.std(ddof=1)),
        "min": float(numeric.min()),
        "q25": float(numeric.quantile(0.25)),
        "q75": float(numeric.quantile(0.75)),
        "max": float(numeric.max()),
    }


def describe_words(series: pd.Series) -> dict[str, float]:
    numeric = pd.to_numeric(series, errors="coerce")
    return {
        "mean": float(numeric.mean()),
        "median": float(numeric.median()),
        "max": float(numeric.max()),
    }


def plot_bar(series: pd.Series, title: str, ylabel: str, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    series.plot(kind="bar", ax=ax, color="#4c78a8")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("")
    ax.set_ylim(bottom=0)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def plot_hist(series: pd.Series, title: str, xlabel: str, output: Path, upper_quantile: float = 0.99) -> None:
    values = pd.to_numeric(series, errors="coerce").dropna()
    upper = values.quantile(upper_quantile)
    clipped = values[values <= upper]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(clipped, bins=60, color="#59a14f", edgecolor="white")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Anzahl E-Mails")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def plot_boxplot_by_group(df: pd.DataFrame, value_column: str, group_column: str, title: str, ylabel: str, output: Path) -> None:
    groups = [(str(name), group[value_column].dropna().to_numpy()) for name, group in df.groupby(group_column)]
    labels = [name for name, values in groups if len(values) > 0]
    values = [values for _, values in groups if len(values) > 0]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.boxplot(values, tick_labels=labels, showfliers=False)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_ylim(bottom=0)
    ax.tick_params(axis="x", rotation=20)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def plot_label_boxplots(df: pd.DataFrame, output: Path) -> None:
    label_names = {0: "Legitim", 1: "Phishing/verdaechtig"}
    metrics = [("text_length", "Zeichen"), ("word_count", "Woerter"), ("token_count", "Tokens")]
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for ax, (column, ylabel) in zip(axes, metrics):
        grouped = []
        labels = []
        for label_value, group in df.groupby("label"):
            labels.append(label_names.get(int(label_value), str(label_value)))
            grouped.append(group[column].dropna().to_numpy())
        ax.boxplot(grouped, tick_labels=labels, showfliers=False)
        ax.set_title(ylabel)
        ax.set_ylim(bottom=0)
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Vergleich nach Label")
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


def count_distilbert_tokens(texts: pd.Series, tokenizer_name: str) -> list[int]:
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    counts: list[int] = []
    for text in texts.fillna("").astype(str):
        token_ids = tokenizer.encode(text, add_special_tokens=True, truncation=False, verbose=False)
        counts.append(len(token_ids))
    return counts


def language_class(text: str) -> str:
    lower = text.lower()
    german_markers = {
        " der ",
        " die ",
        " das ",
        " und ",
        " nicht ",
        " mit ",
        " fuer ",
        " für ",
        " ist ",
        " sie ",
        " eine ",
        " ein ",
    }
    english_markers = {
        " the ",
        " and ",
        " you ",
        " your ",
        " for ",
        " with ",
        " this ",
        " from ",
        " account ",
        " please ",
        " subject ",
    }
    padded = f" {lower} "
    german_score = sum(marker in padded for marker in german_markers)
    english_score = sum(marker in padded for marker in english_markers)
    if german_score and english_score:
        return "gemischt"
    if german_score > english_score:
        return "deutsch"
    if english_score > 0:
        return "englisch"
    return "unbestimmt"


def estimate_language(df: pd.DataFrame, random_state: int) -> dict[str, Any]:
    sample_size = min(1000, len(df))
    sample = df.sample(n=sample_size, random_state=random_state) if sample_size else df
    counts = Counter(language_class(text) for text in sample["text"].fillna("").astype(str))
    return {"sample_size": sample_size, "counts": dict(counts)}


def estimate_html(df: pd.DataFrame) -> dict[str, int]:
    text = clean_series(df["text"])
    html_pattern = re.compile(r"(?:<html|</html>|<body|</body>|<br|</p>|&nbsp;|&lt;|&gt;)", re.IGNORECASE)
    html_like = text.str.contains(html_pattern, regex=True, na=False)
    return {
        "html_like": int(html_like.sum()),
        "plain_text_like": int((~html_like).sum()),
    }


def duplicate_indicators(df: pd.DataFrame) -> dict[str, int]:
    normalized = clean_series(df["text"]).str.lower().str.replace(r"\s+", " ", regex=True).str.strip()
    exact_duplicates = int(normalized.duplicated().sum())
    repeated_subjects = int(clean_series(df["subject"]).str.lower().str.strip().duplicated().sum())
    repeated_prefixes = int(normalized.str.slice(0, 250).duplicated().sum())
    return {
        "exact_text_duplicates": exact_duplicates,
        "repeated_subjects": repeated_subjects,
        "repeated_250_char_prefixes": repeated_prefixes,
    }


def recommend_max_length(token_stats: dict[str, float]) -> tuple[int, str]:
    p95 = token_stats["p95"]
    median = token_stats["median"]
    if p95 <= 128:
        return 128, "Das 95%-Perzentil liegt innerhalb von 128 Tokens."
    if p95 <= 256:
        return 256, "256 Tokens decken mindestens 95% der beobachteten Tokenlaengen ab und begrenzen Rechenaufwand."
    if median <= 256:
        return 256, "Das 95%-Perzentil liegt ueber 256, der Median aber deutlich darunter; 256 ist ein pragmatischer Kompromiss gegen sehr lange Ausreisser."
    return 512, "Die Verteilung ist insgesamt lang; 512 reduziert Trunkierung, erhoeht aber Rechenaufwand."


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
        values = [str(row[column]).replace("\n", " ") for column in table.columns]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def fmt(value: float) -> str:
    if math.isnan(value):
        return "n/a"
    return f"{value:.2f}"


def build_report(
    df: pd.DataFrame,
    overview: dict[str, Any],
    missing: pd.DataFrame,
    char_stats: dict[str, float],
    word_stats: dict[str, float],
    token_stats: dict[str, float],
    language: dict[str, Any],
    html_info: dict[str, int],
    duplicates: dict[str, int],
    max_length: int,
    max_length_reason: str,
) -> str:
    label_counts = overview["label_counts"]
    label_percent = overview["label_percent"]
    source_counts = overview["source_counts"]
    subtype_counts = overview["subtype_counts"]
    source_metrics = df.groupby("source")[["text_length", "word_count", "token_count"]].mean().round(2).reset_index()
    label_metrics = df.groupby("label")[["text_length", "word_count", "token_count"]].mean().round(2).reset_index()
    missing_focus = missing[missing["column"].isin(["subject", "body", "text"])]

    lines = [
        "# Explorative Datenanalyse des Arbeitsdatensatzes Version 1.0",
        "",
        "## 1. Ziel der Analyse",
        "",
        "Ziel dieser explorativen Datenanalyse ist die wissenschaftlich nachvollziehbare Beschreibung des Arbeitsdatensatzes "
        "`data/processed/emails_dataset_raw.csv`. Die Analyse dient als Grundlage fuer die spaetere transformerbasierte "
        "Phishing-E-Mail-Klassifikation, ohne bereits Modelltraining, Splits oder Feature-Engineering umzusetzen.",
        "",
        "## 2. Datensatzuebersicht",
        "",
        f"Der Arbeitsdatensatz umfasst **{len(df)} E-Mails**. Er kombiniert legitime Unternehmenskommunikation aus Enron, "
        "Ham-/Spam-Beispiele aus SpamAssassin sowie kuratierte Phishing-Daten.",
        "",
        "### Anzahl pro Quelle",
        "",
        markdown_table(source_counts.reset_index().rename(columns={"index": "source", "count": "anzahl"})),
        "",
        "### Anzahl pro Subtype",
        "",
        markdown_table(subtype_counts.reset_index().rename(columns={"index": "subtype", "count": "anzahl"})),
        "",
        "## 3. Datenqualitaet",
        "",
        "### Fehlende Werte",
        "",
        markdown_table(missing),
        "",
        "Fuer die spaetere Klassifikation ist die Spalte `text` entscheidend, da sie aus Betreff und Body kombiniert wurde. "
        "Fehlende Betreffzeilen sind daher nicht unmittelbar kritisch, solange der Body vorhanden ist. Sie koennen aber "
        "Informationsverlust bedeuten, da Betreffzeilen bei Phishing haeufig starke Hinweise auf Dringlichkeit, Markenbezug "
        "oder Aufforderungen enthalten.",
        "",
        "Fokusspalten:",
        "",
        markdown_table(missing_focus),
        "",
        "## 4. Klassenverteilung",
        "",
        markdown_table(label_counts.reset_index().rename(columns={"index": "label", "count": "anzahl"})),
        "",
        "### Prozentuale Klassenverteilung",
        "",
        markdown_table(label_percent.reset_index().rename(columns={"index": "label", "proportion": "anteil_prozent"})),
        "",
        f"Die legitime Klasse umfasst {label_counts.get(0, 0)} Instanzen, die Phishing-/verdächtige Klasse {label_counts.get(1, 0)} Instanzen. "
        "Die Verteilung ist moderat unausgeglichen, aber nicht extrem. Class Weights sollten spaeter dennoch geprueft werden, "
        "weil die Kosten falsch negativer Phishing-Erkennung hoeher sein koennen als reine Klassenanteile nahelegen.",
        "",
        "## 5. Quellenanalyse",
        "",
        markdown_table(source_metrics),
        "",
        "Die Quellen unterscheiden sich deutlich in Laenge und Herkunft. Enron repraesentiert legitime interne Unternehmenskommunikation, "
        "waehrend SpamAssassin und die kuratierten Phishing-Daten andere Kommunikationskontexte und teils andere Schreibstile abbilden. "
        "Diese Heterogenitaet ist fuer die Evaluation wertvoll, erzeugt aber ein Risiko fuer Domain Shift.",
        "",
        "## 6. Textanalyse",
        "",
        "### Zeichenlaengen",
        "",
        f"- Mittelwert: {fmt(char_stats['mean'])}",
        f"- Median: {fmt(char_stats['median'])}",
        f"- Standardabweichung: {fmt(char_stats['std'])}",
        f"- Minimum: {fmt(char_stats['min'])}",
        f"- 25%-Quartil: {fmt(char_stats['q25'])}",
        f"- 75%-Quartil: {fmt(char_stats['q75'])}",
        f"- Maximum: {fmt(char_stats['max'])}",
        "",
        "### Wortanzahlen",
        "",
        f"- Mittelwert: {fmt(word_stats['mean'])}",
        f"- Median: {fmt(word_stats['median'])}",
        f"- Maximum: {fmt(word_stats['max'])}",
        "",
        markdown_table(label_metrics),
        "",
        "## 7. Tokenanalyse",
        "",
        "Die Tokenlaengen wurden mit dem DistilBERT-Tokenizer `distilbert-base-uncased` berechnet. Es wurden keine model-ready "
        "Token-Dateien erzeugt und kein Training vorbereitet.",
        "",
        f"- Mittelwert: {fmt(token_stats['mean'])}",
        f"- Median: {fmt(token_stats['median'])}",
        f"- 95%-Perzentil: {fmt(token_stats['p95'])}",
        f"- Maximum: {fmt(token_stats['max'])}",
        "",
        f"Empfohlene `max_length`: **{max_length}**. {max_length_reason} Diese Empfehlung ist als Ausgangspunkt zu verstehen; "
        "sie sollte spaeter gegen Rechenbudget, Trunkierungsrate und Modellleistung abgewogen werden.",
        "",
        "## 8. Sprachanalyse",
        "",
        f"Die Sprache wurde heuristisch auf einer reproduzierbaren Stichprobe von {language['sample_size']} E-Mails geschaetzt:",
        "",
        markdown_table(pd.DataFrame([{"sprache": key, "anzahl": value} for key, value in language["counts"].items()])),
        "",
        "Da ueberwiegend englischsprachige oeffentliche Datensaetze verwendet werden, erfolgt die Evaluation auf dieser Sprachbasis. "
        "Deutschsprachige Phishing-Szenarien sind damit nur eingeschraenkt abgedeckt.",
        "",
        "## 9. Erkenntnisse",
        "",
        f"- Residualer HTML-Hinweis im bereits bereinigten Text: {html_info['html_like']} E-Mails.",
        f"- Plaintext-aehnlich nach bereinigtem Text: {html_info['plain_text_like']} E-Mails.",
        f"- Exakte Textdubletten im Arbeitsdatensatz: {duplicates['exact_text_duplicates']}.",
        "- Die Anzahl bereits vor Version 1.0 entfernter Dubletten ist aus `emails_dataset_raw.csv` allein nicht rekonstruierbar; "
        "die EDA dokumentiert daher ausschliesslich verbleibende Dublettenindikatoren im Arbeitsdatensatz.",
        f"- Wiederholte Betreffzeilen: {duplicates['repeated_subjects']}.",
        f"- Wiederholte 250-Zeichen-Anfaenge als Hinweis auf verbleibende nahezu identische Texte: {duplicates['repeated_250_char_prefixes']}.",
        "",
        "Der HTML-Anteil kann auf Basis des Arbeitsdatensatzes nur unterschaetzt werden, weil die Ingestion HTML-Tags bereits entfernt hat. "
        "Die Messung beschreibt daher verbleibende HTML-Artefakte, nicht den urspruenglichen MIME-Anteil.",
        "",
        "## 10. Empfehlungen fuer die Modellierung",
        "",
        f"- `max_length`: {max_length}, begruendet durch Median und 95%-Perzentil der DistilBERT-Tokenlaengen.",
        "- Batch Size: initial 16 oder 32, abhaengig von GPU-Speicher; bei `max_length=512` eher 8 bis 16.",
        "- Class Weights: pruefen, da eine moderate Klassenunwucht und asymmetrische Fehlerkosten vorliegen.",
        "- Weitere Datenbereinigung: vor Training keine aggressive Entfernung mehr, aber auffaellige Systemzeilen und sehr lange Ausreisser dokumentiert pruefen.",
        "- Overfitting-Risiko: wiederkehrende Templates, Nigerian-Fraud-Stil und Quellensignaturen koennen vom Modell auswendig gelernt werden.",
        "- Domain-Shift-Risiko: Enron/SpamAssassin sind historisch und englischsprachig; moderne deutschsprachige Phishing-Mails koennen abweichen.",
        "",
        "## 11. Limitationen",
        "",
        "- Die Analyse basiert ausschliesslich auf Version 1.0 des Arbeitsdatensatzes und veraendert diese Datei nicht.",
        "- Sprache und HTML-Anteil werden heuristisch aus bereits bereinigten Texten geschaetzt.",
        "- Tokenlaengen wurden nur zur Laengenanalyse berechnet; es wurde keine Modellpipeline vorbereitet.",
        "- Die Quellen sind historisch und oeffentlich; reale produktive Phishing-Umgebungen koennen andere Verteilungen aufweisen.",
        "",
    ]
    return "\n".join(lines)


def run_analysis(config: EdaConfig) -> dict[str, Any]:
    ensure_dirs(config)
    df = load_dataset(config)
    missing = missing_values(df[["id", "source", "subtype", "subject", "body", "text", "label", "generated", "raw_path"]])
    df["subject"] = clean_series(df["subject"])
    df["body"] = clean_series(df["body"])
    df["text"] = clean_series(df["text"])
    df["text_length"] = df["text"].str.len()
    df["word_count"] = df["text"].map(word_count)

    print("Berechne DistilBERT-Tokenlaengen...", flush=True)
    df["token_count"] = count_distilbert_tokens(df["text"], config.tokenizer_name)

    overview = {
        "source_counts": df["source"].value_counts(),
        "subtype_counts": df["subtype"].value_counts(),
        "label_counts": df["label"].value_counts().sort_index(),
        "label_percent": (df["label"].value_counts(normalize=True).sort_index() * 100).round(2),
    }
    char_stats = describe_numeric(df["text_length"])
    word_stats = describe_words(df["word_count"])
    token_stats = {
        "mean": float(df["token_count"].mean()),
        "median": float(df["token_count"].median()),
        "p95": float(df["token_count"].quantile(0.95)),
        "max": float(df["token_count"].max()),
    }
    language = estimate_language(df, config.random_state)
    html_info = estimate_html(df)
    duplicates = duplicate_indicators(df)
    max_length, max_length_reason = recommend_max_length(token_stats)

    plot_bar(overview["label_counts"], "Labelverteilung", "Anzahl", config.figures_dir / "label_distribution.png")
    plot_bar(overview["source_counts"], "Quellenverteilung", "Anzahl", config.figures_dir / "source_distribution.png")
    plot_hist(df["text_length"], "Verteilung der Textlaengen", "Zeichen", config.figures_dir / "text_length_distribution.png")
    plot_hist(df["word_count"], "Verteilung der Wortanzahlen", "Woerter", config.figures_dir / "word_count_distribution.png")
    plot_hist(df["token_count"], "Verteilung der DistilBERT-Tokenlaengen", "Tokens", config.figures_dir / "token_length_distribution.png")
    plot_boxplot_by_group(
        df,
        "text_length",
        "source",
        "Textlaengen nach Quelle",
        "Zeichen",
        config.figures_dir / "boxplot_textlength_by_source.png",
    )
    plot_label_boxplots(df, config.figures_dir / "boxplot_by_label.png")

    report = build_report(
        df,
        overview,
        missing,
        char_stats,
        word_stats,
        token_stats,
        language,
        html_info,
        duplicates,
        max_length,
        max_length_reason,
    )
    config.report_path.write_text(report, encoding="utf-8")
    return {
        "total": len(df),
        "label_counts": overview["label_counts"].to_dict(),
        "source_counts": overview["source_counts"].to_dict(),
        "recommended_max_length": max_length,
        "token_mean": token_stats["mean"],
        "token_p95": token_stats["p95"],
        "duplicates": duplicates,
        "language": language,
    }


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    config = EdaConfig(
        project_root=project_root,
        input_csv=project_root / "data" / "processed" / "emails_dataset_raw.csv",
        report_path=project_root / "data" / "processed" / "eda_report.md",
        figures_dir=project_root / "reports" / "figures",
        tokenizer_name="distilbert-base-uncased",
        random_state=42,
    )
    summary = run_analysis(config)
    print("EDA abgeschlossen", flush=True)
    print(f"Gesamtanzahl: {summary['total']}", flush=True)
    print(f"Labelverteilung: {summary['label_counts']}", flush=True)
    print(f"Quellenverteilung: {summary['source_counts']}", flush=True)
    print(f"Empfohlene max_length: {summary['recommended_max_length']}", flush=True)
    print(f"Durchschnittliche Tokenanzahl: {summary['token_mean']:.2f}", flush=True)
    print(f"95%-Perzentil Tokens: {summary['token_p95']:.2f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
