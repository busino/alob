Über das Programm
=================

Das Programm dient der Analyse von Punktmustern zur Wiedererkennung von Individuen der Geburtshelferkröte. 
Typische Anwendungsbereichen des Programms sind Monitoring und Erfolgskontrolle,
wenn mit Fang-Wiederfang Bestandesgrössen oder die Raumnutzung der Tiere bestimmt werden sollen.

Die automatisierte Vergleichsmethode basiert auf der Idee, dass die Positionen auffälliger 
Punkte auf dem Körper der Tiere als Koordinaten direkt im Programm erfasst werden.
Für jeden Paarvergleich der «Koordinaten-Muster» zweier Tiere wird eine Art Ähnlichkeitsindex berechnet.
Je höher der Index, desto eher liegt ein Wiederfang desselben Tiers vor.
Der Entscheid, ob es wirklich ein Wiederfang ist, wird von Auge gefällt. 
Der Computer hilft mit, die Fälle mit grösster Wahrscheinlichkeit auszusortieren und verringert damit die Arbeitszeit. 

Das Programm wird auf einem Server installiert und kann über einen Browser geöffnet werden.
Dadurch kann es von verschiedenen Nutzern gemeinsam verwendet werden.
Im Programm implementiert ist eine Datenbank, welche Daten wie Fotos, Koordinaten der Warzen etc. enthält.
Das Programm ist gratis zugänglich und dank ungeschütztem Quellcode auch durch Dritte erweiterbar (open source). 


Installieren des Programms
==========================
Das Programm ist gratis zugänglich und dank ungeschütztem Quellcode auch durch Dritte erweiterbar (open source).
Es wird auf einem Server installiert und ist plattformunabhängig. 
Die Installation erfordert vertiefte Informatikkenntnisse und deshalb nach Bedarf die Unterstützung eines Informatik-Spezialisten (Aufwand ca. 1-2 h).
Mehr Informationen finden sich hier:

.. raw:: html
    
    <p>
    <a href="./deploy">Deploy</a> für die Installation eines Alob Server.<br>
    <a href="./devel">Devel</a> für ein Setup zur Erweiterung und Test von Alob.
    </p>

Qualitätsanforderungen Fotos
----------------------------

Das Programm funktioniert bereits mit unbearbeiteten Fotos. 
Minimale Voraussetzung für die Anwendung sind Fotos mit demselben Ausschnitt, auf welchen die Punktmuster erkennbar sind.
Die Trefferquote, dass ein zweites Foto als übereinstimmendes Tier erkannt wird,
steigt jedoch mit der Qualität der Feldfotos.
**Wir empfehlen deshalb beim Fotografieren das Benutzen einer hellen Unterlage als Hintergrund, 
eine starke, gleichmässige Beleuchtung und ein Stativ für die Kamera, damit stets derselbe Ausschnitt aus demselben Winkel aufgenommen wird.**
Bewährt hat sich eine Auflösung der Fotos von ca. 1000x1000 Pixel.



Import Fotos
------------

Fotos können im Register *Image* über die Rubriken *Create* und *Import* in das Programm eingelesen werden:

Create: zum Einlesen von einzelnen Fotos. Dabei können zu jedem Foto Informationen hinzugefügt werden (s. Bearbeitung Fotos).

Import: zum Einlesen von ganzen Fotoordnern. Die Informationen zu den Fotos können optional in einer Tabelle im Format .csv oder .xlsx hochgeladen werden.


Fotos aufrufen
--------------

Jedes importierte Foto kann direkt mit dem Klick auf die ID-Nummer aufgerufen werden.
Dabei werden die hinterlegten Informationen und das importierte Originalfoto angezeigt.
Falls die Warzenmuster bereits digitalisiert wurden wird auch das bearbeitete Foto mit einer Tabelle und Grafik der Warzenmuster angefügt.


Datenmanagement
---------------

