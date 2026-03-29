from spellchecker import SpellChecker
_spell = SpellChecker()
def correct_query(text: str) -> tuple[str, bool]:
    words = text.split()
    corrected, changed = [], False
    for word in words:
        if word.islower() and len(word) >= 4 and word.isalpha():
            fixed = _spell.correction(word)
            if fixed and fixed != word:
                corrected.append(fixed); changed = True; continue
        corrected.append(word)
    return " ".join(corrected), changed
