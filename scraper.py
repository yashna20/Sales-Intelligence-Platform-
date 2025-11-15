"""
GAF Contractor Scraper with Numbered Pagination
Clicks through page numbers (1, 2, 3, ... 10) to get all contractors
"""
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

class ContractorScraper:
    def __init__(self, zipcode="10013", country_code="us"):
        self.zipcode = zipcode
        self.country_code = country_code
        self.base_url = "https://www.gaf.com/en-us/roofing-contractors/residential"
        self.contractors = []
        self.seen_ids = set()
    
    def scrape_contractors(self):
        """Scrape all contractors by clicking through numbered pages"""
        print("\n" + "="*80)
        print("GAF CONTRACTOR SCRAPER - NUMBERED PAGINATION")
        print("="*80)
        
        driver = webdriver.Chrome()
        driver.maximize_window()
        
        try:
            url = f"{self.base_url}?distance=25&postalCode={self.zipcode}&countryCode={self.country_code}"
            print(f"\n1. Navigating to: {url}\n")
            driver.get(url)
            
            print("2. Waiting for initial page load...")
            time.sleep(8)
            
            # Scrape page 1
            print("\n" + "="*80)
            print("📄 SCRAPING PAGE 1")
            print("="*80)
            new_on_page = self.extract_current_page(driver)
            print(f"✓ Extracted {new_on_page} contractors from page 1")
            print(f"   Running total: {len(self.contractors)}")
            
            # Now click through pages 2, 3, 4, etc.
            page_number = 2
            max_pages = 15  # Safety limit
            
            while page_number <= max_pages:
                print("\n" + "="*80)
                print(f"📄 GOING TO PAGE {page_number}")
                print("="*80)
                
                # Try to click the page number
                if not self.click_page_number(driver, page_number):
                    print(f"✗ Could not find page {page_number} button. Stopping.")
                    break
                
                # Wait for page to load
                print(f"   Waiting for page {page_number} to load...")
                time.sleep(5)
                
                # Extract contractors from this page
                new_on_page = self.extract_current_page(driver)
                
                if new_on_page == 0:
                    print(f"✗ No new contractors on page {page_number}. Stopping.")
                    break
                
                print(f"✓ Extracted {new_on_page} contractors from page {page_number}")
                print(f"   Running total: {len(self.contractors)}")
                
                page_number += 1
            
            print("\n" + "="*80)
            print("🎉 SCRAPING COMPLETE!")
            print("="*80)
            print(f"Total contractors scraped: {len(self.contractors)}")
            print(f"Expected: ~93")
            print(f"Difference: {abs(93 - len(self.contractors))}")
            
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n5. Closing browser...")
            driver.quit()
        
        return self.contractors
    
    def click_page_number(self, driver, page_num):
        """
        Click on a specific page number in the pagination
        Tries multiple strategies to find and click the button
        """
        print(f"   Looking for page {page_num} button...")
        
        # Scroll to bottom where pagination is
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Strategy 1: Direct page number link/button
        selectors = [
            f"//a[text()='{page_num}']",
            f"//button[text()='{page_num}']",
            f"//a[@aria-label='Page {page_num}']",
            f"//button[@aria-label='Page {page_num}']",
            f"//a[contains(@class, 'pagination') and text()='{page_num}']",
            f"//button[contains(@class, 'pagination') and text()='{page_num}']",
            f"//li/a[text()='{page_num}']",
            f"//li/button[text()='{page_num}']",
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                
                for elem in elements:
                    try:
                        if elem.is_displayed():
                            # Scroll to element
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                            time.sleep(1)
                            
                            # Try regular click
                            try:
                                elem.click()
                                print(f"   ✓ Clicked page {page_num} button!")
                                return True
                            except ElementClickInterceptedException:
                                # Try JavaScript click
                                driver.execute_script("arguments[0].click();", elem)
                                print(f"   ✓ Clicked page {page_num} button (JavaScript)!")
                                return True
                    except:
                        continue
            except:
                continue
        
        # Strategy 2: Try "Next" button (›) if specific page number not found
        next_selectors = [
            "//button[contains(@aria-label, 'Next')]",
            "//a[contains(@aria-label, 'Next')]",
            "//button[contains(text(), '›')]",
            "//a[contains(text(), '›')]",
            "//button[contains(@class, 'next')]",
            "//a[contains(@class, 'next')]",
        ]
        
        for selector in next_selectors:
            try:
                elem = driver.find_element(By.XPATH, selector)
                if elem.is_displayed() and elem.is_enabled():
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                    time.sleep(1)
                    
                    try:
                        elem.click()
                        print(f"   ✓ Clicked 'Next' button to go to page {page_num}!")
                        return True
                    except:
                        driver.execute_script("arguments[0].click();", elem)
                        print(f"   ✓ Clicked 'Next' button (JavaScript)!")
                        return True
            except:
                continue
        
        print(f"   ✗ Could not find page {page_num} button")
        return False
    
    def extract_current_page(self, driver):
        """Extract all contractors from the currently loaded page"""
        # Scroll through page to ensure all content loads
        self.scroll_page(driver)
        
        # Wait a bit for any lazy loading
        time.sleep(2)
        
        # Find all contractor elements
        contractor_elements = driver.find_elements(By.CSS_SELECTOR, "article.certification-card")
        
        if len(contractor_elements) == 0:
            contractor_elements = driver.find_elements(By.CSS_SELECTOR, "div.certification-card__wrapper")
        
        print(f"   Found {len(contractor_elements)} contractor elements on this page")
        
        new_count = 0
        
        for idx, element in enumerate(contractor_elements, 1):
            contractor = self.extract_contractor_data(element)
            
            if contractor and contractor.get('name'):
                # Create unique ID to avoid duplicates
                unique_id = f"{contractor.get('name', '')}_{contractor.get('address', '')}"
                
                if unique_id not in self.seen_ids:
                    self.seen_ids.add(unique_id)
                    self.contractors.append(contractor)
                    new_count += 1
                    print(f"      {idx}. ✓ {contractor.get('name', 'Unknown')}")
                else:
                    print(f"      {idx}. ⊘ Duplicate: {contractor.get('name', 'Unknown')}")
            else:
                print(f"      {idx}. ✗ Failed to extract")
        
        return new_count
    
    def scroll_page(self, driver):
        """Scroll through the current page"""
        # Scroll down gradually
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        
        while current_position < scroll_height:
            current_position += 300
            driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(0.3)
        
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
    
    def extract_contractor_data(self, element):
        """Extract data from a single contractor element"""
        try:
            contractor = {}
            
            # Name
            try:
                name_elem = element.find_element(By.CSS_SELECTOR, "h2 a, h3 a")
                contractor['name'] = name_elem.text.strip()
            except:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, "h2, h3")
                    contractor['name'] = name_elem.text.strip()
                except:
                    contractor['name'] = None
            
            # Rating
            try:
                rating_elem = element.find_element(By.CSS_SELECTOR, "div.rating-stars, span[class*='rating']")
                rating = rating_elem.get_attribute("data-rating")
                if not rating:
                    rating = rating_elem.text.strip()
                contractor['rating'] = rating
            except:
                contractor['rating'] = None
            
            # Data layer JSON (contains lots of info)
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a[data-layer]")
                data_layer_json = link_elem.get_attribute("data-layer")
                if data_layer_json:
                    data = json.loads(data_layer_json)
                    contractor['contractor_id'] = data.get('contractor_id')
                    contractor['name'] = contractor.get('name') or data.get('contractor_name')
                    contractor['rating'] = contractor.get('rating') or str(data.get('contractor_rating', ''))
                    contractor['reviews_count'] = data.get('contractor_reviews_count')
                    contractor['certificates_count'] = data.get('contractor_certificates_count')
                    contractor['certificate_name'] = data.get('contractor_certificate_name')
            except:
                pass
            
            # Address/Location
            try:
                address_elem = element.find_element(By.CSS_SELECTOR, "p[class*='city'], p[class*='location'], p[class*='address']")
                contractor['address'] = address_elem.text.strip()
            except:
                contractor['address'] = None
            
            # Phone
            try:
                phone_elem = element.find_element(By.CSS_SELECTOR, "a[href*='tel:']")
                contractor['phone'] = phone_elem.text.strip()
            except:
                contractor['phone'] = None
            
            # Website
            try:
                website_elem = element.find_element(By.CSS_SELECTOR, "a[target='_blank'][href*='http']")
                contractor['website'] = website_elem.get_attribute('href')
            except:
                contractor['website'] = None
            
            # Certifications
            try:
                cert_elements = element.find_elements(By.CSS_SELECTOR, "img[alt]")
                certs = []
                for img in cert_elements:
                    alt = img.get_attribute('alt')
                    if alt and any(word in alt.lower() for word in ['award', 'elite', 'master', 'certified']):
                        certs.append(alt)
                contractor['certifications'] = certs
            except:
                contractor['certifications'] = []
            
            contractor['description'] = None
            contractor['services'] = []
            
            return contractor
            
        except Exception as e:
            return None
    
    def save_to_json(self, filename='contractors_raw.json'):
        """Save scraped data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.contractors, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Data saved to {filename}")
        
        if self.contractors:
            print(f"\n{'='*80}")
            print("SAMPLE DATA (First 3 Contractors):")
            print(f"{'='*80}")
            for i in range(min(3, len(self.contractors))):
                print(f"\nContractor {i+1}:")
                print(json.dumps(self.contractors[i], indent=2))

if __name__ == "__main__":
    print("\n" + "="*80)
    print("GAF CONTRACTOR SCRAPER")
    print("Handles numbered pagination (1, 2, 3, ... 10)")
    print("="*80)
    print("\nThis will take 2-3 minutes to complete...")
    print("Starting in 3 seconds...\n")
    time.sleep(3)
    
    scraper = ContractorScraper(zipcode="10013")
    contractors = scraper.scrape_contractors()
    
    if contractors:
        scraper.save_to_json()
        print(f"\n{'='*80}")
        print("✅ SUCCESS!")
        print(f"{'='*80}")
        print(f"Scraped {len(contractors)} contractors")
        print(f"Data saved to: contractors_raw.json")
        
        if len(contractors) >= 90:
            print("\n🎉 Got all contractors!")
        else:
            print(f"\n⚠️  Expected ~93, got {len(contractors)}")
    else:
        print("\n❌ FAILED! No contractors found.")