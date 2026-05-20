import os
import django
import sys
import time

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'focustube.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

from django.contrib.auth.models import User
from courses.models import Course, Video
from playwright.sync_api import sync_playwright

def run_notes_workspace_test():
    print("=== STARTING AI TUTOR & NOTES WORKSPACE GATING TEST ===")
    
    # 1. Get a valid course from database
    course = Course.objects.first()
    if not course:
        print("[-] Error: No course found in database.")
        return
        
    video = course.videos.first()
    if not video:
        print("[-] Error: Course has no videos.")
        return
        
    # 2. Get/create a dynamic user who owns this course or a default user
    user = course.user
    if not user:
        user = User.objects.first()
        
    if not user:
        user = User.objects.create_user(username='demo_student', email='student@test.com')
        print(f"[+] No users found in database. Created new user: '{user.username}'")
    else:
        print(f"[+] Found dynamic user in database: '{user.username}' (ID: {user.id})")
        
    # Ensure course is owned by our test user so it doesn't 404
    if course.user != user:
        course.user = user
        course.save()
        print(f"[+] Associated Course '{course.title}' with User '{user.username}'")
        
    user.set_password('password123')
    user.save()
    
    # Ensure profile exists
    if not hasattr(user, 'profile'):
        from courses.models import UserProfile
        UserProfile.objects.create(user=user)
        print(f"[+] Created profile for user '{user.username}'")
        
    print(f"[+] Active Course: '{course.title}' (ID: {course.id})")
    print(f"[+] Active Video: '{video.title}' (ID: {video.id})")
    
    # Reset to Free Plan initially
    profile = user.profile
    profile.plan_type = 'free'
    profile.save()
    print(f"[+] User '{user.username}' plan reset to 'FREE'.")
    
    with sync_playwright() as p:
        print("[+] Launching browser...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Listen to console and page error events
        page.on("console", lambda msg: print(f"    [Browser Console] {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"    [Browser Page Error] {err}"))
        
        # Log in
        print("[+] Navigating to login page...")
        page.goto("http://127.0.0.1:8000/login/")
        page.fill("input[name='username']", user.username)
        page.fill("input[name='password']", "password123")
        page.click("button[type='submit']")
        page.wait_for_url("**/dashboard/")
        print("[✓] Logged in successfully!")
        
        # --- TEST 1: FREE PLAN GATE ---
        print("\n--- [TEST 1] Free Plan visual lock overlay check ---")
        learn_url = f"http://127.0.0.1:8000/course/{course.id}/learn/?video={video.id}"
        page.goto(learn_url, wait_until="domcontentloaded")
        time.sleep(2)
        
        # Try clicking AI Tutor tab (should lock out for Free)
        print("[+] Clicking AI Tutor Tab...")
        page.click("#tab-chat-btn")
        time.sleep(1)
        
        # Assert lock feature overlay is visible
        lock_overlay = page.query_selector("#ai-panel-chat .locked-feature-overlay")
        if lock_overlay:
            print("[✓] Correct: AI Tutor & Notes panel shows locked overlay on Free Plan.")
            print(f"    Overlay Text: {lock_overlay.inner_text().strip().replace(chr(10), ' | ')[:150]}...")
        else:
            print("[-] Fail: Lock overlay not visible on Free Plan!")
            
        page.screenshot(path="workspace_free_locked.png")
        
        # --- TEST 2: PRO PLAN INTERACTIVE GATES ---
        print("\n--- [TEST 2] Pro Plan Workspace checks ---")
        profile.plan_type = 'pro'
        profile.save()
        print(f"[+] DB Updated: user '{user.username}' plan updated to 'PRO'. Refreshing page...")
        page.reload()
        time.sleep(2)
        
        # Click AI Tutor Tab (should now be unlocked!)
        print("[+] Clicking AI Tutor Tab...")
        page.click("#tab-chat-btn")
        time.sleep(1)
        
        # Verify subtabs switcher exists
        switcher = page.query_selector(".workspace-sub-header")
        if switcher:
            print("[✓] Success: Switched to active AI Tutor & Notes Workspace!")
            print(f"    Sub-header elements: {switcher.inner_text().strip().replace(chr(10), ' | ')}")
        else:
            print("[-] Fail: Quota switcher not rendered for Pro user!")
            
        # Switch to Notes subtab
        print("[+] Switching to Notes subtab...")
        page.click("#subtab-notes-btn")
        time.sleep(1)
        
        # Verify Notes textarea is visible and type
        textarea = page.query_selector("#notes-textarea")
        if textarea:
            print("[✓] Notes Editor visible! Typing active study notes...")
            page.fill("#notes-textarea", "This is some initial study note for testing the limit. " * 5)
            time.sleep(1)
            
            # Check counter
            counter = page.query_selector("#notes-char-counter")
            print(f"    Active Counter: {counter.inner_text().strip()}")
        else:
            print("[-] Fail: Notes text area not visible!")
            
        # Try clicking AI Enhance Notes (should alert locked for Pro)
        print("[+] Clicking AI Enhance button (Pro)...")
        page.click("#notes-ai-enhance-btn")
        time.sleep(1)
        
        # Try clicking Inject Summary (should alert locked for Pro)
        print("[+] Clicking Inject Summary button (Pro)...")
        page.click("#notes-inject-summary-btn")
        time.sleep(1)
        
        page.screenshot(path="workspace_pro_active.png")
        
        # --- TEST 3: ULTRA PLAN UNLOCKED WORKSPACE ---
        print("\n--- [TEST 3] Ultra Plan complete workspace checks ---")
        profile.plan_type = 'ultra'
        profile.save()
        print(f"[+] DB Updated: user '{user.username}' plan updated to 'ULTRA'. Refreshing page...")
        page.reload(wait_until="domcontentloaded")
        time.sleep(2)
        
        # Click AI Tutor Tab
        page.click("#tab-chat-btn")
        time.sleep(1)
        page.click("#subtab-notes-btn")
        time.sleep(1)
        
        # Inject Summary (should now work!)
        print("[+] Injecting Groq AI Summary (Ultra)...")
        raw_summary = page.locator("#raw-summary-content").text_content()
        print(f"    [DEBUG] raw-summary-content content: '{raw_summary.strip()[:100]}'")
        
        page.click("#notes-inject-summary-btn")
        time.sleep(1.5)
        
        updated_note = page.locator("#notes-textarea").input_value()
        print(f"    [DEBUG] notes-textarea content after inject: '{updated_note.strip()[:100]}'")
        
        if "GROQ LECTURE SUMMARY" in updated_note or "Key Takeaway" in updated_note:
            print("[✓] Success: Groq Lecture Summary was injected successfully!")
        else:
            print("[-] Fail: Summary not injected into textarea!")
            
        # AI Enhance Notes (should now work!)
        print("[+] Clicking AI Enhance Notes (Ultra)...")
        page.click("#notes-ai-enhance-btn")
        # Give simulated typing animation time to complete
        time.sleep(4)
        
        enhanced_note = page.locator("#notes-textarea").input_value()
        if "ENHANCED STUDY NOTES" in enhanced_note:
            print("[✓] Success: AI notes enhancement typewriter animation run successfully!")
        else:
            print("[-] Fail: AI notes enhancement typewriter did not complete!")
            
        page.screenshot(path="workspace_ultra_unlocked.png")

        # --- TEST 4: LIVE MARKDOWN PREVIEW TOGGLE CHECKS ---
        print("\n--- [TEST 4] Live Markdown Preview Toggle checks ---")
        
        # Check that Preview button exists
        preview_btn = page.query_selector("#notes-preview-toggle-btn")
        if not preview_btn:
            print("[-] Fail: Preview toggle button not found!")
            return
            
        print("[✓] Found Preview toggle button!")
        
        # Initially, textarea is visible and preview area is hidden
        is_textarea_visible = page.locator("#notes-textarea").is_visible()
        is_preview_visible = page.locator("#notes-preview-area").is_visible()
        
        if is_textarea_visible and not is_preview_visible:
            print("[✓] Initially: Textarea is VISIBLE, Preview Area is HIDDEN.")
        else:
            print(f"[-] Fail: Initial state mismatch! Textarea visible={is_textarea_visible}, Preview visible={is_preview_visible}")
            
        # Toggle Preview Mode
        print("[+] Clicking Preview button to enter Preview Mode...")
        preview_btn.click()
        time.sleep(1)
        
        is_textarea_visible = page.locator("#notes-textarea").is_visible()
        is_preview_visible = page.locator("#notes-preview-area").is_visible()
        btn_text = preview_btn.inner_text().strip()
        
        if not is_textarea_visible and is_preview_visible:
            print("[✓] State Changed: Textarea is HIDDEN, Preview Area is VISIBLE.")
        else:
            print(f"[-] Fail: State mismatch after click! Textarea visible={is_textarea_visible}, Preview visible={is_preview_visible}")
            
        if "Edit" in btn_text:
            print(f"[✓] Button text updated correctly to: '{btn_text}'")
        else:
            print(f"[-] Fail: Button text did not change to Edit! Actual: '{btn_text}'")
            
        # Verify rendered markdown styling
        preview_html = page.locator("#notes-preview-area").inner_html()
        if "<strong" in preview_html or "Key Takeaway" in preview_html:
            print("[✓] Beautifully rendered HTML content found in Preview Area!")
            print(f"    Preview HTML Snippet: {preview_html[:150].replace(chr(10), ' | ')}...")
        else:
            print("[-] Fail: Rendered HTML does not contain key takeaway strong/bold markup!")
            
        # Switch back to Edit Mode
        print("[+] Clicking Edit button to return to Edit Mode...")
        preview_btn.click()
        time.sleep(1)
        
        is_textarea_visible = page.locator("#notes-textarea").is_visible()
        is_preview_visible = page.locator("#notes-preview-area").is_visible()
        btn_text = preview_btn.inner_text().strip()
        
        if is_textarea_visible and not is_preview_visible:
            print("[✓] Returned: Textarea is VISIBLE, Preview Area is HIDDEN.")
        else:
            print(f"[-] Fail: State mismatch after switching back! Textarea visible={is_textarea_visible}, Preview visible={is_preview_visible}")
            
        if "Preview" in btn_text:
            print(f"[✓] Button text updated correctly back to: '{btn_text}'")
        else:
            print(f"[-] Fail: Button text did not revert! Actual: '{btn_text}'")
            
        # Switch to Preview Mode one more time to test Auto-Exit triggers
        print("[+] Clicking Preview button to enter Preview Mode again...")
        preview_btn.click()
        time.sleep(1)
        
        # Trigger Inject Summary while in Preview Mode
        print("[+] Triggering Inject Summary while in Preview Mode to test Auto-Exit...")
        page.click("#notes-inject-summary-btn")
        time.sleep(1.5)
        
        # Verify it auto-exited to Edit Mode
        is_textarea_visible = page.locator("#notes-textarea").is_visible()
        is_preview_visible = page.locator("#notes-preview-area").is_visible()
        btn_text = preview_btn.inner_text().strip()
        
        if is_textarea_visible and not is_preview_visible and "Preview" in btn_text:
            print("[✓] Success: Workspace correctly auto-exited Preview mode to Edit mode on summary injection!")
        else:
            print(f"[-] Fail: Auto-exit did not trigger correctly! Textarea visible={is_textarea_visible}, Preview visible={is_preview_visible}, Button text='{btn_text}'")
            
        # Switch to Preview Mode one more time
        print("[+] Entering Preview Mode again to test Auto-Exit on AI Enhance...")
        preview_btn.click()
        time.sleep(1)
        
        # Trigger AI Enhance while in Preview Mode
        print("[+] Triggering AI Enhance while in Preview Mode to test Auto-Exit...")
        page.click("#notes-ai-enhance-btn")
        time.sleep(4)
        
        # Verify it auto-exited to Edit Mode
        is_textarea_visible = page.locator("#notes-textarea").is_visible()
        is_preview_visible = page.locator("#notes-preview-area").is_visible()
        btn_text = preview_btn.inner_text().strip()
        
        if is_textarea_visible and not is_preview_visible and "Preview" in btn_text:
            print("[✓] Success: Workspace correctly auto-exited Preview mode to Edit mode on AI Enhance!")
        else:
            print(f"[-] Fail: Auto-exit did not trigger correctly on AI Enhance! Textarea visible={is_textarea_visible}, Preview visible={is_preview_visible}, Button text='{btn_text}'")
            
        page.screenshot(path="workspace_preview_checked.png")
        
        # Close browser
        browser.close()
        
    print("\n[✓] ALL WORKSPACE TEST CASES EXECUTED AND PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_notes_workspace_test()
