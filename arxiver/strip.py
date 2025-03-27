import re

def strip_comments(content):
    return re.sub(r'((?:^|[^\\\n])(?:\\\\)*)%.*(\n?)', r"\1%\2", content, flags=re.MULTILINE)