Unter dem Register *Image* können Fotos in verschiedene *Pools* gruppiert und abgespeichert werden.
Dadurch können z.B. einzelne Fangdaten oder Untersuchungsgebiete separat oder direkt miteinander verglichen werden.
Mit Anklicken des Feldes *Create Pool* oder direkt beim Anwählen der Rubrik *Create Pool* wird ein Fenster geöffnet,
wo die Fotos ausgewählt und als Fotoordner abgespeichert werden können.

In der Rubrik *Pools* werden die einzelnen Fotoordner dargestellt.
Beim Klick auf die ID fasst das Programm die wichtigsten Informationen zusammen wie Anzahl enthaltener Fotos, allfälliger doppelter Fotos oder Matches.
Die Matches und Fotos werden unten aufgelistet und können direkt aufgerufen, bearbeitet und analysiert werden.


Bearbeitung Fotos
-----------------
Jedes importierte Foto kann direkt beim Import oder beim Klick auf die ID-Nummer bearbeitet werden.
Dadurch können die Vergleiche auf eine Untermengen der Fotos - z.B. einzelne Fangdaten oder Untersuchungsgebiete - beschränkt werden.
Das Anlegen von Fotoordnern ermöglicht auch verschiedene Projekte gleichzeitig zu bearbeiten.
 
Folgende Möglichkeiten bestehen:

- Edit: Informationen zum Foto anfügen wie Datum, Untersuchungsgebiet/Fangort, Alter, Eier vorhanden, Bearbeiter, Fotoqualität (Foto kann bei schlechter Qualität mit Anklicken des Feldes Disabled aus der Analyse genommen werden), allgemeine Bemerkungen.
- Label: Digitalisieren der Warzenmuster (s. unten)
- Rotate: Drehen des Fotos. **Wir empfehlen die Fotos jeweils in derselben Rotation zu analysieren, z.B. Nase links bzw. Schwanz rechts.**


Digitalisieren der Warzenmuster
-------------------------------

Die Warzenmuster der Fotos können über das Feld *Label* digitalisiert werden (via ID-Nummer des Fotos).
Es empfiehlt sich die Warzenpunkte mit Hilfe einer Maus zu setzen und nicht mit einem Trackpad.

Punkte setzen:
``````````````

*Neuer Punkt*:
    Doppelklick
*Punkt bearbeiten*:
    Punkt anwählen > verschieben > Klicken
*Punkt löschen*:
    Punkt anwählen > Eingabetaste Delete drücken

Dabei ist die Reihenfolge der Punkte wichtig, welche bearbeitet werden:

1. Punkt wird beim linken Auge gesetzt (violetter Punkt)

2. Punkt wird bei der Nase gesetzt (blauer Punkt)

3. Punkt wird beim rechten Auge gesetzt (violetter Punkt)

4. Punkt wird beim Schwanz gesetzt (blauer Punkt; falls dieser durch Eier überdeckt ist muss eine Annahme getroffen werden)

5. Für alle charakteristischen Warzenmuster wird ein Punkt gesetzt (gelbe Punkte).


Die Koordinaten der gesetzten Punkte werden rechts in einer Tabelle zusammengefasst.

Am Schluss wird die Digitalisierung mit *Save* beendet.

Die Koordinatenpunkte können jederzeit bearbeitet oder gelöscht werden.


Berechnen der Paarvergleiche
----------------------------

Im Register *Prediction* werden in der Rubrik *Create* diejenigen Fotos ausgewählt und als Ordner abgespeichert, für welche ein Paarvergleich berechnet werden soll. 
Unter *Start* wird die Analyse des Paarvergleichs durchgeführt. Die Resultate können anschliessend im Register *List* aufgerufen werden.

Unter dem Titel *Matches* fasst das Programm die Resultate der Paarvergleiche innerhalb des jeweiligen Ordners zusammen.
Für eine Erläuterung der Resultate siehe Abschnitt *„Analysieren der Paarvergleiche“*. 

