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