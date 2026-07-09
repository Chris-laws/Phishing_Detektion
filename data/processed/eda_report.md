# Explorative Datenanalyse des Arbeitsdatensatzes Version 1.0

## 1. Ziel der Analyse

Ziel dieser explorativen Datenanalyse ist die wissenschaftlich nachvollziehbare Beschreibung des Arbeitsdatensatzes `data/processed/emails_dataset_raw.csv`. Die Analyse dient als Grundlage fuer die spaetere transformerbasierte Phishing-E-Mail-Klassifikation, ohne bereits Modelltraining, Splits oder Feature-Engineering umzusetzen.

## 2. Datensatzuebersicht

Der Arbeitsdatensatz umfasst **16621 E-Mails**. Er kombiniert legitime Unternehmenskommunikation aus Enron, Ham-/Spam-Beispiele aus SpamAssassin sowie kuratierte Phishing-Daten.

### Anzahl pro Quelle

| source | anzahl |
| --- | --- |
| enron | 7341 |
| phishing_curated | 4843 |
| spamassassin | 4437 |

### Anzahl pro Subtype

| subtype | anzahl |
| --- | --- |
| enron | 7341 |
| nigerian_fraud | 3291 |
| easy_ham | 2408 |
| nazario | 1552 |
| spam_2 | 1329 |
| spam | 471 |
| hard_ham | 229 |

## 3. Datenqualitaet

### Fehlende Werte

| column | missing | missing_percent |
| --- | --- | --- |
| id | 0 | 0.0 |
| source | 0 | 0.0 |
| subtype | 0 | 0.0 |
| subject | 326 | 1.96 |
| body | 9 | 0.05 |
| text | 0 | 0.0 |
| label | 0 | 0.0 |
| generated | 0 | 0.0 |
| raw_path | 0 | 0.0 |

Fuer die spaetere Klassifikation ist die Spalte `text` entscheidend, da sie aus Betreff und Body kombiniert wurde. Fehlende Betreffzeilen sind daher nicht unmittelbar kritisch, solange der Body vorhanden ist. Sie koennen aber Informationsverlust bedeuten, da Betreffzeilen bei Phishing haeufig starke Hinweise auf Dringlichkeit, Markenbezug oder Aufforderungen enthalten.

Fokusspalten:

| column | missing | missing_percent |
| --- | --- | --- |
| subject | 326 | 1.96 |
| body | 9 | 0.05 |
| text | 0 | 0.0 |

## 4. Klassenverteilung

| label | anzahl |
| --- | --- |
| 0 | 9978 |
| 1 | 6643 |

### Prozentuale Klassenverteilung

| label | anteil_prozent |
| --- | --- |
| 0.0 | 60.03 |
| 1.0 | 39.97 |

Die legitime Klasse umfasst 9978 Instanzen, die Phishing-/verdächtige Klasse 6643 Instanzen. Die Verteilung ist moderat unausgeglichen, aber nicht extrem. Class Weights sollten spaeter dennoch geprueft werden, weil die Kosten falsch negativer Phishing-Erkennung hoeher sein koennen als reine Klassenanteile nahelegen.

## 5. Quellenanalyse

| source | text_length | word_count | token_count |
| --- | --- | --- | --- |
| enron | 1520.64 | 254.91 | 414.82 |
| phishing_curated | 3290.87 | 465.34 | 1193.17 |
| spamassassin | 2055.99 | 322.21 | 639.35 |

Die Quellen unterscheiden sich deutlich in Laenge und Herkunft. Enron repraesentiert legitime interne Unternehmenskommunikation, waehrend SpamAssassin und die kuratierten Phishing-Daten andere Kommunikationskontexte und teils andere Schreibstile abbilden. Diese Heterogenitaet ist fuer die Evaluation wertvoll, erzeugt aber ein Risiko fuer Domain Shift.

## 6. Textanalyse

### Zeichenlaengen

- Mittelwert: 2179.36
- Median: 1085.00
- Standardabweichung: 36450.52
- Minimum: 2.00
- 25%-Quartil: 484.00
- 75%-Quartil: 2288.00
- Maximum: 4560761.00

