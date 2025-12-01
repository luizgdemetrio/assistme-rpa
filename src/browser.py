# src/browser.py
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE_DIR = ".pw-edge-profile"  # pasta com sessão/cookies


def get_playwright_context(headless: bool = False):
    Path(PROFILE_DIR).mkdir(exist_ok=True)
    p = sync_playwright().start()
    browser = p.chromium.launch(channel="msedge", headless=headless, slow_mo=50)
    context = browser.new_context(
        accept_downloads=True,
        viewport={"width": 800, "height": 600},
        # Se quiser persistir storage_state.json em vez de user-data-dir,
        # use context.storage_state(path="storage_state.json") depois do login.
    )
    return p, browser, context
