from dataclasses import dataclass, asdict
from typing import List, Union
import re, json

#
# ---------- Primitive element classes ----------
#
@dataclass
class Paragraph:   text: List[Union[str, 'Term']]  # Paragraph now stores a list of strings and terms
@dataclass
class Bullet:      label: str; text: str
@dataclass
class Link:        label: str; url: str
@dataclass
class Term:        text: str; definition: str  # Technical terms with definitions

Element = Union[Paragraph, Bullet, Link, Term]

#
# ---------- Mid-level structure ----------
#
@dataclass
class SubSection:
    title: str
    body: List[Element]

@dataclass
class Section:
    number: int
    title: str
    subs: List[SubSection]

#
# ---------- Helper function to fetch definitions ----------
#
def fetch_definition(term: str) -> str:
    """
    Simulates an API call to fetch definitions for technical terms.
    In a real scenario, you would replace this with an actual API request.
    """
    # For now, returning a mock definition for demonstration
    mock_definitions = {
        "AI": "Artificial Intelligence, the simulation of human intelligence in machines.",
        "IPO": "Initial Public Offering, a company's first sale of stock to the public."
    }
    return mock_definitions.get(term, "Definition not found.")

#
# ---------- Public API ----------
#
def parse(raw: str) -> List[Section]:
    """
    Main entry point.  Returns a list[Section] ready for Jinja OR json.dumps().
    """
    lines = [ln.rstrip() for ln in raw.splitlines()]
    sec_pat   = re.compile(r'^###\s*(\d+)\.\s+(.*)$')            # “### 1. …”
    sub_pat   = re.compile(r'^\*\*(.+?)\*\*:?\s*$')              # “**Deal 1:**”
    body_pat  = re.compile(r'^[A-Za-z0-9\-\s\.:,;]*$')           # Catch generic body content (Deal 1 etc.)
    link_pat  = re.compile(r'\*\*(?P<title>.+?)\*\*\s*\(\s*\[Link\]\((?P<url>https?://[^\s)]+)\)\s*\)')  # [label](url)
    term_pat  = re.compile(r'\b[A-Z]{2,}\b')                     # crude TODO term
    bullet_pat = re.compile(r'^[\*\-\•]\s+\*\*(.+?)\*\*\s*(.*)$')  # "- **Deal Size:** something"

    sections: List[Section] = []
    cur_sec, cur_sub = None, None

    def flush_sub():
        nonlocal cur_sec, cur_sub
        if cur_sub and cur_sub.body:  # Only append non-empty subsections
            cur_sec.subs.append(cur_sub)
        cur_sub = None

    def flush_sec():
        nonlocal cur_sec
        if cur_sec:
            sections.append(cur_sec)
        cur_sec = None

    def replace_terms_in_paragraph(paragraph_text: str) -> List[Union[str, Term]]:
        """
        Replaces technical terms in a paragraph text with Term objects
        and returns the modified list of elements (strings and Term objects).
        """
        elements = []
        last_pos = 0

        for match in term_pat.finditer(paragraph_text):
            # Append text before the term
            elements.append(paragraph_text[last_pos:match.start()].strip())
            # Create a Term object with definition and append it
            term = match.group(0)
            definition = fetch_definition(term)
            elements.append(Term(text=term, definition=definition))
            last_pos = match.end()

        # Append any remaining text after the last term
        elements.append(paragraph_text[last_pos:].strip())
        return elements

    for ln in lines:
        if not ln.strip():                      # blank → paragraph boundary
            continue

        # SECTION
        if (m := sec_pat.match(ln)):
            flush_sub(); flush_sec()
            cur_sec = Section(int(m.group(1)), m.group(2), subs=[])
            continue

        # SUBSECTION (title is specifically given)
        if (m := sub_pat.match(ln)):
            flush_sub()
            cur_sub = SubSection(m.group(1), body=[])
            continue

        # Generic "body" or unnamed subsections (not a **Deal X:**)
        if (m := body_pat.match(ln)):
            if cur_sub:
                cur_sub.body.append(Paragraph(text=[ln.strip()]))  # Store text in list
            else:
                # If there's no valid subsection yet, create a default one
                cur_sub = SubSection("", body=[Paragraph(text=[ln.strip()])])
            continue

        # If no subsection, create a default one
        if not cur_sub:
            cur_sub = SubSection("", body=[])

        # Bullet?
        if bullet_pat.match(ln):
            m = bullet_pat.match(ln)
            label = m.group(1).strip()
            text = m.group(2).strip()
            if label.endswith(":"):
                label = label[:-1]
            cur_sub.body.append(Bullet(label=label, text=text))   # Clean the bullet content
            continue

        # Links (may be inline inside paragraph)
        def _replace_link(match):
            cur_sub.body.append(Link(match.group("title"), match.group("url")))
            return match.group("title")  # Keep the link text as plain text

        ln_clean = link_pat.sub(_replace_link, ln)

        # Only append the cleaned line if it wasn't replaced by a link
        if link_pat.search(ln) is None:
            # Replace any technical terms in the paragraph
            cur_sub.body.append(Paragraph(text=replace_terms_in_paragraph(ln_clean)))

    flush_sub(); flush_sec()
    return sections
