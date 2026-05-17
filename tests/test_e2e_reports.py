"""
Playwright E2E tests for the /reports page.
The real server is started automatically by the start_server
fixture in conftest.py.
"""
import requests
from playwright.sync_api import sync_playwright

SERVER_URL = "http://127.0.0.1:8000"


def _register_and_get_token(username: str, email: str, password: str = "Pass123!") -> str:
    """Register via API and return a valid JWT token."""
    requests.post(f"{SERVER_URL}/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
    })
    resp = requests.post(f"{SERVER_URL}/auth/login", json={
        "username": username,
        "password": password,
    })
    return resp.json()["access_token"]


def _add_calculations(token: str, operations: list):
    """Add calculations directly via API."""
    headers = {"Authorization": f"Bearer {token}"}
    for op in operations:
        requests.post(f"{SERVER_URL}/calculations/", json=op, headers=headers)


def _inject_token_and_go(page, token: str, path: str):
    """Put the JWT into localStorage then navigate to path."""
    page.goto(f"{SERVER_URL}/login")
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.goto(f"{SERVER_URL}{path}")


def test_reports_redirects_when_not_logged_in():
    """Visiting /reports without a token must redirect to /login."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{SERVER_URL}/reports")
        page.wait_for_url("**/login", timeout=6000)
        assert "/login" in page.url
        browser.close()


def test_reports_page_loads_for_authenticated_user():
    """An authenticated user must reach the reports page."""
    token = _register_and_get_token("e2e_rpt1", "e2e_rpt1@test.com")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        _inject_token_and_go(page, token, "/reports")
        page.wait_for_selector("#total-count", timeout=6000)
        assert "/reports" in page.url
        browser.close()


def test_reports_shows_zero_for_new_user():
    """A user with no calculations should see total = 0."""
    token = _register_and_get_token("e2e_rpt2", "e2e_rpt2@test.com")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        _inject_token_and_go(page, token, "/reports")
        page.wait_for_selector("#total-count", timeout=6000)
        assert page.text_content("#total-count").strip() == "0"
        browser.close()


def test_reports_total_updates_after_calculations():
    """After adding 3 calculations, total-count must show 3."""
    token = _register_and_get_token("e2e_rpt3", "e2e_rpt3@test.com")
    _add_calculations(token, [
        {"a": 2, "b": 3, "type": "Add"},
        {"a": 10, "b": 2, "type": "Divide"},
        {"a": 4, "b": 5, "type": "Multiply"},
    ])
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        _inject_token_and_go(page, token, "/reports")
        page.wait_for_selector("#total-count", timeout=6000)
        assert page.text_content("#total-count").strip() == "3"
        browser.close()


def test_reports_recent_list_renders():
    """Recent calculations list must show one item per calculation."""
    token = _register_and_get_token("e2e_rpt4", "e2e_rpt4@test.com")
    _add_calculations(token, [
        {"a": 1, "b": 1, "type": "Add"},
        {"a": 2, "b": 2, "type": "Multiply"},
    ])
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        _inject_token_and_go(page, token, "/reports")
        page.wait_for_selector(".recent-item", timeout=6000)
        assert page.locator(".recent-item").count() == 2
        browser.close()


def test_reports_logout_redirects_to_login():
    """Clicking Logout must redirect to /login."""
    token = _register_and_get_token("e2e_rpt5", "e2e_rpt5@test.com")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        _inject_token_and_go(page, token, "/reports")
        page.wait_for_selector("#logout-btn", timeout=6000)
        page.click("#logout-btn")
        page.wait_for_url("**/login", timeout=6000)
        assert "/login" in page.url
        browser.close()