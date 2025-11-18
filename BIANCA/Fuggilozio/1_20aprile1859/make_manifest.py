import json
from pathlib import Path

# ====== CONFIGURAZIONE ======
BASE_DIR = Path(__file__).resolve().parent
TILES_DIR = BASE_DIR / "iiif"

# Base URL delle sottocartelle iiif (come sono hostate su GitHub Pages)
BASE_URL = "https://ai4ch-uniud.github.io/DigitalImages/BIANCA/Fuggilozio/1_20aprile1859/iiif"

# URL a cui sarà raggiungibile il manifest P2
MANIFEST_ID = "https://ai4ch-uniud.github.io/DigitalImages/BIANCA/Fuggilozio/1_20aprile1859/manifest-p2.json"

LABEL = "Fuggilozio 1_20 aprile 1859"
# ============================


def main():
    print(f"Uso TILES_DIR = {TILES_DIR}")
    if not TILES_DIR.exists():
        print(f"Cartella tiles non trovata: {TILES_DIR}")
        return

    subdirs = sorted([d for d in TILES_DIR.iterdir() if d.is_dir()])
    if not subdirs:
        print(f"Nessuna sottocartella trovata in {TILES_DIR}")
        return

    canvases = []
    sequence_id = MANIFEST_ID + "/sequence/normal"

    for idx, d in enumerate(subdirs, start=1):
        info_path = d / "info.json"
        if not info_path.exists():
            print(f"SKIP {d.name}: info.json non trovato")
            continue

        with info_path.open(encoding="utf-8") as f:
            info = json.load(f)

        height = info.get("height")
        width = info.get("width")

        if height is None or width is None:
            sizes = info.get("sizes") or []
            if sizes:
                size = sizes[-1]
                height = size.get("height")
                width = size.get("width")

        if height is None or width is None:
            print(f"SKIP {d.name}: non trovo width/height in info.json")
            continue

        identifier = d.name  # es. "p233"
        service_id = f"{BASE_URL}/{identifier}"
        canvas_id = f"{MANIFEST_ID}/canvas/{identifier}"
        annotation_id = f"{canvas_id}/annotation"

        canvas = {
            "@id": canvas_id,
            "@type": "sc:Canvas",
            "label": f"Pagina {idx}",
            "height": height,
            "width": width,
            "images": [
                {
                    "@context": "http://iiif.io/api/presentation/2/context.json",
                    "@id": annotation_id,
                    "@type": "oa:Annotation",
                    "motivation": "sc:painting",
                    "resource": {
                        "@id": f"{service_id}/full/full/0/default.jpg",
                        "@type": "dctypes:Image",
                        "format": "image/jpeg",
                        "service": {
                            "@context": "http://iiif.io/api/image/2/context.json",
                            "@id": service_id,
                            "profile": "http://iiif.io/api/image/2/level0.json"
                        },
                        "height": height,
                        "width": width,
                    },
                    "on": canvas_id,
                }
            ],
        }

        canvases.append(canvas)
        print(f"Aggiunta canvas per '{identifier}' (Pagina {idx}, w={width}, h={height})")

    manifest = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": MANIFEST_ID,
        "@type": "sc:Manifest",
        "label": LABEL,
        "metadata": [],
        "sequences": [
            {
                "@id": sequence_id,
                "@type": "sc:Sequence",
                "label": [
                    {"@value": "Normal Sequence", "@language": "en"}
                ],
                "canvases": canvases,
            }
        ],
        "structures": [],
    }

    out_path = BASE_DIR / "manifest-p2.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print()
    print(f"Manifest P2 scritto in: {out_path}")
    print(f"ID manifest: {MANIFEST_ID}")


if __name__ == "__main__":
    main()
