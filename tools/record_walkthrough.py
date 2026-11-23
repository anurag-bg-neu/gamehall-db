"""Records the README walkthrough GIF (docs/walkthrough.gif). Run with the server started:

    npm start                                      # terminal 1
    .venv/bin/python tools/record_walkthrough.py   # terminal 2

Part 1 runs real psql (from the postgres Docker image) against DATABASE_URL and replays
its output in a terminal-styled page with the password masked. Part 2 drives the app.
"""
import html
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE = os.environ.get("BASE_URL", "http://localhost:3001")
OUT = ROOT / "docs" / "walkthrough.gif"
SIZE = {"width": 1280, "height": 720}


def database_url():
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("DATABASE_URL="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("DATABASE_URL not found in environment or .env")


def run_psql(url):
    script = "\\pset format wrapped\n\\pset columns 175\nSELECT * FROM characters;\n"
    out = subprocess.run(
        ["docker", "run", "--rm", "-i", "postgres:16-alpine", "psql", url + "?sslmode=require", "-q"],
        input=script, capture_output=True, text=True, check=True,
    )
    return out.stdout.rstrip()


def terminal_page(url, output):
    u = urlparse(url)
    db = u.path.lstrip("/")
    connect = f"PGPASSWORD=******** psql -h {u.hostname} -U {u.username} {db}"
    steps = [
        ("$ ", connect, ""),
        (f"{db}=> ", "\\pset format wrapped", "Output format is wrapped.\n"),
        (f"{db}=> ", "SELECT * FROM characters;", output + "\n"),
    ]
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
      body {{ margin:0; background:#0d1117; color:#c9d1d9; font:11.5px/1.35 Menlo,monospace; }}
      .bar {{ background:#21262d; color:#8b949e; padding:8px 14px; font:12px -apple-system,sans-serif; }}
      .bar b {{ color:#58a6ff; }}
      pre {{ margin:0; padding:12px 14px; white-space:pre; }}
      .p {{ color:#7ee787; }}
    </style></head><body>
      <div class="bar"><b>Terminal</b> &mdash; psql connected to Render PostgreSQL (password hidden)</div>
      <pre id="t"></pre>
      <script>
        const steps = {[[html.escape(a), html.escape(b), html.escape(c)] for a, b, c in steps]!r};
        const t = document.getElementById('t');
        const dec = s => {{ const d = document.createElement('textarea'); d.innerHTML = s; return d.value; }};
        window.play = async () => {{
          for (const [prompt, cmd, out] of steps) {{
            const p = document.createElement('span'); p.className = 'p'; p.textContent = dec(prompt); t.append(p);
            for (const ch of dec(cmd)) {{ t.append(ch); await new Promise(r => setTimeout(r, 28)); }}
            t.append('\\n'); await new Promise(r => setTimeout(r, 500));
            t.append(dec(out)); await new Promise(r => setTimeout(r, 700));
          }}
        }};
      </script></body></html>"""


OVERLAY = """
(() => {
  if (location.protocol === 'file:') return;
  const mount = () => {
    const bar = document.createElement('div');
    bar.id = '__urlbar';
    bar.textContent = location.href;
    bar.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:99999;background:#e8eaed;color:#202124;' +
      'font:13px -apple-system,sans-serif;padding:7px 14px;border-bottom:1px solid #c4c7c5;';
    const cap = document.createElement('div');
    cap.id = '__caption';
    cap.style.cssText = 'position:fixed;bottom:18px;left:50%;transform:translateX(-50%);z-index:99999;' +
      'background:rgba(0,0,0,.82);color:#fff;font:600 15px -apple-system,sans-serif;padding:9px 18px;' +
      'border-radius:6px;max-width:90%;text-align:center;';
    cap.hidden = true;
    document.body.append(bar, cap);
    document.body.style.paddingTop = '34px';
  };
  document.readyState === 'loading' ? document.addEventListener('DOMContentLoaded', mount) : mount();
})();
"""


def caption(page, text):
    page.evaluate("t => { const c = document.getElementById('__caption'); c.textContent = t; c.hidden = false; }", text)


def scroll(page, to, steps=25):
    page.evaluate("""async ([to, steps]) => {
      const from = scrollY;
      for (let i = 1; i <= steps; i++) { scrollTo(0, from + (to - from) * i / steps); await new Promise(r => setTimeout(r, 40)); }
    }""", [to, steps])


def record(term_html, video_dir):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport=SIZE, record_video_dir=video_dir, record_video_size=SIZE)
        ctx.add_init_script(OVERLAY)
        page = ctx.new_page()

        # 1. Table contents straight from Render via psql
        page.goto(term_html.as_uri())
        page.evaluate("play()")
        page.wait_for_timeout(6500)

        # 2. Roster loaded from the database
        page.goto(BASE + "/")
        page.wait_for_selector(".card")
        caption(page, "Vanilla HTML/CSS/JS front end — roster fetched from PostgreSQL")
        page.wait_for_timeout(2000)
        scroll(page, 620)
        page.wait_for_timeout(1800)
        scroll(page, 1150)
        page.wait_for_timeout(1500)

        # 3. The JSON API behind it
        page.goto(BASE + "/api/characters/kratos")
        caption(page, "Express API: GET /api/characters/:slug returns a row from the characters table")
        page.wait_for_timeout(2600)

        # 4. Search by attribute (stretch feature)
        page.goto(BASE + "/")
        page.wait_for_selector(".card")
        scroll(page, 560, 15)
        caption(page, "Stretch feature: search by a specific attribute (role)")
        page.select_option("#search-field", "role")
        page.locator("#search-input").press_sequentially("hunter", delay=110)
        page.wait_for_timeout(400)
        page.click("#search-form button")
        page.wait_for_timeout(2300)
        caption(page, "Search by game — case-insensitive, partial match")
        page.select_option("#search-field", "game")
        page.fill("#search-input", "")
        page.locator("#search-input").press_sequentially("war", delay=110)
        page.click("#search-form button")
        page.wait_for_timeout(2300)

        # 5. Detail views with unique URLs
        caption(page, "Each item has its own page with every database field")
        page.wait_for_timeout(800)
        page.click("a.card[href='/characters/kratos']")
        page.wait_for_selector(".fighter-card")
        caption(page, "Detail view: /characters/kratos")
        page.wait_for_timeout(2800)
        page.goto(BASE + "/characters/samus-aran")
        page.wait_for_selector(".fighter-card")
        caption(page, "Detail view: /characters/samus-aran")
        page.wait_for_timeout(2500)

        # 6. 404
        page.goto(BASE + "/characters/mario")
        caption(page, "Unknown items and routes return a 404 page")
        page.wait_for_timeout(2500)

        video = page.video.path()
        ctx.close()
        browser.close()
        return Path(video)


def to_gif(video):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    OUT.parent.mkdir(exist_ok=True)
    vf = "fps=10,scale=1000:-1:flags=lanczos"
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(video), "-vf",
                    f"{vf},split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4",
                    str(OUT)], check=True)
    shutil.copy(video, OUT.with_suffix(".webm"))


if __name__ == "__main__":
    url = database_url()
    output = run_psql(url)
    with tempfile.TemporaryDirectory() as tmp:
        term = Path(tmp) / "terminal.html"
        term.write_text(terminal_page(url, output))
        video = record(term, tmp)
        to_gif(video)
    print(f"Saved {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.1f} MB) and {OUT.with_suffix('.webm').name}")
