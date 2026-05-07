from __future__ import annotations

import argparse
import re
from pathlib import Path

from pypdf import PdfReader


def clean_text(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(pdf_path: Path, max_pages: int | None = None) -> str:
    reader = PdfReader(str(pdf_path))
    pages = reader.pages if max_pages is None else reader.pages[:max_pages]
    chunks: list[str] = []
    for p in pages:
        chunks.append(p.extract_text() or "")
    return clean_text("\n\n".join(chunks))


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text from report PDFs.")
    parser.add_argument(
        "--report-dir",
        type=str,
        default="code/stock1800/report_Daily",
        help="Directory containing PDFs",
    )
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=["华泰金工", "缺口回补", "上下影线"],
        help="Select PDFs by filename keyword",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=8,
        help="Max pages to extract from each PDF",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default="code/stock1800/classwork_pdf_text",
        help="Output txt directory",
    )
    args = parser.parse_args()

    report_dir = Path(args.report_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(report_dir.glob("*.pdf"))
    selected = [p for p in pdfs if any(k in p.name for k in args.keywords)]

    if not selected:
        raise FileNotFoundError(f"No PDFs matched keywords={args.keywords}")

    for pdf in selected:
        txt = extract_pdf_text(pdf, max_pages=args.max_pages)
        out_name = pdf.stem + ".txt"
        out_path = out_dir / out_name
        out_path.write_text(txt, encoding="utf-8")
        print(f"Extracted: {pdf.name} -> {out_path}")


if __name__ == "__main__":
    main()

