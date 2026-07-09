from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable


try:
    import pandas as pd
except ImportError:  # pragma: no cover - handled at runtime in the audit report
    pd = None


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "data" / "processed" / "audit_report.md"


@dataclass
class CheckResult:
    status: str
    message: str


@dataclass
class SectionReport:
    title: str
    results: list[CheckResult] = field(default_factory=list)
    details: list[str] = field(default_factory=list)

    def ok(self, message: str) -> None:
        self.results.append(CheckResult("OK", message))

    def warn(self, message: str) -> None:
        self.results.append(CheckResult("WARNUNG", message))

    def error(self, message: str) -> None:
        self.results.append(CheckResult("FEHLER", message))

    def detail(self, message: str) -> None:
        self.details.append(message)


EMAIL_HEADERS = ("from:", "to:", "subject:", "date:")
REQUIRED_DIRS = (
    "data/raw/enron",
    "data/raw/spamassassin",
    "data/raw/phishing_curated",
    "data/raw/synthetic_ai",
    "data/processed",
    "datasets",
    "src",
)
REQUIRED_FILES = (
    "datasets/enron.md",
    "datasets/spamassassin.md",
    "datasets/phishing_curated.md",
    "datasets/synthetic_ai.md",
    "README.md",
    "requirements.txt",
)
SPAMASSASSIN_DIRS = ("easy_ham", "hard_ham", "spam", "spam_2")
PHISHING_CSVS = ("Nazario.csv", "Nigerian_Fraud.csv")
REQUIRED_MARKDOWN_HEADINGS = (
    "Herkunft",
    "Ziel der Verwendung",
    "Anzahl",
    "Klassen",
    "Rohformat",
    "Besonderheiten",
    "Limitationen",
    "Verwendung in der BA",
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def iter_files(path: Path) -> Iterable[Path]:
    if not path.exists() or not path.is_dir():
        return []
    return (p for p in path.rglob("*") if p.is_file())


def count_files(path: Path) -> int:
    return sum(1 for _ in iter_files(path))


def read_text_sample(path: Path, max_chars: int = 8000) -> tuple[bool, str, str | None]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            text = handle.read(max_chars)
        return True, text, None
    except OSError as exc:
        return False, "", str(exc)


def check_email_samples(files: list[Path], sample_size: int) -> tuple[int, int, int, list[str]]:
    readable = 0
    non_empty = 0
    with_headers = 0
    problems: list[str] = []

    for path in files[:sample_size]:
        ok, text, error = read_text_sample(path)
        if not ok:
            problems.append(f"{rel(path)} nicht lesbar: {error}")
            continue
        readable += 1
        stripped = text.strip()
        if stripped:
            non_empty += 1
        lower_text = text.lower()
        if any(header in lower_text for header in EMAIL_HEADERS):
            with_headers += 1
        else:
            problems.append(f"{rel(path)} ohne typische Header in der Stichprobe")

    return readable, non_empty, with_headers, problems


def audit_project_structure() -> SectionReport:
    section = SectionReport("Projektstruktur")

    for item in REQUIRED_DIRS:
        path = ROOT / item
        if path.is_dir():
            section.ok(f"Ordner vorhanden: {item}")
        else:
            section.error(f"Ordner fehlt: {item}")

    for item in REQUIRED_FILES:
        path = ROOT / item
        if path.is_file():
            section.ok(f"Datei vorhanden: {item}")
        else:
            section.error(f"Datei fehlt: {item}")

    top_level = sorted(p.name for p in (ROOT / "data" / "raw").iterdir()) if (ROOT / "data" / "raw").is_dir() else []
    section.detail("Gefundene raw-Unterordner: " + (", ".join(top_level) if top_level else "keine"))
    return section


def audit_enron() -> SectionReport:
    section = SectionReport("Enron Dataset")
    enron_dir = ROOT / "data" / "raw" / "enron"
    archives = list(enron_dir.glob("*.tar.gz")) + list(enron_dir.glob("*.tgz"))

    if not enron_dir.is_dir():
        section.error("data/raw/enron fehlt.")
        return section

    maildir_candidates = [p for p in enron_dir.iterdir() if p.is_dir() and p.name.lower() == "maildir"]
    if not maildir_candidates:
        nested = [p for p in enron_dir.rglob("maildir") if p.is_dir()]
        maildir_candidates.extend(nested)

    if not maildir_candidates:
        if archives:
            section.warn("Nur ein Enron-Archiv gefunden, aber kein entpackter Maildir-Ordner.")
        else:
            section.error("Kein entpackter Enron-Maildir-Ordner gefunden.")
        return section

    maildir = maildir_candidates[0]
    files = sorted(iter_files(maildir))
    section.ok(f"Entpackter Maildir-Ordner gefunden: {rel(maildir)}")
    section.detail(f"Anzahl Dateien: {len(files)}")

    readable, non_empty, with_headers, problems = check_email_samples(files, 20)
    section.detail(f"Stichprobe Enron: {readable}/20 lesbar, {non_empty}/20 mit Text, {with_headers}/20 mit typischen Headern.")
    if files and readable == min(20, len(files)) and non_empty == min(20, len(files)) and with_headers > 0:
        section.ok("Enron-Stichprobe ist lesbar und enthaelt E-Mail-Struktur.")
    else:
        section.warn("Enron-Stichprobe ist teilweise auffaellig oder leer.")
    for problem in problems[:10]:
        section.warn(problem)

    return section


def audit_spamassassin() -> SectionReport:
    section = SectionReport("SpamAssassin Dataset")
    base = ROOT / "data" / "raw" / "spamassassin"

    if not base.is_dir():
        section.error("data/raw/spamassassin fehlt.")
        return section

    archives = list(base.glob("*.tar.bz2"))
    missing_dirs = []
    for folder in SPAMASSASSIN_DIRS:
        path = base / folder
        if not path.is_dir():
            missing_dirs.append(folder)
            section.error(f"Unterordner fehlt: {rel(path)}")
            continue

        files = sorted(iter_files(path))
        section.ok(f"Unterordner vorhanden: {rel(path)}")
        section.detail(f"{folder}: {len(files)} Dateien")
        readable, non_empty, with_headers, problems = check_email_samples(files, 10)
        sample_target = min(10, len(files))
        section.detail(
            f"Stichprobe {folder}: {readable}/{sample_target} lesbar, "
            f"{non_empty}/{sample_target} mit Text, {with_headers}/{sample_target} mit typischen Headern."
        )
        if files and readable == sample_target and non_empty == sample_target and with_headers > 0:
            section.ok(f"{folder}: Stichprobe ist lesbar und enthaelt E-Mail-Struktur.")
        else:
            section.warn(f"{folder}: Stichprobe ist teilweise auffaellig oder leer.")
        for problem in problems[:5]:
            section.warn(problem)

    if archives and missing_dirs:
        section.warn("SpamAssassin enthaelt .tar.bz2-Archive, aber nicht alle entpackten Ordner sind vorhanden.")
    elif archives:
        section.detail("Hinweis: Im SpamAssassin-Ordner liegen noch Archive neben entpackten Daten.")

    return section


def load_csv(path: Path) -> tuple[object | None, str | None]:
    if pd is None:
        return None, "pandas ist nicht installiert."
    try:
        return pd.read_csv(path), None
    except Exception as first_error:
        try:
            return pd.read_csv(path, engine="python", on_bad_lines="skip"), (
                f"Standard-CSV-Parser fehlgeschlagen, Fallback mit uebersprungenen fehlerhaften Zeilen genutzt: {first_error}"
            )
        except Exception as second_error:
            return None, f"CSV nicht lesbar: {second_error}"


def audit_phishing_curated() -> SectionReport:
    section = SectionReport("Curated Phishing Dataset")
    base = ROOT / "data" / "raw" / "phishing_curated"

    if not base.is_dir():
        section.error("data/raw/phishing_curated fehlt.")
        return section

    for filename in PHISHING_CSVS:
        path = base / filename
        if not path.is_file():
            section.error(f"CSV fehlt: {rel(path)}")
            continue

        section.ok(f"CSV vorhanden: {rel(path)}")
        df, error = load_csv(path)
        if error and df is None:
            section.error(f"{filename}: {error}")
            continue
        if error:
            section.warn(f"{filename}: {error}")
        if df is None:
            continue

        row_count = len(df)
        columns = [str(column) for column in df.columns]
        section.detail(f"{filename}: {row_count} Zeilen")
        section.detail(f"{filename}: Spalten: {', '.join(columns) if columns else 'keine'}")
        if row_count == 0:
            section.warn(f"{filename}: CSV ist leer.")

        missing = df.isna().sum().to_dict()
        missing_text = ", ".join(f"{column}={count}" for column, count in missing.items())
        section.detail(f"{filename}: Fehlende Werte je Spalte: {missing_text if missing_text else 'keine Spalten'}")

        for column in ("body", "subject", "label"):
            if column in df.columns:
                section.ok(f"{filename}: Spalte `{column}` vorhanden.")
            else:
                section.warn(f"{filename}: Spalte `{column}` fehlt.")

        if "label" in df.columns:
            labels = df["label"].dropna().unique().tolist()
            section.detail(f"{filename}: eindeutige label-Werte: {labels}")

        usable_text_columns = []
        for column in ("body", "subject"):
            if column in df.columns and df[column].fillna("").astype(str).str.strip().ne("").any():
                usable_text_columns.append(column)
        if usable_text_columns:
            section.ok(f"{filename}: Nutzbare Textspalten fuer spaeteres Textfeld: {', '.join(usable_text_columns)}")
        else:
            section.warn(f"{filename}: Weder `body` noch `subject` enthalten nutzbaren Text.")

        expected_columns = {"sender", "receiver", "date", "subject", "body", "urls", "label"}
        if not expected_columns.issubset(set(columns)):
            section.warn(f"{filename}: Struktur weicht vom erwarteten Schema ab.")

    return section


def audit_synthetic_ai() -> SectionReport:
    section = SectionReport("Synthetic AI Dataset")
    base = ROOT / "data" / "raw" / "synthetic_ai"

    if not base.is_dir():
        section.error("data/raw/synthetic_ai fehlt.")
        return section

    files = sorted(iter_files(base))
    section.ok("data/raw/synthetic_ai ist vorhanden.")
    section.detail(f"Gefundene Dateien: {len(files)}")
    if files:
        section.warn(
            "Hinweis: synthetic_ai enthaelt bereits Dateien. Methodisch sollte dieser Ordner erst spaeter "
            "fuer das separate Zero-Day-Testset verwendet werden."
        )
    else:
        section.ok("synthetic_ai ist leer.")
    return section


def audit_documentation() -> SectionReport:
    section = SectionReport("Dokumentationspruefung")
    docs_dir = ROOT / "datasets"

    if not docs_dir.is_dir():
        section.error("datasets-Ordner fehlt.")
        return section

    for path in sorted(docs_dir.glob("*.md")):
        ok, text, error = read_text_sample(path, max_chars=200000)
        if not ok:
            section.error(f"{rel(path)} nicht lesbar: {error}")
            continue

        missing = []
        lowered = text.lower()
        for heading in REQUIRED_MARKDOWN_HEADINGS:
            needle = heading.lower()
            if f"# {needle}" not in lowered and f"## {needle}" not in lowered and f"### {needle}" not in lowered:
                missing.append(heading)

        if missing:
            section.warn(f"{rel(path)}: fehlende Ueberschriften: {', '.join(missing)}")
        else:
            section.ok(f"{rel(path)}: alle geforderten Ueberschriften vorhanden.")

    return section


def collect_next_steps(sections: list[SectionReport]) -> list[str]:
    steps: list[str] = []
    all_results = [result for section in sections for result in section.results]

    if any(result.status == "FEHLER" for result in all_results):
        steps.append("Als Erstes alle FEHLER beheben, weil sie auf fehlende Pflichtbestandteile hinweisen.")
    if any("fehlende Ueberschriften" in result.message for result in all_results):
        steps.append("Datenblaetter in `datasets/` an die geforderten Ueberschriften angleichen.")
    if any("pandas ist nicht installiert" in result.message for result in all_results):
        steps.append("`pandas` in der Projektumgebung installieren und Audit erneut ausfuehren.")
    if any("synthetic_ai enthaelt bereits Dateien" in result.message for result in all_results):
        steps.append("Dateien in `data/raw/synthetic_ai/` bis zum separaten Zero-Day-Testset entfernen oder bewusst dokumentieren.")
    if any("Stichprobe ist teilweise auffaellig" in result.message for result in all_results):
        steps.append("Auffaellige E-Mail-Stichproben manuell pruefen, bevor Vorverarbeitung oder Training geplant wird.")
    if not steps:
        steps.append("Projektstruktur und Datengrundlage sind fuer die naechste vorbereitende Phase plausibel.")
    return steps


def render_console(sections: list[SectionReport]) -> None:
    print("AUDIT-REPORT")
    print(f"Projekt: {ROOT}")
    print(f"Zeitpunkt: {datetime.now().isoformat(timespec='seconds')}")
    print()

    for section in sections:
        print(f"## {section.title}")
        for result in section.results:
            print(f"[{result.status}] {result.message}")
        for detail in section.details:
            print(f"  - {detail}")
        print()

    counts = {"OK": 0, "WARNUNG": 0, "FEHLER": 0}
    for result in (result for section in sections for result in section.results):
        counts[result.status] = counts.get(result.status, 0) + 1
    print("ZUSAMMENFASSUNG")
    print(f"OK: {counts['OK']} | WARNUNG: {counts['WARNUNG']} | FEHLER: {counts['FEHLER']}")


def render_markdown(sections: list[SectionReport]) -> str:
    now = datetime.now().isoformat(timespec="seconds")
    lines = [
        "# Audit Report",
        "",
        f"- Zeitpunkt des Audits: `{now}`",
        f"- Projektwurzel: `{ROOT}`",
        "",
        "## Gefundene Ordnerstruktur",
    ]

    for item in REQUIRED_DIRS:
        path = ROOT / item
        status = "vorhanden" if path.is_dir() else "fehlt"
        lines.append(f"- `{item}`: {status}")

    lines.extend(["", "## Ergebnisse"])
    for section in sections:
        lines.extend(["", f"### {section.title}"])
        for result in section.results:
            lines.append(f"- **{result.status}**: {result.message}")
        if section.details:
            lines.append("")
            lines.append("Details:")
            for detail in section.details:
                lines.append(f"- {detail}")

    problems = [
        result for section in sections for result in section.results if result.status in {"WARNUNG", "FEHLER"}
    ]
    lines.extend(["", "## Erkannte Probleme"])
    if problems:
        for result in problems:
            lines.append(f"- **{result.status}**: {result.message}")
    else:
        lines.append("- Keine Warnungen oder Fehler erkannt.")

    lines.extend(["", "## Konkrete naechste Schritte"])
    for step in collect_next_steps(sections):
        lines.append(f"- {step}")

    lines.append("")
    return "\n".join(lines)


def write_markdown_report(sections: list[SectionReport]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(render_markdown(sections), encoding="utf-8")


def main() -> int:
    sections = [
        audit_project_structure(),
        audit_enron(),
        audit_spamassassin(),
        audit_phishing_curated(),
        audit_synthetic_ai(),
        audit_documentation(),
    ]
    render_console(sections)
    write_markdown_report(sections)
    print()
    print(f"Markdown-Report erstellt: {rel(REPORT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
