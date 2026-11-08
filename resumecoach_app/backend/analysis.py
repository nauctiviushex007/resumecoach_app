"""Resume vs job-posting analysis. Pure Python - easy to read and unit-test."""
import re

STOP = set("a an the and or of to in for with on at by from as is are be will you your we our us this that it their they have has can must should may not but if into about across using use work working experience years year strong ability skills skill team teams role responsibilities requirements preferred plus including etc also such more other new well within who what when where than all any each".split())
SKILLS = set("python java javascript typescript sql react node docker kubernetes aws azure gcp git linux api rest graphql html css c++ c# go rust django flask fastapi spring mongodb postgresql mysql redis agile scrum ci/cd jenkins terraform pandas numpy tensorflow pytorch excel tableau figma communication leadership testing".split())
WEAK = ["responsible for", "worked on", "helped with", "helped", "assisted", "duties included", "tasked with", "involved in"]
NUM = re.compile(r"\d[\d,.]*%?")


def tokens(text):
    return [t.lower().strip(".-") for t in re.findall(r"[A-Za-z][A-Za-z+#./\-]*", text)]


def norm(t):
    return t[:-1] if len(t) > 3 and t.endswith("s") and not t.endswith("ss") else t


def keywords(job, limit=25):
    freq = {}
    for t in (norm(t) for t in tokens(job)):
        if t not in STOP and len(t) > 2:
            freq[t] = freq.get(t, 0) + 1
    ranked = [k for k, c in sorted(freq.items(), key=lambda x: -x[1]) if k in SKILLS or c >= 2]
    return ranked[:limit]


def get_bullets(resume):
    return [re.sub(r"^[\s\-•*·▪]+", "", l).strip() for l in resume.splitlines()
            if re.match(r"^\s*[\-•*·▪]", l) and len(l.strip()) > 15]


def analyze(resume, job):
    rset = {norm(t) for t in tokens(resume)}
    kws = keywords(job)
    matched = [k for k in kws if k in rset]
    missing = [k for k in kws if k not in rset]
    bl = get_bullets(resume)
    weak = [b for b in bl if any(w in b.lower()[:30] for w in WEAK)]
    nometric = [b for b in bl if not NUM.search(b)]
    words = len(resume.split())
    checks = [
        ("Email address found", bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", resume))),
        ("Phone number found", bool(re.search(r"\+?\d[\d\s\-()]{8,}", resume))),
        ("Uses bullet points (lines starting with - or •)", len(bl) >= 3),
        (f"Bullets with measurable results ({len(bl) - len(nometric)}/{len(bl)})", bool(bl) and len(nometric) <= len(bl) / 2),
        (f"No weak openers like 'responsible for' ({len(weak)} found)", not weak),
        (f"Length: {words} words (about 250-800 is typical)", 250 <= words <= 800),
    ]
    return {"score": round(100 * len(matched) / len(kws)) if kws else None,
            "matched": matched, "missing": missing, "checks": checks, "bullets": bl}


def new_numbers(original, rewritten):
    """Numbers in the rewrite that were NOT in the original (possible invention)."""
    have = set(NUM.findall(original))
    return [n for n in NUM.findall(rewritten) if n not in have]
