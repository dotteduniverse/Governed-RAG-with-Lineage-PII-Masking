import re
import spacy
from typing import List, Tuple

# Load spaCy model (small English)
nlp = spacy.load("en_core_web_sm")

def detect_pii(text: str) -> List[Tuple[str, str, int, int]]:
    """Return list of (text, label, start, end) for PII entities."""
    doc = nlp(text)
    entities = []
    # spaCy NER
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "EMAIL", "ORG", "GPE", "LOC"]:
            entities.append((ent.text, ent.label_, ent.start_char, ent.end_char))
    # Additional regex for emails, SSNs, phone numbers
    email_pattern = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')
    for match in email_pattern.finditer(text):
        entities.append((match.group(), "EMAIL", match.start(), match.end()))
    ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    for match in ssn_pattern.finditer(text):
        entities.append((match.group(), "SSN", match.start(), match.end()))
    phone_pattern = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    for match in phone_pattern.finditer(text):
        entities.append((match.group(), "PHONE", match.start(), match.end()))
    # Remove duplicates (keep longest span)
    entities.sort(key=lambda x: (x[2], -x[3]))
    merged = []
    for e in entities:
        if not merged or e[2] >= merged[-1][3]:
            merged.append(e)
        elif e[3] > merged[-1][3]:
            merged[-1] = e
    return merged

def mask_pii(text: str) -> str:
    """Replace PII with [REDACTED] placeholders."""
    entities = detect_pii(text)
    # Sort in reverse order of start index to avoid offset issues
    entities.sort(key=lambda x: x[2], reverse=True)
    masked = text
    for ent_text, label, start, end in entities:
        masked = masked[:start] + f"[REDACTED {label}]" + masked[end:]
    return masked