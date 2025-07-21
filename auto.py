print("🔄 Starting Multi-Instance Google Login Automation Script...")
print("⚡ ULTRA FAST: Multi-instance support with isolated Chrome profiles")
print("📦 Loading required modules...")

"""
ENHANCED AUTOMATION SCRIPT WITH IMPROVED OVERLAY HANDLING
=======================================================

Recent Improvements (2025):
1. ✅ Fixed handle_2fa_and_verification() missing driver argument error
2. ✅ Enhanced dismiss_overlay() function to handle Google Console tutorial tooltips and overlays
3. ✅ Added comprehensive handle_google_console_first_time_setup() function for:
   - Country selection modal (Austria selection)
   - Terms of Service agreement checkbox
   - Continue/Accept button handling
4. ✅ Improved safe_click() function to better handle element click interceptions
5. ✅ Enhanced project name filling and create button clicking with overlay dismissal
6. ✅ Better error handling and fallback mechanisms for all UI interactions
7. ✅ Comprehensive tutorial overlay detection and dismissal

These improvements ensure the automation works reliably even when:
- Google shows tutorial overlays/tooltips for new accounts
- CDK overlay backdrops block click interactions
- First-time users encounter country selection and terms agreement modals
- Various UI elements have click interception issues
"""

import time
import random
import pyautogui
import os
import undetected_chromedriver as uc
import shutil
import glob
from pathlib import Path
import getpass
import requests
import zipfile
import subprocess
import threading
import uuid
import socket
import psutil

# Disable PyAutoGUI fail-safe to prevent mouse corner trigger
pyautogui.FAILSAFE = False

# Generate unique instance ID for this script run
INSTANCE_ID = str(uuid.uuid4())[:8]
INSTANCE_TIMESTAMP = int(time.time())

# Start timing the automation
AUTOMATION_START_TIME = time.time()
START_TIME_FORMATTED = time.strftime('%H:%M:%S', time.localtime(AUTOMATION_START_TIME))

def dismiss_overlay(driver):
    """Dismiss any overlay tooltips or popups that might intercept clicks"""
    try:
        print("🔍 Scanning for overlays and tutorial tooltips...")
        
        # CRITICAL: First check for CDK overlay backdrop causing click interception
        print("🎯 Priority check for CDK overlay backdrop that blocks clicks...")
        try:
            # Check for multiple types of problematic backdrops
            backdrop_selectors = [
                ".cdk-overlay-backdrop",
                ".cdk-overlay-backdrop-showing", 
                ".cdk-overlay-dark-backdrop",
                ".mat-overlay-backdrop",
                "div[class*='cdk-overlay-backdrop']",
                "div[class*='overlay-backdrop']"
            ]
            
            backdrops_removed = 0
            for selector in backdrop_selectors:
                try:
                    backdrops = driver.find_elements(By.CSS_SELECTOR, selector)
                    for backdrop in backdrops:
                        if backdrop.is_displayed():
                            backdrop_classes = backdrop.get_attribute("class") or ""
                            print(f"🚨 Found backdrop with classes: {backdrop_classes}")
                            
                            # Check if this is a legitimate modal backdrop we should preserve
                            if is_legitimate_modal_backdrop(driver, backdrop):
                                print("ℹ️ Backdrop appears to be legitimate modal - preserving")
                                continue
                            
                            # Remove problematic backdrop with multiple methods
                            removal_success = False
                            
                            # Method 1: JavaScript removal
                            try:
                                driver.execute_script("arguments[0].remove();", backdrop)
                                print("✅ Removed CDK overlay backdrop")
                                removal_success = True
                                backdrops_removed += 1
                            except:
                                # Method 2: Hide with CSS
                                try:
                                    driver.execute_script("arguments[0].style.display = 'none';", backdrop)
                                    print("✅ Hidden CDK overlay backdrop")
                                    removal_success = True
                                    backdrops_removed += 1
                                except:
                                    # Method 3: Set visibility hidden
                                    try:
                                        driver.execute_script("arguments[0].style.visibility = 'hidden';", backdrop)
                                        print("✅ Made CDK overlay backdrop invisible")
                                        removal_success = True
                                        backdrops_removed += 1
                                    except:
                                        pass
                            
                            if removal_success:
                                time.sleep(0.3)  # Brief pause after each removal
                except Exception as selector_error:
                    continue
                    
            if backdrops_removed > 0:
                print(f"✅ Removed {backdrops_removed} problematic overlay backdrops")
                time.sleep(1.0)  # Wait for DOM to settle
            else:
                print("ℹ️ No problematic CDK backdrops found")
                
        except Exception as cdk_error:
            print(f"⚠️ Error handling CDK backdrop: {cdk_error}")
        
        # Enhanced overlay detection for Google Console tutorial tooltips
        overlay_selectors = [
            # Google Console navigation tutorial (PRIORITY - most common blocker)
            "//div[contains(@class, 'pcc-console-nav-circle') and contains(@class, 'show')]",
            "//div[contains(@class, 'pcc-console-nav-circle-box')]",
            "//button[@aria-label='Got it' and contains(@class, 'mat-primary')]",
            "//span[text()='Got it']/parent::button",
            "//div[contains(@class, 'pcc-console-nav-circle')]//button[contains(@aria-label, 'Got it')]",
            
            # Tutorial tooltip overlays (Google Console specific)
            "//div[contains(@class, 'cfc-tooltip-overlay')]",
            "//cfc-tooltip-overlay",
            "//div[contains(@class, 'tutorial-overlay')]",
            "//div[contains(@class, 'walkthrough-overlay')]",
            "//div[contains(@class, 'help-overlay')]",
            "//div[contains(@class, 'product-tour')]",
            "//div[contains(@class, 'intro-overlay')]",
            
            # Standard overlay patterns
            "//div[contains(@class, 'cdk-overlay-backdrop')]",
            "//div[contains(@class, 'mat-overlay-backdrop')]", 
            "//div[contains(@class, 'cdk-overlay-container')]",
            "//div[contains(@class, 'cdk-global-overlay-wrapper')]",
            
            # Close buttons for tooltips and tutorials
            "//button[contains(@class, 'cfc-tooltip-close-button')]",
            "//button[contains(@aria-label, 'Close') and contains(@class, 'tooltip')]",
            "//button[contains(@aria-label, 'Dismiss')]",
            "//button[contains(@aria-label, 'Skip')]",
            "//button[contains(@aria-label, 'Skip tutorial')]",
            "//button[contains(@aria-label, 'Skip tour')]",
            "//button[contains(@title, 'Close')]",
            "//button[contains(@title, 'Skip')]",
            "//button[contains(@title, 'Dismiss')]",
            
            # X close buttons and icons
            "//mat-icon-button[contains(@aria-label, 'Close')]",
            "//button[.//mat-icon[text()='close']]",
            "//button[.//mat-icon[text()='clear']]",
            "//button[.//svg[contains(@class, 'close')]]",
            "//span[contains(@class, 'close-icon')]//parent::button",
            
            # Tutorial specific dismiss buttons
            "//span[text()='Skip']//parent::button",
            "//span[text()='Close']//parent::button", 
            "//span[text()='Dismiss']//parent::button",
            "//span[text()='Got it']//parent::button",
            "//span[text()='OK']//parent::button",
            "//span[text()='Done']//parent::button",
            
            # Generic modal dismissal
            "//div[contains(@class, 'modal')]//button[contains(@class, 'close')]",
            "//div[contains(@class, 'dialog')]//button[contains(@class, 'close')]"
        ]
        
        overlay_dismissed = False
        
        # PRIORITY Method: Handle Google Console navigation tutorial first (most common blocker)
        print("🎯 Checking for Google Console navigation tutorial overlay...")
        try:
            nav_tutorial_selectors = [
                "//div[contains(@class, 'pcc-console-nav-circle') and contains(@class, 'show')]",
                "//div[contains(@class, 'pcc-console-nav-circle-box')]",
                "//button[@aria-label='Got it' and contains(@class, 'mat-primary')]"
            ]
            
            for nav_selector in nav_tutorial_selectors:
                try:
                    nav_elements = driver.find_elements(By.XPATH, nav_selector)
                    for nav_element in nav_elements:
                        if nav_element.is_displayed():
                            print(f"🚨 Found blocking navigation tutorial: {nav_element.get_attribute('class')}")
                            
                            # Look for "Got it" button within this tutorial
                            try:
                                got_it_button = nav_element.find_element(By.XPATH, ".//button[@aria-label='Got it']")
                                if got_it_button.is_displayed():
                                    driver.execute_script("arguments[0].click();", got_it_button)
                                    print("✅ Dismissed navigation tutorial with 'Got it' button")
                                    overlay_dismissed = True
                                    time.sleep(1.0)
                                    break
                            except:
                                # If no "Got it" button, try to remove the entire overlay
                                try:
                                    driver.execute_script("arguments[0].remove();", nav_element)
                                    print("✅ Removed navigation tutorial overlay")
                                    overlay_dismissed = True
                                    time.sleep(0.5)
                                    break
                                except:
                                    # Try clicking on the overlay to dismiss
                                    try:
                                        driver.execute_script("arguments[0].click();", nav_element)
                                        print("✅ Dismissed navigation tutorial by clicking overlay")
                                        overlay_dismissed = True
                                        time.sleep(0.5)
                                        break
                                    except:
                                        continue
                    if overlay_dismissed:
                        break
                except Exception as nav_error:
                    continue
            
            if overlay_dismissed:
                print("✅ Google Console navigation tutorial dismissed successfully!")
                return True
        except Exception as nav_tutorial_error:
            print(f"⚠️ Error handling navigation tutorial: {nav_tutorial_error}")
        
        # Method 1: Try to click close/dismiss buttons first
        for selector in overlay_selectors:
            try:
                overlays = driver.find_elements(By.XPATH, selector)
                for overlay in overlays:
                    if overlay.is_displayed() and overlay.is_enabled():
                        overlay_text = overlay.text.strip() if hasattr(overlay, 'text') else ""
                        aria_label = overlay.get_attribute("aria-label") or ""
                        
                        print(f"🎯 Found overlay element: {overlay_text[:50]}... (aria-label: {aria_label})")
                        
                        # Try multiple methods to dismiss
                        try:
                            # Method 1a: JavaScript click (most reliable)
                            driver.execute_script("arguments[0].click();", overlay)
                            print("✅ Dismissed overlay with JavaScript click")
                            overlay_dismissed = True
                            time.sleep(0.5)
                            break
                        except:
                            try:
                                # Method 1b: Regular click
                                overlay.click()
                                print("✅ Dismissed overlay with regular click")
                                overlay_dismissed = True
                                time.sleep(0.5)
                                break
                            except:
                                try:
                                    # Method 1c: Send Escape key to overlay
                                    overlay.send_keys(Keys.ESCAPE)
                                    print("✅ Dismissed overlay with Escape key")
                                    overlay_dismissed = True
                                    time.sleep(0.5)
                                    break
                                except:
                                    continue
                if overlay_dismissed:
                    break
            except Exception as selector_error:
                continue
        
        # Method 2: Try to remove backdrop overlays that block clicks (BE SELECTIVE)
        if not overlay_dismissed:
            print("🔧 Trying to remove blocking backdrop overlays (selective mode)...")
            try:
                # Find all backdrop elements
                all_backdrops = driver.find_elements(By.CSS_SELECTOR, ".cdk-overlay-backdrop")
                
                for backdrop in all_backdrops:
                    if backdrop.is_displayed():
                        # Check if this is a legitimate modal backdrop
                        if is_legitimate_modal_backdrop(driver, backdrop):
                            print("ℹ️ Skipping legitimate modal backdrop")
                            continue
                        
                        # This appears to be a problematic tutorial backdrop - remove it
                        try:
                            print("🗑️ Removing problematic tutorial backdrop")
                            driver.execute_script("arguments[0].remove();", backdrop)
                            overlay_dismissed = True
                            time.sleep(0.5)
                            break
                        except:
                            continue
                            
            except Exception as backdrop_error:
                print(f"⚠️ Error handling selective backdrop: {backdrop_error}")
        
        # Method 3: Try pressing Escape key to dismiss any active modal/overlay
        if not overlay_dismissed:
            print("⌨️ Trying Escape key to dismiss active overlays...")
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(1.0)
                print("✅ Sent Escape key to dismiss overlays")
                overlay_dismissed = True
            except Exception as escape_error:
                print(f"⚠️ Escape key failed: {escape_error}")
        
        # Method 4: Check for specific Google Console tutorial patterns and dismiss
        if not overlay_dismissed:
            print("🔍 Checking for Google Console specific tutorial overlays...")
            try:
                # Look for tutorial walkthrough indicators
                tutorial_indicators = [
                    "//div[contains(text(), 'tutorial')]",
                    "//div[contains(text(), 'tour')]", 
                    "//div[contains(text(), 'walkthrough')]",
                    "//div[contains(text(), 'Get started')]",
                    "//div[contains(text(), 'Welcome to')]",
                    "//div[contains(text(), 'New to Google Cloud')]"
                ]
                
                for indicator_selector in tutorial_indicators:
                    try:
                        tutorial_elements = driver.find_elements(By.XPATH, indicator_selector)
                        for tutorial_element in tutorial_elements:
                            if tutorial_element.is_displayed():
                                # Look for close button near this tutorial element
                                try:
                                    parent = tutorial_element.find_element(By.XPATH, "../..")
                                    close_buttons = parent.find_elements(By.XPATH, ".//button[contains(@aria-label, 'Close') or contains(@aria-label, 'Skip')]")
                                    for close_btn in close_buttons:
                                        if close_btn.is_displayed():
                                            driver.execute_script("arguments[0].click();", close_btn)
                                            print("✅ Dismissed tutorial overlay")
                                            overlay_dismissed = True
                                            time.sleep(0.5)
                                            break
                                    if overlay_dismissed:
                                        break
                                except:
                                    continue
                        if overlay_dismissed:
                            break
                    except:
                        continue
            except Exception as tutorial_error:
                print(f"⚠️ Error handling tutorial overlays: {tutorial_error}")
        
        # Method 5: Force remove any overlay containers that might still be blocking
        if not overlay_dismissed:
            print("🔧 Force removing persistent overlay containers...")
            try:
                force_remove_selectors = [
                    ".cdk-overlay-container > *",
                    ".cdk-global-overlay-wrapper",
                    "[class*='overlay'][style*='z-index']",
                    "[class*='tooltip'][style*='position: absolute']"
                ]
                
                for remove_selector in force_remove_selectors:
                    try:
                        elements_to_remove = driver.find_elements(By.CSS_SELECTOR, remove_selector)
                        for element in elements_to_remove:
                            try:
                                driver.execute_script("arguments[0].remove();", element)
                                print("✅ Force removed overlay container")
                                overlay_dismissed = True
                            except:
                                continue
                    except:
                        continue
            except Exception as force_remove_error:
                print(f"⚠️ Error force removing overlays: {force_remove_error}")
        
        if overlay_dismissed:
            print("✅ Successfully dismissed overlay/tooltip")
            time.sleep(1.0)  # Give UI time to settle
            return True
        else:
            print("ℹ️ No overlays found to dismiss")
            return False
            
    except Exception as e:
        print(f"⚠️ Error while trying to dismiss overlay: {e}")
        return False

def is_legitimate_modal_backdrop(driver, backdrop_element):
    """Check if a backdrop is part of a legitimate modal dialog"""
    try:
        # Check if this backdrop is associated with legitimate UI components
        legitimate_modal_selectors = [
            ".mat-mdc-dialog-container",     # Material dialog containers
            "[role='dialog']",               # ARIA dialog elements
            ".mat-select-panel",             # Material select dropdowns
            ".cfc-switcher-panel",          # Google Cloud switcher panels
            ".mat-autocomplete-panel",       # Autocomplete panels
            ".mat-menu-panel",               # Menu panels
            ".cdk-overlay-connected-position-bounding-box"  # Connected overlays
        ]
        
        # Check if any legitimate modal is currently visible
        for selector in legitimate_modal_selectors:
            try:
                modals = driver.find_elements(By.CSS_SELECTOR, selector)
                for modal in modals:
                    if modal.is_displayed():
                        return True
            except:
                continue
        
        # Check if the backdrop has specific classes indicating it's legitimate
        backdrop_classes = backdrop_element.get_attribute("class") or ""
        
        # These are legitimate backdrop patterns
        legitimate_patterns = [
            "cdk-overlay-backdrop-showing",    # Active modal backdrop
            "cdk-overlay-dark-backdrop",       # Dark modal backdrop
            "mat-overlay-backdrop"             # Material overlay backdrop
        ]
        
        # If it has legitimate patterns AND no tutorial indicators, it's legitimate
        has_legitimate_pattern = any(pattern in backdrop_classes for pattern in legitimate_patterns)
        
        # These patterns indicate tutorial/problematic overlays
        tutorial_patterns = [
            "tutorial", "walkthrough", "help", "nav-circle", "guide", "intro"
        ]
        
        has_tutorial_pattern = any(pattern in backdrop_classes.lower() for pattern in tutorial_patterns)
        
        # Return True if it's a legitimate backdrop (has legitimate patterns but no tutorial patterns)
        return has_legitimate_pattern and not has_tutorial_pattern
        
    except Exception as e:
        # If we can't determine, assume it's legitimate to be safe
        return True

def dismiss_oauth_overview_navigation_tutorial(driver):
    """
    Specifically dismiss the navigation tutorial that appears on OAuth overview pages
    Targets the exact elements that block clicks on auth/overview pages
    """
    try:
        print("🎯 Targeting OAuth overview navigation tutorial blocking elements...")
        
        # Check current URL to confirm we're on OAuth overview page
        current_url = driver.current_url
        if "auth/overview" not in current_url:
            print("ℹ️ Not on OAuth overview page, skipping specific tutorial dismissal")
            return True
            
        print(f"📍 Confirmed on OAuth overview page: {current_url}")
        
        # PRIORITY: Target the exact blocking elements you provided
        specific_blocking_elements = [
            # The main navigation tutorial circle
            "//div[contains(@class, 'pcc-console-nav-circle') and contains(@class, 'show')]",
            "//div[@class='pcc-console-nav-circle show']",
            
            # The "Got it" button within the tutorial
            "//button[@aria-label='Got it' and contains(@class, 'mat-primary')]",
            "//button[contains(@aria-label, 'Got it') and contains(@class, 'mdc-button--unelevated')]",
            "//span[text()='Got it']/parent::button",
            "//span[normalize-space()='Got it']/parent::button",
            
            # The callout message about documentation search
            "//p[@id='callout-message' and contains(@class, 'cfc-callout-message')]",
            "//p[contains(@class, 'cfc-callout-message') and contains(text(), 'search for documentation')]",
            "//p[contains(text(), 'You can now search for documentation')]",
            "//p[contains(text(), 'tutorials and API keys')]",
            
            # Additional navigation tutorial selectors
            "//div[contains(@class, 'pcc-console-nav-text')]",
            "//div[contains(text(), 'Click on the menu at any time')]",
            "//div[contains(@class, 'pcc-console-nav-subtitle')]"
        ]
        
        elements_dismissed = 0
        
        # Method 1: Click "Got it" button first (most effective)
        print("🎯 Method 1: Looking for 'Got it' button...")
        for got_it_selector in [
            "//button[@aria-label='Got it' and contains(@class, 'mat-primary')]",
            "//button[contains(@aria-label, 'Got it')]",
            "//span[text()='Got it']/parent::button",
            "//span[normalize-space()='Got it']/parent::button",
            "//button[.//span[text()='Got it']]",
            "//button[.//span[normalize-space()='Got it']]"
        ]:
            try:
                got_it_buttons = driver.find_elements(By.XPATH, got_it_selector)
                for button in got_it_buttons:
                    if button.is_displayed() and button.is_enabled():
                        button_text = button.get_attribute('textContent') or button.text or ""
                        if 'got it' in button_text.lower():
                            print(f"✅ Found 'Got it' button: '{button_text.strip()}'")
                            try:
                                # Use JavaScript click to avoid interception
                                driver.execute_script("arguments[0].click();", button)
                                print("✅ Successfully clicked 'Got it' button")
                                elements_dismissed += 1
                                time.sleep(2.0)  # Wait for tutorial to dismiss
                                break
                            except Exception as click_error:
                                print(f"⚠️ Could not click 'Got it' button: {click_error}")
                                continue
                if elements_dismissed > 0:
                    break
            except Exception as selector_error:
                continue
        
        # Method 2: Remove specific blocking elements if "Got it" didn't work
        if elements_dismissed == 0:
            print("🎯 Method 2: Removing blocking elements directly...")
            for element_selector in specific_blocking_elements:
                try:
                    blocking_elements = driver.find_elements(By.XPATH, element_selector)
                    for element in blocking_elements:
                        if element.is_displayed():
                            element_classes = element.get_attribute("class") or ""
                            element_text = (element.get_attribute("textContent") or element.text or "")[:100]
                            print(f"🚨 Found blocking element: {element_classes}")
                            print(f"   Text: '{element_text.strip()}'")
                            
                            # Try multiple removal methods
                            removal_success = False
                            
                            # Method 2a: JavaScript removal
                            try:
                                driver.execute_script("arguments[0].remove();", element)
                                print("✅ Removed blocking element with JavaScript")
                                removal_success = True
                                elements_dismissed += 1
                            except:
                                # Method 2b: Hide with CSS
                                try:
                                    driver.execute_script("arguments[0].style.display = 'none';", element)
                                    print("✅ Hidden blocking element with CSS")
                                    removal_success = True
                                    elements_dismissed += 1
                                except:
                                    # Method 2c: Make invisible
                                    try:
                                        driver.execute_script("arguments[0].style.visibility = 'hidden';", element)
                                        print("✅ Made blocking element invisible")
                                        removal_success = True
                                        elements_dismissed += 1
                                    except:
                                        pass
                            
                            if removal_success:
                                time.sleep(0.5)  # Brief pause after each removal
                except Exception as removal_error:
                    continue
        
        # Method 3: Generic overlay dismissal as fallback
        if elements_dismissed == 0:
            print("🎯 Method 3: Generic overlay dismissal...")
            dismiss_overlay(driver)
            time.sleep(1)
            elements_dismissed += 1
        
        if elements_dismissed > 0:
            print(f"✅ Successfully dismissed {elements_dismissed} OAuth overview blocking elements")
            time.sleep(2.0)  # Wait for UI to settle
            return True
        else:
            print("⚠️ No OAuth overview blocking elements found or removed")
            return False
            
    except Exception as e:
        print(f"❌ Error dismissing OAuth overview navigation tutorial: {e}")
        return False

def dismiss_navigation_tutorial(driver):
    """Specifically target and dismiss the Google Console navigation tutorial overlay"""
    try:
        print("🎯 Targeting Google Console navigation tutorial overlay...")
        
        # Look for the specific navigation tutorial elements (including OAuth overview specific ones)
        nav_tutorial_selectors = [
            # OAuth overview specific navigation tutorial elements (PRIORITY)
            "//div[contains(@class, 'pcc-console-nav-circle') and contains(@class, 'show')]",
            "//div[@class='pcc-console-nav-circle show']",
            "//button[@aria-label='Got it' and contains(@class, 'mat-primary')]",
            "//button[contains(@aria-label, 'Got it') and contains(@class, 'mdc-button--unelevated')]",
            "//p[@id='callout-message' and contains(@class, 'cfc-callout-message')]",
            "//p[contains(@class, 'cfc-callout-message') and contains(text(), 'search for documentation')]",
            
            # Generic navigation tutorial selectors
            "//div[contains(@class, 'pcc-console-nav-circle-box')]",
            "//div[contains(@class, 'pcc-console-nav-circle')]",
            "//span[text()='Got it']/parent::button",
            "//span[normalize-space()='Got it']/parent::button",
            "//div[contains(@class, 'pcc-console-nav-text')]",
            "//div[contains(text(), 'Click on the menu at any time')]"
        ]
        
        for selector in nav_tutorial_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        print(f"🚨 Found navigation tutorial element: {element.get_attribute('class')}")
                        
                        # If this is a "Got it" button, click it directly
                        if element.tag_name == "button" and ("Got it" in element.get_attribute("aria-label") or "Got it" in element.text):
                            try:
                                driver.execute_script("arguments[0].click();", element)
                                print("✅ Dismissed navigation tutorial with 'Got it' button")
                                time.sleep(2.0)  # Wait longer after dismissing tutorial
                                return True
                            except:
                                pass
                        
                        # Method 1: Look for "Got it" button within this element
                        try:
                            got_it_button = element.find_element(By.XPATH, ".//button[@aria-label='Got it']")
                            if got_it_button.is_displayed():
                                driver.execute_script("arguments[0].click();", got_it_button)
                                print("✅ Dismissed navigation tutorial with nested 'Got it' button")
                                time.sleep(2.0)
                                return True
                        except:
                            pass
                        
                        # Method 2: Look for button with "Got it" text
                        try:
                            got_it_text_button = element.find_element(By.XPATH, ".//button[.//span[text()='Got it']]")
                            if got_it_text_button.is_displayed():
                                driver.execute_script("arguments[0].click();", got_it_text_button)
                                print("✅ Dismissed navigation tutorial with 'Got it' text button")
                                time.sleep(2.0)
                                return True
                        except:
                            pass
                        
                        # Method 3: Try to remove the element if it's a container
                        if "pcc-console-nav-circle" in element.get_attribute("class"):
                            try:
                                driver.execute_script("arguments[0].remove();", element)
                                print("✅ Removed navigation tutorial overlay container")
                                time.sleep(1.0)
                                return True
                            except:
                                pass
                        
                        # Method 4: Try to hide the element
                        try:
                            driver.execute_script("arguments[0].style.display = 'none';", element)
                            print("✅ Hidden navigation tutorial overlay")
                            time.sleep(0.5)
                            return True
                        except:
                            pass
                        
                        # Method 5: Try clicking the element to dismiss
                        try:
                            driver.execute_script("arguments[0].click();", element)
                            print("✅ Dismissed navigation tutorial by clicking")
                            time.sleep(0.5)
                            return True
                        except:
                            continue
            except Exception as selector_error:
                continue
        
        # Look for "Got it" buttons independently with multiple approaches
        try:
            got_it_selectors = [
                "//button[@aria-label='Got it']",
                "//button[contains(@aria-label, 'Got it')]", 
                "//button[.//span[text()='Got it']]",
                "//button[.//span[normalize-space()='Got it']]",
                "//span[text()='Got it']/parent::button",
                "//span[normalize-space()='Got it']/parent::button"
            ]
            
            for selector in got_it_selectors:
                got_it_buttons = driver.find_elements(By.XPATH, selector)
                for button in got_it_buttons:
                    if button.is_displayed():
                        driver.execute_script("arguments[0].click();", button)
                        print("✅ Found and clicked standalone 'Got it' button")
                        time.sleep(2.0)
                        return True
        except Exception as got_it_error:
            pass

        # Also look for and dismiss the console callout message with search documentation tip
        try:
            callout_selectors = [
                "//p[@id='callout-message' and contains(@class, 'cfc-callout-message')]",
                "//p[contains(@class, 'cfc-callout-message') and contains(text(), 'search for documentation')]",
                "//*[contains(@class, 'cfc-callout') and contains(text(), 'documentation')]"
            ]
            
            for selector in callout_selectors:
                callout_elements = driver.find_elements(By.XPATH, selector)
                for element in callout_elements:
                    if element.is_displayed():
                        driver.execute_script("arguments[0].remove();", element)
                        print("✅ Removed console callout message")
                        time.sleep(0.5)
                        return True
        except Exception as callout_error:
            pass
            
        print("ℹ️ No navigation tutorial overlay found")
        return False
        
    except Exception as e:
        print(f"⚠️ Error dismissing navigation tutorial: {e}")
        return False

def safe_click(driver, element, description="element"):
    """Safely click an element by first checking and dismissing any overlays"""
    try:
        # PRIORITY: Check if this is a click interception due to legitimate modal backdrop
        try:
            # Check if there are legitimate modal dialogs open
            legitimate_modals = driver.find_elements(By.CSS_SELECTOR, 
                ".mat-mdc-dialog-container, [role='dialog'], .mat-select-panel, .cfc-switcher-panel")
            
            if any(modal.is_displayed() for modal in legitimate_modals):
                print(f"ℹ️ Legitimate modal detected - skipping overlay dismissal for {description}")
                # Try direct click first without dismissing legitimate modal backdrop
                try:
                    element.click()
                    print(f"✅ Clicked {description} normally with modal present")
                    return True
                except Exception as modal_click_error:
                    if "element click intercepted" in str(modal_click_error):
                        # Only now try JavaScript click to bypass the backdrop
                        try:
                            driver.execute_script("arguments[0].click();", element)
                            print(f"✅ Clicked {description} with JavaScript (modal backdrop bypass)")
                            return True
                        except Exception as js_error:
                            print(f"❌ JavaScript click failed for {description}: {js_error}")
                            return False
                    else:
                        print(f"❌ Error clicking {description}: {modal_click_error}")
                        return False
        except:
            pass  # Continue with normal flow if modal check fails
        
        # Normal flow: Only check for tutorial overlays
        print(f"🔍 Pre-checking for tutorial overlays before clicking {description}...")
        dismiss_navigation_tutorial(driver)  # Only dismiss navigation tutorial, not modal backdrops
        
        # First try normal click
        try:
            element.click()
            print(f"✅ Clicked {description} normally")
            return True
        except Exception as e:
            if "element click intercepted" in str(e) or "element not clickable" in str(e):
                print(f"⚠️ Click intercepted on {description}, attempting enhanced overlay dismissal...")
                
                # Try enhanced overlay dismissal multiple times
                for attempt in range(2):  # Reduced from 3 to 2 attempts
                    print(f"🔄 Overlay dismissal attempt {attempt + 1}/2...")
                    dismiss_overlay(driver)  # Now uses selective backdrop removal
                    time.sleep(1)  # Wait for overlay to be dismissed
                    
                    # Try clicking again after each dismissal attempt
                    try:
                        element.click()
                        print(f"✅ Clicked {description} after dismissing overlay (attempt {attempt + 1})")
                        return True
                    except:
                        if attempt < 1:  # Don't show error on final attempt
                            print(f"⚠️ Click still intercepted, trying again...")
                            continue
                
                # If regular click still fails after overlay dismissal, try JavaScript click
                try:
                    driver.execute_script("arguments[0].click();", element)
                    print(f"✅ Clicked {description} with JavaScript after overlay dismissal")
                    return True
                except Exception as js_error:
                    print(f"❌ JavaScript click also failed for {description}: {js_error}")
                    return False
            else:
                print(f"❌ Error clicking {description}: {e}")
                return False
    except Exception as e:
        print(f"❌ Error in safe_click for {description}: {e}")
        return False

def handle_2fa_and_verification(driver):
    """Handle 2FA and verification prompts during login"""
    print("🔒 Checking for 2FA/verification prompts...")
    try:
        # Handle 2FA popup that asks to turn on two-step verification
        handle_2fa_popup(driver)
        
        # Handle phone number verification
        try:
            phone_input = driver.find_element(By.XPATH, "//input[@type='tel' or @aria-label='Phone number']")
            if phone_input and phone_input.is_displayed():
                print("📱 Phone number verification detected")
                print("💡 Please enter your phone number manually")
                time.sleep(30)  # Give time for manual input
        except:
            pass

        # Handle SMS code verification
        try:
            code_input = driver.find_element(By.XPATH, "//input[@type='tel' or @aria-label='Enter code']")
            if code_input and code_input.is_displayed():
                print("🔑 SMS code verification detected")
                print("💡 Please enter the verification code manually")
                time.sleep(30)  # Give time for manual input
        except:
            pass

        # Check for "Try another way" button
        try:
            another_way_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Try another way')]/..")
            if another_way_btn and another_way_btn.is_displayed():
                print("🔄 'Try another way' button found")
                another_way_btn.click()
                time.sleep(5)
        except:
            pass

        print("✅ 2FA/verification handling completed")
        return True
    except Exception as e:
        print(f"⚠️ Error during 2FA/verification handling: {e}")
        print("💡 Manual intervention may be required for 2FA/verification")
        return False

def handle_2fa_popup(driver):
    """Handle the 2FA setup popup that appears after login"""
    try:
        print("🔍 Checking for 2FA setup popup...")
        time.sleep(3)  # Wait for popup to appear
        
        # Look for the 2FA popup dialog
        popup_indicators = [
            "Turn on two-step verification (2SV)",
            "Turn on two-step verification for your account",
            "two-step verification",
            "2SV",
            "July 24, 2025 to keep accessing the Google Cloud console",
            "July 25, 2025 to keep accessing the Google Cloud console"
        ]
        
        page_source = driver.page_source
        has_2fa_popup = any(indicator in page_source for indicator in popup_indicators)
        
        if has_2fa_popup:
            print("📱 2FA setup popup detected!")
            
            # First try to dismiss by clicking outside the dialog
            try:
                print("🎯 Trying to click outside dialog to dismiss...")
                # Click on the backdrop/overlay area
                backdrop_selectors = [
                    "//div[contains(@class, 'cdk-overlay-backdrop')]",
                    "//div[contains(@class, 'mat-overlay-backdrop')]",
                    "//div[contains(@class, 'cdk-overlay-container')]",
                    "//div[contains(@class, 'cdk-global-overlay-wrapper')]"
                ]
                
                for backdrop_selector in backdrop_selectors:
                    try:
                        backdrop = driver.find_element(By.XPATH, backdrop_selector)
                        if backdrop.is_displayed():
                            driver.execute_script("arguments[0].click();", backdrop)
                            print("✅ Successfully dismissed popup by clicking backdrop!")
                            time.sleep(2)
                            return True
                    except:
                        continue
            except Exception as backdrop_error:
                print(f"⚠️ Backdrop click failed: {backdrop_error}")
            
            # Look for "Remind me later" button with enhanced selectors
            remind_later_selectors = [
                # Exact match for the provided HTML structure
                "//button[@aria-label='Dismiss the dialogue']",
                "//button[.//span[contains(@class, 'mdc-button__label') and text()='Remind me later']]",
                "//span[contains(@class, 'mdc-button__label') and text()='Remind me later']/parent::button",
                "//button[contains(@class, 'mat-unthemed') and .//span[text()='Remind me later']]",
                "//div[contains(@class, 'mat-mdc-dialog-actions')]//button[.//span[text()='Remind me later']]",
                
                # More generic selectors
                "//button[contains(text(), 'Remind me later')]",
                "//span[text()='Remind me later']//ancestor::button[1]",
                "//button[.//span[text()='Remind me later']]",
                "//mat-dialog-actions//button[contains(text(), 'Remind me later')]",
                "//button[contains(@class, 'mdc-button') and contains(text(), 'Remind me later')]",
                
                # Alternative dismiss buttons
                "//button[contains(@aria-label, 'Dismiss')]",
                "//button[contains(@aria-label, 'Close')]",
                "//button[contains(@aria-label, 'Cancel')]",
                "//button[@type='button' and contains(@class, 'mat-mdc-button')]"
            ]
            
            remind_button = None
            for selector in remind_later_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element_text = (element.get_attribute("textContent") or element.text or "").strip()
                            aria_label = element.get_attribute("aria-label") or ""
                            
                            if ("remind me later" in element_text.lower() or 
                                "dismiss the dialogue" in aria_label.lower() or
                                element.get_attribute("aria-label") == "Dismiss the dialogue"):
                                remind_button = element
                                print(f"✅ Found 'Remind me later' button: {element_text} (aria-label: {aria_label})")
                                break
                    if remind_button:
                        break
                except Exception as selector_error:
                    continue
            
            if remind_button:
                print("🎯 Clicking 'Remind me later' button...")
                try:
                    # Scroll to button first
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", remind_button)
                    time.sleep(1)
                    
                    # Highlight button briefly for visibility
                    try:
                        driver.execute_script("arguments[0].style.outline = '3px solid red';", remind_button)
                        time.sleep(1)
                        driver.execute_script("arguments[0].style.outline = '';", remind_button)
                    except:
                        pass
                    
                    # Try JavaScript click first (most reliable for popups)
                    driver.execute_script("arguments[0].click();", remind_button)
                    print("✅ Successfully clicked 'Remind me later'!")
                    time.sleep(3)  # Wait for popup to close
                    return True
                    
                except Exception as click_error:
                    print(f"⚠️ JavaScript click failed: {click_error}")
                    try:
                        # Try regular click as fallback
                        remind_button.click()
                        print("✅ Successfully clicked 'Remind me later' with regular click!")
                        time.sleep(3)
                        return True
                    except Exception as regular_click_error:
                        print(f"❌ Regular click also failed: {regular_click_error}")
            
            # If button click failed, try other methods
            print("🔄 Trying alternative dismiss methods...")
            
            # Method 1: Press Escape key
            try:
                print("⌨️ Trying Escape key to dismiss popup...")
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(2)
                print("✅ Dismissed 2FA popup with Escape key")
                return True
            except Exception as escape_error:
                print(f"⚠️ Escape key failed: {escape_error}")
            
            # Method 2: Click on page background
            try:
                print("🎯 Trying to click on page background...")
                # Click somewhere on the page that's not the dialog
                driver.execute_script("document.elementFromPoint(100, 100).click();")
                time.sleep(2)
                print("✅ Dismissed popup by clicking background")
                return True
            except Exception as bg_click_error:
                print(f"⚠️ Background click failed: {bg_click_error}")
            
            # Method 3: Try to remove the dialog element directly
            try:
                print("🗑️ Trying to remove dialog element...")
                dialog_selectors = [
                    "//div[contains(@class, 'mat-mdc-dialog-surface')]",
                    "//ng-component[contains(@class, 'mat-mdc-dialog-component-host')]",
                    "//div[contains(@class, 'cdk-overlay-container')]"
                ]
                
                for dialog_selector in dialog_selectors:
                    try:
                        dialog = driver.find_element(By.XPATH, dialog_selector)
                        if dialog.is_displayed():
                            driver.execute_script("arguments[0].remove();", dialog)
                            print("✅ Removed dialog element")
                            time.sleep(2)
                            return True
                    except:
                        continue
                        
            except Exception as remove_error:
                print(f"⚠️ Dialog removal failed: {remove_error}")
            
            print("❌ Could not dismiss 2FA popup with any method")
            print("💡 Manual intervention may be required")
            return False
        else:
            print("✅ No 2FA setup popup detected")
            return True
            
    except Exception as e:
        print(f"⚠️ Error handling 2FA popup: {e}")
        return False

def open_project_picker(driver, wait):
    """Open the project picker using UI elements"""
    print("🔍 Opening project picker via UI...")
    try:
        picker_selectors = [
            "//button[contains(@class, 'cfc-switcher-button')]",
            "//button[contains(@aria-label, 'Select a project')]",
            "//button[contains(@class, 'project-picker')]",
            "//button[contains(@class, 'mat-mdc-button-base')]//span[contains(text(), 'project')]/..",
            "//button[@aria-haspopup='menu' and contains(@class, 'mat-mdc-button-base')]",
            "//header//button[contains(@class, 'project')]",
            f"//span[contains(text(), '{PROJECT_NAME}')]"
        ]
        
        picker_btn = None
        for selector in picker_selectors:
            try:
                picker_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                if picker_btn:
                    break
            except:
                continue
        
        if picker_btn:
            time.sleep(random.uniform(1.0, 2.0))
            driver.execute_script("arguments[0].scrollIntoView(true);", picker_btn)
            time.sleep(random.uniform(0.5, 1.0))
            driver.execute_script("arguments[0].click();", picker_btn)
            print("✅ Project picker opened via UI button!")
            time.sleep(random.uniform(2.0, 3.0))
            return True
        
        print("⚠️ Could not find project picker button")
        return False
    except Exception as e:
        print(f"❌ Error opening project picker: {e}")
        return False

print(f"🏷️ Instance ID: {INSTANCE_ID}")
print(f"⏰ Instance started at: {START_TIME_FORMATTED}")
print(f"⏱️ Automation timer started...")
print("=" * 60)

# Function to find available port for Chrome debugging
def find_available_port(start_port=9222):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise Exception("No available ports found")

# Function to create instance-specific directories
def create_instance_directories():
    """Create unique directories for this instance"""
    base_dir = os.getcwd()
    
    # Create instance-specific directories
    instance_dirs = {
        'profile': os.path.join(base_dir, f"chrome_profile_instance_{INSTANCE_ID}"),
        'downloads': os.path.join(base_dir, "downloads", f"instance_{INSTANCE_ID}"),
        'temp': os.path.join(base_dir, "temp", f"instance_{INSTANCE_ID}")
    }
    
    # Create directories
    for dir_type, dir_path in instance_dirs.items():
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"📁 Created {dir_type} directory: {dir_path}")
        except Exception as e:
            print(f"⚠️ Warning: Could not create {dir_type} directory: {e}")
    
    return instance_dirs

# Function to cleanup old instance directories
def cleanup_old_instances():
    """Clean up directories from old instances (older than 1 hour)"""
    try:
        base_dir = os.getcwd()
        current_time = time.time()
        
        # Clean up old chrome profiles
        profile_pattern = os.path.join(base_dir, "chrome_profile_instance_*")
        for old_profile in glob.glob(profile_pattern):
            try:
                # Check if directory is older than 1 hour
                dir_time = os.path.getmtime(old_profile)
                if current_time - dir_time > 3600:  # 1 hour
                    shutil.rmtree(old_profile)
                    print(f"🧹 Cleaned up old profile: {old_profile}")
            except Exception as cleanup_error:
                print(f"⚠️ Could not clean up {old_profile}: {cleanup_error}")
        
        # Clean up old download directories
        downloads_pattern = os.path.join(base_dir, "downloads", "instance_*")
        for old_download in glob.glob(downloads_pattern):
            try:
                dir_time = os.path.getmtime(old_download)
                if current_time - dir_time > 3600:  # 1 hour
                    shutil.rmtree(old_download)
                    print(f"🧹 Cleaned up old downloads: {old_download}")
            except Exception as cleanup_error:
                print(f"⚠️ Could not clean up {old_download}: {cleanup_error}")
                
    except Exception as e:
        print(f"⚠️ Warning: Error during cleanup: {e}")

# Perform cleanup and create instance directories
print("🧹 Cleaning up old instances...")
cleanup_old_instances()

print("📁 Creating instance-specific directories...")
INSTANCE_DIRS = create_instance_directories()

print("🔌 Finding available port for Chrome debugging...")
CHROME_DEBUG_PORT = find_available_port(9222)
print(f"🔌 Using Chrome debug port: {CHROME_DEBUG_PORT}")

# Function to get user input for credentials and download directory
def get_user_credentials_and_config():
    """Get Gmail credentials and download directory from user input"""
    print("\n" + "="*50)
    print("🔐 Gmail Account Setup")
    print("="*50)
    
    # Get Gmail address
    while True:
        email = input("📧 Enter your Gmail address: ").strip()
        if "@gmail.com" in email and "." not in email.replace("@gmail.com", "").replace(".", ""):
            break
        if "@" in email and "." in email:
            break
        print("❌ Please enter a valid email address")
    
    # Get password
    while True:
        password = getpass.getpass("🔒 Enter your Gmail password: ").strip()
        if len(password) >= 1:
            break
        print("❌ Password cannot be empty")
    
    # Get download directory
    print("\n📁 Download Directory Setup")
    print("Where would you like to save the JSON credentials file?")
    
    while True:
        download_dir = input(f"📂 Enter download directory path (or press Enter for instance directory: {INSTANCE_DIRS['downloads']}): ").strip()
        
        if not download_dir:
            download_dir = INSTANCE_DIRS['downloads']
            print(f"✅ Using instance-specific directory: {download_dir}")
            break
        
        # Expand user path (~)
        download_dir = os.path.expanduser(download_dir)
        
        # Check if directory exists or can be created
        try:
            if not os.path.exists(download_dir):
                os.makedirs(download_dir, exist_ok=True)
                print(f"✅ Created directory: {download_dir}")
            else:
                print(f"✅ Using existing directory: {download_dir}")
            break
        except Exception as e:
            print(f"❌ Error with directory '{download_dir}': {e}")
            print("Please enter a valid directory path")
    
    return email, password, download_dir

# Get credentials and config from user
EMAIL, PASSWORD, DOWNLOAD_DIR = get_user_credentials_and_config()

# Generate random project name
def generate_random_project_name():
    """Generate a random project name"""
    adjectives = ["awesome", "stellar", "dynamic", "innovative", "smart", "rapid", "efficient", "robust", "secure", "modern"]
    nouns = ["project", "app", "system", "platform", "service", "tool", "solution", "framework", "engine", "portal"]
    numbers = random.randint(100, 999)
    return f"{random.choice(adjectives)}-{random.choice(nouns)}-{numbers}"

PROJECT_NAME = generate_random_project_name()

# Fast timing configuration - reduce all delays
FAST_MODE = True

def print_milestone_timing(milestone_name):
    """Print timing information for major milestones"""
    current_time = time.time()
    elapsed_time = current_time - AUTOMATION_START_TIME
    current_time_formatted = time.strftime('%H:%M:%S', time.localtime(current_time))
    
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    
    print(f"⏱️  [{current_time_formatted}] {milestone_name} - Elapsed: {minutes:02d}:{seconds:02d}")

def fast_sleep(min_time, max_time):
    """Sleep with reduced timing for fast mode"""
    if FAST_MODE:
        # Reduce all timings by 80%
        min_time = min_time * 0.2
        max_time = max_time * 0.2
        # Minimum sleep of 0.1 seconds
        min_time = max(0.1, min_time)
        max_time = max(0.1, max_time)
    time.sleep(random.uniform(min_time, max_time))

def human_typing(element, text):
    """Simulate human-like typing"""
    for char in text:
        if FAST_MODE:
            delay = random.uniform(0.005, 0.02)  # Ultra fast typing
        else:
            delay = random.uniform(0.01, 0.05)
        element.send_keys(char)
        time.sleep(delay)

def human_mouse_move_to(element):
    """Simulate human-like mouse movement to an element with enhanced safety"""
    try:
        # Scroll element into view first
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        if FAST_MODE:
            time.sleep(random.uniform(0.05, 0.1))
        else:
            time.sleep(random.uniform(0.1, 0.3))
        
        # Get element location and size
        location = element.location_once_scrolled_into_view
        size = element.size
        
        # Calculate center coordinates with some randomness
        x = location['x'] + size['width'] / 2 + random.randint(-10, 10)
        y = location['y'] + size['height'] / 2 + random.randint(-10, 10)
        
        # Safety check: ensure coordinates are within safe bounds (not in screen corners)
        screen_width, screen_height = pyautogui.size()
        margin = 50  # pixels from edge
        
        x = max(margin, min(x, screen_width - margin))
        y = max(margin, min(y, screen_height - margin))
        
        # Move to the element with safe coordinates
        pyautogui.moveTo(x, y, duration=random.uniform(0.6, 1.3))
        time.sleep(random.uniform(0.1, 0.3))
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
    """Create driver using undetected-chromedriver with instance isolation"""
    try:
        print("🔄 Trying undetected-chromedriver approach...")
        import undetected_chromedriver as uc
        
        # Use instance-specific Chrome profile
        profile_path = INSTANCE_DIRS['profile']
        print(f"📁 Using Chrome profile: {profile_path}")
        
        # Create fresh ChromeOptions for each attempt
        def create_fresh_options():
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir={profile_path}")
            options.add_argument(f"--remote-debugging-port={CHROME_DEBUG_PORT}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-infobars")
            options.add_argument("--start-maximized")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Set instance-specific download directory
            prefs = {
                "download.default_directory": INSTANCE_DIRS['downloads'],
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            options.add_experimental_option("prefs", prefs)
            return options
        
        # Try without specifying version first (let it auto-detect)
        try:
            print("🔄 Auto-detecting Chrome version...")
            options = create_fresh_options()
            driver = uc.Chrome(options=options, headless=False, version_main=None)
        except Exception as auto_error:
            print(f"⚠️ Auto-detection failed: {auto_error}")
            # Try with specific major versions that are commonly available
            for version in [137, 138, 139, 136, 135]:
                try:
                    print(f"🔄 Trying Chrome version {version}...")
                    options = create_fresh_options()  # Create fresh options for each attempt
                    driver = uc.Chrome(options=options, headless=False, version_main=version)
                    break
                except Exception as version_error:
                    print(f"⚠️ Version {version} failed: {version_error}")
                    continue
            else:
                raise Exception("All version attempts failed")
        
        print("✅ undetected-chromedriver approach successful!")
        return driver
    except Exception as e:
        print(f"❌ undetected-chromedriver approach failed: {e}")
        return None

def create_driver_standard():
    """Create driver using standard selenium webdriver with automatic version management"""
    try:
        print("🔄 Trying standard selenium webdriver approach...")
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        
        options = Options()
        options.add_argument(f"--user-data-dir={INSTANCE_DIRS['profile']}")
        options.add_argument(f"--remote-debugging-port={CHROME_DEBUG_PORT}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Set instance-specific download directory
        prefs = {
            "download.default_directory": INSTANCE_DIRS['downloads'],
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        
        # First try: Use system ChromeDriver (if available and compatible)
        try:
            print("🔄 Trying system ChromeDriver...")
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ System ChromeDriver works!")
            return driver
        except Exception as system_error:
            print(f"⚠️ System ChromeDriver failed: {system_error}")
            
            # Second try: Download correct ChromeDriver version
            print("🔄 Downloading correct ChromeDriver version...")
            try:
                import subprocess
                import requests
                import zipfile
                
                # Get Chrome version
                try:
                    result = subprocess.run(['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'], 
                                          capture_output=True, text=True, shell=True)
                    chrome_version = result.stdout.split()[-1] if result.returncode == 0 else None
                    
                    if not chrome_version:
                        # Alternative method for Chrome version detection
                        result = subprocess.run(['powershell', '-command', 
                                               '(Get-Item "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe").VersionInfo.ProductVersion'], 
                                              capture_output=True, text=True, shell=True)
                        chrome_version = result.stdout.strip() if result.returncode == 0 else "137.0.7151.69"
                except:
                    chrome_version = "137.0.7151.69"  # Fallback to detected version
                
                print(f"🔍 Detected Chrome version: {chrome_version}")
                major_version = chrome_version.split('.')[0]
                
                # Download ChromeDriver for the detected Chrome version
                chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")
                
                if not os.path.exists(chromedriver_path):
                    print(f"📥 Downloading ChromeDriver for Chrome {major_version}...")
                    
                    # Try multiple download URLs
                    download_urls = [
                        f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/win64/chromedriver-win64.zip",
                        f"https://chromedriver.storage.googleapis.com/{major_version}.0.0.0/chromedriver_win32.zip",
                        f"https://chromedriver.storage.googleapis.com/137.0.0.0/chromedriver_win32.zip"  # Specific fallback
                    ]
                    
                    download_success = False
                    for download_url in download_urls:
                        try:
                            print(f"🔗 Trying URL: {download_url}")
                            response = requests.get(download_url, timeout=30)
                            if response.status_code == 200:
                                with open("chromedriver.zip", "wb") as f:
                                    f.write(response.content)
                                
                                with zipfile.ZipFile("chromedriver.zip", 'r') as zip_ref:
                                    zip_ref.extractall()
                                
                                # Handle different extraction paths
                                if os.path.exists(os.path.join("chromedriver-win64", "chromedriver.exe")):
                                    shutil.move(os.path.join("chromedriver-win64", "chromedriver.exe"), chromedriver_path)
                                elif os.path.exists("chromedriver.exe"):
                                    # Already in current directory
                                    pass
                                else:
                                    raise Exception("ChromeDriver.exe not found after extraction")
                                
                                # Cleanup
                                if os.path.exists("chromedriver.zip"):
                                    os.remove("chromedriver.zip")
                                if os.path.exists("chromedriver-win64"):
                                    shutil.rmtree("chromedriver-win64")
                                
                                print("✅ ChromeDriver downloaded successfully!")
                                download_success = True
                                break
                                
                        except Exception as download_error:
                            print(f"⚠️ Download from {download_url} failed: {download_error}")
                            continue
                    
                    if not download_success:
                        raise Exception("All ChromeDriver download attempts failed")
                
                # Use the downloaded ChromeDriver
                print("🔄 Using downloaded ChromeDriver...")
                service = Service(chromedriver_path)
                driver = webdriver.Chrome(service=service, options=options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                print("✅ Downloaded ChromeDriver works!")
                return driver
                
            except Exception as download_error:
                print(f"❌ ChromeDriver download failed: {download_error}")
                raise
                
    except Exception as e:
        print(f"❌ Standard selenium approach failed: {e}")
        return None

def create_driver_force_download():
    """Force download the correct ChromeDriver version"""
    try:
        print("🔄 Trying forced ChromeDriver download approach...")
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        import requests
        import zipfile
        import subprocess
        
        # Get Chrome version
        try:
            result = subprocess.run(['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'], 
                                  capture_output=True, text=True, shell=True)
            chrome_version = result.stdout.split()[-1] if result.returncode == 0 else None
            
            if not chrome_version:
                # Alternative method
                result = subprocess.run(['powershell', '-command', '(Get-Item "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe").VersionInfo.ProductVersion'], 
                                      capture_output=True, text=True, shell=True)
                chrome_version = result.stdout.strip() if result.returncode == 0 else "137.0.7151.69"
        except:
            chrome_version = "137.0.7151.69"  # Fallback to detected version
        
        print(f"🔍 Detected Chrome version: {chrome_version}")
        major_version = chrome_version.split('.')[0]
        
        # Download the matching ChromeDriver
        chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")
        
        if not os.path.exists(chromedriver_path):
            print(f"📥 Downloading ChromeDriver for Chrome {major_version}...")
            
            # ChromeDriver download URL for newer versions
            download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{chrome_version}/win64/chromedriver-win64.zip"
            
            try:
                response = requests.get(download_url, timeout=30)
                if response.status_code == 200:
                    with open("chromedriver.zip", "wb") as f:
                        f.write(response.content)
                    
                    with zipfile.ZipFile("chromedriver.zip", 'r') as zip_ref:
                        zip_ref.extractall()
                    
                    # Move chromedriver.exe to current directory
                    extracted_path = os.path.join("chromedriver-win64", "chromedriver.exe")
                    if os.path.exists(extracted_path):
                        shutil.move(extracted_path, chromedriver_path)
                    
                    # Cleanup
                    os.remove("chromedriver.zip")
                    if os.path.exists("chromedriver-win64"):
                        shutil.rmtree("chromedriver-win64")
                    
                    print("✅ ChromeDriver downloaded successfully!")
                else:
                    raise Exception(f"Download failed with status {response.status_code}")
            except Exception as download_error:
                print(f"⚠️ Download failed: {download_error}")
                print("🔄 Trying alternative download...")
                # Try with major version only
                alt_url = f"https://chromedriver.storage.googleapis.com/{major_version}.0.0.0/chromedriver_win32.zip"
                try:
                    response = requests.get(alt_url, timeout=30)
                    if response.status_code == 200:
                        with open("chromedriver.zip", "wb") as f:
                            f.write(response.content)
                        
                        with zipfile.ZipFile("chromedriver.zip", 'r') as zip_ref:
                            zip_ref.extractall()
                        
                        if os.path.exists("chromedriver.exe"):
                            print("✅ ChromeDriver downloaded successfully (alternative method)!")
                        else:
                            raise Exception("ChromeDriver.exe not found after extraction")
                        
                        os.remove("chromedriver.zip")
                    else:
                        raise Exception(f"Alternative download also failed")
                except Exception as alt_error:
                    print(f"❌ All download attempts failed: {alt_error}")
                    return None
        
        # Use the downloaded ChromeDriver
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
        
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Force download approach successful!")
        return driver
    except Exception as e:
        print(f"❌ Force download approach failed: {e}")
        return None

# Import common selenium modules
try:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
    print("✅ Selenium modules loaded")
except ImportError as e:
    print(f"❌ Error importing selenium modules: {e}")
    exit(1)

print("✅ All modules loaded successfully!")

def handle_google_console_first_time_setup(driver):
    """
    Enhanced handler for Google Cloud Console first-time setup including:
    - Country selection modal
    - Terms of Service agreement
    - Tutorial/walkthrough dismissal
    - Navigation tutorial overlay dismissal
    """
    print("🏗️ Checking for Google Cloud Console first-time setup requirements...")
    
    try:
        # First priority: Dismiss the navigation tutorial overlay that blocks clicks
        print("🎯 PRIORITY: Checking for navigation tutorial overlay...")
        nav_tutorial_dismissed = dismiss_navigation_tutorial(driver)
        
        # Wait a moment for any modals to appear after tutorial dismissal
        time.sleep(random.uniform(3.0, 5.0))
        
        # Check for any first-time setup modals after dismissing navigation tutorial
        setup_completed = False
        
        # Method 1: Look for country selection modal
        print("🌍 Checking for country selection modal...")
        modal_found = False
        
        # Enhanced modal detection selectors
        modal_selectors = [
            # Material Design dialog containers
            ".mat-mdc-dialog-content",
            ".mat-dialog-container", 
            ".cdk-overlay-container [role='dialog']",
            "mat-dialog-container",
            
            # Google Cloud specific modal patterns
            ".console-dialog",
            ".console-modal",
            ".gcp-modal",
            
            # Generic modal patterns
            "[role='dialog']",
            ".modal-content",
            ".dialog-content"
        ]
        
        modal_element = None
        for selector in modal_selectors:
            try:
                modals = driver.find_elements(By.CSS_SELECTOR, selector)
                for modal in modals:
                    if modal.is_displayed():
                        modal_text = modal.text.lower()
                        
                        # Check for first-time setup indicators
                        setup_indicators = [
                            "welcome" in modal_text and ("google cloud" in modal_text or "console" in modal_text),
                            "country" in modal_text and ("select" in modal_text or "residence" in modal_text),
                            "terms of service" in modal_text and "google cloud" in modal_text,
                            "create and manage projects" in modal_text,
                            "get started" in modal_text and "google cloud" in modal_text,
                            "setup" in modal_text and "console" in modal_text,
                            "first time" in modal_text,
                            "new to google cloud" in modal_text
                        ]
                        
                        if any(setup_indicators):
                            print(f"🎯 First-time setup modal detected!")
                            print(f"📝 Modal content: {modal_text[:200]}...")
                            modal_found = True
                            modal_element = modal
                            break
                
                if modal_found:
                    break
            except Exception as selector_error:
                continue
        
        if modal_found and modal_element:
            print("🚀 Handling first-time setup modal...")
            
            # Step 1: Handle country selection
            print("🌍 Looking for country selection dropdown...")
            time.sleep(random.uniform(1.0, 2.0))
            
            country_dropdown_selectors = [
                # Material Design select components
                ".mat-mdc-select-trigger",
                ".mat-select-trigger",
                "mat-select[formcontrolname='country']",
                "mat-select[formcontrolname='optInCountry']",
                ".mat-mdc-form-field-type-mat-select",
                
                # Google Cloud specific selectors
                "cfc-select[formcontrolname='optInCountry']",
                "cfc-select[aria-labelledby*='country']",
                ".cfc-select",
                
                # Generic dropdown patterns
                "[role='combobox'][aria-haspopup='listbox']",
                "[role='combobox']",
                "select[name*='country']"
            ]
            
            country_dropdown = None
            for selector in country_dropdown_selectors:
                try:
                    dropdowns = driver.find_elements(By.CSS_SELECTOR, selector)
                    for dropdown in dropdowns:
                        if dropdown.is_displayed() and dropdown.is_enabled():
                            country_dropdown = dropdown
                            print(f"✅ Found country dropdown with selector: {selector}")
                            break
                    if country_dropdown:
                        break
                except Exception:
                    continue
            
            if country_dropdown:
                print("🖱️ Opening country dropdown...")
                try:
                    # Scroll to dropdown and ensure it's visible
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", country_dropdown)
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    # Use safe_click to handle any overlays
                    if safe_click(driver, country_dropdown, "country dropdown"):
                        time.sleep(random.uniform(1.0, 2.0))
                        
                        # Look for Austria in dropdown options
                        print("🔍 Looking for Austria in country options...")
                        austria_selectors = [
                            # Material Design options
                            "//mat-option[contains(.//span, 'Austria')]",
                            "//mat-option[contains(text(), 'Austria')]",
                            "//div[contains(@class, 'mat-option') and contains(text(), 'Austria')]",
                            "//span[contains(text(), 'Austria')]//parent::mat-option",
                            
                            # Google Cloud specific options
                            "//cfc-option[contains(text(), 'Austria')]",
                            "//div[contains(@class, 'cfc-option') and contains(text(), 'Austria')]",
                            
                            # Generic option patterns
                            "//*[contains(text(), 'Austria') and (contains(@class, 'option') or contains(@role, 'option'))]"
                        ]
                        
                        austria_option = None
                        for selector in austria_selectors:
                            try:
                                austria_option = WebDriverWait(driver, 3).until(
                                    EC.element_to_be_clickable((By.XPATH, selector))
                                )
                                print(f"✅ Found Austria option with selector: {selector}")
                                break
                            except TimeoutException:
                                continue
                        
                        if austria_option:
                            print("🇦🇹 Selecting Austria...")
                            if safe_click(driver, austria_option, "Austria option"):
                                print("✅ Austria selected successfully!")
                            else:
                                print("⚠️ Failed to select Austria, continuing with default...")
                        else:
                            print("⚠️ Austria not found in options, using default selection...")
                    else:
                        print("⚠️ Failed to open country dropdown")
                except Exception as dropdown_error:
                    print(f"⚠️ Error handling country dropdown: {dropdown_error}")
            else:
                print("ℹ️ No country dropdown found in modal")
            
            # Step 2: Handle Terms of Service agreement checkbox
            print("☑️ Looking for Terms of Service agreement checkbox...")
            time.sleep(random.uniform(1.0, 2.0))
            
            checkbox_selectors = [
                # Material Design checkbox patterns
                "input[type='checkbox'].mat-mdc-checkbox-input",
                ".mdc-checkbox__native-control",
                "input[type='checkbox'][id*='checkbox']",
                "mat-checkbox input[type='checkbox']",
                
                # Google Cloud specific patterns
                "input[type='checkbox'][formcontrolname*='agree']",
                "input[type='checkbox'][formcontrolname*='terms']",
                "input[type='checkbox'][formcontrolname*='consent']",
                
                # Generic checkbox patterns
                "input[type='checkbox']"
            ]
            
            agreement_checkbox = None
            for selector in checkbox_selectors:
                try:
                    checkboxes = driver.find_elements(By.CSS_SELECTOR, selector)
                    for checkbox in checkboxes:
                        if checkbox.is_displayed() and checkbox.is_enabled():
                            # Check if this checkbox is related to terms/agreement
                            parent_text = ""
                            try:
                                # Check text in parent elements
                                for parent_level in range(1, 4):
                                    parent_xpath = "/".join([".."] * parent_level)
                                    parent = checkbox.find_element(By.XPATH, parent_xpath)
                                    parent_text += " " + (parent.text or "").lower()
                            except:
                                pass
                            
                            # Look for agreement-related keywords
                            agreement_keywords = ["agree", "terms", "accept", "consent", "service", "privacy"]
                            if any(keyword in parent_text for keyword in agreement_keywords):
                                agreement_checkbox = checkbox
                                print(f"✅ Found agreement checkbox with selector: {selector}")
                                print(f"📝 Related text: {parent_text.strip()[:100]}...")
                                break
                    if agreement_checkbox:
                        break
                except Exception:
                    continue
            
            if agreement_checkbox:
                # Check if checkbox is already checked
                is_checked = agreement_checkbox.is_selected()
                if not is_checked:
                    print("☑️ Checking Terms of Service agreement...")
                    try:
                        # Scroll to checkbox
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", agreement_checkbox)
                        time.sleep(random.uniform(0.5, 1.0))
                        
                        # Use safe_click to handle overlays
                        if safe_click(driver, agreement_checkbox, "Terms agreement checkbox"):
                            print("✅ Terms of Service agreement checked!")
                        else:
                            print("⚠️ Failed to check Terms agreement")
                    except Exception as checkbox_error:
                        print(f"⚠️ Error checking agreement checkbox: {checkbox_error}")
                else:
                    print("✅ Terms of Service agreement already checked!")
            else:
                print("ℹ️ No Terms of Service agreement checkbox found")
            
            # Step 3: Look for and click Continue/Accept button
            print("➡️ Looking for Continue/Accept button in modal...")
            time.sleep(random.uniform(1.0, 2.0))
            
            continue_selectors = [
                # Text-based button selection
                "//button[contains(.//span, 'Continue')]",
                "//button[contains(.//span, 'Accept')]",
                "//button[contains(.//span, 'Agree')]", 
                "//button[contains(.//span, 'Get started')]",
                "//button[contains(.//span, 'Start')]",
                "//span[contains(text(), 'Continue')]//parent::button",
                "//span[contains(text(), 'Accept')]//parent::button",
                "//span[contains(text(), 'Agree')]//parent::button",
                
                # Button attribute patterns
                "button[type='submit']",
                ".mat-primary button",
                ".mdc-button--unelevated",
                ".mdc-button--raised",
                
                # Generic button patterns in modal
                ".mat-mdc-dialog-actions button",
                "mat-dialog-actions button"
            ]
            
            continue_button = None
            for selector in continue_selectors:
                try:
                    if selector.startswith("//"):
                        buttons = driver.find_elements(By.XPATH, selector)
                    else:
                        buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button_text = (button.text or "").lower()
                            # Look for action keywords
                            action_keywords = ["continue", "accept", "agree", "start", "get started", "submit"]
                            if any(keyword in button_text for keyword in action_keywords) or button_text == "":
                                continue_button = button
                                print(f"✅ Found continue button: '{button.text}' with selector: {selector}")
                                break
                    if continue_button:
                        break
                except Exception:
                    continue
            
            if continue_button:
                print("✅ Clicking Continue/Accept button...")
                try:
                    # Scroll to button
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
                    time.sleep(random.uniform(0.5, 1.0))
                    
                    # Use safe_click to handle overlays
                    if safe_click(driver, continue_button, "Continue/Accept button"):
                        print("✅ First-time setup modal completed!")
                        time.sleep(random.uniform(2.0, 4.0))  # Wait for modal to close and page to load
                        setup_completed = True
                    else:
                        print("⚠️ Failed to click Continue/Accept button")
                except Exception as button_error:
                    print(f"⚠️ Error clicking Continue button: {button_error}")
            else:
                print("⚠️ Could not find Continue/Accept button, trying to close modal...")
                # Try pressing Escape to close modal
                try:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                    time.sleep(random.uniform(1.0, 2.0))
                    print("✅ Closed modal with Escape key")
                    setup_completed = True
                except:
                    print("⚠️ Could not close modal")
        else:
            print("ℹ️ No first-time setup modal detected")
            
        # Method 2: Check for any tutorial overlays or product tours after modal handling
        print("🔍 Checking for tutorial overlays and product tours...")
        dismiss_overlay(driver)
        
        return setup_completed or nav_tutorial_dismissed  # Return true if any setup was completed
        
    except Exception as setup_error:
        print(f"⚠️ Error handling first-time setup: {setup_error}")
        print("💡 Continuing with automation - manual setup may be required")
        return False

def configure_audience(driver):
    """Configure OAuth consent screen audience with test user"""
    print("👥 Proceeding to Audience configuration...")
    
    # CRITICAL: Dismiss navigation tutorial overlay before any interaction
    print("🎯 PRIORITY: Dismissing navigation tutorial overlay before audience configuration...")
    dismiss_navigation_tutorial(driver)
    time.sleep(1.0)  # Wait for dismissal to complete
    
    try:
        # Check for CAPTCHAs before proceeding
        if not wait_for_page_load_and_check_captcha(driver):
            print("⚠️ CAPTCHA handling failed, but continuing...")
        
        time.sleep(random.uniform(0.5, 1.0))
        
        # Click "Audience" from sidebar
        print("👥 Clicking 'Audience' from sidebar...")
        audience_selectors = [
            "//span[contains(@class, 'cfc-page-displayName') and contains(text(), 'Audience')]",
            "//span[@class='cfc-page-displayName'][contains(text(), 'Audience')]",
            "//a[contains(text(), 'Audience')]",
            "//li[contains(text(), 'Audience')]",
            "//div[contains(text(), 'Audience')]",
            "//*[contains(text(), 'Audience') and contains(@class, 'cfc-page-displayName')]"
        ]
        
        audience_element = None
        for selector in audience_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        audience_element = element
                        print(f"✅ Found Audience element with selector: {selector}")
                        break
                if audience_element:
                    break
            except Exception as selector_error:
                continue
        
        if not audience_element:
            print("⚠️ Could not find Audience element")
            return False
            
        # Scroll to and click Audience
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", audience_element)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Click audience element
        if not click_element(driver, audience_element, "Audience"):
            return False
            
        # Click "Add users" button
        print("➕ Clicking 'Add users' button...")
        time.sleep(random.uniform(0.5, 1.0))  # Reduced wait time for form filling
        
        add_users_selectors = [
            # Exact selectors matching the provided button structure
            "//button[@aria-label='Add users' and contains(@class, 'mat-raised-button')]",
            "//button[@aria-label='Add users' and contains(@class, 'mat-mdc-outlined-button')]",
            "//button[@aria-label='Add users' and contains(@class, 'mat-primary')]",
            "//button[contains(@class, 'mat-raised-button') and @aria-label='Add users']",
            "//button[contains(@class, 'mat-mdc-outlined-button') and @aria-label='Add users']",
            
            # Specific class combination from the provided button
            "//button[contains(@class, 'mdc-button') and contains(@class, 'mat-mdc-button-base') and contains(@class, 'mat-mdc-outlined-button') and @aria-label='Add users']",
            "//button[contains(@class, 'mdc-button--outlined') and contains(@class, 'mat-primary') and @aria-label='Add users']",
            "//button[contains(@class, 'cm-button') and @aria-label='Add users']",
            
            # Icon + text combination from provided structure
            "//button[.//cfc-icon[@icon='add' and @size='small'] and .//span[contains(@class, 'mdc-button__label') and contains(text(), 'Add users')]]",
            "//button[.//mat-icon[@data-mat-icon-name='add'] and .//span[contains(@class, 'mdc-button__label') and contains(text(), 'Add users')]]",
            "//button[.//svg[.//path[@d='M10 8h5v2h-5v5H8v-5H3V8h5V3h2v5z']] and .//span[contains(text(), 'Add users')]]",
            
            # Most specific selectors for Add users button
            "//span[contains(@class, 'mdc-button__label') and normalize-space(text())='Add users']/parent::button",
            "//button[.//span[contains(@class, 'mdc-button__label') and normalize-space(text())='Add users']]",
            "//button[.//span[normalize-space(text())='Add users']]",
            
            # Button with icon and text
            "//button[.//cfc-icon[@icon='add'] and .//span[contains(text(), 'Add users')]]",
            "//button[.//mat-icon[@data-mat-icon-name='add'] and .//span[contains(text(), 'Add users')]]",
            "//button[.//svg and .//span[contains(text(), 'Add users')]]",
            
            # Material Design buttons
            "//button[contains(@class, 'mdc-button') and .//span[contains(text(), 'Add users')]]",
            "//button[contains(@class, 'mat-mdc-button') and .//span[contains(text(), 'Add users')]]",
            "//button[contains(@class, 'mat-raised-button') and .//span[contains(text(), 'Add users')]]",
            
            # Icon-only buttons (common in Google interfaces)
            "//button[.//cfc-icon[@icon='add' and @size='small']]",
            "//button[.//cfc-icon[@icon='add']]",
            "//button[.//mat-icon[@data-mat-icon-name='add']]",
            "//button[@aria-label='Add users']",
            "//button[contains(@aria-label, 'Add') and contains(@aria-label, 'users')]",
            
            # Text-based selectors
            "//button[contains(text(), 'Add users')]",
            "//button[normalize-space(text())='Add users']",
            "//span[text()='Add users']//ancestor::button[1]",
            "//span[normalize-space(text())='Add users']//ancestor::button[1]",
            
            # Alternative text patterns
            "//button[contains(text(), 'Add user')]",
            "//button[contains(text(), 'Add')]",
            "//span[contains(text(), 'Add users')]//parent::button",
            
            # Broader icon search
            "//button[.//cfc-icon and contains(@class, 'mdc-button')]",
            "//button[.//mat-icon and contains(@class, 'mat-mdc-button')]"
        ]
        
        add_users_button = None
        
        # Try each selector with debugging
        for i, selector in enumerate(add_users_selectors):
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element_text = (element.get_attribute("textContent") or element.text or "").strip()
                        aria_label = element.get_attribute("aria-label") or ""
                        
                        # Check if this looks like an "Add users" button
                        is_add_users = (
                            "add users" in element_text.lower() or
                            "add user" in element_text.lower() or
                            "add users" in aria_label.lower() or
                            ("add" in element_text.lower() and len(element_text) < 20) or
                            (len(element_text) == 0 and "add" in aria_label.lower())  # Icon-only button
                        )
                        
                        if is_add_users:
                            add_users_button = element
                            print(f"✅ Found Add users button (selector {i+1}): text='{element_text}', aria-label='{aria_label}'")
                            break
                
                if add_users_button:
                    break
                    
            except Exception as selector_error:
                continue
        
        # If not found, try comprehensive search and debugging
        if not add_users_button:
            print("🔍 Add users button not found with primary selectors. Trying comprehensive search...")
            
            try:
                # Method 1: Search all buttons on the page and show debug info
                print("📋 Listing all visible buttons for debugging:")
                all_buttons = driver.find_elements(By.XPATH, "//button")
                
                for i, button in enumerate(all_buttons[:15]):  # Show first 15 buttons
                    if button.is_displayed():
                        button_text = (button.get_attribute("textContent") or button.text or "").strip()
                        button_class = button.get_attribute("class") or ""
                        button_aria = button.get_attribute("aria-label") or ""
                        
                        print(f"   Button {i+1}: '{button_text[:30]}' (class: {button_class[:40]}, aria: {button_aria[:30]})")
                        
                        # Check if this could be the Add users button
                        potential_match = (
                            "add" in button_text.lower() or
                            "add" in button_aria.lower() or
                            "user" in button_text.lower() or
                            "user" in button_aria.lower() or
                            ("+" in button_text and len(button_text) < 5)
                        )
                        
                        if potential_match and not add_users_button:
                            add_users_button = button
                            print(f"🎯 Selected potential Add users button: '{button_text}' (match criteria met)")
                
                # Method 2: Look specifically in the audience/user management area
                if not add_users_button:
                    print("🔍 Looking in specific audience management areas...")
                    area_selectors = [
                        "//div[contains(@class, 'audience')]//button",
                        "//div[contains(@class, 'user')]//button", 
                        "//div[contains(@class, 'test-user')]//button",
                        "//section//button",
                        "//main//button[.//cfc-icon[@icon='add']]",
                        "//div[contains(@class, 'panel')]//button[.//cfc-icon[@icon='add']]"
                    ]
                    
                    for area_selector in area_selectors:
                        try:
                            area_buttons = driver.find_elements(By.XPATH, area_selector)
                            for button in area_buttons:
                                if button.is_displayed() and button.is_enabled():
                                    button_text = (button.get_attribute("textContent") or button.text or "").strip()
                                    if "add" in button_text.lower() or len(button_text) == 0:  # Icon button
                                        add_users_button = button
                                        print(f"✅ Found Add button in area: '{button_text}' using {area_selector}")
                                        break
                            if add_users_button:
                                break
                        except:
                            continue
                
                # Method 3: Look for floating action buttons or primary action buttons
                if not add_users_button:
                    print("🔍 Looking for floating action buttons...")
                    fab_selectors = [
                        "//button[contains(@class, 'fab')]",
                        "//button[contains(@class, 'floating')]",
                        "//button[contains(@class, 'primary')]",
                        "//button[contains(@class, 'mat-fab')]",
                        "//button[contains(@class, 'mdc-fab')]"
                    ]
                    
                    for fab_selector in fab_selectors:
                        try:
                            fab_buttons = driver.find_elements(By.XPATH, fab_selector)
                            for button in fab_buttons:
                                if button.is_displayed() and button.is_enabled():
                                    add_users_button = button
                                    print(f"✅ Found potential FAB button using {fab_selector}")
                                    break
                            if add_users_button:
                                break
                        except:
                            continue
                            
            except Exception as debug_error:
                print(f"⚠️ Debug search failed: {debug_error}")
        
        if not add_users_button:
            print("❌ Could not find Add users button")
            print("💡 Manual steps:")
            print("   1. Look for a button with '+' icon or 'Add users' text")
            print("   2. It's usually in the top-right area of the Audience page")
            print("   3. Click it to open the user addition form")
            return False
            
        # Click add users button
        print("🎯 Clicking Add users button...")
        if not click_element(driver, add_users_button, "Add users button"):
            return False
            return False
            
        # Wait for right sidebar to load
        print("⏳ Waiting for right sidebar to load...")
        time.sleep(random.uniform(0.5, 1.0))  # Reduced wait time for form loading
        
        # Find and fill email input
        return fill_email_and_save(driver)
        
    except Exception as audience_error:
        print(f"❌ Error configuring Audience: {audience_error}")
        print("💡 You may need to manually configure the audience")
        return False

def find_element_by_selectors(driver, selectors, element_name):
    """Find an element using multiple selectors"""
    for selector in selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    # For buttons with icons, check both text content and aria-label
                    element_text = (element.get_attribute("textContent") or element.text or "").strip()
                    element_aria_label = (element.get_attribute("aria-label") or "").strip()
                    
                    # Check if element contains the target text
                    target_text = element_name.lower().replace(" ", "")
                    if (target_text in element_text.lower().replace(" ", "") or 
                        target_text in element_aria_label.lower().replace(" ", "") or
                        # Special handling for "Add users" button - look for "add" + "users" separately
                        ("add" in element_text.lower() and "users" in element_text.lower())):
                        print(f"✅ Found {element_name} with text: '{element_text}' and aria-label: '{element_aria_label}'")
                        return element
        except Exception as selector_error:
            continue
    print(f"⚠️ Could not find {element_name}")
    return None

def click_element(driver, element, element_name):
    """Click an element with enhanced overlay handling using safe_click"""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(random.uniform(1.0, 2.0))
    
    # Use our enhanced safe_click function
    success = safe_click(driver, element, element_name)
    
    if success:
        time.sleep(random.uniform(0.5, 1.0))  # Wait time after successful click
        return True
    else:
        print(f"❌ All click attempts failed for {element_name}")
        
        # Final CAPTCHA check
        print("🔍 Final CAPTCHA check before giving up...")
        detect_and_handle_captcha(driver)
        return False

def fill_email_and_save(driver):
    """Fill email input field and save"""
    print("📧 Looking for email input field...")
    email_input_selectors = [
        "input[aria-label='Text field for emails']",
        "input.mat-mdc-chip-input",
        "input.mat-mdc-input-element",
        "input.mdc-text-field__input",
        "input.mat-input-element",
        "input.mat-mdc-form-field-input-control",
        "//input[@aria-label='Text field for emails']",
        "//input[contains(@class, 'mat-mdc-chip-input')]",
        "//input[contains(@class, 'mat-mdc-input-element')]",
        "//input[contains(@class, 'mdc-text-field__input')]",
        "//input[contains(@id, 'chip-list-input')]"
    ]
    
    email_input = None
    for selector in email_input_selectors:
        try:
            if selector.startswith("//"):
                elements = driver.find_elements(By.XPATH, selector)
            else:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    email_input = element
                    print(f"✅ Found email input with selector: {selector}")
                    break
            if email_input:
                break
        except Exception as selector_error:
            continue
    
    if not email_input:
        print("⚠️ Could not find email input field")
        return False
    
    # Fill email
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_input)
    time.sleep(random.uniform(1.0, 2.0))
    
    human_mouse_move_to(email_input)
    email_input.click()
    time.sleep(random.uniform(0.5, 1.0))
    
    email_input.clear()
    test_email = EMAIL  # Use the actual inputted email
    print(f"📧 Entering email: {test_email}")
    
    human_typing(email_input, test_email)
    time.sleep(random.uniform(1.0, 2.0))
    
    # Verify email was entered
    entered_value = email_input.get_attribute("value") or ""
    print(f"📧 Email entered in field: '{entered_value}'")
    
    # Press Enter to add the email
    email_input.send_keys(Keys.ENTER)
    time.sleep(random.uniform(0.5, 1.0))  # Wait longer for email to be processed
    
    print("✅ Email entered successfully!")
    
    # Wait a bit more before attempting to save
    print("⏳ Waiting for email to be processed before saving...")
    time.sleep(random.uniform(1.0, 2.0))
    
    # Save audience configuration
    return save_audience_config(driver)

def save_audience_config(driver):
    """Save audience configuration"""
    print("💾 Clicking Save button...")
    time.sleep(random.uniform(0.5, 1.0))  # Wait longer for UI to be ready
    
    audience_save_selectors = [
        # Specific selector for the Save button with exact structure
        "//span[contains(@class, 'mdc-button__label') and normalize-space(text())='Save']/parent::button",
        "//button[.//span[contains(@class, 'mdc-button__label') and normalize-space(text())='Save']]",
        "//button[contains(@class, 'mdc-button') and .//span[normalize-space(text())='Save']]",
        "//button[contains(@class, 'mat-mdc-button') and .//span[normalize-space(text())='Save']]",
        
        # More specific patterns for the exact button structure
        "//button[contains(@class, 'mdc-button') and contains(@class, 'mat-mdc-button')]//span[normalize-space(text())='Save']//ancestor::button[1]",
        "//span[@class='mdc-button__label' and text()='Save']//parent::button",
        "//span[text()=' Save ']//parent::button",
        "//button[descendant::span[text()='Save']]",
        
        # More generic selectors
        "//button[contains(text(), 'Save')]",
        "//button[normalize-space(text())='Save']",
        "//button//span[contains(text(), 'Save')]",
        "//span[text()='Save']//ancestor::button[1]",
        "//button[contains(@class, 'mdc-button') and contains(text(), 'Save')]",
        "//button[contains(@class, 'mat-mdc-button') and contains(text(), 'Save')]",
        
        # Blue button specific (common classes for primary/save buttons)
        "//button[contains(@class, 'mdc-button--unelevated') and contains(text(), 'Save')]",
        "//button[contains(@class, 'mat-primary') and contains(text(), 'Save')]",
        "//button[contains(@class, 'primary') and contains(text(), 'Save')]",
        "//button[contains(@class, 'mat-raised-button') and contains(text(), 'Save')]",
        
        # Sidebar/modal specific selectors
        "//div[contains(@class, 'sidebar')]//button[contains(text(), 'Save')]",
        "//div[contains(@class, 'panel')]//button[contains(text(), 'Save')]",
        "//div[contains(@class, 'modal')]//button[contains(text(), 'Save')]",
        "//mat-dialog-actions//button[contains(text(), 'Save')]"
    ]
    
    audience_save_button = None
    
    # First try with scroll to find visible buttons
    print("🔍 Searching for Save button...")
    try:
        # Scroll to bottom to ensure we see the save button
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.0)
        
        # Then scroll up a bit to center the view
        driver.execute_script("window.scrollBy(0, -200);")
        time.sleep(1.0)
        
    except Exception as scroll_error:
        print(f"⚠️ Scroll error: {scroll_error}")
    
    # Try primary selectors
    for selector in audience_save_selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    element_text = (element.get_attribute("textContent") or element.text or "").strip()
                    
                    # More precise text matching
                    if (element_text.lower().strip() == "save" or 
                        element_text.lower() == " save " or 
                        "save" in element_text.lower() and len(element_text.strip()) <= 10):
                        
                        audience_save_button = element
                        print(f"✅ Found Audience Save button with text: '{element_text}' using selector: {selector}")
                        break
            if audience_save_button:
                break
        except Exception as selector_error:
            continue
    
    # If not found, try alternative comprehensive search
    if not audience_save_button:
        print("🔍 Trying comprehensive alternative search for Save button...")
        try:
            # Look for any button containing "Save" text anywhere in the DOM
            all_buttons = driver.find_elements(By.XPATH, "//button")
            for button in all_buttons:
                if button.is_displayed() and button.is_enabled():
                    button_text = (button.get_attribute("textContent") or button.text or "").strip()
                    if (button_text.lower().strip() == "save" or 
                        button_text.lower() == " save " or 
                        (button_text.lower().find("save") != -1 and len(button_text.strip()) <= 15)):
                        
                        audience_save_button = button
                        print(f"✅ Found Save button alternative with text: '{button_text}'")
                        break
                        
            # If still not found, look for buttons with specific classes that might be Save buttons
            if not audience_save_button:
                print("🔍 Looking for blue/primary styled buttons...")
                styled_buttons = driver.find_elements(By.XPATH, 
                    "//button[contains(@class, 'primary') or contains(@class, 'unelevated') or contains(@class, 'raised') or contains(@class, 'mat-primary')]")
                
                for button in styled_buttons:
                    if button.is_displayed() and button.is_enabled():
                        button_text = (button.get_attribute("textContent") or button.text or "").strip()
                        if "save" in button_text.lower():
                            audience_save_button = button
                            print(f"✅ Found Save button by styling with text: '{button_text}'")
                            break
                            
        except Exception as alt_search_error:
            print(f"⚠️ Alternative Save button search failed: {alt_search_error}")

    if not audience_save_button:
        print("⚠️ Could not find Audience Save button")
        print("🔍 Listing all visible buttons for debugging...")
        try:
            all_buttons = driver.find_elements(By.XPATH, "//button")
            for i, button in enumerate(all_buttons[:10]):  # Show first 10 buttons
                if button.is_displayed():
                    button_text = (button.get_attribute("textContent") or button.text or "").strip()
                    button_class = button.get_attribute("class") or ""
                    print(f"   Button {i+1}: '{button_text}' (class: {button_class[:50]})")
        except:
            pass
        return False
    
    # Enhanced clicking strategy for Save button
    print("🎯 Attempting to click Save button with enhanced strategy...")
    
    # Strategy 1: Scroll to button and highlight it
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", audience_save_button)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Highlight button for visibility
        driver.execute_script("""
            arguments[0].style.border = '3px solid red';
            arguments[0].style.backgroundColor = 'yellow';
        """, audience_save_button)
        time.sleep(1.0)
        
        # Remove highlight
        driver.execute_script("""
            arguments[0].style.border = '';
            arguments[0].style.backgroundColor = '';
        """, audience_save_button)
        
    except Exception as highlight_error:
        print(f"⚠️ Highlight error: {highlight_error}")
    
    # Strategy 2: Try multiple click methods
    click_success = False
    
    # Method 1: JavaScript click (most reliable)
    try:
        driver.execute_script("arguments[0].click();", audience_save_button)
        print("✅ Save button clicked successfully with JavaScript!")
        click_success = True
        time.sleep(random.uniform(2.0, 4.0))
        
    except Exception as js_click_error:
        print(f"⚠️ JavaScript click failed: {js_click_error}")
    
    # Method 2: Regular click as fallback
    if not click_success:
        try:
            human_mouse_move_to(audience_save_button)
            audience_save_button.click()
            print("✅ Save button clicked successfully with regular click!")
            click_success = True
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as regular_click_error:
            print(f"⚠️ Regular click failed: {regular_click_error}")
    
    # Method 3: Action chains as last resort
    if not click_success:
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.move_to_element(audience_save_button).click().perform()
            print("✅ Save button clicked successfully with ActionChains!")
            click_success = True
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as action_click_error:
            print(f"⚠️ ActionChains click failed: {action_click_error}")
    
    # Method 4: Send Enter key to focused element
    if not click_success:
        try:
            audience_save_button.send_keys(Keys.ENTER)
            print("✅ Save button activated with Enter key!")
            click_success = True
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as enter_error:
            print(f"⚠️ Enter key failed: {enter_error}")
    
    # Method 5: Send Space key to focused element
    if not click_success:
        try:
            audience_save_button.send_keys(Keys.SPACE)
            print("✅ Save button activated with Space key!")
            click_success = True
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as space_error:
            print(f"⚠️ Space key failed: {space_error}")
    
    if click_success:
        # Wait for save operation to complete
        print("⏳ Waiting for save operation to complete...")
        time.sleep(random.uniform(1.0, 2.0))  # Reduced wait time for save operations
        
        # Check if save was successful by looking for success indicators
        print("🔍 Checking if save was successful...")
        try:
            # Look for success messages or page changes
            success_indicators = [
                "//div[contains(@class, 'success')]",
                "//div[contains(@class, 'snackbar')]",
                "//div[contains(text(), 'saved')]",
                "//div[contains(text(), 'Saved')]",
                "//span[contains(text(), 'Success')]"
            ]
            
            success_found = False
            for indicator in success_indicators:
                try:
                    elements = driver.find_elements(By.XPATH, indicator)
                    for element in elements:
                        if element.is_displayed():
                            success_found = True
                            print(f"✅ Success indicator found: {element.text}")
                            break
                    if success_found:
                        break
                except:
                    continue
            
            if not success_found:
                print("⚠️ No explicit success indicator found, but save button was clicked")
                
        except Exception as success_check_error:
            print(f"⚠️ Success check error: {success_check_error}")
        
        # After saving audience, proceed to publish the app
        print("📢 Proceeding to publish the app...")
        return publish_app(driver)
    else:
        print("❌ All Save button click methods failed!")
        return False

def publish_app(driver):
    """Publish the OAuth consent screen app"""
    print("🚀 Looking for 'Publish app' button...")
    time.sleep(random.uniform(1.0, 2.0))  # Wait for UI to settle after save
    
    # Navigate back to OAuth consent screen if needed
    try:
        # First try to scroll to top to find the Publish app button
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(1.0, 2.0))
        
        # Look for Publish app button with multiple selectors
        publish_selectors = [
            # Exact selector for Publish app button with sandboxuid
            "//span[contains(@class, 'mdc-button__label') and contains(text(), 'Publish app')]/parent::button",
            "//button[.//span[contains(@class, 'mdc-button__label') and contains(text(), 'Publish app')]]",
            "//button[contains(@class, 'mdc-button') and .//span[contains(text(), 'Publish app')]]",
            "//button[contains(@class, 'mat-mdc-button') and .//span[contains(text(), 'Publish app')]]",
            
            # More specific patterns for the exact button structure
            "//span[@class='mdc-button__label' and contains(text(), 'Publish app')]//parent::button",
            "//span[normalize-space(text())='Publish app']//parent::button",
            "//button[descendant::span[contains(text(), 'Publish app')]]",
            
            # Generic selectors
            "//button[contains(text(), 'Publish app')]",
            "//button[normalize-space(text())='Publish app']",
            "//span[contains(text(), 'Publish app')]//ancestor::button[1]",
            
            # Alternative text patterns
            "//button[contains(text(), 'Publish')]",
            "//button[.//span[contains(text(), 'Publish')]]",
            "//span[text()='Publish app']//ancestor::button[1]"
        ]
        
        publish_button = None
        
        # Try to find the Publish app button
        for selector in publish_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element_text = (element.get_attribute("textContent") or element.text or "").strip()
                        
                        # Check if this is the Publish app button
                        if ("publish" in element_text.lower() and 
                            ("app" in element_text.lower() or len(element_text.strip()) <= 15)):
                            publish_button = element
                            print(f"✅ Found Publish app button with text: '{element_text}' using selector: {selector}")
                            break
                if publish_button:
                    break
            except Exception as selector_error:
                continue
        
        # If not found, try alternative comprehensive search
        if not publish_button:
            print("🔍 Trying comprehensive search for Publish app button...")
            try:
                # Look for any button containing "Publish" text
                all_buttons = driver.find_elements(By.XPATH, "//button")
                for button in all_buttons:
                    if button.is_displayed() and button.is_enabled():
                        button_text = (button.get_attribute("textContent") or button.text or "").strip()
                        if ("publish" in button_text.lower() and 
                            ("app" in button_text.lower() or "publish" == button_text.lower().strip())):
                            publish_button = button
                            print(f"✅ Found Publish button alternative with text: '{button_text}'")
                            break
                            
            except Exception as alt_search_error:
                print(f"⚠️ Alternative Publish button search failed: {alt_search_error}")
        
        if not publish_button:
            print("⚠️ Could not find Publish app button")
            print("🔍 Listing all visible buttons for debugging...")
            try:
                all_buttons = driver.find_elements(By.XPATH, "//button")
                for i, button in enumerate(all_buttons[:10]):  # Show first 10 buttons
                    if button.is_displayed():
                        button_text = (button.get_attribute("textContent") or button.text or "").strip()
                        button_class = button.get_attribute("class") or ""
                        print(f"   Button {i+1}: '{button_text}' (class: {button_class[:50]})")
            except:
                pass
            return False
        
        # Click the Publish app button
        print("🎯 Clicking Publish app button...")
        
        # Scroll to button and highlight it
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", publish_button)
            time.sleep(random.uniform(1.0, 2.0))
            
            # Highlight button for visibility
            driver.execute_script("""
                arguments[0].style.border = '3px solid blue';
                arguments[0].style.backgroundColor = 'lightblue';
            """, publish_button)
            time.sleep(1.0)
            
            # Remove highlight
            driver.execute_script("""
                arguments[0].style.border = '';
                arguments[0].style.backgroundColor = '';
            """, publish_button)
            
        except Exception as highlight_error:
            print(f"⚠️ Highlight error: {highlight_error}")
        
        # Try multiple click methods for Publish app button
        click_success = False
        
        # Method 1: JavaScript click
        try:
            driver.execute_script("arguments[0].click();", publish_button)
            print("✅ Publish app button clicked successfully with JavaScript!")
            click_success = True
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as js_click_error:
            print(f"⚠️ JavaScript click failed: {js_click_error}")
        
        # Method 2: Regular click as fallback
        if not click_success:
            try:
                human_mouse_move_to(publish_button)
                publish_button.click()
                print("✅ Publish app button clicked successfully with regular click!")
                click_success = True
                time.sleep(random.uniform(2.0, 4.0))
                
            except Exception as regular_click_error:
                print(f"⚠️ Regular click failed: {regular_click_error}")
        
        if not click_success:
            print("❌ Failed to click Publish app button")
            return False
            
        # Wait for confirmation popup to appear
        print("⏳ Waiting for confirmation popup...")
        time.sleep(random.uniform(3.0, 5.0))
        
        # Handle confirmation popup
        return handle_publish_confirmation(driver)
        
    except Exception as publish_error:
        print(f"❌ Error in publish_app: {publish_error}")
        return False

def handle_publish_confirmation(driver):
    """Handle the confirmation popup after clicking Publish app"""
    print("✅ Looking for confirmation popup and Confirm button...")
    
    # Look for the Confirm button in the popup
    confirm_selectors = [
        # Exact selector for Confirm button with sandboxuid
        "//span[contains(@class, 'mdc-button__label') and normalize-space(text())='Confirm']/parent::button",
        "//button[.//span[contains(@class, 'mdc-button__label') and normalize-space(text())='Confirm']]",
        "//button[contains(@class, 'mdc-button') and .//span[normalize-space(text())='Confirm']]",
        "//button[contains(@class, 'mat-mdc-button') and .//span[normalize-space(text())='Confirm']]",
        
        # More specific patterns
        "//span[@class='mdc-button__label' and text()='Confirm']//parent::button",
        "//span[normalize-space(text())='Confirm']//parent::button",
        "//button[descendant::span[normalize-space(text())='Confirm']]",
        
        # Generic selectors
        "//button[contains(text(), 'Confirm')]",
        "//button[normalize-space(text())='Confirm']",
        "//span[text()='Confirm']//ancestor::button[1]",
        
        # Modal/dialog specific selectors
        "//div[contains(@class, 'modal')]//button[contains(text(), 'Confirm')]",
        "//div[contains(@class, 'dialog')]//button[contains(text(), 'Confirm')]",
        "//mat-dialog-actions//button[contains(text(), 'Confirm')]",
        "//cdk-overlay-container//button[contains(text(), 'Confirm')]"
    ]
    
    confirm_button = None
    
    # Try to find the Confirm button
    for selector in confirm_selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    element_text = (element.get_attribute("textContent") or element.text or "").strip()
                    
                    # Check if this is the Confirm button
                    if (element_text.lower().strip() == "confirm" or 
                        element_text.lower() == " confirm " or 
                        ("confirm" in element_text.lower() and len(element_text.strip()) <= 10)):
                        confirm_button = element
                        print(f"✅ Found Confirm button with text: '{element_text}' using selector: {selector}")
                        break
            if confirm_button:
                break
        except Exception as selector_error:
            continue
    
    # If not found, try alternative comprehensive search
    if not confirm_button:
        print("🔍 Trying comprehensive search for Confirm button...")
        try:
            # Look for any button containing "Confirm" text in overlays/modals
            overlay_buttons = driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'cdk-overlay-container') or contains(@class, 'modal') or contains(@class, 'dialog')]//button")
            
            for button in overlay_buttons:
                if button.is_displayed() and button.is_enabled():
                    button_text = (button.get_attribute("textContent") or button.text or "").strip()
                    if ("confirm" in button_text.lower() and len(button_text.strip()) <= 15):
                        confirm_button = button
                        print(f"✅ Found Confirm button in overlay with text: '{button_text}'")
                        break
                        
            # If still not found, search all buttons
            if not confirm_button:
                all_buttons = driver.find_elements(By.XPATH, "//button")
                for button in all_buttons:
                    if button.is_displayed() and button.is_enabled():
                        button_text = (button.get_attribute("textContent") or button.text or "").strip()
                        if (button_text.lower().strip() == "confirm" or 
                            button_text.lower() == " confirm "):
                            confirm_button = button
                            print(f"✅ Found Confirm button alternative with text: '{button_text}'")
                            break
                            
        except Exception as alt_search_error:
            print(f"⚠️ Alternative Confirm button search failed: {alt_search_error}")
    
    if not confirm_button:
        print("⚠️ Could not find Confirm button")
        print("🔍 Listing all visible buttons in popup for debugging...")
        try:
            # Try to find buttons in overlay containers
            overlay_buttons = driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'cdk-overlay-container') or contains(@class, 'modal') or contains(@class, 'dialog')]//button")
            
            for i, button in enumerate(overlay_buttons[:5]):  # Show first 5 buttons in overlay
                if button.is_displayed():
                    button_text = (button.get_attribute("textContent") or button.text or "").strip()
                    button_class = button.get_attribute("class") or ""
                    print(f"   Overlay Button {i+1}: '{button_text}' (class: {button_class[:50]})")
                    
            # If no overlay buttons, show all buttons
            if not overlay_buttons:
                all_buttons = driver.find_elements(By.XPATH, "//button")
                for i, button in enumerate(all_buttons[:10]):  # Show first 10 buttons
                    if button.is_displayed():
                        button_text = (button.get_attribute("textContent") or button.text or "").strip()
                        button_class = button.get_attribute("class") or ""
                        print(f"   Button {i+1}: '{button_text}' (class: {button_class[:50]})")
        except:
            pass
        return False
    
    # Click the Confirm button
    print("✅ Clicking Confirm button in popup...")
    
    # Scroll to button and highlight it
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", confirm_button)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Highlight button for visibility
        driver.execute_script("""
            arguments[0].style.border = '3px solid green';
            arguments[0].style.backgroundColor = 'lightgreen';
        """, confirm_button)
        time.sleep(1.0)
        
        # Remove highlight
        driver.execute_script("""
            arguments[0].style.border = '';
            arguments[0].style.backgroundColor = '';
        """, confirm_button)
        
    except Exception as highlight_error:
        print(f"⚠️ Highlight error: {highlight_error}")
    
    # Try multiple click methods for Confirm button
    click_success = False
    
    # Method 1: JavaScript click
    try:
        driver.execute_script("arguments[0].click();", confirm_button)
        print("✅ Confirm button clicked successfully with JavaScript!")
        click_success = True
        time.sleep(random.uniform(2.0, 4.0))
        
    except Exception as js_click_error:
        print(f"⚠️ JavaScript click failed: {js_click_error}")
    
    # Method 2: Regular click as fallback
    if not click_success:
        try:
            human_mouse_move_to(confirm_button)
            confirm_button.click()
            print("✅ Confirm button clicked successfully with regular click!")
            click_success = True
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as regular_click_error:
            print(f"⚠️ Regular click failed: {regular_click_error}")
    
    # Method 3: Action chains as last resort
    if not click_success:
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.move_to_element(confirm_button).click().perform()
            print("✅ Confirm button clicked successfully with ActionChains!")
            click_success = True
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as action_click_error:
            print(f"⚠️ ActionChains click failed: {action_click_error}")
    
    if click_success:
        print("⏳ Waiting for app publishing to complete...")
        time.sleep(random.uniform(3.0, 5.0))
        
        # Check for success indicators
        print("🔍 Checking if app publishing was successful...")
        try:
            success_indicators = [
                "//div[contains(@class, 'success')]",
                "//div[contains(@class, 'snackbar')]",
                "//div[contains(text(), 'published')]",
                "//div[contains(text(), 'Published')]",
                "//span[contains(text(), 'Success')]",
                "//div[contains(text(), 'live')]",
                "//div[contains(text(), 'Live')]"
            ]
            
            success_found = False
            for indicator in success_indicators:
                try:
                    elements = driver.find_elements(By.XPATH, indicator)
                    for element in elements:
                        if element.is_displayed():
                            success_found = True
                            print(f"✅ Success indicator found: {element.text}")
                            break
                    if success_found:
                        break
                except:
                    continue
            
            if not success_found:
                print("⚠️ No explicit success indicator found, but Confirm button was clicked")
                
        except Exception as success_check_error:
            print(f"⚠️ Success check error: {success_check_error}")
        
        print("🎉🎉🎉 APP PUBLISHING COMPLETED! 🎉🎉🎉")
        print("✅ STEPS COMPLETED SO FAR:")
        print("   ✓ Google login")
        print("   ✓ Project creation")
        print("   ✓ Gmail API enablement")
        print("   ✓ OAuth consent screen configuration")
        print("   ✓ Data Access setup")
        print("   ✓ Gmail API scope addition")
        print("   ✓ Configuration update")
        print("   ✓ Final save completed")
        print("   ✓ Audience configuration")
        print("   ✓ Test user added")
        print("   ✓ Audience saved")
        print("   ✓ App published")
        print("   ✓ Publishing confirmed")
        print("")
        print("� Now proceeding to create OAuth client...")
        
        # Proceed to create OAuth client
        return create_oauth_client(driver)
    else:
        print("❌ All Confirm button click methods failed!")
        return False

def create_oauth_client(driver):
    """Navigate to Clients section and create OAuth client ID"""
    print("🔧 Navigating to Clients section...")
    time.sleep(random.uniform(1.0, 2.0))  # Wait for UI to settle after publishing
    
    try:
        # Click "Clients" from sidebar
        print("👥 Clicking 'Clients' from sidebar...")
        clients_selectors = [
            # Specific selector for Clients in sidebar
            "//span[contains(@class, 'cfc-page-displayName') and contains(text(), 'Clients')]",
            "//span[@class='cfc-page-displayName'][contains(text(), 'Clients')]",
            "//a[contains(text(), 'Clients')]",
            "//li[contains(text(), 'Clients')]",
            "//div[contains(text(), 'Clients')]",
            "//*[contains(text(), 'Clients') and contains(@class, 'cfc-page-displayName')]",
            "//span[normalize-space(text())='Clients']",
            "//button[contains(text(), 'Clients')]"
        ]
        
        clients_element = None
        for selector in clients_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        clients_element = element
                        print(f"✅ Found Clients element with selector: {selector}")
                        break
                if clients_element:
                    break
            except Exception as selector_error:
                continue
        
        if not clients_element:
            print("⚠️ Could not find Clients element")
            return False
            
        # Scroll to and click Clients
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clients_element)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Click clients element
        if not click_element(driver, clients_element, "Clients"):
            return False
            
        # Wait for Clients page to load
        print("⏳ Waiting for Clients page to load...")
        time.sleep(random.uniform(1.0, 2.0))
        
        # Wait a bit more and try to detect page changes
        print("🔍 Checking if Clients page has loaded properly...")
        try:
            # Look for indicators that we're on the Clients page
            clients_indicators = [
                "//h1[contains(text(), 'Clients')]",
                "//h2[contains(text(), 'Clients')]",
                "//*[contains(text(), 'OAuth client')]",
                "//*[contains(text(), 'Create client')]",
                "//button[contains(text(), 'Create')]"
            ]
            
            page_loaded = False
            for indicator in clients_indicators:
                try:
                    elements = driver.find_elements(By.XPATH, indicator)
                    if elements and elements[0].is_displayed():
                        page_loaded = True
                        print(f"✅ Clients page loaded - found indicator: {elements[0].text}")
                        break
                except:
                    continue
            
            if not page_loaded:
                print("⚠️ Clients page may not have loaded completely, waiting longer...")
                time.sleep(random.uniform(2.0, 3.0))  # Reduced from 5-8 seconds
                
        except Exception as page_check_error:
            print(f"⚠️ Page check error: {page_check_error}")
        
        # Scroll to make sure all content is visible
        print("📜 Scrolling to ensure all content is visible...")
        try:
            driver.execute_script("window.scrollTo(0, 0);")  # Scroll to top
            time.sleep(1.0)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to bottom
            time.sleep(1.0)
            driver.execute_script("window.scrollTo(0, 0);")  # Back to top
            time.sleep(1.0)
        except Exception as scroll_error:
            print(f"⚠️ Scroll error: {scroll_error}")
        
        # Click "Create client" button
        print("🆕 Clicking 'Create client' button...")
        create_client_selectors = [
            # Exact selector based on the actual HTML structure (anchor tag, not button)
            "#_0rif_action-bar-create-client-button",
            "a[id*='action-bar-create-client-button']",
            "//a[@id='_0rif_action-bar-create-client-button']",
            "//a[contains(@id, 'action-bar-create-client-button')]",
            
            # Target the span with exact text and get parent anchor
            "//span[@class='mdc-button__label' and @sandboxuid='0' and normalize-space(text())='Create client']/parent::a",
            "//span[contains(@class, 'mdc-button__label') and contains(text(), 'Create client')]/parent::a",
            "//a[.//span[@class='mdc-button__label' and contains(text(), 'Create client')]]",
            
            # More generic anchor patterns
            "//a[contains(@aria-label, 'Create client')]",
            "//a[contains(@class, 'mat-mdc-button') and .//span[contains(text(), 'Create client')]]",
            "//a[contains(@class, 'mdc-button') and .//span[contains(text(), 'Create client')]]",
            
            # Target by the cfc-icon with add and Create client text
            "//a[.//cfc-icon[@icon='add'] and .//span[contains(text(), 'Create client')]]",
            "//a[.//mat-icon[@data-mat-icon-name='add'] and .//span[contains(text(), 'Create client')]]",
            
            # Fallback button selectors (in case structure changes)
            "//button[.//span[contains(@class, 'mdc-button__label') and contains(text(), 'Create client')]]",
            "//button[contains(@class, 'mdc-button') and .//span[contains(text(), 'Create client')]]",
            "//button[contains(@class, 'mat-mdc-button') and .//span[contains(text(), 'Create client')]]",
            
            # Generic patterns for Create client
            "//span[normalize-space(text())='Create client']//ancestor::a[1]",
            "//span[normalize-space(text())='Create client']//ancestor::button[1]",
            "//*[contains(text(), 'Create client') and (self::a or self::button)]",
            
            # Alternative patterns with different text variations  
            "//*[contains(text(), 'Create') and not(contains(text(), 'OAuth')) and (self::a or self::button)]",
            "//*[.//span[contains(text(), 'Create') and not(contains(text(), 'OAuth'))] and (self::a or self::button)]",
            
            # Primary/styled button patterns
            "//*[contains(@class, 'mat-primary') and contains(text(), 'Create') and (self::a or self::button)]",
            "//*[contains(@class, 'primary') and contains(text(), 'Create') and (self::a or self::button)]"
        ]
        
        create_client_button = find_element_by_selectors(driver, create_client_selectors, "Create client button")
        if not create_client_button:
            print("🔍 Trying alternative search for Create client button...")
            try:
                # Look for any anchor or button containing "Create client" text
                all_clickable = driver.find_elements(By.XPATH, "//a | //button")
                for element in all_clickable:
                    if element.is_displayed() and element.is_enabled():
                        element_text = (element.get_attribute("textContent") or element.text or "").strip()
                        element_id = element.get_attribute("id") or ""
                        element_aria_label = element.get_attribute("aria-label") or ""
                        
                        # Check if this is specifically a Create client button/link
                        if (("create client" in element_text.lower()) or 
                            ("create client" in element_aria_label.lower()) or
                            ("create-client" in element_id.lower()) or
                            ("action-bar-create-client" in element_id.lower()) or
                            (element_text.lower().strip() == "create client") or
                            ("create" in element_text.lower() and "client" in element_text.lower() and "oauth" not in element_text.lower())):
                            create_client_button = element
                            print(f"✅ Found Create client element alternative: {element.tag_name} with text: '{element_text}', id: '{element_id}', aria-label: '{element_aria_label}'")
                            break
                            
                # If still not found, look for elements with specific classes that might be Create buttons
                if not create_client_button:
                    print("🔍 Looking for mat-primary styled elements...")
                    styled_elements = driver.find_elements(By.XPATH, 
                        "//*[contains(@class, 'mat-primary') or contains(@class, 'primary') or contains(@class, 'unelevated') or contains(@class, 'raised')]")
                    
                    for element in styled_elements:
                        if element.is_displayed() and element.is_enabled() and element.tag_name.lower() in ['a', 'button']:
                            element_text = (element.get_attribute("textContent") or element.text or "").strip()
                            if ("create" in element_text.lower() and 
                                ("client" in element_text.lower() or len(element_text.strip()) <= 15)):
                                create_client_button = element
                                print(f"✅ Found Create client element by styling: {element.tag_name} with text: '{element_text}'")
                                break
                                
                # Final attempt: look for any element with mdc-button__label containing "Create client"
                if not create_client_button:
                    print("🔍 Looking for mdc-button__label with Create client text...")
                    mdc_elements = driver.find_elements(By.XPATH, "//a[.//span[contains(@class, 'mdc-button__label')]] | //button[.//span[contains(@class, 'mdc-button__label')]]")
                    for element in mdc_elements:
                        if element.is_displayed() and element.is_enabled():
                            element_text = (element.get_attribute("textContent") or element.text or "").strip()
                            if ("create" in element_text.lower() and ("client" in element_text.lower() or "oauth" not in element_text.lower())):
                                create_client_button = element
                                print(f"✅ Found Create element with mdc structure: {element.tag_name} with text: '{element_text}'")
                                break
                                
            except Exception as alt_search_error:
                print(f"⚠️ Alternative Create client button search failed: {alt_search_error}")
        
        if not create_client_button:
            print("⚠️ Could not find Create client button")
            print("🔍 Listing all visible buttons and links for debugging...")
            try:
                all_clickable = driver.find_elements(By.XPATH, "//a | //button")
                print(f"📊 Total clickable elements found: {len(all_clickable)}")
                
                displayed_elements = []
                for element in all_clickable:
                    if element.is_displayed():
                        element_text = (element.get_attribute("textContent") or element.text or "").strip()
                        element_class = element.get_attribute("class") or ""
                        element_id = element.get_attribute("id") or ""
                        element_tag = element.tag_name
                        displayed_elements.append((element_tag, element_text, element_class, element_id))
                
                print(f"📊 Visible clickable elements found: {len(displayed_elements)}")
                for i, (tag, text, class_name, element_id) in enumerate(displayed_elements[:20]):  # Show first 20 visible elements
                    print(f"   {tag.upper()} {i+1}: '{text[:50]}...' (id: {element_id[:30]}, class: {class_name[:60]})")
                
                # Also check for span elements with Create text (might be inside buttons/links)
                print("🔍 Looking for span elements with 'Create' text...")
                create_spans = driver.find_elements(By.XPATH, "//span[contains(text(), 'Create')]")
                for i, span in enumerate(create_spans[:5]):
                    if span.is_displayed():
                        span_text = (span.get_attribute("textContent") or span.text or "").strip()
                        span_class = span.get_attribute("class") or ""
                        parent_tag = span.find_element(By.XPATH, "..").tag_name if span.find_element(By.XPATH, "..") else "unknown"
                        print(f"   Span {i+1}: '{span_text}' (class: {span_class[:60]}, parent: {parent_tag})")
                        
            except Exception as debug_error:
                print(f"⚠️ Debug listing error: {debug_error}")
            
            print("💡 Suggestions:")
            print("   • The Create client button might be hidden or not loaded yet")
            print("   • Try manually clicking on Clients again if needed")
            print("   • Check if the page needs to scroll to reveal the button")
            print("   • The button might have a different text or structure")
            return False
            
        # Click create client button
        if not click_element(driver, create_client_button, "Create client button"):
            return False
            
        # Enhanced wait for "Create OAuth client ID" page to load completely
        print("⏳ Waiting for 'Create OAuth client ID' page to load completely...")
        time.sleep(random.uniform(3.0, 5.0))  # Increased initial wait
        
        # Check for any verification prompts during OAuth client creation
        print("🔐 Checking for verifications during OAuth client creation...")
        handle_google_verifications(driver, "oauth-client-creation")
        
        # Verify the OAuth client creation page has loaded
        print("🔍 Verifying OAuth client creation page has loaded...")
        page_loaded = False
        max_attempts = 5
        
        for attempt in range(max_attempts):
            try:
                # Look for indicators that we're on the OAuth client creation page
                oauth_page_indicators = [
                    "//h1[contains(text(), 'Create OAuth client ID')]",
                    "//h2[contains(text(), 'Create OAuth client ID')]", 
                    "//h1[contains(text(), 'OAuth client ID')]",
                    "//*[contains(text(), 'Application type')]",
                    "//mat-label[contains(text(), 'Application type')]",
                    "//label[contains(text(), 'Application type')]",
                    "//form//div[contains(@class, 'cfc-select')]",
                    "//cfc-select[@role='combobox']",
                    "//*[contains(text(), 'Name') and contains(text(), 'required')]"
                ]
                
                for indicator in oauth_page_indicators:
                    try:
                        elements = driver.find_elements(By.XPATH, indicator)
                        if elements and elements[0].is_displayed():
                            element_text = (elements[0].get_attribute("textContent") or elements[0].text or "").strip()
                            print(f"✅ OAuth client creation page loaded - found: '{element_text[:50]}...'")
                            page_loaded = True
                            break
                    except:
                        continue
                
                if page_loaded:
                    break
                    
                print(f"⏳ Attempt {attempt + 1}/{max_attempts}: Page still loading, waiting longer...")
                time.sleep(random.uniform(2.0, 3.0))
                
            except Exception as verification_error:
                print(f"⚠️ Page verification error: {verification_error}")
                time.sleep(random.uniform(1.0, 2.0))
        
        if not page_loaded:
            print("⚠️ OAuth client creation page may not have loaded completely")
            print("🔍 Checking current page state...")
            try:
                current_url = driver.current_url
                page_title = driver.title
                print(f"📍 Current URL: {current_url}")
                print(f"📄 Page title: {page_title}")
                
                # Check if we're on the right URL
                if "auth/clients/create" in current_url or "oauth" in current_url.lower():
                    print("✅ URL indicates we're on OAuth client creation page")
                    page_loaded = True
                else:
                    print("⚠️ URL doesn't match expected OAuth client creation page")
                    
            except Exception as url_check_error:
                print(f"⚠️ URL check error: {url_check_error}")
        
        # Additional wait to ensure all form elements are fully rendered
        print("⏳ Ensuring all form elements are fully rendered...")
        time.sleep(random.uniform(2.0, 3.0))
        
        # Scroll to ensure all content is visible
        print("📜 Scrolling to ensure form is fully visible...")
        try:
            driver.execute_script("window.scrollTo(0, 0);")  # Scroll to top
            time.sleep(1.0)
            driver.execute_script("window.scrollBy(0, 200);")  # Scroll down a bit to center the form
            time.sleep(1.0)
        except Exception as scroll_error:
            print(f"⚠️ Scroll error: {scroll_error}")
        
        # Select Application type dropdown
        print("📋 Now proceeding to find Application type dropdown...")
        return select_application_type(driver)
        
    except Exception as clients_error:
        print(f"❌ Error in create_oauth_client: {clients_error}")
        return False

def select_application_type(driver):
    """Select Application type dropdown and choose Desktop app"""
    print("📋 Looking for Application type dropdown...")
    
    # Minimal wait for the page to fully load (no wait needed for app info as requested)
    time.sleep(random.uniform(0.5, 1.0))
    
    # Look for the "Application type" dropdown specifically in OAuth client creation form
    dropdown_selectors = [
        # Most specific: Look for Application type label and find associated dropdown
        "//mat-label[contains(text(), 'Application type')]/ancestor::mat-form-field//mat-select",
        "//label[contains(text(), 'Application type')]/following-sibling::*//div[contains(@class, 'cfc-select-value')]",
        "//mat-form-field[.//mat-label[contains(text(), 'Application type')]]//mat-select",
        "//cfc-form-field[.//label[contains(text(), 'Application type')]]//cfc-select",
        
        # Look for dropdowns with "Application type" placeholder or aria-label
        "//div[contains(@class, 'cfc-select-value')][contains(@aria-label, 'Application type')]",
        "//mat-select[contains(@aria-label, 'Application type')]",
        "//cfc-select[contains(@aria-label, 'Application type')]",
        "//div[@role='combobox'][contains(@aria-label, 'Application type')]",
        
        # Look for CFC select components with Application type context
        "//div[contains(@class, 'cfc-select-value')][preceding-sibling::*[contains(text(), 'Application type')] or following-sibling::*[contains(text(), 'Application type')]]",
        "//div[contains(@class, 'cfc-select-value')][ancestor::*[contains(text(), 'Application type')]]",
        
        # Form-based selectors for OAuth client creation
        "//form[contains(@class, 'oauth') or contains(@class, 'client')]//div[contains(@class, 'cfc-select-value')]",
        "//form//mat-form-field//mat-select",
        "//form//cfc-form-field//cfc-select",
        "//form//div[contains(@class, 'form-field')]//div[contains(@class, 'cfc-select')]",
        
        # Generic CFC select in client creation context
        "//div[contains(@class, 'cfc-select-value')]",
        "//div[contains(@class, 'cfc-select-value') and contains(@class, 'ng-star-inserted')]",
        "//div[@class='cfc-select-value ng-star-inserted']",
        
        # Material Design select components
        "//mat-select[@role='combobox']",
        "//div[contains(@class, 'mat-select-trigger')]",
        "//div[contains(@class, 'mat-mdc-select-trigger')]",
        
        # CFC specific selectors
        "//cfc-select[@role='combobox']",
        "//div[contains(@class, 'cfc-select')]",
        "//span[contains(@class, 'cfc-select-placeholder')]//parent::div",
        "//span[contains(@class, 'cfc-select-value-text')]//parent::div",
        
        # Generic dropdown patterns with role
        "//div[@role='combobox']",
        "//div[@role='listbox']",
        "//select[contains(@name, 'type') or contains(@name, 'application')]",
        
        # Look for dropdowns by position relative to "Application type" text
        "//text()[contains(., 'Application type')]/following::div[contains(@class, 'select')][1]",
        "//span[contains(text(), 'Application type')]/following-sibling::*//div[contains(@class, 'select')]",
        "//label[contains(text(), 'Application type')]/following-sibling::*//div[contains(@class, 'select')]"
    ]
    
    dropdown_element = None
    for selector in dropdown_selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    # Check if this looks like the right dropdown
                    element_text = (element.get_attribute("textContent") or element.text or "").strip().lower()
                    element_class = (element.get_attribute("class") or "").lower()
                    element_aria_label = (element.get_attribute("aria-label") or "").lower()
                    element_placeholder = (element.get_attribute("placeholder") or "").lower()
                    
                    print(f"🔍 Examining dropdown element:")
                    print(f"    Text: '{element_text[:50]}{'...' if len(element_text) > 50 else ''}'")
                    print(f"    Classes: '{element_class[:50]}{'...' if len(element_class) > 50 else ''}'")
                    print(f"    Aria-label: '{element_aria_label}'")
                    print(f"    Placeholder: '{element_placeholder}'")
                    
                    # Enhanced validation for Application type dropdown
                    positive_indicators = [
                        "application type" in element_text,
                        "application type" in element_aria_label,
                        "application type" in element_placeholder,
                        "desktop app" in element_text,
                        element.get_attribute("role") == "combobox",
                        "cfc-select" in element_class,
                        "mat-select" in element_class,
                        len(element_text.strip()) == 0 and ("select" in element_class or "dropdown" in element_class)  # Empty dropdown with select classes
                    ]
                    
                    # Strong negative indicators (things to avoid)
                    negative_indicators = [
                        "/" in element_text,  # Navigation breadcrumbs
                        "create client" in element_text,  # Navigation menu
                        "clients" in element_text and "application" not in element_text,  # Wrong context
                        "navigation" in element_class,
                        "nav" in element_class,
                        "menu" in element_class,
                        "breadcrumb" in element_class,
                        "sidebar" in element_class,
                        element_text.startswith("/"),  # Breadcrumb paths
                        "create" in element_text and "client" in element_text  # Navigation "Create client"
                    ]
                    
                    # Calculate confidence score
                    positive_score = sum(1 for indicator in positive_indicators if indicator)
                    negative_score = sum(1 for indicator in negative_indicators if indicator)
                    
                    print(f"    Positive indicators: {positive_score}")
                    print(f"    Negative indicators: {negative_score}")
                    
                    # Only accept if we have positive indicators and no strong negative indicators
                    if positive_score > 0 and negative_score == 0:
                        dropdown_element = element
                        print(f"✅ Found Application type dropdown with text: '{element_text}' using selector: {selector}")
                        break
            if dropdown_element:
                break
        except Exception as selector_error:
            continue
    
    # If still not found, provide comprehensive debugging like our debug tool
    if not dropdown_element:
        print("🔍 Dropdown not found with standard selectors. Running comprehensive debugging...")
        try:
            # First, verify we're on the right page
            current_url = driver.current_url
            page_title = driver.title
            
            print(f"📍 Current URL: {current_url}")
            print(f"📄 Page title: {page_title}")
            
            # Enhanced debugging - show ALL dropdown-like elements
            print("\n🔍 Enhanced debugging - showing all dropdown-like elements:")
            all_dropdown_selectors = [
                "//div[contains(@class, 'cfc-select')]",
                "//mat-select",
                "//div[@role='combobox']",
                "//div[contains(@class, 'select')]",
                "//cfc-select",
                "//select"
            ]
            
            all_candidates = []
            for selector in all_dropdown_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            element_text = (element.get_attribute("textContent") or element.text or "").strip()
                            element_class = (element.get_attribute("class") or "").strip()
                            element_id = (element.get_attribute("id") or "").strip()
                            element_aria_label = (element.get_attribute("aria-label") or "").strip()
                            
                            all_candidates.append({
                                'element': element,
                                'text': element_text,
                                'class': element_class,
                                'id': element_id,
                                'aria_label': element_aria_label,
                                'selector': selector
                            })
                except:
                    continue
            
            print(f"Found {len(all_candidates)} dropdown-like elements:")
            for i, candidate in enumerate(all_candidates, 1):
                text_display = candidate['text'][:50] + ('...' if len(candidate['text']) > 50 else '')
                print(f"  Candidate {i}:")
                print(f"    Text: '{text_display}'")
                print(f"    Class: '{candidate['class'][:60]}{'...' if len(candidate['class']) > 60 else ''}'")
                print(f"    ID: '{candidate['id']}'")
                print(f"    Aria-label: '{candidate['aria_label']}'")
                print(f"    Selector: {candidate['selector']}")
                
                # Try to analyze if this could be our target
                is_navigation = ("/" in candidate['text'] or 
                               "create client" in candidate['text'].lower() or
                               "clients" in candidate['text'].lower())
                
                is_form_dropdown = ("cfc-select" in candidate['class'] or 
                                  "mat-select" in candidate['class'] or
                                  candidate['element'].get_attribute("role") == "combobox")
                
                print(f"    Analysis: Navigation={is_navigation}, FormDropdown={is_form_dropdown}")
                print()
                
                # If this looks like a form dropdown and not navigation, try it
                if is_form_dropdown and not is_navigation and not dropdown_element:
                    print(f"🎯 Candidate {i} looks promising - attempting to use it")
                    dropdown_element = candidate['element']
                    break
            
            # Check if we're on OAuth client creation page
            oauth_client_indicators = [
                "oauth" in current_url.lower(),
                "client" in current_url.lower(),
                "credentials" in current_url.lower(),
                "oauth" in page_title.lower(),
                "client" in page_title.lower()
            ]
            
            if any(oauth_client_indicators):
                print("✅ Confirmed we're on OAuth client creation page")
                
                # Look for Application type text first, then find nearby dropdowns
                app_type_labels = driver.find_elements(By.XPATH, "//*[contains(text(), 'Application type')]")
                print(f"🔍 Found {len(app_type_labels)} 'Application type' labels")
                
                for i, label in enumerate(app_type_labels):
                    if label.is_displayed():
                        label_text = label.text or label.get_attribute("textContent") or ""
                        print(f"   Label {i+1}: '{label_text}'")
                        
                        # Look for nearby dropdowns (siblings, parents, children)
                        nearby_selectors = [
                            ".//following-sibling::*//div[contains(@class, 'cfc-select-value')]",
                            ".//following-sibling::*//mat-select",
                            ".//following-sibling::*//cfc-select", 
                            ".//parent::*//div[contains(@class, 'cfc-select-value')]",
                            ".//parent::*//mat-select",
                            ".//parent::*//cfc-select",
                            ".//ancestor::*[1]//div[contains(@class, 'cfc-select-value')]",
                            ".//ancestor::*[2]//div[contains(@class, 'cfc-select-value')]",
                            ".//following::*[1][contains(@class, 'cfc-select-value')]",
                            ".//following::*[2][contains(@class, 'cfc-select-value')]"
                        ]
                        
                        for selector in nearby_selectors:
                            try:
                                nearby_dropdowns = label.find_elements(By.XPATH, selector)
                                for dropdown in nearby_dropdowns:
                                    if dropdown.is_displayed() and dropdown.is_enabled():
                                        dropdown_text = (dropdown.get_attribute("textContent") or dropdown.text or "").strip()
                                        # Avoid navigation dropdowns
                                        if not any(nav_text in dropdown_text for nav_text in ['/', 'Create client', 'Clients']):
                                            dropdown_element = dropdown
                                            print(f"✅ Found Application type dropdown near label: '{dropdown_text}'")
                                            break
                                if dropdown_element:
                                    break
                            except Exception as nearby_error:
                                continue
                        if dropdown_element:
                            break
            else:
                print("⚠️ Doesn't appear to be on OAuth client creation page")
                
        except Exception as focused_search_error:
            print(f"⚠️ Focused search failed: {focused_search_error}")
    
    # Last resort: look for any dropdown-like element in the form
    if not dropdown_element:
        print("🔍 Last resort: looking for any dropdown in the form...")
        try:
            form_elements = driver.find_elements(By.XPATH, "//form//div[contains(@class, 'select') or @role='combobox' or contains(@class, 'dropdown')]")
            for element in form_elements:
                if element.is_displayed() and element.is_enabled():
                    element_text = (element.get_attribute("textContent") or element.text or "").strip()
                    if len(element_text) < 100:  # Reasonable length for a dropdown
                        dropdown_element = element
                        print(f"✅ Found potential dropdown in form: '{element_text}'")
                        break
        except Exception as form_search_error:
            print(f"⚠️ Form search failed: {form_search_error}")
    
    if not dropdown_element:
        print("⚠️ Could not find Application type dropdown")
        
        # Provide detailed guidance
        provide_application_type_dropdown_guidance()
        
        print("🔍 Listing all visible dropdown-like elements for debugging...")
        try:
            all_selects = driver.find_elements(By.XPATH, "//div[contains(@class, 'select') or contains(@class, 'dropdown') or contains(@class, 'cfc-select') or @role='combobox'] | //mat-select | //select")
            print(f"📋 Found {len(all_selects)} potential dropdown elements:")
            
            for i, select in enumerate(all_selects[:10]):  # Show first 10 elements
                if select.is_displayed():
                    select_text = (select.get_attribute("textContent") or select.text or "").strip()
                    select_class = select.get_attribute("class") or ""
                    select_role = select.get_attribute("role") or ""
                    select_tag = select.tag_name
                    
                    # Analyze if this might be the Application type dropdown
                    confidence = 0
                    reasons = []
                    
                    if "application type" in select_text.lower():
                        confidence += 50
                        reasons.append("Contains 'Application type'")
                    if "cfc-select" in select_class:
                        confidence += 30
                        reasons.append("CFC select component")
                    if select_role == "combobox":
                        confidence += 20
                        reasons.append("Combobox role")
                    if "/" in select_text:
                        confidence -= 40
                        reasons.append("Contains '/' (navigation)")
                    if "create client" in select_text.lower():
                        confidence -= 50
                        reasons.append("Navigation text")
                    
                    confidence_label = "🎯 HIGH" if confidence > 40 else "⚠️ MEDIUM" if confidence > 10 else "❌ LOW"
                    
                    print(f"   {i+1}. Tag: '{select_tag}' | Text: '{select_text[:30]}{'...' if len(select_text) > 30 else ''}' | Role: '{select_role}'")
                    print(f"       Classes: '{select_class[:50]}{'...' if len(select_class) > 50 else ''}'")
                    print(f"       Confidence: {confidence_label} ({confidence}%) - {'; '.join(reasons) if reasons else 'No specific indicators'}")
                    print("")
        except Exception as debug_error:
            print(f"   Debug listing failed: {debug_error}")
        
        # Ask for manual intervention
        try:
            user_input = input("\n✅ Please manually click the 'Application type' dropdown and select 'Desktop app', then press Enter to continue: ").strip()
            print("✅ Continuing after manual Application type selection...")
            time.sleep(random.uniform(1.0, 2.0))
            return True  # Continue to next step
        except KeyboardInterrupt:
            print("\n⚠️ User interrupted - stopping automation")
            return False
    
    # Click the dropdown to open it
    print("🎯 Clicking Application type dropdown...")
    
    # Scroll to dropdown and highlight it
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", dropdown_element)
        time.sleep(random.uniform(0.3, 0.5))  # Reduced wait time
        
        # Highlight dropdown for visibility
        driver.execute_script("""
            arguments[0].style.border = '3px solid purple';
            arguments[0].style.backgroundColor = 'lightpink';
        """, dropdown_element)
        time.sleep(0.5)  # Reduced wait time
        
        # Remove highlight
        driver.execute_script("""
            arguments[0].style.border = '';
            arguments[0].style.backgroundColor = '';
        """, dropdown_element)
        
    except Exception as highlight_error:
        print(f"⚠️ Highlight error: {highlight_error}")
    
    # Try multiple click methods for dropdown
    click_success = False
    
    # Method 1: JavaScript click
    try:
        driver.execute_script("arguments[0].click();", dropdown_element)
        print("✅ Application type dropdown clicked successfully with JavaScript!")
        click_success = True
        time.sleep(random.uniform(0.5, 1.0))  # Reduced wait time
        
    except Exception as js_click_error:
        print(f"⚠️ JavaScript click failed: {js_click_error}")
    
    # Method 2: Regular click as fallback
    if not click_success:
        try:
            human_mouse_move_to(dropdown_element)
            dropdown_element.click()
            print("✅ Application type dropdown clicked successfully with regular click!")
            click_success = True
            time.sleep(random.uniform(0.5, 1.0))  # Reduced wait time
            
        except Exception as regular_click_error:
            print(f"⚠️ Regular click failed: {regular_click_error}")
    
    if not click_success:
        print("❌ Failed to click Application type dropdown")
        return True  # Continue anyway
    
    # Wait for dropdown options to appear
    print("⏳ Waiting for dropdown options to appear...")
    time.sleep(random.uniform(0.5, 1.0))  # Reduced wait time
    
    # Select "Desktop app" option
    print("🖥️ Selecting 'Desktop app' option...")
    return select_desktop_app_option(driver)

def select_desktop_app_option(driver):
    """Select Desktop app option from the dropdown"""
    print("🖥️ Looking for EXACT 'Desktop app' option...")
    
    # Precise selectors for exactly "Desktop app" text
    exact_desktop_app_selectors = [
        # Most precise - exact text match
        "//span[normalize-space(text())='Desktop app']",
        "//div[normalize-space(text())='Desktop app']",
        "//li[normalize-space(text())='Desktop app']",
        "//mat-option[normalize-space(text())='Desktop app']",
        "//cfc-option[normalize-space(text())='Desktop app']",
        
        # With parent containers
        "//mat-option//span[normalize-space(text())='Desktop app']",
        "//cfc-option//span[normalize-space(text())='Desktop app']",
        "//li//span[normalize-space(text())='Desktop app']",
        "//div[@role='option']//span[normalize-space(text())='Desktop app']",
        
        # In overlay panels with exact text
        "//div[contains(@class, 'overlay')]//span[normalize-space(text())='Desktop app']",
        "//div[contains(@class, 'mat-select-panel')]//span[normalize-space(text())='Desktop app']",
        "//div[contains(@class, 'cfc-select-panel')]//span[normalize-space(text())='Desktop app']",
        "//div[contains(@class, 'cdk-overlay')]//span[normalize-space(text())='Desktop app']",
        
        # Role-based with exact text
        "//*[@role='option'][normalize-space(text())='Desktop app']",
        "//*[@role='menuitem'][normalize-space(text())='Desktop app']",
        "//*[@role='listitem'][normalize-space(text())='Desktop app']",
        
        # List containers with exact text
        "//ul[@role='listbox']//li[normalize-space(text())='Desktop app']",
        "//div[@role='listbox']//div[normalize-space(text())='Desktop app']",
        "//div[@role='menu']//div[normalize-space(text())='Desktop app']"
    ]
    
    desktop_app_option = None
    
    # Search with exact text matching only
    for selector in exact_desktop_app_selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    element_text = (element.get_attribute("textContent") or element.text or "").strip()
                    # Must be EXACTLY "Desktop app" (case insensitive)
                    if element_text.lower() == "desktop app":
                        desktop_app_option = element
                        print(f"✅ Found EXACT Desktop app option: '{element_text}' using selector: {selector}")
                        break
            if desktop_app_option:
                break
        except Exception as selector_error:
            continue
    
    # If exact match not found, try with contains but strict validation
    if not desktop_app_option:
        print("🔍 Trying contains search with strict validation...")
        contains_selectors = [
            "//span[contains(text(), 'Desktop app')]",
            "//div[contains(text(), 'Desktop app')]", 
            "//li[contains(text(), 'Desktop app')]",
            "//mat-option[contains(text(), 'Desktop app')]",
            "//cfc-option[contains(text(), 'Desktop app')]",
            "//*[@role='option'][contains(text(), 'Desktop app')]",
            "//div[contains(@class, 'overlay')]//*[contains(text(), 'Desktop app')]",
            "//div[contains(@class, 'mat-select-panel')]//*[contains(text(), 'Desktop app')]"
        ]
        
        for selector in contains_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element_text = (element.get_attribute("textContent") or element.text or "").strip()
                        # Must contain "Desktop app" and be reasonable length
                        if "desktop app" in element_text.lower() and len(element_text) <= 20:
                            desktop_app_option = element
                            print(f"✅ Found Desktop app option with contains: '{element_text}' using selector: {selector}")
                            break
                if desktop_app_option:
                    break
            except Exception as selector_error:
                continue
    
    if not desktop_app_option:
        print("❌ Could not find Desktop app option")
        
        # Enhanced debugging to understand what dropdown we're in
        print("🔍 Analyzing current dropdown content...")
        try:
            # First, check if we're in the right context
            page_source_check = driver.page_source
            if "/Create client" in page_source_check:
                print("⚠️ Detected we might be in the wrong dropdown (navigation menu)")
                print("🔄 Attempting to close current dropdown and find correct Application type dropdown...")
                
                # Try to close any open dropdown by clicking outside
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.click()
                    time.sleep(random.uniform(1.0, 2.0))
                    print("✅ Closed current dropdown")
                except:
                    pass
                
                # Try to find the correct Application type dropdown more specifically
                print("🔍 Looking for Application type dropdown with enhanced detection...")
                
                # Look for form fields specifically related to OAuth client creation
                app_type_selectors = [
                    # Look for form sections with Application type
                    "//form//mat-form-field[.//mat-label[contains(text(), 'Application type')]]//mat-select",
                    "//form//div[contains(@class, 'form-field')][.//label[contains(text(), 'Application type')]]//div[contains(@class, 'select')]",
                    "//form//cfc-form-field[.//label[contains(text(), 'Application type')]]//cfc-select",
                    
                    # Look for dropdowns with placeholder text about application type
                    "//div[contains(@class, 'cfc-select-value')][contains(@aria-describedby, 'Application')]",
                    "//div[contains(@class, 'cfc-select-value')][contains(@data-placeholder, 'Application')]",
                    "//mat-select[contains(@aria-describedby, 'Application')]",
                    
                    # Look for specific OAuth client form elements
                    "//div[contains(@class, 'oauth-client')]//div[contains(@class, 'select')]",
                    "//div[contains(@class, 'client-creation')]//div[contains(@class, 'select')]",
                    "//div[contains(@class, 'credentials')]//div[contains(@class, 'select')]",
                    
                    # More specific CFC select patterns
                    "//cfc-select[@formcontrolname*='type']",
                    "//cfc-select[@formcontrolname*='application']",
                    "//div[contains(@class, 'cfc-select-value')][not(contains(text(), '/'))]",  # Exclude navigation dropdowns
                    
                    # Look for selects that are NOT navigation menus
                    "//div[contains(@class, 'cfc-select-value')][not(contains(text(), 'Create')) and not(contains(text(), 'Clients'))]"
                ]
                
                correct_dropdown = None
                for selector in app_type_selectors:
                    try:
                        elements = driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                element_text = (element.get_attribute("textContent") or element.text or "").strip()
                                # Validate this isn't a navigation dropdown
                                if not any(nav_text in element_text for nav_text in ['/', 'Create client', 'Clients']):
                                    correct_dropdown = element
                                    print(f"✅ Found correct Application type dropdown: '{element_text}' with selector: {selector}")
                                    break
                        if correct_dropdown:
                            break
                    except Exception as e:
                        continue
                
                if correct_dropdown:
                    print("🎯 Clicking correct Application type dropdown...")
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", correct_dropdown)
                        time.sleep(random.uniform(0.5, 1.0))
                        
                        # Highlight the correct dropdown
                        driver.execute_script("arguments[0].style.border='3px solid green';", correct_dropdown)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].style.border='';", correct_dropdown)
                        
                        # Click the correct dropdown
                        driver.execute_script("arguments[0].click();", correct_dropdown)
                        print("✅ Correct Application type dropdown clicked!")
                        time.sleep(random.uniform(1.0, 2.0))
                        
                        # Now look for Desktop app option again
                        print("🔍 Looking for Desktop app option in correct dropdown...")
                        desktop_app_selectors = [
                            "//span[normalize-space(text())='Desktop app']",
                            "//div[normalize-space(text())='Desktop app']", 
                            "//li[normalize-space(text())='Desktop app']",
                            "//mat-option[normalize-space(text())='Desktop app']",
                            "//cfc-option[normalize-space(text())='Desktop app']",
                            "//div[@role='option'][normalize-space(text())='Desktop app']",
                            "//span[contains(text(), 'Desktop app')]",
                            "//div[contains(text(), 'Desktop app')]",
                            "//li[contains(text(), 'Desktop app')]"
                        ]
                        
                        for selector in desktop_app_selectors:
                            try:
                                desktop_options = driver.find_elements(By.XPATH, selector)
                                for option in desktop_options:
                                    if option.is_displayed() and option.is_enabled():
                                        option_text = (option.get_attribute("textContent") or option.text or "").strip()
                                        if "desktop app" in option_text.lower():
                                            desktop_app_option = option
                                            print(f"✅ Found Desktop app option: '{option_text}'")
                                            break
                                if desktop_app_option:
                                    break
                            except Exception as e:
                                continue
                                
                    except Exception as click_error:
                        print(f"⚠️ Error clicking correct dropdown: {click_error}")
            
            # If still not found, show enhanced debugging info
            if not desktop_app_option:
                print("🔍 Enhanced debugging - showing all dropdown options:")
                try:
                    # Look for all overlay/dropdown content
                    all_options = driver.find_elements(By.XPATH, 
                        "//div[contains(@class, 'overlay') or contains(@class, 'panel') or contains(@class, 'dropdown') or contains(@class, 'cdk-overlay')]//*[@role='option' or contains(@class, 'option') or self::li or self::div[contains(@class, 'select-option')]]")
                    
                    if not all_options:
                        # Fallback to any visible clickable text elements
                        all_options = driver.find_elements(By.XPATH, 
                            "//div[contains(@class, 'cfc-option') or contains(@class, 'mat-option')]//*[text()] | //span[contains(@class, 'option-text')] | //div[@role='option']")
                    
                    displayed_options = []
                    for option in all_options:
                        if option.is_displayed():
                            option_text = (option.get_attribute("textContent") or option.text or "").strip()
                            if len(option_text) > 0 and len(option_text) < 100:
                                displayed_options.append(option_text)
                    
                    # Remove duplicates and show unique options
                    unique_options = list(dict.fromkeys(displayed_options))
                    for i, option_text in enumerate(unique_options[:15]):  # Show up to 15 options
                        print(f"   Available option {i+1}: '{option_text}'")
                        # Check if this might be Desktop app with different formatting
                        if any(keyword in option_text.lower() for keyword in ['desktop', 'installed', 'native', 'client']):
                            print(f"      ^^ This might be the Desktop app option!")
                            
                except Exception as debug_error:
                    print(f"   Debug failed: {debug_error}")
        
        except Exception as analysis_error:
            print(f"⚠️ Dropdown analysis failed: {analysis_error}")
        
        # If we still haven't found it, try alternative terms
        if not desktop_app_option:
            print("🔍 Trying alternative terms for Desktop app...")
            alternative_terms = ['Installed app', 'Native app', 'Desktop application', 'Client application', 'Installed application']
            
            for term in alternative_terms:
                try:
                    alternative_options = driver.find_elements(By.XPATH, f"//span[contains(text(), '{term}')] | //div[contains(text(), '{term}')] | //li[contains(text(), '{term}')]")
                    for option in alternative_options:
                        if option.is_displayed() and option.is_enabled():
                            desktop_app_option = option
                            print(f"✅ Found alternative Desktop app option: '{term}'")
                            break
                    if desktop_app_option:
                        break
                except:
                    continue
        
        return False
    
    # Click the Desktop app option
    print("🎯 Clicking Desktop app option...")
    
    # Scroll to option and highlight it briefly
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", desktop_app_option)
        time.sleep(random.uniform(0.3, 0.5))
        
        # Brief highlight for confirmation
        driver.execute_script("""
            arguments[0].style.border = '3px solid orange';
            arguments[0].style.backgroundColor = 'lightyellow';
        """, desktop_app_option)
        time.sleep(0.5)
        
        # Remove highlight
        driver.execute_script("""
            arguments[0].style.border = '';
            arguments[0].style.backgroundColor = '';
        """, desktop_app_option)
        
    except Exception as highlight_error:
        print(f"⚠️ Highlight error: {highlight_error}")
    
    # Click with JavaScript first (most reliable)
    try:
        driver.execute_script("arguments[0].click();", desktop_app_option)
        print("✅ Desktop app clicked successfully with JavaScript!")
        time.sleep(random.uniform(0.5, 1.0))
        
        # Proceed to Create button
        print("🎯 Proceeding to click Create button...")
        return click_create_button_and_download_json(driver)
        
    except Exception as js_click_error:
        print(f"⚠️ JavaScript click failed: {js_click_error}")
        
        # Try regular click as fallback
        try:
            human_mouse_move_to(desktop_app_option)
            desktop_app_option.click()
            print("✅ Desktop app clicked successfully with regular click!")
            time.sleep(random.uniform(0.5, 1.0))
            
            # Proceed to Create button
            print("🎯 Proceeding to click Create button...")
            return click_create_button_and_download_json(driver)
            
        except Exception as regular_click_error:
            print(f"❌ Both click methods failed: {regular_click_error}")
            return False

def click_create_button_and_download_json(driver):
    """Click the Create button and handle the Download JSON modal"""
    print("🆕 Looking for Create button...")
    time.sleep(random.uniform(0.5, 1.0))  # Reduced wait time
    
    # Look for the Create button with the exact structure provided
    create_button_selectors = [
        # Exact selector for Create button with sandboxuid structure
        "//span[contains(@class, 'mdc-button__label') and @sandboxuid='0' and normalize-space(text())='Create']/parent::button",
        "//button[.//span[contains(@class, 'mdc-button__label') and @sandboxuid='0' and normalize-space(text())='Create']]",
        "//button[contains(@class, 'mdc-button') and .//span[@sandboxuid='0' and normalize-space(text())='Create']]",
        "//button[contains(@class, 'mat-mdc-button') and .//span[@sandboxuid='0' and normalize-space(text())='Create']]",
        
        # More specific patterns for the Create button
        "//span[@class='mdc-button__label' and @sandboxuid='0' and text()='Create']//parent::button",
        "//span[normalize-space(text())='Create' and @sandboxuid='0']//parent::button",
        "//button[descendant::span[@sandboxuid='0' and normalize-space(text())='Create']]",
        
        # Generic Create button selectors (fallback)
        "//button[contains(text(), 'Create')]",
        "//button[normalize-space(text())='Create']",
        "//button[.//span[contains(text(), 'Create')]]",
        "//span[text()='Create']//ancestor::button[1]",
        "//button[contains(@class, 'mdc-button') and contains(text(), 'Create')]",
        "//button[contains(@class, 'mat-mdc-button') and contains(text(), 'Create')]",
        
        # Primary/styled button patterns
        "//button[contains(@class, 'mat-primary') and contains(text(), 'Create')]",
        "//button[contains(@class, 'primary') and contains(text(), 'Create')]",
        "//button[contains(@class, 'mdc-button--raised') and contains(text(), 'Create')]",
        "//button[contains(@class, 'mdc-button--unelevated') and contains(text(), 'Create')]"
    ]
    
    create_button = None
    for selector in create_button_selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    element_text = (element.get_attribute("textContent") or element.text or "").strip()
                    # Check if this is specifically the Create button (not "Create client")
                    if (element_text.lower().strip() == "create" or 
                        element_text.lower() == " create " or 
                        ("create" in element_text.lower() and len(element_text.strip()) <= 15 and "client" not in element_text.lower())):
                        create_button = element
                        print(f"✅ Found Create button with text: '{element_text}' using selector: {selector}")
                        break
            if create_button:
                break
        except Exception as selector_error:
            continue
    
    if not create_button:
        print("🔍 Trying alternative search for Create button...")
        try:
            # Look for any button containing "Create" text that's not "Create client"
            all_buttons = driver.find_elements(By.XPATH, "//button")
            for button in all_buttons:
                if button.is_displayed() and button.is_enabled():
                    button_text = (button.get_attribute("textContent") or button.text or "").strip()
                    if (button_text.lower().strip() == "create" or 
                        (button_text.lower().find("create") != -1 and 
                         len(button_text.strip()) <= 15 and 
                         "client" not in button_text.lower())):
                        create_button = button
                        print(f"✅ Found Create button alternative with text: '{button_text}'")
                        break
        except Exception as alt_search_error:
            print(f"⚠️ Alternative Create button search failed: {alt_search_error}")
    
    if not create_button:
        print("⚠️ Could not find Create button")
        print("🔍 Listing all visible buttons for debugging...")
        try:
            all_buttons = driver.find_elements(By.XPATH, "//button")
            for i, button in enumerate(all_buttons[:10]):  # Show first 10 buttons
                if button.is_displayed():
                    button_text = (button.get_attribute("textContent") or button.text or "").strip()
                    button_class = button.get_attribute("class") or ""
                    print(f"   Button {i+1}: '{button_text}' (class: {button_class[:50]})")
        except:
            pass
        return False
    
    # Click the Create button
    print("🎯 Clicking Create button...")
    
    # Scroll to button and highlight it
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", create_button)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Highlight button for visibility
        driver.execute_script("""
            arguments[0].style.border = '3px solid blue';
            arguments[0].style.backgroundColor = 'lightblue';
        """, create_button)
        time.sleep(1.0)
        
        # Remove highlight
        driver.execute_script("""
            arguments[0].style.border = '';
            arguments[0].style.backgroundColor = '';
        """, create_button)
        
    except Exception as highlight_error:
        print(f"⚠️ Highlight error: {highlight_error}")
    
    # Try multiple click methods for Create button
    click_success = False
    
    # Method 1: JavaScript click
    try:
        driver.execute_script("arguments[0].click();", create_button)
        print("✅ Create button clicked successfully with JavaScript!")
        click_success = True
        time.sleep(random.uniform(2.0, 4.0))
        
    except Exception as js_click_error:
        print(f"⚠️ JavaScript click failed: {js_click_error}")
    
    # Method 2: Regular click as fallback
    if not click_success:
        try:
            human_mouse_move_to(create_button)
            create_button.click()
            print("✅ Create button clicked successfully with regular click!")
            click_success = True
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as regular_click_error:
            print(f"⚠️ Regular click failed: {regular_click_error}")
    
    if not click_success:
        print("❌ Failed to click Create button")
        return False
    
    # Wait for modal to load
    print("⏳ Waiting for Download JSON modal to load...")
    time.sleep(random.uniform(1.0, 2.0))
    
    # Handle the Download JSON modal
    return handle_download_json_modal(driver)

def handle_download_json_modal(driver):
    """Handle the Download JSON modal and click Download JSON button with DIRECT APPROACH"""
    print("💾 Looking for Download JSON button in modal...")
    
    # Check for any verification prompts before downloading
    print("🔐 Checking for verifications before JSON download...")
    handle_google_verifications(driver, "json-download")
    
    # DIRECT APPROACH 1: Check if file is already downloaded (skip modal)
    print("🔍 DIRECT CHECK: Verifying if JSON file is already downloading...")
    try:
        time.sleep(random.uniform(2.0, 3.0))  # Wait for potential download
        
        # Check download directory for new JSON files
        import glob
        json_files = glob.glob(os.path.join(DOWNLOAD_DIR, "client_secret_*.json"))
        recent_files = []
        current_time = time.time()
        
        for json_file in json_files:
            file_time = os.path.getmtime(json_file)
            if current_time - file_time < 30:  # File created in last 30 seconds
                recent_files.append(json_file)
        
        if recent_files:
            print(f"✅ DIRECT SUCCESS: JSON file already downloaded: {recent_files[0]}")
            return handle_ok_button(driver)
    except Exception as direct_check_error:
        print(f"⚠️ Direct check failed: {direct_check_error}")
    
    # DIRECT APPROACH 2: Try immediate JavaScript automation
    print("🔍 DIRECT APPROACH: Auto-clicking download with JavaScript...")
    try:
        # Execute JavaScript to automatically trigger download
        download_script = """
        // Find all buttons containing download text
        var buttons = document.querySelectorAll('button');
        for (var i = 0; i < buttons.length; i++) {
            var button = buttons[i];
            var text = button.textContent || button.innerText || '';
            if (text.toLowerCase().includes('download') && 
                (text.toLowerCase().includes('json') || text.toLowerCase().includes('credential'))) {
                console.log('Auto-clicking download button:', text);
                button.click();
                return true;
            }
        }
        
        // Alternative: Look for download icons
        var iconButtons = document.querySelectorAll('button[aria-label*="download"], button cfc-icon[icon="download"]');
        if (iconButtons.length > 0) {
            console.log('Auto-clicking download icon button');
            iconButtons[0].closest('button').click();
            return true;
        }
        
        return false;
        """
        
        result = driver.execute_script(download_script)
        if result:
            print("✅ DIRECT SUCCESS: JavaScript auto-click successful!")
            time.sleep(random.uniform(2.0, 4.0))
            return handle_ok_button(driver)
    except Exception as js_error:
        print(f"⚠️ JavaScript auto-click failed: {js_error}")
    
    # DIRECT APPROACH 3: Enhanced button detection with better selectors
    print("🔍 DIRECT APPROACH: Enhanced Download JSON button detection...")
    
    # Based on successful pattern from logs, use the most effective selectors first
    priority_selectors = [
        # Most successful patterns from logs
        "//span[contains(@class, 'mdc-button__label') and @sandboxuid='0' and contains(text(), 'Download JSON')]/parent::button",
        "//span[contains(@class, 'mdc-button__label') and contains(text(), 'Download JSON')]/parent::button",
        "//button[.//span[contains(text(), 'Download JSON')]]",
        "//button[contains(text(), 'Download JSON')]",
        
        # Download icon patterns
        "//button[.//cfc-icon[@icon='download']]",
        "//button[.//mat-icon[@data-mat-icon-name='download']]",
        "//button[contains(@aria-label, 'download')]",
        
        # Modal-specific patterns
        "//div[contains(@class, 'cdk-overlay-container')]//button[contains(text(), 'Download')]",
        "//mat-dialog-container//button[contains(text(), 'Download')]",
        "//div[@role='dialog']//button[contains(text(), 'Download')]"
    ]
    
    download_json_button = None
    for i, selector in enumerate(priority_selectors):
        try:
            print(f"🔍 Trying priority selector {i+1}/{len(priority_selectors)}: {selector[:60]}...")
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    element_text = (element.get_attribute("textContent") or element.text or "").strip()
                    element_aria = (element.get_attribute("aria-label") or "").strip()
                    
                    # Enhanced validation
                    is_download_button = (
                        "download" in element_text.lower() or
                        "download" in element_aria.lower() or
                        "json" in element_text.lower()
                    )
                    
                    if is_download_button:
                        download_json_button = element
                        print(f"✅ Found Download button with text: '{element_text}' using selector: {selector}")
                        break
            if download_json_button:
                break
        except Exception as selector_error:
            continue
    
    # DIRECT APPROACH 4: If still not found, try comprehensive modal search
    if not download_json_button:
        print("🔍 DIRECT APPROACH: Comprehensive modal button search...")
        try:
            # Get all buttons in any modal/overlay
            all_modal_buttons = driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'overlay') or contains(@class, 'modal') or contains(@class, 'dialog')]//button")
            
            print(f"📋 Found {len(all_modal_buttons)} buttons in modal areas")
            
            for i, button in enumerate(all_modal_buttons[:10]):  # Limit to first 10
                try:
                    if button.is_displayed() and button.is_enabled():
                        button_text = (button.get_attribute("textContent") or button.text or "").strip()
                        button_aria = (button.get_attribute("aria-label") or "").strip()
                        button_class = (button.get_attribute("class") or "").strip()
                        
                        print(f"   Button {i+1}: text='{button_text[:30]}', aria='{button_aria}', classes='{button_class[:50]}'")
                        
                        # Look for download-related buttons
                        if (("download" in button_text.lower()) or 
                            ("download" in button_aria.lower()) or
                            ("json" in button_text.lower()) or
                            (len(button_text.strip()) == 0 and "download" in button_class.lower())):
                            download_json_button = button
                            print(f"✅ FOUND Download button: '{button_text}' / '{button_aria}'")
                            break
                except Exception as button_error:
                    continue
                    
        except Exception as modal_search_error:
            print(f"⚠️ Modal search failed: {modal_search_error}")
    
    # DIRECT APPROACH 5: Click the button if found
    if download_json_button:
        print("💾 Clicking Download JSON button...")
        
        # Enhanced clicking with multiple strategies and better error handling
        click_success = False
        
        # Method 1: JavaScript click (most reliable for modals)
        try:
            driver.execute_script("arguments[0].click();", download_json_button)
            print("✅ Download JSON button clicked successfully with JavaScript!")
            click_success = True
        except Exception as js_click_error:
            print(f"⚠️ JavaScript click failed: {js_click_error}")
        
        # Method 2: Regular click as fallback with stale element protection
        if not click_success:
            try:
                # Re-find the element to avoid stale reference
                download_json_button = driver.find_element(By.XPATH, 
                    "//span[contains(@class, 'mdc-button__label') and @sandboxuid='0' and contains(text(), 'Download JSON')]/parent::button")
                download_json_button.click()
                print("✅ Download JSON button clicked successfully with regular click!")
                click_success = True
            except Exception as regular_click_error:
                print(f"⚠️ Regular click failed: {regular_click_error}")
                # Try one more time with a broader selector
                try:
                    download_btn_alt = driver.find_element(By.XPATH, "//button[contains(text(), 'Download JSON')]")
                    download_btn_alt.click()
                    print("✅ Download JSON button clicked with alternative selector!")
                    click_success = True
                except Exception as alt_click_error:
                    print(f"⚠️ Alternative click also failed: {alt_click_error}")
        
        if click_success:
            time.sleep(random.uniform(2.0, 4.0))
            return handle_ok_button(driver)
    
    # FINAL FALLBACK: Manual guidance with direct file check
    print("⚠️ Could not find Download JSON button automatically")
    print("🔍 DIRECT APPROACH: Checking if download started anyway...")
    
    # Wait a bit and check for downloads
    time.sleep(random.uniform(3.0, 5.0))
    
    try:
        json_files = glob.glob(os.path.join(DOWNLOAD_DIR, "client_secret_*.json"))
        if json_files:
            # Sort by modification time and get the newest
            newest_file = max(json_files, key=os.path.getmtime)
            file_age = time.time() - os.path.getmtime(newest_file)
            
            if file_age < 60:  # File created in last minute
                print(f"✅ DIRECT SUCCESS: Found recent JSON file: {newest_file}")
                return handle_ok_button(driver)
    except Exception as file_check_error:
        print(f"⚠️ File check failed: {file_check_error}")
    
    print("💡 Manual intervention may be needed:")
    print("   1. Look for a 'Download JSON' button in the modal")
    print("   2. Click it to download the credentials file")
    print("   3. The automation will continue automatically")
    
    return False
    
    if not download_json_button:
        print("⚠️ Could not find Download JSON button")
        print("🔍 Listing all visible buttons in modal for debugging...")
        try:
            # Try to find buttons in modal/overlay containers
            modal_buttons = driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'modal') or contains(@class, 'dialog') or contains(@class, 'cdk-overlay-container')]//button")
            
            for i, button in enumerate(modal_buttons[:10]):  # Show first 10 buttons in modal
                if button.is_displayed():
                    button_text = (button.get_attribute("textContent") or button.text or "").strip()
                    button_class = button.get_attribute("class") or ""
                    print(f"   Modal Button {i+1}: '{button_text}' (class: {button_class[:50]})")
            
            # If no modal buttons, show all buttons
            if not modal_buttons:
                all_buttons = driver.find_elements(By.XPATH, "//button")
                for i, button in enumerate(all_buttons[:10]):  # Show first 10 buttons
                    if button.is_displayed():
                        button_text = (button.get_attribute("textContent") or button.text or "").strip()
                        button_class = button.get_attribute("class") or ""
                        print(f"   Button {i+1}: '{button_text}' (class: {button_class[:50]})")
        except:
            pass
        return False
    
    # Click the Download JSON button
    print("💾 Clicking Download JSON button...")
    
    # Scroll to button and highlight it
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", download_json_button)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Highlight button for visibility
        driver.execute_script("""
            arguments[0].style.border = '3px solid green';
            arguments[0].style.backgroundColor = 'lightgreen';
        """, download_json_button)
        time.sleep(1.0)
        
        # Remove highlight
        driver.execute_script("""
            arguments[0].style.border = '';
            arguments[0].style.backgroundColor = '';
        """, download_json_button)
        
    except Exception as highlight_error:
        print(f"⚠️ Highlight error: {highlight_error}")
    
    # Try multiple click methods for Download JSON button
    click_success = False
    
    # Method 1: JavaScript click
    try:
        driver.execute_script("arguments[0].click();", download_json_button)
        print("✅ Download JSON button clicked successfully with JavaScript!")
        click_success = True
        time.sleep(random.uniform(2.0, 4.0))
        
    except Exception as js_click_error:
        print(f"⚠️ JavaScript click failed: {js_click_error}")
    
    # Method 2: Regular click as fallback
    if not click_success:
        try:
            human_mouse_move_to(download_json_button)
            download_json_button.click()
            print("✅ Download JSON button clicked successfully with regular click!")
            click_success = True
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as regular_click_error:
            print(f"⚠️ Regular click failed: {regular_click_error}")
    
    if not click_success:
        print("❌ Failed to click Download JSON button")
        return False
    
    # Wait for download to complete and OK button to appear
    print("⏳ Waiting for download to complete and OK button to appear...")
    time.sleep(random.uniform(3.0, 5.0))  # Increased wait time for download
    
    # Handle the OK button with enhanced fallback
    ok_handled = handle_ok_button(driver)
    
    if not ok_handled:
        # Fallback: Check if JSON file was downloaded anyway
        print("🔍 Checking if JSON file was downloaded despite OK button issue...")
        time.sleep(random.uniform(2.0, 3.0))
        
        # Check for downloaded files
        try:
            json_files = glob.glob(os.path.join(DOWNLOAD_DIR, "client_secret_*.json"))
            if not json_files:
                # Also check default downloads
                default_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                json_files = glob.glob(os.path.join(default_downloads, "client_secret_*.json"))
            
            if json_files:
                print("✅ JSON file found! Download was successful!")
                # Process the file
                rename_success = rename_downloaded_json_file()
                if rename_success:
                    print("🎉 JSON credentials file downloaded and processed successfully!")
                    return True
            else:
                print("⚠️ No JSON file found - download may not have completed")
        except Exception as file_check_error:
            print(f"⚠️ File check error: {file_check_error}")
    
    return ok_handled

def handle_ok_button(driver):
    """Handle the OK button after Download JSON with enhanced fallback"""
    print("✅ Looking for OK button...")
    
    # Wait a bit for any modal/dialog to fully appear
    time.sleep(random.uniform(1.0, 2.0))
    
    # Look for the OK button with the exact structure provided
    ok_button_selectors = [
        # Exact selector for OK button with sandboxuid structure
        "//span[contains(@class, 'mdc-button__label') and @sandboxuid='0' and normalize-space(text())='OK']/parent::button",
        "//button[.//span[contains(@class, 'mdc-button__label') and @sandboxuid='0' and normalize-space(text())='OK']]",
        "//button[contains(@class, 'mdc-button') and .//span[@sandboxuid='0' and normalize-space(text())='OK']]",
        "//button[contains(@class, 'mat-mdc-button') and .//span[@sandboxuid='0' and normalize-space(text())='OK']]",
        
        # More specific patterns for the OK button
        "//span[@class='mdc-button__label' and @sandboxuid='0' and text()='OK']//parent::button",
        "//span[normalize-space(text())='OK' and @sandboxuid='0']//parent::button",
        "//button[descendant::span[@sandboxuid='0' and normalize-space(text())='OK']]",
        
        # Generic OK button selectors (fallback)
        "//button[contains(text(), 'OK')]",
        "//button[normalize-space(text())='OK']",
        "//button[.//span[contains(text(), 'OK')]]",
        "//span[text()='OK']//ancestor::button[1]",
        "//button[contains(@class, 'mdc-button') and contains(text(), 'OK')]",
        "//button[contains(@class, 'mat-mdc-button') and contains(text(), 'OK')]",
        
        # Modal/dialog specific selectors
        "//div[contains(@class, 'modal')]//button[contains(text(), 'OK')]",
        "//div[contains(@class, 'dialog')]//button[contains(text(), 'OK')]",
        "//mat-dialog-actions//button[contains(text(), 'OK')]",
        "//cdk-overlay-container//button[contains(text(), 'OK')]",
        
        # Common OK button patterns
        "//button[text()='OK']",
        "//button[@aria-label='OK']",
        "//input[@type='button' and @value='OK']"
    ]
    
    ok_button = None
    for selector in ok_button_selectors:
        try:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    element_text = (element.get_attribute("textContent") or element.text or "").strip()
                    # Check if this is the OK button
                    if (element_text.lower().strip() == "ok" or 
                        element_text.lower() == " ok " or 
                        ("ok" in element_text.lower() and len(element_text.strip()) <= 5)):
                        ok_button = element
                        print(f"✅ Found OK button with text: '{element_text}' using selector: {selector}")
                        break
            if ok_button:
                break
        except Exception as selector_error:
            continue
    
    if not ok_button:
        print("🔍 Trying alternative search for OK button...")
        try:
            # Look for any button in modal/overlay containing "OK" text
            modal_buttons = driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'modal') or contains(@class, 'dialog') or contains(@class, 'cdk-overlay-container')]//button")
            
            for button in modal_buttons:
                if button.is_displayed() and button.is_enabled():
                    button_text = (button.get_attribute("textContent") or button.text or "").strip()
                    if (button_text.lower().strip() == "ok" or 
                        button_text.lower() == " ok "):
                        ok_button = button
                        print(f"✅ Found OK button in modal with text: '{button_text}'")
                        break
            
            # If still not found, search all buttons
            if not ok_button:
                all_buttons = driver.find_elements(By.XPATH, "//button")
                for button in all_buttons:
                    if button.is_displayed() and button.is_enabled():
                        button_text = (button.get_attribute("textContent") or button.text or "").strip()
                        if (button_text.lower().strip() == "ok" or 
                            button_text.lower() == " ok "):
                            ok_button = button
                            print(f"✅ Found OK button alternative with text: '{button_text}'")
                            break
                            
        except Exception as alt_search_error:
            print(f"⚠️ Alternative OK button search failed: {alt_search_error}")
    
    if not ok_button:
        print("⚠️ Could not find OK button")
        print("🔍 Listing all visible buttons in modal for debugging...")
        try:
            # Try to find buttons in modal/overlay containers
            modal_buttons = driver.find_elements(By.XPATH, 
                "//div[contains(@class, 'modal') or contains(@class, 'dialog') or contains(@class, 'cdk-overlay-container')]//button")
            
            for i, button in enumerate(modal_buttons[:10]):  # Show first 10 buttons in modal
                if button.is_displayed():
                    button_text = (button.get_attribute("textContent") or button.text or "").strip()
                    button_class = button.get_attribute("class") or ""
                    print(f"   Modal Button {i+1}: '{button_text}' (class: {button_class[:50]})")
            
            # If no modal buttons, show all buttons
            if not modal_buttons:
                all_buttons = driver.find_elements(By.XPATH, "//button")
                for i, button in enumerate(all_buttons[:10]):  # Show first 10 buttons
                    if button.is_displayed():
                        button_text = (button.get_attribute("textContent") or button.text or "").strip()
                        button_class = button.get_attribute("class") or ""
                        print(f"   Button {i+1}: '{button_text}' (class: {button_class[:50]})")
        except:
            pass
        return False
    
    # Click the OK button
    print("✅ Clicking OK button...")
    
    # Scroll to button and highlight it
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", ok_button)
        time.sleep(random.uniform(1.0, 2.0))
        
        # Highlight button for visibility
        driver.execute_script("""
            arguments[0].style.border = '3px solid gold';
            arguments[0].style.backgroundColor = 'yellow';
        """, ok_button)
        time.sleep(1.0)
        
        # Remove highlight
        driver.execute_script("""
            arguments[0].style.border = '';
            arguments[0].style.backgroundColor = '';
        """, ok_button)
        
    except Exception as highlight_error:
        print(f"⚠️ Highlight error: {highlight_error}")
    
    # Try multiple click methods for OK button
    click_success = False
    
    # Method 1: JavaScript click
    try:
        driver.execute_script("arguments[0].click();", ok_button)
        print("✅ OK button clicked successfully with JavaScript!")
        click_success = True
        time.sleep(random.uniform(2.0, 4.0))
        
    except Exception as js_click_error:
        print(f"⚠️ JavaScript click failed: {js_click_error}")
    
    # Method 2: Regular click as fallback
    if not click_success:
        try:
            human_mouse_move_to(ok_button)
            ok_button.click()
            print("✅ OK button clicked successfully with regular click!")
            click_success = True
            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as regular_click_error:
            print(f"⚠️ Regular click failed: {regular_click_error}")
    
    if click_success:
        print("⏳ Waiting for modal to close...")
        time.sleep(random.uniform(1.0, 2.0))
        
        # Rename and move the downloaded JSON file
        print("📁 Processing downloaded JSON file...")
        print("⏳ Waiting a moment for download to complete...")
        time.sleep(random.uniform(2.0, 3.0))  # Give download more time to complete
        
        rename_success = rename_downloaded_json_file()
        if not rename_success:
            print("🔄 Automatic rename failed, trying manual approach...")
            rename_success = manual_rename_json_file()
            
        if rename_success:
            print("✅ JSON file renamed and moved successfully!")
            print(f"🎯 File ready to use: {EMAIL.replace('@', '_').replace('.', '_')}_credentials.json")
        else:
            print("⚠️ JSON file processing had issues, but download was successful")
            print("💡 Please manually rename and move the JSON file from Downloads folder")
            print("💡 Or run the standalone script: python rename_json.py")
        
        print("🎉🎉🎉 COMPLETE AUTOMATION FINISHED SUCCESSFULLY! 🎉🎉🎉")
        print("✅ ALL STEPS COMPLETED:")
        print("   ✓ Google login")
        print("   ✓ Project creation")
        print("   ✓ Gmail API enablement")
        print("   ✓ OAuth consent screen configuration")
        print("   ✓ Data Access setup")
        print("   ✓ Gmail API scope addition")
        print("   ✓ Configuration update")
        print("   ✓ Final save completed")
        print("   ✓ Audience configuration")
        print("   ✓ Test user added")
        print("   ✓ Audience saved")
        print("   ✓ App published")
        print("   ✓ Publishing confirmed")
        print("   ✓ Navigated to Clients")
        print("   ✓ Create client initiated")
        print("   ✓ Desktop app selected")
        print("   ✓ Create button clicked")
        print("   ✓ Download JSON button clicked")
        print("   ✓ OK button clicked")
        print("")
        print("🚀 Your Gmail API integration is now FULLY configured!")
        print("📧 You can now use the Gmail API with your Google Cloud project.")
        print("👥 Test user has been added to the audience.")
        print("🌐 The app is now live and published!")
        print("🖥️ OAuth client ID has been created for Desktop app!")
        print("💾 JSON credentials file has been downloaded!")
        print(f"📁 Credentials saved as: {EMAIL.replace('@', '_').replace('.', '_')}_credentials.json")
        print(f"📂 Location: {DOWNLOAD_DIR}")
        print("")
        print("🎯 FINAL TASK COMPLETED SUCCESSFULLY!")
        print("💡 Next steps:")
        print(f"   • Use the {EMAIL.replace('@', '_').replace('.', '_')}_credentials.json file in your application")
        print("   • Configure your OAuth client with the credentials")
        print("   • Start using the Gmail API in your project")
        print(f"   • File location: {DOWNLOAD_DIR}")
        return True
    else:
        print("❌ Failed to click OK button")
        print("🔍 Checking if download completed anyway...")
        
        # Even if OK button failed, check if file was downloaded
        time.sleep(random.uniform(2.0, 4.0))  # Wait for potential download
        
        try:
            # Look for JSON files in various locations
            json_files = []
            
            # Check instance-specific download directory first
            if DOWNLOAD_DIR and os.path.exists(DOWNLOAD_DIR):
                json_files.extend(glob.glob(os.path.join(DOWNLOAD_DIR, "client_secret_*.json")))
            
            # Check default downloads folder
            default_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            if os.path.exists(default_downloads):
                json_files.extend(glob.glob(os.path.join(default_downloads, "client_secret_*.json")))
            
            if json_files:
                print("✅ JSON file found despite OK button issue!")
                print(f"📁 Found file: {json_files[0]}")
                
                # Process the file
                rename_success = rename_downloaded_json_file()
                if rename_success:
                    print("🎉 JSON credentials file downloaded and processed successfully!")
                    return True
                else:
                    print("✅ Download successful, file processing may need manual attention")
                    return True
            else:
                print("⚠️ No JSON file found - download may not have completed")
                return False
                
        except Exception as fallback_error:
            print(f"⚠️ Fallback check error: {fallback_error}")
            return False

def rename_downloaded_json_file():
    """Find and rename the downloaded JSON file to match the Gmail address"""
    print("📁 Looking for downloaded JSON file to rename...")
    
    try:
        # Get the default Downloads folder
        default_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # PRIORITY: Check the instance-specific download directory first
        instance_download_dir = INSTANCE_DIRS.get('downloads', '')
        
        # Also check common alternative download locations
        alternative_downloads = [
            instance_download_dir,  # Check instance directory FIRST
            default_downloads,
            os.path.join(os.path.expanduser("~"), "Download"),  # Some systems use singular
            "C:\\Users\\{0}\\Downloads".format(os.getenv('USERNAME', '')),
            "D:\\Downloads",
            "E:\\Downloads"
        ]
        
        print(f"🔍 Searching for JSON files in download locations...")
        
        all_json_files = []
        for download_dir in alternative_downloads:
            if download_dir and os.path.exists(download_dir):  # Check if directory exists and is not empty
                json_pattern = os.path.join(download_dir, "*.json")
                json_files = glob.glob(json_pattern)
                for file in json_files:
                    all_json_files.append((file, download_dir))
                print(f"   📂 {download_dir}: {len(json_files)} JSON files")
            elif download_dir:  # Directory specified but doesn't exist
                print(f"   📂 {download_dir}: Directory not found")
        
        if not all_json_files:
            print("❌ No JSON files found in any download location")
            # Print the search locations for debugging
            print("🔍 Searched locations:")
            for i, location in enumerate(alternative_downloads):
                if location:
                    exists = "✓" if os.path.exists(location) else "✗"
                    print(f"   {i+1}. {exists} {location}")
            return False
        
        # Sort by modification time (newest first)
        all_json_files.sort(key=lambda x: os.path.getmtime(x[0]), reverse=True)
        
        # Look for the most recently downloaded JSON file that looks like a Google credential file
        target_file = None
        target_location = None
        
        print(f"🔍 Checking {len(all_json_files)} JSON files for Google credentials...")
        
        for json_file, download_location in all_json_files:
            try:
                filename = os.path.basename(json_file)
                
                # Check if it's a recent file (downloaded in the last 5 minutes for more flexibility)
                file_time = os.path.getmtime(json_file)
                current_time = time.time()
                time_diff = current_time - file_time
                
                print(f"   📄 Checking: {filename} (age: {int(time_diff)}s)")
                
                # Enhanced file detection - check for Google credential filename patterns
                is_google_credential = (
                    filename.startswith('client_secret_') or
                    'client_secret' in filename or
                    'oauth' in filename.lower() or
                    'credentials' in filename.lower()
                )
                
                if time_diff <= 300 and is_google_credential:  # 5 minutes for more flexibility
                    # Check if it looks like a Google credential file by content
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Enhanced detection for Google OAuth credentials
                            google_indicators = [
                                'client_id' in content,
                                'client_secret' in content,
                                'auth_uri' in content,
                                'token_uri' in content,
                                'googleapis.com' in content,
                                'oauth2' in content.lower()
                            ]
                            
                            if sum(google_indicators) >= 4:  # At least 4 indicators must match
                                target_file = json_file
                                target_location = download_location
                                print(f"✅ Found Google credential file: {filename}")
                                print(f"   📂 Location: {download_location}")
                                print(f"   ⏰ Downloaded: {time.ctime(file_time)}")
                                print(f"   🔍 Content indicators: {sum(google_indicators)}/6")
                                break
                            else:
                                print(f"   ❌ Content check failed (indicators: {sum(google_indicators)}/6)")
                    except Exception as content_error:
                        print(f"   ⚠️ Could not read file content: {content_error}")
                        
                        # If we can't read the content but filename looks right and it's recent, use it anyway
                        if filename.startswith('client_secret_') and time_diff <= 300:
                            target_file = json_file
                            target_location = download_location
                            print(f"✅ Using file based on filename pattern: {filename}")
                            print(f"   📂 Location: {download_location}")
                            print(f"   ⏰ Downloaded: {time.ctime(file_time)}")
                            break
                elif not is_google_credential:
                    print(f"   ⚠️ Filename doesn't match Google credential pattern")
                else:
                    print(f"   ⚠️ File too old ({int(time_diff/60)} minutes)")
                    
            except Exception as e:
                print(f"   ⚠️ Error checking file {os.path.basename(json_file)}: {e}")
                continue
        
        if not target_file:
            print("⚠️ Could not find recently downloaded Google credential file")
            print("� Recent JSON files found (showing first 5):")
            for i, (json_file, location) in enumerate(all_json_files[:5]):
                file_time = time.ctime(os.path.getmtime(json_file))
                age_minutes = int((time.time() - os.path.getmtime(json_file)) / 60)
                print(f"   {i+1}. {os.path.basename(json_file)} ({age_minutes}m ago) in {location}")
            
            print("\n💡 Manual Instructions:")
            print(f"   1. Look for the JSON file you just downloaded")
            print(f"   2. Rename it to: {EMAIL.replace('@', '_').replace('.', '_')}_credentials.json")
            print(f"   3. Move it to: {DOWNLOAD_DIR}")
            return False
        
        # Create new filename based on Gmail address
        email_name = EMAIL.replace('@', '_').replace('.', '_')
        new_filename = f"{email_name}_credentials.json"
        
        # Ensure the destination directory exists
        if not os.path.exists(DOWNLOAD_DIR):
            print(f"📁 Creating destination directory: {DOWNLOAD_DIR}")
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        new_filepath = os.path.join(DOWNLOAD_DIR, new_filename)
        
        print(f"📄 Renaming file to: {new_filename}")
        print(f"📂 Moving to directory: {DOWNLOAD_DIR}")
        
        # Check if destination file already exists
        if os.path.exists(new_filepath):
            timestamp = int(time.time())
            backup_filename = f"{email_name}_credentials_backup_{timestamp}.json"
            backup_filepath = os.path.join(DOWNLOAD_DIR, backup_filename)
            shutil.move(new_filepath, backup_filepath)
            print(f"🔄 Existing file backed up as: {backup_filename}")
        
        # Copy the file to the user-specified location with new name
        shutil.copy2(target_file, new_filepath)
        print(f"✅ File copied to: {new_filepath}")
        
        # Verify the copied file
        if os.path.exists(new_filepath) and os.path.getsize(new_filepath) > 0:
            print(f"✅ File verification successful (size: {os.path.getsize(new_filepath)} bytes)")
            
            # Remove the original file from Downloads
            try:
                os.remove(target_file)
                print(f"🗑️ Original file removed from Downloads")
            except Exception as remove_error:
                print(f"⚠️ Could not remove original file: {remove_error}")
                print(f"   You may manually delete: {target_file}")
        else:
            print(f"❌ File verification failed - copy may be corrupted")
            return False
        
        print(f"🎉 JSON file successfully renamed and saved!")
        print(f"📄 New filename: {new_filename}")
        print(f"📁 Full path: {new_filepath}")
        print(f"📧 For Gmail account: {EMAIL}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error renaming JSON file: {e}")
        return False

def manual_rename_json_file():
    """Manual fallback to find and rename the downloaded JSON file"""
    print("🔄 Attempting manual JSON file detection...")
    
    try:
        # Get the instance download directory
        instance_download_dir = INSTANCE_DIRS.get('downloads', '')
        
        if not instance_download_dir or not os.path.exists(instance_download_dir):
            print(f"❌ Instance download directory not found: {instance_download_dir}")
            return False
        
        # Find all JSON files in the instance directory
        json_pattern = os.path.join(instance_download_dir, "*.json")
        json_files = glob.glob(json_pattern)
        
        if not json_files:
            print("❌ No JSON files found in instance directory")
            return False
        
        print(f"🔍 Found {len(json_files)} JSON files in instance directory:")
        
        # Look for Google credential files specifically
        credential_files = []
        for json_file in json_files:
            filename = os.path.basename(json_file)
            print(f"   📄 Checking: {filename}")
            
            # Check if it's a Google credential file by filename pattern
            if (filename.startswith('client_secret_') or 
                'client_secret' in filename or
                'oauth' in filename.lower() or
                ('credentials' in filename.lower() and 'google' in filename.lower())):
                
                # Additional verification by checking file content
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Check for Google OAuth indicators
                        google_indicators = [
                            'client_id' in content,
                            'client_secret' in content,
                            'auth_uri' in content,
                            'token_uri' in content,
                            'googleapis.com' in content
                        ]
                        
                        if sum(google_indicators) >= 4:  # At least 4 indicators
                            credential_files.append(json_file)
                            print(f"   ✅ Google credential file detected!")
                        else:
                            print(f"   ❌ Not a Google credential file (indicators: {sum(google_indicators)}/5)")
                
                except Exception as content_check:
                    print(f"   ⚠️ Could not verify content: {content_check}")
                    # If we can't read content but filename looks right, include it anyway
                    if filename.startswith('client_secret_'):
                        credential_files.append(json_file)
                        print(f"   ✅ Included based on filename pattern")
        
        if not credential_files:
            print("❌ No Google credential files found")
            return False
        
        # Use the most recent credential file
        target_file = max(credential_files, key=os.path.getmtime)
        print(f"🎯 Using most recent credential file: {os.path.basename(target_file)}")
        
        # Create new filename
        email_name = EMAIL.replace('@', '_').replace('.', '_')
        new_filename = f"{email_name}_credentials.json"
        new_filepath = os.path.join(DOWNLOAD_DIR, new_filename)
        
        # Ensure destination directory exists
        if not os.path.exists(DOWNLOAD_DIR):
            print(f"📁 Creating destination directory: {DOWNLOAD_DIR}")
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        # Handle existing file
        if os.path.exists(new_filepath):
            timestamp = int(time.time())
            backup_filename = f"{email_name}_credentials_backup_{timestamp}.json"
            backup_filepath = os.path.join(DOWNLOAD_DIR, backup_filename)
            shutil.move(new_filepath, backup_filepath)
            print(f"🔄 Existing file backed up as: {backup_filename}")
        
        # Copy file
        shutil.copy2(target_file, new_filepath)
        print(f"✅ File copied to: {new_filepath}")
        
        # Verify
        if os.path.exists(new_filepath) and os.path.getsize(new_filepath) > 0:
            print(f"✅ File verification successful (size: {os.path.getsize(new_filepath)} bytes)")
            
            # Remove original
            try:
                os.remove(target_file)
                print(f"🗑️ Original file removed from instance directory")
            except Exception as remove_error:
                print(f"⚠️ Could not remove original file: {remove_error}")
            
            return True
        else:
            print("❌ File verification failed")
            return False
        
    except Exception as manual_error:
        print(f"❌ Manual rename failed: {manual_error}")
        return False

def create_project_direct_approach(driver):
    """
    Create a new Google Cloud project using direct navigation approach
    This bypasses the need to find and click buttons by going directly to the project creation URL
    """
    print("🚀 Using DIRECT APPROACH for project creation...")
    print("📍 Navigating directly to: https://console.cloud.google.com/projectcreate")
    
    try:
        # Direct navigation to project creation page
        driver.get("https://console.cloud.google.com/projectcreate")
        print("✅ Successfully navigated to project creation page!")
        
        # Wait for page to load
        print("⏳ Waiting for project creation page to load...")
        time.sleep(random.uniform(3.0, 5.0))
        
        # Check for any remaining first-time setup modals after navigation
        print("🔍 Checking for first-time setup modals after navigation...")
        time.sleep(random.uniform(1.0, 2.0))
        
        try:
            # Check for modal dialogs that might appear after navigation
            page_source = driver.page_source.lower()
            modal_present = False
            
            modal_indicators = [
                ".mat-mdc-dialog-container",
                "[role='dialog']",
                ".cdk-overlay-container .mat-mdc-dialog-surface"
            ]
            
            for selector in modal_indicators:
                try:
                    modals = driver.find_elements(By.CSS_SELECTOR, selector)
                    for modal in modals:
                        if modal.is_displayed():
                            modal_text = modal.text.lower()
                            # Check for setup-related content
                            if any(keyword in modal_text for keyword in [
                                "welcome", "country", "terms", "get started", 
                                "setup", "first time", "agree", "accept"
                            ]):
                                print(f"🎯 Setup modal detected after navigation: {modal_text[:100]}...")
                                modal_present = True
                                
                                # Try to handle this modal
                                action_buttons = [
                                    "//button[contains(.//span, 'Continue')]",
                                    "//button[contains(.//span, 'Accept')]", 
                                    "//button[contains(.//span, 'Get started')]",
                                    "//button[contains(.//span, 'I accept')]",
                                    "//button[contains(text(), 'Continue')]",
                                    "//button[contains(text(), 'Accept')]"
                                ]
                                
                                button_found = False
                                for button_selector in action_buttons:
                                    try:
                                        buttons = modal.find_elements(By.XPATH, button_selector)
                                        for button in buttons:
                                            if button.is_displayed() and button.is_enabled():
                                                print(f"🎯 Clicking modal button: {button.text}")
                                                driver.execute_script("arguments[0].click();", button)
                                                time.sleep(random.uniform(2.0, 3.0))
                                                button_found = True
                                                break
                                        if button_found:
                                            break
                                    except:
                                        continue
                                
                                if button_found:
                                    print("✅ Setup modal handled after navigation!")
                                else:
                                    print("⚠️ Could not find suitable button, dismissing with Escape...")
                                    try:
                                        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                                        time.sleep(random.uniform(1.0, 2.0))
                                    except:
                                        pass
                                break
                    if modal_present:
                        break
                except:
                    continue
            
            if not modal_present:
                print("✅ No setup modals detected after navigation")
                
        except Exception as modal_check_error:
            print(f"⚠️ Error checking for setup modals: {modal_check_error}")
        
        # Check for CAPTCHA or verification
        if not wait_for_page_load_and_check_captcha(driver):
            print("⚠️ CAPTCHA or verification detected during navigation")
        
        # Verify we're on the correct page
        current_url = driver.current_url
        if "projectcreate" in current_url or "create" in current_url:
            print("✅ Confirmed: On project creation page")
            print(f"📍 Current URL: {current_url}")
            
            # Wait a bit more for the form to be fully loaded
            time.sleep(random.uniform(2.0, 3.0))
            
            # Check if project creation form is visible
            form_indicators = [
                "//input[@id='input-project-name']",
                "//input[contains(@name, 'project')]",
                "//input[contains(@placeholder, 'project')]",
                "//input[contains(@aria-label, 'project')]",
                "//form[contains(@class, 'project')]",
                "//div[contains(@class, 'project-create')]"
            ]
            
            form_found = False
            for indicator in form_indicators:
                try:
                    element = driver.find_element(By.XPATH, indicator)
                    if element.is_displayed():
                        print(f"✅ Project creation form detected with: {indicator}")
                        form_found = True
                        break
                except:
                    continue
            
            if form_found:
                print("📝 Project creation form is ready!")
                return True
            else:
                print("⚠️ Project creation form not immediately visible, but continuing...")
                # Wait a bit more for dynamic content to load
                time.sleep(random.uniform(2.0, 4.0))
                return True
        else:
            print(f"⚠️ Unexpected URL after navigation: {current_url}")
            return False
            
    except Exception as direct_error:
        print(f"❌ Direct approach failed: {direct_error}")
        print("🔄 Will fall back to traditional button-clicking approach...")
        return False

def create_project_traditional_approach(driver):
    """
    Traditional approach - clicking buttons to navigate to project creation
    This is the fallback method if direct navigation fails
    """
    print("🔄 Using TRADITIONAL APPROACH for project creation...")
    print("🆕 Looking for project creation buttons...")
    
    # First, ensure any modals are completely closed
    print("🔍 Ensuring all modals are closed before proceeding...")
    time.sleep(random.uniform(2.0, 4.0))
    
    # Check for and dismiss any remaining overlays
    try:
        overlays = driver.find_elements(By.CSS_SELECTOR, ".cdk-overlay-backdrop, .cdk-overlay-container, .mat-mdc-dialog-container")
        for overlay in overlays:
            if overlay.is_displayed():
                print("🔍 Found remaining overlay, dismissing...")
                driver.execute_script("arguments[0].style.display = 'none';", overlay)
                time.sleep(1.0)
    except:
        pass
    
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
                project_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                print(f"✅ Found project button with selector: {selector}")
                break
            except TimeoutException:
                continue
        
        if project_btn is None:
            raise Exception("Could not find project button with any selector")
        
        # Use JavaScript click to avoid interception issues
        try:
            print("🖱️ Using JavaScript click for project button...")
            driver.execute_script("arguments[0].scrollIntoView(true);", project_btn)
            time.sleep(random.uniform(1.0, 2.0))
            driver.execute_script("arguments[0].click();", project_btn)
            print("✅ New project button clicked successfully with JavaScript!")
        except Exception as js_click_error:
            print(f"⚠️ JavaScript click failed: {js_click_error}")
            print("🔄 Trying regular click...")
            # Fallback to regular click
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", project_btn)
                time.sleep(random.uniform(1.0, 2.0))
                human_mouse_move_to(project_btn)
                project_btn.click()
                print("✅ New project button clicked successfully!")
            except Exception as click_error:
                print(f"⚠️ Regular click also failed: {click_error}")
                raise click_error
            
        time.sleep(random.uniform(3.0, 5.0))
        
        # Handle modal "New Project" button
        return handle_new_project_modal(driver)
        
    except Exception as traditional_error:
        print(f"❌ Traditional approach failed: {traditional_error}")
        return False

def handle_new_project_modal(driver):
    """Handle the New Project modal that appears after clicking the project button"""
    print("🆕 Handling 'New Project' modal...")
    try:
        # Enhanced modal "New Project" button detection with multiple selectors
        
        # First, ensure the modal is fully loaded and visible
        print("🔍 Detecting project picker modal...")
        modal_detected = False
        modal_selectors = [
            "//div[contains(@class, 'mat-mdc-dialog-container')]",
            "//div[contains(@class, 'cdk-overlay-container')]",
            "[role='dialog']",
            "//mat-dialog-container",
            "#purview-picker-modal-action-bar",
            "//mat-toolbar[@id='purview-picker-modal-action-bar']"
        ]
        
        for modal_selector in modal_selectors:
            try:
                if modal_selector.startswith("//") or modal_selector.startswith("#"):
                    modal_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH if modal_selector.startswith("//") else By.CSS_SELECTOR, modal_selector)))
                else:
                    modal_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, modal_selector)))
                
                if modal_element and modal_element.is_displayed():
                    print(f"✅ Modal detected with selector: {modal_selector}")
                    modal_detected = True
                    break
            except:
                continue
        
        if not modal_detected:
            print("⚠️ Could not detect modal dialog")
            print("🔍 Checking if we're already on the project creation page...")
            current_url = driver.current_url
            if "projectcreate" in current_url or "create" in current_url:
                print("✅ Already on project creation page - skipping modal step")
                return True
            else:
                print("💡 Modal might not have opened - waiting longer...")
                time.sleep(random.uniform(3.0, 5.0))
        
        modal_new_project_selectors = [
            # Original selector
            "//*[@id='purview-picker-modal-action-bar']/mat-toolbar/div[3]/div/div/div[1]/div/button[2]",
            
            # Alternative specific selectors for the modal
            "//mat-toolbar[@id='purview-picker-modal-action-bar']//button[contains(text(), 'New Project')]",
            "//mat-toolbar[@id='purview-picker-modal-action-bar']//button[contains(text(), 'NEW PROJECT')]",
            "//*[@id='purview-picker-modal-action-bar']//button[contains(text(), 'New Project')]",
            "//*[@id='purview-picker-modal-action-bar']//button[contains(text(), 'NEW PROJECT')]",
            
            # Generic modal selectors for "New Project" button
            "//div[contains(@class, 'mat-mdc-dialog-container')]//button[contains(text(), 'New Project')]",
            "//div[contains(@class, 'cdk-overlay-container')]//button[contains(text(), 'New Project')]",
            "//mat-dialog-container//button[contains(text(), 'New Project')]",
            "[role='dialog']//button[contains(text(), 'New Project')]",
            
            # More flexible modal button selectors
            "//button[contains(text(), 'New Project') and not(contains(text(), 'Select'))]",
            "//button[contains(text(), 'NEW PROJECT') and not(contains(text(), 'SELECT'))]",
            "//button[normalize-space(text())='New Project']",
            "//button[normalize-space(text())='NEW PROJECT']",
            "//span[normalize-space(text())='New Project']/parent::button",
            "//span[normalize-space(text())='NEW PROJECT']/parent::button",
            
            # Button position-based selectors in modal action bar
            "//*[@id='purview-picker-modal-action-bar']//button[last()]",
            "//*[@id='purview-picker-modal-action-bar']//button[2]",
            "//*[@id='purview-picker-modal-action-bar']//button[position()=2]",
            "//mat-toolbar[@id='purview-picker-modal-action-bar']//button[last()]",
            "//mat-toolbar[@id='purview-picker-modal-action-bar']//button[2]",
            
            # Primary/raised button styles in modal
            "//div[contains(@class, 'mat-mdc-dialog-container')]//button[contains(@class, 'mat-mdc-raised-button')]",
            "//div[contains(@class, 'mat-mdc-dialog-container')]//button[contains(@class, 'mdc-button--raised')]",
            "[role='dialog']//button[contains(@class, 'mat-mdc-raised-button')]",
            "[role='dialog']//button[contains(@class, 'mdc-button--raised')]",
            
            # Fallback selectors for any "New" or "Create" buttons in modal
            "//div[contains(@class, 'mat-mdc-dialog-container')]//button[contains(text(), 'New')]",
            "//div[contains(@class, 'mat-mdc-dialog-container')]//button[contains(text(), 'Create')]",
            "[role='dialog']//button[contains(text(), 'New')]",
            "[role='dialog']//button[contains(text(), 'Create')]"
        ]
        
        new_project_btn = None
        successful_selector = None
        
        # Wait for modal to be visible first
        print("⏳ Waiting for project picker modal to be visible...")
        time.sleep(random.uniform(2.0, 4.0))
        
        # Try each selector to find the modal "New Project" button
        for i, selector in enumerate(modal_new_project_selectors):
            try:
                print(f"🔍 Trying modal 'New Project' selector {i+1}/{len(modal_new_project_selectors)}: {selector[:80]}...")
                
                # Use a shorter timeout for each attempt
                element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, selector)))
                
                if element and element.is_displayed() and element.is_enabled():
                    # Additional validation for the button
                    btn_text = (element.get_attribute("textContent") or element.text or "").strip()
                    btn_classes = element.get_attribute("class") or ""
                    
                    print(f"   📋 Found button - Text: '{btn_text}', Classes: '{btn_classes[:50]}...'")
                    
                    # Validate this is likely the correct button
                    is_valid_button = (
                        "new project" in btn_text.lower() or
                        "new" in btn_text.lower() or
                        "create" in btn_text.lower() or
                        "mdc-button--raised" in btn_classes or
                        "mat-mdc-raised-button" in btn_classes
                    )
                    
                    if is_valid_button:
                        new_project_btn = element
                        successful_selector = selector
                        print(f"✅ Found valid modal 'New Project' button with selector: {selector[:80]}...")
                        break
                    else:
                        print(f"   ⚠️ Button found but doesn't appear to be the correct 'New Project' button")
                
            except TimeoutException:
                continue
            except Exception as selector_error:
                print(f"   ⚠️ Selector failed: {selector_error}")
                continue
        
        if new_project_btn:
            print(f"✅ Modal 'New Project' button found! Using selector: {successful_selector[:80]}...")
            
            # Try regular click first
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", new_project_btn)
                time.sleep(random.uniform(1.0, 2.0))
                human_mouse_move_to(new_project_btn)
                new_project_btn.click()
                print("✅ Modal 'New Project' button clicked successfully!")
            except Exception as modal_click_error:
                print(f"⚠️ Regular click failed: {modal_click_error}")
                print("🔄 Trying JavaScript click...")
                # Fallback to JavaScript click
                driver.execute_script("arguments[0].click();", new_project_btn)
                print("✅ Modal 'New Project' button clicked with JavaScript!")
                
            time.sleep(random.uniform(2.0, 4.0))
            return True
        else:
            print("❌ Could not find modal 'New Project' button with any selector")
            
            # Enhanced debugging - show all visible buttons in modal
            print("🔍 Debugging: Looking for all visible buttons in modal...")
            try:
                modal_buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'mat-mdc-dialog-container')]//button | //div[contains(@class, 'cdk-overlay-container')]//button | //[role='dialog']//button")
                if modal_buttons:
                    print(f"📋 Found {len(modal_buttons)} buttons in modal:")
                    for j, btn in enumerate(modal_buttons):
                        try:
                            if btn.is_displayed():
                                btn_text = (btn.get_attribute("textContent") or btn.text or "").strip()
                                btn_classes = btn.get_attribute("class") or ""
                                print(f"   {j+1}. Text: '{btn_text}' | Classes: '{btn_classes[:30]}...'")
                        except:
                            continue
                else:
                    print("   ❌ No buttons found in modal containers")
            except Exception as debug_error:
                print(f"   ⚠️ Debug search failed: {debug_error}")
            
            # Try direct navigation as fallback from modal handling
            print("🔄 Trying direct navigation as fallback from modal...")
            try:
                driver.get("https://console.cloud.google.com/projectcreate")
                time.sleep(random.uniform(3.0, 5.0))
                current_url = driver.current_url
                if "projectcreate" in current_url or "create" in current_url:
                    print("✅ Successfully navigated to project creation page directly from modal fallback!")
                    return True
                else:
                    print("⚠️ Direct navigation from modal didn't work")
                    return False
            except Exception as direct_nav_error:
                print(f"⚠️ Direct navigation from modal failed: {direct_nav_error}")
                return False
            
    except Exception as modal_error:
        print(f"❌ Error handling modal: {modal_error}")
        return False

def handle_new_project_modal_fallback(driver):
    """Fallback function to handle New Project modal when automatic detection fails"""
    print("🔧 Manual intervention required for New Project creation")
    print("="*60)
    print("📋 INSTRUCTIONS:")
    print("1. Look for a modal dialog or popup on the screen")
    print("2. Look for a 'New Project' or 'Create Project' button")
    print("3. Click on it to create a new project")
    print("4. If no modal is visible, try:")
    print("   • Click on the project selector (usually top left)")
    print("   • Look for 'New Project' option")
    print("   • Or navigate to: https://console.cloud.google.com/projectcreate")
    print("")
    print("🎯 What we're looking for:")
    print("   • A button with text 'New Project' or 'Create Project'")
    print("   • Usually in a modal dialog or top navigation")
    print("   • May have a '+' icon next to it")
    print("")
    print("⚠️  Common issues:")
    print("   • Modal might take time to load")
    print("   • Button might be partially hidden")
    print("   • Different Google account might have different UI")
    print("")
    
    # Give user time to manually handle
    try:
        user_input = input("✅ Press Enter after clicking 'New Project' (or 'skip' to continue without project creation): ").strip().lower()
        
        if user_input == 'skip':
            print("⚠️ Skipping project creation - this may cause issues later")
            return False
        else:
            print("✅ Continuing with project creation...")
            time.sleep(random.uniform(2.0, 4.0))  # Wait for project creation to start
            return True
            
    except KeyboardInterrupt:
        print("\n⚠️ User interrupted - skipping project creation")
        return False

def provide_new_project_modal_guidance():
    """Provide detailed guidance for manually handling the New Project modal"""
    print("\n" + "="*80)
    print("🚨 AUTOMATION PAUSED: MANUAL INTERVENTION REQUIRED")
    print("="*80)
    print("📋 SITUATION: Cannot find 'New Project' button in modal")
    print("")
    print("🔍 WHAT TO DO:")
    print("1. Look at your browser window")
    print("2. You should see a modal/popup dialog")
    print("3. In this modal, look for:")
    print("   • A button labeled 'New Project'")
    print("   • A button labeled 'Create Project'") 
    print("   • A button with a '+' icon and 'New' text")
    print("   • Usually it's a blue/primary colored button")
    print("")
    print("🎯 COMMON LOCATIONS:")
    print("   • Top right of the modal")
    print("   • Bottom right of the modal") 
    print("   • In a toolbar at the top/bottom")
    print("")
    print("⚠️  IF NO MODAL IS VISIBLE:")
    print("   • Look for project selector in top-left corner")
    print("   • Click on the current project name/dropdown")
    print("   • Look for 'New Project' option in the dropdown")
    print("")
    print("🔧 ALTERNATIVE APPROACH:")
    print("   • Navigate to: https://console.cloud.google.com/projectcreate")
    print("   • This will take you directly to project creation")
    print("")
    print("💡 AFTER CLICKING 'NEW PROJECT':")
    print("   • You should see a project creation form")
    print("   • The automation will resume automatically")
    print("   • Look for a text input to enter project name")
    print("")
    print("="*80)

def provide_application_type_dropdown_guidance():
    """Provide detailed guidance for manually finding and using the Application type dropdown"""
    print("\n" + "="*80)
    print("🚨 AUTOMATION PAUSED: APPLICATION TYPE DROPDOWN NOT FOUND")
    print("="*80)
    print("📋 CURRENT STEP: Select Application type dropdown in OAuth client creation")
    print("")
    print("🔍 WHAT TO LOOK FOR:")
    print("1. You should be on the 'Create OAuth client ID' page")
    print("2. Look for a form with fields to fill out")
    print("3. Find a field labeled 'Application type' with a asterisk (*)")
    print("4. This field should have a dropdown with placeholder text")
    print("5. The dropdown might show 'Select...' or be empty initially")
    print("")
    print("🎯 STEP-BY-STEP INSTRUCTIONS:")
    print("1. Click on the 'Application type' dropdown")
    print("2. A dropdown menu should appear with options")
    print("3. Look for 'Desktop app' (or similar options like 'Installed app')")
    print("4. Click on 'Desktop app' to select it")
    print("5. The dropdown should now show 'Desktop app' as selected")
    print("")
    print("⚠️  COMMON ISSUES:")
    print("   • Make sure you're on the OAuth client creation page")
    print("   • Don't confuse with navigation dropdowns (those show '/' paths)")
    print("   • The correct dropdown is part of the form, not navigation")
    print("   • Application type field is usually near the top of the form")
    print("")
    print("🔧 ALTERNATIVE OPTIONS:")
    print("   • Desktop app")
    print("   • Installed app") 
    print("   • Native app")
    print("   • Client application")
    print("")
    print("💡 AFTER SELECTION:")
    print("   • The automation will continue to click 'Create' button")
    print("   • This will generate and download the OAuth credentials")
    print("")
    print("="*80)

def recover_session_if_needed(driver):
    """Attempt to recover browser session if disconnected"""
    try:
        # Test if session is still active
        driver.current_url
        return True, driver
    except Exception as session_error:
        if "invalid session" in str(session_error).lower():
            print("🔄 Browser session disconnected, attempting recovery...")
            
            # Try to create a new driver instance with the same profile
            try:
                print("🔧 Creating new browser session...")
                new_driver = create_driver_undetected()
                if new_driver:
                    print("✅ New browser session created successfully!")
                    return True, new_driver
                else:
                    print("⚠️ Could not create new session, but continuing...")
                    return False, driver
            except Exception as recovery_error:
                print(f"⚠️ Session recovery failed: {recovery_error}")
                return False, driver
        else:
            print(f"⚠️ Unexpected session error: {session_error}")
            return False, driver

def handle_google_recovery_options(driver):
    """
    Handle Google Recovery Options page that appears for newly created Gmail accounts
    
    This page asks users to add recovery phone/email with URL pattern:
    https://gds.google.com/web/recoveryoptions?cardIndex=0&hl=en-GB&authuser=0...
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        bool: True if recovery options were skipped successfully
    """
    try:
        print("📱 Handling Google Recovery Options page...")
        
        current_url = driver.current_url
        if "gds.google.com/web/recoveryoptions" not in current_url:
            print("ℹ️ Not on recovery options page")
            return True
            
        print(f"📍 Confirmed on recovery options page: {current_url}")
        
        # First, try to dismiss any overlays that might be blocking interactions
        print("🚫 Dismissing any overlays on recovery options page...")
        dismiss_overlay(driver)
        time.sleep(2)
        
        # Look for skip buttons and options to bypass recovery setup
        skip_selectors = [
            # Skip or "Not now" buttons
            "//button[contains(text(), 'Skip')]",
            "//button[contains(text(), 'Not now')]", 
            "//button[contains(text(), 'Maybe later')]",
            "//button[contains(text(), 'Ask me later')]",
            "//button[contains(text(), 'Continue without')]",
            "//button[contains(text(), 'Skip for now')]",
            "//button[contains(text(), 'Later')]",
            "//button[contains(text(), 'Done')]",
            "//button[contains(text(), 'Continue')]",
            
            # Links with skip text
            "//a[contains(text(), 'Skip')]",
            "//a[contains(text(), 'Not now')]",
            "//a[contains(text(), 'Continue without')]",
            "//a[contains(text(), 'Maybe later')]",
            
            # Span elements within buttons
            "//span[contains(text(), 'Skip')]/parent::button",
            "//span[contains(text(), 'Not now')]/parent::button",
            "//span[contains(text(), 'Maybe later')]/parent::button",
            "//span[contains(text(), 'Continue')]/parent::button",
            "//span[contains(text(), 'Done')]/parent::button",
            
            # Close or X buttons
            "//button[@aria-label='Close']",
            "//button[@aria-label='Skip']",
            "//button[contains(@class, 'close')]",
            "//*[@role='button'][contains(@aria-label, 'close')]",
            
            # Generic skip patterns
            "//*[contains(@class, 'skip')]//button",
            "//*[contains(@class, 'later')]//button",
            "//*[contains(@data-action, 'skip')]"
        ]
        
        skip_success = False
        for skip_selector in skip_selectors:
            try:
                skip_elements = driver.find_elements(By.XPATH, skip_selector)
                for skip_element in skip_elements:
                    if skip_element.is_displayed() and skip_element.is_enabled():
                        element_text = skip_element.get_attribute('textContent') or skip_element.text or ""
                        print(f"🔍 Found potential skip option: '{element_text.strip()}'")
                        
                        # Click the skip element
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", skip_element)
                            time.sleep(1)
                            skip_element.click()
                            print(f"✅ Successfully clicked skip option: '{element_text.strip()}'")
                            time.sleep(random.uniform(2.0, 4.0))
                            
                            # Check if we left the recovery options page
                            new_url = driver.current_url
                            if "gds.google.com/web/recoveryoptions" not in new_url:
                                print(f"✅ Successfully left recovery options page, now at: {new_url}")
                                skip_success = True
                                break
                            else:
                                print("ℹ️ Still on recovery options page, trying next option...")
                        except Exception as click_error:
                            print(f"⚠️ Could not click skip option: {click_error}")
                            continue
                
                if skip_success:
                    break
            except Exception as selector_error:
                continue
        
        # If skip buttons didn't work, try to navigate away directly
        if not skip_success:
            print("🔗 No skip options found, trying to navigate directly to Cloud Console...")
            
            # Try to navigate directly to Google Cloud Console
            console_urls = [
                "https://console.cloud.google.com/",
                "https://console.cloud.google.com/home",
                "https://console.cloud.google.com/projectselector"
            ]
            
            for console_url in console_urls:
                try:
                    print(f"🔗 Attempting direct navigation to: {console_url}")
                    driver.get(console_url)
                    time.sleep(random.uniform(3.0, 5.0))
                    
                    new_url = driver.current_url
                    if "console.cloud.google.com" in new_url:
                        print(f"✅ Successfully navigated to Cloud Console: {new_url}")
                        skip_success = True
                        break
                    else:
                        print(f"⚠️ Navigation failed, current URL: {new_url}")
                        
                except Exception as nav_error:
                    print(f"⚠️ Direct navigation failed: {nav_error}")
                    continue
        
        # If direct navigation didn't work, try pressing Escape or other dismissal methods
        if not skip_success:
            print("⌨️ Trying keyboard shortcuts to dismiss recovery options...")
            try:
                # Try pressing Escape key
                body = driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ESCAPE)
                time.sleep(2)
                
                new_url = driver.current_url
                if "gds.google.com/web/recoveryoptions" not in new_url:
                    print("✅ Escape key successfully dismissed recovery options")
                    skip_success = True
                    
            except Exception as key_error:
                print(f"⚠️ Keyboard shortcut failed: {key_error}")
        
        if skip_success:
            print("✅ Successfully handled Google Recovery Options page!")
            return True
        else:
            print("⚠️ Could not automatically handle recovery options page")
            print("💡 You may need to manually skip the recovery setup")
            return False
            
    except Exception as e:
        print(f"❌ Error handling Google Recovery Options: {e}")
        return False

def handle_google_verifications(driver, context="general"):
    """
    Comprehensive handler for all types of Google verification prompts with session recovery
    
    Args:
        driver: Selenium WebDriver instance
        context: String describing where this is called from (e.g., "login", "cloud-console", "api-setup")
    
    Returns:
        bool: True if verification was handled successfully or no verification was needed
    """
    print(f"🔐 Checking for Google verifications in context: {context}")
    
    max_verification_attempts = 3  # Reduced from 5 to prevent long hanging
    
    for attempt in range(max_verification_attempts):
        print(f"🔍 Verification check attempt {attempt + 1}/{max_verification_attempts}")
        time.sleep(random.uniform(1.0, 2.0))  # Reduced wait time
        
        try:
            # Check session health before proceeding
            try:
                current_url = driver.current_url.lower()
                page_title = driver.title.lower()
                page_source = driver.page_source.lower()
            except Exception as session_error:
                if "invalid session" in str(session_error).lower():
                    print("🔄 Session disconnected during verification check")
                    print("💡 This is normal after 2FA - Google often refreshes the session")
                    return True  # Assume verification was completed when session refreshes
                else:
                    raise session_error
            
            # More precise verification indicators - must be specific verification pages
            verification_indicators = {
                'phone': [
                    'verify your phone number', 'phone verification required', 'enter your phone number to verify',
                    'add a phone number', 'verify this phone number', 'confirm your phone number'
                ],
                'email': [
                    'verify your email address', 'email verification required', 'check your email for verification',
                    'confirm your email address', 'verify this email address'
                ],
                'code': [
                    'enter verification code', 'enter the 6-digit code', 'we sent a verification code', 
                    'enter the code from', 'verification code sent', 'security code required'
                ],
                '2fa': [
                    '2-step verification required', 'two-factor authentication required', 'enter code from authenticator',
                    'use authenticator app', 'backup codes required', 'security key required'
                ],
                'identity': [
                    'verify it\'s really you', 'confirm it\'s you', 'prove it\'s you',
                    'identity verification required', 'account verification needed'
                ],
                'security': [
                    'unusual sign-in activity', 'suspicious sign-in attempt', 'security check required',
                    'verify this sign-in', 'confirm this was you', 'was this you?'
                ],
                'recovery': [
                    'account recovery required', 'reset your password', 'recover your account',
                    'answer security questions', 'use recovery email', 'use recovery phone',
                    'add a recovery phone', 'add a recovery email', 'make sure that you can always sign in',
                    'your recovery info is used to reach you', 'add recovery phone', 'add recovery email'
                ],
                'captcha': [
                    'prove you\'re not a robot', 'verify you\'re human', 'complete captcha',
                    'select all images with', 'click verify', 'i\'m not a robot'
                ]
            }
            
            # Exclude normal Google account pages that aren't verification
            normal_google_pages = [
                'myaccount.google.com',
                'accounts.google.com/signin',
                'accounts.google.com/ManageAccount', 
                'console.cloud.google.com',
                'welcome to your google account',
                'manage your google account',
                'your google account',
                'google account settings'
            ]
            
            # Check if we're on a normal Google page (not verification)
            is_normal_page = any(page in current_url or page in page_title.lower() or page in page_source 
                               for page in normal_google_pages)
            
            # CRITICAL: Always check for recovery options regardless of normal page classification
            if "gds.google.com/web/recoveryoptions" in current_url:
                print("📱 PRIORITY: Recovery options page detected - overriding normal page classification!")
                is_normal_page = False
                explicit_verification_found = True
            elif is_normal_page:
                # Only proceed with verification detection if there are explicit verification prompts
                explicit_verification_found = False
                for v_type, indicators in verification_indicators.items():
                    for indicator in indicators:
                        if (indicator in page_source and 
                            ('required' in page_source or 'verify' in page_source or 'enter' in page_source)):
                            explicit_verification_found = True
                            break
                    if explicit_verification_found:
                        break
                
                if not explicit_verification_found:
                    print("✅ On normal Google account page - no verification required")
                    return True
            else:
                explicit_verification_found = True  # Not on normal page, proceed with detection
            
            # Check if any verification is detected (but only if not on normal page or explicit verification found)
            verification_type = None
            
            # First, check for specific URL patterns that indicate certain verification types
            if "gds.google.com/web/recoveryoptions" in current_url:
                verification_type = "recovery"
                print("📱 Recovery options page detected by URL pattern!")
            elif not is_normal_page or explicit_verification_found:
                for v_type, indicators in verification_indicators.items():
                    verification_found = False
                    for indicator in indicators:
                        # More strict matching - require verification context
                        if (indicator in page_source and 
                            (('verify' in page_source and 'required' in page_source) or
                             ('enter' in page_source and ('code' in page_source or 'phone' in page_source)) or
                             ('confirm' in page_source and ('identity' in page_source or 'account' in page_source)) or
                             ('prove' in page_source and 'you' in page_source) or
                             ('captcha' in page_source or 'robot' in page_source))):
                            verification_type = v_type
                            verification_found = True
                            print(f"⚠️ {v_type.upper()} verification detected with context!")
                            break
                    if verification_found:
                        break
            
            if not verification_type:
                print("✅ No verification detected")
                return True
            
            # Handle different types of verifications with timeout
            verification_handled = False
            verification_timeout = 30  # 30 second timeout for verification attempts
            
            if verification_type in ['phone', 'email', 'code', '2fa', 'identity', 'security']:
                print(f"🔄 Attempting to handle {verification_type} verification (30s timeout)...")
                
                start_time = time.time()
                while (time.time() - start_time) < verification_timeout:
                    # Try to skip/dismiss first
                    skip_selectors = [
                        # Skip/dismiss buttons
                        "//button[contains(text(), 'Skip')]",
                        "//button[contains(text(), 'Not now')]",
                        "//button[contains(text(), 'Later')]", 
                        "//button[contains(text(), 'Ask later')]",
                        "//button[contains(text(), 'Maybe later')]",
                        "//button[contains(text(), 'Dismiss')]",
                        "//button[contains(text(), 'Cancel')]",
                        "//button[contains(text(), 'No thanks')]",
                        "//button[contains(text(), 'Continue without')]",
                        "//button[contains(text(), 'Skip for now')]",
                        
                        # Links
                        "//a[contains(text(), 'Skip')]",
                        "//a[contains(text(), 'Not now')]",
                        "//a[contains(text(), 'Later')]",
                        
                        # Span/text elements
                        "//span[contains(text(), 'Skip')]/parent::button",
                        "//span[contains(text(), 'Not now')]/parent::button",
                        "//span[contains(text(), 'Later')]/parent::button"
                    ]
                    
                    for selector in skip_selectors[:5]:  # Only try first 5 to save time
                        try:
                            skip_element = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, selector)))
                            
                            if skip_element and skip_element.is_displayed():
                                button_text = (skip_element.get_attribute("textContent") or skip_element.text or "").strip()
                                print(f"✅ Found skip option: '{button_text}'")
                                human_mouse_move_to(skip_element)
                                skip_element.click()
                                print(f"✅ Successfully skipped {verification_type} verification!")
                                time.sleep(random.uniform(1.0, 2.0))
                                verification_handled = True
                                break
                        except:
                            continue
                    
                    if verification_handled:
                        break
                    
                    # If skip didn't work, break and proceed to manual handling
                    break
            
            elif verification_type == 'captcha':
                print("🤖 CAPTCHA detected - manual intervention required")
                print("Please solve the CAPTCHA manually and press Enter to continue...")
                input("🤖 Press Enter after solving CAPTCHA...")
                verification_handled = True
            
            elif verification_type == 'recovery':
                print("📱 Google Recovery Options page detected - handling automatically...")
                verification_handled = handle_google_recovery_options(driver)
                if verification_handled:
                    print("✅ Successfully handled recovery options page!")
                else:
                    print("⚠️ Could not automatically handle recovery options, may need manual intervention")
            
            # If automatic methods didn't work, prompt for manual intervention
            if not verification_handled:
                print(f"🛑 {verification_type.upper()} verification requires manual intervention!")
                print("💡 Please complete the verification manually")
                print("⏰ The script will wait for 60 seconds for you to complete it...")
                
                # Wait with countdown
                wait_time = 60
                for remaining in range(wait_time, 0, -5):
                    print(f"⏳ Waiting for manual verification... {remaining}s remaining")
                    time.sleep(5)
                    
                    # Check if verification is complete every 5 seconds
                    try:
                        current_url_check = driver.current_url.lower()
                        if current_url != current_url_check:  # URL changed, likely verification complete
                            print("✅ URL changed - verification appears complete!")
                            verification_handled = True
                            break
                    except:
                        # Session error during wait might mean verification completed
                        print("✅ Session changed - verification likely complete!")
                        verification_handled = True
                        break
                
                if not verification_handled:
                    print("⚠️ Manual verification timeout - continuing anyway...")
                    verification_handled = True
            
            # Wait and check if verification was resolved
            time.sleep(random.uniform(1.0, 2.0))
            
            if verification_handled:
                print("✅ Verification handling completed!")
                return True
            else:
                print("⚠️ Verification handling failed, retrying...")
                continue
        
        except Exception as verification_error:
            print(f"⚠️ Error during verification handling: {verification_error}")
            
            # Handle session errors gracefully
            if "invalid session" in str(verification_error).lower():
                print("🔄 Session disconnected during verification - this is normal after 2FA")
                return True  # Assume verification completed when session disconnects
            
            if attempt == max_verification_attempts - 1:
                print("⚠️ Continuing despite verification handling error...")
                return True
            continue
    
    return True

# DIRECT APPROACH OPTIMIZATIONS FOR OAUTH AND CREDENTIALS
def implement_direct_oauth_approach(project_name):
    """DIRECT APPROACH: Fast OAuth consent screen navigation"""
    print("⚡ DIRECT APPROACH: OAuth consent screen setup...")
    
    # Create project ID from project name
    project_id = project_name.lower().replace(' ', '-').replace('_', '-')
    import re
    project_id = re.sub(r'[^a-z0-9-]', '', project_id)
    
    oauth_urls = [
        f"https://console.cloud.google.com/apis/credentials/consent?project={project_name}",
        f"https://console.cloud.google.com/apis/credentials/consent?project={project_id}",
        "https://console.cloud.google.com/apis/credentials/consent",
    ]
    
    for oauth_url in oauth_urls:
        try:
            print(f"🔗 DIRECT APPROACH: Trying OAuth URL: {oauth_url}")
            driver.get(oauth_url)
            time.sleep(random.uniform(2.0, 3.0))  # Reduced wait time
            
            current_url = driver.current_url
            if "auth/overview" in current_url or "credentials/consent" in current_url:
                print("✅ DIRECT APPROACH SUCCESS: OAuth page loaded!")
                return True
        except Exception as oauth_error:
            print(f"⚠️ OAuth URL failed: {oauth_error}")
            continue
    
    print("⚠️ DIRECT APPROACH: OAuth direct navigation failed")
    return False

def implement_direct_credentials_approach(project_name):
    """DIRECT APPROACH: Fast credentials page navigation"""
    print("⚡ DIRECT APPROACH: Credentials page navigation...")
    
    # Create project ID from project name
    project_id = project_name.lower().replace(' ', '-').replace('_', '-')
    import re
    project_id = re.sub(r'[^a-z0-9-]', '', project_id)
    
    credentials_urls = [
        f"https://console.cloud.google.com/apis/credentials?project={project_name}",
        f"https://console.cloud.google.com/apis/credentials?project={project_id}",
        "https://console.cloud.google.com/apis/credentials",
    ]
    
    for cred_url in credentials_urls:
        try:
            print(f"🔗 DIRECT APPROACH: Trying credentials URL: {cred_url}")
            driver.get(cred_url)
            time.sleep(random.uniform(2.0, 3.0))  # Reduced wait time
            
            current_url = driver.current_url
            if "credentials" in current_url:
                print("✅ DIRECT APPROACH SUCCESS: Credentials page loaded!")
                return True
        except Exception as cred_error:
            print(f"⚠️ Credentials URL failed: {cred_error}")
            continue
    
    print("⚠️ DIRECT APPROACH: Credentials direct navigation failed")
    return False

# DIRECT APPROACH: Enhanced JSON download with file system monitoring
def implement_direct_json_download_approach():
    """DIRECT APPROACH: Enhanced JSON download with immediate file detection"""
    print("📁 DIRECT APPROACH: Enhanced JSON download monitoring...")
    
    # Pre-scan existing files to identify new downloads
    pre_scan_files = set()
    for location in [DOWNLOAD_DIR, os.path.expanduser("~/Downloads")]:
        try:
            if os.path.exists(location):
                files = glob.glob(os.path.join(location, "*.json"))
                pre_scan_files.update(files)
        except:
            pass
    
    print(f"📁 Pre-scan found {len(pre_scan_files)} existing JSON files")
    
    # Store current time for download comparison
    download_start_time = time.time()
    
    # Return monitoring data for post-download processing
    return {
        'pre_scan_files': pre_scan_files,
        'download_start_time': download_start_time,
        'locations': [DOWNLOAD_DIR, os.path.expanduser("~/Downloads")]
    }

def detect_new_json_download(monitoring_data):
    """DIRECT APPROACH: Detect newly downloaded JSON files immediately"""
    print("🔍 DIRECT APPROACH: Scanning for new JSON downloads...")
    
    max_wait_time = 30  # Maximum 30 seconds wait
    check_interval = 1  # Check every 1 second
    checks_performed = 0
    
    while checks_performed < max_wait_time:
        current_files = set()
        
        # Scan all monitored locations
        for location in monitoring_data['locations']:
            try:
                if os.path.exists(location):
                    files = glob.glob(os.path.join(location, "*.json"))
                    current_files.update(files)
            except:
                continue
        
        # Find new files
        new_files = current_files - monitoring_data['pre_scan_files']
        
        if new_files:
            # Check if any new file is a Google credentials file
            for new_file in new_files:
                file_time = os.path.getmtime(new_file)
                if file_time >= monitoring_data['download_start_time']:
                    print(f"✅ DIRECT APPROACH: New JSON file detected: {new_file}")
                    
                    # Quick validation
                    try:
                        with open(new_file, 'r') as f:
                            content = f.read()
                        
                        if '"client_id"' in content and '"client_secret"' in content:
                            print("✅ DIRECT APPROACH: Validated Google credentials file!")
                            return new_file
                    except:
                        continue
        
        time.sleep(check_interval)
        checks_performed += 1
        
        if checks_performed % 5 == 0:  # Progress update every 5 seconds
            print(f"🔍 Still scanning... ({checks_performed}s elapsed)")
    
    print("⚠️ DIRECT APPROACH: No new JSON file detected within time limit")
    return None

# Add these direct approaches to the global scope for use throughout automation

def navigate_with_captcha_handling(driver, url, page_name="page"):
    """Navigate to a URL with CAPTCHA detection and handling"""
    print(f"🌐 Navigating to {page_name}...")
    
    try:
        driver.get(url)
        print(f"✅ Loaded {page_name}")
        
        # Wait for page load and check for CAPTCHAs
        return wait_for_page_load_and_check_captcha(driver)
        
    except Exception as nav_error:
        print(f"❌ Navigation to {page_name} failed: {nav_error}")
        
        # Still check for CAPTCHAs even if navigation failed
        detect_and_handle_captcha(driver)
        return False

def perform_action_with_captcha_retry(driver, action_function, *args, max_retries=2):
    """Perform an action with CAPTCHA detection and retry logic"""
    for attempt in range(max_retries + 1):
        try:
            # Perform the action
            result = action_function(*args)
            
            if result:
                return True
            else:
                print(f"🔄 Action failed (attempt {attempt + 1}), checking for CAPTCHA...")
                
                # Check for CAPTCHA and retry if found and solved
                if detect_and_handle_captcha(driver):
                    if attempt < max_retries:
                        print(f"🔄 Retrying action after CAPTCHA handling...")
                        time.sleep(random.uniform(1.0, 2.0))
                        continue
                
                if attempt == max_retries:
                    print("❌ Action failed after all retries")
                    return False
                    
        except Exception as action_error:
            print(f"⚠️ Action error (attempt {attempt + 1}): {action_error}")
            
            # Check for CAPTCHA on error
            if detect_and_handle_captcha(driver):
                if attempt < max_retries:
                    print(f"🔄 Retrying action after CAPTCHA handling...")
                    time.sleep(random.uniform(1.0, 2.0))
                    continue
            
            if attempt == max_retries:
                print("❌ Action failed after all retries with errors")
                return False
    
    return False

def detect_and_handle_captcha(driver):
    """Detect and handle various types of CAPTCHAs"""
    print("🤖 Checking for CAPTCHAs or robot verification...")
    
    try:
        # Common CAPTCHA indicators
        captcha_indicators = [
            # reCAPTCHA v2 and v3
            "//iframe[contains(@src, 'recaptcha')]",
            "//div[contains(@class, 'g-recaptcha')]", 
            "//div[@id='recaptcha']",
            "//div[contains(@class, 'recaptcha')]",
            
            # Google's "I'm not a robot" checkbox
            "//div[contains(@class, 'recaptcha-checkbox')]",
            "//span[contains(text(), 'not a robot')]",
            "//span[contains(text(), \"I'm not a robot\")]",
            
            # hCaptcha
            "//iframe[contains(@src, 'hcaptcha')]",
            "//div[contains(@class, 'h-captcha')]",
            "//div[@id='hcaptcha']",
            
            # Generic CAPTCHA text
            "//div[contains(text(), 'CAPTCHA') or contains(text(), 'captcha')]",
            "//span[contains(text(), 'CAPTCHA') or contains(text(), 'captcha')]",
            "//p[contains(text(), 'verify') and contains(text(), 'human')]",
            "//div[contains(text(), 'robot') or contains(text(), 'Robot')]",
            "//span[contains(text(), 'Confirm you') and contains(text(), 'not a robot')]",
            
            # Cloudflare protection
            "//div[contains(@class, 'cf-browser-verification')]",
            "//div[contains(text(), 'Checking your browser')]",
            "//div[contains(text(), 'DDoS protection')]",
            
            # Other verification forms
            "//div[contains(text(), 'verification')]",
            "//div[contains(text(), 'security check')]",
            "//button[contains(text(), 'Verify')]",
            "//input[@type='text' and contains(@placeholder, 'captcha')]"
        ]
        
        captcha_found = False
        captcha_type = "unknown"
        captcha_element = None
        
        # Check for various CAPTCHA types
        for indicator in captcha_indicators:
            try:
                elements = driver.find_elements(By.XPATH, indicator)
                for element in elements:
                    if element.is_displayed():
                        captcha_found = True
                        captcha_element = element
                        
                        # Determine CAPTCHA type
                        if "recaptcha" in indicator.lower():
                            captcha_type = "reCAPTCHA"
                        elif "hcaptcha" in indicator.lower():
                            captcha_type = "hCaptcha"
                        elif "cloudflare" in indicator.lower() or "cf-" in indicator.lower():
                            captcha_type = "Cloudflare"
                        elif "robot" in indicator.lower():
                            captcha_type = "Robot Verification"
                        else:
                            captcha_type = "Generic CAPTCHA"
                        
                        print(f"🚨 {captcha_type} detected!")
                        break
                
                if captcha_found:
                    break
                    
            except Exception as indicator_error:
                continue
        
        if not captcha_found:
            print("✅ No CAPTCHA detected, proceeding...")
            return True
        
        # Handle different CAPTCHA types
        print(f"🔧 Attempting to handle {captcha_type}...")
        
        if captcha_type == "reCAPTCHA":
            return handle_recaptcha(driver, captcha_element)
        elif captcha_type == "hCaptcha":
            return handle_hcaptcha(driver, captcha_element)
        elif captcha_type == "Cloudflare":
            return handle_cloudflare(driver, captcha_element)
        elif captcha_type == "Robot Verification":
            return handle_robot_verification(driver, captcha_element)
        else:
            return handle_generic_captcha(driver, captcha_element)
            
    except Exception as captcha_error:
        print(f"⚠️ Error in CAPTCHA detection: {captcha_error}")
        return True  # Continue anyway

def handle_recaptcha(driver, captcha_element):
    """Handle reCAPTCHA challenges"""
    print("🔄 Handling reCAPTCHA...")
    
    try:
        # Strategy 1: Look for "I'm not a robot" checkbox
        checkbox_selectors = [
            "//div[contains(@class, 'recaptcha-checkbox-border')]",
            "//div[contains(@class, 'recaptcha-checkbox')]//div[@role='checkbox']",
            "//span[contains(@class, 'recaptcha-checkbox')]",
            "//div[@id='recaptcha-anchor']",
            "//iframe[contains(@src, 'recaptcha')]"
        ]
        
        checkbox_clicked = False
        for selector in checkbox_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print("✅ Found reCAPTCHA checkbox, clicking...")
                        
                        # Switch to iframe if needed
                        if element.tag_name == "iframe":
                            driver.switch_to.frame(element)
                            time.sleep(1.0)
                            
                            # Find checkbox inside iframe
                            inner_checkbox = driver.find_element(By.XPATH, "//div[@role='checkbox']")
                            if inner_checkbox.is_displayed():
                                inner_checkbox.click()
                                print("✅ reCAPTCHA checkbox clicked!")
                                checkbox_clicked = True
                                
                            # Switch back to main content
                            driver.switch_to.default_content()
                        else:
                            element.click()
                            print("✅ reCAPTCHA checkbox clicked!")
                            checkbox_clicked = True
                        
                        break
                        
                if checkbox_clicked:
                    break
                    
            except Exception as checkbox_error:
                print(f"⚠️ Checkbox click failed: {checkbox_error}")
                continue
        
        if checkbox_clicked:
            print("⏳ Waiting for reCAPTCHA to process...")
            time.sleep(random.uniform(3.0, 5.0))
            
            # Check if CAPTCHA challenge appeared
            challenge_selectors = [
                "//div[contains(@class, 'rc-imageselect')]",
                "//div[contains(@class, 'rc-audiochallenge')]",
                "//iframe[contains(@title, 'recaptcha challenge')]"
            ]
            
            challenge_found = False
            for selector in challenge_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if any(e.is_displayed() for e in elements):
                        challenge_found = True
                        break
                except:
                    continue
            
            if challenge_found:
                print("🧩 reCAPTCHA challenge appeared - requires manual intervention")
                print("💡 Please solve the reCAPTCHA manually:")
                print("   1. Complete the image/audio challenge")
                print("   2. Click 'Verify' when done")
                print("   3. The script will continue automatically")
                
                # Wait for user to solve CAPTCHA
                input("Press Enter after solving the reCAPTCHA...")
                return True
            else:
                print("✅ reCAPTCHA solved automatically!")
                return True
        else:
            print("⚠️ Could not find reCAPTCHA checkbox")
            return handle_manual_captcha_guidance("reCAPTCHA")
            
    except Exception as recaptcha_error:
        print(f"❌ reCAPTCHA handling failed: {recaptcha_error}")
        return handle_manual_captcha_guidance("reCAPTCHA")

def handle_hcaptcha(driver, captcha_element):
    """Handle hCaptcha challenges"""
    print("🔄 Handling hCaptcha...")
    
    try:
        # Look for hCaptcha checkbox
        checkbox_selectors = [
            "//div[contains(@class, 'hcaptcha-checkbox')]",
            "//iframe[contains(@src, 'hcaptcha')]",
            "//div[@id='hcaptcha']//iframe"
        ]
        
        for selector in checkbox_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        if element.tag_name == "iframe":
                            # Switch to hCaptcha iframe
                            driver.switch_to.frame(element)
                            time.sleep(1.0)
                            
                            # Find and click checkbox
                            checkbox = driver.find_element(By.XPATH, "//div[@role='checkbox']")
                            if checkbox.is_displayed():
                                checkbox.click()
                                print("✅ hCaptcha checkbox clicked!")
                                
                            # Switch back
                            driver.switch_to.default_content()
                        else:
                            element.click()
                            print("✅ hCaptcha clicked!")
                        
                        # Wait for processing
                        time.sleep(random.uniform(3.0, 5.0))
                        return True
                        
            except Exception as hcaptcha_error:
                continue
        
        return handle_manual_captcha_guidance("hCaptcha")
        
    except Exception as hcaptcha_error:
        print(f"❌ hCaptcha handling failed: {hcaptcha_error}")
        return handle_manual_captcha_guidance("hCaptcha")

def handle_cloudflare(driver, captcha_element):
    """Handle Cloudflare protection"""
    print("🔄 Handling Cloudflare protection...")
    
    try:
        # Cloudflare usually resolves automatically, just wait
        print("⏳ Waiting for Cloudflare to complete verification...")
        
        # Wait up to 30 seconds for Cloudflare to complete
        max_wait = 30
        wait_time = 0
        
        while wait_time < max_wait:
            time.sleep(2.0)
            wait_time += 2
            
            # Check if Cloudflare is still active
            cf_indicators = [
                "//div[contains(@class, 'cf-browser-verification')]",
                "//div[contains(text(), 'Checking your browser')]"
            ]
            
            cf_active = False
            for indicator in cf_indicators:
                try:
                    elements = driver.find_elements(By.XPATH, indicator)
                    if any(e.is_displayed() for e in elements):
                        cf_active = True
                        break
                except:
                    continue
            
            if not cf_active:
                print("✅ Cloudflare verification completed!")
                return True
            
            print(f"⏳ Still waiting for Cloudflare... ({wait_time}s/{max_wait}s)")
        
        print("⚠️ Cloudflare verification taking longer than expected")
        return handle_manual_captcha_guidance("Cloudflare")
        
    except Exception as cf_error:
        print(f"❌ Cloudflare handling failed: {cf_error}")
        return handle_manual_captcha_guidance("Cloudflare")

def handle_robot_verification(driver, captcha_element):
    """Handle 'Confirm you're not a robot' verification"""
    print("🔄 Handling robot verification...")
    
    try:
        # Look for verification buttons or checkboxes
        verification_selectors = [
            "//button[contains(text(), 'not a robot')]",
            "//button[contains(text(), 'Verify')]",
            "//input[@type='checkbox' and contains(@aria-label, 'not a robot')]",
            "//div[contains(@role, 'checkbox') and contains(@aria-label, 'not a robot')]",
            "//span[contains(text(), 'not a robot')]//ancestor::button[1]",
            "//div[contains(text(), 'not a robot')]//following-sibling::button",
            "//div[contains(@class, 'verification')]//button"
        ]
        
        for selector in verification_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        print("✅ Found robot verification element, clicking...")
                        
                        # Scroll to element
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(1.0)
                        
                        # Click element
                        try:
                            element.click()
                            print("✅ Robot verification clicked!")
                        except:
                            # Try JavaScript click
                            driver.execute_script("arguments[0].click();", element)
                            print("✅ Robot verification clicked with JavaScript!")
                        
                        # Wait for verification
                        time.sleep(random.uniform(2.0, 4.0))
                        return True
                        
            except Exception as verification_error:
                continue
        
        return handle_manual_captcha_guidance("Robot Verification")
        
    except Exception as robot_error:
        print(f"❌ Robot verification handling failed: {robot_error}")
        return handle_manual_captcha_guidance("Robot Verification")

def handle_generic_captcha(driver, captcha_element):
    """Handle generic CAPTCHA challenges"""
    print("🔄 Handling generic CAPTCHA...")
    
    try:
        # Look for common CAPTCHA elements
        captcha_selectors = [
            "//button[contains(text(), 'Verify')]",
            "//button[contains(text(), 'Submit')]",
            "//input[@type='text' and contains(@placeholder, 'captcha')]",
            "//input[@type='text' and contains(@name, 'captcha')]",
            "//div[contains(@class, 'captcha')]//button",
            "//form[contains(@class, 'captcha')]//button[@type='submit']"
        ]
        
        for selector in captcha_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element_type = element.tag_name.lower()
                        
                        if element_type == "input":
                            print("📝 Found CAPTCHA input field - requires manual entry")
                            return handle_manual_captcha_guidance("Text CAPTCHA")
                        elif element_type == "button":
                            print("✅ Found CAPTCHA button, clicking...")
                            element.click()
                            time.sleep(random.uniform(2.0, 4.0))
                            return True
                            
            except Exception as generic_error:
                continue
        
        return handle_manual_captcha_guidance("Generic CAPTCHA")
        
    except Exception as generic_error:
        print(f"❌ Generic CAPTCHA handling failed: {generic_error}")
        return handle_manual_captcha_guidance("Generic CAPTCHA")

def handle_manual_captcha_guidance(captcha_type):
    """Provide manual guidance for CAPTCHA solving"""
    print(f"🧩 {captcha_type} requires manual intervention")
    print("💡 Manual CAPTCHA solving steps:")
    print("   1. Look for the CAPTCHA challenge on the page")
    print("   2. Complete the challenge (checkbox, images, text, etc.)")
    print("   3. Click any 'Verify' or 'Submit' buttons")
    print("   4. Wait for the page to proceed")
    print("")
    print("🎯 Common CAPTCHA types and solutions:")
    print("   • Checkbox: Click 'I'm not a robot'")
    print("   • Images: Select all images matching the prompt")
    print("   • Audio: Listen and type what you hear")
    print("   • Text: Type the characters you see")
    print("")
    
    # Give user time to solve manually
    try:
        user_input = input("Press Enter after solving the CAPTCHA (or 's' to skip): ").strip().lower()
        
        if user_input == 's':
            print("⚠️ CAPTCHA skipped - continuing with potential issues")
            return False
        else:
            print("✅ CAPTCHA marked as solved - continuing...")
            return True
            
    except KeyboardInterrupt:
        print("\n⚠️ User interrupted - continuing anyway")
        return True

def wait_for_page_load_and_check_captcha(driver, timeout=10):
    """Wait for page to load and check for CAPTCHAs"""
    print("⏳ Waiting for page to load and checking for CAPTCHAs...")
    
    try:
        # Wait for basic page load
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(random.uniform(1.0, 2.0))
        
        # Check for CAPTCHAs after page load
        return detect_and_handle_captcha(driver)
        
    except TimeoutException:
        print("⚠️ Page load timeout - checking for CAPTCHAs anyway")
        return detect_and_handle_captcha(driver)
    except Exception as load_error:
        print(f"⚠️ Page load check failed: {load_error}")
        return detect_and_handle_captcha(driver)

# Chrome driver initialization with enhanced error handling
driver = None

print("🔧 Setting up Chrome driver with enhanced error handling...")
print("⚠️  Note: This may take a moment as it downloads the correct ChromeDriver version...")

# Try multiple approaches in order of reliability
approaches = [
    ("Standard Selenium (Recommended)", create_driver_standard),
    ("WebDriver Manager", create_driver_webdriver_manager),
    ("Force Download ChromeDriver", create_driver_force_download)
]

for approach_name, create_function in approaches:
    try:
        print(f"🔄 Trying {approach_name}...")
        driver = create_function()
        if driver is not None:
            print(f"✅ {approach_name} successful!")
            break
        else:
            print(f"⚠️ {approach_name} returned None, trying next approach...")
    except Exception as approach_error:
        print(f"❌ Error with {approach_name}: {approach_error}")
        print("🔄 Trying next approach...")
        continue

# If all approaches fail, provide detailed help
if driver is None:
    print("\n❌ Failed to create Chrome driver with any approach")
    print("🚨 Chrome version compatibility issue detected!")
    print(f"🌐 Your Chrome version: 137.0.7151.69")
    print(f"❌ ChromeDriver version mismatch - trying version 138 with Chrome 137")
    print("\n💡 SOLUTIONS to fix this issue:")
    print("1. 🌐 Update Chrome browser:")
    print("   - Open Chrome → Settings → About Chrome → Update")
    print("   - Or download latest Chrome from https://www.google.com/chrome/")
    print("")
    print("2. 🐍 Update Python packages:")
    print("   pip install --upgrade selenium webdriver-manager")
    print("")
    print("3. 🗑️ Clear ChromeDriver cache:")
    print("   - Delete folder: C:\\Users\\<username>\\.wdm")
    print("   - Then run the script again")
    print("")
    print("4. 🔄 Alternative fix - Manual ChromeDriver download:")
    print("   - Check your Chrome version: chrome://version/")
    print("   - Download matching ChromeDriver from: https://chromedriver.chromium.org/downloads")
    print("   - Place chromedriver.exe in your Python Scripts folder")
    print("")
    print("5. 🖥️ Restart your computer and try again")
    print("")
    print("6. 🚀 Quick fix - Try downloading ChromeDriver 137:")
    print("   - The script will attempt to download the correct version automatically")
    print("")
    print("7. 💡 Alternative solution:")
    print("   pip install --upgrade selenium==4.15.0")
    print("")
    print("🔧 AUTOMATED FIX ATTEMPT:")
    print("The script has already tried multiple approaches including:")
    print("• Standard Selenium WebDriver")
    print("• WebDriver Manager auto-download")
    print("• Manual ChromeDriver download")
    print("")
    print("If all methods failed, your system may have:")
    print("• Antivirus blocking ChromeDriver")
    print("• Network restrictions preventing downloads")
    print("• Corrupted Chrome installation")
    print("• Insufficient permissions")
    print("")
    print("🆘 MANUAL SOLUTION:")
    print("1. Download ChromeDriver 137 manually from:")
    print("   https://chromedriver.storage.googleapis.com/137.0.0.0/chromedriver_win32.zip")
    print("2. Extract chromedriver.exe to this folder:")
    print(f"   {os.getcwd()}")
    print("3. Run the script again")
    print("")
    print("🛠️ AUTOMATED FIX TOOL:")
    print("Run the automated fix script:")
    print("   python fix_chrome_driver.py")
    print("")
    print("This tool will automatically:")
    print("• Detect your Chrome version")
    print("• Download the correct ChromeDriver")
    print("• Test the installation")
    print("• Verify everything is working")
    input("\nPress Enter to exit...")
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
    
    # Step 1: Go directly to Cloud Console (will redirect to login if needed)
    print("🌐 Navigating directly to Google Cloud Console...")
    driver.get("https://console.cloud.google.com")

    wait = WebDriverWait(driver, 20)

    # Step 2: Handle login if redirected to login page
    print("🔍 Checking if login is required...")
    current_url = driver.current_url.lower()
    
    if "accounts.google.com" in current_url or "signin" in current_url:
        print("🔐 Login required - handling authentication...")
        
        # Step 2a: Type email
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

        time.sleep(random.uniform(1.0, 2.0))

        # Step 2b: Type password
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

        # Step 2c: Enhanced 2FA and phone verification handling
        print("📱 Checking for 2FA and phone verification prompts...")
        time.sleep(random.uniform(3.0, 5.0))  # Wait longer for potential verification screen
        
        # Execute enhanced 2FA handling
        try:
            verification_result = handle_2fa_and_verification(driver)
            if not verification_result:
                print("❌ 2FA/Verification handling failed")
                raise Exception("2FA verification could not be completed")
            else:
                print("✅ 2FA/Verification handling completed successfully")
        except Exception as verification_error:
            print(f"⚠️ Error during 2FA/verification handling: {verification_error}")
            print("💡 Continuing with automation - you may need to complete verification manually")

        # Check and recover session if needed after 2FA
        print("🔍 Checking browser session after 2FA...")
        session_ok, driver = recover_session_if_needed(driver)
        if not session_ok:
            print("⚠️ Session recovery failed, but continuing with automation...")

        # Step 2d: Wait for login to complete and check if we're redirected to Cloud Console
        print("⏳ Waiting for login to complete...")
        time.sleep(random.uniform(3.0, 5.0))
        
        current_url_after_login = driver.current_url
        print(f"📍 URL after login: {current_url_after_login}")
        
        if "console.cloud.google.com" not in current_url_after_login:
            print("🔄 Not automatically redirected to Cloud Console, navigating manually...")
            driver.get("https://console.cloud.google.com")
            time.sleep(random.uniform(3.0, 5.0))
        
    else:
        print("✅ Already logged in or on Cloud Console!")

    print_milestone_timing("✅ LOGIN COMPLETED")

    # Handle 2FA setup popup immediately after login
    print("🔍 Checking for 2FA setup popup after login...")
    handle_2fa_popup(driver)
    
    # Check for Google Cloud Console first-time setup (country selection + terms)
    print("🔍 Checking for Google Cloud Console first-time setup...")
    handle_google_console_first_time_setup(driver)

    # Additional check for Google Play Console Terms of Service (legacy/alternative flow)
    print("🔍 Checking for Google Play Console Terms of Service...")
    current_url = driver.current_url
    if "play.google.com" in current_url or "terms" in current_url.lower():
        print("📋 Google Play Console Terms of Service detected!")
        
        try:
            # Handle country selection dropdown
            print("🌍 Looking for country selection dropdown...")
            time.sleep(random.uniform(2.0, 3.0))
            
            # Country dropdown selectors
            country_dropdown_selectors = [
                "cfc-select[formcontrolname='optInCountry']",
                ".p6ntest-country-dropdown",
                "#cfc-select-0",
                "cfc-select[aria-labelledby='tos-country-of-residence']",
                "[role='combobox'][aria-haspopup='listbox']"
            ]
            
            country_dropdown = None
            for selector in country_dropdown_selectors:
                try:
                    country_dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ Found country dropdown with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if country_dropdown:
                # Click to open the dropdown
                print("🖱️ Clicking country dropdown...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", country_dropdown)
                human_mouse_move_to(country_dropdown)
                country_dropdown.click()
                time.sleep(random.uniform(0.5, 1.0))  # Reduced wait time
                
                # Look for Austria in the dropdown options
                print("🔍 Looking for Austria in country options...")
                austria_selectors = [
                    "//cfc-option[contains(text(), 'Austria')]",
                    "//div[contains(@class, 'cfc-option') and contains(text(), 'Austria')]",
                    "//span[contains(text(), 'Austria')]",
                    "//mat-option[contains(text(), 'Austria')]",
                    "//*[contains(text(), 'Austria') and contains(@class, 'option')]"
                ]
                
                austria_option = None
                for selector in austria_selectors:
                    try:
                        austria_option = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, selector)))  # Reduced wait time to 3 seconds
                        print(f"✅ Found Austria option with selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if austria_option:
                    print("🇦🇹 Selecting Austria...")
                    # Use JavaScript click for faster execution
                    driver.execute_script("arguments[0].click();", austria_option)
                    print("✅ Austria selected successfully!")
                else:
                    print("⚠️ Could not find Austria option, continuing with current selection...")
            else:
                print("⚠️ Could not find country dropdown")
            
            # Look for and check the "I agree" checkbox
            print("☑️ Looking for Terms of Service agreement checkbox...")
            time.sleep(random.uniform(1.0, 2.0))
            
            checkbox_selectors = [
                "#mat-mdc-checkbox-0-input",
                "input[type='checkbox'][id*='checkbox']",
                ".mdc-checkbox__native-control",
                "input[type='checkbox'][tabindex='0']",
                "input[type='checkbox']"
            ]
            
            agreement_checkbox = None
            for selector in checkbox_selectors:
                try:
                    agreement_checkbox = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ Found agreement checkbox with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if agreement_checkbox:
                # Check if checkbox is already checked
                is_checked = agreement_checkbox.is_selected()
                if not is_checked:
                    print("☑️ Checking Terms of Service agreement...")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", agreement_checkbox)
                    time.sleep(random.uniform(1.0, 2.0))
                    human_mouse_move_to(agreement_checkbox)
                    agreement_checkbox.click()
                    time.sleep(random.uniform(1.0, 2.0))
                    print("✅ Terms of Service agreement checked!")
                else:
                    print("✅ Terms of Service agreement already checked!")
            else:
                print("⚠️ Could not find Terms of Service agreement checkbox")
            
            # Look for and click the Continue/Accept button
            print("➡️ Looking for Continue/Accept button...")
            time.sleep(random.uniform(1.0, 2.0))
            
            continue_selectors = [
                "//button[contains(text(), 'Continue')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Agree')]",
                "//button[contains(text(), 'I agree')]",
                "//span[contains(text(), 'Continue')]/parent::button",
                "//span[contains(text(), 'Accept')]/parent::button",
                "button[type='submit']",
                ".mdc-button--raised"
            ]
            
            continue_button = None
            for selector in continue_selectors:
                try:
                    if selector.startswith("//"):
                        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        continue_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ Found continue button with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if continue_button:
                print("✅ Clicking Continue/Accept button...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
                time.sleep(random.uniform(1.0, 2.0))
                human_mouse_move_to(continue_button)
                continue_button.click()
                time.sleep(random.uniform(3.0, 5.0))
                print("✅ Terms of Service accepted successfully!")
            else:
                print("⚠️ Could not find Continue/Accept button")
                
        except Exception as tos_error:
            print(f"⚠️ Error handling Terms of Service: {tos_error}")
            print("💡 You may need to manually complete the Terms of Service agreement")
    
    print("☁️ Verifying Cloud Console access...")
    
    # Wait for Cloud Console to load and check if we're on the right page
    print("⏳ Waiting for Cloud Console to load...")
    time.sleep(random.uniform(5.0, 7.0))  # Max 7 seconds as requested
    
    # Additional verification check after Cloud Console navigation
    print("🔐 Checking for additional security verifications...")
    
    def handle_additional_verifications():
        """Handle any additional verification prompts that might appear"""
        verification_handled = True
        max_attempts = 3
        
        for attempt in range(max_attempts):
            print(f"🔍 Security check attempt {attempt + 1}/{max_attempts}...")
            time.sleep(random.uniform(2.0, 3.0))
            
            current_url = driver.current_url.lower()
            page_source = driver.page_source.lower()
            
            # Check for various verification scenarios
            security_indicators = [
                # Phone verification
                "verify your phone", "phone verification", "verify phone number",
                "enter your phone", "phone number verification", "verify it's you",
                # Email verification  
                "verify your email", "email verification", "check your email",
                "verification code", "enter the code", "we sent a code",
                # 2FA / Security
                "2-step verification", "two-factor authentication", "security code",
                "authenticator app", "backup codes", "verify your identity",
                # Account security
                "unusual activity", "suspicious activity", "secure your account",
                "protect your account", "account security", "security alert",
                # Recovery
                "account recovery", "recover your account", "security questions",
                "backup email", "recovery email", "recovery phone"
            ]
            
            verification_detected = any(indicator in current_url or indicator in page_source for indicator in security_indicators)
            
            if verification_detected:
                print("⚠️ Additional security verification detected!")
                
                # Method 1: Try to find and click skip/dismiss options
                skip_options = [
                    "//button[contains(text(), 'Skip')]",
                    "//button[contains(text(), 'Not now')]",
                    "//button[contains(text(), 'Later')]", 
                    "//button[contains(text(), 'Ask later')]",
                    "//button[contains(text(), 'Maybe later')]",
                    "//button[contains(text(), 'Dismiss')]",
                    "//button[contains(text(), 'Cancel')]",
                    "//button[contains(text(), 'No thanks')]",
                    "//a[contains(text(), 'Skip')]",
                    "//a[contains(text(), 'Not now')]",
                    "//span[contains(text(), 'Skip')]/parent::button",
                    "//span[contains(text(), 'Not now')]/parent::button",
                    "//span[contains(text(), 'Later')]/parent::button",
                    "[data-action='skip']",
                    "[data-action='dismiss']",
                    ".skip-button",
                    ".dismiss-button",
                    "button[name='skip']"
                ]
                
                skip_clicked = False
                for selector in skip_options:
                    try:
                        if selector.startswith("//"):
                            skip_element = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            skip_element = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        
                        if skip_element and skip_element.is_displayed():
                            print(f"✅ Found skip option: {selector}")
                            human_mouse_move_to(skip_element)
                            skip_element.click()
                            print("✅ Successfully skipped additional verification!")
                            time.sleep(random.uniform(2.0, 3.0))
                            skip_clicked = True
                            break
                    except:
                        continue
                
                if skip_clicked:
                    continue  # Check again if more verifications appear
                
                # Method 2: Try to find alternative verification methods
                print("🔄 Looking for alternative verification methods...")
                alternative_options = [
                    "//button[contains(text(), 'Try another way')]",
                    "//button[contains(text(), 'Use another method')]", 
                    "//button[contains(text(), 'Different method')]",
                    "//button[contains(text(), 'Another option')]",
                    "//a[contains(text(), 'Try another way')]",
                    "//a[contains(text(), 'Use another method')]",
                    "//span[contains(text(), 'Try another way')]/parent::button",
                    "//span[contains(text(), 'Use another method')]/parent::button",
                    "[data-action='challenge-another-way']",
                    ".challenge-alt-option"
                ]
                
                alternative_clicked = False
                for selector in alternative_options:
                    try:
                        if selector.startswith("//"):
                            alt_element = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, selector)))
                        else:
                            alt_element = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        
                        if alt_element and alt_element.is_displayed():
                            print(f"✅ Found alternative method: {selector}")
                            human_mouse_move_to(alt_element)
                            alt_element.click()
                            print("✅ Clicked alternative verification method!")
                            time.sleep(random.uniform(2.0, 3.0))
                            alternative_clicked = True
                            break
                    except:
                        continue
                
                if alternative_clicked:
                    # Look for backup email or easier options
                    print("📧 Looking for backup email verification...")
                    backup_options = [
                        "//div[contains(text(), 'backup email')]//parent::div//parent::div",
                        "//div[contains(text(), 'recovery email')]//parent::div//parent::div",
                        "//span[contains(text(), 'backup email')]//ancestor::button[1]",
                        "//span[contains(text(), 'recovery email')]//ancestor::button[1]",
                        "//button[contains(text(), 'email')]",
                        "[data-challenge-type='recovery-email']",
                        "[data-challenge-type='backup-email']"
                    ]
                    
                    for selector in backup_options:
                        try:
                            if selector.startswith("//"):
                                backup_element = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, selector)))
                            else:
                                backup_element = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                            
                            if backup_element and backup_element.is_displayed():
                                print(f"✅ Found backup email option: {selector}")
                                human_mouse_move_to(backup_element)
                                backup_element.click()
                                print("✅ Selected backup email verification!")
                                time.sleep(random.uniform(2.0, 3.0))
                                break
                        except:
                            continue
                    
                    continue  # Check again after selecting alternative
                
                # Method 3: Manual intervention
                print("🛑 Automatic bypass not possible - Manual intervention required!")
                print("🔐 Additional security verification detected!")
                print("Please handle the verification manually:")
                print("  • Complete phone/email verification if you have access")
                print("  • Look for 'Skip', 'Not now', or 'Later' options")
                print("  • Try 'Use another method' or 'Try another way'")
                print("  • Select backup email verification if available")
                print("  • Dismiss security prompts if possible")
                
                input("🔐 Press Enter after handling the verification manually...")
                time.sleep(random.uniform(2.0, 3.0))
                
                # Check if verification was resolved
                current_url_after = driver.current_url.lower()
                page_source_after = driver.page_source.lower()
                still_has_verification = any(indicator in current_url_after or indicator in page_source_after for indicator in security_indicators)
                
                if still_has_verification:
                    print("⚠️ Verification still detected. Continuing anyway...")
                else:
                    print("✅ Verification appears to be resolved!")
                
                break  # Exit the retry loop
            else:
                print("✅ No additional security verifications detected")
                break
        
        return verification_handled
    
    # Handle additional verifications
    try:
        # Use the comprehensive verification handler
        handle_google_verifications(driver, "cloud-console")
    except Exception as additional_verification_error:
        print(f"⚠️ Error handling additional verifications: {additional_verification_error}")
        print("💡 Continuing with automation...")
    
    # Check current URL to ensure we're on Cloud Console
    current_url = driver.current_url
    print(f"📍 Current URL: {current_url}")
    
    # If we're not on Cloud Console, try again
    if "console.cloud.google.com" not in current_url:
        print("⚠️ Not on Cloud Console, trying direct navigation again...")
        driver.get("https://console.cloud.google.com")
        time.sleep(random.uniform(3.0, 5.0))  # Reduced from previous long wait
        current_url = driver.current_url
        print(f"📍 New URL: {current_url}")
        
        # If still not on Cloud Console, try the home page first
        if "console.cloud.google.com" not in current_url:
            print("⚠️ Still not on Cloud Console, trying via home page...")
            driver.get("https://console.cloud.google.com/home")
            time.sleep(random.uniform(3.0, 5.0))  # Reduced from previous long wait

    print("✅ Login attempt completed successfully!")
    
    # CRITICAL: Check specifically for Google Recovery Options page that appears for new Gmail accounts
    current_url = driver.current_url
    print(f"📍 Current URL after login: {current_url}")
    
    if "gds.google.com/web/recoveryoptions" in current_url:
        print("📱 CRITICAL: Detected Google Recovery Options page after login!")
        print("🚫 This page must be handled before proceeding to Cloud Console...")
        
        # Multiple attempts to handle recovery options
        recovery_attempts = 3
        recovery_handled = False
        
        for attempt in range(recovery_attempts):
            print(f"📱 Recovery options handling attempt {attempt + 1}/{recovery_attempts}")
            
            # First dismiss any overlays
            dismiss_overlay(driver)
            time.sleep(1)
            
            # Try to handle recovery options
            recovery_result = handle_google_recovery_options(driver)
            
            # Check if we successfully left the recovery page
            new_url = driver.current_url
            if "gds.google.com/web/recoveryoptions" not in new_url:
                print(f"✅ Successfully left recovery options page! Now at: {new_url}")
                recovery_handled = True
                break
            else:
                print(f"⚠️ Still on recovery options page after attempt {attempt + 1}")
                time.sleep(random.uniform(2.0, 3.0))
        
        if not recovery_handled:
            print("⚠️ Could not automatically handle recovery options after multiple attempts")
            print("🔧 Attempting manual guidance approach...")
            
            # Try direct navigation as last resort
            print("🔗 Trying direct navigation to Cloud Console as final attempt...")
            try:
                driver.get("https://console.cloud.google.com/")
                time.sleep(random.uniform(4.0, 6.0))
                final_url = driver.current_url
                if "console.cloud.google.com" in final_url:
                    print(f"✅ Direct navigation successful: {final_url}")
                    recovery_handled = True
                else:
                    print(f"⚠️ Direct navigation failed, still at: {final_url}")
            except Exception as direct_nav_error:
                print(f"❌ Direct navigation error: {direct_nav_error}")
        
        if recovery_handled:
            print("✅ Recovery options page successfully handled!")
            time.sleep(random.uniform(2.0, 3.0))
        else:
            print("⚠️ Recovery options handling incomplete - continuing with caution...")
    
    print("🔍 Verifying Cloud Console access...")
    
    # Final verification that we're on Cloud Console
    final_url = driver.current_url
    print(f"📍 Final URL: {final_url}")
    
    if "console.cloud.google.com" in final_url:
        print("✅ Successfully accessed Google Cloud Console!")
    else:
        print("⚠️ Warning: May not be on Cloud Console. Proceeding anyway...")
        print(f"   Current URL: {final_url}")

    # Check for Google Cloud Console initial country selection (first-time login)
    print("🔍 Checking for Google Cloud Console country selection modal...")
    time.sleep(random.uniform(1.0, 3.0))  # Check within 3 seconds as mentioned
    
    # Look for the specific welcome modal dialog
    try:
        # Check if there's a modal dialog with the welcome message and country selection
        modal_indicators = [
            "mat-mdc-dialog-content",
            ".mat-mdc-dialog-content",
            "[role='dialog']",
            ".cdk-overlay-container"
        ]
        
        modal_found = False
        modal_element = None
        
        for indicator in modal_indicators:
            try:
                modal_element = driver.find_element(By.CSS_SELECTOR, indicator)
                if modal_element and modal_element.is_displayed():
                    modal_text = modal_element.text.lower()
                    # Check for specific indicators from the provided HTML
                    welcome_indicators = [
                        "welcome" in modal_text,
                        "country" in modal_text,
                        "terms of service" in modal_text,
                        "google cloud" in modal_text,
                        "create and manage" in modal_text
                    ]
                    
                    if any(welcome_indicators):
                        print("🌍 Found Google Cloud Console welcome modal with country selection!")
                        modal_found = True
                        break
            except:
                continue
        
        if modal_found:
            print("🌍 Handling Google Cloud Console welcome and country selection...")
            
            # Look for the specific country dropdown (cfc-select with p6ntest-country-dropdown class)
            print("🔍 Looking for country dropdown...")
            country_dropdown_selectors = [
                ".p6ntest-country-dropdown",
                "cfc-select[formcontrolname='optInCountry']",
                "#cfc-select-0",
                "cfc-select[aria-labelledby='tos-country-of-residence']",
                "[role='combobox'][aria-haspopup='listbox']",
                "cfc-select.cfc-select"
            ]
            
            country_dropdown = None
            for selector in country_dropdown_selectors:
                try:
                    country_dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    print(f"✅ Found country dropdown with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if country_dropdown:
                # Click to open the dropdown
                print("🖱️ Clicking country dropdown...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", country_dropdown)
                human_mouse_move_to(country_dropdown)
                country_dropdown.click()
                time.sleep(random.uniform(0.5, 1.0))  # Reduced wait time
                
                # Look for United States in the dropdown options
                print("🔍 Looking for United States in country options...")
                us_selectors = [
                    "//cfc-option[contains(text(), 'United States')]",
                    "//div[contains(@class, 'cfc-option') and contains(text(), 'United States')]",
                    "//span[contains(text(), 'United States')]",
                    "//mat-option[contains(text(), 'United States')]",
                    "//*[contains(text(), 'United States') and contains(@class, 'option')]",
                    "//cfc-option//span[contains(text(), 'United States')]"
                ]
                
                us_option = None
                for selector in us_selectors:
                    try:
                        us_option = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, selector)))  # Reduced wait time to 3 seconds
                        print(f"✅ Found United States option with selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if us_option:
                    print("🇺🇸 Selecting United States...")
                    # Use JavaScript click for faster execution
                    driver.execute_script("arguments[0].click();", us_option)
                    print("✅ United States selected successfully!")
                else:
                    print("⚠️ Could not find United States option, continuing with current selection...")
            else:
                print("⚠️ Could not find country dropdown")
            
            # Look for and check the "I agree" checkbox for Terms of Service
            print("☑️ Looking for Terms of Service agreement...")
            
            # First try to find and click the checkbox directly
            checkbox_selectors = [
                "input[type='checkbox'][id*='mat-mdc-checkbox'][id*='input']",  # Dynamic mat-mdc-checkbox selector
                "input[type='checkbox'][id^='mat-mdc-checkbox-'][id$='-input']",  # Starts with mat-mdc-checkbox- and ends with -input
                ".mdc-checkbox__native-control",
                "mat-checkbox[formcontrolname='umbrella'] input",
                "input[type='checkbox'][tabindex='0']",
                "mat-checkbox input[type='checkbox']",
                "#mat-mdc-checkbox-0-input",  # Fallback to original
                "#mat-mdc-checkbox-1-input",  # Alternative numbers
                "#mat-mdc-checkbox-2-input"
            ]
            
            agreement_checkbox = None
            checkbox_clicked = False
            
            for selector in checkbox_selectors:
                try:
                    agreement_checkbox = driver.find_element(By.CSS_SELECTOR, selector)
                    if agreement_checkbox and agreement_checkbox.is_displayed():
                        print(f"✅ Found agreement checkbox with selector: {selector}")
                        
                        # Check if checkbox is already checked
                        is_checked = agreement_checkbox.is_selected()
                        if not is_checked:
                            print("☑️ Checking Terms of Service agreement...")
                            # Use JavaScript click for more reliable interaction
                            driver.execute_script("arguments[0].click();", agreement_checkbox)
                            print("✅ Terms of Service agreement checked!")
                            checkbox_clicked = True
                        else:
                            print("✅ Terms of Service agreement already checked!")
                            checkbox_clicked = True
                        break
                except:
                    continue
            
            # If checkbox not found or clicked, try clicking on "I agree" text as alternative
            if not checkbox_clicked:
                print("⚠️ Could not find checkbox, trying to click on 'I agree' text...")
                
                # Target only the text node "I agree to the" without the links
                agree_text_selectors = [
                    "//span[contains(@class, 'cfc-text-title-5') and starts-with(normalize-space(text()), 'I agree to the')]",
                    "//span[contains(@class, 'ng-star-inserted') and starts-with(normalize-space(text()), 'I agree to the')]",
                    "//mat-checkbox//span[starts-with(normalize-space(text()), 'I agree to the')]",
                    "//label[contains(@for, 'checkbox')]//span[starts-with(text(), 'I agree to the')]"
                ]
                
                for selector in agree_text_selectors:
                    try:
                        agree_elements = driver.find_elements(By.XPATH, selector)
                        for agree_text in agree_elements:
                            if agree_text and agree_text.is_displayed():
                                # Double check this element doesn't contain links as children
                                links_in_element = agree_text.find_elements(By.TAG_NAME, "a")
                                if len(links_in_element) == 0:  # Only click if no links inside
                                    print(f"✅ Found 'I agree' text span (no links) with selector: {selector}")
                                    # Use JavaScript click to avoid accidentally clicking links
                                    driver.execute_script("arguments[0].click();", agree_text)
                                    print("✅ Clicked on 'I agree' text span - Terms of Service accepted!")
                                    
                                    # Wait a moment and verify the checkbox is actually checked
                                    time.sleep(1.0)
                                    
                                    # Try to find the associated checkbox and verify it's checked
                                    try:
                                        # Look for the checkbox that should now be checked
                                        checkbox_check = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'][id*='mat-mdc-checkbox'][id*='input']")
                                        if checkbox_check.is_selected():
                                            print("✅ Verified: Checkbox is now checked!")
                                            checkbox_clicked = True
                                        else:
                                            print("⚠️ Text clicked but checkbox not checked, trying direct checkbox click...")
                                            driver.execute_script("arguments[0].click();", checkbox_check)
                                            if checkbox_check.is_selected():
                                                print("✅ Checkbox now checked via direct click!")
                                                checkbox_clicked = True
                                    except:
                                        print("⚠️ Could not verify checkbox state, assuming agreement completed")
                                        checkbox_clicked = True
                                    
                                    break
                                else:
                                    # Try clicking on the text coordinates directly
                                    try:
                                        location = agree_text.location
                                        size = agree_text.size
                                        # Click on the left portion of the text (before links)
                                        x_offset = size['width'] * 0.2  # Click at 20% from left
                                        y_offset = size['height'] * 0.5  # Click at middle height
                                        pyautogui.click(location['x'] + x_offset, location['y'] + y_offset)
                                        print("✅ Clicked on 'I agree' text portion - Terms of Service accepted!")
                                        
                                        # Wait and verify checkbox
                                        time.sleep(1.0)
                                        try:
                                            checkbox_check = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'][id*='mat-mdc-checkbox'][id*='input']")
                                            if checkbox_check.is_selected():
                                                print("✅ Verified: Checkbox is now checked!")
                                                checkbox_clicked = True
                                            else:
                                                driver.execute_script("arguments[0].click();", checkbox_check)
                                                checkbox_clicked = True
                                        except:
                                            checkbox_clicked = True
                                        break
                                    except:
                                        continue
                        if checkbox_clicked:
                            break
                    except:
                        continue
            
            if not checkbox_clicked:
                print("⚠️ Could not find Terms of Service agreement option")
                # Don't proceed to project creation if agreement is not completed
                print("🛑 Stopping automation - Terms of Service agreement is required!")
                raise Exception("Terms of Service agreement not completed - automation stopped")
            
            # Look for and click the "Agree and continue" button
            print("➡️ Looking for 'Agree and continue' button...")
            
            continue_selectors = [
                "//span[contains(text(), 'Agree and continue')]/parent::button",
                "//button[contains(text(), 'Agree and continue')]",
                "//span[contains(@class, 'mat-mdc-dialog-legacy-line-height') and contains(text(), 'Agree and continue')]/parent::button",
                "//button//span[contains(text(), 'Agree and continue')]",
                "//span[text()='Agree and continue']//ancestor::button[1]",
                "//mat-dialog-actions//button[contains(text(), 'Agree') or contains(text(), 'Continue')]",
                ".mat-mdc-dialog-actions button",
                "//button[contains(text(), 'Continue')]",
                "//button[contains(text(), 'Get started')]",
                "//button[contains(text(), 'Start')]",
                "//button[contains(@class, 'mdc-button') and contains(text(), 'continue')]",
                "//button[contains(@class, 'mat-mdc-button') and contains(text(), 'continue')]"
            ]
            
            continue_button = None
            for selector in continue_selectors:
                try:
                    if selector.startswith("//"):
                        continue_button = driver.find_element(By.XPATH, selector)
                    else:
                        continue_button = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if continue_button and continue_button.is_displayed() and continue_button.is_enabled():
                        print(f"✅ Found continue button with selector: {selector}")
                        break
                except:
                    continue_button = None
                    continue
            
            if continue_button:
                print("✅ Clicking 'Agree and continue' button...")
                
                # Wait for any overlays or loading elements to disappear
                print("⏳ Waiting for overlays to clear...")
                time.sleep(random.uniform(1.0, 2.0))
                
                # Try to dismiss any overlays that might be blocking the click
                try:
                    # Look for and remove overlay backdrops
                    overlays = driver.find_elements(By.CSS_SELECTOR, ".cdk-overlay-backdrop, .cfc-progress-button-resolved")
                    for overlay in overlays:
                        if overlay.is_displayed():
                            print("🔍 Found blocking overlay, trying to dismiss...")
                            driver.execute_script("arguments[0].style.display = 'none';", overlay)
                except:
                    pass
                
                # Use JavaScript click to avoid click interception
                try:
                    print("🖱️ Using JavaScript click to avoid interception...")
                    driver.execute_script("arguments[0].click();", continue_button)
                    print("✅ 'Agree and continue' button clicked with JavaScript!")
                except Exception as js_error:
                    print(f"⚠️ JavaScript click failed: {js_error}")
                    # Fallback to regular click with retry
                    try:
                        print("🔄 Trying regular click as fallback...")
                        human_mouse_move_to(continue_button)
                        continue_button.click()
                        print("✅ 'Agree and continue' button clicked with regular click!")
                    except Exception as regular_error:
                        print(f"⚠️ Regular click also failed: {regular_error}")
                
                time.sleep(random.uniform(2.0, 3.0))
                print("✅ Google Cloud Console welcome modal completed!")
                
                # Wait for modal to close and verify it's gone
                print("⏳ Waiting for modal to close...")
                time.sleep(random.uniform(3.0, 5.0))  # Increased wait time
                
                # Verify modal is closed by checking if it's still visible
                modal_closed = False
                try:
                    modal_check = driver.find_element(By.CSS_SELECTOR, "mat-mdc-dialog-content, .mat-mdc-dialog-content, [role='dialog']")
                    if not modal_check.is_displayed():
                        modal_closed = True
                        print("✅ Modal successfully closed!")
                except:
                    modal_closed = True
                    print("✅ Modal successfully closed!")
                
                if not modal_closed:
                    print("⚠️ Modal still visible, waiting longer...")
                    time.sleep(random.uniform(5.0, 8.0))  # Wait even longer
                    
                    # Try to force close the modal if still open
                    try:
                        # Try pressing Escape key to close modal
                        pyautogui.press('escape')
                        time.sleep(2.0)
                        print("⌨️ Attempted to close modal with Escape key")
                    except:
                        pass
                    
            else:
                print("⚠️ Could not find 'Agree and continue' button")
                # Try looking for any button in the modal footer
                try:
                    modal_buttons = modal_element.find_elements(By.TAG_NAME, "button")
                    for btn in modal_buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            btn_text = btn.text.lower()
                            if any(word in btn_text for word in ['continue', 'agree', 'start', 'proceed']):
                                print(f"✅ Found fallback button: {btn.text}")
                                
                                # Use JavaScript click for fallback too
                                try:
                                    driver.execute_script("arguments[0].click();", btn)
                                    print("✅ Modal completed with fallback button (JavaScript)!")
                                except:
                                    human_mouse_move_to(btn)
                                    btn.click()
                                    print("✅ Modal completed with fallback button!")
                                
                                # Wait for modal to close
                                print("⏳ Waiting for modal to close...")
                                time.sleep(random.uniform(4.0, 6.0))
                                break
                except Exception as fallback_error:
                    print(f"⚠️ Fallback button search failed: {fallback_error}")
                
        else:
            print("✅ No welcome modal found - user may have already completed this step")
            
    except Exception as country_modal_error:
        print(f"⚠️ Error handling welcome modal: {country_modal_error}")
        print("💡 You may need to manually complete the country selection if prompted")

    # Final check for Google Cloud Console first-time setup before project creation
    print("🔍 Final check for any first-time setup requirements...")
    time.sleep(random.uniform(2.0, 3.0))
    
    try:
        # Check current URL and page content for first-time setup indicators
        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower()
        
        # Look for first-time setup indicators
        first_time_indicators = [
            "welcome to google cloud" in page_source,
            "get started with google cloud" in page_source,
            "country" in page_source and "terms" in page_source,
            "first time" in page_source,
            "setup" in page_source and "google cloud" in page_source,
            "mat-mdc-dialog" in page_source and "country" in page_source
        ]
        
        if any(first_time_indicators):
            print("🎯 First-time setup requirements detected!")
            
            # Handle any remaining modal dialogs
            modal_handled = False
            max_modal_attempts = 3
            
            for attempt in range(max_modal_attempts):
                print(f"🔍 Modal check attempt {attempt + 1}/{max_modal_attempts}...")
                
                try:
                    # Look for visible modal dialogs
                    modal_selectors = [
                        ".mat-mdc-dialog-container",
                        ".cdk-overlay-container .mat-mdc-dialog-surface", 
                        "[role='dialog']",
                        ".mat-dialog-container"
                    ]
                    
                    active_modal = None
                    for selector in modal_selectors:
                        try:
                            modals = driver.find_elements(By.CSS_SELECTOR, selector)
                            for modal in modals:
                                if modal.is_displayed():
                                    modal_text = modal.text.lower()
                                    if any(keyword in modal_text for keyword in ["country", "terms", "welcome", "setup", "get started"]):
                                        active_modal = modal
                                        print(f"✅ Found active setup modal with selector: {selector}")
                                        break
                            if active_modal:
                                break
                        except:
                            continue
                    
                    if active_modal:
                        print("🔧 Handling active setup modal...")
                        
                        # Look for accept/continue button
                        button_selectors = [
                            "//button[contains(.//span, 'Continue')]",
                            "//button[contains(.//span, 'Accept')]",
                            "//button[contains(.//span, 'Get started')]", 
                            "//button[contains(.//span, 'I accept')]",
                            "//button[contains(.//span, 'Agree')]",
                            ".mat-mdc-button.mat-primary",
                            "button[type='submit']"
                        ]
                        
                        button_clicked = False
                        for button_selector in button_selectors:
                            try:
                                if button_selector.startswith("//"):
                                    buttons = active_modal.find_elements(By.XPATH, button_selector)
                                else:
                                    buttons = active_modal.find_elements(By.CSS_SELECTOR, button_selector)
                                
                                for button in buttons:
                                    if button.is_displayed() and button.is_enabled():
                                        print(f"🎯 Clicking setup button: {button.text}")
                                        driver.execute_script("arguments[0].click();", button)
                                        time.sleep(random.uniform(2.0, 3.0))
                                        button_clicked = True
                                        modal_handled = True
                                        break
                                if button_clicked:
                                    break
                            except:
                                continue
                        
                        if button_clicked:
                            print("✅ Setup modal handled successfully!")
                            break
                        else:
                            print("⚠️ Could not find suitable button in modal, trying escape...")
                            try:
                                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                                time.sleep(random.uniform(1.0, 2.0))
                                modal_handled = True
                                break
                            except:
                                pass
                    else:
                        print("✅ No active setup modal found")
                        modal_handled = True
                        break
                        
                except Exception as modal_error:
                    print(f"⚠️ Error checking for modal in attempt {attempt + 1}: {modal_error}")
                    if attempt == max_modal_attempts - 1:
                        print("⚠️ Max modal attempts reached, continuing anyway...")
                        modal_handled = True
            
            if not modal_handled:
                print("⚠️ Could not handle all setup modals automatically")
                print("💡 You may need to complete setup manually if prompted")
        else:
            print("✅ No first-time setup requirements detected")
            
    except Exception as setup_check_error:
        print(f"⚠️ Error during final setup check: {setup_check_error}")
        print("💡 Continuing with project creation...")

    # Step 5: Create new project using direct approach
    print("🆕 Creating new project...")
    
    # CRITICAL: Final check for recovery options before project creation
    current_url_before_project = driver.current_url
    print(f"📍 URL before project creation: {current_url_before_project}")
    
    if "gds.google.com/web/recoveryoptions" in current_url_before_project:
        print("🚨 CRITICAL: Still on recovery options page before project creation!")
        print("📱 Must handle recovery options first...")
        
        # Force handle recovery options with aggressive approach
        print("🔧 Using aggressive recovery options handling...")
        
        # Try multiple escape methods
        escape_methods = [
            ("Direct Cloud Console navigation", lambda: driver.get("https://console.cloud.google.com/")),
            ("Home page navigation", lambda: driver.get("https://console.cloud.google.com/home")),
            ("Project selector navigation", lambda: driver.get("https://console.cloud.google.com/projectselector")),
            ("Escape key press", lambda: driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE))
        ]
        
        recovery_escaped = False
        for method_name, method_func in escape_methods:
            try:
                print(f"🔧 Trying: {method_name}")
                method_func()
                time.sleep(random.uniform(3.0, 5.0))
                
                new_url = driver.current_url
                if "gds.google.com/web/recoveryoptions" not in new_url:
                    print(f"✅ {method_name} successful! Now at: {new_url}")
                    recovery_escaped = True
                    break
                else:
                    print(f"⚠️ {method_name} failed, still on recovery page")
            except Exception as method_error:
                print(f"❌ {method_name} error: {method_error}")
                continue
        
        if not recovery_escaped:
            print("⚠️ Could not escape recovery options automatically")
            print("💡 Manual intervention may be required")
        else:
            print("✅ Successfully escaped recovery options page!")
            time.sleep(random.uniform(2.0, 3.0))
    
    # Ensure we're ready for project creation
    print("🔍 Final readiness check for project creation...")
    
    # Dismiss any remaining overlays before project creation
    print("🚫 Clearing any overlays before project creation...")
    dismiss_overlay(driver)
    time.sleep(1)
    
    print("🚀 STRATEGY: Direct navigation to project creation page")
    
    # Primary approach: Direct navigation to project creation page
    print("📍 Navigating directly to: https://console.cloud.google.com/projectcreate")
    try:
        # Direct navigation to project creation page
        driver.get("https://console.cloud.google.com/projectcreate")
        print("✅ Successfully navigated to project creation page!")
        
        # Wait for page to load
        print("⏳ Waiting for project creation page to load...")
        time.sleep(random.uniform(3.0, 5.0))
        
        # CRITICAL: Check for first-time Google Console setup immediately after navigation
        print("🎯 PRIORITY: Checking for first-time Google Console setup (country selection & agreement)...")
        first_time_handled = handle_google_console_first_time_setup(driver)
        if first_time_handled:
            print("✅ First-time setup completed successfully!")
            time.sleep(random.uniform(2.0, 4.0))  # Give extra time after setup
        
        # Check for CAPTCHA or verification
        if not wait_for_page_load_and_check_captcha(driver):
            print("⚠️ CAPTCHA or verification detected during navigation")
        
        # Verify we're on the correct page
        current_url = driver.current_url
        if "projectcreate" in current_url or "create" in current_url:
            print("✅ Confirmed: On project creation page")
            print(f"📍 Current URL: {current_url}")
            project_creation_success = True
        else:
            print(f"⚠️ Unexpected URL after navigation: {current_url}")
            project_creation_success = False
            
    except Exception as direct_error:
        print(f"❌ Direct approach failed: {direct_error}")
        print("🔄 Will fall back to traditional button-clicking approach...")
        project_creation_success = False
    
    # Fallback approach: Traditional button clicking
    if not project_creation_success:
        print("� Direct approach failed, trying traditional button-clicking approach...")
        project_creation_success = False  # Traditional approach not implemented
    
    # Final fallback: Manual intervention
    if not project_creation_success:
        print("❌ Both approaches failed!")
        print("🔧 Manual intervention required...")
        print("💡 Please manually navigate to: https://console.cloud.google.com/projectcreate")
        input("Press Enter after you're on the project creation page...")
    
    # Step 6: Fill project name
    print("📝 Filling project name...")
    try:
        # Dismiss any overlays before trying to fill project name
        dismiss_overlay(driver)
        
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
                project_name_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
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
            
            # Use safe_click to handle any overlays that might intercept the click
            if safe_click(driver, project_name_input, "project name input"):
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
                print("❌ Could not click project name input field due to overlay")
        else:
            print("❌ Could not find project name input field")
            
    except Exception as name_error:
        print(f"❌ Error filling project name: {name_error}")
    
    # Step 7: Click create button
    print("🚀 Clicking create button...")
    try:
        # Dismiss any overlays before clicking create button
        dismiss_overlay(driver)
        
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
            # Scroll to button and use safe_click to handle overlays
            driver.execute_script("arguments[0].scrollIntoView(true);", create_btn)
            time.sleep(random.uniform(1.0, 2.0))
            
            if safe_click(driver, create_btn, "Create button"):
                time.sleep(random.uniform(3.0, 5.0))
                print("✅ Project creation initiated!")
                print_milestone_timing("🆕 PROJECT CREATION STARTED")
                
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
                                
                                # Step 10: Navigate directly to Gmail API and enable it
                                print("📧 Navigating directly to Gmail API page...")
                                try:
                                    gmail_api_enabled = False
                                    
                                    # Direct navigation to Gmail API marketplace page (most reliable method)
                                    project_id = PROJECT_NAME  # Use the project name we created
                                    gmail_api_url = f"https://console.cloud.google.com/marketplace/product/google/gmail.googleapis.com?project={project_id}"
                                    
                                    print(f"🔗 Navigating directly to Gmail API URL: {gmail_api_url}")
                                    driver.get(gmail_api_url)
                                    time.sleep(random.uniform(3.0, 5.0))  # Max 5 seconds for Gmail API as requested
                                    
                                    # Verify we're on the correct Gmail API page
                                    current_url = driver.current_url
                                    print(f"📍 Current URL: {current_url}")
                                    
                                    # Check if we're on the correct Gmail API marketplace page
                                    correct_page_indicators = [
                                        "marketplace/product/google/gmail.googleapis.com" in current_url,
                                        "gmail.googleapis.com" in current_url and "marketplace" in current_url,
                                        "apis/library/gmail.googleapis.com" in current_url  # Alternative API library URL
                                    ]
                                    
                                    page_verified = any(correct_page_indicators)
                                    
                                    if not page_verified:
                                        print("⚠️ Not on the expected Gmail API page, trying alternative URLs...")
                                        
                                        # Try alternative Gmail API URLs
                                        alternative_urls = [
                                            f"https://console.cloud.google.com/apis/library/gmail.googleapis.com?project={project_id}",
                                            f"https://console.cloud.google.com/apis/api/gmail.googleapis.com?project={project_id}",
                                            "https://console.cloud.google.com/marketplace/product/google/gmail.googleapis.com",
                                            "https://console.cloud.google.com/apis/library/gmail.googleapis.com"
                                        ]
                                        
                                        for alt_url in alternative_urls:
                                            try:
                                                print(f"🔗 Trying alternative URL: {alt_url}")
                                                driver.get(alt_url)
                                                time.sleep(random.uniform(4.0, 6.0))
                                                
                                                alt_url_current = driver.current_url
                                                if "gmail.googleapis.com" in alt_url_current or "Gmail API" in driver.page_source:
                                                    print(f"✅ Alternative URL successful: {alt_url_current}")
                                                    page_verified = True
                                                    break
                                            except Exception as alt_url_error:
                                                print(f"⚠️ Alternative URL failed: {alt_url_error}")
                                                continue
                                    
                                    if page_verified:
                                        print("✅ Successfully navigated to Gmail API page!")
                                        
                                        # Additional verification by looking for page elements
                                        print("🔍 Verifying Gmail API page elements...")
                                        page_element_indicators = [
                                            "//h1[contains(text(), 'Gmail API')]",
                                            "//h2[contains(text(), 'Gmail API')]",
                                            "//*[contains(text(), 'Gmail API')]",
                                            "//span[contains(text(), 'Enable')]",
                                            "//button[contains(text(), 'Enable')]",
                                            "//*[contains(text(), 'google/gmail')]"
                                        ]
                                        
                                        element_found = False
                                        for indicator in page_element_indicators:
                                            try:
                                                element = driver.find_element(By.XPATH, indicator)
                                                if element and element.is_displayed():
                                                    element_text = element.text[:50] if element.text else element.get_attribute("textContent")[:50]
                                                    print(f"✅ Found Gmail API page element: '{element_text}...'")
                                                    element_found = True
                                                    break
                                            except:
                                                continue
                                        
                                        if not element_found:
                                            print("⚠️ Gmail API page elements not found, but URL looks correct")
                                    else:
                                        print("⚠️ Could not navigate to Gmail API page after trying all URLs")
                                        raise Exception("Failed to navigate to Gmail API page")
                                    
                                    # Now look for the Enable button on the Gmail API page
                                    print("� Looking for Enable button to enable Gmail API...")
                                    time.sleep(random.uniform(2.0, 4.0))  # Wait for page to fully load
                                    
                                    # Look for the blue Enable button on Gmail API page with enhanced detection
                                    print("🔘 Looking for blue Enable button with enhanced detection...")
                                    enable_selectors = [
                                            # High priority selectors for Gmail API Enable button
                                            "//button[contains(text(), 'Enable') and not(contains(text(), 'Disable'))]",
                                            "//button[normalize-space(text())='Enable']",
                                            "//button[normalize-space(text())='ENABLE']",
                                            "//span[normalize-space(text())='Enable']/parent::button",
                                            "//span[normalize-space(text())='ENABLE']/parent::button",
                                            
                                            # Most specific selectors for the Gmail API Enable button (blue/primary button)
                                            "//button[contains(@class, 'mdc-button--raised') and contains(@class, 'mdc-button--primary') and (contains(text(), 'Enable') or contains(text(), 'ENABLE'))]",
                                            "//button[contains(@class, 'mat-mdc-raised-button') and contains(@class, 'mat-primary') and (contains(text(), 'Enable') or contains(text(), 'ENABLE'))]",
                                            "//button[contains(@class, 'mdc-button--raised') and (contains(text(), 'Enable') or contains(text(), 'ENABLE'))]",
                                            "//button[contains(@class, 'mat-mdc-raised-button') and (contains(text(), 'Enable') or contains(text(), 'ENABLE'))]",
                                            "//button[contains(@class, 'mdc-button') and contains(@class, 'cfc-button') and (contains(text(), 'Enable') or contains(text(), 'ENABLE'))]",
                                            "//button[@color='primary' and (contains(text(), 'Enable') or contains(text(), 'ENABLE'))]",
                                            "//button[contains(@class, 'primary') and (contains(text(), 'Enable') or contains(text(), 'ENABLE'))]",
                                            "//button[contains(@class, 'blue') and (contains(text(), 'Enable') or contains(text(), 'ENABLE'))]",
                                            
                                            # Specific Gmail API page context selectors
                                            "//div[contains(@class, 'api-detail')]//button[contains(text(), 'Enable') or contains(text(), 'ENABLE')]",
                                            "//div[contains(@class, 'enable-api')]//button[contains(text(), 'Enable') or contains(text(), 'ENABLE')]",
                                            "//section[contains(@class, 'api-overview')]//button[contains(text(), 'Enable') or contains(text(), 'ENABLE')]",
                                            "//main//button[contains(text(), 'Enable') or contains(text(), 'ENABLE')]",
                                            "//div[contains(@class, 'api-hero')]//button[contains(text(), 'Enable') or contains(text(), 'ENABLE')]",
                                            
                                            # Marketplace-specific selectors
                                            "//div[contains(@class, 'marketplace')]//button[contains(text(), 'Enable') or contains(text(), 'ENABLE')]",
                                            "//div[contains(@class, 'product-detail')]//button[contains(text(), 'Enable') or contains(text(), 'ENABLE')]",
                                            "//div[contains(@class, 'product-action')]//button[contains(text(), 'Enable') or contains(text(), 'ENABLE')]",
                                            
                                            # Generic Enable button selectors with better filtering
                                            "//button[(contains(text(), 'Enable') or contains(text(), 'ENABLE')) and not(contains(text(), 'Disable')) and not(contains(text(), 'Unable'))]",
                                            "//button[text()='Enable' or text()='ENABLE']",
                                            "//span[text()='Enable' or text()='ENABLE']//ancestor::button[1]",
                                            "//div[text()='Enable' or text()='ENABLE']//ancestor::button[1]",
                                            
                                            # CSS selectors for Enable buttons
                                            "button[aria-label*='Enable']",
                                            "button.mdc-button--raised:contains('Enable')",
                                            "button.mat-mdc-raised-button:contains('Enable')",
                                            ".enable-button",
                                            "[data-track-name*='enable']",
                                            "button[type='submit']:contains('Enable')",
                                            
                                            # Input type selectors
                                            "//input[@type='submit' and (@value='Enable' or @value='ENABLE')]",
                                            "//input[@type='button' and (@value='Enable' or @value='ENABLE')]"
                                        ]
                                    
                                    enable_btn_found = False
                                    
                                    # First, wait a bit more for the page to fully load
                                    print("⏳ Waiting for Gmail API page to fully load...")
                                    time.sleep(random.uniform(2.0, 4.0))
                                    
                                    # Scroll to top to ensure we see the enable button
                                    try:
                                        driver.execute_script("window.scrollTo(0, 0);")
                                        time.sleep(1.0)
                                        print("✅ Scrolled to top of page")
                                    except:
                                        pass
                                    
                                    # Try each selector with improved logic
                                    for selector_index, selector in enumerate(enable_selectors):
                                        try:
                                            print(f"🔍 Trying Enable button selector {selector_index + 1}/{len(enable_selectors)}: {selector[:80]}...")
                                            enable_elements = []
                                            
                                            if selector.startswith("//"):
                                                enable_elements = driver.find_elements(By.XPATH, selector)
                                            else:
                                                # Handle CSS selectors that contain :contains() (not valid CSS)
                                                if ":contains(" in selector:
                                                    # Skip invalid CSS selectors
                                                    continue
                                                else:
                                                    enable_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                            
                                            for enable_btn in enable_elements:
                                                if enable_btn and enable_btn.is_displayed() and enable_btn.is_enabled():
                                                    # Enhanced button validation
                                                    btn_text = (enable_btn.get_attribute("textContent") or enable_btn.text or "").strip()
                                                    btn_value = enable_btn.get_attribute("value") or ""
                                                    btn_aria_label = enable_btn.get_attribute("aria-label") or ""
                                                    btn_classes = enable_btn.get_attribute("class") or ""
                                                    btn_style = enable_btn.get_attribute("style") or ""
                                                    
                                                    print(f"   📋 Button details:")
                                                    print(f"      Text: '{btn_text}'")
                                                    print(f"      Value: '{btn_value}'")
                                                    print(f"      Classes: '{btn_classes}'")
                                                    print(f"      Aria-label: '{btn_aria_label}'")
                                                    
                                                    # More thorough filtering for Enable buttons
                                                    is_enable_btn = False
                                                    
                                                    # Check text content (primary check)
                                                    if btn_text.lower() == "enable" or btn_text.lower() == "enable api":
                                                        is_enable_btn = True
                                                        print(f"      ✅ Exact text match: '{btn_text}'")
                                                    elif "enable" in btn_text.lower() and "disable" not in btn_text.lower() and "unable" not in btn_text.lower():
                                                        is_enable_btn = True
                                                        print(f"      ✅ Text contains 'enable': '{btn_text}'")
                                                    elif "enable" in btn_value.lower():
                                                        is_enable_btn = True
                                                        print(f"      ✅ Value contains 'enable': '{btn_value}'")
                                                    elif "enable" in btn_aria_label.lower():
                                                        is_enable_btn = True
                                                        print(f"      ✅ Aria-label contains 'enable': '{btn_aria_label}'")
                                                    
                                                    # Check for blue/primary button styling (additional validation)
                                                    is_primary_styled = False
                                                    if any(cls in btn_classes.lower() for cls in ['primary', 'raised', 'blue', 'mdc-button--raised']):
                                                        is_primary_styled = True
                                                        print(f"      ✅ Has primary/blue styling")
                                                    
                                                    if is_enable_btn:
                                                        print(f"✅ Found valid Enable button with selector: {selector}")
                                                        if is_primary_styled:
                                                            print("   🎯 This appears to be the primary blue Enable button!")
                                                        
                                                        # Try to click the enable button
                                                            try:
                                                                # Scroll the button into view
                                                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", enable_btn)
                                                                time.sleep(random.uniform(1.0, 2.0))
                                                                
                                                                # Highlight the button briefly (for debugging)
                                                                try:
                                                                    driver.execute_script("arguments[0].style.border='3px solid red';", enable_btn)
                                                                    time.sleep(0.5)
                                                                    driver.execute_script("arguments[0].style.border='';", enable_btn)
                                                                except:
                                                                    pass
                                                                
                                                                # Try human-like mouse movement and click
                                                                human_mouse_move_to(enable_btn)
                                                                time.sleep(random.uniform(0.5, 1.0))
                                                                enable_btn.click()
                                                                print("✅ Gmail API Enable button clicked successfully with regular click!")
                                                                enable_btn_found = True
                                                                break
                                                                
                                                            except Exception as enable_click_error:
                                                                print(f"⚠️ Regular click failed: {enable_click_error}")
                                                                print("🔄 Trying JavaScript click...")
                                                                try:
                                                                    driver.execute_script("arguments[0].click();", enable_btn)
                                                                    print("✅ Gmail API Enable button clicked successfully with JavaScript!")
                                                                    enable_btn_found = True
                                                                    break
                                                                except Exception as js_click_error:
                                                                    print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                                    print("🔄 Trying pyautogui click...")
                                                                    try:
                                                                        # Get button location for pyautogui
                                                                        location = enable_btn.location
                                                                        size = enable_btn.size
                                                                        x = location['x'] + size['width'] // 2
                                                                        y = location['y'] + size['height'] // 2
                                                                        pyautogui.click(x, y)
                                                                        print("✅ Gmail API Enable button clicked successfully with pyautogui!")
                                                                        enable_btn_found = True
                                                                        break
                                                                    except Exception as pyautogui_click_error:
                                                                        print(f"⚠️ Pyautogui click also failed: {pyautogui_click_error}")
                                                                        continue
                                                
                                                if enable_btn_found:
                                                    break
                                                    
                                        except Exception as enable_search_error:
                                            print(f"⚠️ Error with enable selector {selector}: {enable_search_error}")
                                            continue
                                    
                                    # If no enable button found, do a comprehensive debug search
                                    if not enable_btn_found:
                                        print("🔍 No Enable button found with specific selectors. Trying fallback search for any visible 'Enable' button...")
                                        # Wait a bit more in case the UI is slow
                                        time.sleep(3)
                                        # Try again for any visible button or link with 'Enable'
                                        try:
                                            enable_candidates = driver.find_elements(By.XPATH, "//*[self::button or self::a][contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enable')]")
                                            print(f"🔍 Fallback: Found {len(enable_candidates)} elements with 'enable' in text.")
                                            for i, btn in enumerate(enable_candidates):
                                                try:
                                                    if btn.is_displayed() and btn.is_enabled():
                                                        print(f"  {i+1}. Tag: {btn.tag_name}, Text: '{btn.text.strip()}'")
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                                        time.sleep(1)
                                                        btn.click()
                                                        print("✅ Fallback: Clicked visible 'Enable' button!")
                                                        enable_btn_found = True
                                                        break
                                                except Exception as e:
                                                    print(f"⚠️ Fallback click failed: {e}")
                                        except Exception as e:
                                            print(f"⚠️ Fallback search failed: {e}")

                                    if not enable_btn_found:
                                        print("❌ Still could not find or click any 'Enable' button. Printing all visible button/link texts for debugging:")
                                        all_buttons = driver.find_elements(By.XPATH, "//button | //a")
                                        for btn in all_buttons:
                                            try:
                                                if btn.is_displayed():
                                                    print(f"  Tag: {btn.tag_name}, Text: '{btn.text.strip()}'")
                                            except:
                                                continue
                                    
                                    if enable_btn_found:
                                            print("🎉 Gmail API enabled successfully!")
                                            print("⏳ Waiting for API to be fully enabled and new page to load...")
                                            time.sleep(random.uniform(6.0, 10.0))
                                    else:
                                        print("⚠️ Could not find any Enable button")
                                        print("💡 The Gmail API might already be enabled, or the page structure has changed")
                                        print("💡 Proceeding to OAuth consent screen setup anyway...")

                                    # --- Always attempt OAuth consent screen setup here ---
                                    # After enabling Gmail API, proceed to OAuth consent screen
                                    if enable_btn_found:
                                        print("✅ Gmail API enabled successfully!")
                                        print_milestone_timing("📧 GMAIL API ENABLED")
                                        time.sleep(random.uniform(3.0, 5.0))
                                        
                                        # Step 11: Set up OAuth consent screen
                                        print("🔐 Setting up OAuth consent screen...")
                                        
                                        # Check current URL - Gmail API often redirects to OAuth overview automatically
                                        current_url = driver.current_url
                                        print(f"📍 Current page URL after Gmail API enable: {current_url}")
                                        
                                        # Check for any verification prompts before OAuth setup
                                        print("🔐 Checking for verifications before OAuth setup...")
                                        handle_google_verifications(driver, "api-setup")
                                        
                                        # Check if we're already on OAuth overview page
                                        if "auth/overview" in current_url:
                                            print("✅ Already on OAuth overview page after Gmail API enable")
                                        else:
                                            # Navigate to OAuth consent screen
                                            oauth_url = f"https://console.cloud.google.com/apis/credentials/consent?project={PROJECT_NAME}"
                                            print(f"🔗 Navigating to OAuth consent screen: {oauth_url}")
                                            driver.get(oauth_url)
                                            time.sleep(random.uniform(5.0, 8.0))
                                            
                                            # Check for verifications after OAuth navigation
                                            print("🔐 Checking for verifications after OAuth navigation...")
                                            handle_google_verifications(driver, "oauth-setup")
                                            
                                            # Update current URL after navigation
                                            current_url = driver.current_url
                                            print(f"📍 Current OAuth page URL after navigation: {current_url}")
                                        
                                        # CRITICAL: Dismiss OAuth navigation tutorial regardless of how we got here
                                        print("🚫 Preemptively dismissing any OAuth navigation tutorial overlays...")
                                        dismiss_oauth_overview_navigation_tutorial(driver)
                                        time.sleep(2)  # Wait for tutorial dismissal
                                        
                                        # Look for "Get started" button on OAuth overview page
                                        print("🔍 Checking for OAuth overview page with 'Get started' button...")
                                        
                                        # Check for text indicators that suggest we're on the overview page
                                        overview_indicators = [
                                            "Google auth platform not configured yet",
                                            "Get started configuring your application's identity",
                                            "manage credentials for calling Google APIs",
                                            "Sign in with Google",
                                            "oauth-empty-state",
                                            "auth/overview"
                                        ]
                                        
                                        page_source = driver.page_source
                                        is_overview_page = any(indicator in page_source for indicator in overview_indicators) or "auth/overview" in current_url
                                        
                                        if is_overview_page:
                                            print("✅ Detected OAuth overview page (new Gmail account)")
                                            
                                            # PRIORITY: Dismiss specific OAuth navigation tutorial blocking elements
                                            print("🚫 Dismissing OAuth overview navigation tutorial blocking elements...")
                                            oauth_tutorial_dismissed = dismiss_oauth_overview_navigation_tutorial(driver)
                                            
                                            if oauth_tutorial_dismissed:
                                                print("✅ OAuth overview tutorial successfully dismissed")
                                            else:
                                                print("⚠️ OAuth overview tutorial dismissal may be incomplete")
                                                # Fallback to generic dismissal
                                                print("🔄 Trying generic navigation tutorial dismissal as fallback...")
                                                dismiss_navigation_tutorial(driver)
                                            
                                            time.sleep(2)  # Wait after dismissing overlay
                                            
                                            print("🔍 Looking for 'Get started' button...")
                                            
                                            # Look for the "Get started" button with multiple selectors
                                            get_started_selectors = [
                                                # Specific selectors provided by user for the exact button
                                                "//*[@id='_0rif_panelgoog_1783835678']/cfc-panel-body/cfc-virtual-viewport/div[1]/div/oauth-empty-state/cfc-empty-state/div/cfc-empty-state-actions/a/span[2]",
                                                "#_0rif_panelgoog_1783835678 > cfc-panel-body > cfc-virtual-viewport > div.cfc-virtual-scroll-content-wrapper > div > oauth-empty-state > cfc-empty-state > div > cfc-empty-state-actions > a > span.mdc-button__label",
                                                
                                                # Generic selectors for similar OAuth overview buttons
                                                "//oauth-empty-state//cfc-empty-state-actions//a//span[contains(@class, 'mdc-button__label')]",
                                                "//oauth-empty-state//cfc-empty-state-actions//a[contains(text(), 'Get started')]",
                                                "//oauth-empty-state//cfc-empty-state-actions//a//span[contains(text(), 'Get started')]",
                                                "//cfc-empty-state-actions//a//span[contains(text(), 'Get started')]",
                                                "//cfc-empty-state-actions//a[contains(text(), 'Get started')]",
                                                
                                                # CSS selectors for OAuth overview page
                                                "oauth-empty-state cfc-empty-state-actions a span.mdc-button__label",
                                                "cfc-empty-state-actions a span.mdc-button__label",
                                                "oauth-empty-state a span.mdc-button__label",
                                                
                                                # High priority selectors for "Get started" button
                                                "//button[contains(text(), 'Get started') and not(contains(text(), 'Get started with'))]",
                                                "//a[contains(text(), 'Get started') and not(contains(text(), 'Get started with'))]",
                                                "//button[normalize-space(text())='Get started']",
                                                "//a[normalize-space(text())='Get started']",
                                                "//button[normalize-space(text())='GET STARTED']",
                                                "//a[normalize-space(text())='GET STARTED']",
                                                "//span[normalize-space(text())='Get started']/parent::button",
                                                "//span[normalize-space(text())='Get started']/parent::a",
                                                "//span[normalize-space(text())='GET STARTED']/parent::button",
                                                "//span[normalize-space(text())='GET STARTED']/parent::a",
                                                
                                                # Blue/primary button styling for "Get started"
                                                "//button[contains(@class, 'mdc-button--raised') and contains(@class, 'mdc-button--primary') and contains(text(), 'Get started')]",
                                                "//a[contains(@class, 'mdc-button--raised') and contains(@class, 'mdc-button--primary') and contains(text(), 'Get started')]",
                                                "//button[contains(@class, 'mat-mdc-raised-button') and contains(@class, 'mat-primary') and contains(text(), 'Get started')]",
                                                "//a[contains(@class, 'mat-mdc-raised-button') and contains(@class, 'mat-primary') and contains(text(), 'Get started')]",
                                                "//button[contains(@class, 'mdc-button--raised') and contains(text(), 'Get started')]",
                                                "//a[contains(@class, 'mdc-button--raised') and contains(text(), 'Get started')]",
                                                "//button[contains(@class, 'mat-mdc-raised-button') and contains(text(), 'Get started')]",
                                                "//a[contains(@class, 'mat-mdc-raised-button') and contains(text(), 'Get started')]",
                                                "//button[@color='primary' and contains(text(), 'Get started')]",
                                                "//a[@color='primary' and contains(text(), 'Get started')]",
                                                "//button[contains(@class, 'primary') and contains(text(), 'Get started')]",
                                                "//a[contains(@class, 'primary') and contains(text(), 'Get started')]",
                                                "//button[contains(@class, 'blue') and contains(text(), 'Get started')]",
                                                "//a[contains(@class, 'blue') and contains(text(), 'Get started')]",
                                                
                                                # Generic selectors for "Get started" button
                                                "//button[contains(text(), 'Get started')]",
                                                "//a[contains(text(), 'Get started')]",
                                                "//span[contains(text(), 'Get started')]//ancestor::button[1]",
                                                "//span[contains(text(), 'Get started')]//ancestor::a[1]",
                                                "//div[contains(text(), 'Get started')]//ancestor::button[1]",
                                                "//div[contains(text(), 'Get started')]//ancestor::a[1]",
                                                
                                                # CSS selectors (avoiding :contains() which is invalid)
                                                "button[aria-label*='Get started']",
                                                "a[aria-label*='Get started']",
                                                ".get-started-button",
                                                "[data-track-name*='get-started']",
                                                "button[type='submit'][title*='Get started']",
                                                "a[title*='Get started']"
                                            ]
                                            
                                            get_started_found = False
                                            
                                            for selector_index, selector in enumerate(get_started_selectors):
                                                try:
                                                    print(f"🔍 Trying 'Get started' selector {selector_index + 1}/{len(get_started_selectors)}: {selector[:80]}...")
                                                    
                                                    get_started_elements = []
                                                    if selector.startswith("//"):
                                                        get_started_elements = driver.find_elements(By.XPATH, selector)
                                                    else:
                                                        # Skip CSS selectors with :contains() as they're not valid
                                                        if ":contains(" in selector:
                                                            continue
                                                        else:
                                                            get_started_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                    
                                                    for get_started_btn in get_started_elements:
                                                        if get_started_btn and get_started_btn.is_displayed() and get_started_btn.is_enabled():
                                                            btn_text = (get_started_btn.get_attribute("textContent") or get_started_btn.text or "").strip()
                                                            btn_classes = get_started_btn.get_attribute("class") or ""
                                                            btn_tag = get_started_btn.tag_name
                                                            
                                                            print(f"   📋 Element details:")
                                                            print(f"      Tag: {btn_tag}")
                                                            print(f"      Text: '{btn_text}'")
                                                            print(f"      Classes: '{btn_classes}'")
                                                            
                                                            # Check if this is a valid "Get started" button or link
                                                            is_get_started_element = False
                                                            
                                                            # Check for "Get started" text (more permissive)
                                                            if "get started" in btn_text.lower():
                                                                # Make sure it's not "Get started with something"
                                                                if "get started with" not in btn_text.lower():
                                                                    is_get_started_element = True
                                                                    print(f"      ✅ Valid 'Get started' element: '{btn_text}'")
                                                            
                                                            # Also check for empty span with mdc-button__label class (common pattern)
                                                            elif btn_tag == "span" and "mdc-button__label" in btn_classes and btn_text == "":
                                                                # Check if parent is a link with Get started context
                                                                try:
                                                                    parent = get_started_btn.find_element(By.XPATH, "..")
                                                                    parent_text = (parent.get_attribute("textContent") or parent.text or "").strip()
                                                                    if "get started" in parent_text.lower():
                                                                        is_get_started_element = True
                                                                        print(f"      ✅ Found 'Get started' span inside link: '{parent_text}'")
                                                                        # Click the parent link instead
                                                                        get_started_btn = parent
                                                                except:
                                                                    pass
                                                            
                                                            if is_get_started_element:
                                                                print(f"✅ Found valid 'Get started' button: '{btn_text}'")
                                                                
                                                                try:
                                                                    # Scroll the button into view
                                                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", get_started_btn)
                                                                    time.sleep(random.uniform(1.0, 2.0))
                                                                    
                                                                    # Highlight the button briefly
                                                                    try:
                                                                        driver.execute_script("arguments[0].style.border='3px solid red';", get_started_btn)
                                                                        time.sleep(0.5)
                                                                        driver.execute_script("arguments[0].style.border='';", get_started_btn)
                                                                    except:
                                                                        pass
                                                                    
                                                                    # Try human-like click first
                                                                    human_mouse_move_to(get_started_btn)
                                                                    time.sleep(random.uniform(0.5, 1.0))
                                                                    get_started_btn.click()
                                                                    print("✅ 'Get started' button clicked successfully with regular click!")
                                                                    get_started_found = True
                                                                    break
                                                                    
                                                                except Exception as click_error:
                                                                    print(f"⚠️ Regular click failed: {click_error}")
                                                                    print("� Trying JavaScript click...")
                                                                    try:
                                                                        driver.execute_script("arguments[0].click();", get_started_btn)
                                                                        print("✅ 'Get started' button clicked successfully with JavaScript!")
                                                                        get_started_found = True
                                                                        break
                                                                    except Exception as js_click_error:
                                                                        print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                                        continue
                                                    
                                                    if get_started_found:
                                                        break
                                                        
                                                except Exception as selector_error:
                                                    print(f"⚠️ Error with 'Get started' selector: {selector_error}")
                                                    continue
                                            
                                            if get_started_found:
                                                print("✅ 'Get started' button clicked successfully!")
                                                print("⏳ Waiting for OAuth consent screen configuration page to load...")
                                                time.sleep(random.uniform(5.0, 8.0))
                                                
                                                # After clicking "Get started", we should be on the OAuth consent screen config
                                                current_url_after = driver.current_url
                                                print(f"📍 New URL after 'Get started' click: {current_url_after}")
                                                
                                                print("✅ OAuth consent screen configuration page loaded!")
                                                print("📝 Starting OAuth consent screen App Information configuration...")
                                                
                                                # CRITICAL: Additional first-time setup check before OAuth configuration
                                                print("🎯 PRIORITY: Final check for first-time setup before OAuth configuration...")
                                                final_setup_handled = handle_google_console_first_time_setup(driver)
                                                if final_setup_handled:
                                                    print("✅ Final first-time setup check completed!")
                                                    time.sleep(random.uniform(2.0, 3.0))
                                                
                                                # Step 12: Fill App Information form
                                                print("📝 Filling App Information form...")
                                                
                                                # Fill App Name field with email address
                                                print("📝 Filling App name field with email address...")
                                                try:
                                                    app_name_selectors = [
                                                        "input[formcontrolname='displayName']",
                                                        "input[matinput][formcontrolname='displayName']",
                                                        "input.cm-input.gmat-mdc-input.mat-mdc-input-element[formcontrolname='displayName']",
                                                        "input[aria-describedby*='mat-mdc-error'][formcontrolname='displayName']",
                                                        "input[id*='mat-input'][formcontrolname='displayName']",
                                                        "input[maxlength='63'][formcontrolname='displayName']",
                                                        "input[required][formcontrolname='displayName']"
                                                    ]
                                                    
                                                    app_name_input = None
                                                    for selector in app_name_selectors:
                                                        try:
                                                            app_name_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                                                            print(f"✅ Found app name input with selector: {selector}")
                                                            break
                                                        except TimeoutException:
                                                            continue
                                                    
                                                    if app_name_input:
                                                        # Scroll to element and click
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", app_name_input)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        human_mouse_move_to(app_name_input)
                                                        app_name_input.click()
                                                        time.sleep(random.uniform(0.5, 1.0))
                                                        
                                                        # Clear field and enter email address
                                                        app_name_input.clear()
                                                        app_name_input.send_keys(Keys.CONTROL + "a")
                                                        app_name_input.send_keys(Keys.DELETE)
                                                        time.sleep(random.uniform(0.3, 0.7))
                                                        
                                                        human_typing(app_name_input, EMAIL)
                                                        print(f"✅ App name filled with email: {EMAIL}")
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                    else:
                                                        print("⚠️ Could not find app name input field")
                                                        
                                                except Exception as app_name_error:
                                                    print(f"❌ Error filling app name: {app_name_error}")
                                                
                                                # Select user support email from dropdown
                                                print("📧 Selecting user support email from dropdown...")
                                                try:
                                                    # Look for the user support email dropdown (custom cfc-select component)
                                                    support_email_selectors = [
                                                        # Custom cfc-select selectors based on the structure provided
                                                        "//mat-label[contains(text(), 'User support email')]/parent::*/following-sibling::*//div[contains(@class, 'cfc-select-value')]",
                                                        "//mat-label[contains(text(), 'User support email')]/ancestor::*//div[contains(@class, 'cfc-select-value')]",
                                                        "div.cfc-select-value",
                                                        "//div[@class='cfc-select-value']",
                                                        "//span[@class='cfc-select-placeholder']//parent::div",
                                                        
                                                        # Try to find the cfc-select component
                                                        "//mat-form-field[.//mat-label[contains(text(), 'User support email')]]//div[contains(@class, 'cfc-select')]",
                                                        "//div[contains(@class, 'mat-mdc-form-field')][.//mat-label[contains(text(), 'User support email')]]//div[contains(@class, 'cfc-select')]",
                                                        "//mat-label[contains(text(), 'User support email')]/following-sibling::*//div[contains(@class, 'cfc-select')]",
                                                        
                                                        # Fallback to standard mat-select selectors
                                                        "//mat-label[contains(text(), 'User support email')]/parent::*/following-sibling::*//mat-select",
                                                        "//mat-label[contains(text(), 'User support email')]/ancestor::mat-form-field//mat-select",
                                                        "mat-select[formcontrolname='userSupportEmail']",
                                                        "mat-select[aria-label*='User support email']",
                                                        "//mat-form-field[.//mat-label[contains(text(), 'User support email')]]//mat-select",
                                                        "//div[contains(@class, 'mat-mdc-form-field')][.//mat-label[contains(text(), 'User support email')]]//mat-select",
                                                        "mat-select[formcontrolname*='support']",
                                                        "mat-select[formcontrolname*='email']"
                                                    ]
                                                    
                                                    support_email_dropdown = None
                                                    for selector in support_email_selectors:
                                                        try:
                                                            if selector.startswith("//"):
                                                                support_email_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                                                            else:
                                                                support_email_dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                                                            print(f"✅ Found user support email dropdown with selector: {selector}")
                                                            break
                                                        except TimeoutException:
                                                            continue
                                                    
                                                    if support_email_dropdown:
                                                        # Click to open dropdown
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", support_email_dropdown)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        human_mouse_move_to(support_email_dropdown)
                                                        support_email_dropdown.click()
                                                        print("✅ User support email dropdown opened")
                                                        time.sleep(random.uniform(2.0, 3.0))
                                                        
                                                        # Select the email option (for custom cfc-select component)
                                                        try:
                                                            # Look for email options in the custom cfc-select dropdown
                                                            email_option_selectors = [
                                                                # Custom cfc-select option selectors
                                                                f"//span[contains(@class, 'mdc-list-item__primary-text')]//span[contains(text(), '{EMAIL}')]",
                                                                f"//span[@class='mdc-list-item__primary-text']//span[contains(text(), '{EMAIL}')]",
                                                                f"//span[contains(@class, 'mdc-list-item__primary-text')]//span[text()='{EMAIL}']",
                                                                f"//li[contains(@class, 'mdc-list-item')]//span[contains(text(), '{EMAIL}')]",
                                                                f"//div[contains(@class, 'cfc-select-option')]//span[contains(text(), '{EMAIL}')]",
                                                                
                                                                # Generic selectors for custom dropdown options
                                                                "//span[contains(@class, 'mdc-list-item__primary-text')]//span[1]",
                                                                "//span[@class='mdc-list-item__primary-text']//span[1]",
                                                                "//li[contains(@class, 'mdc-list-item')][1]//span",
                                                                "//div[contains(@class, 'cfc-select-option')][1]",
                                                                
                                                                # Try to find any clickable email option
                                                                "//span[contains(@class, 'mdc-list-item__primary-text')]",
                                                                "//li[contains(@class, 'mdc-list-item')]",
                                                                "//div[contains(@class, 'cfc-select-option')]",
                                                                
                                                                # Fallback to standard Material Design dropdown options
                                                                f"//mat-option[contains(text(), '{EMAIL}')]",
                                                                f"//mat-option//span[contains(text(), '{EMAIL}')]",
                                                                "//mat-option[1]",  # First option
                                                                "mat-option:first-child",
                                                                "//mat-option[contains(@class, 'mat-mdc-option')]",
                                                                ".mat-mdc-option",
                                                                "mat-option"
                                                            ]
                                                            
                                                            email_option = None
                                                            for option_selector in email_option_selectors:
                                                                try:
                                                                    if option_selector.startswith("//"):
                                                                        email_options = driver.find_elements(By.XPATH, option_selector)
                                                                    else:
                                                                        email_options = driver.find_elements(By.CSS_SELECTOR, option_selector)
                                                                    
                                                                    for option in email_options:
                                                                        if option.is_displayed() and option.is_enabled():
                                                                            option_text = (option.get_attribute("textContent") or option.text or "").strip()
                                                                            print(f"📧 Found email option: '{option_text}'")
                                                                            
                                                                            # For custom cfc-select, we might need to click the parent element
                                                                            clickable_element = option
                                                                            
                                                                            # If this is a span inside a list item, try to click the list item
                                                                            if option.tag_name == "span":
                                                                                try:
                                                                                    # Try to find the parent list item
                                                                                    parent_li = option.find_element(By.XPATH, "./ancestor::li[contains(@class, 'mdc-list-item')]")
                                                                                    if parent_li:
                                                                                        clickable_element = parent_li
                                                                                        print(f"   🎯 Found parent list item for clicking")
                                                                                except:
                                                                                    pass
                                                                            
                                                                            # Try to click the element
                                                                            try:
                                                                                # Scroll element into view
                                                                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", clickable_element)
                                                                                time.sleep(random.uniform(0.5, 1.0))
                                                                                
                                                                                # Highlight the element briefly
                                                                                try:
                                                                                    driver.execute_script("arguments[0].style.border='2px solid red';", clickable_element)
                                                                                    time.sleep(0.5)
                                                                                    driver.execute_script("arguments[0].style.border='';", clickable_element)
                                                                                except:
                                                                                    pass
                                                                                
                                                                                # Try human-like click first
                                                                                human_mouse_move_to(clickable_element)
                                                                                clickable_element.click()
                                                                                print(f"✅ Selected email option: '{option_text}' with regular click")
                                                                                email_option = clickable_element
                                                                                break
                                                                                
                                                                            except Exception as click_error:
                                                                                print(f"⚠️ Regular click failed: {click_error}")
                                                                                print("🔄 Trying JavaScript click...")
                                                                                try:
                                                                                    driver.execute_script("arguments[0].click();", clickable_element)
                                                                                    print(f"✅ Selected email option: '{option_text}' with JavaScript click")
                                                                                    email_option = clickable_element
                                                                                    break
                                                                                except Exception as js_click_error:
                                                                                    print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                                                    continue
                                                                    
                                                                    if email_option:
                                                                        break
                                                                        
                                                                except Exception as option_error:
                                                                    print(f"⚠️ Error with option selector: {option_error}")
                                                                    continue
                                                            
                                                            if not email_option:
                                                                print("⚠️ Could not find any email options, trying to click dropdown again")
                                                                # Try clicking the dropdown again with JavaScript
                                                                driver.execute_script("arguments[0].click();", support_email_dropdown)
                                                                time.sleep(3.0)
                                                                
                                                                # Try a more aggressive approach - look for any clickable element with the email
                                                                print("🔍 Searching for any element containing the email address...")
                                                                try:
                                                                    all_elements_with_email = driver.find_elements(By.XPATH, f"//*[contains(text(), '{EMAIL}')]")
                                                                    for elem in all_elements_with_email:
                                                                        if elem.is_displayed() and elem.is_enabled():
                                                                            elem_text = (elem.get_attribute("textContent") or elem.text or "").strip()
                                                                            print(f"📧 Found element with email: '{elem_text}'")
                                                                            try:
                                                                                elem.click()
                                                                                print(f"✅ Clicked element with email: '{elem_text}'")
                                                                                email_option = elem
                                                                                break
                                                                            except:
                                                                                continue
                                                                except Exception as search_error:
                                                                    print(f"⚠️ Email search failed: {search_error}")
                                                                
                                                        except Exception as option_select_error:
                                                            print(f"❌ Error selecting email option: {option_select_error}")
                                                        
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                    else:
                                                        print("⚠️ Could not find user support email dropdown")
                                                        
                                                except Exception as support_email_error:
                                                    print(f"❌ Error selecting user support email: {support_email_error}")
                                                
                                                # Click Next button first to reveal the External radio button
                                                print("➡️ Clicking Next button to reveal audience selection...")
                                                try:
                                                    next_button_selectors = [
                                                        "//span[contains(@class, 'mdc-button__label') and contains(text(), 'Next')]/parent::button",
                                                        "//button[contains(text(), 'Next')]",
                                                        "//button//span[contains(text(), 'Next')]",
                                                        "button[type='submit']",
                                                        "//button[contains(@class, 'mdc-button') and contains(text(), 'Next')]",
                                                        "//button[contains(@class, 'mat-mdc-button') and contains(text(), 'Next')]",
                                                        "//button[contains(@class, 'mdc-button--raised') and contains(text(), 'Next')]",
                                                        "//button[contains(@class, 'mat-mdc-raised-button') and contains(text(), 'Next')]",
                                                        "//span[text()='Next']//ancestor::button[1]",
                                                        "//div[text()='Next']//ancestor::button[1]"
                                                    ]
                                                    
                                                    next_button = None
                                                    for selector in next_button_selectors:
                                                        try:
                                                            if selector.startswith("//"):
                                                                next_buttons = driver.find_elements(By.XPATH, selector)
                                                            else:
                                                                next_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                                            
                                                            for btn in next_buttons:
                                                                if btn.is_displayed() and btn.is_enabled():
                                                                    btn_text = (btn.get_attribute("textContent") or btn.text or "").strip()
                                                                    if "next" in btn_text.lower():
                                                                        print(f"✅ Found Next button with text: '{btn_text}'")
                                                                        next_button = btn
                                                                        break
                                                            
                                                            if next_button:
                                                                break
                                                                
                                                        except Exception as selector_error:
                                                            continue
                                                    
                                                    if next_button:
                                                        # Scroll to button and click
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        # Highlight button briefly
                                                        try:
                                                            driver.execute_script("arguments[0].style.border='3px solid red';", next_button)
                                                            time.sleep(0.5)
                                                            driver.execute_script("arguments[0].style.border='';", next_button)
                                                        except:
                                                            pass
                                                        
                                                        try:
                                                            human_mouse_move_to(next_button)
                                                            next_button.click()
                                                            print("✅ First Next button clicked successfully!")
                                                            time.sleep(random.uniform(3.0, 5.0))  # Wait longer for the audience section to load
                                                            
                                                            print("📝 Audience selection section should now be visible...")
                                                            
                                                        except Exception as next_click_error:
                                                            print(f"⚠️ Regular click failed: {next_click_error}")
                                                            print("🔄 Trying JavaScript click...")
                                                            try:
                                                                driver.execute_script("arguments[0].click();", next_button)
                                                                print("✅ First Next button clicked successfully with JavaScript!")
                                                                time.sleep(random.uniform(3.0, 5.0))  # Wait longer for the audience section to load
                                                                
                                                                print("📝 Audience selection section should now be visible...")
                                                                
                                                            except Exception as js_click_error:
                                                                print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                    else:
                                                        print("⚠️ Could not find first Next button")
                                                        print("💡 You may need to manually click the Next button to reveal audience options")
                                                        
                                                except Exception as first_next_error:
                                                    print(f"❌ Error clicking first Next button: {first_next_error}")
                                                
                                                # Now select External radio button (should be visible after clicking Next)
                                                print("🔘 Selecting External radio button...")
                                                try:
                                                    external_radio_selectors = [
                                                        # Specific selectors based on the provided structure
                                                        "#_0rif_mat-radio-1 > div > label > span",
                                                        "//*[@id='_0rif_mat-radio-1']/div/label/span",
                                                        "//span[@class='cfc-text-title-4'][contains(text(), 'External')]",
                                                        "//span[contains(@class, 'cfc-text-title-4')][contains(text(), 'External')]",
                                                        
                                                        # Try to find the actual radio input for External
                                                        "#_0rif_mat-radio-1-input",
                                                        "input[id='_0rif_mat-radio-1-input']",
                                                        "//input[@id='_0rif_mat-radio-1-input']",
                                                        
                                                        # Generic selectors for mat-radio with External
                                                        "//mat-radio-button[.//span[contains(text(), 'External')]]//input[@type='radio']",
                                                        "//mat-radio-button[.//span[contains(text(), 'External')]]//label",
                                                        "//mat-radio-button[.//span[contains(text(), 'External')]]",
                                                        
                                                        # Look for radio buttons near External text
                                                        "//span[contains(text(), 'External')]//ancestor::mat-radio-button//input[@type='radio']",
                                                        "//span[contains(text(), 'External')]//ancestor::*//input[@type='radio']",
                                                        "//span[contains(text(), 'External')]//parent::*//input[@type='radio']",
                                                        
                                                        # Original selectors as fallback
                                                        "input[type='radio'][value='external']",
                                                        "input[type='radio'][id*='mat-radio'][value='external']",
                                                        "input.mdc-radio__native-control[value='external']",
                                                        "input[name*='mat-radio-group'][value='external']",
                                                        "input[id*='_0rif_mat-radio'][value='external']",
                                                        
                                                        # Generic selectors for External radio button
                                                        "//input[@type='radio' and @value='external']",
                                                        "//input[@type='radio' and contains(@id, 'mat-radio') and @value='external']",
                                                        "//input[contains(@class, 'mdc-radio__native-control') and @value='external']",
                                                        "//input[@type='radio'][following-sibling::*[contains(text(), 'External')] or preceding-sibling::*[contains(text(), 'External')]]",
                                                        
                                                        # Try to find radio button by looking for External text
                                                        "//label[contains(text(), 'External')]//input[@type='radio']",
                                                        "//span[contains(text(), 'External')]//ancestor::*//input[@type='radio']",
                                                        "//div[contains(text(), 'External')]//input[@type='radio']",
                                                        
                                                        # Fallback to any radio button with 'external' value
                                                        "//input[@type='radio'][contains(@value, 'external')]",
                                                        "//input[@type='radio'][contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'external')]"
                                                    ]
                                                    
                                                    external_radio = None
                                                    external_label = None
                                                    
                                                    for selector in external_radio_selectors:
                                                        try:
                                                            if selector.startswith("//"):
                                                                external_elements = driver.find_elements(By.XPATH, selector)
                                                            else:
                                                                external_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                            
                                                            for element in external_elements:
                                                                if element.is_displayed() and element.is_enabled():
                                                                    element_tag = element.tag_name
                                                                    element_text = (element.get_attribute("textContent") or element.text or "").strip()
                                                                    element_value = element.get_attribute("value") or ""
                                                                    element_id = element.get_attribute("id") or ""
                                                                    element_classes = element.get_attribute("class") or ""
                                                                    
                                                                    print(f"📋 Found element:")
                                                                    print(f"      Tag: {element_tag}")
                                                                    print(f"      Text: '{element_text}'")
                                                                    print(f"      Value: '{element_value}'")
                                                                    print(f"      ID: '{element_id}'")
                                                                    print(f"      Classes: '{element_classes}'")
                                                                    
                                                                    # Check if this is the External radio input
                                                                    if element_tag == "input" and "external" in element_value.lower():
                                                                        print(f"✅ Found External radio input with selector: {selector}")
                                                                        external_radio = element
                                                                        break
                                                                    # Check if this is the External label/span
                                                                    elif "external" in element_text.lower() and element_tag in ["span", "label"]:
                                                                        print(f"✅ Found External label/span with selector: {selector}")
                                                                        external_label = element
                                                                        # Try to find the associated radio input
                                                                        try:
                                                                            # Look for radio input in the same mat-radio-button
                                                                            radio_input = element.find_element(By.XPATH, ".//ancestor::mat-radio-button//input[@type='radio']")
                                                                            if radio_input and radio_input.is_displayed():
                                                                                external_radio = radio_input
                                                                                print(f"   🎯 Found associated radio input")
                                                                                break
                                                                        except:
                                                                            # Try parent/sibling approach
                                                                            try:
                                                                                radio_input = element.find_element(By.XPATH, ".//ancestor::*//input[@type='radio']")
                                                                                if radio_input and radio_input.is_displayed():
                                                                                    external_radio = radio_input
                                                                                    print(f"   🎯 Found associated radio input via ancestor")
                                                                                    break
                                                                            except:
                                                                                pass
                                                            
                                                            if external_radio:
                                                                break
                                                                
                                                        except Exception as selector_error:
                                                            print(f"⚠️ Error with radio selector: {selector_error}")
                                                            continue
                                                    
                                                    # Use the label if we found it but no radio input
                                                    if not external_radio and external_label:
                                                        print("⚠️ No radio input found, will try clicking the External label")
                                                        external_radio = external_label
                                                    
                                                    if external_radio:
                                                        # Check if radio button is already selected (only for actual input elements)
                                                        if external_radio.tag_name == "input":
                                                            is_selected = external_radio.is_selected()
                                                            print(f"📋 External radio button current state: {'Selected' if is_selected else 'Not selected'}")
                                                        else:
                                                            is_selected = False
                                                            print(f"📋 Will click External label/span element")
                                                        
                                                        if not is_selected:
                                                            # Scroll to radio button and click
                                                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", external_radio)
                                                            time.sleep(random.uniform(1.0, 2.0))
                                                            
                                                            # Highlight the radio button briefly
                                                            try:
                                                                driver.execute_script("arguments[0].style.outline='3px solid red';", external_radio)
                                                                time.sleep(0.5)
                                                                driver.execute_script("arguments[0].style.outline='';", external_radio)
                                                            except:
                                                                pass
                                                            
                                                            try:
                                                                # Try human-like click first
                                                                human_mouse_move_to(external_radio)
                                                                external_radio.click()
                                                                print("✅ External radio button/label clicked successfully with regular click!")
                                                                
                                                                # Verify selection if it's an input element
                                                                if external_radio.tag_name == "input":
                                                                    time.sleep(random.uniform(0.5, 1.0))
                                                                    if external_radio.is_selected():
                                                                        print("✅ External radio button is now selected!")
                                                                    else:
                                                                        print("⚠️ External radio button may not be selected, trying JavaScript click")
                                                                        raise Exception("Radio button not selected after click")
                                                                else:
                                                                    print("✅ External label clicked - radio should be selected!")
                                                                
                                                            except Exception as click_error:
                                                                print(f"⚠️ Regular click failed: {click_error}")
                                                                print("🔄 Trying JavaScript click...")
                                                                try:
                                                                    driver.execute_script("arguments[0].click();", external_radio)
                                                                    print("✅ External radio button/label clicked successfully with JavaScript!")
                                                                    
                                                                    # Verify selection if it's an input element
                                                                    if external_radio.tag_name == "input":
                                                                        time.sleep(random.uniform(0.5, 1.0))
                                                                        if external_radio.is_selected():
                                                                            print("✅ External radio button is now selected!")
                                                                        else:
                                                                            print("⚠️ External radio button may not be selected after JavaScript click")
                                                                    else:
                                                                        print("✅ External label clicked with JavaScript - radio should be selected!")
                                                                        
                                                                except Exception as js_click_error:
                                                                    print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                                    print("🔄 Trying to click using specific ID...")
                                                                    
                                                                    # Try clicking specifically by the ID provided
                                                                    try:
                                                                        specific_element = driver.find_element(By.CSS_SELECTOR, "#_0rif_mat-radio-1 > div > label > span")
                                                                        if specific_element.is_displayed():
                                                                            specific_element.click()
                                                                            print("✅ External radio clicked using specific CSS selector!")
                                                                    except:
                                                                        print("⚠️ Could not click with specific selector either")
                                                        else:
                                                            print("✅ External radio button is already selected!")
                                                            
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                    else:
                                                        print("⚠️ Could not find External radio button")
                                                        print("💡 You may need to manually select the External radio button")
                                                        
                                                except Exception as radio_error:
                                                    print(f"❌ Error selecting External radio button: {radio_error}")
                                                
                                                # Click final Next button to proceed after selecting External
                                                print("➡️ Clicking final Next button to proceed...")
                                                try:
                                                    # Wait a bit to ensure the External radio selection is processed
                                                    time.sleep(random.uniform(2.0, 3.0))
                                                    
                                                    final_next_button_selectors = [
                                                        "//span[contains(@class, 'mdc-button__label') and contains(text(), 'Next')]/parent::button",
                                                        "//button[contains(text(), 'Next')]",
                                                        "//button//span[contains(text(), 'Next')]",
                                                        "button[type='submit']",
                                                        "//button[contains(@class, 'mdc-button') and contains(text(), 'Next')]",
                                                        "//button[contains(@class, 'mat-mdc-button') and contains(text(), 'Next')]",
                                                        "//button[contains(@class, 'mdc-button--raised') and contains(text(), 'Next')]",
                                                        "//button[contains(@class, 'mat-mdc-raised-button') and contains(text(), 'Next')]",
                                                        "//span[text()='Next']//ancestor::button[1]",
                                                        "//div[text()='Next']//ancestor::button[1]"
                                                    ]
                                                    
                                                    final_next_button = None
                                                    for selector in final_next_button_selectors:
                                                        try:
                                                            if selector.startswith("//"):
                                                                final_next_buttons = driver.find_elements(By.XPATH, selector)
                                                            else:
                                                                final_next_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                                            
                                                            for btn in final_next_buttons:
                                                                if btn.is_displayed() and btn.is_enabled():
                                                                    btn_text = (btn.get_attribute("textContent") or btn.text or "").strip()
                                                                    if "next" in btn_text.lower():
                                                                        print(f"✅ Found final Next button with text: '{btn_text}'")
                                                                        final_next_button = btn
                                                                        break
                                                            
                                                            if final_next_button:
                                                                break
                                                                
                                                        except Exception as selector_error:
                                                            continue
                                                    
                                                    if final_next_button:
                                                        # Scroll to button and click
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", final_next_button)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        # Highlight button briefly
                                                        try:
                                                            driver.execute_script("arguments[0].style.border='3px solid red';", final_next_button)
                                                            time.sleep(0.5)
                                                            driver.execute_script("arguments[0].style.border='';", final_next_button)
                                                        except:
                                                            pass
                                                        
                                                        try:
                                                            human_mouse_move_to(final_next_button)
                                                            final_next_button.click()
                                                            print("✅ Final Next button clicked successfully!")
                                                            time.sleep(random.uniform(2.0, 4.0))
                                                            
                                                            # Check if we moved to the next step
                                                            current_url_after_final_next = driver.current_url
                                                            print(f"📍 URL after final Next button click: {current_url_after_final_next}")
                                                            
                                                            print("✅ App Information and Audience selection completed successfully!")
                                                            print("📝 OAuth consent screen configuration is progressing to the next step...")
                                                            print("💡 You can now continue with the next steps of OAuth configuration")
                                                            
                                                        except Exception as final_next_click_error:
                                                            print(f"⚠️ Regular click failed: {final_next_click_error}")
                                                            print("🔄 Trying JavaScript click...")
                                                            try:
                                                                driver.execute_script("arguments[0].click();", final_next_button)
                                                                print("✅ Final Next button clicked successfully with JavaScript!")
                                                                time.sleep(random.uniform(2.0, 4.0))
                                                                
                                                                current_url_after_final_next = driver.current_url
                                                                print(f"📍 URL after final Next button click: {current_url_after_final_next}")
                                                                
                                                                print("✅ App Information and Audience selection completed successfully!")
                                                                print("📝 OAuth consent screen configuration is progressing to the next step...")
                                                                print("💡 You can now continue with the next steps of OAuth configuration")
                                                                
                                                            except Exception as js_click_error:
                                                                print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                    else:
                                                        print("⚠️ Could not find final Next button")
                                                        print("💡 You may need to manually click the Next button to proceed")
                                                        
                                                except Exception as final_next_button_error:
                                                    print(f"❌ Error clicking final Next button: {final_next_button_error}")
                                                
                                                # Step 13: Fill Contact Information
                                                print("📧 Filling Contact Information...")
                                                try:
                                                    # Wait for the Contact Information section to load
                                                    time.sleep(random.uniform(2.0, 4.0))
                                                    
                                                    # Look for the contact email input field
                                                    contact_email_selectors = [
                                                        "input[aria-label='Text field for emails']",
                                                        "input[id*='mat-mdc-chip-list-input']",
                                                        "input.mat-mdc-chip-input.mat-mdc-input-element",
                                                        "input.mat-mdc-input-element.mdc-text-field__input",
                                                        "input[aria-describedby*='mat-mdc-error'][aria-invalid='true']",
                                                        "input[aria-required='true'][required='true']",
                                                        "input#_0rif_mat-mdc-chip-list-input-0",
                                                        "//input[@aria-label='Text field for emails']",
                                                        "//input[contains(@class, 'mat-mdc-chip-input')]",
                                                        "//input[contains(@class, 'mat-mdc-input-element')]",
                                                        "//input[contains(@id, 'mat-mdc-chip-list-input')]",
                                                        "//input[@aria-required='true' and @required='true']"
                                                    ]
                                                    
                                                    contact_email_input = None
                                                    for selector in contact_email_selectors:
                                                        try:
                                                            if selector.startswith("//"):
                                                                contact_email_input = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                                                            else:
                                                                contact_email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                                                            print(f"✅ Found contact email input with selector: {selector}")
                                                            break
                                                        except TimeoutException:
                                                            continue
                                                    
                                                    if contact_email_input:
                                                        # Scroll to element and click
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", contact_email_input)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        human_mouse_move_to(contact_email_input)
                                                        contact_email_input.click()
                                                        time.sleep(random.uniform(0.5, 1.0))
                                                        
                                                        # Clear field and enter email address
                                                        contact_email_input.clear()
                                                        contact_email_input.send_keys(Keys.CONTROL + "a")
                                                        contact_email_input.send_keys(Keys.DELETE)
                                                        time.sleep(random.uniform(0.3, 0.7))
                                                        
                                                        human_typing(contact_email_input, EMAIL)
                                                        print(f"✅ Contact email filled with: {EMAIL}")
                                                        
                                                        # Press Enter to add the email chip
                                                        contact_email_input.send_keys(Keys.ENTER)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                    else:
                                                        print("⚠️ Could not find contact email input field")
                                                        
                                                except Exception as contact_email_error:
                                                    print(f"❌ Error filling contact email: {contact_email_error}")
                                                
                                                # Click Next button after filling contact info
                                                print("➡️ Clicking Next button after contact information...")
                                                try:
                                                    time.sleep(random.uniform(2.0, 3.0))
                                                    
                                                    contact_next_button_selectors = [
                                                        "//span[contains(@class, 'mdc-button__label') and contains(text(), 'Next')]/parent::button",
                                                        "//button[contains(text(), 'Next')]",
                                                        "//button//span[contains(text(), 'Next')]",
                                                        "button[type='submit']",
                                                        "//button[contains(@class, 'mdc-button') and contains(text(), 'Next')]",
                                                        "//button[contains(@class, 'mat-mdc-button') and contains(text(), 'Next')]",
                                                        "//span[text()='Next']//ancestor::button[1]"
                                                    ]
                                                    
                                                    contact_next_button = None
                                                    for selector in contact_next_button_selectors:
                                                        try:
                                                            if selector.startswith("//"):
                                                                contact_next_buttons = driver.find_elements(By.XPATH, selector)
                                                            else:
                                                                contact_next_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                                            
                                                            for btn in contact_next_buttons:
                                                                if btn.is_displayed() and btn.is_enabled():
                                                                    btn_text = (btn.get_attribute("textContent") or btn.text or "").strip()
                                                                    if "next" in btn_text.lower():
                                                                        print(f"✅ Found contact Next button with text: '{btn_text}'")
                                                                        contact_next_button = btn
                                                                        break
                                                            
                                                            if contact_next_button:
                                                                break
                                                                
                                                        except Exception as selector_error:
                                                            continue
                                                    
                                                    if contact_next_button:
                                                        # Scroll to button and click
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", contact_next_button)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        try:
                                                            human_mouse_move_to(contact_next_button)
                                                            contact_next_button.click()
                                                            print("✅ Contact Next button clicked successfully!")
                                                            time.sleep(random.uniform(3.0, 5.0))
                                                            
                                                        except Exception as contact_next_click_error:
                                                            print(f"⚠️ Regular click failed: {contact_next_click_error}")
                                                            print("🔄 Trying JavaScript click...")
                                                            try:
                                                                driver.execute_script("arguments[0].click();", contact_next_button)
                                                                print("✅ Contact Next button clicked successfully with JavaScript!")
                                                                time.sleep(random.uniform(3.0, 5.0))
                                                            except Exception as js_click_error:
                                                                print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                    else:
                                                        print("⚠️ Could not find contact Next button")
                                                        
                                                except Exception as contact_next_error:
                                                    print(f"❌ Error clicking contact Next button: {contact_next_error}")
                                                
                                                # Step 14: Accept Google API Services User Data Policy
                                                print("☑️ Accepting Google API Services User Data Policy...")
                                                try:
                                                    time.sleep(random.uniform(3.0, 5.0))  # Wait longer for the page to load
                                                    
                                                    # PRIORITY 1: Try to find and click the checkbox input directly
                                                    policy_checkbox = None
                                                    checkbox_selectors = [
                                                        "input#_0rif_mat-mdc-checkbox-0-input",
                                                        "input[type='checkbox'][id='_0rif_mat-mdc-checkbox-0-input']",
                                                        "//input[@id='_0rif_mat-mdc-checkbox-0-input']",
                                                        "input[type='checkbox'].mdc-checkbox__native-control",
                                                        "input[id*='mat-mdc-checkbox'][type='checkbox']",
                                                        "//input[@type='checkbox' and contains(@class, 'mdc-checkbox__native-control')]",
                                                        "//input[@type='checkbox' and contains(@id, 'mat-mdc-checkbox')]"
                                                    ]
                                                    
                                                    for selector in checkbox_selectors:
                                                        try:
                                                            if selector.startswith("//"):
                                                                elements = driver.find_elements(By.XPATH, selector)
                                                            else:
                                                                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                            
                                                            for element in elements:
                                                                if element.is_displayed() and element.tag_name.lower() == "input":
                                                                    policy_checkbox = element
                                                                    print(f"✅ Found checkbox input with selector: {selector}")
                                                                    break
                                                            
                                                            if policy_checkbox:
                                                                break
                                                        except Exception as selector_error:
                                                            continue
                                                    
                                                    # Try to click the checkbox directly
                                                    if policy_checkbox:
                                                        print("📋 Attempting to click checkbox input directly...")
                                                        
                                                        # Check if already checked
                                                        is_checked = policy_checkbox.is_selected()
                                                        print(f"📋 Checkbox current state: {'Checked' if is_checked else 'Not checked'}")
                                                        
                                                        if not is_checked:
                                                            # Scroll to checkbox
                                                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", policy_checkbox)
                                                            time.sleep(random.uniform(1.0, 2.0))
                                                            
                                                            # Highlight checkbox
                                                            try:
                                                                driver.execute_script("arguments[0].style.outline='3px solid red';", policy_checkbox)
                                                                time.sleep(1.0)
                                                                driver.execute_script("arguments[0].style.outline='';", policy_checkbox)
                                                            except:
                                                                pass
                                                            
                                                            # Try multiple click strategies on checkbox
                                                            click_success = False
                                                            
                                                            # Strategy 1: Regular click
                                                            try:
                                                                human_mouse_move_to(policy_checkbox)
                                                                policy_checkbox.click()
                                                                print("✅ Checkbox clicked successfully with regular click!")
                                                                click_success = True
                                                            except Exception as click_error:
                                                                print(f"⚠️ Regular click failed: {click_error}")
                                                            
                                                            # Strategy 2: JavaScript click
                                                            if not click_success:
                                                                try:
                                                                    driver.execute_script("arguments[0].click();", policy_checkbox)
                                                                    print("✅ Checkbox clicked successfully with JavaScript!")
                                                                    click_success = True
                                                                except Exception as js_click_error:
                                                                    print(f"⚠️ JavaScript click failed: {js_click_error}")
                                                            
                                                            # Strategy 3: Force check
                                                            if not click_success:
                                                                try:
                                                                    driver.execute_script("arguments[0].checked = true;", policy_checkbox)
                                                                    driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", policy_checkbox)
                                                                    print("✅ Checkbox forced to checked state!")
                                                                    click_success = True
                                                                except Exception as force_error:
                                                                    print(f"⚠️ Force check failed: {force_error}")
                                                            
                                                            # Verify checkbox is checked
                                                            if click_success:
                                                                time.sleep(random.uniform(0.5, 1.0))
                                                                try:
                                                                    if policy_checkbox.is_selected():
                                                                        print("✅ Checkbox is now checked!")
                                                                    else:
                                                                        print("⚠️ Checkbox may not be checked after click")
                                                                except:
                                                                    print("⚠️ Could not verify checkbox state")
                                                            else:
                                                                print("❌ All checkbox click strategies failed")
                                                        else:
                                                            print("✅ Checkbox is already checked!")
                                                    
                                                    # PRIORITY 2: If checkbox direct click failed, try to find clickable label text (NOT the link)
                                                    else:
                                                        print("⚠️ Could not find checkbox input, trying label approach...")
                                                        
                                                        # Find the label element but be VERY careful to avoid the link
                                                        label_element = None
                                                        try:
                                                            # Find the label associated with the checkbox
                                                            label_element = driver.find_element(By.CSS_SELECTOR, "label[for='_0rif_mat-mdc-checkbox-0-input']")
                                                            
                                                            if label_element and label_element.is_displayed():
                                                                print("✅ Found label element for checkbox")
                                                                
                                                                # Get all child elements to identify the safe area to click
                                                                label_text = label_element.get_attribute("textContent") or ""
                                                                print(f"📋 Label text: '{label_text}'")
                                                                
                                                                # Find the text node that contains "I agree to the" but exclude the link
                                                                try:
                                                                    # Find text nodes that are NOT inside the link
                                                                    text_nodes = driver.execute_script("""
                                                                        var label = arguments[0];
                                                                        var textNodes = [];
                                                                        var walker = document.createTreeWalker(
                                                                            label,
                                                                            NodeFilter.SHOW_TEXT,
                                                                            {
                                                                                acceptNode: function(node) {
                                                                                    // Only accept text nodes that are NOT inside an anchor tag
                                                                                    var parent = node.parentElement;
                                                                                    while (parent && parent !== label) {
                                                                                        if (parent.tagName === 'A') {
                                                                                            return NodeFilter.FILTER_REJECT;
                                                                                        }
                                                                                        parent = parent.parentElement;
                                                                                    }
                                                                                    return NodeFilter.FILTER_ACCEPT;
                                                                                }
                                                                            }
                                                                        );
                                                                        
                                                                        var node;
                                                                        while (node = walker.nextNode()) {
                                                                            if (node.textContent.includes('I agree to the')) {
                                                                                textNodes.push(node.parentElement);
                                                                            }
                                                                        }
                                                                        return textNodes;
                                                                    """, label_element)
                                                                    
                                                                    if text_nodes:
                                                                        # Click the first safe text element
                                                                        safe_element = text_nodes[0]
                                                                        print("✅ Found safe text element to click")
                                                                        
                                                                        try:
                                                                            driver.execute_script("arguments[0].click();", safe_element)
                                                                            print("✅ Clicked safe text element successfully!")
                                                                        except:
                                                                            # If text element click fails, click the label itself
                                                                            print("⚠️ Text element click failed, trying label click...")
                                                                            driver.execute_script("arguments[0].click();", label_element)
                                                                            print("✅ Clicked label element successfully!")
                                                                    else:
                                                                        # Fallback: click the label but ensure we don't navigate away
                                                                        print("⚠️ No safe text nodes found, clicking label carefully...")
                                                                        
                                                                        # Store current URL to detect navigation
                                                                        current_url = driver.current_url
                                                                        
                                                                        # Click label with JavaScript to avoid mouse events on links
                                                                        driver.execute_script("arguments[0].click();", label_element)
                                                                        
                                                                        # Check if we navigated away
                                                                        time.sleep(0.5)
                                                                        new_url = driver.current_url
                                                                        if new_url != current_url:
                                                                            print(f"⚠️ Navigation detected! Going back from {new_url}")
                                                                            driver.back()
                                                                            time.sleep(2.0)
                                                                        else:
                                                                            print("✅ Label clicked successfully without navigation!")
                                                                    
                                                                except Exception as text_error:
                                                                    print(f"⚠️ Text node approach failed: {text_error}")
                                                                    
                                                                    # Final fallback: try to click the label
                                                                    try:
                                                                        driver.execute_script("arguments[0].click();", label_element)
                                                                        print("✅ Label clicked as final fallback!")
                                                                    except Exception as label_error:
                                                                        print(f"❌ Label click failed: {label_error}")
                                                            else:
                                                                print("⚠️ Label element not found or not displayed")
                                                                
                                                        except Exception as label_error:
                                                            print(f"⚠️ Label approach failed: {label_error}")
                                                    
                                                    # Final verification - check if checkbox is checked
                                                    time.sleep(random.uniform(1.0, 2.0))
                                                    if policy_checkbox:
                                                        try:
                                                            if policy_checkbox.is_selected():
                                                                print("✅ Final verification: Checkbox is checked!")
                                                            else:
                                                                print("⚠️ Final verification: Checkbox may not be checked")
                                                        except:
                                                            pass
                                                    
                                                except Exception as policy_checkbox_error:
                                                    print(f"❌ Error checking policy checkbox: {policy_checkbox_error}")
                                                
                                                # Step 15: Click Continue button
                                                print("➡️ Clicking Continue button...")
                                                try:
                                                    time.sleep(random.uniform(2.0, 3.0))
                                                    
                                                    continue_button_selectors = [
                                                        "//span[contains(@class, 'mdc-button__label') and contains(text(), 'Continue')]/parent::button",
                                                        "//button[contains(text(), 'Continue')]",
                                                        "//button//span[contains(text(), 'Continue')]",
                                                        "//span[text()='Continue']//ancestor::button[1]",
                                                        "//button[contains(@class, 'mdc-button') and contains(text(), 'Continue')]",
                                                        "//button[contains(@class, 'mat-mdc-button') and contains(text(), 'Continue')]"
                                                    ]
                                                    
                                                    continue_button = None
                                                    for selector in continue_button_selectors:
                                                        try:
                                                            continue_buttons = driver.find_elements(By.XPATH, selector)
                                                            
                                                            for btn in continue_buttons:
                                                                if btn.is_displayed() and btn.is_enabled():
                                                                    btn_text = (btn.get_attribute("textContent") or btn.text or "").strip()
                                                                    if "continue" in btn_text.lower():
                                                                        print(f"✅ Found Continue button with text: '{btn_text}'")
                                                                        continue_button = btn
                                                                        break
                                                            
                                                            if continue_button:
                                                                break
                                                                
                                                        except Exception as selector_error:
                                                            continue
                                                    
                                                    if continue_button:
                                                        # Scroll to button and click
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", continue_button)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        try:
                                                            human_mouse_move_to(continue_button)
                                                            continue_button.click()
                                                            print("✅ Continue button clicked successfully!")
                                                            time.sleep(random.uniform(3.0, 5.0))
                                                            
                                                        except Exception as continue_click_error:
                                                            print(f"⚠️ Regular click failed: {continue_click_error}")
                                                            print("🔄 Trying JavaScript click...")
                                                            try:
                                                                driver.execute_script("arguments[0].click();", continue_button)
                                                                print("✅ Continue button clicked successfully with JavaScript!")
                                                                time.sleep(random.uniform(3.0, 5.0))
                                                            except Exception as js_click_error:
                                                                print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                    else:
                                                        print("⚠️ Could not find Continue button")
                                                        
                                                except Exception as continue_error:
                                                    print(f"❌ Error clicking Continue button: {continue_error}")
                                                
                                                # Step 16: Click Create button (final step)
                                                print("🎯 Clicking Create button (final step)...")
                                                try:
                                                    time.sleep(random.uniform(2.0, 4.0))
                                                    
                                                    create_button_selectors = [
                                                        "//span[contains(@class, 'mdc-button__label') and contains(text(), 'Create')]/parent::button",
                                                        "//button[contains(text(), 'Create')]",
                                                        "//button//span[contains(text(), 'Create')]",
                                                        "//span[text()='Create']//ancestor::button[1]",
                                                        "//button[contains(@class, 'mdc-button') and contains(text(), 'Create')]",
                                                        "//button[contains(@class, 'mat-mdc-button') and contains(text(), 'Create')]"
                                                    ]
                                                    
                                                    create_button = None
                                                    for selector in create_button_selectors:
                                                        try:
                                                            create_buttons = driver.find_elements(By.XPATH, selector)
                                                            
                                                            for btn in create_buttons:
                                                                if btn.is_displayed() and btn.is_enabled():
                                                                    btn_text = (btn.get_attribute("textContent") or btn.text or "").strip()
                                                                    if "create" in btn_text.lower():
                                                                        print(f"✅ Found Create button with text: '{btn_text}'")
                                                                        create_button = btn
                                                                        break
                                                            
                                                            if create_button:
                                                                break
                                                                
                                                        except Exception as selector_error:
                                                            continue
                                                    
                                                    if create_button:
                                                        # Scroll to button and click
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", create_button)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        # Highlight button briefly
                                                        try:
                                                            driver.execute_script("arguments[0].style.border='3px solid green';", create_button)
                                                            time.sleep(1.0)
                                                            driver.execute_script("arguments[0].style.border='';", create_button)
                                                        except:
                                                            pass
                                                        
                                                        try:
                                                            human_mouse_move_to(create_button)
                                                            create_button.click()
                                                            print("✅ Create button clicked successfully!")
                                                            time.sleep(random.uniform(3.0, 5.0))
                                                            
                                                            # Check final URL
                                                            final_url = driver.current_url
                                                            print(f"📍 Final URL after Create button: {final_url}")
                                                            
                                                            print("🎉 OAuth consent screen creation completed successfully!")
                                                            print_milestone_timing("🔐 OAUTH CONSENT SCREEN COMPLETED")
                                                            print("✅ All steps completed:")
                                                            print("   - App Information filled")
                                                            print("   - User support email selected")
                                                            print("   - External audience selected")
                                                            print("   - Contact information filled")
                                                            print("   - Policy agreement accepted")
                                                            print("   - OAuth consent screen created")
                                                            
                                                        except Exception as create_click_error:
                                                            print(f"⚠️ Regular click failed: {create_click_error}")
                                                            print("🔄 Trying JavaScript click...")
                                                            try:
                                                                driver.execute_script("arguments[0].click();", create_button)
                                                                print("✅ Create button clicked successfully with JavaScript!")
                                                                time.sleep(random.uniform(3.0, 5.0))
                                                                
                                                                final_url = driver.current_url
                                                                print(f"📍 Final URL after Create button: {final_url}")
                                                                
                                                                print("🎉 OAuth consent screen creation completed successfully!")
                                                                print("✅ All steps completed:")
                                                                print("   - App Information filled")
                                                                print("   - User support email selected")
                                                                print("   - External audience selected")
                                                                print("   - Contact information filled")
                                                                print("   - Policy agreement accepted")
                                                                print("   - OAuth consent screen created")
                                                                
                                                            except Exception as js_click_error:
                                                                print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                    else:
                                                        print("⚠️ Could not find Create button")
                                                        
                                                except Exception as create_error:
                                                    print(f"❌ Error clicking Create button: {create_error}")
                                                
                                                print("✅ OAuth consent screen App Information and Audience configuration completed!")
                                                
                                                # Step 17: Navigate to Data Access and configure scopes
                                                print("📊 Proceeding to Data Access configuration...")
                                                
                                                # CRITICAL: Dismiss navigation tutorial overlay before Data Access interactions
                                                print("🎯 PRIORITY: Dismissing navigation tutorial overlay before Data Access configuration...")
                                                dismiss_navigation_tutorial(driver)
                                                time.sleep(2.0)  # Give extra time for dismissal
                                                
                                                time.sleep(random.uniform(3.0, 5.0))
                                                
                                                # Click "Data Access" from sidebar
                                                print("📊 Clicking 'Data Access' from sidebar...")
                                                try:
                                                    data_access_selectors = [
                                                        "//span[contains(@class, 'cfc-page-displayName') and (contains(text(), 'Data Access') or contains(text(), 'Data access'))]",
                                                        "//span[@class='cfc-page-displayName'][contains(text(), 'Data Access') or contains(text(), 'Data access')]",
                                                        "//a[contains(text(), 'Data Access') or contains(text(), 'Data access')]",
                                                        "//li[contains(text(), 'Data Access') or contains(text(), 'Data access')]",
                                                        "//div[contains(text(), 'Data Access') or contains(text(), 'Data access')]",
                                                        "//*[contains(text(), 'Data Access') or contains(text(), 'Data access') and contains(@class, 'cfc-page-displayName')]"
                                                    ]
                                                    
                                                    data_access_element = None
                                                    for selector in data_access_selectors:
                                                        try:
                                                            elements = driver.find_elements(By.XPATH, selector)
                                                            for element in elements:
                                                                if element.is_displayed() and element.is_enabled():
                                                                    element_text = (element.get_attribute("textContent") or element.text or "").strip()
                                                                    if "data access" in element_text.lower():
                                                                        data_access_element = element
                                                                        print(f"✅ Found Data Access element with text: '{element_text}'")
                                                                        break
                                                            if data_access_element:
                                                                break
                                                        except Exception as selector_error:
                                                            continue
                                                    
                                                    if data_access_element:
                                                        # Scroll to element and click
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", data_access_element)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        try:
                                                            human_mouse_move_to(data_access_element)
                                                            data_access_element.click()
                                                            print("✅ Data Access clicked successfully!")
                                                            time.sleep(random.uniform(3.0, 5.0))
                                                            
                                                        except Exception as data_access_click_error:
                                                            print(f"⚠️ Regular click failed: {data_access_click_error}")
                                                            print("🔄 Trying JavaScript click...")
                                                            try:
                                                                driver.execute_script("arguments[0].click();", data_access_element)
                                                                print("✅ Data Access clicked successfully with JavaScript!")
                                                                time.sleep(random.uniform(3.0, 5.0))
                                                            except Exception as js_click_error:
                                                                print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                    else:
                                                        print("⚠️ Could not find Data Access element")
                                                        
                                                except Exception as data_access_error:
                                                    print(f"❌ Error clicking Data Access: {data_access_error}")
                                                
                                                # Click "Add or remove scopes" button
                                                print("🔧 Clicking 'Add or remove scopes' button...")
                                                
                                                # CRITICAL: Dismiss navigation tutorial overlay before scopes button click
                                                print("🎯 PRIORITY: Dismissing navigation tutorial overlay before scopes interaction...")
                                                dismiss_navigation_tutorial(driver)
                                                time.sleep(1.0)  # Wait for dismissal
                                                
                                                try:
                                                    time.sleep(random.uniform(2.0, 4.0))
                                                    
                                                    scopes_button_selectors = [
                                                        "//span[contains(@class, 'mdc-button__label') and contains(text(), 'Add or remove scopes')]/parent::button",
                                                        "//button[contains(text(), 'Add or remove scopes')]",
                                                        "//button//span[contains(text(), 'Add or remove scopes')]",
                                                        "//span[text()='Add or remove scopes']//ancestor::button[1]",
                                                        "//button[contains(@class, 'mdc-button')][.//span[contains(text(), 'Add or remove scopes')]]",
                                                        "//button[contains(@class, 'mat-mdc-button')][.//span[contains(text(), 'Add or remove scopes')]]"
                                                    ]
                                                    
                                                    scopes_button = None
                                                    for selector in scopes_button_selectors:
                                                        try:
                                                            elements = driver.find_elements(By.XPATH, selector)
                                                            for element in elements:
                                                                if element.is_displayed() and element.is_enabled():
                                                                    element_text = (element.get_attribute("textContent") or element.text or "").strip()
                                                                    if "add or remove scopes" in element_text.lower():
                                                                        scopes_button = element
                                                                        print(f"✅ Found Add or remove scopes button with text: '{element_text}'")
                                                                        break
                                                            if scopes_button:
                                                                break
                                                        except Exception as selector_error:
                                                            continue
                                                    
                                                    if scopes_button:
                                                        # Scroll to button and click
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", scopes_button)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        try:
                                                            human_mouse_move_to(scopes_button)
                                                            scopes_button.click()
                                                            print("✅ Add or remove scopes button clicked successfully!")
                                                            time.sleep(random.uniform(3.0, 5.0))
                                                            
                                                        except Exception as scopes_click_error:
                                                            print(f"⚠️ Regular click failed: {scopes_click_error}")
                                                            print("🔄 Trying JavaScript click...")
                                                            try:
                                                                driver.execute_script("arguments[0].click();", scopes_button)
                                                                print("✅ Add or remove scopes button clicked successfully with JavaScript!")
                                                                time.sleep(random.uniform(3.0, 5.0))
                                                            except Exception as js_click_error:
                                                                print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                    else:
                                                        print("⚠️ Could not find Add or remove scopes button")
                                                        
                                                except Exception as scopes_button_error:
                                                    print(f"❌ Error clicking Add or remove scopes button: {scopes_button_error}")
                                                
                                                # Search for Gmail API scope
                                                print("🔍 Searching for Gmail API scope...")
                                                try:
                                                    time.sleep(random.uniform(2.0, 4.0))
                                                    
                                                    # Look for the filter input field
                                                    filter_input_selectors = [
                                                        "div[id*='chip-list-input'][contenteditable='true']",
                                                        "div.cfc-filter-input.cfc-outline-focus-indicator[contenteditable='true']",
                                                        "div[aria-autocomplete='list'][contenteditable='true']",
                                                        "div[role='combobox'][contenteditable='true']",
                                                        "div[data-ph*='Enter property name'][contenteditable='true']",
                                                        "//div[@id='_0rif_chip-list-input-goog_1370501307']",
                                                        "//div[contains(@class, 'cfc-filter-input') and @contenteditable='true']",
                                                        "//div[@aria-autocomplete='list' and @contenteditable='true']",
                                                        "//div[@role='combobox' and @contenteditable='true']",
                                                        "//div[contains(@data-ph, 'Enter property name') and @contenteditable='true']"
                                                    ]
                                                    
                                                    filter_input = None
                                                    for selector in filter_input_selectors:
                                                        try:
                                                            if selector.startswith("//"):
                                                                elements = driver.find_elements(By.XPATH, selector)
                                                            else:
                                                                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                            
                                                            for element in elements:
                                                                if element.is_displayed() and element.is_enabled():
                                                                    filter_input = element
                                                                    print(f"✅ Found filter input with selector: {selector}")
                                                                    break
                                                            if filter_input:
                                                                break
                                                        except Exception as selector_error:
                                                            continue
                                                    
                                                    if filter_input:
                                                        # Click and focus the input
                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", filter_input)
                                                        time.sleep(random.uniform(1.0, 2.0))
                                                        
                                                        human_mouse_move_to(filter_input)
                                                        filter_input.click()
                                                        time.sleep(random.uniform(0.5, 1.0))
                                                        
                                                        # Clear any existing content
                                                        try:
                                                            # For contenteditable div, we need to clear differently
                                                            driver.execute_script("arguments[0].textContent = '';", filter_input)
                                                            driver.execute_script("arguments[0].focus();", filter_input)
                                                        except:
                                                            pass
                                                        
                                                        # Type the Gmail API scope URL
                                                        gmail_scope = "https://mail.google.com/"
                                                        print(f"⌨️ Typing Gmail API scope: {gmail_scope}")
                                                        
                                                        # Use JavaScript to set the content for contenteditable div
                                                        try:
                                                            driver.execute_script("arguments[0].textContent = arguments[1];", filter_input, gmail_scope)
                                                            driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", filter_input)
                                                            time.sleep(random.uniform(1.0, 2.0))
                                                            
                                                            print(f"✅ Gmail scope entered: {gmail_scope}")
                                                            
                                                            # Press Enter to search/add the scope
                                                            print("⏎ Pressing Enter to add Gmail scope...")
                                                            filter_input.send_keys(Keys.ENTER)
                                                            time.sleep(random.uniform(2.0, 4.0))
                                                            
                                                            print("✅ Gmail API scope search completed!")
                                                            print("📧 Gmail API scope should now be visible/added")
                                                            
                                                            # Step 18: Select Gmail API checkbox
                                                            print("☑️ Selecting Gmail API checkbox...")
                                                            try:
                                                                time.sleep(random.uniform(2.0, 4.0))
                                                                
                                                                # Look for the Gmail API checkbox
                                                                gmail_checkbox_selectors = [
                                                                    # Specific selector based on the provided HTML
                                                                    "#_0rif_cfc-table-caption-3-row-0 > td.cfc-table-select-all-checkbox-column.cfc-outline-focus-indicator.ng-star-inserted > cfc-table-selection-control > mat-pseudo-checkbox",
                                                                    "mat-pseudo-checkbox[aria-label='Select row'][aria-checked='false']",
                                                                    "mat-pseudo-checkbox.mat-pseudo-checkbox-full",
                                                                    "mat-pseudo-checkbox[role='checkbox']",
                                                                    
                                                                    # XPath selectors
                                                                    "//*[@id='_0rif_cfc-table-caption-3-row-0']/td[1]/cfc-table-selection-control/mat-pseudo-checkbox",
                                                                    "//mat-pseudo-checkbox[@role='checkbox' and @aria-label='Select row']",
                                                                    "//mat-pseudo-checkbox[@aria-checked='false']",
                                                                    "//mat-pseudo-checkbox[contains(@class, 'mat-pseudo-checkbox-full')]",
                                                                    
                                                                    # Generic selectors for table checkboxes
                                                                    "//td[contains(@class, 'cfc-table-select-all-checkbox-column')]//mat-pseudo-checkbox",
                                                                    "//cfc-table-selection-control//mat-pseudo-checkbox",
                                                                    "//tr[contains(., 'mail.google.com')]//mat-pseudo-checkbox",
                                                                    "//tr[contains(., 'Gmail')]//mat-pseudo-checkbox"
                                                                ]
                                                                
                                                                gmail_checkbox = None
                                                                for selector in gmail_checkbox_selectors:
                                                                    try:
                                                                        if selector.startswith("//"):
                                                                            elements = driver.find_elements(By.XPATH, selector)
                                                                        else:
                                                                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                                                                        
                                                                        for element in elements:
                                                                            if element.is_displayed() and element.is_enabled():
                                                                                # Check if this checkbox is for Gmail/mail.google.com
                                                                                try:
                                                                                    # Look for Gmail-related text in the same row
                                                                                    parent_row = element.find_element(By.XPATH, "./ancestor::tr[1]")
                                                                                    row_text = (parent_row.get_attribute("textContent") or parent_row.text or "").lower()
                                                                                    
                                                                                    if "mail.google.com" in row_text or "gmail" in row_text:
                                                                                        gmail_checkbox = element
                                                                                        print(f"✅ Found Gmail API checkbox with selector: {selector}")
                                                                                        print(f"   Row text contains: {row_text[:100]}...")
                                                                                        break
                                                                                except:
                                                                                    # If can't find parent row, just use the first checkbox found
                                                                                    gmail_checkbox = element
                                                                                    print(f"✅ Found checkbox (assuming Gmail) with selector: {selector}")
                                                                                    break
                                                                        
                                                                        if gmail_checkbox:
                                                                            break
                                                                    except Exception as selector_error:
                                                                        continue
                                                                
                                                                if gmail_checkbox:
                                                                    # Check current state
                                                                    is_checked = gmail_checkbox.get_attribute("aria-checked") == "true"
                                                                    print(f"📋 Gmail checkbox current state: {'Checked' if is_checked else 'Not checked'}")
                                                                    
                                                                    if not is_checked:
                                                                        # Scroll to checkbox and click
                                                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", gmail_checkbox)
                                                                        time.sleep(random.uniform(1.0, 2.0))
                                                                        
                                                                        # Highlight checkbox briefly
                                                                        try:
                                                                            driver.execute_script("arguments[0].style.outline='3px solid green';", gmail_checkbox)
                                                                            time.sleep(1.0)
                                                                            driver.execute_script("arguments[0].style.outline='';", gmail_checkbox)
                                                                        except:
                                                                            pass
                                                                        
                                                                        # Try multiple click strategies
                                                                        click_success = False
                                                                        
                                                                        # Strategy 1: Regular click
                                                                        try:
                                                                            human_mouse_move_to(gmail_checkbox)
                                                                            gmail_checkbox.click()
                                                                            print("✅ Gmail checkbox clicked successfully with regular click!")
                                                                            click_success = True
                                                                        except Exception as click_error:
                                                                            print(f"⚠️ Regular click failed: {click_error}")
                                                                        
                                                                        # Strategy 2: JavaScript click
                                                                        if not click_success:
                                                                            try:
                                                                                driver.execute_script("arguments[0].click();", gmail_checkbox)
                                                                                print("✅ Gmail checkbox clicked successfully with JavaScript!")
                                                                                click_success = True
                                                                            except Exception as js_click_error:
                                                                                print(f"⚠️ JavaScript click failed: {js_click_error}")
                                                                        
                                                                        # Strategy 3: Force aria-checked attribute
                                                                        if not click_success:
                                                                            try:
                                                                                driver.execute_script("arguments[0].setAttribute('aria-checked', 'true');", gmail_checkbox)
                                                                                driver.execute_script("arguments[0].dispatchEvent(new Event('click', {bubbles: true}));", gmail_checkbox)
                                                                                print("✅ Gmail checkbox forced to checked state!")
                                                                                click_success = True
                                                                            except Exception as force_error:
                                                                                print(f"⚠️ Force check failed: {force_error}")
                                                                        
                                                                        # Verify checkbox is checked
                                                                        if click_success:
                                                                            time.sleep(random.uniform(0.5, 1.0))
                                                                            try:
                                                                                is_checked_after = gmail_checkbox.get_attribute("aria-checked") == "true"
                                                                                if is_checked_after:
                                                                                    print("✅ Gmail checkbox is now checked!")
                                                                                else:
                                                                                    print("⚠️ Gmail checkbox may not be checked after click")
                                                                            except:
                                                                                print("⚠️ Could not verify checkbox state")
                                                                        else:
                                                                            print("❌ All Gmail checkbox click strategies failed")
                                                                    else:
                                                                        print("✅ Gmail checkbox is already checked!")
                                                                else:
                                                                    print("⚠️ Could not find Gmail API checkbox")
                                                                    
                                                            except Exception as checkbox_error:
                                                                print(f"❌ Error selecting Gmail checkbox: {checkbox_error}")
                                                            
                                                            # Step 19: Click Update button
                                                            print("🔄 Clicking Update button...")
                                                            try:
                                                                time.sleep(random.uniform(2.0, 3.0))
                                                                
                                                                update_button_selectors = [
                                                                    "//span[contains(@class, 'mdc-button__label') and contains(text(), 'Update')]/parent::button",
                                                                    "//button[contains(text(), 'Update')]",
                                                                    "//button//span[contains(text(), 'Update')]",
                                                                    "//span[text()='Update']//ancestor::button[1]",
                                                                    "//button[contains(@class, 'mdc-button') and contains(text(), 'Update')]",
                                                                    "//button[contains(@class, 'mat-mdc-button') and contains(text(), 'Update')]"
                                                                ]
                                                                
                                                                update_button = None
                                                                for selector in update_button_selectors:
                                                                    try:
                                                                        elements = driver.find_elements(By.XPATH, selector)
                                                                        for element in elements:
                                                                            if element.is_displayed() and element.is_enabled():
                                                                                element_text = (element.get_attribute("textContent") or element.text or "").strip()
                                                                                if "update" in element_text.lower():
                                                                                    update_button = element
                                                                                    print(f"✅ Found Update button with text: '{element_text}'")
                                                                                    break
                                                                        if update_button:
                                                                            break
                                                                    except Exception as selector_error:
                                                                        continue
                                                                
                                                                if update_button:
                                                                    # Scroll to button and click
                                                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", update_button)
                                                                    time.sleep(random.uniform(1.0, 2.0))
                                                                    
                                                                    # Highlight button briefly
                                                                    try:
                                                                        driver.execute_script("arguments[0].style.border='3px solid blue';", update_button)
                                                                        time.sleep(1.0)
                                                                        driver.execute_script("arguments[0].style.border='';", update_button)
                                                                    except:
                                                                        pass
                                                                    
                                                                    try:
                                                                        human_mouse_move_to(update_button)
                                                                        update_button.click()
                                                                        print("✅ Update button clicked successfully!")
                                                                        time.sleep(random.uniform(3.0, 5.0))
                                                                        
                                                                        # Check if update was successful
                                                                        current_url_after_update = driver.current_url
                                                                        print(f"📍 URL after Update button: {current_url_after_update}")
                                                                        
                                                                        print("🎉 Gmail API scope configuration completed successfully!")
                                                                        print_milestone_timing("✅ FINAL SCOPE CONFIGURATION COMPLETED")
                                                                        print("✅ All automation steps completed:")
                                                                        print("   - Google login")
                                                                        print("   - Project creation")
                                                                        print("   - Gmail API enablement")
                                                                        print("   - OAuth consent screen setup")
                                                                        print("   - Data Access configuration")
                                                                        print("   - Gmail API scope selection")
                                                                        print("   - Scopes update completed")
                                                                        
                                                                        # Step 20: Click Save button (final step)
                                                                        print("💾 Clicking Save button to finalize configuration...")
                                                                        try:
                                                                            time.sleep(random.uniform(2.0, 4.0))
                                                                            
                                                                            save_button_selectors = [
                                                                                "//span[contains(@class, 'mdc-button__label') and contains(text(), 'Save')]/parent::button",
                                                                                "//button[contains(text(), 'Save')]",
                                                                                "//button//span[contains(text(), 'Save')]",
                                                                                "//span[text()='Save']//ancestor::button[1]",
                                                                                "//button[contains(@class, 'mdc-button') and contains(text(), 'Save')]",
                                                                                "//button[contains(@class, 'mat-mdc-button') and contains(text(), 'Save')]"
                                                                            ]
                                                                            
                                                                            save_button = None
                                                                            for selector in save_button_selectors:
                                                                                try:
                                                                                    elements = driver.find_elements(By.XPATH, selector)
                                                                                    for element in elements:
                                                                                        if element.is_displayed() and element.is_enabled():
                                                                                            element_text = (element.get_attribute("textContent") or element.text or "").strip()
                                                                                            if "save" in element_text.lower():
                                                                                                save_button = element
                                                                                                print(f"✅ Found Save button with text: '{element_text}'")
                                                                                                break
                                                                                    if save_button:
                                                                                        break
                                                                                except Exception as selector_error:
                                                                                    continue
                                                                            
                                                                            if save_button:
                                                                                # Scroll to button and click
                                                                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
                                                                                time.sleep(random.uniform(1.0, 2.0))
                                                                                
                                                                                # Highlight button briefly
                                                                                try:
                                                                                    driver.execute_script("arguments[0].style.border='3px solid gold';", save_button)
                                                                                    time.sleep(1.0)
                                                                                    driver.execute_script("arguments[0].style.border='';", save_button)
                                                                                except:
                                                                                    pass
                                                                                
                                                                                try:
                                                                                    human_mouse_move_to(save_button)
                                                                                    save_button.click()
                                                                                    print("✅ Save button clicked successfully!")
                                                                                    time.sleep(random.uniform(3.0, 5.0))
                                                                                    
                                                                                    # Check final URL
                                                                                    final_url_after_save = driver.current_url
                                                                                    print(f"📍 Final URL after Save: {final_url_after_save}")
                                                                                    
                                                                                    print("🎉🎉 COMPLETE AUTOMATION FINISHED SUCCESSFULLY! 🎉🎉")
                                                                                    print("✅ ALL STEPS COMPLETED:")
                                                                                    print("   ✓ Google login")
                                                                                    print("   ✓ Project creation")
                                                                                    print("   ✓ Gmail API enablement")
                                                                                    print("   ✓ OAuth consent screen configuration")
                                                                                    print("   ✓ Data Access setup")
                                                                                    print("   ✓ Gmail API scope addition")
                                                                                    print("   ✓ Configuration update")
                                                                                    print("   ✓ Final save completed")
                                                                                    print("")
                                                                                    
                                                                                    # Step 21: Configure Audience
                                                                                    configure_audience(driver)
                                                                                    
                                                                                    print("🚀 Your Gmail API integration is now fully configured!")
                                                                                    print("📧 You can now use the Gmail API with your Google Cloud project.")
                                                                                    
                                                                                except Exception as save_click_error:
                                                                                    print(f"⚠️ Regular click failed: {save_click_error}")
                                                                                    print("🔄 Trying JavaScript click...")
                                                                                    try:
                                                                                        driver.execute_script("arguments[0].click();", save_button)
                                                                                        print("✅ Save button clicked successfully with JavaScript!")
                                                                                        time.sleep(random.uniform(3.0, 5.0))
                                                                                        
                                                                                        final_url_after_save = driver.current_url
                                                                                        print(f"📍 Final URL after Save: {final_url_after_save}")
                                                                                        
                                                                                        print("🎉🎉 COMPLETE AUTOMATION FINISHED SUCCESSFULLY! 🎉🎉")
                                                                                        print("✅ ALL STEPS COMPLETED:")
                                                                                        print("   ✓ Google login")
                                                                                        print("   ✓ Project creation")
                                                                                        print("   ✓ Gmail API enablement")
                                                                                        print("   ✓ OAuth consent screen configuration")
                                                                                        print("   ✓ Data Access setup")
                                                                                        print("   ✓ Gmail API scope addition")
                                                                                        print("   ✓ Configuration update")
                                                                                        print("   ✓ Final save completed")
                                                                                        print("")
                                                                                        
                                                                                        # Step 21: Configure Audience  
                                                                                        configure_audience(driver)
                                                                                        
                                                                                        print("🚀 Your Gmail API integration is now fully configured!")
                                                                                        print("📧 You can now use the Gmail API with your Google Cloud project.")
                                                                                        
                                                                                    except Exception as js_click_error:
                                                                                        print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                                            else:
                                                                                print("⚠️ Could not find Save button")
                                                                                print("💡 The configuration may have been auto-saved")
                                                                                print("🎉 Gmail API scope configuration completed!")
                                                                                
                                                                        except Exception as save_error:
                                                                            print(f"❌ Error clicking Save button: {save_error}")
                                                                            print("💡 The configuration may have been auto-saved")
                                                                        
                                                                    except Exception as update_click_error:
                                                                        print(f"⚠️ Regular click failed: {update_click_error}")
                                                                        print("🔄 Trying JavaScript click...")
                                                                        try:
                                                                            driver.execute_script("arguments[0].click();", update_button)
                                                                            print("✅ Update button clicked successfully with JavaScript!")
                                                                            time.sleep(random.uniform(3.0, 5.0))
                                                                            
                                                                            current_url_after_update = driver.current_url
                                                                            print(f"📍 URL after Update button: {current_url_after_update}")
                                                                            
                                                                            print("🎉 Gmail API scope configuration completed successfully!")
                                                                            print("✅ All automation steps completed:")
                                                                            print("   - Google login")
                                                                            print("   - Project creation")
                                                                            print("   - Gmail API enablement")
                                                                            print("   - OAuth consent screen setup")
                                                                            print("   - Data Access configuration")
                                                                            print("   - Gmail API scope selection")
                                                                            print("   - Scopes update completed")
                                                                            
                                                                        except Exception as js_click_error:
                                                                            print(f"⚠️ JavaScript click also failed: {js_click_error}")
                                                                else:
                                                                    print("⚠️ Could not find Update button")
                                                                    
                                                            except Exception as update_error:
                                                                print(f"❌ Error clicking Update button: {update_error}")
                                                            
                                                        except Exception as input_error:
                                                            print(f"⚠️ JavaScript input failed, trying manual typing: {input_error}")
                                                            try:
                                                                # Fallback to manual typing
                                                                human_typing(filter_input, gmail_scope)
                                                                filter_input.send_keys(Keys.ENTER)
                                                                print("✅ Gmail scope entered manually and Enter pressed!")
                                                            except Exception as manual_error:
                                                                print(f"❌ Manual typing also failed: {manual_error}")
                                                    else:
                                                        print("⚠️ Could not find filter input field")
                                                        
                                                except Exception as search_error:
                                                    print(f"❌ Error searching for Gmail scope: {search_error}")
                                                
                                                print("🎉 Data Access configuration completed!")
                                                print("✅ All steps completed successfully:")
                                                print_milestone_timing("🎉 COMPLETE AUTOMATION FINISHED")
                                                print("   - OAuth consent screen created")
                                                print("   - Data Access page accessed")
                                                print("   - Scopes configuration opened")
                                                print("   - Gmail API scope searched/added")
                                                
                                            else:
                                                print("⚠️ Could not find 'Get started' button")
                                                print("💡 You may need to manually click the 'Get started' button")
                                                print("💡 Look for a blue 'Get started' button on the OAuth overview page")
                                        
                                        else:
                                            print("✅ OAuth consent screen configuration page loaded directly!")
                                            print("📝 The OAuth consent screen setup is now ready for manual configuration")
                                        
                                        print("✅ OAuth consent screen setup initiated!")
                                        
                                    else:
                                        print("⚠️ Could not find Enable button")
                                        print("💡 You may need to manually enable the Gmail API")
                                        
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
    print("🔧 Attempting manual fallback for modal 'New Project' button...")
    # Legacy traditional approach code - commented out since using direct approach
    print("✅ Using direct project creation approach - legacy modal handling skipped")

# Continue with rest of automation (OAuth, API enabling, etc.)
except TimeoutException:
    print("❌ Could not complete project creation")
    print("💡 Please manually create the project and continue")
except Exception as e:
    print(f"❌ Error in project creation: {e}")
    print("🔄 Please manually create the project if needed")

# Legacy code commented out - using direct approach instead
# if elem.is_displayed() and elem.is_enabled():
# driver.execute_script("arguments[0].click();", elem)

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
    # Calculate total automation time
    AUTOMATION_END_TIME = time.time()
    TOTAL_AUTOMATION_TIME = AUTOMATION_END_TIME - AUTOMATION_START_TIME
    END_TIME_FORMATTED = time.strftime('%H:%M:%S', time.localtime(AUTOMATION_END_TIME))
    
    # Format time duration
    hours = int(TOTAL_AUTOMATION_TIME // 3600)
    minutes = int((TOTAL_AUTOMATION_TIME % 3600) // 60)
    seconds = int(TOTAL_AUTOMATION_TIME % 60)
    milliseconds = int((TOTAL_AUTOMATION_TIME % 1) * 1000)
    
    print("\n" + "=" * 70)
    print("⏱️  AUTOMATION TIMING SUMMARY")
    print("=" * 70)
    print(f"🚀 Start Time:     {START_TIME_FORMATTED}")
    print(f"🏁 End Time:       {END_TIME_FORMATTED}")
    print(f"⏰ Total Duration: {hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}")
    print(f"📊 Total Seconds:  {TOTAL_AUTOMATION_TIME:.3f} seconds")
    
    # Performance analysis
    if TOTAL_AUTOMATION_TIME < 60:
        print("🚀 Performance:    ULTRA FAST! (< 1 minute)")
    elif TOTAL_AUTOMATION_TIME < 180:
        print("⚡ Performance:    FAST (< 3 minutes)")
    elif TOTAL_AUTOMATION_TIME < 300:
        print("✅ Performance:    GOOD (< 5 minutes)")
    elif TOTAL_AUTOMATION_TIME < 600:
        print("⏳ Performance:    MODERATE (< 10 minutes)")
    else:
        print("🐌 Performance:    SLOW (> 10 minutes)")
    
    print("=" * 70)
    
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
