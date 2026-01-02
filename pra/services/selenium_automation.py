from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

logger = logging.getLogger(__name__)


class SephoraAutomation:
    """
    Automate Sephora login and add products to cart
    """

    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None

    def init_driver(self):
        """Initialize Chrome driver"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Use webdriver-manager to auto-download chromedriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.maximize_window()

        logger.info("Chrome driver initialized")

    def login(self, email, password):
        """
        Login to Sephora account

        Args:
            email: Sephora account email
            password: Sephora account password

        Returns:
            bool: True if login successful
        """
        try:
            logger.info(f"Attempting to login with email: {email}")

            # Navigate to Sephora login page
            self.driver.get("https://www.sephora.com/profile/login")

            # Wait for page load
            time.sleep(2)

            # Find and fill email field
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_input.clear()
            email_input.send_keys(email)

            # Find and fill password field
            password_input = self.driver.find_element(By.ID, "password")
            password_input.clear()
            password_input.send_keys(password)

            # Click sign in button
            sign_in_button = self.driver.find_element(
                By.CSS_SELECTOR,
                "button[type='submit']"
            )
            sign_in_button.click()

            # Wait for login to complete
            time.sleep(3)

            # Check if login was successful
            if "profile" in self.driver.current_url.lower():
                logger.info("Login successful!")
                return True
            else:
                logger.error("Login failed")
                return False

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False

    def search_product(self, product_name):
        """
        Search for a product on Sephora

        Args:
            product_name: Name of product to search

        Returns:
            str: URL of first product found
        """
        try:
            logger.info(f"Searching for product: {product_name}")

            # Navigate to search
            self.driver.get(f"https://www.sephora.com/search?keyword={product_name.replace(' ', '+')}")

            time.sleep(2)

            # Find first product link
            product_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "a[data-at='product_link']"
                ))
            )

            product_url = product_link.get_attribute('href')
            logger.info(f"Found product: {product_url}")

            return product_url

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return None

    def add_to_cart(self, product_url):
        """
        Add a product to cart

        Args:
            product_url: Direct URL to product page

        Returns:
            bool: True if added successfully
        """
        try:
            logger.info(f"Adding to cart: {product_url}")

            # Navigate to product page
            self.driver.get(product_url)
            time.sleep(2)

            # Click "Add to Basket" button
            add_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    "button[data-at='add_to_basket']"
                ))
            )
            add_button.click()

            logger.info("Product added to cart!")
            time.sleep(2)

            return True

        except Exception as e:
            logger.error(f"Add to cart error: {str(e)}")
            return False

    def add_multiple_products(self, product_list):
        """
        Add multiple products to cart

        Args:
            product_list: List of product names or URLs

        Returns:
            dict: Summary of additions
        """
        results = {
            'successful': [],
            'failed': []
        }

        for product in product_list:
            try:
                # Check if it's a URL or product name
                if product.startswith('http'):
                    product_url = product
                else:
                    product_url = self.search_product(product)

                if product_url:
                    if self.add_to_cart(product_url):
                        results['successful'].append(product)
                    else:
                        results['failed'].append(product)
                else:
                    results['failed'].append(product)

                time.sleep(1)  # Rate limiting

            except Exception as e:
                logger.error(f"Error processing {product}: {str(e)}")
                results['failed'].append(product)

        return results

    def view_cart(self):
        """Navigate to shopping cart"""
        self.driver.get("https://www.sephora.com/basket")
        time.sleep(2)

    def get_cart_items(self):
        """
        Get list of items in cart

        Returns:
            list: Cart items
        """
        try:
            self.view_cart()

            items = []
            cart_items = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div[data-at='item_name']"
            )

            for item in cart_items:
                items.append(item.text)

            return items

        except Exception as e:
            logger.error(f"Error getting cart items: {str(e)}")
            return []

    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


class SephoraCartService:
    """
    High-level service for Sephora cart automation
    """

    def __init__(self):
        self.automation = SephoraAutomation(headless=False)

    def auto_add_recommendations(self, email, password, recommendations):
        """
        Login and add recommended products to cart

        Args:
            email: Sephora account email
            password: Sephora account password
            recommendations: List of product dicts from recommender

        Returns:
            dict: Results summary
        """
        try:
            # Initialize browser
            self.automation.init_driver()

            # Login
            if not self.automation.login(email, password):
                return {
                    'success': False,
                    'error': 'Login failed',
                    'added': [],
                    'failed': []
                }

            # Extract product names/URLs
            products = []
            for rec in recommendations:
                if rec.get('url'):
                    products.append(rec['url'])
                else:
                    product_name = f"{rec.get('brand')} {rec.get('name')}"
                    products.append(product_name)

            # Add products to cart
            results = self.automation.add_multiple_products(products)

            # View cart
            self.automation.view_cart()

            # Get final cart items
            cart_items = self.automation.get_cart_items()

            return {
                'success': True,
                'added': results['successful'],
                'failed': results['failed'],
                'cart_items': cart_items,
                'total_added': len(results['successful'])
            }

        except Exception as e:
            logger.error(f"Auto-add error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'added': [],
                'failed': []
            }

        finally:
            # Keep browser open for user to review
            # self.automation.close()
            pass