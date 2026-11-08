from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "data" / "docs"


def read_doc(path):
    # Remove the metadata header (Source, Fetched, Licence, Note) up to the first '---' line
    lines = Path(path).read_text().splitlines()
    if "---" in lines[:10]:
        lines = lines[lines.index("---") + 1:]
    return "\n".join(lines).strip()


def split_blocks(text):
    # Split on blank lines, but keep fenced code blocks (```) in one piece
    blocks, current, in_code = [], [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            current.append(line)
        elif line.strip() == "" and not in_code:
            if current:
                blocks.append("\n".join(current))
                current = []
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def word_count(text):
    return len(text.split())


def split_long_block(block, chunk_words):
    # A block that is longer than one chunk is cut at line boundaries
    pieces, current, size = [], [], 0
    for line in block.splitlines():
        n = word_count(line)
        if current and size + n > chunk_words:
            pieces.append("\n".join(current))
            current, size = [], 0
        current.append(line)
        size += n
    if current:
        pieces.append("\n".join(current))
    return pieces


def chunk_text(text, chunk_words):
    # Pack whole blocks into chunks of at most about chunk_words words
    chunks, current, size = [], [], 0
    for block in split_blocks(text):
        n = word_count(block)
        if n > chunk_words:
            if current:
                chunks.append("\n\n".join(current))
                current, size = [], 0
            chunks.extend(split_long_block(block, chunk_words))
            continue
        if current and size + n > chunk_words:
            chunks.append("\n\n".join(current))
            current, size = [], 0
        current.append(block)
        size += n
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def load_chunks(chunk_words, docs_dir=DOCS_DIR):
    chunks = []
    for path in sorted(Path(docs_dir).glob("*.md")):
        for i, text in enumerate(chunk_text(read_doc(path), chunk_words)):
            chunks.append({"id": f"{path.stem}#{i}", "source": path.name, "text": text})
    return chunks
