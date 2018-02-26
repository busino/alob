�ber das Programm
=================

Das Programm dient der Analyse von Punktmustern zur Wiedererkennung von Individuen der Geburtshelferkr�te. 
Typische Anwendungsbereichen des Programms sind Monitoring und Erfolgskontrolle,
wenn mit Fang-Wiederfang Bestandesgr�ssen oder die Raumnutzung der Tiere bestimmt werden sollen.

Die automatisierte Vergleichsmethode basiert auf der Idee, dass die Positionen auff�lliger 
Punkte auf dem K�rper der Tiere als Koordinaten direkt im Programm erfasst werden.
F�r jeden Paarvergleich der �Koordinaten-Muster� zweier Tiere wird eine Art �hnlichkeitsindex berechnet.
Je h�her der Index, desto eher liegt ein Wiederfang desselben Tiers vor.
Der Entscheid, ob es wirklich ein Wiederfang ist, wird von Auge gef�llt. 
Der Computer hilft mit, die F�lle mit gr�sster Wahrscheinlichkeit auszusortieren und verringert damit die Arbeitszeit. 

Das Programm wird auf einem Server installiert und kann �ber einen Browser ge�ffnet werden.
Dadurch kann es von verschiedenen Nutzern gemeinsam verwendet werden.
Im Programm implementiert ist eine Datenbank, welche Daten wie Fotos, Koordinaten der Warzen etc. enth�lt.
Das Programm ist gratis zug�nglich und dank ungesch�tztem Quellcode auch durch Dritte erweiterbar (open source). 


Installieren des Programms
==========================

.. raw:: html
    
    <p>
    <a href="./deploy">Deploy</a> f�r die Installation eines Alob Server.<br>
    <a href="./devel">Devel</a> f�r ein Setup zur Erweiterung und Test von Alob.
    </p>

Qualit�tsanforderungen Fotos
----------------------------

Das Programm funktioniert bereits mit unbearbeiteten Fotos. 
Minimale Voraussetzung f�r die Anwendung sind Fotos mit demselben Ausschnitt, auf welchen die Punktmuster erkennbar sind.
Die Trefferquote, dass ein zweites Foto als �bereinstimmendes Tier erkannt wird,
steigt jedoch mit der Qualit�t der Feldfotos.
**Wir empfehlen deshalb beim Fotografieren das Benutzen einer hellen Unterlage als Hintergrund, 
eine starke, gleichm�ssige Beleuchtung und ein Stativ f�r die Kamera, damit stets derselbe Ausschnitt aus demselben Winkel aufgenommen wird.**
Die Aufl�sung der Fotos sollte in etwa 1000x1000 Pixel betragen.



Import Fotos
------------

Fotos k�nnen im Register *Image* �ber die Rubriken *Create* und *Import* in das Programm eingelesen werden:

Create: zum Einlesen von einzelnen Fotos. Dabei k�nnen zu jedem Foto Informationen hinzugef�gt werden (s. Bearbeitung Fotos).

Import: Ordner: zum Einlesen von ganzen Fotoordnern. Die Informationen zu den Fotos k�nnen optional in einer Tabelle im Format .csv oder .xlsx hochgeladen werden.


Fotos aufrufen
--------------

Jedes importierte Foto kann direkt mit dem Klick auf die ID-Nummer aufgerufen werden. Dabei werden die hinterlegten Informationen und das importierte Originalfoto angezeigt. Falls die Warzenmuster bereits digitalisiert wurden wird auch das bearbeitete Foto mit einer Tabelle und Grafik der Warzenmuster angef�gt.


Datenmanagement
---------------

Unter dem Register *Image* k�nnen Fotos in verschiedene *Pools* gruppiert und abgespeichert werden.
Dadurch k�nnen z.B. einzelne Fangdaten oder Untersuchungsgebiete separat oder direkt miteinander verglichen werden.
Mit Anklicken des Feldes *Create Pool* oder direkt beim Anw�hlen der Rubrik *Create Pool* wird ein Fenster ge�ffnet,
wo die Fotos ausgew�hlt und als Fotoordner abgespeichert werden k�nnen.

