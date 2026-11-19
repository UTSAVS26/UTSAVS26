"""Generates the static hero + stack SVGs (self-contained, look identical in any theme)."""
import os

A = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
FONT = "Segoe UI,Helvetica,Arial,sans-serif"

phrases = ["AI / ML Research Engineer", "Agentic AI & LLM Systems", "Applied GenAI & Document Intelligence", "GPU & AI Infrastructure", "Quantum & Post-Quantum Cryptography"]
dur = 4 * len(phrases)
txt = ""
for i, p in enumerate(phrases):
    a, b = i / len(phrases), (i + 1) / len(phrases)
    kt = f"0;{max(a - .001, 0):.3f};{a + .03:.3f};{b - .03:.3f};{b:.3f};1" if i else f"0;{b - .03:.3f};{b:.3f};1"
    kv = "0;0;1;1;0;0" if i else "1;1;0;0"
    txt += (f'<text x="500" y="165" text-anchor="middle" fill="#24c6dc" font-size="24" font-weight="500" opacity="{1 if i == 0 else 0}">{p.replace("&", "&amp;")}'
            f'<animate attributeName="opacity" dur="{dur}s" repeatCount="indefinite" keyTimes="{kt}" values="{kv}"/></text>\n')

orbits = ""
for r, d, col in ((70, 9, "#24c6dc"), (105, 14, "#7c5cff"), (140, 21, "#ff8a5c")):
    orbits += f'<ellipse cx="500" cy="115" rx="{r * 3.2:.0f}" ry="{r * .55:.0f}" fill="none" stroke="{col}" stroke-opacity=".12"/>\n'
    orbits += (f'<circle r="4" fill="{col}"><animateMotion dur="{d}s" repeatCount="indefinite" '
               f'path="M{500 - r * 3.2:.0f},115 a{r * 3.2:.0f},{r * .55:.0f} 0 1,0 {r * 6.4:.0f},0 a{r * 3.2:.0f},{r * .55:.0f} 0 1,0 -{r * 6.4:.0f},0"/></circle>\n')

hero = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="260" viewBox="0 0 1000 260" font-family="{FONT}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f0c29"/><stop offset=".55" stop-color="#1b1b4b"/><stop offset="1" stop-color="#0e3a52"/></linearGradient>
<linearGradient id="nm" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#9fe9f5"/></linearGradient>
</defs>
<rect width="1000" height="260" rx="20" fill="url(#bg)"/>
{orbits}<text x="500" y="108" text-anchor="middle" fill="url(#nm)" font-size="62" font-weight="800" letter-spacing="1">Utsav Singhal</text>
{txt}<text x="500" y="212" text-anchor="middle" fill="#8b98b8" font-size="14" letter-spacing="3">M3AI  ·  B.TECH AI &amp; ML  ·  VIPS-TC</text>
</svg>
'''
open(os.path.join(A, "hero.svg"), "w", encoding="utf8", newline="\n").write(hero)

groups = [
    ("LANGUAGES", "#3776AB", ["Python", "SQL", "C / C++", "Java"]),
    ("MACHINE LEARNING", "#EE4C2C", ["Machine Learning", "Deep Learning", "NLP", "Feature Engineering", "Statistical Analysis"]),
    ("ML FRAMEWORKS", "#FF6F00", ["PyTorch", "TensorFlow", "Keras", "scikit-learn", "Hugging Face"]),
    ("GENERATIVE AI", "#7c5cff", ["LLMs", "RAG", "Prompt Engineering", "OpenAI", "Azure OpenAI"]),
    ("AGENTIC AI", "#e879f9", ["AI Agents", "Tool Calling", "MCP", "Multi-Agent Systems", "LangChain", "Agent Evaluation"]),
    ("DOCUMENT INTELLIGENCE & DATA", "#24c6dc", ["AWS Textract", "pandas", "NumPy", "OpenPyXL", "ETL Pipelines"]),
    ("GPU & AI INFRASTRUCTURE", "#76b900", ["NVIDIA GPUs", "CUDA", "Triton", "PyTorch GPU Programming", "GPU Memory Optimization"]),
    ("QUANTUM & CRYPTOGRAPHY", "#ff8a5c", ["Qiskit", "Quantum Algorithms", "ECC", "Post-Quantum Cryptography", "NIST Standards"]),
    ("ENGINEERING", "#f5c542", ["Docker", "AWS", "FastAPI", "Git", "GitHub", "Jupyter"]),
]
W, y, out = 840, 0, []
for title, col, items in groups:
    out.append(f'<text x="0" y="{y + 12}" fill="{col}" font-size="11" font-weight="700" letter-spacing="2">{title.replace("&", "&amp;")}</text>')
    y += 22
    x = 0
    for name in items:
        w = 46 + len(name) * 7.8
        if x + w > W:
            x, y = 0, y + 38
        out.append(f'<g transform="translate({x:.0f},{y})"><rect width="{w:.0f}" height="30" rx="15" fill="#14172e" stroke="{col}" stroke-opacity=".55"/>'
                   f'<circle cx="16" cy="15" r="4.5" fill="{col}"/><text x="30" y="19.5" fill="#e6edf3" font-size="13" font-weight="600">{name.replace("&", "&amp;")}</text></g>')
        x += w + 10
    y += 48
H = y - 6 + 40
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W + 40}" height="{H}" viewBox="0 0 {W + 40} {H}" font-family="{FONT}">'
       f'<rect width="{W + 40}" height="{H}" rx="16" fill="#0f0c29" stroke="#2a3558"/>'
       f'<g transform="translate(20,20)">' + "".join(out) + "</g></svg>\n")
open(os.path.join(A, "stack.svg"), "w", encoding="utf8", newline="\n").write(svg)
