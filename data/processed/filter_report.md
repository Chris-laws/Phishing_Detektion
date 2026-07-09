# Dataset Refinement Report

## Ziel

Dieser Schritt erzeugt eine finale Trainingsgrundlage aus `emails_dataset_raw.csv`, ohne die Rohdaten oder Version 1.0 des Arbeitsdatensatzes zu veraendern. Die Filterung basiert ausschliesslich auf den bereits dokumentierten EDA-Erkenntnissen zu extremen Laengenausreissern.

## Manuelle Qualitaetsanalyse der 20 laengsten Dokumente

| id | source | subtype | label | text_length | token_count_review | subject | raw_path | vermutete_ursache |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| phishing_curated_nazario_0000001 | phishing_curated | nazario | 1 | 4560761 | 2901224.0 | DON'T DELETE THIS MESSAGE -- FOLDER INTERNAL DATA | data/raw/phishing_curated/Nazario.csv#row=2 | Mailbox-/Folder-Artefakt, keine eigentliche Nachricht |
| phishing_curated_nazario_0000528 | phishing_curated | nazario | 1 | 1023603 | 463695.0 | someone has your password | data/raw/phishing_curated/Nazario.csv#row=535 | extremer Laengenausreisser mit ungewoehnlicher Struktur |
| spamassassin_spam_0000328 | spamassassin | spam | 1 | 230889 | 149025.0 | May I have a moment of your Time PLEASE | data/raw/spamassassin/spam/0352.f7adb4aa267e50a8db1e4bcacfe863f3 | extremer Laengenausreisser mit ungewoehnlicher Struktur |
| spamassassin_hard_ham_0000194 | spamassassin | hard_ham | 0 | 163495 | 62508.0 | updated weblogs from blo.gs | data/raw/spamassassin/hard_ham/0196.9dc01775acba34e580ddf9a56ea6891e | sehr lange Newsletter-/Webseitenstruktur |
| spamassassin_spam_0000463 | spamassassin | spam | 1 | 125736 | 85061.0 | 一网“惠”天下，一展天下知----2003年4月1日--4 | data/raw/spamassassin/spam/0492.f2d030fd71d7c3075626195b5c0b56f7 | extremer Laengenausreisser mit ungewoehnlicher Struktur |
| phishing_curated_nigerian_fraud_0000351 | phishing_curated | nigerian_fraud | 1 | 122708 | 30582.0 | BUSINESS PROPOSER REQUESTING CHANGE OF OWNERSHIP | data/raw/phishing_curated/Nigerian_Fraud.csv#row=358 | extremer Laengenausreisser mit ungewoehnlicher Struktur |
| spamassassin_spam_2_0001329 | spamassassin | spam_2 | 1 | 113399 | 77227.0 |  | data/raw/spamassassin/spam_2/cmds | SpamAssassin-Steuerdatei, keine eigentliche E-Mail |
| spamassassin_easy_ham_0000730 | spamassassin | easy_ham | 0 | 88009 | 17454.0 | Re: sed /s/United States/Roman Empire/g | data/raw/spamassassin/easy_ham/0737.aa298505cb31aac78d0dbf229fc45fb9 | langer, aber plausibler Mailtext |
| spamassassin_easy_ham_0000723 | spamassassin | easy_ham | 0 | 84325 | 15683.0 | sed /s/United States/Roman Empire/g | data/raw/spamassassin/easy_ham/0730.9570ee3b6bf144198297b23bca5044e9 | langer, aber plausibler Mailtext |
| spamassassin_spam_2_0001026 | spamassassin | spam_2 | 1 | 72640 | 15783.0 | HAWAI`I & ENENKIO KINGDOMS AMERICANS SHAME ! | data/raw/spamassassin/spam_2/01083.a6b3c50be5abf782b585995d2c11176b | sehr lange Newsletter-/Webseitenstruktur |
| spamassassin_spam_0000239 | spamassassin | spam | 1 | 71407 | 15463.0 | LIE`S, MIS-INFORMATION and FRAUD | data/raw/spamassassin/spam/0255.42a6feb4435a0a68929075c0926f085d | sehr lange Newsletter-/Webseitenstruktur |
| spamassassin_spam_2_0000050 | spamassassin | spam_2 | 1 | 51402 | 13097.0 | Your Membership Community & Commentary, 06-29-01 | data/raw/spamassassin/spam_2/00051.8b17ce16ace4d5845e2299c0123e1f14 | sehr lange Newsletter-/Webseitenstruktur |
| spamassassin_spam_2_0000194 | spamassassin | spam_2 | 1 | 48867 | 32365.0 | Votre maintenance Informatique | data/raw/spamassassin/spam_2/00200.2fcabc2b58baa0ebc051e3ea3dfafd8f | langer, aber plausibler Mailtext |
| spamassassin_spam_2_0000030 | spamassassin | spam_2 | 1 | 43810 | 30060.0 | READ---SHIPPING INSTRUTIONS--FOR YOUR ORDER | data/raw/spamassassin/spam_2/00030.b360f27c098b3ab5cff96433e7963d4a | langer, aber plausibler Mailtext |
| spamassassin_easy_ham_0000622 | spamassassin | easy_ham | 0 | 40076 |  | CBS News' interview w/Bush & reconstruction of his peregrinations | data/raw/spamassassin/easy_ham/0627.c9ad8730dad7bda1e1169ee00c4006fc | langer, aber plausibler Mailtext |
| enron_enron_0006180 | enron | enron | 0 | 40043 |  | National Journal's CongressDaily - Wednesday, October 24, 2001 | data/raw/enron/maildir/shapiro-r/deleted_items/491 | langer, aber plausibler Mailtext |
| enron_enron_0000789 | enron | enron | 0 | 40031 |  | VentureWire, Friday, May 25, 2001 | data/raw/enron/maildir/dasovich-j/all_documents/13073 | sehr lange Newsletter-/Webseitenstruktur |
| enron_enron_0003678 | enron | enron | 0 | 39168 |  | Enron Mentions | data/raw/enron/maildir/kitchen-l/_americas/sec_media/56 | langer, aber plausibler Mailtext |
| spamassassin_easy_ham_0000983 | spamassassin | easy_ham | 0 | 38002 |  | Re: Lord of the Ringtones: Arbocks vs. Seelecks | data/raw/spamassassin/easy_ham/1022.73ab70b91862d709897cfe3dd5bb22a0 | langer, aber plausibler Mailtext |
| enron_enron_0001021 | enron | enron | 0 | 37234 |  | VentureWire, Thursday, September 14, 2000 | data/raw/enron/maildir/dasovich-j/notes_inbox/427 | sehr lange Newsletter-/Webseitenstruktur |

