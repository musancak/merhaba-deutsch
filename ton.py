# Erzeugt für jeden deutschen Eintrag eine Aufnahme (Piper Thorsten high) als m4a in ton/.
# Piper klingt bei jedem Durchlauf etwas anders – deshalb werden mehrere Varianten erzeugt,
# von Whisper abgehört und die verständlichste behalten. Vorhandene Dateien werden übersprungen.
# Aufruf mit venv-server von Cockpit-stimme.
import difflib, hashlib, json, os, re, subprocess, tempfile, wave
import numpy as np, mlx_whisper
from piper import PiperVoice, SynthesisConfig

HIER = os.path.dirname(os.path.abspath(__file__))
MODELL = os.path.expanduser("~/projects/Cockpit-stimme/modelle/piper/de_DE-thorsten-high.onnx")
WHISPER = "mlx-community/whisper-large-v3-turbo"
VARIANTEN = 3
CFG = SynthesisConfig(length_scale=1.12, noise_scale=0.5, noise_w_scale=0.7)
# Einzelwörter kommen sonst in ~0,4 s – zu schnell zum Nachsprechen
CFG_KURZ = SynthesisConfig(length_scale=1.25, noise_scale=0.5, noise_w_scale=0.7)
STILLE_VORN, STILLE_HINTEN = 0.15, 0.3  # Sekunden; Handys/Bluetooth verschlucken sonst den Anfang

def schluessel(text):
    return hashlib.sha1(text.encode()).hexdigest()[:10]

def sprechtext(eintrag):
    return eintrag[3] if len(eintrag) > 3 else eintrag[0]

def normal(s, zahlen):
    s = re.sub(r"\d+", lambda m: zahlen.get(m.group(), m.group()), s.lower())
    return re.sub(r"[^a-zäöüß ]", "", s.replace("-", " ")).replace(" ", "")

def erzeugen(stimme, text, pfad):
    cfg = CFG_KURZ if len(text.split()) <= 2 else CFG
    with wave.open(pfad, "wb") as w:
        stimme.synthesize_wav(text, w, syn_config=cfg)
    with wave.open(pfad, "rb") as w:
        p, frames = w.getparams(), w.readframes(w.getnframes())
    null = lambda s: b"\0" * (int(p.framerate * s) * p.sampwidth)
    with wave.open(pfad, "wb") as w:
        w.setparams(p)
        w.writeframes(null(STILLE_VORN) + frames + null(STILLE_HINTEN))
    return p.framerate, np.frombuffer(frames, np.int16)

def hoeren(rate, pcm):
    a = pcm.astype(np.float32) / 32768
    a = np.interp(np.arange(0, len(a), rate / 16000), np.arange(len(a)), a).astype(np.float32)
    a = np.concatenate([np.zeros(8000, np.float32), a, np.zeros(16000, np.float32)])
    return mlx_whisper.transcribe(a, path_or_hf_repo=WHISPER, language="de")["text"].strip()

def main():
    inhalt = json.load(open(os.path.join(HIER, "inhalt.json")))
    zahlen = {"25": "fünfundzwanzig", "5": "fünf"}
    texte = {}
    for thema in inhalt:
        for e in thema["items"]:
            texte[schluessel(e[0])] = sprechtext(e)
            if thema["id"] == "sayilar":
                zahlen[e[1]] = e[0]
    os.makedirs(os.path.join(HIER, "ton"), exist_ok=True)
    stimme, neu, unsicher = None, 0, []
    for k, t in texte.items():
        ziel = os.path.join(HIER, "ton", k + ".m4a")
        if os.path.exists(ziel):
            continue
        stimme = stimme or PiperVoice.load(MODELL)
        with tempfile.TemporaryDirectory() as tmp:
            beste = (-1, None, "")
            for v in range(VARIANTEN):
                pfad = os.path.join(tmp, f"{v}.wav")
                gehoert = hoeren(*erzeugen(stimme, t, pfad))
                wert = difflib.SequenceMatcher(None, normal(t, zahlen), normal(gehoert, zahlen)).ratio()
                if wert > beste[0]:
                    beste = (wert, pfad, gehoert)
                if wert == 1:
                    break
            subprocess.run(["afconvert", beste[1], ziel, "-f", "m4af", "-d", "aac", "-b", "48000"], check=True)
        neu += 1
        if beste[0] < 1:
            unsicher.append(f"{beste[0]:.2f}  {t}  →  {beste[2]}")
        print(neu, f"{beste[0]:.2f}", t, flush=True)
    print("fertig:", len(texte), "Aufnahmen,", neu, "neu")
    if unsicher:
        print("Whisper hörte nicht genau den Text (bei Einzelwörtern oft Whisper-Schwäche):")
        print("\n".join(unsicher))

if __name__ == "__main__":
    main()