Im Register *Pair* werden alle Paarvergleiche, welche das Programm je durchgeführt hat (unabhängig der Ordner), in Form einer Tabelle dargestellt.
Jede Zeile stellt ein Vergleich von Koordinatenmuster zweier Fotos dar. Geordnet wird die Tabelle nach dem Vorhandensein eines *Matches*.
In den Spalten werden die Fotonamen und Anzahl Punktkoordinaten pro Foto aufgeführt.
In der Spalte *Result* wird der Ähnlichkeitsindex dargestellt (siehe Abschnitt „Berechnung der Übereinstimmung“).

Berechnung der Übereinstimmung
------------------------------

Die Warzenmuster werden von Hand digitalisiert und als Punktkoordinaten abgespeichert.
Dabei entsteht für jedes Foto eine Punktwolke, welche mit einer Punktwolke eines zweiten Fotos übereinandergelegt werden kann. 
Um jeden Punkt der Referenzpunktwolke wird nun mit einem definierten Suchradius nach Nachbarpunkten gesucht.
Alle Punkte im Suchradius sind Übereinstimmungen. 
Die Summe der Übereinstimmungen wird durch die kleinere Anzahl der Punkte der Punktwolken dividiert und ergibt das Übereinstimmungsresultat.
Dieser Ähnlichkeitsindex berechnet sich wie folgt:

::

    result = Anzahl Übereinstimmungen / min(Anzahl Punkte der Punktwolken)

Bei jedem Paarvergleich wird der Ähnlichkeitsindex im Feld *Result* dargestellt.
Je höher der Wert von Result, desto besser die Übereinstimmung bzw. desto höher die Chance, dass es sich um identische Individuen handelt.


Identische Individuen finden
----------------------------

Paarvergleiche mit einem hohen Ähnlichkeitsindex (hoher Wert von *Result*) müssen nun von Auge überprüft werden.
Dabei können unter dem Register *Pair* alle Paarvergleiche aufgerufen werden oder unter *Prediction* nur diejenigen ausgewählter Ordner.
Zur Analyse kann für jeden Paarvergleich in der jeweiligen Spalte die dazugehörigen Fotos inkl. Warzenmuster angezeigt werden (Augensymbol hinter Fotoname).
Mit dem Klick auf die ID des Paarvergleichs können die Resultate auch detailliert dargestellt werden.

Mit den Feldern *match*, *no match* oder *undef* wird von Hand festgelegt, ob es sich um eine Übereinstimmung bzw. um dasselbe Individuum handelt.


Analysieren der Paarvergleiche
------------------------------

Im Register *Prediction* werden die Paarvergleiche von ausgewählten Fotos berechnet (s. oben).
Mit dem Klick auf die jeweilige Liste der berechneten Paarvergleiche können die Resultate genauer analysiert werden. 


Als Beispiel die Zusammenfassung der Resultate eines fiktiven Paarvergleiches mit 34 Fotos:

::

    #Images: 34
    Combinations: 561
    Num. Processes: 1
    Time approx:  5.61 s

Es werden 561 mögliche Kombinationen von Paarvergleichen berechnet. Die Berechnung dauert 5.6 Sekunden.
Im Programm ist eine machine-learning-Routine implementiert, welche basierend auf verschiedenen Berechnungen für jeden Paarvergleich entscheidet, ob eine Übereinstimmung vorliegt.
Diese Resultate werden immer genauer, je mehr Paarvergleiche von Hand analysiert bzw. als *Match* oder *no Match* bewertet werden. 
Die Resultate werden wie folgt dargestellt:

::

    TP: 2
    FP: 4
    TN: 282
    FN: 0

**TP (true positive)**: Es sind 2 Matches vorhanden, welche vom Programm als Übereinstimmung vorgeschlagen und bereits zu einem früheren Zeitpunkt vom Bearbeiter als Match bestätigt wurden. Hier können wir also sicher sein, dass die Fotos vom selben Individuum stammen.

