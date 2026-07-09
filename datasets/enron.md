# Enron Email Dataset

## Herkunft
- Lokales Roharchiv: `data/raw/archives/enron_mail_20150507.tar.gz`
- Entpackte lokale Daten: `data/raw/enron/maildir/`
- Primaerquelle: CMU Enron Email Dataset, CALO Project
- URL: https://www.cs.cmu.edu/~enron/
- Ursprung: E-Mails wurden im Rahmen der FERC-Untersuchung zu Enron oeffentlich verfuegbar und spaeter fuer Forschungszwecke aufbereitet.

## Version
- Datei: `enron_mail_20150507.tar.gz`
- Version: May 7, 2015 version
- Lokaler Download-Zeitpunkt: 2026-07-06

## Lizenz
- Auf der CMU-Seite ist keine explizite Standardlizenz wie CC BY oder MIT angegeben.
- Der Datensatz wird als Forschungsressource bereitgestellt.
- Wegen realer personenbezogener Kommunikation ist ein sorgsamer Umgang erforderlich; keine Rohmails in der Bachelorarbeit abdrucken.

## Anzahl Mails
- Lokal gezaehlte entpackte Dateien: 517401
- Die Primaerquelle beschreibt den Umfang als ca. 0.5 Mio. Nachrichten.

## Klassen
- Keine expliziten Labels im Rohdatensatz.
- Fuer dieses Projekt als legitime bzw. nicht-phishing Unternehmenskommunikation verwendbar, sofern diese Annahme in der Arbeit klar dokumentiert wird.

## Besonderheiten
- Realer Unternehmensmailverkehr von ca. 150 Enron-Nutzern.
- Maildir-aehnliche Ordnerstruktur nach Nutzern und Mailbox-Ordnern.
- Keine Attachments in dieser Version.
- Einige Nachrichten wurden redigiert oder entfernt.

## Limitationen
- Altbestand aus einem spezifischen Unternehmenskontext; Sprache, Themen und Angriffsbild unterscheiden sich deutlich von modernen Phishing-Mails.
- Keine nativen Spam-/Phishing-Labels.
- Datenschutz- und Ethikrisiko durch reale Kommunikation.
- Moegliche Duplikate, Weiterleitungen und Antwortketten muessen bei der Vorverarbeitung beruecksichtigt werden.

## Verwendung in der BA
- Einsatz als legitime Vergleichsklasse bzw. Ham-Korpus.
- Nicht als alleinige Negativklasse verwenden, sondern mit SpamAssassin-Ham kombinieren.
- In der Methodik klar festhalten, dass Enron nicht als kuratierter Anti-Phishing-Datensatz entstanden ist.
