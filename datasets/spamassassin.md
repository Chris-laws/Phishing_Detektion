# SpamAssassin Public Mail Corpus

## Herkunft
- Lokale Roharchive: `data/raw/archives/`
- Entpackte lokale Daten: `data/raw/spamassassin/`
- Primaerquelle: Apache SpamAssassin Public Corpus
- URL: https://spamassassin.apache.org/old/publiccorpus/
- README: https://spamassassin.apache.org/old/publiccorpus/readme.html

## Version
- Enthaltene lokale Archive unter `data/raw/archives/`:
  - `20021010_easy_ham.tar.bz2`
  - `20021010_hard_ham.tar.bz2`
  - `20021010_spam.tar.bz2`
  - `20030228_spam_2.tar.bz2`
- Korpus-Versionen: 2002-10-10 und 2003-02-28
- Lokaler Download-Zeitpunkt: 2026-07-06

## Lizenz
- Das README nennt keine einheitliche offene Lizenz fuer alle Nachrichten.
- Copyright der Nachrichtentexte verbleibt laut README bei den urspruenglichen Absendern.
- Der Korpus ist fuer Tests von Spamfiltern gedacht; die Nachrichten duerfen nicht in Live-Mail-Systeme eingespeist werden.

## Anzahl Mails
- Lokal gezaehlte nutzbare Dateien:
  - easy_ham: 2551
  - hard_ham: 250
  - spam: 501
  - spam_2: 1397
- Gesamt lokal: 4699
- Ham gesamt lokal: 2801
- Spam gesamt lokal: 1898

## Klassen
- `easy_ham`: legitime, eher leicht von Spam unterscheidbare E-Mails
- `hard_ham`: legitime, spamnahe E-Mails
- `spam` und `spam_2`: Spam

## Besonderheiten
- Nachrichten liegen als einzelne Rohmails mit vollstaendigen Headern vor.
- Ham- und Spam-Klassen sind bereits durch Archivnamen getrennt.
- `hard_ham` ist besonders wertvoll als schwierige Negativklasse, weil die Nachrichten spamtypische Merkmale enthalten koennen.

## Limitationen
- Datensatz ist alt; heutige Spam- und Phishing-Muster sind nur eingeschraenkt abgebildet.
- Spam ist nicht gleich Phishing; Spam-Beispiele sollten nicht pauschal als Phishing gelabelt werden.
- Netzwerk-Reputation, Blacklists und URLs koennen sich seit Erhebung veraendert haben.
- Einige Header und Hostnamen wurden obfuskiert oder bereinigt.

## Verwendung in der BA
- Einsatz als Ham/Spam-Baseline fuer klassische E-Mail-Klassifikation.
- `easy_ham` und `hard_ham` als legitime bzw. nicht-phishing Klasse nutzen.
- `spam` und `spam_2` separat als Spam-Klasse fuehren oder bei binaerer Phishing-Erkennung nur kontrolliert einbeziehen.