In der Rubrik *Pools* werden die einzelnen Fotoordner dargestellt. Beim Klick auf die ID fasst das Programm die wichtigsten Informationen zusammen wie Anzahl enthaltener Fotos, allf�lliger doppelter Fotos oder Matches. Die Matches und Fotos werden unten aufgelistet und k�nnen direkt aufgerufen und bearbeitet werden.


Bearbeitung Fotos
-----------------
Jedes importierte Foto kann direkt beim Import oder beim Klick auf die ID-Nummer bearbeitet werden.

Folgende M�glichkeiten bestehen:

- Edit: Informationen zum Foto anf�gen wie Datum, Untersuchungsgebiet/Fangort, Alter, Eier vorhanden, Bearbeiter, Fotoqualit�t (Foto kann bei schlechter Qualit�t mit Anklicken des Feldes Disabled aus der Analyse genommen werden), allgemeine Bemerkungen.
- Label: Digitalisieren der Warzenmuster (s. unten)
- Rotate: Drehen des Fotos. **Wir empfehlen die Fotos jeweils in derselben Rotation zu analysieren, z.B. Nase links bzw. Schwanz rechts.**


Digitalisieren der Warzenmuster
-------------------------------

Die Warzenmuster der Fotos k�nnen �ber das Feld *Label* digitalisiert werden (via ID-Nummer des Fotos).
Es empfiehlt sich die Warzenpunkte mit Hilfe einer Maus zu setzen und nicht mit einem Trackpad.

Punkte setzen:
``````````````

*Neuer Punkt*:
    Doppelklick
*Punkt bearbeiten*:
    Punkt anw�hlen > verschieben > Klicken
*Punkt l�schen*:
    Punkt anw�hlen > Eingabetaste Delete dr�cken

Dabei ist die Reihenfolge der Punkte wichtig, welche bearbeitet werden:

1. Punkt wird beim linken Auge gesetzt (violetter Punkt)

2. Punkt wird bei der Nase gesetzt (blauer Punkt)

3. Punkt wird beim rechten Auge gesetzt (violetter Punkt)

4. Punkt wird beim Schwanz gesetzt (blauer Punkt; falls dieser durch Eier �berdeckt ist muss eine Annahme getroffen werden)

5. F�r alle charakteristischen Warzenmuster wird ein Punkt gesetzt (gelbe Punkte).


Die Koordinaten der gesetzten Punkte werden rechts in einer Tabelle zusammengefasst.

Am Schluss wird die Digitalisierung mit *Save* beendet.

Die Koordinatenpunkte k�nnen jederzeit bearbeitet oder gel�scht werden.


Berechnen der Paarvergleiche
----------------------------

Im Register *Prediction* werden in der Rubrik *Create* diejenigen Fotos ausgew�hlt und als Ordner abgespeichert, f�r welche ein Paarvergleich berechnet werden soll. 
Unter *Start* wird die Analyse des Paarvergleichs durchgef�hrt. Die Resultate k�nnen anschliessend im Register *List* aufgerufen werden.

Unter dem Titel *Matches* fasst das Programm die Resultate der Paarvergleiche innerhalb des jeweiligen Ordners zusammen: true positive =TP, false positive = FP, true negative = TN, false negative = FN. 
- Die FP-Werte sollten von Hand noch einmal �berpr�ft werden.
- Der Paarvergleich funktioniert gut, wenn die FN-Werte klein sind. Dazu werden die Matches unten gerade aufgelistet und k�nnen direkt bearbeitet werden.

Im Register *Pair* werden alle Paarvergleiche in Form einer Tabelle dargestellt, welche das Programm durchgef�hrt hat (unabh�ngig der Ordner).
Jede Zeile stellt ein Vergleich von Koordinatenmuster zweier Fotos dar. Geordnet wird die Tabelle nach dem vorhandensein eines *Matches*.

In den Spalten werden die Fotonamen und Anzahl Punktkoordinaten pro Foto aufgef�hrt.
In der Spalte *Result* wird der �hnlichkeitsindex dargestellt.


Berechnung der �bereinstimmung
------------------------------

