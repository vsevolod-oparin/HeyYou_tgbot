from pathlib import Path


def get_file_content(token_path: Path) -> str:
    with open(token_path) as f:
        return f.read()


def get_joined_lines(content: str) -> str:
    lines = content.split('\n')
    result = []
    for line in lines:
        line = line.strip()
        if len(line) == 0:
            result.append([line])
        elif len(result) != 0 and len(result[-1][0]) > 0 and result[-1][0][0] not in '-*+0123456789':
            result[-1].append(line)
        else:
            result.append([line])
    return "\n".join(" ".join(multiline) for multiline in result)


def code_langauge(tag, content):
    if len(content) == 0 or content[0] in list(" \n\t"):
        return tag, content
    language = content.split('\n')[0]
    return f'{tag[:-1]} language="{language}">', '\n'.join(content.split('\n')[1:])


def stripper(content):
    return content.strip()

def decorate_with_alternating_tag(content, separator, beg_tag, end_tag, under_tag_func=None, out_tag_func=None, tag_mod=None):
    new_parts = []
    alternate = beg_tag
    parts = list(content.split(separator))
    for i, part in enumerate(parts):
        if alternate == beg_tag and out_tag_func is not None:
            part = out_tag_func(part)
            if tag_mod is not None and i + 1 < len(parts):
                alternate, parts[i + 1] = tag_mod(beg_tag, parts[i + 1])
        elif alternate == end_tag and under_tag_func is not None:
            part = under_tag_func(part)
        new_parts.append(part)
        new_parts.append(alternate)
        alternate = beg_tag if alternate == end_tag else end_tag
    if alternate == end_tag:
        new_parts.append(end_tag)
    return ''.join(new_parts)


def fixed_width(content: str):
    parts = content.split('`')
    if len(parts) <= 2:
        return content
    return decorate_with_alternating_tag(
        content,
        "`",
        "<code>",
        "</code>",
    )


def htmlify(content):
    return decorate_with_alternating_tag(
        content,
        "```",
        "<code>",
        "</code>",
        out_tag_func=fixed_width,
        tag_mod=code_langauge,
    )


class CounterVar:
    def __init__(self):
        self.val = 0

class Counter:

    def __init__(self, variable):
        self.variable = variable

    def __enter__(self):
        self.variable.val += 1

    def __exit__(self, exc_type, exc_value, traceback):
        self.variable.val -= 1
