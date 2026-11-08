from pathlib import Path

from ingest import chunk_text, load_chunks, read_doc, split_blocks, word_count

TEXT = "First paragraph here.\n\nSecond paragraph here.\n\n```\ncode line 1\n\ncode line 2\n```\n\nLast one."


def test_code_block_with_blank_line_stays_in_one_block():
    blocks = split_blocks(TEXT)
    assert len(blocks) == 4
    assert "code line 1\n\ncode line 2" in blocks[2]


def test_small_chunk_size_gives_more_chunks():
    assert len(chunk_text(TEXT, 5)) > len(chunk_text(TEXT, 100))


def test_no_text_is_lost_and_no_chunk_is_empty():
    chunks = chunk_text(TEXT, 5)
    assert all(c.strip() for c in chunks)
    original_words = " ".join(TEXT.split())
    rejoined = " ".join(" ".join(chunks).split())
    assert rejoined == original_words


def test_long_block_is_split_by_lines():
    long_block = "\n".join(f"line {i} with some words" for i in range(50))
    chunks = chunk_text(long_block, 30)
    assert len(chunks) > 1
    assert all(word_count(c) <= 30 + 5 for c in chunks)


def test_header_is_removed_from_docs():
    assert "Fetched:" in Path("data/docs/compression.md").read_text()
    assert "Fetched:" not in read_doc("data/docs/compression.md")
    chunks = load_chunks(300)
    assert chunks
    assert not any("Fetched:" in c["text"] for c in chunks)
