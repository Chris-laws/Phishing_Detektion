# Synthetic AI / Human-LLM Email Dataset

## Herkunft
- Lokaler Status: aktuell nicht im Projekt abgelegt; Nutzung ist fuer nach dem Training vorgesehen.
- Vorgesehener Ablageort bei spaeterer Nutzung: `data/raw/synthetic_ai/`
- Urspruenglich bereitgestellte Datei: `Zeroday.zip`
- Zugeordnete Quelle: Kaggle "Human-LLM generated phishing-legitimate emails"
- URL: https://www.kaggle.com/datasets/francescogreco97/human-llm-generated-phishing-legitimate-emails

## Version
- Lokale Datei: derzeit entfernt
- Lokaler Download-Zeitpunkt: 2026-07-06
- Im Archiv enthaltene Dateien:
  - `human-generated/legit.csv`
  - `human-generated/phishing.csv`
  - `llm-generated/legit.csv`
  - `llm-generated/phishing.csv`

## Lizenz
- In der bereitgestellten ZIP-Datei wurde keine Lizenzdatei dauerhaft im Projekt abgelegt.
- Vor Veroeffentlichung von Ausschnitten oder Weitergabe des Datensatzes Kaggle-Lizenzseite erneut pruefen und zitieren.

## Anzahl Mails
- Lokal gezaehlte CSV-Datensaetze im ZIP:
  - human-generated/legit.csv: 142563
  - human-generated/phishing.csv: 4510
  - llm-generated/legit.csv: 1000
  - llm-generated/phishing.csv: 1000
- Gesamt: 149073

## Klassen
- `legit`: legitime E-Mails
- `phishing`: Phishing-E-Mails
- Zusaetzliche Dimension:
  - `human-generated`
  - `llm-generated`

## Besonderheiten
- Erlaubt getrennte Auswertung von menschlich geschriebenen und LLM-generierten E-Mails.
- Enthaelt sowohl legitime als auch Phishing-Beispiele.
- Besonders relevant fuer die Fragestellung, ob KI-generierte Phishing-Mails anders erkannt werden als klassische Phishing-Mails.

## Limitationen
- Starke Klassenungleichheit durch sehr viele menschlich generierte legitime E-Mails.
- LLM-generierte Teilmengen sind mit je 1000 Beispielen deutlich kleiner.
- Generierungsmodell, Prompting und Qualitaet der synthetischen Beispiele muessen vor finaler Interpretation aus der Quelle nachvollzogen werden.
- Synthetische Phishing-Mails koennen andere Artefakte enthalten als echte Angriffsmails.

## Verwendung in der BA
- Separater Evaluationsdatensatz fuer Robustheit gegen LLM-generierte Inhalte.
- Nicht unkontrolliert mit realen Phishing-Daten vermischen; stattdessen Quelle `human`/`llm` als Metadatum behalten.
- Fuer Experimente eine balancierte Teilmenge oder gewichtete Metriken verwenden.
