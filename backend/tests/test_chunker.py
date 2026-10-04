from app.ingestion.chunker import split_text
def test_empty():          assert split_text("") == []
def test_list():           assert isinstance(split_text("Hello."), list)
def test_single():         assert len(split_text("Hi world. "*10, chunk_size=200)) >= 1
def test_multiple():       assert len(split_text("A sentence. "*100, chunk_size=50, overlap=10)) > 1
def test_short_single():
    c = split_text("Short text.", chunk_size=512)
    assert len(c)==1 and c[0]=="Short text."
def test_content():        assert "keyword" in " ".join(split_text("Important keyword here. Another."))
def test_overlap():        assert len(split_text("Word "*200, chunk_size=50, overlap=10)) > 1
def test_size():
    for c in split_text("word "*1000, chunk_size=100, overlap=10)[:-1]:
        assert len(c.split()) <= 110
def test_newlines():       assert len(split_text("L1.\nL2.\nL3.", chunk_size=512)) >= 1
def test_large():          assert len(split_text("Fox jumps. "*500, chunk_size=100, overlap=20)) > 4

def test_no_punctuation_respects_size():
    chunks = split_text("word " * 200, chunk_size=50, overlap=10)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 50 for c in chunks)
def test_long_sentence_is_split():
    chunks = split_text(" ".join(f"w{i}" for i in range(300)) + ".", chunk_size=100, overlap=0)
    assert len(chunks) == 3 and all(len(c.split()) <= 100 for c in chunks)
def test_all_words_covered():
    words = [f"w{i}" for i in range(250)]
    out = " ".join(split_text(" ".join(words), chunk_size=60, overlap=10)).split()
    assert set(words) <= set(out)
def test_overlap_shared():
    a, b = split_text(" ".join(f"w{i}" for i in range(120)), chunk_size=100, overlap=10)[:2]
    assert a.split()[-10:] == b.split()[:10]
def test_no_trailing_duplicate_chunk():
    chunks = split_text("one two three four five six", chunk_size=3, overlap=1)
    assert chunks[-1] != chunks[-2]
def test_bad_chunk_size():
    import pytest
    with pytest.raises(ValueError): split_text("x", chunk_size=0)
