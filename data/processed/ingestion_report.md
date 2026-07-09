# Ingestion Report

- Start: `2026-07-09T10:19:10`
- Ende: `2026-07-09T10:21:14`
- Ausgabe: `data/processed/emails_dataset_raw.csv`
- Gewaehlte Enron-Sample-Size: `7500`
- Enron-Kandidaten nach Filter: `516317`

## Methodische Begruendung der Enron-Stichprobe

Enron wird nicht vollstaendig materialisiert, weil der Korpus mit 517401 Dateien die legitime Klasse massiv dominieren wuerde. Fuer das Arbeitsdataset wird deshalb eine reproduzierbare Stichprobe genutzt: nur parsebare, nicht rohduplizierte Dateien mit begrenzter Dateigroesse und begrenzter geschaetzter Textlaenge. Damit bleibt Enron als legitime Unternehmenskommunikation vertreten, ohne die kuratierten Phishing- und SpamAssassin-Daten methodisch zu ueberdecken.

## Finale Anzahl je Source/Subtype

| source | subtype | ausgewaehlt | leere Texte entfernt | Duplikate entfernt | final |
|---|---:|---:|---:|---:|---:|
| enron | enron | 7500 | 0 | 159 | 7341 |
| phishing_curated | nazario | 1565 | 0 | 13 | 1552 |
| phishing_curated | nigerian_fraud | 3332 | 0 | 41 | 3291 |
| spamassassin | easy_ham | 2551 | 0 | 143 | 2408 |
| spamassassin | hard_ham | 250 | 0 | 21 | 229 |
| spamassassin | spam | 501 | 0 | 30 | 471 |
| spamassassin | spam_2 | 1398 | 0 | 69 | 1329 |

## Finale Anzahl je Label

- Label `0`: 9978
- Label `1`: 6643

## Beispielzeilen

### enron/enron
- `enron_enron_0000001` label=0 raw=`data/raw/enron/maildir/allen-p/_sent_mail/122` subject="Gas Physical/Financial Position" text="Gas Physical/Financial Position ---------------------- Forwarded by Phillip K Allen/HOU/ECT on 09/26/2000 12:07 PM --------------------------- From: Cindy Cicch"
- `enron_enron_0000002` label=0 raw=`data/raw/enron/maildir/allen-p/_sent_mail/168` subject="" text="Mark, The following is a guest password that will allow you temporary view only access to EnronOnline. Please note, the user ID and password are CASE SENSITIVE."
- `enron_enron_0000003` label=0 raw=`data/raw/enron/maildir/allen-p/_sent_mail/187` subject="Re:" text="Re: Cooper, This is the website I use: http://ectpdx-sunone/~ctatham/navsetup/index.htm Should I use a different address."

### phishing_curated/nazario
- `phishing_curated_nazario_0000001` label=1 raw=`data/raw/phishing_curated/Nazario.csv#row=2` subject="DON'T DELETE THIS MESSAGE -- FOLDER INTERNAL DATA" text="DON'T DELETE THIS MESSAGE -- FOLDER INTERNAL DATA This text is part of the internal format of your mail folder, and is not a real message. It is created automat"
- `phishing_curated_nazario_0000002` label=1 raw=`data/raw/phishing_curated/Nazario.csv#row=3` subject="Verify Your Account" text="Verify Your Account Business with cPanel & WHM Dear client, Our Technical Services Department are carrying out a planned software upgrade. Please login to re-co"
- `phishing_curated_nazario_0000003` label=1 raw=`data/raw/phishing_curated/Nazario.csv#row=4` subject="Helpdesk Mailbox Alert!!!" text="Helpdesk Mailbox Alert!!! Your two incoming mails were placed on pending status due to the recent upgrade in our database, In order to receive the messages kind"

### phishing_curated/nigerian_fraud
- `phishing_curated_nigerian_fraud_0000001` label=1 raw=`data/raw/phishing_curated/Nigerian_Fraud.csv#row=2` subject="URGENT BUSINESS ASSISTANCE AND PARTNERSHIP" text="URGENT BUSINESS ASSISTANCE AND PARTNERSHIP FROM:MR. JAMES NGOLA. CONFIDENTIAL TEL: 233-27-587908. E-MAIL: (james_ngola2002@maktoob.com). URGENT BUSINESS ASSISTA"
- `phishing_curated_nigerian_fraud_0000002` label=1 raw=`data/raw/phishing_curated/Nigerian_Fraud.csv#row=3` subject="URGENT ASSISTANCE /RELATIONSHIP (P)" text="URGENT ASSISTANCE /RELATIONSHIP (P) Dear Friend, I am Mr. Ben Suleman a custom officer and work as Assistant controller of the Customs and Excise department Of "
- `phishing_curated_nigerian_fraud_0000003` label=1 raw=`data/raw/phishing_curated/Nigerian_Fraud.csv#row=4` subject="GOOD DAY TO YOU" text="GOOD DAY TO YOU FROM HIS ROYAL MAJESTY (HRM) CROWN RULER OF ELEME KINGDOM CHIEF DANIEL ELEME, PHD, EZE 1 OF ELEME.E-MAIL ADDRESS:obong_715@epatra.com ATTENTION:"

