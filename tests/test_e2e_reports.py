"""
Playwright E2E tests for the /reports page.
Uses pytest-playwright fixtures to match the existing test style.
"""
import pytest
import requests

SERVER_URL = "http://127.0.0.1:8000"


def _register_and_get_token(username: str, email: str, password: str = "Pass123!") -> str:
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
    headers = {"Authorization": f"Bearer {token}"}
    for op in operations:
        requests.post(f"{SERVER_URL}/calculations/", json=op, headers=headers)


def _inject_token_and_go(page, token: str, path: str):
    page.goto(f"{SERVER_URL}/login")
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.goto(f"{SERVER_URL}{path}")


def test_reports_redirects_when_not_logged_in(page):
    """Visiting /reports without a token must redirect to /login."""
    page.goto(f"{SERVER_URL}/reports")
    page.wait_for_url("**/login", timeout=6000)
    assert "/login" in page.url


def test_reports_page_loads_for_authenticated_user(page):
    """An authenticated user must reach the reports page."""
    token = _register_and_get_token("e2e_rpt1", "e2e_rpt1@test.com")
    _inject_token_and_go(page, token, "/reports")
    page.wait_for_selector("#total-count", timeout=6000)
    assert "/reports" in page.url


def test_reports_shows_zero_for_new_user(page):
    """A user with no calculations should see total = 0."""
    token = _register_and_get_token("e2e_rpt2", "e2e_rpt2@test.com")
    _inject_token_and_go(page, token, "/reports")
    page.wait_for_selector("#total-count", timeout=6000)
    assert page.text_content("#total-count").strip() == "0"


def test_reports_total_updates_after_calculations(page):
    """After adding 3 calculations, total-count must show 3."""
    token = _register_and_get_token("e2e_rpt3", "e2e_rpt3@test.com")
    _add_calculations(token, [
        {"a": 2, "b": 3, "type": "Add"},
        {"a": 10, "b": 2, "type": "Divide"},
        {"a": 4, "b": 5, "type": "Multiply"},
    ])
    _inject_token_and_go(page, token, "/reports")
    page.wait_for_selector("#total-count", timeout=6000)
    assert page.text_content("#total-count").strip() == "3"


def test_reports_recent_list_renders(page):
    """Recent calculations list must show one item per calculation."""
    token = _register_and_get_token("e2e_rpt4", "e2e_rpt4@test.com")
    _add_calculations(token, [
        {"a": 1, "b": 1, "type": "Add"},
        {"a": 2, "b": 2, "type": "Multiply"},
    ])
    _inject_token_and_go(page, token, "/reports")
    page.wait_for_selector(".recent-item", timeout=6000)
    assert page.locator(".recent-item").count() == 2


def test_reports_logout_redirects_to_login(page):
    """Clicking Logout must redirect to /login."""
    token = _register_and_get_token("e2e_rpt5", "e2e_rpt5@test.com")
    _inject_token_and_go(page, token, "/reports")
    page.wait_for_selector("#logout-btn", timeout=6000)
    page.click("#logout-btn")
    page.wait_for_url("**/login", timeout=6000)
    assert "/login" in page.url