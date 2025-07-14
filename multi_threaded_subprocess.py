#!/usr/bin/env python3
"""
Multi-Threaded Gmail Automation - SUBPROCESS APPROACH
Runs multiple instances of auto.py in parallel using subprocesses
This ensures complete isolation and maximum compatibility
"""

import os
import sys
import time
import threading
import concurrent.futures
import subprocess
import csv
import shutil
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
import logging

# Configure logging without unicode characters
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [Worker-%(thread)d] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('multi_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EmailAccount:
    """Data class for email account information"""
    email: str
    password: str
    worker_dir: str
    thread_id: Optional[int] = None
    status: str = "pending"
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    credentials_path: Optional[str] = None
    process_output: Optional[str] = None

class ThreadSafeCounter:
    """Thread-safe counter for tracking progress"""
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
            return self._value
    
    def get_value(self):
        with self._lock:
            return self._value

class SubprocessMultiThreadedAutomation:
    """Multi-threaded automation using subprocess approach"""
    
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.accounts = []
        self.completed_counter = ThreadSafeCounter()
        self.failed_counter = ThreadSafeCounter()
        self.base_dir = os.getcwd()
    
    def load_accounts_from_csv(self, csv_file="gmail_accounts.csv"):
        """Load email accounts from CSV file"""
        try:
            if not os.path.exists(csv_file):
                logger.error(f"CSV file not found: {csv_file}")
                return False
            
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, 1):
                    if 'email' in row and 'password' in row:
                        # Create worker-specific directory
                        worker_dir = os.path.join(self.base_dir, f"worker_{row_num}")
                        os.makedirs(worker_dir, exist_ok=True)
                        
                        account = EmailAccount(
                            email=row['email'].strip(),
                            password=row['password'].strip(),
                            worker_dir=worker_dir
                        )
                        self.accounts.append(account)
                        logger.info(f"Loaded account: {account.email}")
                    else:
                        logger.warning(f"Invalid row {row_num}: missing email or password")
            
            logger.info(f"Loaded {len(self.accounts)} accounts from {csv_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading accounts: {e}")
            return False
    
    def setup_worker_environment(self, account: EmailAccount, worker_id: int):
        """Setup isolated environment for a worker"""
        try:
            # Create Unicode-safe version of auto.py
            if not self.create_unicode_safe_auto_py(account.worker_dir):
                logger.error(f"Worker {worker_id}: Failed to create Unicode-safe auto.py")
                return False
            logger.info(f"Worker {worker_id}: Created Unicode-safe auto.py")
            
            # List of additional files that auto.py might need
            required_files = [
                "chromedriver.exe"
            ]
            
            # Optional files that might be useful
            optional_files = [
                "config.py",
                "requirements.txt",
                "credentials_sample.json",
                ".env"
            ]
            
            # Copy required files to worker directory
            for filename in required_files:
                source_path = os.path.join(self.base_dir, filename)
                dest_path = os.path.join(account.worker_dir, filename)
                
                if os.path.exists(source_path):
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"Worker {worker_id}: Copied {filename}")
                else:
                    logger.warning(f"Worker {worker_id}: {filename} not found - might be needed")
            
            # Copy optional files if they exist
            for filename in optional_files:
                source_path = os.path.join(self.base_dir, filename)
                dest_path = os.path.join(account.worker_dir, filename)
                
                if os.path.exists(source_path):
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"Worker {worker_id}: Copied optional file {filename}")
            
            # Create accounts CSV for this worker (using gmail_accounts.csv format)
            accounts_csv = os.path.join(account.worker_dir, "gmail_accounts.csv")
            with open(accounts_csv, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['email', 'password'])
                writer.writerow([account.email, account.password])
            
            logger.info(f"Worker {worker_id}: Created gmail_accounts.csv")
            
            # Also create accounts.csv as backup
            accounts_csv_backup = os.path.join(account.worker_dir, "accounts.csv")
            with open(accounts_csv_backup, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['email', 'password'])
                writer.writerow([account.email, account.password])
            
            # Create downloads directory
            downloads_dir = os.path.join(account.worker_dir, "downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            
            logger.info(f"Worker {worker_id}: Environment setup complete")
            return True
            
        except Exception as e:
            logger.error(f"Worker {worker_id}: Failed to setup environment: {e}")
            return False
    
    def run_single_account_subprocess(self, account: EmailAccount, worker_id: int):
        """Run automation for a single account using subprocess"""
        account.thread_id = worker_id
        account.start_time = datetime.now()
        account.status = "running"
        
        try:
            logger.info(f"Worker {worker_id}: Starting automation for {account.email}")
            
            # Setup worker environment
            if not self.setup_worker_environment(account, worker_id):
                raise Exception("Failed to setup worker environment")
            
            # Change to worker directory
            original_cwd = os.getcwd()
            os.chdir(account.worker_dir)
            
            try:
                # Run auto.py as subprocess
                logger.info(f"Worker {worker_id}: Launching auto.py subprocess...")
                
                process = subprocess.Popen(
                    [sys.executable, "auto.py"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=account.worker_dir
                )
                
                # Wait for process to complete with timeout
                try:
                    stdout, stderr = process.communicate(timeout=1800)  # 30 minutes timeout
                    return_code = process.returncode
                    
                    # Store output for debugging
                    account.process_output = f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
                    
                    # Log the output for debugging
                    if stdout:
                        logger.info(f"Worker {worker_id}: STDOUT: {stdout[:500]}...")  # First 500 chars
                    if stderr:
                        logger.warning(f"Worker {worker_id}: STDERR: {stderr[:500]}...")  # First 500 chars
                    
                    if return_code == 0:
                        logger.info(f"Worker {worker_id}: auto.py completed successfully")
                        account.status = "completed"
                        self.completed_counter.increment()
                        
                        # Look for credentials file
                        self.find_credentials_file(account)
                        return True
                    else:
                        error_msg = f"auto.py failed with return code {return_code}"
                        if stderr:
                            error_msg += f". Error: {stderr[:200]}"
                        raise Exception(error_msg)
                        
                except subprocess.TimeoutExpired:
                    process.kill()
                    raise Exception("auto.py subprocess timed out after 30 minutes")
                
            finally:
                # Always return to original directory
                os.chdir(original_cwd)
            
        except Exception as e:
            account.status = "failed"
            account.error_message = str(e)
            self.failed_counter.increment()
            logger.error(f"Worker {worker_id}: Failed for {account.email}: {e}")
            return False
        
        finally:
            account.end_time = datetime.now()
            if account.start_time and account.end_time:
                duration = (account.end_time - account.start_time).total_seconds()
                logger.info(f"Worker {worker_id}: Completed {account.email} in {duration:.1f} seconds")
            
            # Save worker output for debugging
            self.save_worker_output(account, worker_id)
    
    def find_credentials_file(self, account: EmailAccount):
        """Find and set the credentials file path for the account"""
        try:
            import glob
            
            # Look for JSON credentials in worker directory and subdirectories
            patterns = [
                os.path.join(account.worker_dir, "*.json"),
                os.path.join(account.worker_dir, "**", "*.json"),
                os.path.join(account.worker_dir, "downloads", "*.json")
            ]
            
            json_files = []
            for pattern in patterns:
                json_files.extend(glob.glob(pattern, recursive=True))
            
            if json_files:
                # Get the most recent file
                latest_file = max(json_files, key=os.path.getctime)
                account.credentials_path = latest_file
                logger.info(f"Found credentials: {os.path.basename(latest_file)}")
            else:
                logger.warning(f"No credentials file found for {account.email}")
            
        except Exception as e:
            logger.warning(f"Error finding credentials for {account.email}: {e}")
    
    def run_automation(self):
        """Run automation for all accounts using thread pool"""
        if not self.accounts:
            logger.error("No accounts loaded!")
            return False
        
        logger.info(f"Starting multi-threaded automation for {len(self.accounts)} accounts")
        logger.info(f"Using {self.max_workers} concurrent workers")
        logger.info("Each worker will run auto.py as an isolated subprocess")
        
        start_time = datetime.now()
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_account = {
                    executor.submit(self.run_single_account_subprocess, account, worker_id): account
                    for worker_id, account in enumerate(self.accounts, 1)
                }
                
                # Monitor progress
                completed = 0
                for future in concurrent.futures.as_completed(future_to_account):
                    account = future_to_account[future]
                    completed += 1
                    
                    try:
                        result = future.result()
                        status = "SUCCESS" if result else "FAILED"
                        logger.info(f"Progress: {completed}/{len(self.accounts)} - {account.email} - {status}")
                    except Exception as e:
                        logger.error(f"Task exception for {account.email}: {e}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Print final summary
            self.print_summary(duration)
            return True
            
        except Exception as e:
            logger.error(f"Multi-threading error: {e}")
            return False
    
    def print_summary(self, duration):
        """Print automation summary"""
        total = len(self.accounts)
        completed = self.completed_counter.get_value()
        failed = self.failed_counter.get_value()
        
        print("\n" + "="*60)
        print("MULTI-THREADED AUTOMATION SUMMARY")
        print("="*60)
        print(f"Total Accounts: {total}")
        print(f"Successful: {completed}")
        print(f"Failed: {failed}")
        print(f"Total Duration: {duration:.1f} seconds")
        if total > 0:
            print(f"Average per Account: {duration/total:.1f} seconds")
            print(f"Success Rate: {(completed/total)*100:.1f}%")
        
        print("\nACCOUNT DETAILS:")
        print("-" * 60)
        for account in self.accounts:
            status_icon = "[OK]" if account.status == "completed" else "[FAIL]"
            duration_text = ""
            if account.start_time and account.end_time:
                account_duration = (account.end_time - account.start_time).total_seconds()
                duration_text = f" ({account_duration:.1f}s)"
            
            print(f"{status_icon} {account.email} - {account.status}{duration_text}")
            if account.error_message:
                print(f"   Error: {account.error_message}")
            if account.credentials_path:
                print(f"   Credentials: {os.path.basename(account.credentials_path)}")
            if hasattr(account, 'worker_dir'):
                print(f"   Worker Dir: {account.worker_dir}")
        
        print("="*60)
        print(f"Worker directories created in: {self.base_dir}")
        print("Check individual worker directories for detailed logs and outputs.")
    
    def save_worker_output(self, account: EmailAccount, worker_id: int):
        """Save worker output to a log file for debugging"""
        try:
            if account.process_output:
                output_file = os.path.join(account.worker_dir, "worker_output.log")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Worker {worker_id} Output for {account.email}\n")
                    f.write("="*60 + "\n")
                    f.write(f"Status: {account.status}\n")
                    f.write(f"Start Time: {account.start_time}\n")
                    f.write(f"End Time: {account.end_time}\n")
                    if account.error_message:
                        f.write(f"Error: {account.error_message}\n")
                    f.write("\n" + "="*60 + "\n")
                    f.write(account.process_output)
                logger.info(f"Worker {worker_id}: Output saved to worker_output.log")
        except Exception as e:
            logger.warning(f"Worker {worker_id}: Could not save output: {e}")

    def create_unicode_safe_auto_py(self, worker_dir):
        """Create a Unicode-safe version of auto.py for the worker"""
        try:
            with open("auto.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Replace ALL Unicode characters found in auto.py
            emoji_replacements = {
                # Exact emojis found in auto.py via grep search
                "🔄": "[LOADING]",
                "⚡": "[FAST]", 
                "📦": "[PACKAGE]",
                "🏷️": "[ID]",
                "⏰": "[TIME]",
                "📁": "[FOLDER]",
                "🔌": "[PLUG]",
                "🔐": "[LOGIN]",
                "�": "[EMAIL]",
                "❌": "[ERROR]",
                "�": "[LOCK]",
                "�": "[FOLDER_OPEN]",
                "✅": "[OK]",
                "⚠️": "[WARNING]",
                "🧹": "[CLEAN]",
                
                # Additional Unicode characters that might exist
                "�": "[SEARCH]",
                "�": "[DOWNLOAD]",
                "�": "[TIP]",
                "🎯": "[TARGET]",
                "�": "[START]",
                "�": "[GOODBYE]",
                "🔚": "[END]",
                "📱": "[PHONE]",
                "🎉": "[SUCCESS]",
                "🏗️": "[BUILD]",
                "📝": "[WRITE]",
                "🌍": "[WORLD]",
                "▶️": "[PLAY]",
                "⏭️": "[SKIP]",
                "ℹ️": "[INFO]",
                "🖥️": "[DESKTOP]",
                "🔑": "[KEY]",
                "📄": "[FILE]",
                "": "[ROBOT]",
                "⭐": "[STAR]",
                "💻": "[COMPUTER]",
                "🌐": "[GLOBAL]",
                "🔧": "[TOOL]",
                "📊": "[CHART]",
                "🎁": "[GIFT]",
                "🔔": "[BELL]",
                "📞": "[CALL]",
                "💾": "[SAVE]",
                "🖱️": "[MOUSE]",
                "⌨️": "[KEYBOARD]",
                "🖨️": "[PRINT]",
                "📹": "[VIDEO]",
                "🎬": "[MOVIE]",
                "🎵": "[MUSIC]",
                "🔊": "[SOUND]",
                "🔇": "[MUTE]",
                "📈": "[TRENDING_UP]",
                "📉": "[TRENDING_DOWN]",
                "🔗": "[LINK]",
                "🌟": "[STAR2]",
                "💰": "[MONEY]",
                "💳": "[CARD]",
                "🏆": "[TROPHY]",
                "🎪": "[CIRCUS]",
                "🎭": "[MASK]",
                "🎨": "[ART]",
                "": "[GAME]",
                "🎲": "[DICE]",
                "🃏": "[JOKER]",
                "🎴": "[CARDS]",
                "🎰": "[SLOT]",
                "🎳": "[BOWLING]",
                "🎸": "[GUITAR]",
                "🎺": "[TRUMPET]",
                "🎻": "[VIOLIN]",
                "🥁": "[DRUM]",
                "🎤": "[MIC]",
                "🎧": "[HEADPHONES]",
                "📻": "[RADIO]",
                "📺": "[TV]",
                "📷": "[CAMERA]",
                "📸": "[CAMERA_FLASH]",
                "🔦": "[FLASHLIGHT]",
                "🔥": "[FIRE]",
                "💧": "[WATER]",
                "🌊": "[WAVE]",
                "❄️": "[SNOW]",
                "⛄": "[SNOWMAN]",
                "☀️": "[SUN]",
                "🌙": "[MOON]",
                "💫": "[DIZZY]",
                "✨": "[SPARKLES]",
                "🔆": "[BRIGHT]",
                "🔅": "[DIM]",
                
                # Direct Unicode mapping for all characters found
                "\U0001f504": "[LOADING]",  # 🔄
                "\U000026a1": "[FAST]",     # ⚡
                "\U0001f4e6": "[PACKAGE]",  # 📦
                "\U0001f3f7\ufe0f": "[ID]", # 🏷️
                "\U0001f3f7": "[LABEL]",    # 🏷 (without variation selector)
                "\U000023f0": "[TIME]",     # ⏰
                "\U0001f4c1": "[FOLDER]",   # 📁
                "\U0001f50c": "[PLUG]",     # 🔌
                "\U0001f510": "[LOGIN]",    # 🔐
                "\U0001f4e7": "[EMAIL]",    # 📧
                "\U0000274c": "[ERROR]",    # ❌
                "\U0001f512": "[LOCK]",     # 🔒
                "\U0001f4c2": "[FOLDER_OPEN]", # 📂
                "\U00002705": "[OK]",       # ✅
                "\U000026a0\ufe0f": "[WARNING]", # ⚠️
                "\U000026a0": "[WARNING2]", # ⚠ (without variation selector)
                "\U0001f9f9": "[CLEAN]",    # 🧹
            }
            
            # Modify auto.py to read credentials from CSV instead of user input
            # Replace the get_user_credentials_and_config function
            csv_reader_code = '''
# Modified for multi-threading: Read credentials from CSV
def get_user_credentials_and_config():
    """Read credentials from gmail_accounts.csv for batch processing"""
    import csv
    import os
    
    csv_file = "gmail_accounts.csv"
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Credentials file {csv_file} not found")
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        account = next(reader)  # Get the first (and only) account
        
        email = account['email'].strip()
        password = account['password'].strip()
        
        print(f"Using account: {email}")
        
        # Use instance-specific download directory
        download_dir = INSTANCE_DIRS['downloads']
        print(f"Using download directory: {download_dir}")
        
        return email, password, download_dir
'''
            
            # Find and replace the get_user_credentials_and_config function
            import re
            
            # Pattern to match the function definition and its body
            function_pattern = r'def get_user_credentials_and_config\(\):.*?(?=\ndef|\nclass|\n[a-zA-Z_]|\Z)'
            
            if re.search(function_pattern, content, re.DOTALL):
                content = re.sub(function_pattern, csv_reader_code.strip(), content, flags=re.DOTALL)
                print(f"Modified auto.py to read from CSV for batch processing")
            else:
                print("Could not find get_user_credentials_and_config function to replace")
            
            # Also ensure csv import is added
            if 'import csv' not in content:
                # Add csv import after other imports
                import_pattern = r'(import [^\n]+\n)'
                if re.search(import_pattern, content):
                    content = re.sub(r'(import [^\n]+\n)', r'\1import csv\n', content, count=1)
            
            # Handle Unicode characters encoding
            try:
                # Try to encode as ASCII, replacing problematic characters
                content_bytes = content.encode('ascii', errors='replace')
                content = content_bytes.decode('ascii')
            except Exception as e:
                print(f"ASCII encoding failed: {e}, using UTF-8 with BOM")
                # Fallback: keep original content but save with UTF-8 BOM for Windows compatibility
            
            # Write the Unicode-safe version
            safe_auto_py = os.path.join(worker_dir, "auto.py")
            try:
                # First try ASCII encoding
                with open(safe_auto_py, "w", encoding="ascii") as f:
                    f.write(content)
            except UnicodeEncodeError:
                # Fallback to UTF-8 with BOM for Windows compatibility
                with open(safe_auto_py, "w", encoding="utf-8-sig") as f:
                    f.write(content)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Unicode-safe auto.py: {e}")
            return False

def main():
    """Main function to run the multi-threaded automation"""
    print("Starting Multi-Threaded Gmail API Automation (Subprocess Approach)")
    print("="*60)
    
    # Check if auto.py exists
    if not os.path.exists("auto.py"):
        print("ERROR: auto.py not found in current directory!")
        print("Please make sure auto.py is in the same directory as this script.")
        input("Press Enter to exit...")
        return
    
    # Get number of workers from user
    print(f"\nConfiguring concurrent workers...")
    while True:
        try:
            max_workers_input = input("Enter number of concurrent workers (1-20, default=3): ").strip()
            if not max_workers_input:
                max_workers = 3  # Default value
                break
            max_workers = int(max_workers_input)
            if 1 <= max_workers <= 20:
                break
            else:
                print("Please enter a number between 1 and 20.")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"Using {max_workers} concurrent workers.")
    
    # Create automation instance
    automation = SubprocessMultiThreadedAutomation(max_workers=max_workers)
    
    # Load accounts
    if not automation.load_accounts_from_csv("gmail_accounts.csv"):
        print("Failed to load accounts. Please check your gmail_accounts.csv file.")
        input("Press Enter to exit...")
        return
    
    # Warning about non-Gmail accounts
    non_gmail_accounts = [acc for acc in automation.accounts if "@gmail.com" not in acc.email.lower()]
    if non_gmail_accounts:
        print("\nWARNING: Non-Gmail accounts detected:")
        for acc in non_gmail_accounts:
            print(f"  - {acc.email}")
        print("These accounts may fail as this automation is designed for Gmail accounts.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Automation cancelled.")
            return
    
    print(f"\nStarting automation for {len(automation.accounts)} accounts...")
    print("Each account will run in an isolated subprocess for maximum compatibility.")
    input("Press Enter to start, or Ctrl+C to cancel...")
    
    # Run automation
    try:
        if automation.run_automation():
            print("\nMulti-threaded automation completed!")
        else:
            print("\nMulti-threaded automation failed!")
    except KeyboardInterrupt:
        print("\nAutomation interrupted by user.")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
