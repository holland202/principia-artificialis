import json, sys
from playwright.sync_api import sync_playwright
html, graph = sys.argv[1], sys.argv[2]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); errs=[]; reqs=[]
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
    pg.on("request", lambda r: reqs.append(r.url) if not r.url.startswith(("file:","data:","blob:")) else None)
    pg.goto("file://"+html)
    s0 = pg.text_content("#status")
    pg.click("#sample"); d = (pg.text_content("#detail") or "")[:80]
    pg.set_input_files("#file", graph); pg.wait_for_timeout(400)
    out = {"status_on_load": s0, "detail_after_sample": d, "status_after_injection_file": pg.text_content("#status"),
           "injected_script_ran": pg.evaluate("window.__pwn ?? null"),
           "injected_img_elements": pg.evaluate("document.querySelectorAll('img').length"),
           "title_rendered_as_text": "<img src=x" in (pg.text_content("body") or ""),
           "page_errors": errs, "external_requests": reqs}
    print(json.dumps(out, indent=1)); b.close()
