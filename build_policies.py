#!/usr/bin/env python3
"""Gera páginas .html estáticas e estilizadas a partir dos .md de políticas.

Uso: python build_policies.py
Edite os arquivos .md e rode novamente para atualizar os .html.
"""
import re
from pathlib import Path
import markdown

ROOT = Path(__file__).parent
POLICIES = ROOT / "policies"

# (markdown de origem, html de saída, idioma, título do app)
DOCS = [
    ("renda-facil/privacy-pt.md",   "renda-facil/privacy-pt.html",   "pt-BR", "Renda Fácil"),
    ("bioquiz/privacy-pt.md",       "bioquiz/privacy-pt.html",       "pt-BR", "BioQuiz"),
    ("equilibrium/privacy-en.md",   "equilibrium/privacy-en.html",   "en",    "Equilibrium"),
    ("meus-alugueis/privacy-pt.md", "meus-alugueis/privacy-pt.html", "pt-BR", "Aluguel Fácil"),
]

SHELL = """<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} — {policy_label} — AppSollu</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../../assets/css/style.css" />
  <link rel="stylesheet" href="../../assets/css/doc.css" />
</head>
<body>
  <button id="theme-toggle" class="theme-toggle" aria-label="Alternar tema" title="Alternar tema">
    <span class="theme-toggle__icon">🌙</span>
  </button>

  <header class="doc-hero">
    <div class="doc-hero__inner">
      <a class="doc-back" href="../../index.html">&larr; AppSollu</a>
      <h1 class="doc-hero__title">{heading}</h1>
    </div>
  </header>

  <main class="doc">
    <article class="doc__content">
{body}
    </article>
  </main>

  <footer class="footer">
    <p>&copy; <span id="year"></span> AppSollu. Todos os direitos reservados.</p>
    <p class="footer__links"><a href="../../index.html">Voltar ao início</a></p>
  </footer>

  <script>
    document.getElementById('year').textContent = new Date().getFullYear();
    (function () {{
      var root = document.documentElement;
      var toggle = document.getElementById('theme-toggle');
      var icon = toggle.querySelector('.theme-toggle__icon');
      var saved = localStorage.getItem('theme');
      var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      var theme = saved || (prefersDark ? 'dark' : 'light');
      apply(theme);
      toggle.addEventListener('click', function () {{
        theme = (root.getAttribute('data-theme') === 'dark') ? 'light' : 'dark';
        localStorage.setItem('theme', theme);
        apply(theme);
      }});
      function apply(t) {{
        root.setAttribute('data-theme', t);
        icon.textContent = (t === 'dark') ? '☀️' : '🌙';
      }}
    }})();
  </script>
</body>
</html>
"""


def build():
    md = markdown.Markdown(extensions=["extra", "sane_lists"])
    for src, out, lang, title in DOCS:
        text = (POLICIES / src).read_text(encoding="utf-8")
        md.reset()
        html = md.convert(text)

        # Extrai o primeiro <h1> como título do cabeçalho e remove do corpo.
        heading = title + " — Política de Privacidade"
        m = re.search(r"<h1.*?>(.*?)</h1>", html, re.S)
        if m:
            heading = re.sub(r"<.*?>", "", m.group(1)).strip()
            html = html[:m.start()] + html[m.end():]

        # Indenta o corpo e abre links externos em nova aba.
        html = re.sub(r'(<a\s+href="https?://[^"]+")', r'\1 target="_blank" rel="noopener"', html)
        body = "\n".join("      " + line for line in html.splitlines())

        policy_label = "Privacy Policy" if lang == "en" else "Política de Privacidade"
        page = SHELL.format(lang=lang, title=title, heading=heading, body=body, policy_label=policy_label)
        (POLICIES / out).write_text(page, encoding="utf-8")
        print(f"  {src}  ->  {out}")


if __name__ == "__main__":
    print("Gerando páginas de política:")
    build()
    print("Concluído.")
