import re


def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_delhi_lines(text):

    results = []
    seen = set()

    for raw_line in text.splitlines():

        line = clean_text(raw_line)

        if not line:
            continue

        upper = line.upper()

        # Delhi only
        if "DELHI" not in upper:
            continue

        # Ignore obvious navigation/UI text
        ignored = [
            "PUBLISHERS ON PANEL",
            "HOME",
            "CONTACT",
            "LOGIN",
            "MENU"
        ]

        if any(x in upper for x in ignored):
            continue

        key = line.lower()

        if key in seen:
            continue

        seen.add(key)

        # Try to identify numbers that could represent rates.
        numbers = re.findall(
            r"(?:₹|RS\.?|INR)?\s*\d+(?:,\d{3})*(?:\.\d+)?",
            line,
            flags=re.IGNORECASE
        )

        possible_rate = None

        if numbers:
            cleaned = numbers[-1]
            cleaned = re.sub(
                r"[^\d.]",
                "",
                cleaned
            )

            try:
                possible_rate = float(cleaned)
            except:
                possible_rate = None

        results.append({

            "publication": "",

            "edition": "DELHI",

            "language": "",

            "media_type": "",

            "rate": possible_rate,

            "rate_unit": "",

            "effective_from": "",

            "raw_text": line,

            "confidence":
                "DISCOVERY"

        })

    return results
