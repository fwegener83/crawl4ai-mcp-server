**Anforderungskonzept: Verbesserte Chunking-Strategie für RAG**

**Ziel**  
Optimierung der Antwortqualität eines Retrieval-Augmented-Generation-Systems (RAG) bei technischen Dokumentationen, insbesondere bei gecrawlten Markdown-Inhalten.

---

### 1. Verbesserungsmaßnahmen

**1.1 Chunk-Overlap beim Indexieren**  
- Einführung eines Overlaps von 20–30 % zwischen aufeinanderfolgenden Chunks.  
- Ziel: Verhindern, dass inhaltlich zusammenhängende Informationen an Chunk-Grenzen getrennt werden.  
- Besonders wirksam bei technischen Anleitungen und API-Dokumentationen.

**1.2 Dynamische Kontextvergrößerung nach Score**  
- Falls ein Suchtreffer nur knapp über dem Relevanzschwellenwert liegt, werden automatisch die vorherigen und/oder nachfolgenden Chunks mit einbezogen.  
- Dadurch werden Randtreffer kontextuell ergänzt und besser verständlich.

**1.3 Bestehendes Markdown-basiertes Chunking beibehalten, aber anreichern**  
- Struktur des Dokuments anhand von Überschriften und Code-Blöcken weiterhin als primäre Chunk-Grenzen nutzen.  
- Overlap und dynamische Kontextvergrößerung als zweite Ebene ergänzen.

---

### 2. Nachweisbare Verbesserung (A/B-Test)

**2.1 Testaufbau**
- Auswahl eines identischen technischen Dokuments als Testbasis.
- Indexierung in zwei Varianten:  
  **A**: Status quo (aktuelles Markdown-basiertes Chunking).  
  **B**: Verbesserte Methode (Overlap + dynamische Kontextvergrößerung).

**2.2 Testfragen**
- Gleicher Satz an repräsentativen Fragen pro Variante.
- Fragen decken verschiedene Tiefen ab (Fakten, Prozessabläufe, kombinierte Informationen).

**2.3 Bewertungskriterien**
- Vollständigkeit der Antwort.
- Korrektheit der Inhalte.
- Anzahl der erforderlichen Rückfragen.
- Subjektive Lesbarkeit.

**2.4 Auswertung**
- Jede Antwort wird mit einem Scoring-System (z. B. 1–5 pro Kriterium) bewertet.
- Vergleich der Durchschnittswerte zwischen Variante A und B.
- Dokumentation der Ergebnisse zur quantitativen Erfolgsmessung.

---

### 3. Erwartete Vorteile
- Höhere Antwortgenauigkeit durch Erhalt inhaltlicher Zusammenhänge.
- Weniger Fälle von abgeschnittenem Kontext.
- Bessere Nutzererfahrung bei komplexen, technischen Fragen.

---

**Fazit:**  
Die Kombination aus strukturerhaltendem Markdown-Chunken, gezieltem Overlap und dynamischer Kontextvergrößerung bietet einen messbaren Qualitätsgewinn. Der A/B-Test ermöglicht eine objektive Bewertung dieser Maßnahmen.

