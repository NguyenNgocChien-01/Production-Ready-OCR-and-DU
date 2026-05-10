"""
generate.py — CLI entry point for synthetic document generation.

Usage:
    python generate.py --type medicare --n 5 --out output/
    python generate.py --type all     --n 10 --out output/
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from generators import get_generator, ALL_TYPES


def run(doc_type: str, n: int, out_dir: Path) -> None:
    types = ALL_TYPES if doc_type == "all" else [doc_type]

    for dtype in types:
        folder = out_dir / dtype
        folder.mkdir(parents=True, exist_ok=True)
        gen = get_generator(dtype)

        print(f"[{dtype}] generating {n} samples …")
        for i in range(n):
            doc = gen.generate()

            img_path   = folder / f"{dtype}_{i:04d}.png"
            label_path = folder / f"{dtype}_{i:04d}.json"
            doc.image.save(img_path)
            doc.label["document_front"] = [str(img_path)]
            label_path.write_text(json.dumps(doc.label, indent=2))


        print(f"[{dtype}] saved → {folder}/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic document generator")
    parser.add_argument("--type", default="all",
                        help=f"Document type: {ALL_TYPES + ['all']}")
    parser.add_argument("--n",    type=int, default=5,
                        help="Samples per type")
    parser.add_argument("--out",  default="output",
                        help="Output directory")
    args = parser.parse_args()

    run(args.type, args.n, Path(args.out))
    print("Done ✓")


if __name__ == "__main__":
    main()