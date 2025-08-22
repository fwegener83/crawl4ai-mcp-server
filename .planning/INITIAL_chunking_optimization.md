* Ein neues Modell wurde konfiguriert, da es in einem Python Notebook zu sehr guten Ergebnissen geführt hat insb. bei der Mischung von englischen Dokus und deutschen Fragen
  * Cross-Language Analysis:
  * Average cross-language similarity: 0.919
  * Model: distiluse-base-multilingual-cased-v1
  * Embedding dimensions: 512D

Diese guten Ergebnisse können leider nicht im Frontend nachvollzogen werden. Mit den selben Testqueries auf die gleiche Datenbasis kommt es zu deutlich schlechteren Ergebnissen insbesondere bei deutschen Fragen zur englsiche Doku (chubnks)

Hier einige Beispielfragen die an Claude Code Doku gerichtet wurden (hier aus dem Notebook notebooks/03_realistic_chunking_comparison.ipynb). Im Frontend führen die Fragen auf Deutsch zumeist zu keinen Ergebnissen (bzw. erst unter einem Threshold von 0.1).

=== Cross-Language Semantic Similarity Test ===

--- Query Pair 1 ---
German: Welche verschiedenen Arten von Speicher gibt es in Claude Code?
English: What are the different types of memory in Claude Code?
Cross-language similarity: 0.881
Best match for German: Chunk 0 (similarity: 0.595)
Best match for English: Chunk 0 (similarity: 0.581)
Same best chunk: True ✅

--- Query Pair 2 ---
German: Wie funktioniert die CLAUDE.md Datei?
English: How does the CLAUDE.md file work?
Cross-language similarity: 0.970
Best match for German: Chunk 3 (similarity: 0.454)
Best match for English: Chunk 3 (similarity: 0.469)
Same best chunk: True ✅

--- Query Pair 3 ---
German: Was sind die besten Praktiken für Projektkontext?
English: What are the best practices for project context?
Cross-language similarity: 0.910
Best match for German: Chunk 3 (similarity: 0.378)
Best match for English: Chunk 3 (similarity: 0.406)
Same best chunk: True ✅

--- Query Pair 4 ---
German: Welche Befehle kann ich verwenden um den Speicher zu verwalten?
English: What commands can I use to manage memory?
Cross-language similarity: 0.914
Best match for German: Chunk 0 (similarity: 0.393)
Best match for English: Chunk 2 (similarity: 0.436)
Same best chunk: False ❌

Anforderungen:

* Im Frontend sol nachvollzogen werden können, mit welcher Konfiguration chunks zu einer collection erzeugt (gesynct) wurden.
* Es soll möglich sein, aus dem Frontend heraus chunks zu einer Collection zu löschen und komplett neu syncen zu lassen (bisher geht das nur über die Api, bzw. der klick auf den sync button führt nur dazu dass geänderte Dateien neu gesynct werden)
* Die Funktionalitätebn sollen vernünftig in das Frontend und die UX eingebunden werden
* Wird eine Collection im Fronend gelöscht, sollen auch sämtliche Files die zu der Collection gehören wie auch sämtliche gesyncten Chunks in der Vektordatenbank entfernt werden. Aktuell bleiben diese Dinge bestehen. Das soll automatisch beim löschen einer Collection passieren. Das ganze soll im Backend abgewickelt werden, sodass über den API call angestoßen wird um eine Colelction zu löschen (API call DELETE collection -> alle files der collection löschen -> alle gesyncten chunks löschen)
* Das aktive Modell soll im Frontend visualisiert werden (sowohl für das chunking als auch für die query transformation). Beides soll sinnvoll in die UX eingebunden werden
* Der root cause soll ermittelt werden, warum so schlechte Ergebnisse geliefert werden obwohl das Modell scheinbar geladen wird (Vermutung: Im Hintegrund wird dennoch das alte Modell geladen all-MiniLM-L6-v2 - die Suche danach war recht schwierig. idee: alte modell entfernen und dann gucken ob alles funktioniert, um ein Verwenden auszuschließen und falls sonst nichts klappt)
* Der root cause soll beseitigt werden sodass das neue, aktuell in der .env definierte Modell verwendet wird 