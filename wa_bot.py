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
        session_path = os.path.abspath(self.config['session_path'])
        options.add_argument(f"user-data-dir={session_path}")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # User agent to look more human
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, self.config['scan_timeout'])
        
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
            pause = random.uniform(*self.config['wait_between_messages'])
            time.sleep(pause)
            return True
            
        except Exception as e:
            print(f"Failed to send message to {phone}: {e}")
            return False

    def get_unread_messages(self):
        """
        Scans for unread messages using generic strategies.
        """
        unread_chats = []
        try:
            # Strategy: Find spans with aria-label containing 'unread' OR 'no leído' (for Spanish)
            # This is robust because it relies on accessibility labels, not obfuscated classes
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
                    
                    # Always click the first one found, as the list might shift
                    # But if we want to process all, we need to hope order is preserved or re-calibrated.
                    # Safest is to click the 'i-th' element if it exists
                    if i >= len(indicators): break
                    element = indicators[i]
                    
                    # Scroll into view just in case
                    self.driver.execute_script("arguments[0].scrollIntoView();", element)
                    time.sleep(1)
                    element.click()
                    time.sleep(3) # Wait for chat to load
                    
                    # 1. Get Sender Name
                    # The name is usually in a span inside a div with title (header-title)
                    # We avoid 'Detalles del perfil' by looking for the main title container
                    try:
                        # Try finding the designated header info div
                        # Usually: //header//div[@role="button"]//span[@title] but avoiding the profile pic button
                        header_name_xpath = '//header//div[@role="button"]//span[@dir="auto"]'
                        
                        header_els = self.driver.find_elements(By.XPATH, header_name_xpath)
                        sender_name = "Unknown"
                        
                        for el in header_els:
                            text = el.text
                            if text and text not in ["Detalles del perfil", "Profile details", ""]:
                                sender_name = text
                                break
                                
                    except Exception as e:
                        print(f"Name extr error: {e}")
                        sender_name = "Unknown"

                    # 2. Get Last Message
                    # Look for message containers. 'message-in' is a stable class for incoming messages.
                    # We want the last text content.
                    msg_xpath = '//div[contains(@class, "message-in")]//span[contains(@class, "selectable-text")]/span'
                    # Improved XPath to find the inner text span
                    
                    messages = self.driver.find_elements(By.XPATH, msg_xpath)
                    
                    last_msg = ""
                    if messages:
                        # Get the very last message found
                        last_msg = messages[-1].text
                    
                    unread_chats.append({'sender': sender_name, 'message': last_msg})
                    print(f"Read message from {sender_name}: {last_msg}")
                    
                except Exception as inner_e:
                    print(f"Error processing chat: {inner_e}")
                    continue
                    
        except Exception as e:
            print(f"Error checking unread messages: {e}")
            
        return unread_chats

    def close(self):
        if self.driver:
            self.driver.quit()
