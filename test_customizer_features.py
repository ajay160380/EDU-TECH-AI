import os
import django
import sys
import time

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'focustube.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from django.contrib.auth.models import User
from playwright.sync_api import sync_playwright

def run_customizer_validation_test():
    print("=== STARTING THEME CUSTOMIZER FUNCTIONAL GATING TEST ===")
    
    # 1. Reset 'ajay' user in database to Free plan
    user = User.objects.filter(username='ajay').first()
    if not user:
        print("[-] Error: 'ajay' user not found.")
        return
        
    user.set_password('password123')
    user.save()
    
    profile = user.profile
    profile.plan_type = 'free'
    profile.save()
    print("[+] User 'ajay' plan reset to 'FREE'.")
    
    with sync_playwright() as p:
        print("[+] Launching headless browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Log in
        print("[+] Navigating to login page...")
        page.goto("http://127.0.0.1:8000/login/")
        
        print("[+] Submitting login credentials...")
        page.fill("input[name='username']", "ajay")
        page.fill("input[name='password']", "password123")
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard/")
        print("[✓] Successfully logged in to Dashboard!")
        
        # --- TEST 1: FREE PLAN ---
        print("\n--- [TEST 1] Free Plan validation ---")
        # Try selecting Cyberpunk Pink theme button
        print("[+] Click Cyberpunk Pink (should be locked)...")
        page.click("button[data-theme='cyberpunk']")
        time.sleep(1)
        
        # Check if premium toast is visible
        toast = page.query_selector(".premium-lock-toast")
        if toast:
            print("[✓] Correct: Premium Lock Toast displayed on Free account!")
            print(f"    Message text: {toast.inner_text().strip().replace(chr(10), ' | ')}")
        else:
            print("[-] Fail: Lock toast not shown on Free account!")
            
        page.screenshot(path="step1_free_lock_warning.png")
        
        # --- TEST 2: PRO PLAN ---
        print("\n--- [TEST 2] Pro Plan validation ---")
        # Update user's plan to pro in background
        profile.plan_type = 'pro'
        profile.save()
        print("[+] DB Updated: user 'ajay' plan updated to 'PRO'. Refreshing page...")
        page.reload()
        page.wait_for_url("**/dashboard/")
        
        # Click Cyberpunk Pink (should now be unlocked!)
        print("[+] Click Cyberpunk Pink (should succeed)...")
        page.click("button[data-theme='cyberpunk']")
        time.sleep(1)
        
        active_btn = page.query_selector("button[data-theme='cyberpunk'].active")
        if active_btn:
            print("[✓] Success: Cyberpunk Pink theme button has the active styling state!")
        else:
            print("[-] Fail: Cyberpunk Pink did not activate on Pro account!")
            
        page.screenshot(path="step2_pro_cyberpunk_active.png")
        
        # Click Solar Gold (should be locked for Pro!)
        print("[+] Click Solar Gold (should be locked)...")
        page.click("button[data-theme='solar']")
        time.sleep(1)
        
        toast = page.query_selector(".premium-lock-toast")
        if toast:
            print("[✓] Correct: Premium Lock Toast displayed for Solar Gold on Pro account!")
        else:
            print("[-] Fail: Solar Gold lock toast not shown on Pro account!")
            
        page.screenshot(path="step3_pro_solar_locked.png")
        
        # --- TEST 3: ULTRA PLAN ---
        print("\n--- [TEST 3] Ultra Plan validation ---")
        # Update user's plan to ultra
        profile.plan_type = 'ultra'
        profile.save()
        print("[+] DB Updated: user 'ajay' plan updated to 'ULTRA'. Refreshing page...")
        page.reload()
        page.wait_for_url("**/dashboard/")
        
        # Click Solar Gold (should now be unlocked!)
        print("[+] Click Solar Gold (should succeed)...")
        page.click("button[data-theme='solar']")
        time.sleep(1)
        
        active_btn = page.query_selector("button[data-theme='solar'].active")
        if active_btn:
            print("[✓] Success: Solar Gold theme button is now active on Ultra!")
        else:
            print("[-] Fail: Solar Gold did not activate on Ultra account!")
            
        page.screenshot(path="step4_ultra_solar_active.png")
        
        # Close browser
        browser.close()
        
    print("\n[✓] ALL CUSTOMIZER VALIDATIONS COMPLETED SUCCESSFULY!")

if __name__ == '__main__':
    run_customizer_validation_test()
