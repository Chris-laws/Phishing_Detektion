# Audit Report

- Zeitpunkt des Audits: `2026-07-06T13:13:33`
- Projektwurzel: `C:\Users\IT-Admin\Phishing_Detektion\Phishing_Detektion`

## Gefundene Ordnerstruktur
- `data/raw/enron`: vorhanden
- `data/raw/spamassassin`: vorhanden
- `data/raw/phishing_curated`: vorhanden
- `data/raw/synthetic_ai`: vorhanden
- `data/processed`: vorhanden
- `datasets`: vorhanden
- `src`: vorhanden

## Ergebnisse

### Projektstruktur
- **OK**: Ordner vorhanden: data/raw/enron
- **OK**: Ordner vorhanden: data/raw/spamassassin
- **OK**: Ordner vorhanden: data/raw/phishing_curated
- **OK**: Ordner vorhanden: data/raw/synthetic_ai
- **OK**: Ordner vorhanden: data/processed
- **OK**: Ordner vorhanden: datasets
- **OK**: Ordner vorhanden: src
- **OK**: Datei vorhanden: datasets/enron.md
- **OK**: Datei vorhanden: datasets/spamassassin.md
- **OK**: Datei vorhanden: datasets/phishing_curated.md
- **OK**: Datei vorhanden: datasets/synthetic_ai.md
- **OK**: Datei vorhanden: README.md
- **OK**: Datei vorhanden: requirements.txt

Details:
- Gefundene raw-Unterordner: archives, enron, phishing_curated, spamassassin, synthetic_ai

### Enron Dataset
- **OK**: Entpackter Maildir-Ordner gefunden: data/raw/enron/maildir
- **OK**: Enron-Stichprobe ist lesbar und enthaelt E-Mail-Struktur.

Details:
- Anzahl Dateien: 517401
- Stichprobe Enron: 20/20 lesbar, 20/20 mit Text, 20/20 mit typischen Headern.

### SpamAssassin Dataset
- **OK**: Unterordner vorhanden: data/raw/spamassassin/easy_ham
- **OK**: easy_ham: Stichprobe ist lesbar und enthaelt E-Mail-Struktur.
- **OK**: Unterordner vorhanden: data/raw/spamassassin/hard_ham
- **OK**: hard_ham: Stichprobe ist lesbar und enthaelt E-Mail-Struktur.
- **OK**: Unterordner vorhanden: data/raw/spamassassin/spam
- **OK**: spam: Stichprobe ist lesbar und enthaelt E-Mail-Struktur.
- **WARNUNG**: data/raw/spamassassin/spam/0000.7b1b73cf36cf9dbc3d64e3f2ee2b91f1 ohne typische Header in der Stichprobe
- **OK**: Unterordner vorhanden: data/raw/spamassassin/spam_2
- **OK**: spam_2: Stichprobe ist lesbar und enthaelt E-Mail-Struktur.

Details:
- easy_ham: 2551 Dateien
- Stichprobe easy_ham: 10/10 lesbar, 10/10 mit Text, 10/10 mit typischen Headern.
- hard_ham: 250 Dateien
- Stichprobe hard_ham: 10/10 lesbar, 10/10 mit Text, 10/10 mit typischen Headern.
- spam: 501 Dateien
- Stichprobe spam: 10/10 lesbar, 10/10 mit Text, 9/10 mit typischen Headern.
- spam_2: 1398 Dateien
- Stichprobe spam_2: 10/10 lesbar, 10/10 mit Text, 10/10 mit typischen Headern.

### Curated Phishing Dataset
- **OK**: CSV vorhanden: data/raw/phishing_curated/Nazario.csv
- **OK**: Nazario.csv: Spalte `body` vorhanden.
- **OK**: Nazario.csv: Spalte `subject` vorhanden.
- **OK**: Nazario.csv: Spalte `label` vorhanden.
- **OK**: Nazario.csv: Nutzbare Textspalten fuer spaeteres Textfeld: body, subject
- **OK**: CSV vorhanden: data/raw/phishing_curated/Nigerian_Fraud.csv
- **OK**: Nigerian_Fraud.csv: Spalte `body` vorhanden.
- **OK**: Nigerian_Fraud.csv: Spalte `subject` vorhanden.
- **OK**: Nigerian_Fraud.csv: Spalte `label` vorhanden.
- **OK**: Nigerian_Fraud.csv: Nutzbare Textspalten fuer spaeteres Textfeld: body, subject

Details:
- Nazario.csv: 1565 Zeilen
- Nazario.csv: Spalten: sender, receiver, date, subject, body, urls, label
- Nazario.csv: Fehlende Werte je Spalte: sender=0, receiver=96, date=1, subject=4, body=0, urls=0, label=0
- Nazario.csv: eindeutige label-Werte: [1]
- Nigerian_Fraud.csv: 3332 Zeilen
- Nigerian_Fraud.csv: Spalten: sender, receiver, date, subject, body, urls, label
- Nigerian_Fraud.csv: Fehlende Werte je Spalte: sender=331, receiver=1324, date=482, subject=39, body=0, urls=0, label=0
- Nigerian_Fraud.csv: eindeutige label-Werte: [1]

### Synthetic AI Dataset
- **OK**: data/raw/synthetic_ai ist vorhanden.
- **OK**: synthetic_ai ist leer.

Details:
- Gefundene Dateien: 0

### Dokumentationspruefung
- **WARNUNG**: datasets/enron.md: fehlende Ueberschriften: Ziel der Verwendung, Rohformat
- **WARNUNG**: datasets/phishing_curated.md: fehlende Ueberschriften: Ziel der Verwendung, Rohformat
- **WARNUNG**: datasets/spamassassin.md: fehlende Ueberschriften: Ziel der Verwendung, Rohformat
- **WARNUNG**: datasets/synthetic_ai.md: fehlende Ueberschriften: Ziel der Verwendung, Rohformat

## Erkannte Probleme
- **WARNUNG**: data/raw/spamassassin/spam/0000.7b1b73cf36cf9dbc3d64e3f2ee2b91f1 ohne typische Header in der Stichprobe
- **WARNUNG**: datasets/enron.md: fehlende Ueberschriften: Ziel der Verwendung, Rohformat
- **WARNUNG**: datasets/phishing_curated.md: fehlende Ueberschriften: Ziel der Verwendung, Rohformat
- **WARNUNG**: datasets/spamassassin.md: fehlende Ueberschriften: Ziel der Verwendung, Rohformat
- **WARNUNG**: datasets/synthetic_ai.md: fehlende Ueberschriften: Ziel der Verwendung, Rohformat

## Konkrete naechste Schritte
- Datenblaetter in `datasets/` an die geforderten Ueberschriften angleichen.
