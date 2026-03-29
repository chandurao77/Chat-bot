from app.ingestion.html_parser import parse_html
def test_strips_scripts():
    t,_ = parse_html("<script>alert(1)</script><p>Hi</p>")
    assert "alert" not in t and "Hi" in t
def test_strips_styles():
    t,_ = parse_html("<style>.x{color:red}</style><p>OK</p>")
    assert "color" not in t
def test_h1():  assert "# T" in parse_html("<h1>T</h1>")[0]
def test_h2():  assert "## S" in parse_html("<h2>S</h2>")[0]
def test_table():
    t,_ = parse_html("<table><tr><td>A</td><td>B</td></tr></table>")
    assert "|" in t
def test_code():
    t,_ = parse_html('<pre><code class="language-py">x=1</code></pre>')
    assert "```" in t
def test_links():
    _,links = parse_html('<a href="?pageId=123">L</a>')
    assert "123" in links
def test_empty():
    t,l = parse_html("")
    assert t=="" and l==[]
def test_plain():
    t,_ = parse_html("<p>Simple paragraph.</p>")
    assert "Simple" in t
def test_no_links():
    _,l = parse_html("<p>No links</p>")
    assert l==[]
