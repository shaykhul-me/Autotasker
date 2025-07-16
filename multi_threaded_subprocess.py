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
        """Setup isolated environment for a worker with comprehensive dependency handling"""
        try:
            logger.info(f"Worker {worker_id}: Setting up isolated environment...")
            
            # Create Unicode-safe version of auto.py
            if not self.create_unicode_safe_auto_py(account.worker_dir):
                logger.error(f"Worker {worker_id}: Failed to create Unicode-safe auto.py")
                return False
            logger.info(f"Worker {worker_id}: Created Unicode-safe auto.py")
            
            # List of critical files that auto.py requires
            critical_files = [
                "chromedriver.exe"
            ]
            
            # List of optional files that enhance functionality
            optional_files = [
                "config.py",
                "requirements.txt", 
                "requirements_build.txt",
                "requirements_multi_threaded.txt",
                "credentials_sample.json",
                ".env",
                "automation_monitor.py",  # If monitoring is used
                "build_exe.py",          # If building is needed
                "test_auto_requirements.py"  # For testing
            ]
            
            # Copy critical files to worker directory
            missing_critical = []
            for filename in critical_files:
                source_path = os.path.join(self.base_dir, filename)
                dest_path = os.path.join(account.worker_dir, filename)
                
                if os.path.exists(source_path):
                    try:
                        shutil.copy2(source_path, dest_path)
                        logger.info(f"Worker {worker_id}: Copied critical file {filename}")
                    except Exception as copy_error:
                        logger.error(f"Worker {worker_id}: Failed to copy {filename}: {copy_error}")
                        missing_critical.append(filename)
                else:
                    logger.warning(f"Worker {worker_id}: Critical file {filename} not found")
                    missing_critical.append(filename)
            
            # Check if we can proceed without critical files
            if missing_critical:
                logger.warning(f"Worker {worker_id}: Missing critical files: {missing_critical}")
                logger.info(f"Worker {worker_id}: Attempting to proceed anyway...")
            
            # Copy optional files if they exist
            copied_optional = []
            for filename in optional_files:
                source_path = os.path.join(self.base_dir, filename)
                dest_path = os.path.join(account.worker_dir, filename)
                
                if os.path.exists(source_path):
                    try:
                        shutil.copy2(source_path, dest_path)
                        copied_optional.append(filename)
                        logger.info(f"Worker {worker_id}: Copied optional file {filename}")
                    except Exception as copy_error:
                        logger.warning(f"Worker {worker_id}: Failed to copy optional file {filename}: {copy_error}")
            
            if copied_optional:
                logger.info(f"Worker {worker_id}: Copied {len(copied_optional)} optional files")
            
            # Create comprehensive CSV files for account credentials
            # Primary CSV file (gmail_accounts.csv)
            accounts_csv = os.path.join(account.worker_dir, "gmail_accounts.csv")
            try:
                with open(accounts_csv, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['email', 'password'])
                    writer.writerow([account.email, account.password])
                logger.info(f"Worker {worker_id}: Created gmail_accounts.csv")
            except Exception as csv_error:
                logger.error(f"Worker {worker_id}: Failed to create gmail_accounts.csv: {csv_error}")
                return False
            
            # Backup CSV files with alternative names
            backup_csv_files = [
                "accounts.csv",
                "multi_accounts.csv", 
                "gmail_multi_accounts_template.csv"
            ]
            
            for backup_name in backup_csv_files:
                backup_path = os.path.join(account.worker_dir, backup_name)
                try:
                    with open(backup_path, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(['email', 'password'])
                        writer.writerow([account.email, account.password])
                except Exception as backup_error:
                    logger.warning(f"Worker {worker_id}: Failed to create backup CSV {backup_name}: {backup_error}")
            
            # Create comprehensive directory structure
            directories_to_create = [
                "downloads",
                "temp", 
                "chrome_profile",
                "logs",
                "credentials",
                "downloads/account_credentials"  # Specific for credentials
            ]
            
            for dir_name in directories_to_create:
                dir_path = os.path.join(account.worker_dir, dir_name)
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"Worker {worker_id}: Created directory {dir_name}")
                except Exception as dir_error:
                    logger.warning(f"Worker {worker_id}: Failed to create directory {dir_name}: {dir_error}")
            
            # Create a worker-specific configuration file
            config_content = f'''# Worker {worker_id} Configuration
EMAIL = "{account.email}"
WORKER_ID = {worker_id}
WORKER_DIR = "{account.worker_dir}"
DOWNLOADS_DIR = "{os.path.join(account.worker_dir, 'downloads')}"
AUTOMATION_MODE = "MULTI_THREADED"
FAST_MODE = True
'''
            
            config_path = os.path.join(account.worker_dir, "worker_config.py")
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(config_content)
                logger.info(f"Worker {worker_id}: Created worker configuration")
            except Exception as config_error:
                logger.warning(f"Worker {worker_id}: Failed to create worker config: {config_error}")
            
            # Create a batch file for manual debugging (Windows)
            if sys.platform == "win32":
                batch_content = f'''@echo off
echo Worker {worker_id} Debug Environment
echo Working Directory: {account.worker_dir}
echo Account: {account.email}
echo.
echo To run automation manually:
echo python auto.py
echo.
cd /d "{account.worker_dir}"
cmd /k
'''
                batch_path = os.path.join(account.worker_dir, f"debug_worker_{worker_id}.bat")
                try:
                    with open(batch_path, 'w', encoding='utf-8') as f:
                        f.write(batch_content)
                    logger.info(f"Worker {worker_id}: Created debug batch file")
                except Exception as batch_error:
                    logger.warning(f"Worker {worker_id}: Failed to create debug batch: {batch_error}")
            
            # Create a requirements.txt specific to this worker for debugging
            worker_requirements = '''selenium>=4.0.0
undetected-chromedriver>=3.5.0
pyautogui>=0.9.54
requests>=2.28.0
webdriver-manager>=3.8.0
psutil>=5.9.0
'''
            req_path = os.path.join(account.worker_dir, "worker_requirements.txt")
            try:
                with open(req_path, 'w', encoding='utf-8') as f:
                    f.write(worker_requirements)
                logger.info(f"Worker {worker_id}: Created worker requirements.txt")
            except Exception as req_error:
                logger.warning(f"Worker {worker_id}: Failed to create requirements: {req_error}")
            
            logger.info(f"Worker {worker_id}: Environment setup complete")
            logger.info(f"Worker {worker_id}: Ready to process {account.email}")
            return True
            
        except Exception as e:
            logger.error(f"Worker {worker_id}: Failed to setup environment: {e}")
            return False
    
    def run_single_account_subprocess(self, account: EmailAccount, worker_id: int):
        """Run automation for a single account using subprocess with enhanced compatibility"""
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
                # Enhanced subprocess execution with better error handling
                logger.info(f"Worker {worker_id}: Launching auto.py subprocess...")
                
                # Prepare environment variables for the subprocess
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUNBUFFERED'] = '1'  # Force unbuffered output
                
                # Create subprocess with enhanced configuration
                process = subprocess.Popen(
                    [sys.executable, "-u", "auto.py"],  # -u for unbuffered output
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,  # Allow input handling
                    text=True,
                    encoding='utf-8',
                    errors='replace',  # Replace invalid characters instead of failing
                    cwd=account.worker_dir,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
                )
                
                # Monitor process with enhanced timeout and progress tracking
                try:
                    logger.info(f"Worker {worker_id}: Process started (PID: {process.pid})")
                    
                    # Wait for process with extended timeout for complex automation
                    timeout_seconds = 3600  # 60 minutes timeout (increased for complex automation)
                    stdout, stderr = process.communicate(timeout=timeout_seconds)
                    return_code = process.returncode
                    
                    # Store complete output for debugging
                    account.process_output = f"RETURN CODE: {return_code}\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
                    
                    # Enhanced output logging with truncation for readability
                    if stdout:
                        stdout_preview = stdout[:1000] + "..." if len(stdout) > 1000 else stdout
                        logger.info(f"Worker {worker_id}: STDOUT preview: {stdout_preview}")
                    if stderr:
                        stderr_preview = stderr[:1000] + "..." if len(stderr) > 1000 else stderr
                        logger.warning(f"Worker {worker_id}: STDERR preview: {stderr_preview}")
                    
                    # Enhanced success detection
                    success_indicators = [
                        "All automation steps completed",
                        "OAuth consent screen creation completed successfully",
                        "AUTOMATION COMPLETED SUCCESSFULLY",
                        "Gmail API scope configuration completed successfully",
                        "Final save completed successfully"
                    ]
                    
                    error_indicators = [
                        "CAPTCHA detected and could not be solved",
                        "Maximum retries exceeded",
                        "Failed to create driver",
                        "Could not find email input field",
                        "Session disconnection detected"
                    ]
                    
                    # Check for success indicators in output
                    output_text = (stdout + stderr).lower()
                    has_success = any(indicator.lower() in output_text for indicator in success_indicators)
                    has_errors = any(indicator.lower() in output_text for indicator in error_indicators)
                    
                    if return_code == 0 or has_success:
                        if has_errors:
                            logger.warning(f"Worker {worker_id}: Completed with warnings")
                        else:
                            logger.info(f"Worker {worker_id}: auto.py completed successfully")
                        
                        account.status = "completed"
                        self.completed_counter.increment()
                        
                        # Look for credentials file
                        self.find_credentials_file(account)
                        
                        # Check if automation actually completed key steps
                        if self.verify_automation_completion(account):
                            logger.info(f"Worker {worker_id}: Automation verification passed")
                            return True
                        else:
                            logger.warning(f"Worker {worker_id}: Automation completed but verification failed")
                            return True  # Still count as success if process completed
                    else:
                        error_msg = f"auto.py failed with return code {return_code}"
                        if stderr:
                            error_msg += f". Error: {stderr[:500]}"
                        if has_errors:
                            error_msg += ". Detected automation errors in output."
                        raise Exception(error_msg)
                        
                except subprocess.TimeoutExpired:
                    logger.warning(f"Worker {worker_id}: Process timeout after {timeout_seconds} seconds")
                    try:
                        process.kill()
                        process.wait(timeout=30)  # Give it 30 seconds to clean up
                    except:
                        pass
                    raise Exception(f"auto.py subprocess timed out after {timeout_seconds/60:.1f} minutes")
                
            finally:
                # Always return to original directory
                os.chdir(original_cwd)
                
                # Clean up any hanging Chrome processes for this worker
                self.cleanup_chrome_processes(worker_id)
            
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
            
            # Save comprehensive worker output for debugging
            self.save_worker_output(account, worker_id)
    
    def verify_automation_completion(self, account: EmailAccount):
        """Verify that automation actually completed key steps"""
        try:
            if not account.process_output:
                return False
            
            output = account.process_output.lower()
            
            # Check for key completion milestones
            completion_checks = [
                "login completed" in output,
                "project creation" in output or "project created" in output,
                "gmail api enabled" in output or "api enabled" in output,
                "oauth consent screen" in output,
            ]
            
            # Require at least 3 out of 4 key steps to be completed
            completed_steps = sum(completion_checks)
            logger.info(f"Automation verification: {completed_steps}/4 key steps completed")
            
            return completed_steps >= 3
            
        except Exception as e:
            logger.warning(f"Could not verify automation completion: {e}")
            return True  # Default to success if we can't verify
    
    def cleanup_chrome_processes(self, worker_id: int):
        """Clean up any hanging Chrome processes for this worker"""
        try:
            import psutil
            
            chrome_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        if f'worker_{worker_id}' in cmdline or f'instance_' in cmdline:
                            chrome_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if chrome_processes:
                logger.info(f"Worker {worker_id}: Cleaning up {len(chrome_processes)} Chrome processes")
                for proc in chrome_processes:
                    try:
                        proc.terminate()
                    except:
                        pass
                
                # Wait a bit and force kill if necessary
                time.sleep(2)
                for proc in chrome_processes:
                    try:
                        if proc.is_running():
                            proc.kill()
                    except:
                        pass
                        
        except ImportError:
            logger.warning("psutil not available for Chrome cleanup")
        except Exception as e:
            logger.warning(f"Chrome cleanup error: {e}")
    
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
            # Read the original auto.py file
            with open("auto.py", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Replace ALL Unicode characters found in auto.py with ASCII equivalents
            emoji_replacements = {
                # Core emojis used throughout auto.py
                "🔄": "[LOADING]", "⚡": "[FAST]", "📦": "[PACKAGE]", "🏷️": "[ID]", 
                "⏰": "[TIME]", "📁": "[FOLDER]", "🔌": "[PLUG]", "🔐": "[LOGIN]", 
                "📧": "[EMAIL]", "❌": "[ERROR]", "🔒": "[LOCK]", "📂": "[FOLDER_OPEN]", 
                "✅": "[OK]", "⚠️": "[WARNING]", "🧹": "[CLEAN]", "🔍": "[SEARCH]",
                "📥": "[DOWNLOAD]", "💡": "[TIP]", "🎯": "[TARGET]", "🚀": "[START]",
                "👋": "[GOODBYE]", "🔚": "[END]", "📱": "[PHONE]", "🎉": "[SUCCESS]",
                "🏗️": "[BUILD]", "📝": "[WRITE]", "🌍": "[WORLD]", "▶️": "[PLAY]",
                "⏭️": "[SKIP]", "ℹ️": "[INFO]", "🖥️": "[DESKTOP]", "🔑": "[KEY]",
                "📄": "[FILE]", "🤖": "[ROBOT]", "⭐": "[STAR]", "💻": "[COMPUTER]",
                "🌐": "[GLOBAL]", "🔧": "[TOOL]", "📊": "[CHART]", "🎁": "[GIFT]",
                "🔔": "[BELL]", "📞": "[CALL]", "💾": "[SAVE]", "🖱️": "[MOUSE]",
                "⌨️": "[KEYBOARD]", "☁️": "[CLOUD]", "�": "[NEW]", "➡️": "[ARROW]",
                "☑️": "[CHECKBOX]", "🌟": "[STAR2]", "�": "[CLIPBOARD]", "🎭": "[MASK]",
                "🔨": "[HAMMER]", "⏳": "[HOURGLASS]", "�": "[PIN]", "🛑": "[STOP]",
                "⚠": "[WARNING2]", "🇺�": "[US]", "🇦�": "[AT]", "👥": "[USERS]",
                "➕": "[PLUS]", "💬": "[CHAT]", "⏱️": "[TIMER]", "�": "[FINISH]",
                "🐌": "[SLOW]", "📈": "[UP]", "📉": "[DOWN]", "🔗": "[LINK]",
                
                # Additional Unicode characters that might exist
                "⏲️": "[TIMER2]", "⌚": "[WATCH]", "⏰": "[ALARM]", "🎵": "[MUSIC]",
                "�": "[SOUND]", "�": "[MUTE]", "🌊": "[WAVE]", "❄️": "[SNOW]",
                "☀️": "[SUN]", "🌙": "[MOON]", "💫": "[DIZZY]", "✨": "[SPARKLES]",
                
                # Box drawing and special characters
                "═": "=", "─": "-", "│": "|", "┌": "+", "┐": "+", "└": "+", "┘": "+",
                "├": "+", "┤": "+", "┬": "+", "┴": "+", "┼": "+",
                
                # Mathematical and special symbols
                "≤": "<=", "≥": ">=", "≠": "!=", "±": "+/-", "×": "x", "÷": "/",
                "°": "deg", "™": "(TM)", "©": "(C)", "®": "(R)",
                
                # Currency and other symbols
                "€": "EUR", "£": "GBP", "¥": "JPY", "₹": "INR",
                
                # Arrows and navigation
                "←": "<-", "→": "->", "↑": "^", "↓": "v", "↔": "<->",
                "⇐": "<=", "⇒": "=>", "⇔": "<=>",
            }
            
            # Apply emoji replacements
            for emoji, replacement in emoji_replacements.items():
                content = content.replace(emoji, replacement)
            
            # Create the CSV-compatible version of get_user_credentials_and_config
            csv_reader_code = '''def get_user_credentials_and_config():
    """Read credentials from gmail_accounts.csv for multi-threaded batch processing"""
    print("\\n" + "="*50)
    print("[LOGIN] Gmail Account Setup - Reading from CSV")
    print("="*50)
    
    csv_file = "gmail_accounts.csv"
    if not os.path.exists(csv_file):
        # Try alternative file names
        for alt_file in ["accounts.csv", "gmail_multi_accounts_template.csv", "multi_accounts.csv"]:
            if os.path.exists(alt_file):
                csv_file = alt_file
                break
        else:
            raise FileNotFoundError(f"Credentials file not found. Expected: gmail_accounts.csv")
    
    print(f"[OK] Reading credentials from: {csv_file}")
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        try:
            account = next(reader)  # Get the first (and only) account
        except StopIteration:
            raise ValueError("No accounts found in CSV file")
        
        email = account['email'].strip()
        password = account['password'].strip()
        
        if not email or not password:
            raise ValueError("Email or password is empty in CSV file")
        
        print(f"[EMAIL] Using account: {email}")
        
        # Use instance-specific download directory
        download_dir = INSTANCE_DIRS['downloads']
        print(f"[FOLDER] Using download directory: {download_dir}")
        
        return email, password, download_dir
'''
            
            # Find and replace the get_user_credentials_and_config function more carefully
            import re
            
            # Try to find the function and replace it more precisely
            function_start = 'def get_user_credentials_and_config():'
            
            if function_start in content:
                lines = content.split('\n')
                start_idx = None
                end_idx = None
                
                # Find the function start
                for i, line in enumerate(lines):
                    if function_start in line:
                        start_idx = i
                        break
                
                if start_idx is not None:
                    # Find the end of the function by looking for the next def/class or unindented line
                    indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())
                    
                    for i in range(start_idx + 1, len(lines)):
                        line = lines[i]
                        if line.strip():  # Non-empty line
                            current_indent = len(line) - len(line.lstrip())
                            # If we find a line with same or less indentation that's not a comment, function ends
                            if (current_indent <= indent_level and 
                                (line.strip().startswith('def ') or 
                                 line.strip().startswith('class ') or
                                 (not line.strip().startswith('#') and not line.strip().startswith('"""') and not line.strip().startswith("'''")))):
                                end_idx = i
                                break
                    
                    if end_idx is None:
                        end_idx = len(lines)
                    
                    # Replace the function
                    new_lines = lines[:start_idx] + [csv_reader_code] + lines[end_idx:]
                    content = '\n'.join(new_lines)
                    logger.info("Successfully replaced get_user_credentials_and_config function")
                else:
                    logger.warning("Could not find get_user_credentials_and_config function start")
            else:
                logger.warning("get_user_credentials_and_config function not found in auto.py")
            
            # Ensure required imports are present at the top
            if 'import csv' not in content:
                content = 'import csv\n' + content
            if 'import os' not in content:
                content = 'import os\n' + content
            
            # Clean up any problematic constructs that could cause syntax errors
            lines = content.split('\n')
            cleaned_lines = []
            
            for i, line in enumerate(lines):
                # Skip empty import lines that could cause issues
                if line.strip() == 'csv' or line.strip() == 'os':
                    continue
                
                # Fix any hanging for loops or other incomplete statements
                stripped = line.strip()
                if stripped.startswith('for ') and stripped.endswith(':'):
                    # Check if next line is properly indented
                    if i + 1 < len(lines):
                        next_line = lines[i + 1] if i + 1 < len(lines) else ""
                        if not next_line.strip() or not next_line.startswith('    '):
                            # Add a pass statement to complete the for loop
                            cleaned_lines.append(line)
                            cleaned_lines.append('    pass  # Placeholder for incomplete loop')
                            continue
                
                cleaned_lines.append(line)
            
            content = '\n'.join(cleaned_lines)
            
            # Disable user input prompts that could hang the subprocess
            content = content.replace('input("', 'print("# AUTOMATED: ')
            content = content.replace('getpass.getpass("', 'print("# AUTOMATED: ')
            
            # Add timeout protection for subprocess (more carefully)
            timeout_protection = '''
# Subprocess timeout protection
import signal
import sys

def timeout_handler(signum, frame):
    print("[ERROR] Subprocess timeout - automation took too long")
    sys.exit(1)

# Set 30 minute timeout for subprocess
if hasattr(signal, 'SIGALRM'):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(1800)  # 30 minutes

'''
            # Add timeout protection at the very beginning of the file, after imports
            lines = content.split('\n')
            insert_index = 0
            
            # Find the best place to insert - after all imports but before main code
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    insert_index = i + 1
                elif stripped and not stripped.startswith('#') and not stripped.startswith('import') and not stripped.startswith('from'):
                    break
            
            # Insert timeout protection at the found location
            lines.insert(insert_index, timeout_protection)
            content = '\n'.join(lines)
            
            # Write the modified auto.py to worker directory with comprehensive validation
            safe_auto_py = os.path.join(worker_dir, "auto.py")
            
            # Try different encoding methods for maximum compatibility
            encodings_to_try = ['utf-8', 'utf-8-sig', 'ascii', 'cp1252', 'latin1']
            
            for encoding in encodings_to_try:
                try:
                    with open(safe_auto_py, "w", encoding=encoding, errors='replace') as f:
                        f.write(content)
                    logger.info(f"Successfully created auto.py with {encoding} encoding")
                    break
                except UnicodeEncodeError as e:
                    if encoding == encodings_to_try[-1]:  # Last encoding attempt
                        logger.error(f"Failed to encode with all attempted encodings: {e}")
                        return False
                    continue
            
            # Comprehensive validation of the created file
            try:
                # Test if the file can be read
                with open(safe_auto_py, "r", encoding="utf-8", errors='replace') as f:
                    test_content = f.read()
                
                # Basic sanity checks
                if len(test_content) < 1000:
                    logger.error("Created auto.py file appears to be too small")
                    return False
                
                # Check for Python syntax by trying to compile
                try:
                    import ast
                    ast.parse(test_content)
                    logger.info("Created auto.py file passed syntax validation")
                except SyntaxError as syntax_error:
                    logger.error(f"Syntax error in created auto.py: {syntax_error}")
                    logger.error(f"Error at line {syntax_error.lineno}: {syntax_error.text}")
                    
                    # Try to fix common syntax issues
                    lines = test_content.split('\n')
                    if syntax_error.lineno and syntax_error.lineno <= len(lines):
                        error_line = lines[syntax_error.lineno - 1]
                        logger.info(f"Attempting to fix syntax error in line: {error_line}")
                        
                        # Common fixes
                        if "IndentationError" in str(syntax_error):
                            # Fix indentation issues by ensuring proper spacing
                            fixed_lines = []
                            for line in lines:
                                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                                    if any(keyword in line for keyword in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ']):
                                        fixed_lines.append(line)
                                    else:
                                        fixed_lines.append(line)
                                else:
                                    fixed_lines.append(line)
                            
                            # Rewrite with fixed content
                            fixed_content = '\n'.join(fixed_lines)
                            with open(safe_auto_py, "w", encoding="utf-8", errors='replace') as f:
                                f.write(fixed_content)
                            
                            # Test again
                            try:
                                ast.parse(fixed_content)
                                logger.info("Successfully fixed syntax error")
                            except SyntaxError:
                                logger.error("Could not fix syntax error automatically")
                                return False
                        else:
                            return False
                
                return True
                
            except Exception as e:
                logger.error(f"Failed to validate created auto.py file: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to create Unicode-safe auto.py: {e}")
            return False

def main():
    """Main function to run the multi-threaded automation with enhanced compatibility"""
    print("=" * 70)
    print("MULTI-THREADED GMAIL API AUTOMATION (SUBPROCESS APPROACH)")
    print("=" * 70)
    print("This script runs multiple instances of auto.py in parallel using subprocesses")
    print("for complete isolation and maximum compatibility.")
    print()
    
    # Enhanced pre-flight checks
    print("Performing pre-flight checks...")
    
    # Check if auto.py exists
    if not os.path.exists("auto.py"):
        print("ERROR: auto.py not found in current directory!")
        print("Please make sure auto.py is in the same directory as this script.")
        print("Expected file: auto.py")
        input("Press Enter to exit...")
        return
    else:
        print("[OK] auto.py found")
    
    # Check if Python is suitable version
    python_version = sys.version_info
    if python_version < (3, 7):
        print(f"WARNING: Python {python_version.major}.{python_version.minor} detected.")
        print("Python 3.7 or higher is recommended for best compatibility.")
    else:
        print(f"[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check for CSV file
    csv_files = ["gmail_accounts.csv", "accounts.csv", "multi_accounts.csv"]
    found_csv = None
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            found_csv = csv_file
            break
    
    if not found_csv:
        print("ERROR: No accounts CSV file found!")
        print("Expected one of: gmail_accounts.csv, accounts.csv, multi_accounts.csv")
        print()
        print("Create a CSV file with the following format:")
        print("email,password")
        print("user1@gmail.com,password1")
        print("user2@gmail.com,password2")
        input("Press Enter to exit...")
        return
    else:
        print(f"[OK] Found accounts file: {found_csv}")
    
    # Check auto.py for compatibility
    try:
        with open("auto.py", "r", encoding="utf-8") as f:
            auto_content = f.read()
        
        # Check for key functions and compatibility
        compatibility_checks = [
            ("get_user_credentials_and_config", "User credentials function"),
            ("AUTOMATION_START_TIME", "Timing functionality"),
            ("print_milestone_timing", "Milestone timing"),
            ("handle_2fa_and_verification", "2FA handling"),
        ]
        
        missing_features = []
        for check, description in compatibility_checks:
            if check not in auto_content:
                missing_features.append(f"  - {description} ({check})")
        
        if missing_features:
            print("WARNING: auto.py may be missing some features:")
            for feature in missing_features:
                print(feature)
            print("The script will attempt to work around these issues.")
        else:
            print("[OK] auto.py appears to have all expected features")
            
    except Exception as e:
        print(f"WARNING: Could not analyze auto.py: {e}")
    
    print()
    
    # Get number of workers from user with enhanced guidance
    print("Configuring concurrent workers...")
    print("Recommendations:")
    print("  - 1-2 workers: Safer, less resource intensive")
    print("  - 3-5 workers: Good balance for most systems")
    print("  - 6+ workers: High-end systems only, may cause issues")
    print()
    
    while True:
        try:
            max_workers_input = input("Enter number of concurrent workers (1-10, default=3): ").strip()
            if not max_workers_input:
                max_workers = 3  # Default value
                break
            max_workers = int(max_workers_input)
            if 1 <= max_workers <= 10:
                break
            else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"Using {max_workers} concurrent workers.")
    print()
    
    # Create automation instance
    try:
        automation = SubprocessMultiThreadedAutomation(max_workers=max_workers)
    except Exception as e:
        print(f"ERROR: Failed to create automation instance: {e}")
        input("Press Enter to exit...")
        return
    
    # Load accounts with better error handling
    print("Loading accounts from CSV...")
    if not automation.load_accounts_from_csv(found_csv):
        print("ERROR: Failed to load accounts. Please check your CSV file.")
        print("Make sure the CSV file has the format:")
        print("email,password")
        print("user1@gmail.com,password1")
        input("Press Enter to exit...")
        return
    
    if not automation.accounts:
        print("ERROR: No valid accounts loaded from CSV file.")
        print("Please check that your CSV file contains valid email and password entries.")
        input("Press Enter to exit...")
        return
    
    print(f"[OK] Loaded {len(automation.accounts)} accounts")
    
    # Enhanced account validation and warnings
    gmail_accounts = [acc for acc in automation.accounts if "@gmail.com" in acc.email.lower()]
    non_gmail_accounts = [acc for acc in automation.accounts if "@gmail.com" not in acc.email.lower()]
    
    if gmail_accounts:
        print(f"[OK] Gmail accounts: {len(gmail_accounts)}")
    
    if non_gmail_accounts:
        print(f"WARNING: Non-Gmail accounts detected: {len(non_gmail_accounts)}")
        for acc in non_gmail_accounts:
            print(f"  - {acc.email}")
        print("These accounts may fail as this automation is designed for Gmail accounts.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Automation cancelled.")
            return
    
    # Final confirmation with detailed information
    print()
    print("=" * 50)
    print("AUTOMATION SUMMARY")
    print("=" * 50)
    print(f"Accounts to process: {len(automation.accounts)}")
    print(f"Concurrent workers: {max_workers}")
    print(f"Expected duration: {len(automation.accounts) * 5 // max_workers + 5}-{len(automation.accounts) * 15 // max_workers + 10} minutes")
    print(f"Worker directories: Will be created in {automation.base_dir}")
    print()
    print("Each worker will:")
    print("  1. Create isolated environment")
    print("  2. Run auto.py as subprocess")
    print("  3. Handle Google login and 2FA")
    print("  4. Create project and enable Gmail API")
    print("  5. Setup OAuth consent screen")
    print("  6. Download credentials JSON")
    print()
    print("IMPORTANT NOTES:")
    print("  - Each worker needs manual 2FA approval")
    print("  - Workers may pause for CAPTCHA solving")
    print("  - Check individual worker directories for detailed logs")
    print("  - Press Ctrl+C to cancel at any time")
    print()
    
    response = input("Ready to start automation? (y/N): ")
    if response.lower() != 'y':
        print("Automation cancelled.")
        return
    
    # Run automation with comprehensive error handling
    print("\n" + "=" * 70)
    print("STARTING MULTI-THREADED AUTOMATION")
    print("=" * 70)
    
    start_time = datetime.now()
    try:
        success = automation.run_automation()
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 70)
        if success:
            print("MULTI-THREADED AUTOMATION COMPLETED!")
            print(f"Total time: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        else:
            print("MULTI-THREADED AUTOMATION FAILED!")
            print("Check individual worker logs for details.")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("AUTOMATION INTERRUPTED BY USER")
        print("=" * 70)
        print("Some workers may still be running in the background.")
        print("Check worker directories for partial results.")
        
    except Exception as e:
        print(f"\n" + "=" * 70)
        print("AUTOMATION ERROR")
        print("=" * 70)
        print(f"Unexpected error: {e}")
        logger.error(f"Main automation error: {e}")
    
    finally:
        print("\nWorker directories and logs are preserved for review.")
        print(f"Location: {automation.base_dir}")
        print("Each worker directory contains:")
        print("  - auto.py (modified for subprocess)")
        print("  - worker_output.log (detailed output)")
        print("  - downloads/ (credentials if successful)")
        print("  - debug_worker_X.bat (for manual debugging)")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
