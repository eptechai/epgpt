import time

from playwright.sync_api import Page, expect


def test_attachment_and_messages(page: Page):
    page.goto("http://127.0.0.1:4181/", wait_until="networkidle")
    expect(page.get_by_role("textbox", name="Message Teragonia...")).to_be_visible()

    # Full Diaglogue
    page.get_by_placeholder("Message Teragonia...").click()
    page.get_by_placeholder("Message Teragonia...").fill("Hi")
    page.get_by_role("button", name="Send", exact=True).click()
    page.wait_for_load_state("networkidle")
    page.wait_for_selector(".stop-gen-button", state="visible")
    page.wait_for_selector(".stop-gen-button", state="hidden")
    assert page.locator("div.message").count() == 2

    # Change configuration for the conversation
    expect(page.get_by_role("button", name="Configurations", exact=True)).to_be_visible()
    page.get_by_role("button", name="Configurations", exact=True).click()
    expect(page.get_by_role("dialog")).to_be_visible()
    page.locator("#input-temperature").fill("0.12")
    page.locator("button.apply-button").click()
    page.get_by_role("button", name="Configurations", exact=True).click()
    expect(page.get_by_role("dialog")).to_be_visible()
    assert page.locator("#input-temperature").input_value() == "0.12"
    page.get_by_role("button", name="Close", exact=True).click()

    # Upload an attachment
    expect(page.get_by_role("button", name="Attachments", exact=True)).to_be_visible()
    page.get_by_role("button", name="Attachments", exact=True).click()
    page.locator("#drawer-example > div.custom-dropzone > input[type=file]").set_input_files("test.pdf")
    page.get_by_role("button", name="Upload", exact=True).click()
    page.wait_for_load_state("networkidle")
    expect(page.get_by_role("status")).to_be_visible()
    page.wait_for_load_state("networkidle")

    # Give some time for indexing
    time.sleep(5)

    expect(page.get_by_role("img", name="processed")).to_be_visible()
    with page.expect_download():
        page.get_by_role("img", name="processed").click()
    page.get_by_role("button", name="Close", exact=True).click()

    # Testing stop button
    page.get_by_placeholder("Message Teragonia...").click()
    page.get_by_placeholder("Message Teragonia...").fill("Hello")
    page.get_by_role("button", name="Send", exact=True).click()
    page.wait_for_load_state("networkidle")
    page.wait_for_selector(".stop-gen-button", state="visible")
    page.wait_for_timeout(2000)
    page.get_by_role("button", name="Stop", exact=True).click()
    page.wait_for_load_state("networkidle")
    assert page.locator("div.message").count() == 4

    # Testing whether the conversation can continue and does not throw Convo. BUSY error
    page.get_by_placeholder("Message Teragonia...").click()
    page.get_by_placeholder("Message Teragonia...").fill("Hi")
    page.get_by_role("button", name="Send", exact=True).click()
    page.wait_for_load_state("networkidle")
    page.wait_for_selector(".stop-gen-button", state="visible")
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Stop", exact=True).click()
    page.wait_for_load_state("networkidle")
    assert page.locator("div.message").count() == 6
