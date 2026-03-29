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
