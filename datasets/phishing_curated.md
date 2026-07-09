# Curated Phishing Datasets

## Herkunft
- Lokaler Rohdatensatz: `data/raw/phishing_curated/`
- Dateien:
  - `Nazario.csv`
  - `Nigerian_Fraud.csv`
- Vermutete/zugeordnete Quelle: Figshare "Phishing Email: 11 Curated Datasets"
- URL: https://figshare.com/articles/dataset/Phishing_Email_11_Curated_Datasets/24952503
- DOI: https://doi.org/10.6084/m9.figshare.24952503

## Version
- Figshare-Veroeffentlichung: 2024-01-05
- Lokaler Download-Zeitpunkt: 2026-07-06
- Lokale Dateinamen:
  - `Nazario.csv`
  - `Nigerian_Fraud.csv`

## Lizenz
- Figshare-Eintrag: CC BY 4.0.
- Bei Verwendung in der Bachelorarbeit Quelle und DOI zitieren.

## Anzahl Mails
- Lokal per CSV-Parser gezaehlt:
  - Nazario: 1565 Datensaetze
  - Nigerian_Fraud: 3332 Datensaetze
- Gesamt: 4897 Datensaetze
- CSV-Spalten: `sender`, `receiver`, `date`, `subject`, `body`, `urls`, `label`

## Klassen
- Beide Dateien enthalten nur Phishing-Mails.
- Lokales Label: `1` fuer alle geparsten Datensaetze.

## Besonderheiten
- Enthalten kuratierte Phishing-Beispiele aus bekannten Phishing-/Fraud-Sammlungen.
- Einheitliches CSV-Schema erleichtert die Zusammenfuehrung mit anderen Quellen.
- URLs sind als eigene Spalte vorhanden und koennen fuer Feature Engineering genutzt werden.

## Limitationen
- Keine legitimen Gegenbeispiele innerhalb dieser beiden Dateien.
- Nigerian-Fraud-Beispiele koennen stilistisch stark auf Vorschussbetrug fokussiert sein und moderne Phishing-Varianten nur teilweise abdecken.
- Klassenbalance muss durch Kombination mit Ham-Datensaetzen hergestellt werden.
- CSV-Inhalte enthalten Mailtexte; vor oeffentlicher Darstellung anonymisieren oder nur aggregiert auswerten.

## Verwendung in der BA
- Primaere Phishing-Klasse fuer binaere Klassifikation.
- Mit Enron und SpamAssassin-Ham als legitime Klasse kombinieren.
- Nigerian_Fraud bei Bedarf getrennt auswerten, um Verzerrungen durch Scam-spezifische Sprache sichtbar zu machen.
