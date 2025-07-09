print("🔄 Starting Google Login Automation Script (Multi-Approach Version)...")
print("📦 Loading required modules...")

import time
import random
import pyautogui
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL = os.getenv("EMAIL", "your_email@gmail.com")
PASSWORD = os.getenv("PASSWORD", "your_password")

# Generate random project name
def generate_random_project_name():
    """Generate a random project name"""
    adjectives = ["awesome", "stellar", "dynamic", "innovative", "smart", "rapid", "efficient", "robust", "secure", "modern"]
    nouns = ["project", "app", "system", "platform", "service", "tool", "solution", "framework", "engine", "portal"]
    numbers = random.randint(100, 999)
    return f"{random.choice(adjectives)}-{random.choice(nouns)}-{numbers}"

PROJECT_NAME = generate_random_project_name()

def human_typing(element, text):
    """Simulate human-like typing"""
    for char in text:
        delay = random.uniform(0.08, 0.22)
        element.send_keys(char)
        time.sleep(delay)

def human_mouse_move_to(element):
    """Simulate human-like mouse movement to an element"""
    try:
        # Scroll element into view first
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(random.uniform(0.5, 1.0))
        
        # Get element location and size
        location = element.location_once_scrolled_into_view
        size = element.size
        
        # Calculate center coordinates with some randomness
        x = location['x'] + size['width'] / 2 + random.randint(-10, 10)
        y = location['y'] + size['height'] / 2 + random.randint(-10, 10)
        
        # Move to the element
        pyautogui.moveTo(x, y, duration=random.uniform(0.6, 1.3))
        time.sleep(random.uniform(0.3, 1.0))
    except Exception as e:
        print(f"Warning: Could not move mouse to element: {e}")
        pass

def dismiss_overlays(driver):
    """Try to dismiss any overlays or modals that might be blocking interactions"""
    try:
        # Look for common overlay patterns
        overlay_selectors = [
            ".cdk-overlay-backdrop",
            ".mat-overlay-backdrop", 
            ".modal-backdrop",
            "[role='dialog']",
            ".overlay",
            ".popup"
        ]
        
        for selector in overlay_selectors:
            try:
                overlay = driver.find_element(By.CSS_SELECTOR, selector)
                if overlay.is_displayed():
                    print(f"🔄 Found overlay with selector: {selector}, trying to dismiss...")
                    # Try pressing Escape key
                    pyautogui.press('escape')
                    time.sleep(random.uniform(0.5, 1.0))
                    print("✅ Overlay dismissed with Escape key")
                    return True
            except:
                continue
        
        return False
        
    except Exception as e:
        print(f"⚠️ Error dismissing overlays: {e}")
        return False

def smart_click(driver, element, method="auto"):
    """Intelligently click an element with multiple fallback methods"""
    try:
        # First, try to dismiss any overlays
        dismiss_overlays(driver)
        
        # Scroll to element
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(random.uniform(0.5, 1.0))
        
        if method == "auto" or method == "js":
            # Try JavaScript click first (bypasses most overlays)
            try:
                driver.execute_script("arguments[0].click();", element)
                print("✅ Element clicked with JavaScript")
                return True
            except Exception as js_error:
                if method == "js":
                    print(f"⚠️ JavaScript click failed: {js_error}")
                    return False
        
        if method == "auto" or method == "regular":
            # Try regular click
            try:
                human_mouse_move_to(element)
                element.click()
                print("✅ Element clicked with regular click")
                return True
            except Exception as regular_error:
                if method == "regular":
                    print(f"⚠️ Regular click failed: {regular_error}")
                    return False
        
        return False
        
    except Exception as e:
        print(f"⚠️ Smart click failed: {e}")
        return False

def create_driver_webdriver_manager():
    """Create driver using webdriver-manager"""
    try:
        print("🔄 Trying webdriver-manager approach...")
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ webdriver-manager approach successful!")
        return driver
    except Exception as e:
        print(f"❌ webdriver-manager approach failed: {e}")
        return None

def create_driver_undetected():
    """Create driver using undetected-chromedriver"""
    try:
        print("🔄 Trying undetected-chromedriver approach...")
        import undetected_chromedriver as uc
        
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = uc.Chrome(options=options, headless=False, version_main=None)
        print("✅ undetected-chromedriver approach successful!")
        return driver
    except Exception as e:
        print(f"❌ undetected-chromedriver approach failed: {e}")
        return None

# Import common selenium modules
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    print("✅ Selenium modules loaded")
except ImportError as e:
    print(f"❌ Error importing selenium modules: {e}")
    exit(1)

print("✅ All modules loaded successfully!")

# Try different approaches to create the driver
driver = None

# Approach 1: webdriver-manager (usually more reliable for version compatibility)
driver = create_driver_webdriver_manager()

# Approach 2: undetected-chromedriver (if webdriver-manager fails)
if driver is None:
    driver = create_driver_undetected()

# If both approaches fail, exit
if driver is None:
    print("❌ Failed to create Chrome driver with any approach")
    print("💡 Possible solutions:")
    print("1. Update Chrome browser to the latest version")
    print("2. Run: pip install --upgrade selenium webdriver-manager undetected-chromedriver")
    print("3. Clear Chrome cache and restart")
    print("4. Check your internet connection")
    exit(1)

# Set window size for consistency
driver.set_window_size(1920, 1080)