**FP (false positive)**: Es sind 4 Matches vorhanden, welche vom Programm als Übereinstimmung vorgeschlagen werden. Der Bearbeiter hat diese Paarvergleiche (noch) nicht als Übereinstimmung bewertet. Die FP-Werte sollten deshalb von Hand auf eine Übereinstimmung überprüft werden, um sicher zu gehen, dass keine Matches übersehen wurden.

**TN (true negative)**: Es sind 282 Paarvergleiche vorhanden, welche sowohl vom Programm als auch vom Bearbeiter als keine Übereinstimmung bewertet wurden. Eine manuelle Überprüfung der Fotos lohnt sich hier nicht, sofern davon ausgegangen werden kann, dass die automatisierte Mustererkennung funktioniert (siehe FN-Werte).  

**FN (false negative)**: Hier werden diejenigen Paarvergleiche angezeigt, welche vom Programm als keine Übereinstimmung bewertet werden, der Bearbeiter zu einem früheren Zeitpunkt aber als Match bestätigt hat. Wenn die automatisierte Mustererkennung gut funktioniert, so sollten die FN-Werte möglichst klein sind (hier sogar 0). Der FN-Wert hilft deshalb als Kontrolle, ob das Programm für die spezifischen Fotos auch wirklich funktioniert.


Qualitätskontrolle
------------------

Für die Qualitätskontrolle empfehlen wir zwei Vorgehen:

1.) Testfotos in die Analyse einbeziehen: Mit Vorteil sind dies unterschiedliche Fotos desselben Individuums. Alternativ kann auch ein Foto doppelt importiert und die Warzenmuster von einer Zweitperson erfasst werden. Der Paarvergleich funktioniert gut, wenn das Programm einen hohen Ähnlichkeitsindex für die Testfotos berechnet.

2.) Im Register *Prediction* können für zu definierende Fotos Paarvergleiche berechnet und separat abgespeichert werden.
    Unter dem Titel Matches fasst das Programm die Resultate der Paarvergleiche zusammen: true positive = TP, false positive = FP, true negative = TN, false negative = FN.
    Wenn die automatisierte Mustererkennung gut funktioniert, so sollten die FN-Werte möglichst klein sind (dazu mehr im Abschnitt Analysieren der Paarvergleiche).


Export der Resultate
--------------------

Im Register *Image* können in der Rubrik Results zwei Tabellen im csv-Format exportiert werden: 

*Image results*: Übersicht der Fotos mit denselben Individuen bzw. Wiederfänge

*Capture-Mark-Recapture*: Resultate formatiert für Fang-Wiederfang-Analysen

Die Resultate werden in Form einer Gesamttabelle exportiert, welche alle Paarvergleiche beinhaltet.
Der Export von Paarvergleichen ausgewählter Fotos bzw. Ordnern ist zur Zeit noch nicht möglich.


Anwendung des Programms für weitere Arten
-----------------------------------------

Für die Anwendung in Frage kommen theoretisch alle Tierarten, bei denen die Anordnung punktförmiger Merkmale individuell ausgeprägt ist.
Dies trifft beispielweise auch für Kreuzkröten und Teichmolche zu. Die Tauglichkeit des Programms für diese Arten soll demnächst getestet werden.
Nach Bedarf lässt sich das Werkzeug in Zukunft auch für andere Mustertypen weiterentwickeln.


Dokumentation
-------------

Informationen zum Projekt, zur Programminstallation, zur Programmerweiterung und zur verwendeten Software befinden sich im Register Documentation.


Kontakt
-------

BARBARA SCHLUP,
HINTERMANN & WEBER AG, schlup@hintermannweber.ch

RAPHAEL WALKER,
SOFTWARE ENTWICKLER, raphael.walker@busino.ch