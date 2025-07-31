# UI-Richtlinien für MUI-basierte Komponentenentwicklung

## Ziel

Ziel ist die Entwicklung eines konsistenten, wartbaren und wiederverwendbaren UI-Systems. Die Regeln orientieren sich an bewährten Mustern wie Atomic Design, konsequenter Typisierung und zentralem Theming. Basis soll dabei React und Vite sein wie bisher. Außerdem soll Material UI (MUI) in allen bereichen etabliert werden.

## 1. Absicherung durch Tests

- Vor Umbau oder Einführung neuer Komponenten sicherstellen, dass relevante Unit- und Integrationstests vorhanden sind.
- Prüfen, ob Testabdeckung für bestehende UI-Komponenten ausreichend ist, insbesondere für kritische Pfade.

## 2. Verwende ausschließlich MUI

- Nutze für UI-Elemente ausschließlich Komponenten aus MUI (z. B. `Button`, `Dialog`, `TextField`, `Icon`).
- Keine Mischverwendung mit anderen UI-Bibliotheken.
- Keine Inline-Styles oder individuelle CSS-Dateien für Layout und Farbgebung, sondern Theme-Mechanismen von MUI nutzen.

## 3. Komponentenhierarchie (Atomic Design)

- **Atoms**: Direkt verwendete MUI-Komponenten.
- **Molecules**: Kapselung mehrerer MUI-Komponenten zu funktionalen Einheiten (z. B. `LabeledInput`, `ConfirmDialog`).
- **Organisms**: Feature-spezifische Komponenten, die Molecules kombinieren (z. B. `OrderEditorDialog`).

## 4. Projektstruktur

```
/src
  /components
    /ui         // eigene UI-Komponenten auf MUI-Basis
    /modals     // spezialisierte Dialoge
    /icons      // Icon-Komponenten
  /features
    /featureA
    /featureB
  /theme
  /utils
```

## 5. Theming

- Definiere ein zentrales MUI-Theme (`theme.ts`).
- Verwende Theme-Werte für Farben, Abstände, Schriften etc.
- Keine festen Farbwerte, Abmessungen oder Schriftdefinitionen verwenden.

## 6. Icon-Nutzung

- Verwende ausschließlich Icons aus `@mui/icons-material`.
- Erstelle eine zentrale Icon-Komponente, um Darstellung zu vereinheitlichen.
- Gleiche semantische Funktion → gleiches Icon (z. B. für "Schließen" nur `CloseIcon`).

## 7. Dialog-Komponenten

- Implementiere wiederverwendbare Wrapper-Komponenten für Dialoge mit einheitlichem Verhalten (z. B. Esc schließen, Button-Ausrichtung).
- Direkte Verwendung von `Dialog` vermeiden.

## 8. Formularelemente

- Kapsle häufige Kombinationen (Label + Input + Fehlermeldung).
- Setze Validierung mit `react-hook-form` und `zod` oder `yup` um.
- Kein direktes Styling innerhalb von Formularen, sondern Wiederverwendung von Molecules.

## 9. Typisierung

- Verwende konsequent eigene Typdefinitionen für Props.
- Nutze Generics für datengetriebene Komponenten (z. B. Tabellen, Listen).
- Keine untypisierten Props oder `any`.


## 10. UI-Guideline-Dokumentation

- Definiere:
  - Welche UI-Komponenten existieren
  - Wie Dialoge zu verwenden sind
  - Welche Icons für welche semantische Funktion stehen
  - Wie Theme-Werte zu nutzen sind
  - Vorgehensweise bei neuen Komponentenanforderungen
  - Verweise in der claude.md auf die guidlines, sodass sie bei neuen Feature berücksichtigt werden

---

## Zusammenfassung

| Ziel                 | Maßnahme                                               |
| -------------------- | ------------------------------------------------------ |
| Konsistenz           | Ausschließlich MUI, zentrale Komponenten verwenden     |
| Wiederverwendbarkeit | Komponentenhierarchie und Kapselung nach Atomic Design |
| Wartbarkeit          | Projektstruktur, Theming, Typisierung                  |
| Erweiterbarkeit      | Wrapper-Komponenten, zentrales Theme, zentrale Icons   |
| Skalierbarkeit       | Storybook, dokumentierte Komponentenstrategie          |

