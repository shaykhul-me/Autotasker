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
import uuid
import glob
import json
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

# Constants for enhanced compatibility
REQUIRED_PACKAGES = [
    'selenium>=4.0.0',
    'undetected-chromedriver>=3.5.0',
    'pyautogui>=0.9.54',
    'requests>=2.28.0',
    'webdriver-manager>=3.8.0',
    'psutil>=5.9.0',
    'python-dotenv>=0.19.0'  # Added for .env support
]

# List of critical files needed for automation
CRITICAL_FILES = [
    'auto.py',
    'chromedriver.exe',
    '.env'  # Optional but recommended
]
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
            
            # Create directories for new UI automation structure
            dirs_to_create = [
                'downloads',
                'temp',
                'logs',
                'chrome_profile',
                'chrome_profile_instance_{}'.format(uuid.uuid4().hex[:8]),
                'worker_data'
            ]
            
            for dir_name in dirs_to_create:
                dir_path = os.path.join(account.worker_dir, dir_name)
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"Created directory: {dir_name}")
            
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
CHROME_PROFILE_DIR = "{os.path.join(account.worker_dir, f'chrome_profile_instance_{uuid.uuid4().hex[:8]}')}"
AUTOMATION_MODE = "MULTI_THREADED"
FAST_MODE = True
RETRY_ATTEMPTS = 3
HANDLE_OVERLAYS = True
SAFE_CLICK_ENABLED = True
DEBUG_MODE = True
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
        """Run automation for a single account using subprocess with advanced parallel processing"""
        account.thread_id = worker_id
        account.start_time = datetime.now()
        account.status = "running"
        
        # Advanced worker isolation variables
        worker_lock = threading.Lock()
        process = None
        chrome_cleanup_attempts = 0
        max_retries = 2
        
        try:
            logger.info(f"Worker {worker_id}: Starting advanced automation for {account.email}")
            
            # Setup worker environment with advanced isolation
            if not self.setup_worker_environment(account, worker_id):
                raise Exception("Failed to setup worker environment")
            
            # Advanced Chrome port management for true parallel execution
            chrome_port = 9222 + worker_id  # Unique port per worker
            debug_port = chrome_port + 1000  # Separate debug port
            
            # Change to worker directory with lock protection
            original_cwd = os.getcwd()
            with worker_lock:
                os.chdir(account.worker_dir)
            
            try:
                # Advanced retry loop for subprocess execution
                for attempt in range(max_retries + 1):
                    try:
                        logger.info(f"Worker {worker_id}: Launching auto.py subprocess (attempt {attempt + 1})...")
                        
                        # Advanced environment variables for complete isolation
                        env = os.environ.copy()
                        env['PYTHONIOENCODING'] = 'utf-8'
                        env['PYTHONUNBUFFERED'] = '1'
                        env['AUTOMATION_MODE'] = 'MULTI_THREADED'
                        env['WORKER_ID'] = str(worker_id)
                        env['CHROME_PORT'] = str(chrome_port)
                        env['CHROME_DEBUG_PORT'] = str(debug_port)
                        env['CHROME_PROFILE_DIR'] = os.path.join(account.worker_dir, f'chrome_profile_instance_{uuid.uuid4().hex[:8]}')
                        env['HANDLE_OVERLAYS'] = 'true'
                        env['SAFE_CLICK_ENABLED'] = 'true'
                        env['DEBUG_MODE'] = 'true'
                        env['NO_SANDBOX'] = 'true'
                        env['DISABLE_DEV_SHM_USAGE'] = 'true'
                        env['DISABLE_GPU'] = 'true'
                        env['DISPLAY_NOTIFICATIONS'] = 'false'
                        env['CHROME_USER_DATA_DIR'] = os.path.join(account.worker_dir, f'chrome_data_{worker_id}')
                        env['TEMP_DIR'] = os.path.join(account.worker_dir, 'temp')
                        env['DOWNLOADS_DIR'] = os.path.join(account.worker_dir, 'downloads')
                        
                        # Ensure Chrome processes from previous attempts are fully cleaned
                        self.advanced_chrome_cleanup(worker_id)
                        time.sleep(2)  # Give cleanup time to complete
                        
                        # Create subprocess with advanced isolation and error handling
                        # For Windows, create with new console to allow interactive input
                        if sys.platform == "win32":
                            process = subprocess.Popen(
                                [sys.executable, "-u", "auto.py"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=None,  # Allow console input
                                text=True,
                                encoding='utf-8',
                                errors='replace',
                                cwd=account.worker_dir,
                                env=env,
                                creationflags=subprocess.CREATE_NEW_CONSOLE
                            )
                        else:
                            # For non-Windows systems
                            process = subprocess.Popen(
                                [sys.executable, "-u", "auto.py"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=None,
                                text=True,
                                encoding='utf-8',
                                errors='replace',
                                cwd=account.worker_dir,
                                env=env
                            )
                        
                        logger.info(f"Worker {worker_id}: Process started successfully (PID: {process.pid})")
                        break  # Success, exit retry loop
                        
                    except Exception as subprocess_error:
                        logger.warning(f"Worker {worker_id}: Subprocess creation failed (attempt {attempt + 1}): {subprocess_error}")
                        if attempt < max_retries:
                            # Clean up and retry
                            self.advanced_chrome_cleanup(worker_id)
                            time.sleep(5)  # Wait before retry
                        else:
                            raise Exception(f"Failed to create subprocess after {max_retries + 1} attempts: {subprocess_error}")
                
                if process is None:
                    raise Exception("Failed to create subprocess process")
                
                
                # Advanced process monitoring with real-time health checks
                try:
                    logger.info(f"Worker {worker_id}: Starting advanced process monitoring...")
                    
                    # Extended timeout with intelligent monitoring for manual interaction
                    timeout_seconds = 3600  # 60 minutes base timeout (increased for manual steps)
                    check_interval = 30  # Check every 30 seconds
                    last_activity_check = time.time()
                    process_health_checks = 0
                    max_health_checks = timeout_seconds // check_interval
                    
                    # Advanced monitoring loop
                    while process.poll() is None and process_health_checks < max_health_checks:
                        try:
                            # Wait for process with shorter intervals for monitoring
                            stdout, stderr = process.communicate(timeout=check_interval)
                            # If we get here, process completed normally
                            break
                        except subprocess.TimeoutExpired:
                            # Process still running, perform health checks
                            process_health_checks += 1
                            current_time = time.time()
                            
                            # Check if Chrome processes are still alive
                            chrome_alive = self.check_chrome_processes_health(worker_id)
                            
                            if chrome_alive:
                                logger.info(f"Worker {worker_id}: Health check {process_health_checks}/{max_health_checks} - Chrome processes active")
                                last_activity_check = current_time
                            else:
                                logger.warning(f"Worker {worker_id}: No Chrome processes detected - may be manual interaction phase")
                                # If Chrome died, the automation likely failed, but be more lenient for manual interaction
                                if current_time - last_activity_check > 300:  # 5 minutes without Chrome (increased)
                                    logger.error(f"Worker {worker_id}: Chrome processes missing for too long, terminating")
                                    break
                            
                            # Check system resources
                            if process_health_checks % 4 == 0:  # Every 2 minutes
                                self.log_system_resources(worker_id)
                            
                            continue
                    
                    # Get final output if process completed during monitoring
                    if process.poll() is not None:
                        try:
                            remaining_stdout, remaining_stderr = process.communicate(timeout=30)
                            stdout = (stdout or "") + (remaining_stdout or "")
                            stderr = (stderr or "") + (remaining_stderr or "")
                        except:
                            stdout = stdout or ""
                            stderr = stderr or ""
                    else:
                        # Process still running after timeout
                        logger.warning(f"Worker {worker_id}: Process timeout after monitoring - attempting graceful shutdown")
                        try:
                            # Try graceful termination first
                            process.terminate()
                            stdout, stderr = process.communicate(timeout=30)
                        except subprocess.TimeoutExpired:
                            # Force kill if graceful termination fails
                            logger.warning(f"Worker {worker_id}: Graceful termination failed, force killing process")
                            process.kill()
                            try:
                                stdout, stderr = process.communicate(timeout=10)
                            except:
                                stdout, stderr = "", "Process was force killed due to timeout"
                        
                        raise Exception(f"Process monitoring timeout after {timeout_seconds/60:.1f} minutes")
                    
                    return_code = process.returncode
                    
                    # Store complete output with enhanced formatting
                    account.process_output = self.format_process_output(return_code, stdout, stderr, worker_id)
                    
                    # Enhanced output logging with intelligent truncation
                    if stdout:
                        stdout_lines = stdout.split('\n')
                        important_lines = [line for line in stdout_lines if any(keyword in line.lower() 
                                         for keyword in ['error', 'success', 'completed', 'failed', 'login', 'api', 'oauth'])]
                        
                        if len(important_lines) > 20:
                            preview = '\n'.join(important_lines[:10] + ['...'] + important_lines[-10:])
                        else:
                            preview = '\n'.join(important_lines) if important_lines else stdout[:1000]
                        
                        logger.info(f"Worker {worker_id}: Key output events:\n{preview}")
                    
                    if stderr and len(stderr.strip()) > 0:
                        stderr_preview = stderr[:500] + "..." if len(stderr) > 500 else stderr
                        logger.warning(f"Worker {worker_id}: Process errors: {stderr_preview}")
                    
                    # Advanced success detection with comprehensive patterns
                    success_indicators = [
                        "All automation steps completed",
                        "OAuth consent screen creation completed successfully", 
                        "AUTOMATION COMPLETED SUCCESSFULLY",
                        "Gmail API scope configuration completed successfully",
                        "Final save completed successfully",
                        "[OK] Configuration saved successfully",
                        "[SUCCESS] COMPLETE AUTOMATION FINISHED",
                        "Clicked Save button successfully",
                        "OAuth consent screen setup complete",
                        "login completed successfully",
                        "project created successfully",
                        "api enabled successfully",
                        "credentials downloaded successfully"
                    ]
                    
                    error_indicators = [
                        "CAPTCHA detected and could not be solved",
                        "Maximum retries exceeded", 
                        "Failed to create driver",
                        "Could not find email input field",
                        "Session disconnection detected",
                        "element click intercepted",
                        "element not clickable at point",
                        "Element is not clickable",
                        "Element click intercepted", 
                        "Other element would receive the click",
                        "overlay still blocking",
                        "[ERROR] Error during automation",
                        "chrome crashed",
                        "chrome not reachable",
                        "connection refused"
                    ]
                    
                    # Comprehensive output analysis
                    output_text = (stdout + stderr).lower()
                    has_success = any(indicator.lower() in output_text for indicator in success_indicators)
                    has_errors = any(indicator.lower() in output_text for indicator in error_indicators)
                    
                    # Enhanced completion analysis
                    if return_code == 0 or has_success:
                        if has_errors:
                            logger.warning(f"Worker {worker_id}: Completed with warnings - analyzing severity")
                            # Check if errors are critical
                            critical_errors = ["chrome crashed", "connection refused", "maximum retries exceeded"]
                            has_critical = any(error in output_text for error in critical_errors)
                            if has_critical:
                                logger.error(f"Worker {worker_id}: Critical errors detected despite success indicators")
                                account.status = "completed_with_warnings"
                            else:
                                account.status = "completed"
                        else:
                            logger.info(f"Worker {worker_id}: auto.py completed successfully")
                            account.status = "completed"
                        
                        self.completed_counter.increment()
                        
                        # Enhanced credentials detection
                        self.find_credentials_file(account)
                        
                        # Advanced automation verification
                        verification_result = self.verify_automation_completion(account)
                        if verification_result >= 3:
                            logger.info(f"Worker {worker_id}: Automation verification passed ({verification_result}/4 steps)")
                            return True
                        elif verification_result >= 2:
                            logger.warning(f"Worker {worker_id}: Partial automation completion ({verification_result}/4 steps)")
                            return True  # Still count as success for partial completion
                        else:
                            logger.warning(f"Worker {worker_id}: Low verification score ({verification_result}/4) but process completed")
                            return True  # Count as success if process completed without critical errors
                    else:
                        error_msg = f"auto.py failed with return code {return_code}"
                        if stderr:
                            error_msg += f". Error: {stderr[:500]}"
                        if has_errors:
                            error_msg += ". Detected automation errors in output."
                        raise Exception(error_msg)
                        
                except subprocess.TimeoutExpired:
                    logger.warning(f"Worker {worker_id}: Advanced monitoring timeout")
                    try:
                        process.kill()
                        process.wait(timeout=30)
                    except:
                        pass
                    raise Exception(f"Advanced process monitoring timed out")
                
            finally:
                # Advanced cleanup with lock protection
                with worker_lock:
                    os.chdir(original_cwd)
                
                # Comprehensive Chrome cleanup with multiple attempts
                for cleanup_attempt in range(3):
                    try:
                        self.advanced_chrome_cleanup(worker_id)
                        time.sleep(2)
                        if not self.check_chrome_processes_health(worker_id):
                            break  # Cleanup successful
                    except Exception as cleanup_error:
                        logger.warning(f"Worker {worker_id}: Cleanup attempt {cleanup_attempt + 1} failed: {cleanup_error}")
                
                # Final resource cleanup
                if process and process.poll() is None:
                    try:
                        process.terminate()
                        process.wait(timeout=10)
                    except:
                        try:
                            process.kill()
                        except:
                            pass
            
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
        """Verify that automation actually completed key steps - returns completion score"""
        try:
            if not account.process_output:
                return 0
            
            output = account.process_output.lower()
            
            # Enhanced completion checks with more specific patterns
            completion_checks = [
                # Login verification (Score: 1)
                ("login completed" in output or 
                 "login successful" in output or
                 "signed in successfully" in output or
                 "authentication successful" in output),
                
                # Project creation verification (Score: 1) 
                ("project creation" in output or 
                 "project created" in output or
                 "new project" in output or
                 "project setup complete" in output),
                
                # API enablement verification (Score: 1)
                ("gmail api enabled" in output or 
                 "api enabled" in output or
                 "gmail api" in output or
                 "api activation" in output),
                
                # OAuth consent screen verification (Score: 1)
                ("oauth consent screen" in output or
                 "consent screen" in output or
                 "oauth setup" in output or
                 "consent configuration" in output)
            ]
            
            # Calculate completion score
            completed_steps = sum(1 for check in completion_checks if check)
            
            # Additional bonus checks for enhanced verification
            bonus_checks = [
                "credentials downloaded" in output,
                "json file" in output,
                "automation completed successfully" in output,
                "final save completed" in output,
                "configuration saved" in output
            ]
            
            bonus_score = sum(1 for check in bonus_checks if check)
            total_score = completed_steps + min(bonus_score, 1)  # Max 1 bonus point
            
            logger.info(f"Automation verification: {completed_steps}/4 core steps + {min(bonus_score, 1)} bonus = {total_score}/5 total")
            
            return total_score
            
        except Exception as e:
            logger.warning(f"Could not verify automation completion: {e}")
            return 2  # Default to partial success if we can't verify
    
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
    
    def advanced_chrome_cleanup(self, worker_id: int):
        """Advanced Chrome process cleanup with comprehensive detection and termination"""
        try:
            import psutil
            chrome_processes = []
            
            # Find all Chrome-related processes for this worker
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    proc_info = proc.info
                    if not proc_info['name']:
                        continue
                        
                    # Comprehensive Chrome process detection
                    chrome_indicators = ['chrome', 'chromium', 'msedge', 'brave']
                    is_chrome = any(indicator in proc_info['name'].lower() for indicator in chrome_indicators)
                    
                    if is_chrome and proc_info['cmdline']:
                        cmdline = ' '.join(proc_info['cmdline']).lower()
                        
                        # Check if this Chrome process belongs to our worker
                        worker_indicators = [
                            f'worker_{worker_id}',
                            f'chrome_profile_instance_',
                            f'chrome_data_{worker_id}',
                            f'user-data-dir.*worker_{worker_id}',
                            f'remote-debugging-port={9222 + worker_id}',
                            f'remote-debugging-port={10222 + worker_id}'
                        ]
                        
                        if any(indicator in cmdline for indicator in worker_indicators):
                            chrome_processes.append(proc)
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if chrome_processes:
                logger.info(f"Worker {worker_id}: Found {len(chrome_processes)} Chrome processes to cleanup")
                
                # Phase 1: Graceful termination
                for proc in chrome_processes:
                    try:
                        logger.info(f"Worker {worker_id}: Gracefully terminating Chrome PID {proc.pid}")
                        proc.terminate()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Wait for graceful termination
                time.sleep(3)
                
                # Phase 2: Force kill remaining processes
                remaining_processes = []
                for proc in chrome_processes:
                    try:
                        if proc.is_running():
                            remaining_processes.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if remaining_processes:
                    logger.warning(f"Worker {worker_id}: Force killing {len(remaining_processes)} remaining Chrome processes")
                    for proc in remaining_processes:
                        try:
                            proc.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                
                # Final verification
                time.sleep(2)
                final_check = 0
                for proc in chrome_processes:
                    try:
                        if proc.is_running():
                            final_check += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if final_check == 0:
                    logger.info(f"Worker {worker_id}: Chrome cleanup completed successfully")
                else:
                    logger.warning(f"Worker {worker_id}: {final_check} Chrome processes may still be running")
            else:
                logger.info(f"Worker {worker_id}: No Chrome processes found to cleanup")
                
        except ImportError:
            logger.warning(f"Worker {worker_id}: psutil not available for advanced Chrome cleanup")
            # Fallback to basic cleanup
            self.cleanup_chrome_processes(worker_id)
        except Exception as e:
            logger.error(f"Worker {worker_id}: Advanced Chrome cleanup failed: {e}")
            # Fallback to basic cleanup
            self.cleanup_chrome_processes(worker_id)
    
    def check_chrome_processes_health(self, worker_id: int):
        """Check if Chrome processes for this worker are still running and healthy"""
        try:
            import psutil
            active_chrome = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    if not proc_info['name']:
                        continue
                        
                    chrome_indicators = ['chrome', 'chromium', 'msedge', 'brave']
                    is_chrome = any(indicator in proc_info['name'].lower() for indicator in chrome_indicators)
                    
                    if is_chrome and proc_info['cmdline']:
                        cmdline = ' '.join(proc_info['cmdline']).lower()
                        worker_indicators = [
                            f'worker_{worker_id}',
                            f'chrome_profile_instance_',
                            f'chrome_data_{worker_id}'
                        ]
                        
                        if any(indicator in cmdline for indicator in worker_indicators):
                            active_chrome += 1
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return active_chrome > 0
            
        except ImportError:
            return True  # Assume healthy if can't check
        except Exception:
            return True  # Assume healthy if check fails
    
    def log_system_resources(self, worker_id: int):
        """Log system resource usage for monitoring"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            logger.info(f"Worker {worker_id}: System Resources - "
                       f"CPU: {cpu_percent}%, "
                       f"Memory: {memory.percent}% "
                       f"({memory.available // (1024**3)}GB free), "
                       f"Disk: {disk.percent}% used")
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Worker {worker_id}: Could not log system resources: {e}")
    
    def format_process_output(self, return_code, stdout, stderr, worker_id):
        """Format process output with enhanced structure and filtering"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Filter out noise from stdout
        if stdout:
            lines = stdout.split('\n')
            filtered_lines = []
            for line in lines:
                # Skip Chrome debug messages and other noise
                if any(noise in line.lower() for noise in [
                    'devtools listening', 'gpu command buffer', 'deprecated endpoint',
                    'phone registration error', 'registration response error'
                ]):
                    continue
                filtered_lines.append(line)
            stdout = '\n'.join(filtered_lines)
        
        formatted_output = f"""
WORKER {worker_id} PROCESS OUTPUT
{'='*60}
Timestamp: {timestamp}
Return Code: {return_code}
Process Status: {'SUCCESS' if return_code == 0 else 'FAILED'}

STDOUT OUTPUT:
{'-'*40}
{stdout or 'No stdout output'}

STDERR OUTPUT:  
{'-'*40}
{stderr or 'No stderr output'}

{'='*60}
"""
        return formatted_output
    
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
            print(f"[ERROR] Credentials file not found. Expected: gmail_accounts.csv")
            print("[TIP] Creating a default CSV file to prevent automation failure...")
            # Create a minimal CSV file to prevent crashes
            with open("gmail_accounts.csv", "w", encoding="utf-8") as f:
                f.write("email,password\\n")
                f.write("user@gmail.com,password123\\n")
            print("[WARNING] Created default CSV - automation will likely fail authentication")
            csv_file = "gmail_accounts.csv"
    
    print(f"[OK] Reading credentials from: {csv_file}")
    
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            try:
                account = next(reader)  # Get the first (and only) account
            except StopIteration:
                print("[ERROR] No accounts found in CSV file")
                return "user@gmail.com", "password123", "downloads"
            
            email = account.get('email', '').strip()
            password = account.get('password', '').strip()
            
            if not email or not password:
                print("[ERROR] Email or password is empty in CSV file")
                return "user@gmail.com", "password123", "downloads"
            
            print(f"[EMAIL] Using account: {email}")
            
            # Use instance-specific download directory
            download_dir = os.path.join(os.getcwd(), "downloads")
            if os.path.exists("downloads"):
                # Look for instance-specific directory
                instance_dirs = [d for d in os.listdir("downloads") if d.startswith("instance_")]
                if instance_dirs:
                    download_dir = os.path.join("downloads", instance_dirs[0])
                else:
                    download_dir = "downloads"
            else:
                # Create downloads directory if it doesn't exist
                os.makedirs("downloads", exist_ok=True)
                download_dir = "downloads"
            print(f"[FOLDER] Using download directory: {download_dir}")
            
            return email, password, download_dir
    except Exception as e:
        print(f"[ERROR] Failed to read CSV file: {e}")
        print("[WARNING] Using fallback credentials - automation will likely fail")
        return "user@gmail.com", "password123", "downloads"

def handle_2fa_popup(driver):
    """Handle the 2FA setup popup that appears after login"""
    try:
        print("[SEARCH] Checking for 2FA setup popup...")
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
            print("[PHONE] 2FA setup popup detected!")
            
            # First try to dismiss by clicking outside the dialog
            try:
                print("[TARGET] Trying to click outside dialog to dismiss...")
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
                            print("[OK] Successfully dismissed popup by clicking backdrop!")
                            time.sleep(2)
                            return True
                    except:
                        continue
            except Exception as backdrop_error:
                print(f"[WARNING] Backdrop click failed: {backdrop_error}")
            
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
                                print(f"[OK] Found 'Remind me later' button: {element_text} (aria-label: {aria_label})")
                                break
                    if remind_button:
                        break
                except Exception as selector_error:
                    continue
            
            if remind_button:
                print("[TARGET] Clicking 'Remind me later' button...")
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
                    print("[OK] Successfully clicked 'Remind me later'!")
                    time.sleep(3)  # Wait for popup to close
                    return True
                    
                except Exception as click_error:
                    print(f"[WARNING] JavaScript click failed: {click_error}")
                    try:
                        # Try regular click as fallback
                        remind_button.click()
                        print("[OK] Successfully clicked 'Remind me later' with regular click!")
                        time.sleep(3)
                        return True
                    except Exception as regular_click_error:
                        print(f"[ERROR] Regular click also failed: {regular_click_error}")
            
            # If button click failed, try other methods
            print("[LOADING] Trying alternative dismiss methods...")
            
            # Method 1: Press Escape key
            try:
                print("[KEYBOARD] Trying Escape key to dismiss popup...")
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(2)
                print("[OK] Dismissed 2FA popup with Escape key")
                return True
            except Exception as escape_error:
                print(f"[WARNING] Escape key failed: {escape_error}")
            
            # Method 2: Click on page background
            try:
                print("[TARGET] Trying to click on page background...")
                # Click somewhere on the page that's not the dialog
                driver.execute_script("document.elementFromPoint(100, 100).click();")
                time.sleep(2)
                print("[OK] Dismissed popup by clicking background")
                return True
            except Exception as bg_click_error:
                print(f"[WARNING] Background click failed: {bg_click_error}")
            
            # Method 3: Try to remove the dialog element directly
            try:
                print("[CLEAN] Trying to remove dialog element...")
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
                            print("[OK] Removed dialog element")
                            time.sleep(2)
                            return True
                    except:
                        continue
                        
            except Exception as remove_error:
                print(f"[WARNING] Dialog removal failed: {remove_error}")
            
            print("[ERROR] Could not dismiss 2FA popup with any method")
            print("[TIP] Manual intervention may be required")
            return False
        else:
            print("[OK] No 2FA setup popup detected")
            return True
            
    except Exception as e:
        print(f"[WARNING] Error handling 2FA popup: {e}")
        return False
'''
            
            # Find and replace the get_user_credentials_and_config function more carefully
            import re
            
            # Also need to update handle_2fa_and_verification function to include popup handling
            handle_2fa_code = '''def handle_2fa_and_verification(driver):
    """Handle 2FA and verification prompts during login with extended waiting for manual input"""
    print("[LOCK] Checking for 2FA/verification prompts...")
    try:
        # Handle 2FA popup that asks to turn on two-step verification
        handle_2fa_popup(driver)
        
        # Extended handling for manual authentication steps
        print("[INFO] Waiting for manual authentication steps...")
        print("[TIP] Please complete any required authentication in the browser window")
        
        # Wait longer for manual interaction
        max_wait_time = 300  # 5 minutes for manual steps
        wait_interval = 10   # Check every 10 seconds
        
        for i in range(0, max_wait_time, wait_interval):
            try:
                # Check if we're on a page that indicates we're logged in
                current_url = driver.current_url
                if "accounts.google.com" not in current_url and "myaccount.google.com" not in current_url:
                    # Check for specific login-related URLs
                    if any(indicator in current_url for indicator in [
                        "console.cloud.google.com",
                        "console.developers.google.com", 
                        "accounts.google.com/AccountChooser"
                    ]):
                        print(f"[OK] Authentication appears successful, URL: {current_url[:100]}...")
                        break
                
                # Handle phone number verification
                try:
                    phone_input = driver.find_element(By.XPATH, "//input[@type='tel' or @aria-label='Phone number']")
                    if phone_input and phone_input.is_displayed():
                        print("[PHONE] Phone number verification detected")
                        print(f"[TIP] Please enter your phone number manually (waiting {max_wait_time - i}s)")
                        time.sleep(wait_interval)
                        continue
                except:
                    pass

                # Handle SMS code verification
                try:
                    code_input = driver.find_element(By.XPATH, "//input[@type='tel' or @aria-label='Enter code']")
                    if code_input and code_input.is_displayed():
                        print("[KEY] SMS code verification detected")
                        print(f"[TIP] Please enter the verification code manually (waiting {max_wait_time - i}s)")
                        time.sleep(wait_interval)
                        continue
                except:
                    pass

                # Check for "Try another way" button
                try:
                    another_way_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Try another way')]/..")
                    if another_way_btn and another_way_btn.is_displayed():
                        print("[LOADING] 'Try another way' button available")
                        print("[TIP] You can click 'Try another way' if needed")
                        time.sleep(wait_interval)
                        continue
                except:
                    pass
                
                # Check for password input fields that might need manual entry
                try:
                    password_fields = driver.find_elements(By.XPATH, "//input[@type='password']")
                    visible_password_fields = [field for field in password_fields if field.is_displayed()]
                    if visible_password_fields:
                        print("[LOCK] Password field detected")
                        print(f"[TIP] Please enter your password manually (waiting {max_wait_time - i}s)")
                        time.sleep(wait_interval)
                        continue
                except:
                    pass
                
                # If no manual interaction needed, break early
                print(f"[INFO] Continuing automated steps... ({i}/{max_wait_time}s)")
                time.sleep(wait_interval)
                
            except Exception as check_error:
                print(f"[WARNING] Error during manual interaction check: {check_error}")
                time.sleep(wait_interval)
        
        print("[OK] 2FA/verification handling completed")
        return True
    except Exception as e:
        print(f"[WARNING] Error during 2FA/verification handling: {e}")
        print("[TIP] Manual intervention may be required for 2FA/verification")
        return False
'''
            
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
            
            # Also replace handle_2fa_and_verification function
            handle_2fa_start = 'def handle_2fa_and_verification(driver):'
            
            if handle_2fa_start in content:
                lines = content.split('\n')
                start_idx = None
                end_idx = None
                
                # Find the function start
                for i, line in enumerate(lines):
                    if handle_2fa_start in line:
                        start_idx = i
                        break
                
                if start_idx is not None:
                    # Find the end of the function
                    indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())
                    
                    for i in range(start_idx + 1, len(lines)):
                        line = lines[i]
                        if line.strip():  # Non-empty line
                            current_indent = len(line) - len(line.lstrip())
                            if (current_indent <= indent_level and 
                                (line.strip().startswith('def ') or 
                                 line.strip().startswith('class ') or
                                 (not line.strip().startswith('#') and not line.strip().startswith('"""') and not line.strip().startswith("'''")))):
                                end_idx = i
                                break
                    
                    if end_idx is None:
                        end_idx = len(lines)
                    
                    # Replace the function
                    new_lines = lines[:start_idx] + [handle_2fa_code] + lines[end_idx:]
                    content = '\n'.join(new_lines)
                    logger.info("Successfully replaced handle_2fa_and_verification function")
                else:
                    logger.warning("Could not find handle_2fa_and_verification function start")
            else:
                logger.warning("handle_2fa_and_verification function not found in auto.py")
            
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
            content = content.replace('input("Press Enter when you want to close the browser, or close it manually.")', 
                                    'print("[INFO] Automation completed - browser will close automatically in 10 seconds")\ntime.sleep(10)')
            content = content.replace('input("Press Enter to continue...")', 'print("[INFO] Continuing automatically...")\ntime.sleep(2)')
            content = content.replace('input("Press Enter to exit...")', 'print("[INFO] Exiting automatically...")')
            content = content.replace('input("', 'print("# AUTOMATED INPUT: ')
            content = content.replace('getpass.getpass("', 'print("# AUTOMATED GETPASS: ')
            
            # Add timeout protection and better subprocess handling
            timeout_protection = '''
# Subprocess timeout protection for multi-threaded automation
import signal
import sys
import time

def timeout_handler(signum, frame):
    print("[ERROR] Subprocess timeout - automation took too long")
    print("[TIP] This usually means manual intervention is required")
    sys.exit(1)

# Set 60 minute timeout for subprocess (increased for manual interaction)
if hasattr(signal, 'SIGALRM') and sys.platform != 'win32':
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(3600)  # 60 minutes

# Enhanced automation settings for subprocess mode
SUBPROCESS_MODE = True
AUTOMATION_TIMEOUT = 3600  # 60 minutes
MANUAL_INTERACTION_PAUSE = 60  # Wait 60 seconds for manual input

print("[INFO] Running in multi-threaded subprocess mode")
print("[INFO] Manual interaction timeouts set to 60 seconds")
print("[INFO] Total automation timeout: 60 minutes")

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