## Angewendete Filterregeln

1. Entferne technische SpamAssassin-Steuerdateien (`cmds` oder Zeilenmuster `mv <nummer> ...`).
   Begruendung: Diese Dateien sind keine E-Mails und enthalten keine natuerliche Nachricht.
2. Entferne Mailbox-/Folder-Artefakte mit Subject `DON'T DELETE THIS MESSAGE -- FOLDER INTERNAL DATA`.
   Begruendung: Diese Zeilen repraesentieren internes Mailboxformat, nicht den Inhalt einer E-Mail.
3. Entferne Dokumente mit `text_length > 100000` Zeichen.
   Begruendung: Die manuelle Sichtung zeigt, dass diese extremen Laengenausreisser durch Artefakte, MIME-/Base64-Bloecke, Steuerdateien oder sehr untypische Dokumentstrukturen dominiert werden. Die Regel ist datenqualitaetsbezogen und nicht leistungsbezogen.

## Entfernte Dokumente

- Anzahl vor Filterung: 16621
- Anzahl entfernt: 9
- Finale Datensatzgroesse: 16612

### Betroffene Quellen/Subtypes

| source | subtype | label | removed |
| --- | --- | --- | --- |
| phishing_curated | nazario | 1 | 3 |
| phishing_curated | nigerian_fraud | 1 | 1 |
| spamassassin | hard_ham | 0 | 1 |
| spamassassin | spam | 1 | 3 |
| spamassassin | spam_2 | 1 | 1 |

## Labelverteilung vorher

| label | anzahl |
| --- | --- |
| 0 | 9978 |
| 1 | 6643 |

## Labelverteilung nachher

| label | anzahl |
| --- | --- |
| 0 | 9977 |
| 1 | 6635 |

## Wissenschaftliche Einordnung

Die Filterregeln entfernen nur dokumentierte Datenqualitaetsprobleme. Es werden keine Split-Entscheidungen, keine Modellannahmen und keine leistungsorientierten Optimierungen vorgenommen. Der Rohdatensatz bleibt erhalten; `emails_dataset_filtered.csv` ist die daraus abgeleitete finale Trainingsgrundlage.