Die Warzenmuster werden von Hand digitalisiert und als Punktkoordinaten abgespeichert. Dabei entsteht f�r jedes Foto eine Punktwolke, welche mit einer Punktwolke eines zweiten Fotos �bereinandergelegt werden kann. Um jeden Punkt der Referenzpunktwolke wird nun mit einem definierten Suchradius nach Nachbarpunkten gesucht. Alle Punkte im Suchradius sind �bereinstimmungen. Die Summe der �bereinstimmungen wird durch die kleinere Anzahl der Punkte der Punktwolken dividiert und ergibt das �bereinstimmungsresultat:

::

    result = Anzahl �bereinstimmungen / min(Anzahl Punkte der Punktwolken)

Bei jedem Paarvergleich wird dieses �bereinstimmungsresultat im Feld Result dargestellt. Je h�her der Wert von Result, desto besser die �bereinstimmung bzw. desto h�her die Chance, dass es sich um identische Individuen handelt.


Identische Individuen finden
----------------------------

Paarvergleiche mit einem hohen Wert �bereinstimmungsresultat (hoher Wert von Result) m�ssen nun von Auge �berpr�ft werden.
Dabei k�nnen unter dem Register *Pair* alle Paarvergleiche aufgerufen werden oder unter Prediction nur diejenigen ausgew�hlter Ordner.
Zur Analyse kann f�r jeden Paarvergleich in der jeweiligen Spalte die dazugeh�rigen Fotos inkl. Warzenmuster angezeigt werden (Augensymbol hinter Fotoname).
Mit dem Klick auf die ID des Paarvergleichs k�nnen die Resultate auch detailliert dargestellt werden.

Mit den Feldern *match*, *no match* oder *undef* wird von Hand festgelegt, ob es sich um eine �bereinstimmung bzw. um dasselbe Individuum handelt.


Qualit�tskontrolle
------------------

F�r die Qualit�tskontrolle empfehlen wir zwei Vorgehen:

1.) Testfotos in die Analyse einbeziehen: Mit Vorteil sind dies unterschiedliche Fotos desselben Individuums. Alternativ kann auch ein Foto doppelt importiert und die Warzenmuster von einer Zweitperson erfasst werden. Der Paarvergleich funktioniert gut, wenn das Programm einen hohen �hnlichkeitsindex f�r die Testfotos berechnet.

2.) Im Register *Prediction* k�nnen f�r zu definierende Fotos Paarvergleiche berechnet und separat abgespeichert werden. Unter dem Titel Matches fasst das Programm die Resultate der Paarvergleiche zusammen: true positive =TP, false positive = FP, true negative = TN, false negative = FN. Der Paarvergleich funktioniert gut, wenn die FN-Werte klein sind. 


Export der Resultate
--------------------

Im Register *Image* k�nnen in der Rubrik Results zwei Tabellen im csv-Format exportiert werden: 

*Image results*: �bersicht der Fotos mit denselben Individuen bzw. Wiederf�nge

*Capture-Mark-Recapture*: Resultate formatiert f�r Fang-Wiederfang-Analysen

Die Resultate werden in Form einer Gesamttabelle exportiert, welche alle Paarvergleiche beinhaltet.
Der Export von Paarvergleichen ausgew�hlter Fotos bzw. Ordnern ist zur Zeit noch nicht m�glich.


Anwendung des Programms f�r weitere Arten
-----------------------------------------

F�r die Anwendung in Frage kommen theoretisch alle Tierarten, bei denen die Anordnung punktf�rmiger Merkmale individuell ausgepr�gt ist.
Dies trifft beispielweise auch f�r Kreuzkr�ten und Teichmolche zu. Die Tauglichkeit des Programms f�r diese Arten soll demn�chst getestet werden.
Nach Bedarf l�sst sich das Werkzeug in Zukunft auch f�r andere Mustertypen weiterentwickeln.


Dokumentation
-------------

Informationen zum Projekt, zur Programminstallation, zur Programmerweiterung und zur verwendeten Software befinden sich im Register Documentation.


Kontakt
-------

BARBARA SCHLUP,
HINTERMANN & WEBER AG, schlup@hintermannweber.ch

RAPHAEL WALKER,
SOFTWARE ENTWICKLER, raphael.walker@busino.ch