try:
    # Check if credentials are set
    if EMAIL == "your_email@gmail.com" or PASSWORD == "your_password":
        print("❌ Error: Please set your EMAIL and PASSWORD in environment variables or update the script")
        print("You can create a .env file with:")
        print("EMAIL=your_email@gmail.com")
        print("PASSWORD=your_password")
        exit(1)
    
    print("📧 Using email:", EMAIL)
    print("📝 Using randomly generated project name:", PROJECT_NAME)
    
    # Step 1: Go to login page
    print("🌐 Navigating to Google login page...")
    driver.get("https://accounts.google.com/signin/v2/identifier")

    wait = WebDriverWait(driver, 20)

    # Step 2: Type email
    print("📝 Entering email...")
    try:
        email_input = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
        human_mouse_move_to(email_input)
        email_input.click()
        time.sleep(random.uniform(0.5, 1.0))
        email_input.clear()
        human_typing(email_input, EMAIL)
    except TimeoutException:
        print("❌ Could not find email input field")
        raise

    # Click Next button
    print("➡️ Clicking Next button...")
    try:
        next_btn = wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
        human_mouse_move_to(next_btn)
        next_btn.click()
    except TimeoutException:
        print("❌ Could not find or click Next button")
        raise

    time.sleep(random.uniform(3.0, 5.0))

    # Step 3: Type password
    print("🔒 Entering password...")
    try:
        password_input = wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))
        human_mouse_move_to(password_input)
        password_input.click()
        time.sleep(random.uniform(0.5, 1.0))
        password_input.clear()
        human_typing(password_input, PASSWORD)
    except TimeoutException:
        print("❌ Could not find password input field")
        raise

    # Click Password Next button
    print("➡️ Clicking Password Next button...")
    try:
        pass_btn = wait.until(EC.element_to_be_clickable((By.ID, "passwordNext")))
        human_mouse_move_to(pass_btn)
        pass_btn.click()
    except TimeoutException:
        print("❌ Could not find or click Password Next button")
        raise

    # Step 4: Navigate to cloud console
    print("☁️ Navigating to Google Cloud Console...")
    time.sleep(random.uniform(5.0, 8.0))
    driver.get("https://console.cloud.google.com")

    print("✅ Login attempt completed successfully!")
    print("🔍 Waiting 15 seconds to observe the result...")

    time.sleep(15)  # Wait and observe the result

    # Step 5: Click new project button
    print("🆕 Clicking new project button...")
    try:
        # Try multiple selectors for the project button
        selectors = [
            "#ocb-platform-bar > cfc-platform-bar > div > div.cfc-platform-bar-left > div > div > div > pcc-platform-bar-purview-switcher > pcc-purview-switcher > cfc-switcher-button > button",
            "pcc-purview-switcher cfc-switcher-button button",
            "button[aria-label*='project']",
            "cfc-switcher-button button"
        ]
        
        project_btn = None
        for selector in selectors:
            try:
                project_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"✅ Found project button with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if project_btn is None:
            raise Exception("Could not find project button with any selector")
        
        # First, try scrolling to element and regular click
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", project_btn)
            time.sleep(random.uniform(1.0, 2.0))
            human_mouse_move_to(project_btn)
            project_btn.click()
            print("✅ New project button clicked successfully!")
        except Exception as click_error:
            print(f"⚠️ Regular click failed: {click_error}")
            print("🔄 Trying JavaScript click...")
            # Fallback to JavaScript click
            driver.execute_script("arguments[0].click();", project_btn)
            print("✅ New project button clicked with JavaScript!")
            
        time.sleep(random.uniform(2.0, 4.0))
        
        # Step 6: Click "New Project" button in the modal
        print("🆕 Clicking 'New Project' button in modal...")
        try:
            new_project_btn_xpath = "//*[@id='purview-picker-modal-action-bar']/mat-toolbar/div[3]/div/div/div[1]/div/button[2]"
            new_project_btn = wait.until(EC.element_to_be_clickable((By.XPATH, new_project_btn_xpath)))
            
            # Try regular click first
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", new_project_btn)
                time.sleep(random.uniform(1.0, 2.0))
                human_mouse_move_to(new_project_btn)
                new_project_btn.click()
                print("✅ 'New Project' button clicked successfully!")
            except Exception as modal_click_error:
                print(f"⚠️ Regular click failed: {modal_click_error}")
                print("🔄 Trying JavaScript click...")
                # Fallback to JavaScript click
                driver.execute_script("arguments[0].click();", new_project_btn)
                print("✅ 'New Project' button clicked with JavaScript!")
                
            time.sleep(random.uniform(2.0, 4.0))
            
            # Step 7: Fill project name
            print("📝 Filling project name...")
            try:
                # Try multiple selectors for project name input
                name_selectors = [
                    "#p6ntest-name-input",
                    "input[id='p6ntest-name-input']",
                    "input[matinput][cfcfocusandselectoninit]",
                    "input[name='projectId']",
                    "input[placeholder*='project']",
                    "input[aria-label*='project']",
                    "input[formcontrolname*='project']",
                    "input[type='text']"
                ]
                
                project_name_input = None
                for selector in name_selectors:
                    try:
                        project_name_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        print(f"✅ Found project name input with selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if project_name_input is None:
                    print("⚠️ Could not find project name input, trying alternative approach...")
                    # Try to find any visible text input
                    text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                    for input_elem in text_inputs:
                        if input_elem.is_displayed() and input_elem.is_enabled():
                            project_name_input = input_elem
                            break
                
                if project_name_input:
                    # Make sure the element is visible and clickable
                    driver.execute_script("arguments[0].scrollIntoView(true);", project_name_input)
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    # Click to focus
                    human_mouse_move_to(project_name_input)
                    project_name_input.click()
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    # Clear any existing text using multiple methods
                    project_name_input.clear()
                    project_name_input.send_keys(Keys.CONTROL + "a")  # Select all
                    project_name_input.send_keys(Keys.DELETE)  # Delete
                    time.sleep(random.uniform(0.3, 0.7))
                    
                    # Type the project name
                    human_typing(project_name_input, PROJECT_NAME)
                    print("✅ Project name filled successfully!")
                    time.sleep(random.uniform(1.0, 2.0))
                else:
                    print("❌ Could not find project name input field")
                    
            except Exception as name_error:
                print(f"❌ Error filling project name: {name_error}")
            
            # Step 8: Click create button
            print("🚀 Clicking create button...")
            try:
                create_btn_xpath = "/html/body/div[1]/div[3]/div[3]/div/pan-shell/pcc-shell/cfc-panel-container/div/div/cfc-panel/div/div/div[3]/cfc-panel-container/div/div/cfc-panel/div/div/cfc-panel-container/div/div/cfc-panel/div/div/cfc-panel-container/div/div/cfc-panel[2]/div/div/central-page-area/div/div/pcc-content-viewport/div/div/ng2-router-root/div/cfc-router-outlet/div/ng-component/cfc-single-panel-layout/cfc-panel-container/div/div/cfc-panel/div/div/div/cfc-panel-body/cfc-virtual-viewport/div[1]/div/proj-creation-form/form/button[1]/span[2]"
                
                # Also try alternative selectors
                create_selectors = [
                    create_btn_xpath,
                    "button[type='submit']",
                    "button:contains('Create')",
                    "button:contains('CREATE')",
                    "form button:first-child"
                ]
                
                create_btn = None
                for selector in create_selectors:
                    try:
                        if selector == create_btn_xpath:
                            create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            create_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        print(f"✅ Found create button with selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if create_btn:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView(true);", create_btn)
                        time.sleep(random.uniform(1.0, 2.0))
                        human_mouse_move_to(create_btn)
                        create_btn.click()
                        print("✅ Create button clicked successfully!")
                    except Exception as create_click_error:
                        print(f"⚠️ Regular click failed: {create_click_error}")
                        print("🔄 Trying JavaScript click...")
                        driver.execute_script("arguments[0].click();", create_btn)
                        print("✅ Create button clicked with JavaScript!")
                        
                    time.sleep(random.uniform(3.0, 5.0))
                    print("✅ Project creation initiated!")
                    
                    # Step 9: Wait for project creation to complete and select the project
                    print("⏳ Waiting for project creation to complete...")
                    time.sleep(random.uniform(15.0, 20.0))  # Wait longer for project to be created
                    
                    print("🔍 Selecting the newly created project...")
                    
                    # Function to open project picker
                    def open_project_picker():
                        picker_opened = False
                        
                        # Method 1: Try keyboard shortcut first (Ctrl+O)
                        print("⌨️ Trying keyboard shortcut (Ctrl+O)...")
                        pyautogui.hotkey('ctrl', 'o')
                        time.sleep(random.uniform(3.0, 4.0))
                        
                        # Check if picker opened by looking for modal or dropdown
                        try:
                            # Look for project picker modal or dropdown
                            picker_modal = driver.find_element(By.CSS_SELECTOR, "[role='dialog'], .cdk-overlay-container, .mat-select-panel")
                            if picker_modal and picker_modal.is_displayed():
                                print("✅ Project picker opened with keyboard shortcut!")
                                picker_opened = True
                        except:
                            pass
                        
                        # Method 2: If keyboard shortcut didn't work, try clicking the project picker button
                        if not picker_opened:
                            print("⚠️ Keyboard shortcut didn't work, trying button click...")
                            
                            project_picker_selectors = [
                                "#ocb-platform-bar > cfc-platform-bar > div > div.cfc-platform-bar-left > div > div > div > pcc-platform-bar-purview-switcher > pcc-purview-switcher > cfc-switcher-button > button > span.mdc-button__label > span > span",
                                "#ocb-platform-bar > cfc-platform-bar > div > div.cfc-platform-bar-left > div > div > div > pcc-platform-bar-purview-switcher > pcc-purview-switcher > cfc-switcher-button > button",
                                "pcc-purview-switcher cfc-switcher-button button",
                                "cfc-switcher-button button",
                                "[aria-label*='project']",
                                "[aria-label*='Project']"
                            ]
                            
                            picker_btn = None
                            for selector in project_picker_selectors:
                                try:
                                    picker_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                                    print(f"✅ Found project picker button with selector: {selector}")
                                    break
                                except TimeoutException:
                                    continue
                            
                            if picker_btn:
                                try:
                                    driver.execute_script("arguments[0].scrollIntoView(true);", picker_btn)
                                    time.sleep(random.uniform(1.0, 2.0))
                                    human_mouse_move_to(picker_btn)
                                    picker_btn.click()
                                    print("✅ Project picker button clicked!")
                                    time.sleep(random.uniform(3.0, 4.0))
                                    picker_opened = True
                                    
                                except Exception as picker_click_error:
                                    print(f"⚠️ Regular click failed: {picker_click_error}")
                                    print("🔄 Trying JavaScript click...")
                                    driver.execute_script("arguments[0].click();", picker_btn)
                                    print("✅ Project picker opened with JavaScript!")
                                    time.sleep(random.uniform(3.0, 4.0))
                                    picker_opened = True
                        
                        return picker_opened
                    
                    # Function to find and select project
                    def select_project():
                        print(f"🔍 Looking for project: {PROJECT_NAME}")
                        
                        # Try multiple approaches to find the project
                        project_selectors = [
                            f"//span[contains(text(), '{PROJECT_NAME}')]",
                            f"//div[contains(text(), '{PROJECT_NAME}')]",
                            f"//td[contains(text(), '{PROJECT_NAME}')]",
                            f"//li[contains(text(), '{PROJECT_NAME}')]",
                            f"//button[contains(text(), '{PROJECT_NAME}')]",
                            f"//*[contains(text(), '{PROJECT_NAME}')]"
                        ]
                        
                        project_found = False
                        
                        # Try to find project elements
                        for selector in project_selectors:
                            try:
                                project_elements = driver.find_elements(By.XPATH, selector)
                                for project_element in project_elements:
                                    if project_element.is_displayed() and project_element.is_enabled():
                                        try:
                                            driver.execute_script("arguments[0].scrollIntoView(true);", project_element)
                                            time.sleep(random.uniform(0.5, 1.0))
                                            human_mouse_move_to(project_element)
                                            project_element.click()
                                            print(f"✅ Successfully selected project: {PROJECT_NAME}")
                                            project_found = True
                                            break
                                        except Exception as click_error:
                                            print(f"⚠️ Click failed for element: {click_error}")
                                            continue
                                
                                if project_found:
                                    break
                                    
                            except Exception as selector_error:
                                print(f"⚠️ Selector failed: {selector_error}")
                                continue
                        
                        return project_found
                    
                    # Try to open project picker and select project
                    try:
                        # First attempt
                        picker_opened = open_project_picker()
                        
                        if picker_opened:
                            project_found = select_project()
                            
                            if not project_found:
                                print("⚠️ Project not found in first attempt, waiting and trying again...")
                                time.sleep(random.uniform(5.0, 8.0))
                                
                                # Second attempt - maybe the project list needs to refresh
                                picker_opened = open_project_picker()
                                if picker_opened:
                                    project_found = select_project()
                                    
                                    if not project_found:
                                        print("⚠️ Project still not found, trying to refresh the page...")
                                        # Try refreshing the page and looking for the project
                                        driver.refresh()
                                        time.sleep(random.uniform(8.0, 12.0))
                                        
                                        # Third attempt after refresh
                                        picker_opened = open_project_picker()
                                        if picker_opened:
                                            project_found = select_project()
                            
                            if project_found:
                                print("✅ Project selection completed successfully!")
                                time.sleep(random.uniform(2.0, 3.0))
                                
                                # Step 10: Search for Gmail API and enable it
                                print("📧 Searching for Gmail API to enable...")
                                try:
                                    gmail_api_found = False
                                    
                                    # Method 1: Try to find and click search box first
                                    print("🔍 Looking for search box...")
                                    search_box_selectors = [
                                        "input[placeholder*='Search']",
                                        "input[aria-label*='Search']",
                                        "input[type='search']",
                                        "#search-input",
                                        "[data-testid*='search']",
                                        "input[placeholder*='search']",
                                        "pcc-platform-bar-search input",
                                        ".search-input",
                                        "[role='searchbox']"
                                    ]
                                    
                                    search_box = None
                                    for selector in search_box_selectors:
                                        try:
                                            search_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                            for search_element in search_elements:
                                                if search_element.is_displayed() and search_element.is_enabled():
                                                    search_box = search_element
                                                    print(f"✅ Found search box with selector: {selector}")
                                                    break
                                            if search_box:
                                                break
                                        except Exception:
                                            continue
                                    
                                    if search_box:
                                        # Click search box and type gmail
                                        try:
                                            # Use smart click to handle overlays
                                            if smart_click(driver, search_box, "auto"):
                                                time.sleep(random.uniform(0.5, 1.0))
                                                
                                                # Clear and type gmail
                                                search_box.clear()
                                                time.sleep(random.uniform(0.3, 0.5))
                                                search_box.send_keys("gmail")
                                                time.sleep(random.uniform(2.0, 4.0))  # Wait longer for dropdown to appear
                                                
                                                print("✅ Typed 'gmail' in search box, waiting for dropdown...")
                                            else:
                                                print("⚠️ Could not click search box with smart click")
                                                raise Exception("Smart click failed")
                                            
                                        except Exception as search_click_error:
                                            print(f"⚠️ Search box interaction failed: {search_click_error}")
                                            print("🔄 Trying alternative search approach...")
                                            # Try typing directly without clicking
                                            try:
                                                # Focus on the page first
                                                pyautogui.click(driver.get_window_size()['width']//2, driver.get_window_size()['height']//2)
                                                time.sleep(random.uniform(0.5, 1.0))
                                                pyautogui.typewrite('gmail')
                                                time.sleep(random.uniform(2.0, 4.0))
                                                print("✅ Typed 'gmail' directly")
                                            except Exception as type_error:
                                                print(f"⚠️ Direct typing also failed: {type_error}")
                                    
                                    # Method 2: Enhanced keyboard shortcut approach
                                    if not search_box:
                                        print("🔍 No search box found, trying enhanced keyboard shortcuts...")
                                        
                                        # Focus on the page first by clicking in the center
                                        try:
                                            center_x = driver.get_window_size()['width'] // 2
                                            center_y = driver.get_window_size()['height'] // 2
                                            pyautogui.click(center_x, center_y)
                                            time.sleep(random.uniform(0.5, 1.0))
                                            print("✅ Focused on page center")
                                        except Exception as focus_error:
                                            print(f"⚠️ Could not focus on page: {focus_error}")
                                        
                                        # Try different keyboard shortcuts with improved timing
                                        shortcuts = [
                                            ('/', 'Forward slash search'),
                                            ('ctrl+k', 'Ctrl+K search'), 
                                            ('ctrl+f', 'Ctrl+F find'),
                                            ('ctrl+shift+p', 'Command palette'),
                                            ('alt+s', 'Alt+S search')
                                        ]
                                        
                                        shortcut_success = False
                                        for shortcut, description in shortcuts:
                                            try:
                                                print(f"⌨️ Trying {description}: {shortcut}")
                                                
                                                if shortcut == '/':
                                                    pyautogui.press('/')
                                                elif shortcut == 'ctrl+k':
                                                    pyautogui.hotkey('ctrl', 'k')
                                                elif shortcut == 'ctrl+f':
                                                    pyautogui.hotkey('ctrl', 'f')
                                                elif shortcut == 'ctrl+shift+p':
                                                    pyautogui.hotkey('ctrl', 'shift', 'p')
                                                elif shortcut == 'alt+s':
                                                    pyautogui.hotkey('alt', 's')
                                                
                                                time.sleep(random.uniform(1.5, 2.5))
                                                
                                                # Clear any existing text and type gmail
                                                pyautogui.hotkey('ctrl', 'a')  # Select all
                                                time.sleep(0.2)
                                                pyautogui.press('delete')  # Clear
                                                time.sleep(0.3)
                                                pyautogui.typewrite('gmail api', interval=0.1)
                                                time.sleep(random.uniform(3.0, 5.0))  # Wait longer for search results
                                                
                                                print(f"✅ Typed 'gmail api' using {description}")
                                                shortcut_success = True
                                                break
                                                
                                            except Exception as shortcut_error:
                                                print(f"⚠️ Shortcut {shortcut} failed: {shortcut_error}")
                                                continue
                                        
                                        if shortcut_success:
                                            print("✅ Successfully triggered search with keyboard shortcut")
                                        else:
                                            print("⚠️ All keyboard shortcuts failed, trying direct navigation...")
                                    
                                    # Method 3: Navigate directly to APIs & Services
                                    print("🔍 Trying to navigate to APIs & Services...")
                                    try:
                                        # Look for "APIs & Services" in the navigation
                                        api_nav_selectors = [
                                            "//span[contains(text(), 'APIs & Services')]",
                                            "//a[contains(text(), 'APIs & Services')]",
                                            "//div[contains(text(), 'APIs & Services')]",
                                            "//*[contains(text(), 'API')]",
                                            "//span[contains(text(), 'Library')]",
                                            "//a[contains(text(), 'Library')]"
                                        ]
                                        
                                        api_nav_found = False
                                        for selector in api_nav_selectors:
                                            try:
                                                api_elements = driver.find_elements(By.XPATH, selector)
                                                for api_element in api_elements:
                                                    if api_element.is_displayed() and api_element.is_enabled():
                                                        try:
                                                            driver.execute_script("arguments[0].scrollIntoView(true);", api_element)
                                                            time.sleep(random.uniform(1.0, 2.0))
                                                            human_mouse_move_to(api_element)
                                                            api_element.click()
                                                            print("✅ Navigated to APIs & Services!")
                                                            api_nav_found = True
                                                            time.sleep(random.uniform(3.0, 5.0))
                                                            break
                                                        except Exception:
                                                            continue
                                                if api_nav_found:
                                                    break
                                            except Exception:
                                                continue
                                        
                                        if api_nav_found:
                                            # Now look for Library or Enable APIs
                                            print("🔍 Looking for Library or Enable APIs...")
                                            library_selectors = [
                                                "//span[contains(text(), 'Library')]",
                                                "//a[contains(text(), 'Library')]",
                                                "//div[contains(text(), 'Library')]",
                                                "//span[contains(text(), 'Enable')]",
                                                "//a[contains(text(), 'Enable')]"
                                            ]
                                            
                                            for selector in library_selectors:
                                                try:
                                                    library_elements = driver.find_elements(By.XPATH, selector)
                                                    for library_element in library_elements:
                                                        if library_element.is_displayed() and library_element.is_enabled():
                                                            try:
                                                                driver.execute_script("arguments[0].scrollIntoView(true);", library_element)
                                                                time.sleep(random.uniform(1.0, 2.0))
                                                                human_mouse_move_to(library_element)
                                                                library_element.click()
                                                                print("✅ Navigated to API Library!")
                                                                time.sleep(random.uniform(3.0, 5.0))
                                                                break
                                                            except Exception:
                                                                continue
                                                    break
                                                except Exception:
                                                    continue
                                    
                                    except Exception as nav_error:
                                        print(f"⚠️ Navigation method failed: {nav_error}")
                                    
                                    # Method 4: Look for Gmail API in search dropdown
                                    print("🔍 Searching for Gmail API in search dropdown...")
                                    time.sleep(random.uniform(3.0, 5.0))  # Wait longer for search results
                                    
                                    # Look for Gmail API with improved selectors
                                    gmail_api_selectors = [
                                        # Most reliable selectors for Gmail API
                                        "[id*='gmail.googleapis.com']",
                                        "div[id*='gmail.googleapis.com']",
                                        "[id*='inventorySearch'][id*='gmail']",
                                        # XPath selectors
                                        "//div[contains(@id, 'gmail.googleapis.com')]",
                                        "//*[contains(@id, 'gmail.googleapis.com')]",
                                        "//div[contains(@id, 'inventorySearch') and contains(@id, 'gmail')]",
                                        # Text-based selectors as fallback
                                        "//div[contains(@class, 'pcc-search-result-primary-title')][contains(text(), 'Gmail API')]",
                                        "//div[contains(@class, 'pcc-search-result-text-content')]//div[contains(text(), 'Gmail API')]",
                                        "//div[contains(@class, 'pcc-search-result-primary-title')][contains(text(), 'Gmail')]",
                                        "//div[contains(text(), 'Gmail API')]",
                                        "//span[contains(text(), 'Gmail API')]",
                                        "//*[contains(text(), 'Gmail API')]",
                                        "//a[contains(text(), 'Gmail API')]",
                                        "[aria-label*='Gmail API']",
                                        "[title*='Gmail API']"
                                    ]
                                    
                                    # Now look for Gmail API in the dropdown with the specific selectors
                                    print("🔍 Looking for Gmail API in search results...")
                                    gmail_api_found = False
                                    
                                    for selector in gmail_api_selectors:
                                        try:
                                            gmail_elements = []
                                            
                                            if selector.startswith("//"):
                                                # XPath selector
                                                gmail_elements = driver.find_elements(By.XPATH, selector)
                                            else:
                                                # CSS selector
                                                gmail_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                            
                                            for gmail_element in gmail_elements:
                                                if gmail_element and gmail_element.is_displayed():
                                                    try:
                                                        # Try to click the Gmail API element
                                                        driver.execute_script("arguments[0].scrollIntoView(true);", gmail_element)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        # Get clickable parent if needed
                                                        clickable_element = gmail_element
                                                        parent_element = gmail_element.find_element(By.XPATH, "..")
                                                        if parent_element and parent_element.is_enabled():
                                                            clickable_element = parent_element
                                                        
                                                        # Try JavaScript click first
                                                        driver.execute_script("arguments[0].click();", clickable_element)
                                                        print(f"✅ Gmail API clicked with selector: {selector}")
                                                        gmail_api_found = True
                                                        break
                                                        
                                                    except Exception as click_error:
                                                        print(f"⚠️ Failed to click Gmail API with {selector}: {click_error}")
                                                        # Try regular click as fallback
                                                        try:
                                                            human_mouse_move_to(clickable_element)
                                                            clickable_element.click()
                                                            print(f"✅ Gmail API clicked with regular click using selector: {selector}")
                                                            gmail_api_found = True
                                                            break
                                                        except Exception as regular_click_error:
                                                            print(f"⚠️ Regular click also failed: {regular_click_error}")
                                                            continue
                                            
                                            if gmail_api_found:
                                                break
                                                
                                        except Exception as selector_error:
                                            print(f"⚠️ Selector {selector} failed: {selector_error}")
                                            continue
                                    
                                    # If still not found, try a more aggressive search
                                    if not gmail_api_found:
                                        print("🔍 Gmail API not found with specific selectors, trying broader search...")
                                        
                                        # Look for any clickable elements containing Gmail
                                        all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Gmail') or contains(@id, 'gmail') or contains(@class, 'gmail')]")
                                        
                                        for element in all_elements:
                                            try:
                                                if element.is_displayed() and element.is_enabled():
                                                    element_text = element.get_attribute("textContent") or element.text or ""
                                                    if "gmail" in element_text.lower() and len(element_text.strip()) > 0:
                                                        print(f"✅ Found potential Gmail element: {element_text[:100]}...")
                                                        try:
                                                            driver.execute_script("arguments[0].click();", element)
                                                            print("✅ Gmail API clicked with broader search!")
                                                            gmail_api_found = True
                                                            break
                                                        except Exception as broad_click_error:
                                                            print(f"⚠️ Broader search click failed: {broad_click_error}")
                                                            continue
                                            except Exception:
                                                continue
                                    
                                    # Method 5: Try pressing Enter after typing gmail
                                    if not gmail_api_found:
                                        print("🔍 Trying Enter key after gmail search...")
                                        pyautogui.press('enter')
                                        time.sleep(random.uniform(3.0, 5.0))
                                        
                                        # Look again for Gmail API after pressing Enter
                                        for selector in gmail_api_selectors:
                                            try:
                                                if selector.startswith("//"):
                                                    gmail_elements = driver.find_elements(By.XPATH, selector)
                                                else:
                                                    gmail_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                
                                                for gmail_element in gmail_elements:
                                                    if gmail_element.is_displayed() and gmail_element.is_enabled():
                                                        try:
                                                            element_text = gmail_element.get_attribute("textContent") or gmail_element.text
                                                            if "gmail" in element_text.lower() or "Gmail" in element_text:
                                                                print(f"✅ Found Gmail API after Enter: {element_text[:50]}...")
                                                                
                                                                driver.execute_script("arguments[0].scrollIntoView(true);", gmail_element)
                                                                time.sleep(random.uniform(1.0, 2.0))
                                                                human_mouse_move_to(gmail_element)
                                                                gmail_element.click()
                                                                print("✅ Gmail API clicked after Enter!")
                                                                gmail_api_found = True
                                                                break
                                                        except Exception:
                                                            continue
                                                
                                                if gmail_api_found:
                                                    break
                                                    
                                            except Exception:
                                                continue
                                    
                                    if gmail_api_found:
                                        print("✅ Gmail API search completed successfully!")
                                        print("⏳ Waiting for Gmail API page to load...")
                                        time.sleep(random.uniform(5.0, 8.0))  # Wait longer for page to load
                                        
                                        # Verify we're on the Gmail API page
                                        try:
                                            # Look for indicators that we're on the Gmail API page
                                            page_indicators = [
                                                "//h1[contains(text(), 'Gmail API')]",
                                                "//h2[contains(text(), 'Gmail API')]",
                                                "//*[contains(text(), 'Gmail API')]",
                                                "//title[contains(text(), 'Gmail')]",
                                                "//*[contains(@class, 'api-title') and contains(text(), 'Gmail')]"
                                            ]
                                            
                                            page_verified = False
                                            for indicator in page_indicators:
                                                try:
                                                    element = driver.find_element(By.XPATH, indicator)
                                                    if element and element.is_displayed():
                                                        print(f"✅ Verified Gmail API page: {element.text[:50]}...")
                                                        page_verified = True
                                                        break
                                                except:
                                                    continue
                                            
                                            if not page_verified:
                                                print("⚠️ Could not verify Gmail API page, but continuing...")
                                                # Try to check current URL
                                                current_url = driver.current_url
                                                if "gmail" in current_url.lower():
                                                    print(f"✅ URL contains gmail: {current_url}")
                                                    page_verified = True
                                                else:
                                                    print(f"⚠️ Current URL: {current_url}")
                                        
                                        except Exception as verification_error:
                                            print(f"⚠️ Page verification failed: {verification_error}")
                                            print("🔄 Continuing with Enable button search...")
                                        
                                        
                                        # Look for the blue Enable button on Gmail API page
                                        print("🔘 Looking for blue Enable button...")
                                        enable_selectors = [
                                            # Most specific selectors for the Gmail API Enable button
                                            "//button[contains(@class, 'mdc-button--raised') and contains(@class, 'mdc-button--primary') and contains(text(), 'Enable')]",
                                            "//button[contains(@class, 'mat-mdc-raised-button') and contains(@class, 'mat-primary') and contains(text(), 'Enable')]",
                                            "//button[contains(@class, 'mdc-button--raised') and contains(text(), 'Enable')]",
                                            "//button[contains(@class, 'mat-mdc-raised-button') and contains(text(), 'Enable')]",
                                            "//button[contains(@class, 'mdc-button') and contains(@class, 'cfc-button') and contains(text(), 'Enable')]",
                                            "//button[@color='primary' and contains(text(), 'Enable')]",
                                            "//button[contains(@class, 'primary') and contains(text(), 'Enable')]",
                                            "//button[contains(@class, 'blue') and contains(text(), 'Enable')]",
                                            "//button[contains(@style, 'background-color') and contains(text(), 'Enable')]",
                                            # More specific Gmail API context selectors
                                            "//div[contains(@class, 'api-detail')]//button[contains(text(), 'Enable')]",
                                            "//div[contains(@class, 'enable-api')]//button[contains(text(), 'Enable')]",
                                            "//section[contains(@class, 'api-overview')]//button[contains(text(), 'Enable')]",
                                            "//main//button[contains(text(), 'Enable')]",
                                            # Generic Enable button selectors
                                            "//button[contains(text(), 'Enable') and not(contains(text(), 'Disable'))]",
                                            "//button[contains(text(), 'ENABLE')]",
                                            "//button[text()='Enable']",
                                            "//button[text()='ENABLE']",
                                            "//span[contains(text(), 'Enable')]//ancestor::button[1]",
                                            "//div[contains(text(), 'Enable')]//ancestor::button[1]",
                                            # CSS selectors for Enable buttons
                                            "button[aria-label*='Enable']",
                                            "button.mdc-button--raised",
                                            "button.mat-mdc-raised-button",
                                            ".enable-button",
                                            "[data-track-name*='enable']",
                                            "button[type='submit']",
                                            # Input type selectors
                                            "//input[@type='submit' and @value='Enable']",
                                            "//input[@type='button' and @value='Enable']"
                                        ]
                                        
                                        enable_btn_found = False
                                        for selector in enable_selectors:
                                            try:
                                                enable_elements = []
                                                
                                                if selector.startswith("//"):
                                                    enable_elements = driver.find_elements(By.XPATH, selector)
                                                else:
                                                    # Handle CSS selectors that contain :contains() (not valid CSS)
                                                    if ":contains(" in selector:
                                                        # Convert to XPath
                                                        text_to_find = selector.split(":contains('")[1].split("')")[0]
                                                        base_selector = selector.split(":contains(")[0]
                                                        xpath_selector = f"//{base_selector}[contains(text(), '{text_to_find}')]"
                                                        enable_elements = driver.find_elements(By.XPATH, xpath_selector)
                                                    else:
                                                        enable_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                
                                                for enable_btn in enable_elements:
                                                    if enable_btn and enable_btn.is_displayed() and enable_btn.is_enabled():
                                                        # Check if this is actually an Enable button
                                                        btn_text = (enable_btn.get_attribute("textContent") or enable_btn.text or "").strip()
                                                        btn_value = enable_btn.get_attribute("value") or ""
                                                        btn_aria_label = enable_btn.get_attribute("aria-label") or ""
                                                        btn_classes = enable_btn.get_attribute("class") or ""
                                                        
                                                        # More thorough filtering for Enable buttons
                                                        is_enable_btn = False
                                                        
                                                        # Check text content
                                                        if ("enable" in btn_text.lower() and "disable" not in btn_text.lower()) or "enable" in btn_value.lower():
                                                            is_enable_btn = True
                                                        
                                                        # Check aria-label
                                                        if "enable" in btn_aria_label.lower() and "disable" not in btn_aria_label.lower():
                                                            is_enable_btn = True
                                                        
                                                        # Additional checks for Gmail API context
                                                        if is_enable_btn and btn_text.lower() == "enable":
                                                            # This is likely the main Enable button
                                                            print(f"✅ Found primary Enable button with selector: {selector}")
                                                            print(f"   Button text: '{btn_text}'")
                                                            print(f"   Button classes: {btn_classes}")
                                                            print(f"   Button aria-label: '{btn_aria_label}'")
                                                            
                                                            # Try to click the enable button
                                                            try:
                                                                driver.execute_script("arguments[0].scrollIntoView(true);", enable_btn)
                                                                time.sleep(random.uniform(1.0, 2.0))
                                                                human_mouse_move_to(enable_btn)
                                                                enable_btn.click()
                                                                print("✅ Gmail API Enable button clicked successfully!")
                                                                enable_btn_found = True
                                                                break
                                                            except Exception as enable_click_error:
                                                                print(f"⚠️ Regular click failed: {enable_click_error}")
                                                                print("🔄 Trying JavaScript click...")
                                                                try:
                                                                    driver.execute_script("arguments[0].click();", enable_btn)
                                                                    print("✅ Gmail API Enable button clicked with JavaScript!")
                                                                    enable_btn_found = True
                                                                    break
                                                                except Exception as js_click_error:
                                                                    print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                                    continue
                                                        
                                                        elif is_enable_btn:
                                                            # This might be an Enable button, but not the primary one
                                                            print(f"✅ Found potential Enable button with selector: {selector}")
                                                            print(f"   Button text: '{btn_text}'")
                                                            print(f"   Button classes: {btn_classes}")
                                                            
                                                            # Try to click if no better option found
                                                            try:
                                                                driver.execute_script("arguments[0].scrollIntoView(true);", enable_btn)
                                                                time.sleep(random.uniform(1.0, 2.0))
                                                                human_mouse_move_to(enable_btn)
                                                                enable_btn.click()
                                                                print("✅ Gmail API Enable button clicked successfully!")
                                                                enable_btn_found = True
                                                                break
                                                            except Exception as enable_click_error:
                                                                print(f"⚠️ Regular click failed: {enable_click_error}")
                                                                print("🔄 Trying JavaScript click...")
                                                                try:
                                                                    driver.execute_script("arguments[0].click();", enable_btn)
                                                                    print("✅ Gmail API Enable button clicked with JavaScript!")
                                                                    enable_btn_found = True
                                                                    break
                                                                except Exception as js_click_error:
                                                                    print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                                    continue
                                                
                                                if enable_btn_found:
                                                    break
                                                        
                                            except Exception as enable_search_error:
                                                print(f"⚠️ Error with enable selector {selector}: {enable_search_error}")
                                                continue
                                        
                                        if enable_btn_found:
                                            print("🎉 Gmail API enabled successfully!")
                                            print("⏳ Waiting for API to be fully enabled and new page to load...")
                                            time.sleep(random.uniform(6.0, 10.0))  # Wait for the new page to load

                                            # Step 11: Find and click OAuth consent screen link in sidebar
                                            print("🔐 Looking for OAuth consent screen link in sidebar...")
                                            oauth_sidebar_selectors = [
                                                '#cfctest-section-nav-item-oauth_api_consent',
                                                "//a[@id='cfctest-section-nav-item-oauth_api_consent']",
                                                "//a[contains(@href, '/apis/credentials/consent')]",
                                                "//a[contains(text(), 'OAuth consent screen')]",
                                                "//*[contains(text(), 'OAuth consent screen')]",
                                                "//span[contains(text(), 'OAuth consent screen')]/ancestor::a[1]"
                                            ]
                                            oauth_btn_found = False
                                            for attempt in range(10):
                                                for oauth_selector in oauth_sidebar_selectors:
                                                    try:
                                                        oauth_elements = []
                                                        if oauth_selector.startswith("//"):
                                                            oauth_elements = driver.find_elements(By.XPATH, oauth_selector)
                                                        else:
                                                            oauth_elements = driver.find_elements(By.CSS_SELECTOR, oauth_selector)
                                                        for oauth_element in oauth_elements:
                                                            if oauth_element and oauth_element.is_displayed():
                                                                try:
                                                                    driver.execute_script("arguments[0].scrollIntoView(true);", oauth_element)
                                                                    time.sleep(0.5)
                                                                except Exception:
                                                                    pass
                                                                try:
                                                                    human_mouse_move_to(oauth_element)
                                                                except Exception:
                                                                    pass
                                                                try:
                                                                    oauth_element.click()
                                                                    print("✅ OAuth consent screen link clicked successfully!")
                                                                    oauth_btn_found = True
                                                                    break
                                                                except Exception as click_error:
                                                                    print(f"⚠️ Regular click failed: {click_error}")
                                                                    print("🔄 Trying JavaScript click...")
                                                                    try:
                                                                        driver.execute_script("arguments[0].click();", oauth_element)
                                                                        print("✅ OAuth consent screen link clicked with JavaScript!")
                                                                        oauth_btn_found = True
                                                                        break
                                                                    except Exception as js_click_error:
                                                                        print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                                        continue
                                                        if oauth_btn_found:
                                                            break
                                                    except Exception as oauth_search_error:
                                                        print(f"⚠️ Error with OAuth selector {oauth_selector}: {oauth_search_error}")
                                                        continue
                                                if oauth_btn_found:
                                                    break
                                                time.sleep(1.0)
                                            if oauth_btn_found:
                                                print("✅ Navigated to OAuth consent screen!")
                                                print("⏳ Waiting for OAuth consent screen page to load...")
                                                time.sleep(random.uniform(4.0, 6.0))
                                                # Step 12: Click "Get started" button
                                                print("🚀 Looking for 'Get started' button...")
                                                get_started_selectors = [
                                                    # Updated selector with new panel ID
                                                    "//*[@id='_6rif_panelgoog_342766572']/cfc-panel-body/cfc-virtual-viewport/div[1]/div/oauth-empty-state/cfc-empty-state/div/cfc-empty-state-actions/a",
                                                    "//*[@id='_6rif_panelgoog_342766572']/cfc-panel-body/cfc-virtual-viewport/div[1]/div/oauth-empty-state/cfc-empty-state/div/cfc-empty-state-actions/a/span[2]",
                                                    # CSS selector version
                                                    "#_6rif_panelgoog_342766572 > cfc-panel-body > cfc-virtual-viewport > div.cfc-virtual-scroll-content-wrapper > div > oauth-empty-state > cfc-empty-state > div > cfc-empty-state-actions > a",
                                                    # Fallback to old selector in case ID changes
                                                    "//*[@id='_5rif_panelgoog_95877825']/cfc-panel-body/cfc-virtual-viewport/div[1]/div/oauth-empty-state/cfc-empty-state/div/cfc-empty-state-actions/a/span[2]",
                                                    # Generic selectors that target the oauth-empty-state structure
                                                    "//oauth-empty-state//cfc-empty-state-actions//a",
                                                    "//cfc-empty-state-actions//a[contains(@href, 'oauth') or contains(text(), 'Get started')]",
                                                    "//cfc-empty-state-actions//a",
                                                    # Text-based selectors
                                                    "//span[contains(text(), 'Get started')]",
                                                    "//a[contains(text(), 'Get started')]",
                                                    "//button[contains(text(), 'Get started')]",
                                                    "//a[contains(@aria-label, 'Get started')]",
                                                    "//*[contains(text(), 'Get started')]"
                                                ]
                                                get_started_found = False
                                                for get_started_selector in get_started_selectors:
                                                    try:
                                                        get_started_elements = driver.find_elements(By.XPATH, get_started_selector)
                                                        for get_started_element in get_started_elements:
                                                            if get_started_element and get_started_element.is_displayed():
                                                                print(f"✅ Found 'Get started' element with selector: {get_started_selector}")
                                                                print(f"   Element tag: {get_started_element.tag_name}")
                                                                print(f"   Element text: {get_started_element.text}")
                                                                print(f"   Element href: {get_started_element.get_attribute('href') or 'N/A'}")
                                                                
                                                                clickable_get_started = get_started_element
                                                                
                                                                # If it's a span, try to find the parent link
                                                                if get_started_element.tag_name.lower() == "span":
                                                                    try:
                                                                        parent_link = get_started_element.find_element(By.XPATH, "./ancestor::a[1]")
                                                                        if parent_link:
                                                                            clickable_get_started = parent_link
                                                                            print(f"   Found parent link: {parent_link.get_attribute('href') or 'N/A'}")
                                                                    except:
                                                                        pass
                                                                
                                                                try:
                                                                    driver.execute_script("arguments[0].scrollIntoView(true);", clickable_get_started)
                                                                    time.sleep(random.uniform(1.0, 2.0))
                                                                    human_mouse_move_to(clickable_get_started)
                                                                    clickable_get_started.click()
                                                                    print("✅ 'Get started' button clicked successfully!")
                                                                    get_started_found = True
                                                                    break
                                                                except Exception as get_started_click_error:
                                                                    print(f"⚠️ Regular click failed: {get_started_click_error}")
                                                                    print("🔄 Trying JavaScript click...")
                                                                    try:
                                                                        driver.execute_script("arguments[0].click();", clickable_get_started)
                                                                        print("✅ 'Get started' button clicked with JavaScript!")
                                                                        get_started_found = True
                                                                        break
                                                                    except Exception as js_click_error:
                                                                        print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                                        continue
                                                        if get_started_found:
                                                            break
                                                    except Exception as get_started_search_error:
                                                        print(f"⚠️ Error with Get started selector {get_started_selector}: {get_started_search_error}")
                                                        continue
                                                if get_started_found:
                                                    print("🎉 OAuth consent screen configuration started!")
                                                    print("⏳ Waiting for OAuth configuration page to load...")
                                                    time.sleep(random.uniform(4.0, 6.0))
                                                else:
                                                    print("⚠️ Could not find 'Get started' button")
                                                    print("💡 You may need to manually click the 'Get started' button")
                                                    print("💡 Look for a button or link with 'Get started' text")
                                            else:
                                                print("⚠️ Could not find OAuth consent screen link in sidebar")
                                                print("💡 You may need to manually navigate to OAuth consent screen in the sidebar")
                                        
                                except Exception as gmail_api_error:
                                    print(f"❌ Error enabling Gmail API: {gmail_api_error}")
                                    print("💡 You may need to manually search for and enable Gmail API")
                                    print("💡 Try navigating to: APIs & Services > Library > Search for 'Gmail API'")
                                    
                                    if gmail_api_found:
                                        print("✅ Gmail API search completed successfully!")
                                        time.sleep(random.uniform(3.0, 5.0))
                                        
                                        # Look for Enable button
                                        print("🔘 Looking for Enable button...")
                                        enable_selectors = [
                                            "//button[contains(text(), 'Enable')]",
                                            "//button[contains(text(), 'ENABLE')]",
                                            "//span[contains(text(), 'Enable')]",
                                            "button[aria-label*='Enable']",
                                            "button[type='submit']",
                                            ".enable-button",
                                            "[data-track-name*='enable']"
                                        ]
                                        
                                        enable_btn_found = False
                                        for selector in enable_selectors:
                                            try:
                                                if selector.startswith("//"):
                                                    enable_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                                                else:
                                                    enable_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                                                
                                                if enable_btn and enable_btn.is_displayed():
                                                    print(f"✅ Found Enable button with selector: {selector}")
                                                    
                                                    # Click the enable button
                                                    try:
                                                        driver.execute_script("arguments[0].scrollIntoView(true);", enable_btn)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        human_mouse_move_to(enable_btn)
                                                        enable_btn.click()
                                                        print("✅ Gmail API Enable button clicked successfully!")
                                                        enable_btn_found = True
                                                        break
                                                    except Exception as enable_click_error:
                                                        print(f"⚠️ Regular click failed: {enable_click_error}")
                                                        print("🔄 Trying JavaScript click...")
                                                        driver.execute_script("arguments[0].click();", enable_btn)
                                                        print("✅ Gmail API Enable button clicked with JavaScript!")
                                                        enable_btn_found = True
                                                        break
                                                        
                                            except TimeoutException:
                                                continue
                                            except Exception as enable_search_error:
                                                print(f"⚠️ Error with enable selector {selector}: {enable_search_error}")
                                                continue
                                        
                                        if enable_btn_found:
                                            print("✅ Gmail API enabled successfully!")
                                            time.sleep(random.uniform(3.0, 5.0))
                                        else:
                                            print("⚠️ Could not find Enable button")
                                            print("💡 You may need to manually enable the Gmail API")
                                    else:
                                        print("❌ Could not find Gmail API option")
                                        print("💡 You may need to manually search for and enable Gmail API")
                                        
                                except Exception as gmail_api_error:
                                    print(f"❌ Error enabling Gmail API: {gmail_api_error}")
                                    print("💡 You may need to manually search for and enable Gmail API")
                                
                            else:
                                print("⚠️ Could not automatically select the project")
                                print("💡 You may need to manually select the project from the picker")
                                print(f"💡 Look for project name: {PROJECT_NAME}")
                        else:
                            print("❌ Could not open project picker")
                            print("💡 You may need to manually open the project picker and select the project")
                            
                    except Exception as project_selection_error:
                        print(f"❌ Error selecting project: {project_selection_error}")
                        print("💡 You may need to manually select the project from the picker")
                        print(f"💡 Look for project name: {PROJECT_NAME}")
                    
                else:
                    print("❌ Could not find create button")
                    
            except Exception as create_error:
                print(f"❌ Error clicking create button: {create_error}")
            
        except TimeoutException:
            print("❌ Could not find 'New Project' button in modal")
            print("💡 The modal might not have loaded or the button structure changed")
        except Exception as modal_error:
            print(f"❌ Error clicking 'New Project' button: {modal_error}")
        
    except TimeoutException:
        print("❌ Could not find or click new project button")
        print("💡 The button might not be available yet or the page structure changed")
    except Exception as e:
        print(f"❌ Error clicking new project button: {e}")
        print("🔄 Trying alternative approach...")
        # Try clicking any element that contains "project" text
        try:
            project_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'project') or contains(text(), 'Project')]")
            if project_elements:
                for elem in project_elements:
                    if elem.is_displayed() and elem.is_enabled():
                        driver.execute_script("arguments[0].click();", elem)
                        print("✅ Clicked alternative project element!")
                        break
        except Exception as alt_error:
            print(f"❌ Alternative approach also failed: {alt_error}")

except TimeoutException as e:
    print(f"⏰ Timeout Error: {e}")
    print("The page took too long to load or elements were not found.")
    
except NoSuchElementException as e:
    print(f"🔍 Element Not Found Error: {e}")
    print("Could not locate the required elements on the page.")
    
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
    print(f"Error type: {type(e).__name__}")

finally:
    print("🔚 Browser will remain open for manual interaction...")
    print("💡 Press Enter when you want to close the browser, or close it manually.")
    
    try:
        input()  # Wait for user input before closing
        if 'driver' in locals() and driver is not None:
            driver.quit()
            print("👋 Browser closed successfully.")
        else:
            print("👋 No browser to close.")
    except KeyboardInterrupt:
        print("\n👋 Script interrupted. Browser may still be open.")
    except Exception as e:
        print(f"⚠️  Warning: Error closing browser: {e}")
    print("👋 Script completed.")
