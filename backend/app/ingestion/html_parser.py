\
from bs4 import BeautifulSoup
import re
from typing import Tuple, List
def parse_html(html: str, base_url: str="") -> Tuple[str, List[str]]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style"]): tag.decompose()
    for lvl in range(1,7):
        for h in soup.find_all(f"h{lvl}"):
            h.replace_with(f"\n{'#'*lvl} {h.get_text(strip=True)}\n")
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td","th"])]
            rows.append("| "+" | ".join(cells)+" |")
        table.replace_with("\n"+"\n".join(rows)+"\n")
    for code in soup.find_all(["code","pre"]):
        lang = (code.get("class") or [""])[0].replace("language-","")
        code.replace_with(f"\n```{lang}\n{code.get_text()}\n```\n")
    links = []
    for a in soup.find_all("a", href=True):
        m = re.search(r'pageId=(\d+)', a["href"])
        if m: links.append(m.group(1))
    text = re.sub(r'\n{3,}', '\n\n', soup.get_text(separator="\n")).strip()
    return text, links
