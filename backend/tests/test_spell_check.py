from app.core.spell_check import correct_query
def test_tuple():     assert len(correct_query("test query here")) == 2
def test_correct():
    _, changed = correct_query("what is the deployment process")
    assert changed is False
def test_upper():     assert "JIRA" in correct_query("JIRA deployment")
def test_str():       assert isinstance(correct_query("normal text"), str)
def test_short():     assert correct_query("how do i use it") is not None