### spamassassin/easy_ham
- `spamassassin_easy_ham_0000001` label=0 raw=`data/raw/spamassassin/easy_ham/0001.ea7e79d3153e7469e7a9c3e0af6a357e` subject="Re: New Sequences Window" text="Re: New Sequences Window Date: Wed, 21 Aug 2002 10:54:46 -0500 From: Chris Garrigues Message-ID: | I can't reproduce this error. For me it is very repeatable..."
- `spamassassin_easy_ham_0000002` label=0 raw=`data/raw/spamassassin/easy_ham/0002.b3120c4bcbf3101e661161ee7efcb8bf` subject="[zzzzteana] RE: Alexander" text="[zzzzteana] RE: Alexander Martin A posted: Tassos Papadopoulos, the Greek sculptor behind the plan, judged that the limestone of Mount Kerdylio, 70 miles east o"
- `spamassassin_easy_ham_0000003` label=0 raw=`data/raw/spamassassin/easy_ham/0003.acfc5ad94bbd27118a0d8685d18c89dd` subject="[zzzzteana] Moscow bomber" text="[zzzzteana] Moscow bomber Man Threatens Explosion In Moscow Thursday August 22, 2002 1:40 PM MOSCOW (AP) - Security officers on Thursday seized an unidentified "

### spamassassin/hard_ham
- `spamassassin_hard_ham_0000001` label=0 raw=`data/raw/spamassassin/hard_ham/0001.f0cf04027e74802f09f723cb8916b48e` subject="CNET NEWS.COM: Cable companies cracking down on Wi-Fi" text="CNET NEWS.COM: Cable companies cracking down on Wi-Fi Cable companies cracking down on Wi-Fi Search News.com All CNET The Web Live tech help NOW! April's tech a"
- `spamassassin_hard_ham_0000002` label=0 raw=`data/raw/spamassassin/hard_ham/0002.2fe846db6e3249836abdbfcae459bf2a` subject="Save an extra $50 on the iPaq 3835 PDA (CNET SHOPPER)" text="Save an extra $50 on the iPaq 3835 PDA (CNET SHOPPER) Shopper Newsletter: Alerts Live tech help NOW! April's tech award 1 million open jobs News.com: Top CIOs Z"
- `spamassassin_hard_ham_0000003` label=0 raw=`data/raw/spamassassin/hard_ham/0003.0aa92b5f121c27c6e094fd89c6c89448` subject="This week: Deck, Tex-Edit Plus, Boom" text="This week: Deck, Tex-Edit Plus, Boom CNET | DOWNLOAD DISPATCH(Mac Edition) July 9, 2002 Vol. 7, No. 27 Using a Mac and today's music software, musicians are fin"

### spamassassin/spam
- `spamassassin_spam_0000001` label=1 raw=`data/raw/spamassassin/spam/0000.7b1b73cf36cf9dbc3d64e3f2ee2b91f1` subject="" text="mv 1 00001.bfc8d64d12b325ff385cca8d07b84288 mv 10 00010.7f5fb525755c45eb78efc18d7c9ea5aa mv 100 00100.c60d1c697136b07c947fa180ba3e0441 mv 101 00101.2dfd7ee79ae4"
- `spamassassin_spam_0000002` label=1 raw=`data/raw/spamassassin/spam/0001.bfc8d64d12b325ff385cca8d07b84288` subject="Life Insurance - Why Pay More?" text="Life Insurance - Why Pay More? Save up to 70% on Life Insurance. Why Spend More Than You Have To? Life Quote Savings Ensuring your family's financial security i"
- `spamassassin_spam_0000003` label=1 raw=`data/raw/spamassassin/spam/0002.24b47bb3ce90708ae29d0aec1da08610` subject="[ILUG] Guaranteed to lose 10-12 lbs in 30 days 10.206" text="[ILUG] Guaranteed to lose 10-12 lbs in 30 days 10.206 1) Fight The Risk of Cancer! http://www.adclick.ws/p.cfm?o=315&s=pk007 2) Slim Down - Guaranteed to lose 1"

### spamassassin/spam_2
- `spamassassin_spam_2_0000001` label=1 raw=`data/raw/spamassassin/spam_2/00001.317e78fa8ee2f54cd4890fdc09ba8176` subject="[ILUG] STOP THE MLM INSANITY" text="[ILUG] STOP THE MLM INSANITY Greetings! You are receiving this letter because you have expressed an interest in receiving information about online business oppo"
- `spamassassin_spam_2_0000002` label=1 raw=`data/raw/spamassassin/spam_2/00002.9438920e9a55591b18e60d1ed37d992b` subject="Real Protection, Stun Guns! Free Shipping! Time:2:01:35 PM" text="Real Protection, Stun Guns! Free Shipping! Time:2:01:35 PM The Need For Safety Is Real In 2002, You Might Only Get One Chance - Be Ready! Free Shipping & Handli"
- `spamassassin_spam_2_0000003` label=1 raw=`data/raw/spamassassin/spam_2/00003.590eff932f8704d8b0fcbe69d023b54d` subject="New Improved Fat Burners, Now With TV Fat Absorbers! Time:6:25:49 PM" text="New Improved Fat Burners, Now With TV Fat Absorbers! Time:6:25:49 PM *****Bonus Fat Absorbers As Seen On TV, Included Free With Purchase Of 2 Or More Bottle, $2"

## Bekannte Limitationen

- Enron ist keine kuratierte Anti-Phishing-Negativklasse, sondern reale Unternehmenskommunikation.
- SpamAssassin-Spam wird gemaess Projektdefinition als label=1 gefuehrt, ist aber nicht deckungsgleich mit Phishing.
- Die Enron-Stichprobe reduziert Klassendominanz, ersetzt aber keine spaetere experimentelle Validierung.
- Duplikate werden anhand normalisierten Texts entfernt; semantisch gleiche, aber leicht veraenderte Mails koennen erhalten bleiben.

## Warnungen

- Keine Warnungen.
