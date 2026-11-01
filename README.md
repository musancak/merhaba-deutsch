# Merhaba Deutsch

**[musancak.github.io/merhaba-deutsch](https://musancak.github.io/merhaba-deutsch/)**

Eine Lern-App für Menschen, die neu aus der Türkei nach Deutschland kommen: die wichtigsten Sätze für Alltag, Amt, Arzt, Arbeit und Wohnung – auf Türkisch erklärt und mit Aussprachehilfe in türkischer Schreibweise.

## Funktionen

- **14 Themen, 217 Sätze und Wörter**, Artikel farbig markiert (der · die · das)
- **Natürliche Sprachaufnahmen** für jeden Eintrag, auch langsam abspielbar
- **Selbst nachsprechen:** eigene Aufnahme direkt mit dem Original vergleichen
- **Übungen** in drei Formen, richtige Antworten kommen nach 1, 3, 7, 14 und 30 Tagen wieder
- **Offline** und als App auf dem Home-Bildschirm nutzbar

## Technik

- `inhalt.json` enthält alle Inhalte; `bauen.py` erzeugt daraus eine einzige HTML-Datei mit eingebetteten Aufnahmen
- `ton.py` erzeugt die Aufnahmen lokal mit [Piper](https://github.com/rhasspy/piper) (Stimme „Thorsten“), erstellt je Satz drei Varianten und lässt [Whisper](https://github.com/openai/whisper) die verständlichste auswählen
- Fortschritt bleibt auf dem Gerät (localStorage), kein Server nötig
