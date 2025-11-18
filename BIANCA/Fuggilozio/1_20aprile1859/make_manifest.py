import json
from pathlib import Path

# ====== CONFIGURAZIONE ======
BASE_DIR = Path(__file__).resolve().parent
TILES_DIR = BASE_DIR / "iiif"

BASE_URL = "https://ai4ch-uniud.github.io/DigitalImages/BIANCA/Fuggilozio/1_20aprile1859/iiif"
MANIFEST_ID = "https://ai4ch-uniud.github.io/DigitalImages/BIANCA/Fuggilozio/1_20aprile1859/manifest.json"

LABEL = "Fuggilozio 1_20 aprile 1859"
LANG = "it"
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
    canvas_base = MANIFEST_ID.rsplit("/", 1)[0] + "/canvas/"

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

        identifier = d.name  # nome sottocartella, es. "img1"
        service_id = f"{BASE_URL}/{identifier}"
        service_type = info.get("type") or info.get("@type") or "ImageService3"
        profile = info.get("profile", "level0")

        canvas_id = f"{canvas_base}p{idx}"
        annotation_page_id = f"{canvas_id}/page"
        annotation_id = f"{canvas_id}/annotation"

        canvas = {
            "id": canvas_id,
            "type": "Canvas",
            "label": {LANG: [f"Pagina {idx}"]},
            "height": height,
            "width": width,
            "items": [
                {
                    "id": annotation_page_id,
                    "type": "AnnotationPage",
                    "items": [
                        {
                            "id": annotation_id,
                            "type": "Annotation",
                            "motivation": "painting",
                            "body": {
                                "id": f"{service_id}/full/full/0/default.jpg",
                                "type": "Image",
                                "format": "image/jpeg",
                                "service": [
                                    {
                                        "id": service_id,
                                        "type": service_type,
                                        "profile": profile,
                                    }
                                ],
                            },
                            "target": canvas_id,
                        }
                    ],
                }
            ],
        }

        canvases.append(canvas)
        print(f"Aggiunta pagina {idx} per '{identifier}' (w={width}, h={height})")

    manifest = {
        "@context": "https://iiif.io/api/presentation/3/context.json",
        "id": MANIFEST_ID,
        "type": "Manifest",
        "label": {LANG: [LABEL]},
        "behavior": ["paged"],
        "items": canvases,
    }

    out_path = BASE_DIR / "manifest.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print()
    print(f"Manifest scritto in: {out_path}")
    print(f"ID manifest: {MANIFEST_ID}")


if __name__ == "__main__":
    main()
