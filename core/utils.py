import re

SSTI_PATTERN = re.compile(r"(\{\{.*\}\}|\{%.*%\}|\$\{.*\})", re.DOTALL)


def contains_ssti_markers(text):
    if not text:
        return False
    return bool(SSTI_PATTERN.search(text))