### Wortanzahlen

- Mittelwert: 334.19
- Median: 181.00
- Maximum: 288889.00

| label | text_length | word_count | token_count |
| --- | --- | --- | --- |
| 0.0 | 1600.86 | 267.89 | 444.31 |
| 1.0 | 3048.28 | 433.79 | 1087.93 |

## 7. Tokenanalyse

Die Tokenlaengen wurden mit dem DistilBERT-Tokenizer `distilbert-base-uncased` berechnet. Es wurden keine model-ready Token-Dateien erzeugt und kein Training vorbereitet.

- Mittelwert: 701.55
- Median: 297.00
- 95%-Perzentil: 1287.00
- Maximum: 2901224.00

Empfohlene `max_length`: **512**. Die Verteilung ist insgesamt lang; 512 reduziert Trunkierung, erhoeht aber Rechenaufwand. Diese Empfehlung ist als Ausgangspunkt zu verstehen; sie sollte spaeter gegen Rechenbudget, Trunkierungsrate und Modellleistung abgewogen werden.

## 8. Sprachanalyse

Die Sprache wurde heuristisch auf einer reproduzierbaren Stichprobe von 1000 E-Mails geschaetzt:

| sprache | anzahl |
| --- | --- |
| unbestimmt | 55 |
| englisch | 930 |
| deutsch | 2 |
| gemischt | 13 |

Da ueberwiegend englischsprachige oeffentliche Datensaetze verwendet werden, erfolgt die Evaluation auf dieser Sprachbasis. Deutschsprachige Phishing-Szenarien sind damit nur eingeschraenkt abgedeckt.

## 9. Erkenntnisse

- Residualer HTML-Hinweis im bereits bereinigten Text: 0 E-Mails.
- Plaintext-aehnlich nach bereinigtem Text: 16621 E-Mails.
- Exakte Textdubletten im Arbeitsdatensatz: 0.
- Die Anzahl bereits vor Version 1.0 entfernter Dubletten ist aus `emails_dataset_raw.csv` allein nicht rekonstruierbar; die EDA dokumentiert daher ausschliesslich verbleibende Dublettenindikatoren im Arbeitsdatensatz.
- Wiederholte Betreffzeilen: 3066.
- Wiederholte 250-Zeichen-Anfaenge als Hinweis auf verbleibende nahezu identische Texte: 247.

Der HTML-Anteil kann auf Basis des Arbeitsdatensatzes nur unterschaetzt werden, weil die Ingestion HTML-Tags bereits entfernt hat. Die Messung beschreibt daher verbleibende HTML-Artefakte, nicht den urspruenglichen MIME-Anteil.

## 10. Empfehlungen fuer die Modellierung

- `max_length`: 512, begruendet durch Median und 95%-Perzentil der DistilBERT-Tokenlaengen.
- Batch Size: initial 16 oder 32, abhaengig von GPU-Speicher; bei `max_length=512` eher 8 bis 16.
- Class Weights: pruefen, da eine moderate Klassenunwucht und asymmetrische Fehlerkosten vorliegen.
- Weitere Datenbereinigung: vor Training keine aggressive Entfernung mehr, aber auffaellige Systemzeilen und sehr lange Ausreisser dokumentiert pruefen.
- Overfitting-Risiko: wiederkehrende Templates, Nigerian-Fraud-Stil und Quellensignaturen koennen vom Modell auswendig gelernt werden.
- Domain-Shift-Risiko: Enron/SpamAssassin sind historisch und englischsprachig; moderne deutschsprachige Phishing-Mails koennen abweichen.

## 11. Limitationen

- Die Analyse basiert ausschliesslich auf Version 1.0 des Arbeitsdatensatzes und veraendert diese Datei nicht.
- Sprache und HTML-Anteil werden heuristisch aus bereits bereinigten Texten geschaetzt.
- Tokenlaengen wurden nur zur Laengenanalyse berechnet; es wurde keine Modellpipeline vorbereitet.
- Die Quellen sind historisch und oeffentlich; reale produktive Phishing-Umgebungen koennen andere Verteilungen aufweisen.
