import os
import django
import sys
import time

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'focustube.settings')
django.setup()

from django.contrib.auth.models import User
from playwright.sync_api import sync_playwright

def diagnose_buttons():
    print("=== DIAGNOSING RAZORPAY BUTTON SELECTORS ===")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Log in
        page.goto("http://127.0.0.1:8000/login/")
        page.fill("input[name='username']", "ajay")
        page.fill("input[name='password']", "password123")
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard/")
        
        # Go to pricing and open Razorpay
        page.goto("http://127.0.0.1:8000/pricing/")
        page.click("button[data-plan='pro']")
        
        # Wait for frame
        page.wait_for_selector("iframe.razorpay-checkout-frame")
        frame = page.query_selector("iframe.razorpay-checkout-frame").content_frame()
        time.sleep(2)
        
        # Click Cards
        frame.click("text=Cards", force=True)
        time.sleep(2)
        
        # Print all buttons in the frame
        buttons = frame.query_selector_all("button")
        print(f"\nFound {len(buttons)} button elements inside the Razorpay iframe:")
        for idx, el in enumerate(buttons):
            tag_id = el.get_attribute("id")
            tag_class = el.get_attribute("class")
            tag_text = el.inner_text().strip().replace('\n', ' ')
            print(f"BUTTON [{idx}] ID: '{tag_id}' | Text: '{tag_text}' | Class: '{tag_class}'")
            
        # Print other potential click targets containing 'Pay'
        pay_elements = frame.query_selector_all("*:has-text('Pay')")
        print(f"\nFound {len(pay_elements)} elements containing 'Pay':")
        for idx, el in enumerate(pay_elements[:15]):
            print(f"PAY EL [{idx}] Tag: '{el.evaluate('el => el.tagName')}' | Text: '{el.inner_text().strip().replace('\n', ' ')[:40]}' | Class: '{el.get_attribute('class')}'")
            
        browser.close()

if __name__ == '__main__':
    diagnose_buttons()
