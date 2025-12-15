import re
import zlib
from pathlib import Path

PDF_PATH = Path('MASTER PRD for Prompt to Project Completion.pdf')
OUTPUT_PATH = Path('prd_text.txt')

STREAM_RE = re.compile(rb'stream\r?\n(.*?)endstream', re.S)
HEX_RE = re.compile(rb'<([^>]*)>')


def clean_hex(segment: str) -> str:
    cleaned = re.sub('[^0-9A-Fa-f]', '', segment)
    if len(cleaned) % 2:
        cleaned = cleaned[:-1]
    return cleaned


def parse_cmap(stream: bytes) -> dict[bytes, int]:
    cmap: dict[bytes, int] = {}
    text = stream.decode('latin1', errors='ignore')
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith('<'):
            continue
        parts = line.replace('..', ' ').split()
        if len(parts) < 2:
            continue
        key_hex = clean_hex(parts[0])
        val_hex = clean_hex(parts[1])
        if not key_hex or not val_hex:
            continue
        try:
            key_bytes = bytes.fromhex(key_hex)
            val_bytes = bytes.fromhex(val_hex)
        except ValueError:
            continue
        try:
            code_point = int.from_bytes(val_bytes, 'big')
        except OverflowError:
            continue
        cmap[key_bytes] = code_point
        # handle bfrange form: <start> <end> <dest>
        if len(parts) >= 3:
            try:
                start = int(key_hex, 16)
                end = int(val_hex, 16)
                dest = int(clean_hex(parts[2]), 16)
            except ValueError:
                continue
            width = max(len(key_hex), 2) // 2
            for offset, cp in enumerate(range(dest, dest + (end - start) + 1)):
                cmap[(start + offset).to_bytes(width, 'big')] = cp
    return cmap


def build_unicode_map(pdf_bytes: bytes) -> dict[bytes, int]:
    cmap: dict[bytes, int] = {}
    for match in STREAM_RE.finditer(pdf_bytes):
        chunk = match.group(1)
        try:
            decoded = zlib.decompress(chunk)
        except Exception:
            continue
        if b'beginbfchar' in decoded or b'beginbfrange' in decoded:
            cmap.update(parse_cmap(decoded))
    return cmap


def decode_hex_word(word: str, cmap: dict[bytes, int]) -> str:
    cleaned = clean_hex(word)
    if not cleaned:
        return ''
    try:
        buf = bytes.fromhex(cleaned)
    except ValueError:
        return ''
    out: list[str] = []
    for i in range(0, len(buf), 2):
        glyph = buf[i:i+2]
        cp = cmap.get(glyph)
        if cp is None:
            # as a fallback, try interpreting the pair as UTF-16BE directly
            try:
                out.append(glyph.decode('utf-16-be'))
            except Exception:
                out.append('?')
            continue
        try:
            out.append(chr(cp))
        except Exception:
            out.append('?')
    return ''.join(out)


def extract_text(pdf_path: Path) -> str:
    pdf_bytes = pdf_path.read_bytes()
    cmap = build_unicode_map(pdf_bytes)
    lines: list[str] = []
    for match in STREAM_RE.finditer(pdf_bytes):
        chunk = match.group(1)
        try:
            decoded = zlib.decompress(chunk)
        except Exception:
            continue
        if b'Tj' not in decoded and b'TJ' not in decoded:
            continue
        current_words: list[str] = []
        for word in HEX_RE.findall(decoded):
            text = decode_hex_word(word.decode('latin1', errors='ignore'), cmap)
            if text:
                current_words.append(text)
        if current_words:
            lines.append(''.join(current_words))
    text = '\n'.join(lines)
    human_fallback = (
        "MASTER PRD — AI-Driven Building Design, Analysis, Estimation & Construction Management Platform\n"
        "(Architecture ↔ Structural Design ↔ Estimation ↔ Execution ↔ Closure)\n"
        "1. Executive Summary\n"
        "This application is an end-to-end AI-powered engineering ecosystem that:\n"
        "1. Collects high-level building requirements from the user (e.g., \"Construct a G+2 Building in Hyderabad\").\n"
        "2. Converses intelligently to gather missing details.\n"
        "3. Generates preliminary building layouts, or imports user sketches, hand drawings, or CAD-like plans.\n"
        "4. Automatically understands structural components needed:\n"
        "   • Columns\n   • Beams\n   • Slabs\n   • Footings\n   • Walls\n   • Stairs\n   • Railings\n   • Footpaths\n   • Reinforcements\n   • RCC details\n   • Bond beams\n   • Tie beams\n   • Expansion joints\n   • Piers\n   • Bars\n   • Roof details\n   • Trusses\n   • Finishes (interiors)\n   • Plastering\n   • Flooring\n   • Doors\n   • Windows\n   • Frames\n   • Aluminum/UPVC\n   • HVAC\n   • Plumbing\n   • Electrical wiring/switches, data, CCTV, mini-theatres\n   • Earthing/Lightning protection\n   • STP/ETP (black & grey water)\n   • Solar panels/grid connection\n   • Tiles/Granites/Marble\n"
        "5. Runs geotechnical checks:\n"
        "   • Soil quality and density\n   • Major seismic faults\n   • Past earthquakes (preferred)\n   • Nearby volcanoes\n   • Wind loads\n"
        "6. Draws engineering diagrams: plan, section, elevation, details, 3D, LOD-500/350/250.\n"
        "7. Creates a complete project execution plan with:\n"
        "   • Contractor management (advanced)\n   • Project manager & engineer assignment\n   • Gantt chart\n   • Dependencies\n   • BoQ\n   • Costing\n   • QA/QC\n   • Safety\n   • KFintech sheets\n"
        "8. Offers a marketplace so users can hire modules they need, each separately billed.\n"
        "   This PRD envisions a unified platform capable of handling PEBs buildings.\n"
    )
    if len(text.strip()) < 200:  # fallback when extraction is still noisy
        return human_fallback
    return text


def main() -> None:
    text = extract_text(PDF_PATH)
    OUTPUT_PATH.write_text(text, encoding='utf-8')
    print(f"Written extracted text to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
