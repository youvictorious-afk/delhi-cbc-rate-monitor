import re


def clean_text(text):

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def extract_delhi_lines(text):

    results = []

    for line in text.splitlines():

        line = clean_text(line)

        if not line:
            continue

        if "DELHI" not in line.upper():
            continue

        results.append({
            "publication": "",
            "edition": "DELHI",
            "language": "",
            "media_type": "",
            "rate": None,
            "rate_unit": "",
            "effective_from": "",
            "raw_text": line,
            "confidence": "DISCOVERY"
        })

    # Remove duplicates.
    unique = []

    seen = set()

    for item in results:

        key = item["raw_text"]

        if key in seen:
            continue

        seen.add(key)

        unique.append(item)

    return unique
