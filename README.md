# BestesRepository

Hey Folks,

we try to implement a software here... 

generic tool for progressive, multiple graph alignments

---

## branches
* master
* johann
* AJ
* chrissi

branches, wie wir noch brauchen: tille, def

---
## parameter 
python [graphalign.py](http://graphalign.py) [file] [Argument] 

### Arguments:
* -o [output-file] (outputfile)
* -mp [second graph file] (modulares produkt)
* -a [ankor file] (bron kerbosch mit anchor)
* -p max|random (gibt die art wie pivot gewählt werden soll an)
* -bk (bron kerbosch)
* -ga (muktiples graph alignment)

---

## Workflow GitHub
### Ausgangsituation: man befindet sich in seinem eigenen Branch und hat Dinge verändert 
* git add [veränderte Datei]
* git commit
* git push nicht nötig !!!
* git checkout dev
* git pull (gucken ob jemand anderes was verändert hat)
* git checkout [deinbranch]
* git merge dev (holte die Veränderung die jemand gemacht hat in sein branch, hier können Konflikte austreten)
* Bei Kontlikten: man geht in die Datei rein, die Konflikte enthält 
* dort sieht man dann mittels <<<<<<<<<<<< HEAD Zeichen und >>>>>> master Zeichen was du (HEAD) und was im master (master) verändert wurde
* nun passt man das Problem an und macht wieder git add, git commit (:wq in dem editor)
* nun: git push --set-upstram origin [deinbranch]

### wenn man nun i.wann zufrieden ist mit seinen Änderungen in seinem branch
* Worklflow idealerweise:
* man ist im GitHub in seinem branch und drückt auf "compare, review, create a pull request" (links einen kleiner grüner button)
* dann kommt man auf eine Seite wo man seine Änderungen sieht
* nun "Create Pull Request" drücken, sagen was man verändert hat (und z.b. @AJ kannst du das mal überprüfen) 
* nun ist jemand anders an der Reihe zu checken ob die Änderung so klar geht
* jemand kann nun "merge pull request" drücken  & "confirm merge" 
* nun ist die Änderung in dev
---
