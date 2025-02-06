import requests
import json
import random
import string
import names
import time
import secrets
from datetime import datetime
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
from eth_account import Account
from eth_account.messages import encode_defunct
from websocket import create_connection

# Initialize color output for logs
init(autoreset=True)

def log_message(account_num=None, total=None, message="", message_type="info"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    account_status = f"{account_num}/{total}" if account_num and total else ""
    
    colors = {
        "info": Fore.LIGHTWHITE_EX,
        "success": Fore.LIGHTGREEN_EX,
        "error": Fore.LIGHTRED_EX,
        "warning": Fore.LIGHTYELLOW_EX,
        "process": Fore.LIGHTCYAN_EX,
        "debug": Fore.LIGHTMAGENTA_EX
    }
    
    log_color = colors.get(message_type, Fore.LIGHTWHITE_EX)
    print(f"{Fore.WHITE}[{Style.DIM}{timestamp}{Style.RESET_ALL}{Fore.WHITE}] "
          f"{Fore.WHITE}[{Fore.LIGHTYELLOW_EX}{account_status}{Fore.WHITE}] "
          f"{log_color}{message}")

def generate_ethereum_wallet():
    """Generates an Ethereum wallet with a private key."""
    private_key = '0x' + secrets.token_hex(32)
    account = Account.from_key(private_key)
    return {'address': account.address, 'private_key': private_key}

def create_wallet_signature(wallet, message):
    """Signs a message using the wallet's private key."""
    account = Account.from_key(wallet['private_key'])
    signable_message = encode_defunct(text=message)
    signed_message = account.sign_message(signable_message)
    return signed_message.signature.hex()

class TeneoAutoref:
    def __init__(self, ref_code):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.ref_code = ref_code

    def make_request(self, method, url, **kwargs):
        """Handles HTTP requests with error handling."""
        try:
            kwargs['timeout'] = 60  
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            log_message(message="Request failed: " + str(e), message_type="error")
            return None

    def generate_email(self):
        """Generates a random email."""
        first_name = names.get_first_name().lower()
        last_name = names.get_last_name().lower()
        random_nums = ''.join(random.choices(string.digits, k=3))
        domain = "example.com"  # Replace with a real domain provider
        email = f"{first_name}.{last_name}{random_nums}@{domain}"
        log_message(message=f"Generated email: {email}", message_type="success")
        return email

    def generate_password(self):
        """Generates a strong random password."""
        first_letter = random.choice(string.ascii_uppercase)
        other_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=9))
        special_char = random.choice("!@#$%^&*")
        password = first_letter + other_chars + special_char
        log_message(message="Generated password", message_type="success")
        return password

    def register_account(self):
        """Handles the full registration process."""
        email = self.generate_email()
        password = self.generate_password()
        wallet = generate_ethereum_wallet()

        log_message(message="Registering account...", message_type="process")

        registration_payload = {
            "email": email,
            "password": password,
            "referral_code": self.ref_code
        }
        headers = {
            "User-Agent": self.ua.random,
            "Content-Type": "application/json"
        }
        
        reg_response = self.make_request("POST", "https://teneo-api.com/register", json=registration_payload, headers=headers)
        
        if reg_response and reg_response.status_code == 201:
            log_message(message="Account registered successfully!", message_type="success")
        else:
            log_message(message="Registration failed!", message_type="error")
            return None

        return {"email": email, "password": password, "wallet": wallet}

    def verify_email(self, email):
        """Simulates email verification process."""
        log_message(message=f"Verifying email: {email}", message_type="process")
        time.sleep(2)  # Simulating delay for email verification
        log_message(message="Email verified!", message_type="success")

    def connect_wallet(self, wallet):
        """Handles Web3 wallet authentication."""
        log_message(message="Connecting wallet...", message_type="process")
        message = "Sign this message to verify your wallet"
        signature = create_wallet_signature(wallet, message)

        connect_payload = {
            "wallet_address": wallet['address'],
            "signature": signature
        }
        
        headers = {"User-Agent": self.ua.random, "Content-Type": "application/json"}
        
        connect_response = self.make_request("POST", "https://teneo-api.com/connect-wallet", json=connect_payload, headers=headers)

        if connect_response and connect_response.status_code == 200:
            log_message(message="Wallet connected successfully!", message_type="success")
        else:
            log_message(message="Wallet connection failed!", message_type="error")

    def run(self, num_accounts):
        """Runs the entire process for multiple accounts."""
        log_message(message=f"Starting auto-ref process for {num_accounts} accounts...", message_type="info")
        
        for i in range(1, num_accounts + 1):
            log_message(account_num=i, total=num_accounts, message="Creating new account...", message_type="process")
            account_data = self.register_account()
            
            if account_data:
                self.verify_email(account_data['email'])
                self.connect_wallet(account_data['wallet'])
                log_message(account_num=i, total=num_accounts, message="Account setup complete!", message_type="success")
            else:
                log_message(account_num=i, total=num_accounts, message="Skipping account due to failure", message_type="error")

            time.sleep(random.randint(2, 5))  # Avoid detection with a random delay

        log_message(message="Auto-referral process completed!", message_type="info")

# Example usage:
if __name__ == "__main__":
    referral_code = "YOUR_REFERRAL_CODE_HERE"  # Replace with your actual referral code
    bot = TeneoAutoref(referral_code)
    bot.run(num_accounts=5)  # Change the number of accounts to generate
