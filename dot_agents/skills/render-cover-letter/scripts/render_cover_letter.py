"""Render immutable cover-letter body text as a polished one-page PDF."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

import pdfplumber
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Indenter,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

NAME = "Flo Kempenich"
LOCATION = "London, United Kingdom"
EMAIL = "flo@kempenich.ai"
PHONE = "+44 7501 746364"
LINKEDIN_LABEL = "linkedin.com/in/FloKempenich"
LINKEDIN_URL = "https://www.linkedin.com/in/FloKempenich"

NAVY = colors.HexColor("#17324D")
SLATE = colors.HexColor("#52606D")
RULE = colors.HexColor("#9EAFBF")
INK = colors.HexColor("#17212B")
LINK_HEX = "#365F7D"

AVENIR_NEXT = Path("/System/Library/Fonts/Avenir Next.ttc")
FONT_REGULAR = "AvenirNext-Regular"
FONT_MEDIUM = "AvenirNext-Medium"
FONT_DEMI = "AvenirNext-DemiBold"

EXIT_INPUT = 2
EXIT_OVERFLOW = 3
MAX_COMFORTABLE_BOTTOM = 0.90


@dataclass(frozen=True)
class LayoutPreset:
    """Readable presentation settings; never a content transformation."""

    meta_size: float
    meta_leading: float
    role_size: float
    role_leading: float
    body_size: float
    body_leading: float
    paragraph_space_after: float
    rule_to_role_gap: float
    role_space_after: float
    meta_to_greeting_gap: float
    greeting_space_after: float
    body_right_inset_mm: float


LAYOUTS = {
    "relaxed": LayoutPreset(
        meta_size=9.8,
        meta_leading=12,
        role_size=14.2,
        role_leading=17,
        body_size=12,
        body_leading=17,
        paragraph_space_after=11,
        rule_to_role_gap=60,
        role_space_after=2.6,
        meta_to_greeting_gap=13.9,
        greeting_space_after=7,
        body_right_inset_mm=20,
    ),
    "balanced": LayoutPreset(
        meta_size=9.3,
        meta_leading=11.5,
        role_size=13,
        role_leading=15.5,
        body_size=10.8,
        body_leading=14.4,
        paragraph_space_after=7.2,
        rule_to_role_gap=45,
        role_space_after=2.2,
        meta_to_greeting_gap=10.7,
        greeting_space_after=5.5,
        body_right_inset_mm=0,
    ),
    "compact": LayoutPreset(
        meta_size=9.1,
        meta_leading=11,
        role_size=12.6,
        role_leading=15,
        body_size=10.3,
        body_leading=13.5,
        paragraph_space_after=6,
        rule_to_role_gap=38,
        role_space_after=2,
        meta_to_greeting_gap=9,
        greeting_space_after=5,
        body_right_inset_mm=0,
    ),
}


class InputError(ValueError):
    """Raised when required cover-letter input is invalid."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render approved cover-letter body text without changing its wording."
        )
    )
    parser.add_argument(
        "--body-file",
        required=True,
        help="UTF-8 body text file, or - to read from stdin.",
    )
    parser.add_argument("--company", required=True, help="Target company name.")
    parser.add_argument("--role", required=True, help="Target role title.")
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "Output PDF path. Defaults to "
            "~/Downloads/Flo_Kempenich_<Company>_Cover_Letter.pdf."
        ),
    )
    parser.add_argument(
        "--date",
        help="Letter date, for reproducible renders. Defaults to today in Europe/London.",
    )
    parser.add_argument(
        "--layout",
        choices=("auto", *LAYOUTS),
        default="auto",
        help=(
            "Presentation density. Auto selects relaxed, balanced, or compact "
            "for the cleanest one-page balance without changing the body."
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the resolved output path. Use only with explicit approval.",
    )
    return parser.parse_args()


def clean_required(value: str, label: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise InputError(f"{label} must not be empty")
    return cleaned


def read_body(body_file: str) -> str:
    if body_file == "-":
        raw = sys.stdin.read()
    else:
        path = Path(body_file).expanduser()
        if not path.is_file():
            raise InputError(f"body file not found: {path}")
        raw = path.read_text(encoding="utf-8")

    normalized_newlines = raw.replace("\r\n", "\n").replace("\r", "\n")
    body = normalized_newlines.strip()
    if not body:
        raise InputError("cover-letter body must not be empty")
    return body


def split_paragraphs(body: str) -> list[str]:
    paragraphs = [
        re.sub(r"[\t\n ]+", " ", paragraph).strip()
        for paragraph in re.split(r"\n[ \t]*\n+", body)
    ]
    return [paragraph for paragraph in paragraphs if paragraph]


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def safe_company_filename(company: str) -> str:
    ascii_company = (
        unicodedata.normalize("NFKD", company).encode("ascii", "ignore").decode()
    )
    safe = re.sub(r"[^A-Za-z0-9]+", "_", ascii_company).strip("_")
    return safe or "Company"


def default_output(company: str) -> Path:
    filename = f"Flo_Kempenich_{safe_company_filename(company)}_Cover_Letter.pdf"
    return Path.home() / "Downloads" / filename


def ensure_pdf_suffix(path: Path) -> Path:
    return path if path.suffix.lower() == ".pdf" else path.with_suffix(".pdf")


def next_available_path(path: Path) -> Path:
    if not path.exists():
        return path
    version = 2
    while True:
        candidate = path.with_name(f"{path.stem}_v{version}{path.suffix}")
        if not candidate.exists():
            return candidate
        version += 1


def resolve_output(args: argparse.Namespace, company: str) -> Path:
    requested = args.output.expanduser() if args.output else default_output(company)
    requested = ensure_pdf_suffix(requested).resolve()
    if args.overwrite:
        return requested
    return next_available_path(requested)


def letter_date(explicit_date: str | None) -> str:
    if explicit_date:
        return clean_required(explicit_date, "date")
    current = datetime.now(ZoneInfo("Europe/London"))
    return f"{current.day} {current:%B %Y}"


def link(label: str, url: str) -> str:
    return f'<link href="{escape(url)}" color="{LINK_HEX}">{escape(label)}</link>'


def register_fonts() -> None:
    """Register Flo's established cover-letter typeface from macOS."""

    if not AVENIR_NEXT.is_file():
        raise RuntimeError(f"required font collection not found: {AVENIR_NEXT}")
    for name, index in (
        (FONT_DEMI, 2),
        (FONT_MEDIUM, 5),
        (FONT_REGULAR, 7),
    ):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(
                TTFont(name, str(AVENIR_NEXT), subfontIndex=index)
            )


def styles(preset: LayoutPreset) -> dict[str, ParagraphStyle]:
    return {
        "name": ParagraphStyle(
            "Name",
            fontName=FONT_DEMI,
            fontSize=23,
            leading=25,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceAfter=10,
        ),
        "contact": ParagraphStyle(
            "Contact",
            fontName=FONT_REGULAR,
            fontSize=8.7,
            leading=10.5,
            textColor=SLATE,
            alignment=TA_LEFT,
        ),
        "meta": ParagraphStyle(
            "Meta",
            fontName=FONT_REGULAR,
            fontSize=preset.meta_size,
            leading=preset.meta_leading,
            textColor=SLATE,
        ),
        "role": ParagraphStyle(
            "Role",
            fontName=FONT_DEMI,
            fontSize=preset.role_size,
            leading=preset.role_leading,
            textColor=NAVY,
            spaceAfter=preset.role_space_after,
        ),
        "body": ParagraphStyle(
            "Body",
            fontName=FONT_REGULAR,
            fontSize=preset.body_size,
            leading=preset.body_leading,
            textColor=INK,
            alignment=TA_JUSTIFY,
            spaceAfter=preset.paragraph_space_after,
        ),
        "greeting": ParagraphStyle(
            "Greeting",
            fontName=FONT_MEDIUM,
            fontSize=preset.body_size,
            leading=preset.body_leading,
            textColor=INK,
            alignment=TA_LEFT,
            spaceAfter=preset.greeting_space_after,
        ),
        "closing": ParagraphStyle(
            "Closing",
            fontName=FONT_REGULAR,
            fontSize=preset.body_size,
            leading=preset.body_leading,
            textColor=INK,
        ),
        "signature": ParagraphStyle(
            "Signature",
            fontName=FONT_DEMI,
            fontSize=preset.body_size,
            leading=preset.body_leading,
            textColor=INK,
        ),
    }


def render_pdf(
    output: Path,
    body: str,
    company: str,
    role: str,
    date_text: str,
    preset: LayoutPreset,
) -> None:
    style = styles(preset)
    document = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=15.5 * mm,
        bottomMargin=15.5 * mm,
        title=f"Cover Letter - {role} - {company}",
        author=NAME,
        subject=f"Application for {role} at {company}",
        creator="ReportLab",
    )

    contact_line = " &#160;·&#160; ".join(
        [
            escape(LOCATION),
            link(EMAIL, f"mailto:{EMAIL}"),
            escape(PHONE),
            link(LINKEDIN_LABEL, LINKEDIN_URL),
        ]
    )

    story = [
        Paragraph(escape(NAME), style["name"]),
        Paragraph(contact_line, style["contact"]),
        Spacer(1, 4.06 * mm),
        HRFlowable(
            width="100%",
            thickness=0.75,
            color=RULE,
        ),
        Spacer(1, preset.rule_to_role_gap),
        Indenter(left=0, right=preset.body_right_inset_mm * mm),
        Paragraph(escape(role), style["role"]),
        Paragraph(escape(f"{company} · {date_text}"), style["meta"]),
        Spacer(1, preset.meta_to_greeting_gap),
        Paragraph(escape(f"Dear {company} Hiring Team,"), style["greeting"]),
    ]

    for paragraph in split_paragraphs(body):
        story.append(Paragraph(escape(paragraph), style["body"]))

    story.extend(
        [
            Spacer(1, 5),
            KeepTogether(
                [
                    Paragraph("Kind regards,", style["closing"]),
                    Spacer(1, 2),
                    Paragraph(escape(NAME), style["signature"]),
                ]
            ),
            Indenter(left=0, right=-preset.body_right_inset_mm * mm),
        ]
    )
    document.build(story)


def verify_pdf(
    pdf_path: Path,
    body: str,
    company: str,
    role: str,
    date_text: str,
) -> None:
    reader = PdfReader(str(pdf_path))
    if len(reader.pages) != 1:
        raise OverflowError(f"expected one page, rendered {len(reader.pages)}")

    page = reader.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    if abs(width - A4[0]) > 1 or abs(height - A4[1]) > 1:
        raise RuntimeError(f"expected A4 page, got {width:.2f} x {height:.2f} points")

    extracted = page.extract_text() or ""
    normalized_pdf = normalize_text(extracted)
    normalized_body = normalize_text(body)
    if normalized_body not in normalized_pdf:
        raise RuntimeError("PDF text does not contain the approved body verbatim")

    required_text = [
        NAME,
        LOCATION,
        EMAIL,
        PHONE,
        LINKEDIN_LABEL,
        role,
        f"{company} · {date_text}",
        f"Dear {company} Hiring Team,",
        "Kind regards,",
    ]
    missing = [item for item in required_text if item not in extracted]
    if missing:
        raise RuntimeError(f"PDF is missing required framing: {missing}")

    annotations = page.get("/Annots", [])
    uris: set[str] = set()
    for annotation_ref in annotations:
        annotation = annotation_ref.get_object()
        action = annotation.get("/A")
        if action and action.get("/URI"):
            uris.add(str(action.get("/URI")))
    expected_uris = {f"mailto:{EMAIL}", LINKEDIN_URL}
    if not expected_uris.issubset(uris):
        raise RuntimeError("PDF is missing clickable email or LinkedIn links")

    with pdfplumber.open(str(pdf_path)) as document:
        rendered_page = document.pages[0]
        for word in rendered_page.extract_words(use_text_flow=True):
            if (
                float(word["x0"]) < -1
                or float(word["top"]) < -1
                or float(word["x1"]) > float(rendered_page.width) + 1
                or float(word["bottom"]) > float(rendered_page.height) + 1
            ):
                raise RuntimeError(f"PDF contains clipped text: {word['text']!r}")


def content_bottom_fraction(pdf_path: Path) -> float:
    """Return the bottommost text position as a fraction of page height."""

    with pdfplumber.open(str(pdf_path)) as document:
        if len(document.pages) != 1:
            raise RuntimeError("page-balance analysis requires exactly one page")
        page = document.pages[0]
        words = page.extract_words(use_text_flow=True)
        if not words:
            raise RuntimeError("could not measure page balance: no text found")
        return max(float(word["bottom"]) for word in words) / float(page.height)


def temporary_pdf(output: Path, layout_name: str) -> Path:
    with tempfile.NamedTemporaryFile(
        prefix=f".render-cover-letter-{layout_name}-",
        suffix=".pdf",
        dir=output.parent,
        delete=False,
    ) as temporary:
        return Path(temporary.name)


def render_candidates(
    output: Path,
    body: str,
    company: str,
    role: str,
    date_text: str,
    requested_layout: str,
) -> tuple[Path, str, float, list[Path]]:
    """Render verified candidates and choose the best readable page balance."""

    layout_names = (
        list(LAYOUTS) if requested_layout == "auto" else [requested_layout]
    )
    temporary_paths: list[Path] = []
    fitting: list[tuple[Path, str, float]] = []
    try:
        for layout_name in layout_names:
            candidate = temporary_pdf(output, layout_name)
            temporary_paths.append(candidate)
            render_pdf(
                candidate,
                body,
                company,
                role,
                date_text,
                LAYOUTS[layout_name],
            )
            try:
                verify_pdf(candidate, body, company, role, date_text)
            except OverflowError:
                continue
            fitting.append(
                (candidate, layout_name, content_bottom_fraction(candidate))
            )

        if not fitting:
            raise OverflowError(
                f"none of the requested readable layouts ({', '.join(layout_names)}) "
                "fit on one A4 page"
            )

        if requested_layout == "auto":
            comfortable = [
                item for item in fitting if item[2] <= MAX_COMFORTABLE_BOTTOM
            ]
            # Layouts are ordered from most spacious to most compact. Use the
            # first comfortable fit instead of vertically centering short text.
            selected = comfortable[0] if comfortable else min(
                fitting, key=lambda item: item[2]
            )
        else:
            selected = fitting[0]
        return (*selected, temporary_paths)
    except Exception:
        for temporary_path in temporary_paths:
            if temporary_path.exists():
                temporary_path.unlink()
        raise


def main() -> int:
    args = parse_args()
    temporary_paths: list[Path] = []
    try:
        company = clean_required(args.company, "company")
        role = clean_required(args.role, "role")
        body = read_body(args.body_file)
        date_text = letter_date(args.date)
        output = resolve_output(args, company)
        output.parent.mkdir(parents=True, exist_ok=True)
        register_fonts()

        try:
            selected, selected_layout, balance, temporary_paths = render_candidates(
                output,
                body,
                company,
                role,
                date_text,
                args.layout,
            )
        except OverflowError as error:
            print(
                "OVERFLOW: the approved body does not fit cleanly on one A4 page. "
                "No final PDF was created. Ask whether to allow two pages or shorten "
                f"the source. ({error})",
                file=sys.stderr,
            )
            return EXIT_OVERFLOW

        os.replace(selected, output)
        output.chmod(0o644)
        normalized_hash = hashlib.sha256(
            normalize_text(body).encode("utf-8")
        ).hexdigest()
        print(f"output={output}")
        print("verification=passed")
        print("pages=1")
        print(f"layout={selected_layout}")
        print(f"content_bottom_fraction={balance:.3f}")
        print(f"body_sha256={normalized_hash}")
        return 0
    except InputError as error:
        print(f"INPUT_ERROR: {error}", file=sys.stderr)
        return EXIT_INPUT
    except Exception as error:  # noqa: BLE001 - friendly error boundary for the CLI
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    finally:
        for temporary_path in temporary_paths:
            if temporary_path.exists():
                temporary_path.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
