---
name: render-cover-letter
description: Render Flo's approved cover-letter body text as a polished, upload-ready A4 PDF without changing its wording. Use when Flo asks to format, package, convert, or turn a final or raw cover-letter body into a PDF. Do not use this skill to research, draft, critique, rewrite, spell-check, or improve cover-letter content.
---

# Render Cover Letter

Turn locked body text into a professional one-page PDF. Treat every word and punctuation mark in the body as immutable. The presentation adapts to the amount of text; no single reference letter is a fixed visual template.

## Intake

Require only:

- company
- role
- approved body text

Ask one compact question for anything missing. Accept body text only. Add the contact header, current date, role heading, company line, greeting, closing, and name automatically.

## Render

1. Save the approved body to a temporary UTF-8 text file without shell interpolation.
2. Run `scripts/render_cover_letter.py` with `--body-file`, `--company`, and `--role`.
   - Use the bundled workspace Python when it provides `reportlab`, `pdfplumber`, and `pypdf`.
   - Otherwise use `uv run --with reportlab --with pdfplumber --with pypdf python`.
   - Omit `--output` to use `/Users/flo/Downloads/Flo_Kempenich_<Company>_Cover_Letter.pdf`.
   - Leave `--layout` unset for adaptive layout selection.
   - Use `--layout relaxed`, `balanced`, or `compact` only when Flo asks to iterate on the presentation.
   - Pass `--overwrite` only when Flo explicitly asks to replace an existing PDF. Otherwise the script creates a versioned filename.
3. If the script exits with code `3`, stop. Tell Flo the unchanged body cannot fit cleanly on one page and ask whether to allow two pages or let him shorten it.
4. Render the result to PNG with `pdftoppm -png -r 160` and inspect the complete page.
5. Deliver only after the page has clean spacing, legible glyphs, no clipping or overlap, and intentional whitespace. Never solve a visual problem by editing the body.
6. Remove temporary body and preview files after verification.

Example:

```text
python scripts/render_cover_letter.py \
  --body-file /tmp/approved-cover-letter.txt \
  --company "Example Company" \
  --role "Staff AI Engineer"
```

## Adaptive Layout

- `auto` is the default. It privately renders each readable preset, then chooses the most spacious one that fits comfortably.
- `relaxed` gives shorter letters a larger type size and a narrower text column. The column remains aligned with the header; all additional inset goes on the right.
- `balanced` uses the full text width and approved readable density for a typical five-paragraph letter.
- `compact` is the readable lower bound for longer letters. If it cannot fit, fail instead of shrinking further.

Keep the letter top-weighted. Never vertically centre a short letter or distribute spare page height between sections. Layout selection changes typography, column width, and spacing only. It never changes, shortens, or corrects the body.

## Design Contract

- Use Avenir Next with a navy name and role heading.
- Keep the name, contact row, divider, role, and body on the same left edge.
- Keep a fixed, visibly comfortable gap between `Flo Kempenich` and the contact row.
- Put `<Company> · <current date>` directly below the role heading.
- Keep the contact row compact, with clickable email and LinkedIn links.
- Use balanced margins, deliberate paragraph rhythm, and no recipient address block.
- Inspect the actual final-page PNG before delivery. Text extraction alone is not visual verification.

## Locked Contract

- Preserve the body wording and punctuation verbatim. Reflow whitespace only for PDF line wrapping.
- Preserve blank-line paragraph boundaries.
- Escape markup characters rather than interpreting them.
- Add `<Role>`, `<Company> · <current date>`, `Dear <Company> Hiring Team,`, `Kind regards,`, and `Flo Kempenich`.
- Use the current Europe/London date and Flo's established contact header.
- Use one-page A4, readable typography, clickable email and LinkedIn links, and no recipient address block.
- Preserve the approved design language while allowing the layout density and right inset to suit the text length.
- Never research, critique, rewrite, correct, shorten, or embellish the body.
- Never silently overwrite an existing PDF.
