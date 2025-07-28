# app/merge.py
import re, collections
from pathlib import Path
from jinja2 import Template

TPL = Template((Path(__file__).parent / "templates" / "default.tsx.j2").read_text())

IMPORT_RE  = re.compile(r"^import\s+([\s\S]+?)\s+from\s+['\"]([^'\"]+)['\"];?$",
                        re.MULTILINE)
WRAPPER_RE = re.compile(
    r"""export\s+(?:const|function)\s+[^{=]+?=\s*(?:\(\)\s*=>\s*)?
        \{[^{}]*?return\s*\(\s*(?P<body>[\s\S]+?)\);?\s*\}""",
    re.MULTILINE | re.VERBOSE,
)

def _strip_imports(code: str, nova_syms: set[str]) -> str:
    """Remove import lines; collect Nova‑React symbols for consolidation."""
    def repl(m):
        spec, mod = m.groups()

        # we only intercept @visa/nova‑react
        if mod != '@visa/nova-react':
            return m.group(0)     # keep the whole line

        # split `import Foo, { Bar, Baz }`
        default_sym = spec.split("{")[0].strip().rstrip(",")
        if default_sym:
            nova_syms.add(default_sym)
        if "{" in spec:
            named = re.findall(r"{([^}]+)}", spec)[0]
            nova_syms.update(s.strip() for s in named.split(","))
        return ""                 # strip the Nova line

    return IMPORT_RE.sub(repl, code).strip()

def _unwrap(code: str) -> str:
    m = WRAPPER_RE.search(code)
    return (m.group("body") if m else code).strip()

def merge_variants(snippets: list[str], export_name: str) -> str:
    nova_syms: set[str] = set()
    bodies     = []

    for snip in snippets:
        bodies.append(_unwrap(_strip_imports(snip, nova_syms)))

    import_block = ", ".join(sorted(nova_syms))
    body_block   = "\n\n".join(bodies)

    return TPL.render(
        import_block = import_block,
        export_name  = export_name or "Generated",
        body_block   = body_block,
    )
