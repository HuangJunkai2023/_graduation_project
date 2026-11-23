"""Assemble the ELEC3801 PDF from existing local documents and evidence records."""
from argparse import ArgumentParser
from datetime import date
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from urllib.parse import urlsplit

from pypdf import PdfReader, PdfWriter


def required_text(record, key):
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing recorded value: {key}")
    return value.strip()


def load_pdf(folder, record, key, page_limit=None):
    path = (folder / required_text(record, key)).resolve()
    if not path.is_file():
        raise ValueError(f"PDF is unavailable: {path}")
    reader = PdfReader(path)
    count = len(reader.pages)
    if not count or (page_limit is not None and count > page_limit):
        raise ValueError(f"{key} contains {count} pages, limit {page_limit}")
    return path, reader


def assemble(manifest_path, output):
    record = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    assessor = required_text(record, "assessor")
    required_text(record, "access_confirmed_by")
    one_drive = required_text(record, "one_drive_url")
    url = urlsplit(one_drive)
    host = (url.hostname or "").lower()
    if url.scheme != "https" or not (
        host.endswith(".sharepoint.com") or host in {"1drv.ms", "onedrive.live.com"}
    ):
        raise ValueError("Expected an HTTPS OneDrive sharing URL")

    reviews = sorted(record.get("review_documents", []), key=lambda row: row["number"])
    if [row["number"] for row in reviews] != list(range(1, 11)):
        raise ValueError("Ten numbered Review Documents (1 through 10) are required")
    for row in reviews:
        date.fromisoformat(required_text(row, "approval_date"))
        required_text(row, "approval_method")

    folder = manifest_path.parent
    cover = load_pdf(folder, record, "cover_pdf", 1)
    declaration = load_pdf(folder, record, "signed_declaration_pdf", 1)
    report = load_pdf(folder, record, "technical_report_pdf", 7)
    cover_page = cover[1].pages[0]
    cover_text = " ".join(cover_page.extract_text().casefold().split())
    if " ".join(assessor.casefold().split()) not in cover_text:
        raise ValueError("The assessor in the evidence record is missing from the cover")
    links = []
    for ref in cover_page.get("/Annots", []):
        action = ref.get_object().get("/A")
        if action is not None:
            links.append(action.get_object().get("/URI"))
    if one_drive not in links:
        raise ValueError("The exact OneDrive sharing link needs an active annotation on the cover")

    parts = [cover, declaration, report]
    if record.get("supplement_pdf"):
        parts.append(load_pdf(folder, record, "supplement_pdf"))
    parts.extend(load_pdf(folder, row, "pdf", 2) for row in reviews)
    identities = [sha256(path.read_bytes()).hexdigest() for path, _ in parts]
    if len(set(identities)) != len(identities):
        raise ValueError("Multiple sections use identical PDF inputs")

    writer = PdfWriter()
    for _, reader in parts:
        writer.append(reader, import_outline=False)
    buffer = BytesIO()
    writer.write(buffer)
    content = buffer.getbuffer()
    with output.open("xb") as handle:
        handle.write(content)
    return {
        "output": str(output),
        "pages": len(writer.pages),
        "technical_report_pages": len(report[1].pages),
        "review_documents": len(reviews),
        "sha256": sha256(content).hexdigest(),
        "verification_scope": "PDF order, cover link and provided records. Signatures and account access depend on the supplied evidence.",
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        result = assemble(args.manifest, args.output)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
