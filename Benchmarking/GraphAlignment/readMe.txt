Die unten stehenden Dateinamen enthalten die Ergebnisse des Benchmarkings. Das ist so zu verstehen:
* "benchmark_ga_"... steht für Benchmark GraphAlignment
* ..."_bk_"/"_mb_" zeigt in der Folge an, ob Bron-Kerbosch oder Cordella (matching-based) verwendet wurde
* ..."[Anzahl Knoten]_[Konnektivität].txt" steht am Schluss und zeigt welche Random-generierten Inputgraphen verwendet wurden (Größe und Konnektivität).
Die Inputgraphen sind alle auch im Ordner "Graphen" enthalten

Allgmein wurde das Graph Alignment immer auf drei Input Graphen gleicher Art ausgeführt. Die Anzahl der Aufrufe ist unterschiedlich und in der Folge spezifiziert.
Für Aufrufe, die entweder mit "killed" oder "Out of memory" abgebrochen wurden, sind keine Laufzeiten in der Datei hinterlegt:
benchmark_ga_bk_3_0.5.txt	: 90 Inputgraphen, 30 Aufrufe, 30/30 durchgelaufen
benchmark_ga_bk_4_0.5.txt	: 90 Inputgraphen, 30 Aufrufe, 30/30 durchgelaufen
benchmark_ga_bk_5_0.5.txt	: 90 Inputgraphen, 30 Aufrufe, 30/30 durchgelaufen
benchmark_ga_bk_6_0.5.txt	: 90 Inputgraphen, 30 Aufrufe, 27/30 durchgelaufen, 3/30 Killed, einer davon bei ~35 Minuten und knapp 7 GB Arbeitsspeicher
benchmark_ga_bk_7_0.5.txt	: 30 Inputgraphen, 10 Aufrufe, 7/10 durchgelaufen, 1/30 Killed, 1/30 Out of Memory

benchmark_ga_mb_3_0.5.txt	: 90 Inputgraphen, 30 Aufrufe, 30/30 durchgelaufen
benchmark_ga_mb_4_0.5.txt	: 90 Inputgraphen, 30 Aufrufe, 30/30 durchgelaufen
benchmark_ga_mb_5_0.5.txt	: 90 Inputgraphen, 30 Aufrufe, 30/30 durchgelaufen
benchmark_ga_mb_6_0.5.txt	: 90 Inputgraphen, 30 Aufrufe, 30/30 durchgelaufen
benchmark_ga_mb_7_0.5.txt	: 30 Inputgraphen, 10 Aufrufe, 10/10 durchgelaufen



