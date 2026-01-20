from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import os
import urllib.parse

class WhatsAppBot:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self.wait = None

    def start_browser(self):
        options = webdriver.ChromeOptions()
        # Session persistence
        sess_dir = self.config.get('session_path', 'session_data')
        # Ensure session dir exists or Chrome might complain/fail? Chrome creates it usually.
        # But we need absolute path.
        if not os.path.exists(sess_dir):
            os.makedirs(sess_dir)
            
        session_path = os.path.abspath(sess_dir)
        options.add_argument(f"user-data-dir={session_path}")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # User agent to look more human
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        try:
            service = ChromeService(ChromeDriverManager().install())
            # Hide ChromeDriver Console on Windows
            if os.name == 'nt':
                service.creation_flags = 0x08000000
                
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Error initializing Chrome: {e}")
            import tkinter as tk
            from tkinter import messagebox
            import webbrowser
            import sys
            
            # Create hidden root for popup
            root = tk.Tk()
            root.withdraw()
            
            error_str = str(e).lower()
            if "binary" in error_str or "path" in error_str or "executable" in error_str:
                 ans = messagebox.askyesno("Error Crítico - Falta Google Chrome", 
                    "No encontré Google Chrome instalado en esta computadora.\n\n"
                    "Este software requiere Chrome para funcionar.\n"
                    "¿Deseas ir a la página de descarga oficial ahora?")
                 if ans:
                     webbrowser.open("https://www.google.com/chrome/")
            else:
                messagebox.showerror("Error de Navegador", 
                    f"No pude iniciar el navegador automatizado.\n\nDetalle técnico:\n{e}\n\nPor favor actualiza tu Google Chrome.")
            
            sys.exit(1)
            
        # Use default timeout of 60s if not set
        timeout = self.config.get('scan_timeout', 60)
        self.wait = WebDriverWait(self.driver, timeout)
        
        print("Opening WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        
        # Wait for login (check for a specific element that appears after login)
        try:
            # Waiting for the chat list side pane
            print("Please scan the QR code if requested. Waiting for login...")
            self.wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="pane-side"]')))
            print("Logged in successfully!")
        except Exception as e:
            print("Login timeout or error. Please try again.")
            raise e

    def send_message(self, phone, message):
        try:
            # Encode message for URL
            encoded_msg = urllib.parse.quote(message)
            link = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_msg}"
            self.driver.get(link)
            
            # Wait for the send button (or the chat to load)
            # This is a generic wait, robust selectors are needed.
            # Usually the send button is distinct.
            
            # Wait for chat load (search for input box)
            input_box_xpath = '//div[@contenteditable="true"][@data-tab="10"]'
            
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, input_box_xpath))
            )
            
            time.sleep(2) # Small pause for stability
            
            # Locate text input and press ENTER (simulating human action)
            input_box = self.driver.find_element(By.XPATH, input_box_xpath)
            input_box.send_keys(Keys.ENTER)
            
            print(f"Message sent to {phone}")
            
            # Wait a random amount of time to simulate human behavior
            wait_range = self.config.get('wait_between_messages', [5, 10])
            if not isinstance(wait_range, list) or len(wait_range) != 2:
                wait_range = [5, 10]
                
            pause = random.uniform(wait_range[0], wait_range[1])
            time.sleep(pause)
            return True
            
        except Exception as e:
            print(f"Failed to send message to {phone}: {e}")
            return False

    def get_unread_messages(self, whitelist=None):
        """
        Scans for unread messages.
        If whitelist is provided, only opens chats that match the known names/numbers.
        """
        unread_chats = []
        try:
            # Strategy: Find spans with aria-label containing 'unread' OR 'no leído' (for Spanish)
            xpath = '//span[contains(@aria-label, "unread message") or contains(@aria-label, "no leído")]'
            
            unread_indicators = self.driver.find_elements(By.XPATH, xpath)
            
            if not unread_indicators:
                return []
                
            print(f"Found {len(unread_indicators)} chats with unread messages.")
            
            # Use a while loop to handle the list dynamically as clicks change the DOM
            for i in range(len(unread_indicators)):
                try:
                    # Re-find to avoid stale element
                    indicators = self.driver.find_elements(By.XPATH, xpath)
                    if not indicators: break
                    if i >= len(indicators): break
                    element = indicators[i]
                    
                    # WHITELIST CHECK
                    if whitelist:
                        try:
                            # Go up parents until we find the Row 'div' to scrape the Title
                            # Structure: unread badge -> div -> div -> div (Row) ...
                            # A safer bet is: The Chat Title is usually in a span with "title" attribute nearby in the same container
                            # or simply get all text from the row
                            
                            # Find the parent row container (approximate)
                            # We search for the nearest neighbor 'span' with a 'title' attribute which usually holds the name
                            # Relative XPath from the Badge
                            row_text = element.find_element(By.XPATH, "./../../../../..").text.lower()
                            
                            # Check if any whitelist item is in the row text
                            is_allowed = False
                            for known in whitelist:
                                if known in row_text:
                                    is_allowed = True
                                    break
                            
                            if not is_allowed:
                                print(f"Skipping ignored chat (not in Excel): {row_text[:20]}...")
                                continue
                        except:
                            # If we fail to check, we might process it safely or skip.
                            # Let's process to be safe against DOM changes
                            pass

                    # Scroll into view just in case
                    self.driver.execute_script("arguments[0].scrollIntoView();", element)
                    time.sleep(1)
                    element.click()
                    time.sleep(3) # Wait for chat to load
                    
                    start_time = time.time()
                    while time.time() - start_time < 5: # Try for 5 seconds to get a valid name
                        try:
                            # Try finding the designated header info div
                            header_name_xpath = '//header//div[@role="button"]//span[@dir="auto"]'
                            header_els = self.driver.find_elements(By.XPATH, header_name_xpath)
                            
                            found_valid = False
                            for el in header_els:
                                text = el.text
                                if text and text not in ["Detalles del perfil", "Profile details", "", "Click here for contact info"]:
                                    sender_name = text
                                    found_valid = True
                                    break
                            
                            if found_valid:
                                break
                            time.sleep(0.5)
                        except:
                            time.sleep(0.5)
                            
                    # 1. Get Name (Display Name)
                    if sender_name == "Unknown":
                        print("Warning: Could not extract specific name, using default.")

                    # 2. Get Real Phone Number (Critical for matching saved contacts)
                    sender_phone = ""
                    try:
                        # Click header to open Profile Info
                        header = self.driver.find_element(By.XPATH, '//header')
                        header.click()
                        time.sleep(1) # Wait for slide-in
                        
                        # Scrape text from the side panel (usually the rightmost pane)
                        # We look for a specific container or just grab body text if desperate, 
                        # but Side Panel usually has a distinct ID or class.
                        # Common valid selector for Side Panel info:
                        side_pane = self.driver.find_element(By.XPATH, '//div[contains(@id, "app")]//div//span[contains(text(), "info") or contains(text(), "Info") or contains(text(), "about")]/../../..') 
                        # Fallback: Just grab the whole right side DOM
                        # A better generic approach: Search for a phone number pattern in the visible DOM
                        
                        body_text = self.driver.find_element(By.TAG_NAME, 'body').text
                        # Regex for phone: +52 1 55... or 55...
                        # We grep for lines that look like phones
                        import re
                        # Look for number with at least 10 digits
                        phones = re.findall(r'\+?[\d\s\-]{10,20}', body_text)
                        
                        # Filter likely candidates (the one that isn't the user's own number or random digits)
                        # Best guess: The number usually appears near the "About" section or top of profile.
                        # For now, we will rely on DataHandler to fuzzy match ANY phone found.
                        if phones:
                            # Join all found numbers as a string to let DataHandler search in it
                            sender_phone = " ".join(phones)
                            
                        # Close side panel (Press Escape)
                        webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                        time.sleep(0.5)
                        
                    except Exception as e:
                        # Non-critical, just fallback to name
                        # print(f"Could not extract phone from profile: {e}")
                        pass
                        try:
                             webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                        except:
                            pass

                    # 3. Get Last Message
                    last_msg = ""
                    try:
                        # Strategy 1: Selectable Text (Most common)
                        # We specifically look inside message-in bubbles
                        candidates = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in span.selectable-text span")
                        if not candidates:
                            # Strategy 2: Copyable Text (Newer versions)
                            candidates = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in span.copyable-text span")
                        
                        if not candidates:
                            # Strategy 3: Any span inside message-in that looks like text
                            # Exclude metadata like time
                            candidates = self.driver.find_elements(By.XPATH, "//div[contains(@class,'message-in')]//span[contains(@class,'selectable-text')]")

                        if candidates:
                            last_msg = candidates[-1].text
                    except:
                        pass
                    
                    if not last_msg:
                        # Final Fallback: Grab all text from the last message-in container
                        try:
                            bubbles = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in")
                            if bubbles:
                                last_msg = bubbles[-1].text.replace("\n", " ")
                        except:
                            pass
                    
                    unread_chats.append({'sender': sender_name, 'phone': sender_phone, 'message': last_msg})
                    print(f"Read message from {sender_name} ({sender_phone}): {last_msg}")
                    
                except Exception as inner_e:
                    print(f"Error processing chat: {inner_e}")
                    continue
                    
        except Exception as e:
            err_str = str(e).lower()
            if "invalid session id" in err_str or "disconnected" in err_str or "chrome not reachable" in err_str:
                print("Monitor paused: Browser session ended.")
                return []
            print(f"Error checking unread messages: {e}")
            
        return unread_chats

    def close(self):
        if self.driver:
            self.driver.quit()
