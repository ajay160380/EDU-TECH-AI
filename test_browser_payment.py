import os
import django
import sys
import time

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'focustube.settings')
django.setup()

from django.contrib.auth.models import User
from playwright.sync_api import sync_playwright

def run_browser_payment_test():
    print("=== STARTING BROWSER PAYMENT FLOW TEST ===")
    
    # 1. Reset 'ajay' user in database for clean test
    user = User.objects.filter(username='ajay').first()
    if not user:
        print("[-] Error: 'ajay' user not found.")
        return
        
    user.set_password('password123')
    user.save()
    
    profile = user.profile
    profile.plan_type = 'free'
    profile.save()
    print("[+] User 'ajay' password set to 'password123', plan reset to 'free'.")
    
    # 2. Start Playwright
    with sync_playwright() as p:
        print("[+] Launching headless browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Go to login page
        print("[+] Navigating to login page...")
        page.goto("http://127.0.0.1:8000/login/")
        page.screenshot(path="step1_login_page.png")
        
        # Fill credentials
        print("[+] Logging in...")
        page.fill("input[name='username']", "ajay")
        page.fill("input[name='password']", "password123")
        page.click("button[type='submit']")
        
        # Wait for redirect to dashboard
        page.wait_for_url("**/dashboard/")
        print("[+] Successfully logged in to Dashboard!")
        page.screenshot(path="step2_dashboard.png")
        
        # Go to pricing
        print("[+] Navigating to pricing page...")
        page.goto("http://127.0.0.1:8000/pricing/")
        page.screenshot(path="step3_pricing_page.png")
        
        # Click "Upgrade to Pro"
        print("[+] Clicking 'Upgrade to Pro'...")
        page.click("button[data-plan='pro']")
        
        # Wait for the Razorpay iframe to appear in DOM
        print("[+] Waiting for Razorpay Checkout Iframe...")
        page.wait_for_selector("iframe.razorpay-checkout-frame")
        
        # Select Razorpay iframe
        checkout_frame_element = page.query_selector("iframe.razorpay-checkout-frame")
        frame = checkout_frame_element.content_frame()
        print("[+] Razorpay Iframe loaded successfully!")
        
        # Give Razorpay animations a brief moment to settle
        time.sleep(3)
        
        # 3. Handle the "Contact details" overlay if it appears
        print("[+] Checking if 'Contact details' overlay is present...")
        try:
            frame.wait_for_selector("input[name='contact']", timeout=5000)
            print("[+] Contact details overlay found! Typing official Razorpay test mobile sequentially...")
            # Focus on input and type character-by-character to trigger internal framework state
            contact_input = frame.locator("input[name='contact']")
            contact_input.focus()
            contact_input.press_sequentially("7905398965", delay=150)
            
            time.sleep(2)
            # Take screenshot to verify input value
            page.screenshot(path="diagnose_contact_typed.png")
            
            # Press Enter to submit the form - 100% robust and bypasses click issues!
            contact_input.press("Enter")
            print("[+] Sent 'Enter' keystroke to Contact input form.")
            
            time.sleep(1)
            try:
                frame.click("button:has-text('Continue')", force=True, timeout=2000)
                print("[+] Clicked 'Continue' as fallback.")
            except Exception:
                pass
            time.sleep(3)
        except Exception as e:
            print("[+] Contact details overlay not present or already prefilled.")
            
        # 4. Select Cards
        print("[+] Selecting Card payment method inside iframe...")
        frame.click("text=Cards", force=True)
        
        # Type the first digit of the card number to trigger the Visa brand-detection dynamic UI
        card_num_input = frame.locator("input[name='card.number']")
        card_num_input.focus()
        card_num_input.press_sequentially("4", delay=100)
        
        # Give Razorpay brand-detection UI rendering and focus transitions a moment to settle
        time.sleep(1.5)
        
        # Re-locate the card input and type the remaining digits of the domestic Visa Credit Card
        card_num_input = frame.locator("input[name='card.number']")
        card_num_input.focus()
        card_num_input.press_sequentially("718609108204366", delay=100)
        time.sleep(0.5)
        
        # Sequentially type Expiry to trigger framework formatting (adding the '/')
        card_expiry_input = frame.locator("input[name='card.expiry']")
        card_expiry_input.focus()
        card_expiry_input.press_sequentially("1230", delay=100)
        time.sleep(0.5)
        
        # Sequentially type CVV
        card_cvv_input = frame.locator("input[name='card.cvv']")
        card_cvv_input.focus()
        card_cvv_input.press_sequentially("111", delay=100)
        time.sleep(0.5)
        
        # Screenshot of filled card details
        page.screenshot(path="step4_card_details_filled.png")
        
        # Click Pay/Continue button inside iframe
        print("[+] Clicking payment submission button inside iframe...")
        time.sleep(2)
        try:
            frame.click("button.bg-cta:has-text('Continue'):visible", force=True, timeout=5000)
            print("[+] Clicked 'Continue' button successfully.")
        except Exception:
            try:
                frame.click("button:has-text('Pay')", force=True, timeout=3000)
                print("[+] Clicked 'Pay' button successfully.")
            except Exception:
                frame.click("button:has-text('Continue')", force=True)
                print("[+] Clicked fallback 'Continue' button.")
        
        # Check if card tokenization consent screen appears ("Save your card for future payments?")
        print("[+] Checking for card tokenization consent screen...")
        try:
            frame.click("button:has-text('Maybe later')", force=True, timeout=5000)
            print("[+] Clicked 'Maybe later' on card tokenization consent screen.")
        except Exception:
            print("[+] Tokenization consent screen not shown or already skipped.")
        
        # Wait for Razorpay mock bank OTP/Verification screen inside iframe
        print("[+] Waiting for verification/OTP screen inside iframe...")
        time.sleep(3)
        page.screenshot(path="step5_payment_processing.png")
        print("[+] Captured initial screenshot of OTP screen to step5_payment_processing.png")
        
        try:
            # Check if it's the Axis Bank OTP input screen
            print("[+] Probing for simulated Axis Bank OTP screen...")
            frame.wait_for_selector("input[placeholder='Enter OTP']", timeout=10000)
            print("[✓] Axis Bank OTP screen detected! Entering mock OTP '123456'...")
            
            otp_input = frame.locator("input[placeholder='Enter OTP']")
            otp_input.focus()
            otp_input.fill("123456")
            time.sleep(1)
            
            # Press Enter on OTP input to submit form
            print("[+] Pressing 'Enter' on OTP input field...")
            otp_input.press("Enter")
            time.sleep(2)
            
            # Click visible Continue button(s) in the frame as robust fallback
            print("[+] Clicking visible 'Continue' button(s)...")
            continue_buttons = frame.locator("button:has-text('Continue')")
            count = continue_buttons.count()
            print(f"[+] Found {count} 'Continue' buttons inside Razorpay iframe.")
            clicked_any = False
            for i in range(count):
                btn = continue_buttons.nth(i)
                if btn.is_visible():
                    print(f"[+] Clicking visible 'Continue' button at index {i}...")
                    btn.click(force=True)
                    clicked_any = True
            
            if not clicked_any:
                print("[-] No visible 'Continue' button found, trying standard click...")
                frame.click("button:has-text('Continue')", force=True)
                
            print("[✓] Axis Bank OTP submission logic completed.")
            
        except Exception as e:
            print(f"[+] Axis Bank OTP handler encountered exception: {e}. Falling back to default 'Success' button...")
            try:
                frame.wait_for_selector("button:has-text('Success')", timeout=20000)
                print("[+] Clicking 'Success' on the mock bank screen inside iframe...")
                frame.click("button:has-text('Success')", force=True)
                print("[✓] Mock bank Success button clicked successfully.")
            except Exception as e2:
                print("[-] Timeout waiting for bank screen options.")
                page.screenshot(path="error_otp_timeout.png")
                print("[-] Saved error screenshot to 'error_otp_timeout.png'")
                try:
                    buttons = frame.query_selector_all("button")
                    print(f"[-] Available buttons in OTP frame: {[b.inner_text().strip() for b in buttons]}")
                except Exception:
                    pass
                raise e2
        
        # Wait for redirection back to Django Dashboard
        print("[+] Waiting for redirection to Django Dashboard...")
        try:
            page.wait_for_url("**/dashboard/", timeout=45000)
            print("[✓] Redirection complete!")
        except Exception as e:
            print("[-] Redirection failed or timed out. Capturing diagnostic screenshot...")
            page.screenshot(path="post_otp_redirection_failed.png")
            print("[-] Saved diagnostic screenshot to 'post_otp_redirection_failed.png'")
            raise e
        
        time.sleep(3)  # Wait for UI layout and Toast messages to appear
        
        # Save final upgraded dashboard screenshot
        page.screenshot(path="payment_success.png")
        print("[✓] Saved upgraded dashboard screenshot to 'payment_success.png'")
        
        browser.close()
        
    # Check updated database plan status
    user.profile.refresh_from_db()
    print("\n================ DATABASE PLAN VERIFICATION ================")
    print(f"[✓] Final Database Plan for 'ajay': '{user.profile.plan_type.upper()}'")
    print(f"[✓] Subscription Expiry Date: {user.profile.subscription_end_date}")
    print("============================================================\n")

if __name__ == '__main__':
    run_browser_payment_test()
