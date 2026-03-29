\
from app.core.guardrail import redact_pii
def test_aws():     assert "AKIAIOSFODNN7EXAMPLE" not in redact_pii("key AKIAIOSFODNN7EXAMPLE")
def test_ssn():     assert "123-45-6789" not in redact_pii("SSN 123-45-6789")
def test_ghpat():   assert "ghp_" not in redact_pii("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh")
def test_slack():   assert "xoxb-" not in redact_pii("xoxb-123-abc")
def test_pg():      assert "postgres://" not in redact_pii("postgres://u:p@h/db")
def test_clean():   assert redact_pii("Normal text.") == "Normal text."
def test_privkey(): assert "BEGIN RSA" not in redact_pii("-----BEGIN RSA PRIVATE KEY-----")
def test_cc():      assert "4111111111111111" not in redact_pii("Card: 4111111111111111")
def test_str():     assert isinstance(redact_pii("hi"), str)
def test_multi():
    r = redact_pii("SSN 123-45-6789 key AKIAIOSFODNN7EXAMPLE")
    assert "123-45-6789" not in r and "AKIAIOSFODNN7EXAMPLE" not in r
