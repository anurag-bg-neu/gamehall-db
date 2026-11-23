"""End-to-end checks for GameHall. Run with the server already started:

    npm start                              # terminal 1
    .venv/bin/python tools/e2e_test.py     # terminal 2
"""
import json
import os
import sys
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE_URL", "http://localhost:3001")
EXPECTED_FIELDS = {"id", "slug", "name", "game", "role", "power", "description", "avatar_seed"}
results = []


def check(name, condition, detail=""):
    results.append(condition)
    print(f"{'PASS' if condition else 'FAIL'}  {name}" + (f"  ({detail})" if detail and not condition else ""))


def get(path):
    try:
        with urllib.request.urlopen(BASE + path) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def api(path):
    status, body = get(path)
    return status, json.loads(body)


print(f"== API ({BASE})")
status, rows = api("/api/characters")
check("GET /api/characters returns 200", status == 200, status)
check("roster has at least 5 items", len(rows) >= 5, len(rows))
check("every row has all table columns", all(EXPECTED_FIELDS <= set(r) for r in rows))

_, rows = api("/api/characters?search=ZELDA&field=game")
check("search by game is case-insensitive", [r["slug"] for r in rows] == ["link"], rows)
_, rows = api("/api/characters?search=hunter&field=role")
check("search by role finds partial matches", {r["slug"] for r in rows} == {"samus-aran", "aloy"}, rows)
_, rows = api("/api/characters?search=kra&field=name")
check("search by name works", [r["slug"] for r in rows] == ["kratos"], rows)
status, _ = api("/api/characters?search=x&field=password")
check("unknown search field is rejected with 400", status == 400, status)
status, rows = api("/api/characters?search=%27%3B%20DROP%20TABLE%20characters%3B--&field=name")
check("SQL-injection-style search is treated as text", status == 200 and rows == [], (status, rows))
status, row = api("/api/characters/kratos")
check("GET /api/characters/:slug returns the item", status == 200 and row["name"] == "Kratos", status)
status, _ = api("/api/characters/does-not-exist")
check("unknown slug returns 404 from API", status == 404, status)

print("== Pages")
for path, expected in [("/", 200), ("/characters/link", 200), ("/characters/nope", 404), ("/no/such/page", 404)]:
    status, _ = get(path)
    check(f"GET {path} -> {expected}", status == expected, status)

print("== Browser")
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    errors = []
    page.on("console", lambda m: m.type == "error" and errors.append(m.text))
    page.on("pageerror", lambda e: errors.append(str(e)))

    page.goto(BASE + "/")
    page.wait_for_selector("#roster-grid .card")
    check("title is displayed", page.inner_text(".hero h1") == "GAMEHALL")
    count = page.locator(".card").count()
    check("homepage renders cards from the database", count >= 5, count)

    page.select_option("#search-field", "role")
    page.fill("#search-input", "hunter")
    page.click("#search-form button")
    page.wait_for_function("document.querySelector('#roster-status').textContent.includes('hunter')")
    names = page.locator(".card h3").all_inner_texts()
    check("search UI filters the list", sorted(names) == ["Aloy", "Samus Aran"], names)

    page.fill("#search-input", "")
    page.dispatch_event("#search-input", "search")
    page.wait_for_function(f"document.querySelectorAll('.card').length === {count}")
    check("clearing search restores the full list", page.locator(".card").count() == count)

    page.click("a.card[href='/characters/geralt']")
    page.wait_for_selector(".fighter-card")
    text = page.inner_text(".fighter-card")
    check("clicking a card opens its unique URL", page.url.endswith("/characters/geralt"), page.url)
    check("detail view shows all fields",
          all(s in text for s in ["Geralt of Rivia", "The Witcher", "Witcher", "89", "silver swords", "slug: geralt"]))

    check("no browser console errors on list/search/detail", not errors, errors)

    page.goto(BASE + "/characters/nope")
    check("404 page is shown for unknown items", "No fighter found" in page.inner_text("body"))
    browser.close()

passed = sum(results)
print(f"\n{passed}/{len(results)} checks passed")
sys.exit(0 if passed == len(results) else 1)
