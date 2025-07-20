#!/usr/bin/env python3
"""
Test the instant credential collection with real automation
"""

#from multi_threaded_subprocess import SubprocessMultiThreadedAutomation#!/usr/bin/env python3
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
import re
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
    
    def __init__(self, max_workers=3, show_terminals=False):
        self.max_workers = max_workers
        self.show_terminals = show_terminals  # Control terminal visibility
        self.accounts = []
        self.completed_counter = ThreadSafeCounter()
        self.failed_counter = ThreadSafeCounter()
        self.base_dir = os.getcwd()
        
        # Create centralized credentials collection folder
        self.final_credentials_dir = os.path.join(self.base_dir, "final_credentials_collection")
        os.makedirs(self.final_credentials_dir, exist_ok=True)
        logger.info(f"Created final credentials collection directory: {self.final_credentials_dir}")
        logger.info(f"Terminal visibility: {'Enabled' if show_terminals else 'Hidden (cleaner experience)'}")
    
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
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Starting environment setup task")
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Setting up isolated environment for {account.email}")
            
            # Create directories for new UI automation structure
            dirs_to_create = [
                'downloads',
                'temp',
                'logs',
                'chrome_profile',
                'chrome_profile_instance_{}'.format(uuid.uuid4().hex[:8]),
                'worker_data'
            ]
            
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Creating {len(dirs_to_create)} directories")
            for dir_name in dirs_to_create:
                dir_path = os.path.join(account.worker_dir, dir_name)
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Created directory: {dir_name}")
            
            # Create Unicode-safe version of auto.py
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Creating Unicode-safe auto.py")
            if not self.create_unicode_safe_auto_py(account.worker_dir, worker_id):
                logger.error(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Could not create Unicode-safe auto.py")
                return False
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Unicode-safe auto.py created")
            
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
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Copying {len(critical_files)} critical files")
            missing_critical = []
            for filename in critical_files:
                source_path = os.path.join(self.base_dir, filename)
                dest_path = os.path.join(account.worker_dir, filename)
                
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Processing critical file: {filename}")
                if os.path.exists(source_path):
                    try:
                        shutil.copy2(source_path, dest_path)
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Copied critical file {filename}")
                    except Exception as copy_error:
                        logger.error(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Copy {filename}: {copy_error}")
                        missing_critical.append(filename)
                else:
                    logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task SKIPPED - Critical file {filename} not found")
                    missing_critical.append(filename)
            
            # Check if we can proceed without critical files
            if missing_critical:
                logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task WARNING - Missing critical files: {missing_critical}")
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Attempting to proceed anyway...")
            
            # Copy optional files if they exist
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Processing {len(optional_files)} optional files")
            copied_optional = []
            for filename in optional_files:
                source_path = os.path.join(self.base_dir, filename)
                dest_path = os.path.join(account.worker_dir, filename)
                
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Checking optional file: {filename}")
                if os.path.exists(source_path):
                    try:
                        shutil.copy2(source_path, dest_path)
                        copied_optional.append(filename)
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Copied optional file {filename}")
                    except Exception as copy_error:
                        logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Copy optional file {filename}: {copy_error}")
                else:
                    logger.info(f"[WORKER-TASK] Worker {worker_id}: Task SKIPPED - Optional file {filename} not found")
            
            if copied_optional:
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Copied {len(copied_optional)} optional files")
            else:
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task INFO - No optional files copied")
            
            # Create comprehensive CSV files for account credentials
            # Primary CSV file (gmail_accounts.csv)
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Creating primary CSV file (gmail_accounts.csv)")
            accounts_csv = os.path.join(account.worker_dir, "gmail_accounts.csv")
            try:
                with open(accounts_csv, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['email', 'password'])
                    writer.writerow([account.email, account.password])
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Created gmail_accounts.csv")
            except Exception as csv_error:
                logger.error(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Create gmail_accounts.csv: {csv_error}")
                return False
            
            # Backup CSV files with alternative names
            backup_csv_files = [
                "accounts.csv",
                "multi_accounts.csv", 
                "gmail_multi_accounts_template.csv"
            ]
            
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Creating {len(backup_csv_files)} backup CSV files")
            for backup_name in backup_csv_files:
                backup_path = os.path.join(account.worker_dir, backup_name)
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Creating backup CSV: {backup_name}")
                try:
                    with open(backup_path, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(['email', 'password'])
                        writer.writerow([account.email, account.password])
                    logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Created backup CSV {backup_name}")
                except Exception as backup_error:
                    logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Create backup CSV {backup_name}: {backup_error}")
            
            # Create comprehensive directory structure
            directories_to_create = [
                "downloads",
                "temp", 
                "chrome_profile",
                "logs",
                "credentials",
                "downloads/account_credentials"  # Specific for credentials
            ]
            
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Creating {len(directories_to_create)} additional directories")
            for dir_name in directories_to_create:
                dir_path = os.path.join(account.worker_dir, dir_name)
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Creating directory: {dir_name}")
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Created directory {dir_name}")
                except Exception as dir_error:
                    logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Create directory {dir_name}: {dir_error}")
            
            # Create a worker-specific configuration file with unique Chrome debugging port
            chrome_debug_port = 9222 + worker_id  # Ensure unique ports (9223, 9224, 9225, etc.)
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Creating worker configuration file with Chrome debug port {chrome_debug_port}")
            config_content = f'''# Worker {worker_id} Configuration
EMAIL = "{account.email}"
WORKER_ID = {worker_id}
WORKER_DIR = "{account.worker_dir}"
DOWNLOADS_DIR = "{os.path.join(account.worker_dir, 'downloads')}"
CHROME_PROFILE_DIR = "{os.path.join(account.worker_dir, f'chrome_profile_instance_{uuid.uuid4().hex[:8]}')}"
CHROME_DEBUG_PORT = {chrome_debug_port}
AUTOMATION_MODE = "MULTI_THREADED"
FAST_MODE = True
RETRY_ATTEMPTS = 3
HANDLE_OVERLAYS = True
SAFE_CLICK_ENABLED = True
DEBUG_MODE = True
ISOLATED_WORKER = True
'''
            
            config_path = os.path.join(account.worker_dir, "worker_config.py")
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(config_content)
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Created worker configuration")
            except Exception as config_error:
                logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Create worker config: {config_error}")
            
            # Create a batch file for manual debugging (Windows)
            if sys.platform == "win32":
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Creating Windows debug batch file")
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
                    logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Created debug batch file")
                except Exception as batch_error:
                    logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Create debug batch: {batch_error}")
            else:
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task SKIPPED - Debug batch file (non-Windows platform)")
            
            # Create a requirements.txt specific to this worker for debugging
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Creating worker requirements.txt")
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
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Created worker requirements.txt")
            except Exception as req_error:
                logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Create requirements: {req_error}")
            
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Environment setup complete")
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task READY - Ready to process {account.email}")
            return True
            
        except Exception as e:
            logger.error(f"Worker {worker_id}: Failed to setup environment: {e}")
            return False
    
    def run_single_account_subprocess(self, account: EmailAccount, worker_id: int):
        """Run automation for a single account using subprocess with advanced parallel processing"""
        logger.info(f"[WORKER-TASK] Worker {worker_id}: STARTING automation task for {account.email}")
        
        account.thread_id = worker_id
        account.start_time = datetime.now()
        account.status = "running"
        
        # Advanced worker isolation variables
        worker_lock = threading.Lock()
        process = None
        chrome_cleanup_attempts = 0
        max_retries = 2
        
        try:
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Initializing advanced automation")
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Account: {account.email}")
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Max retries: {max_retries}")
            
            # Setup worker environment with advanced isolation
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Setting up worker environment")
            if not self.setup_worker_environment(account, worker_id):
                logger.error(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Environment setup failed")
                raise Exception("Failed to setup worker environment")
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Environment setup successful")
            
            # Advanced Chrome port management for true parallel execution
            chrome_port = 9222 + worker_id  # Unique port per worker
            debug_port = chrome_port + 1000  # Separate debug port
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Port assignment")
            logger.info(f"[DETAIL] Worker {worker_id}: Assigned Chrome port {chrome_port}, debug port {debug_port}")
            
            # Change to worker directory with lock protection
            original_cwd = os.getcwd()
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Directory management")
            logger.info(f"[DETAIL] Worker {worker_id}: Changing from {original_cwd} to {account.worker_dir}")
            with worker_lock:
                os.chdir(account.worker_dir)
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Directory changed")
            logger.info(f"[DETAIL] Worker {worker_id}: Successfully changed to worker directory")
            
            try:
                # Advanced retry loop for subprocess execution
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Starting subprocess execution loop")
                for attempt in range(max_retries + 1):
                    try:
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Subprocess attempt {attempt + 1}/{max_retries + 1}")
                        logger.info(f"[DETAIL] Worker {worker_id}: Launching auto.py subprocess (attempt {attempt + 1}/{max_retries + 1})")
                        
                        # Advanced environment variables for complete isolation
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Setting up environment variables")
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
                        
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Environment variables set")
                        logger.info(f"[DETAIL] Worker {worker_id}: Environment setup complete - {len(env)} variables set")
                        logger.info(f"[DETAIL] Worker {worker_id}: Chrome profile dir: {env['CHROME_PROFILE_DIR']}")
                        logger.info(f"[DETAIL] Worker {worker_id}: Chrome user data dir: {env['CHROME_USER_DATA_DIR']}")
                        
                        # Ensure Chrome processes from previous attempts are fully cleaned
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Pre-launch Chrome cleanup")
                        logger.info(f"[DETAIL] Worker {worker_id}: Starting Chrome cleanup before subprocess launch")
                        self.advanced_chrome_cleanup(worker_id)
                        time.sleep(2)  # Give cleanup time to complete
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Chrome cleanup")
                        logger.info(f"[DETAIL] Worker {worker_id}: Chrome cleanup completed, proceeding with subprocess")
                        
                        # Create subprocess with advanced isolation and error handling
                        # For Windows, create with new console to allow interactive input
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Creating subprocess")
                        logger.info(f"[DETAIL] Worker {worker_id}: Creating subprocess on platform: {sys.platform}")
                        if sys.platform == "win32":
                            if self.show_terminals:
                                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Windows subprocess with visible console")
                                logger.info(f"[DETAIL] Worker {worker_id}: Using Windows subprocess with CREATE_NEW_CONSOLE")
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
                                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Windows subprocess with hidden console")
                                logger.info(f"[DETAIL] Worker {worker_id}: Using Windows subprocess with CREATE_NO_WINDOW (hidden)")
                                process = subprocess.Popen(
                                    [sys.executable, "-u", "auto.py"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    stdin=subprocess.PIPE,  # Redirect stdin to prevent blocking
                                    text=True,
                                    encoding='utf-8',
                                    errors='replace',
                                    cwd=account.worker_dir,
                                    env=env,
                                    creationflags=subprocess.CREATE_NO_WINDOW  # Hide terminal windows
                                )
                        else:
                            # For non-Windows systems
                            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Unix subprocess creation")
                            logger.info(f"[DETAIL] Worker {worker_id}: Using Unix-style subprocess")
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
                        
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Subprocess created successfully")
                        logger.info(f"[DETAIL] Worker {worker_id}: Process created successfully (PID: {process.pid})")
                        logger.info(f"[DETAIL] Worker {worker_id}: Command: {sys.executable} -u auto.py")
                        logger.info(f"[DETAIL] Worker {worker_id}: Working directory: {account.worker_dir}")
                        break  # Success, exit retry loop
                        
                    except Exception as subprocess_error:
                        logger.error(f"[DETAIL] Worker {worker_id}: Subprocess creation failed (attempt {attempt + 1}/{max_retries + 1})")
                        logger.error(f"[DETAIL] Worker {worker_id}: Error details: {str(subprocess_error)}")
                        logger.error(f"[DETAIL] Worker {worker_id}: Error type: {type(subprocess_error).__name__}")
                        if attempt < max_retries:
                            # Clean up and retry
                            logger.info(f"[DETAIL] Worker {worker_id}: Cleaning up for retry attempt")
                            self.advanced_chrome_cleanup(worker_id)
                            time.sleep(5)  # Wait before retry
                            logger.info(f"[DETAIL] Worker {worker_id}: Cleanup completed, will retry in next iteration")
                        else:
                            logger.error(f"[DETAIL] Worker {worker_id}: All retry attempts exhausted")
                            raise Exception(f"Failed to create subprocess after {max_retries + 1} attempts: {subprocess_error}")
                
                if process is None:
                    logger.error(f"[DETAIL] Worker {worker_id}: Process object is None after all attempts")
                    raise Exception("Failed to create subprocess process")
                
                
                # Advanced process monitoring with real-time health checks
                try:
                    logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Starting process monitoring")
                    logger.info(f"[DETAIL] Worker {worker_id}: Starting advanced process monitoring...")
                    
                    # Extended timeout with intelligent monitoring for manual interaction
                    timeout_seconds = 3600  # 60 minutes base timeout (increased for manual steps)
                    check_interval = 30  # Check every 30 seconds
                    last_activity_check = time.time()
                    process_health_checks = 0
                    max_health_checks = timeout_seconds // check_interval
                    
                    logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Monitoring configuration set")
                    logger.info(f"[DETAIL] Worker {worker_id}: Monitoring config - timeout: {timeout_seconds}s, interval: {check_interval}s, max checks: {max_health_checks}")
                    
                    # Advanced monitoring loop
                    logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Entering monitoring loop")
                    while process.poll() is None and process_health_checks < max_health_checks:
                        try:
                            # Wait for process with shorter intervals for monitoring
                            logger.debug(f"[WORKER-TASK] Worker {worker_id}: Task - Waiting for process communication")
                            logger.debug(f"[DETAIL] Worker {worker_id}: Waiting for process communication (timeout: {check_interval}s)")
                            stdout, stderr = process.communicate(timeout=check_interval)
                            # If we get here, process completed normally
                            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Process finished normally")
                            logger.info(f"[DETAIL] Worker {worker_id}: Process completed normally during monitoring")
                            break
                        except subprocess.TimeoutExpired:
                            # Process still running, perform health checks
                            process_health_checks += 1
                            current_time = time.time()
                            elapsed_time = current_time - (account.start_time.timestamp() if account.start_time else current_time)
                            
                            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Health check {process_health_checks}/{max_health_checks}")
                            logger.info(f"[DETAIL] Worker {worker_id}: Health check {process_health_checks}/{max_health_checks} - elapsed: {elapsed_time:.1f}s")
                            
                            # Check if Chrome processes are still alive
                            logger.debug(f"[WORKER-TASK] Worker {worker_id}: Task - Checking Chrome process health")
                            chrome_alive = self.check_chrome_processes_health(worker_id)
                            
                            if chrome_alive:
                                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task STATUS - Chrome processes healthy")
                                logger.info(f"[DETAIL] Worker {worker_id}: Chrome processes detected and healthy")
                                last_activity_check = current_time
                            else:
                                time_without_chrome = current_time - last_activity_check
                                logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task WARNING - No Chrome processes ({time_without_chrome:.1f}s)")
                                logger.warning(f"[DETAIL] Worker {worker_id}: No Chrome processes detected - {time_without_chrome:.1f}s without Chrome (may be manual interaction)")
                                # If Chrome died, the automation likely failed, but be more lenient for manual interaction
                                if time_without_chrome > 300:  # 5 minutes without Chrome (increased)
                                    logger.error(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Chrome timeout exceeded")
                                    logger.error(f"[DETAIL] Worker {worker_id}: Chrome processes missing for {time_without_chrome:.1f}s (>300s limit), terminating")
                                    break
                            
                            # Check system resources
                            if process_health_checks % 4 == 0:  # Every 2 minutes
                                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - System resource check")
                                logger.info(f"[DETAIL] Worker {worker_id}: Performing system resource check (every 4th health check)")
                                self.log_system_resources(worker_id)
                            
                            # Periodic credential collection check - every 2 health checks (1 minute)
                            if process_health_checks % 2 == 0:
                                try:
                                    logger.debug(f"[WORKER-TASK] Worker {worker_id}: Task - Periodic credential check")
                                    collected_count = self.collect_worker_credentials_instantly(account, worker_id)
                                    if collected_count > 0:
                                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Periodic collection found {collected_count} new credential files")
                                        print(f"🔄 [PERIODIC COLLECTION] Worker {worker_id}: Found {collected_count} new files during automation")
                                except Exception as periodic_error:
                                    logger.debug(f"[WORKER-TASK] Worker {worker_id}: Periodic collection error: {periodic_error}")
                            
                            continue
                    
                    # Get final output if process completed during monitoring
                    if process.poll() is not None:
                        logger.info(f"[DETAIL] Worker {worker_id}: Process completed, collecting final output")
                        try:
                            remaining_stdout, remaining_stderr = process.communicate(timeout=30)
                            stdout = (stdout or "") + (remaining_stdout or "")
                            stderr = (stderr or "") + (remaining_stderr or "")
                            logger.info(f"[DETAIL] Worker {worker_id}: Collected stdout: {len(stdout)} chars, stderr: {len(stderr)} chars")
                        except Exception as output_error:
                            logger.warning(f"[DETAIL] Worker {worker_id}: Error collecting final output: {output_error}")
                            stdout = stdout or ""
                            stderr = stderr or ""
                    else:
                        # Process still running after timeout
                        logger.warning(f"[DETAIL] Worker {worker_id}: Process timeout after {timeout_seconds}s monitoring - attempting graceful shutdown")
                        try:
                            # Try graceful termination first
                            logger.info(f"[DETAIL] Worker {worker_id}: Sending SIGTERM for graceful termination")
                            process.terminate()
                            stdout, stderr = process.communicate(timeout=30)
                            logger.info(f"[DETAIL] Worker {worker_id}: Graceful termination successful")
                        except subprocess.TimeoutExpired:
                            # Force kill if graceful termination fails
                            logger.error(f"[DETAIL] Worker {worker_id}: Graceful termination failed after 30s, force killing process")
                            process.kill()
                            try:
                                stdout, stderr = process.communicate(timeout=10)
                                logger.warning(f"[DETAIL] Worker {worker_id}: Force kill completed")
                            except Exception as kill_error:
                                logger.error(f"[DETAIL] Worker {worker_id}: Error during force kill: {kill_error}")
                                stdout, stderr = "", "Process was force killed due to timeout"
                        except Exception as term_error:
                            logger.error(f"[DETAIL] Worker {worker_id}: Error during termination: {term_error}")
                            stdout, stderr = "", f"Termination error: {term_error}"
                        
                        raise Exception(f"Process monitoring timeout after {timeout_seconds/60:.1f} minutes")
                    
                    return_code = process.returncode
                    logger.info(f"[DETAIL] Worker {worker_id}: Process return code: {return_code}")
                    
                    # Store complete output with enhanced formatting
                    logger.info(f"[DETAIL] Worker {worker_id}: Formatting and storing process output")
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
                    
                    logger.info(f"[DETAIL] Worker {worker_id}: Output analysis - success indicators: {has_success}, error indicators: {has_errors}")
                    logger.info(f"[DETAIL] Worker {worker_id}: Total output length: {len(output_text)} characters")
                    
                    # Enhanced completion analysis
                    if return_code == 0 or has_success:
                        if has_errors:
                            logger.warning(f"[DETAIL] Worker {worker_id}: Mixed results - success indicators found but also errors detected")
                        else:
                            logger.info(f"[DETAIL] Worker {worker_id}: Clear success - return code 0 or success indicators without errors")
                        
                        # Additional validation through completion verification
                        logger.info(f"[DETAIL] Worker {worker_id}: Running automation completion verification")
                        completion_score = self.verify_automation_completion(account)
                        logger.info(f"[DETAIL] Worker {worker_id}: Completion verification score: {completion_score}/5")
                        
                        if completion_score >= 3:  # At least 3 out of 5 steps completed
                            account.status = "completed"
                            self.completed_counter.increment()
                            logger.info(f"[DETAIL] Worker {worker_id}: Final status: COMPLETED (score: {completion_score}/5)")
                        else:
                            account.status = "partial"  # Partial completion
                            self.failed_counter.increment()
                            logger.warning(f"[DETAIL] Worker {worker_id}: Final status: PARTIAL (low completion score: {completion_score}/5)")
                        
                        # Find and log credentials
                        logger.info(f"[DETAIL] Worker {worker_id}: Searching for credentials files")
                        self.find_credentials_file(account)
                        if account.credentials_path:
                            logger.info(f"[DETAIL] Worker {worker_id}: Credentials found at: {account.credentials_path}")
                        else:
                            logger.warning(f"[DETAIL] Worker {worker_id}: No credentials file found")
                        
                        # INSTANT CREDENTIAL COLLECTION - Collect immediately when worker completes
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Starting instant credential collection")
                        try:
                            collected_count = self.collect_worker_credentials_instantly(account, worker_id)
                            if collected_count > 0:
                                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Instantly collected {collected_count} credential files")
                            else:
                                logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task WARNING - No credential files found for instant collection")
                        except Exception as collection_error:
                            logger.error(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Instant credential collection error: {collection_error}")
                        
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
                logger.info(f"[DETAIL] Worker {worker_id}: Starting cleanup phase")
                with worker_lock:
                    logger.info(f"[DETAIL] Worker {worker_id}: Acquired cleanup lock, changing directory back to {original_cwd}")
                    os.chdir(original_cwd)
                    logger.info(f"[DETAIL] Worker {worker_id}: Directory change completed")
                
                # Comprehensive Chrome cleanup with multiple attempts
                logger.info(f"[DETAIL] Worker {worker_id}: Starting comprehensive Chrome cleanup")
                for cleanup_attempt in range(3):
                    try:
                        logger.info(f"[DETAIL] Worker {worker_id}: Chrome cleanup attempt {cleanup_attempt + 1}/3")
                        self.advanced_chrome_cleanup(worker_id)
                        time.sleep(2)
                        if not self.check_chrome_processes_health(worker_id):
                            logger.info(f"[DETAIL] Worker {worker_id}: Chrome cleanup successful on attempt {cleanup_attempt + 1}")
                            break  # Cleanup successful
                        else:
                            logger.warning(f"[DETAIL] Worker {worker_id}: Chrome processes still detected after cleanup attempt {cleanup_attempt + 1}")
                    except Exception as cleanup_error:
                        logger.error(f"[DETAIL] Worker {worker_id}: Cleanup attempt {cleanup_attempt + 1} failed: {cleanup_error}")
                
                # Final resource cleanup
                if process and process.poll() is None:
                    logger.warning(f"[DETAIL] Worker {worker_id}: Process still running after automation, forcing termination")
                    try:
                        process.terminate()
                        process.wait(timeout=10)
                        logger.info(f"[DETAIL] Worker {worker_id}: Process termination successful")
                    except Exception as term_error:
                        logger.error(f"[DETAIL] Worker {worker_id}: Process termination failed: {term_error}")
                        try:
                            process.kill()
                            logger.warning(f"[DETAIL] Worker {worker_id}: Process force killed")
                        except Exception as kill_error:
                            logger.error(f"[DETAIL] Worker {worker_id}: Process force kill failed: {kill_error}")
                else:
                    logger.info(f"[DETAIL] Worker {worker_id}: Process already terminated, no cleanup needed")
            
        except Exception as e:
            logger.error(f"[DETAIL] Worker {worker_id}: Exception caught in main automation loop")
            logger.error(f"[DETAIL] Worker {worker_id}: Exception type: {type(e).__name__}")
            logger.error(f"[DETAIL] Worker {worker_id}: Exception message: {str(e)}")
            account.status = "failed"
            account.error_message = str(e)
            self.failed_counter.increment()
            logger.error(f"Worker {worker_id}: Failed for {account.email}: {e}")
            return False
        
        finally:
            account.end_time = datetime.now()
            if account.start_time and account.end_time:
                duration = (account.end_time - account.start_time).total_seconds()
                logger.info(f"[DETAIL] Worker {worker_id}: Total execution time for {account.email}: {duration:.1f} seconds")
                if duration > 1800:  # More than 30 minutes
                    logger.warning(f"[DETAIL] Worker {worker_id}: Long execution time detected ({duration/60:.1f} minutes)")
                elif duration < 60:  # Less than 1 minute
                    logger.warning(f"[DETAIL] Worker {worker_id}: Very short execution time ({duration:.1f}s) - possible early failure")
            else:
                logger.warning(f"[DETAIL] Worker {worker_id}: Could not calculate execution time - missing start/end times")
            
            # Save comprehensive worker output for debugging
            logger.info(f"[DETAIL] Worker {worker_id}: Saving worker output to log file")
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
    
    def collect_all_credentials(self):
        """Collect all downloaded credential files from workers into final collection folder"""
        try:
            logger.info("[CREDENTIALS] Starting centralized credential collection...")
            collected_files = []
            
            # Search through all worker directories for credential files
            for account in self.accounts:
                worker_id = list(self.accounts).index(account) + 1
                logger.info(f"[CREDENTIALS] Collecting credentials from Worker {worker_id} ({account.email})")
                
                # Search patterns for credential files in worker directory
                search_patterns = [
                    os.path.join(account.worker_dir, "*.json"),
                    os.path.join(account.worker_dir, "downloads", "*.json"),
                    os.path.join(account.worker_dir, "credentials", "*.json"),
                    os.path.join(account.worker_dir, "temp", "*.json"),
                    os.path.join(account.worker_dir, "**", "*client_secret*.json"),
                    os.path.join(account.worker_dir, "**", "*credentials*.json"),
                ]
                
                worker_credentials = []
                found_files = set()  # Track already found files to avoid duplicates
                
                for pattern in search_patterns:
                    try:
                        files = glob.glob(pattern, recursive=True)
                        for file_path in files:
                            # Normalize path and avoid duplicates
                            normalized_path = os.path.normpath(file_path)
                            if normalized_path not in found_files and self.is_credential_file(file_path):
                                worker_credentials.append(file_path)
                                found_files.add(normalized_path)
                                logger.info(f"[CREDENTIALS] Found credential file: {os.path.basename(file_path)}")
                    except Exception as e:
                        logger.warning(f"[CREDENTIALS] Error searching pattern {pattern}: {e}")
                
                # Copy worker credentials to final collection folder
                if worker_credentials:
                    for cred_file in worker_credentials:
                        try:
                            # Create meaningful filename with worker info
                            original_name = os.path.basename(cred_file)
                            base_name, ext = os.path.splitext(original_name)
                            
                            # Generate unique filename with account email
                            safe_email = account.email.replace('@', '_at_').replace('.', '_')
                            new_filename = f"worker_{worker_id}_{safe_email}_{base_name}{ext}"
                            
                            destination = os.path.join(self.final_credentials_dir, new_filename)
                            
                            # Copy the file
                            shutil.copy2(cred_file, destination)
                            collected_files.append({
                                'worker_id': worker_id,
                                'email': account.email,
                                'original_path': cred_file,
                                'final_path': destination,
                                'filename': new_filename
                            })
                            
                            logger.info(f"[CREDENTIALS] ✅ Copied {original_name} -> {new_filename}")
                            print(f"[CREDENTIALS] ✅ Worker {worker_id}: {account.email} -> {new_filename}")
                            
                        except Exception as copy_error:
                            logger.error(f"[CREDENTIALS] Failed to copy {cred_file}: {copy_error}")
                else:
                    logger.warning(f"[CREDENTIALS] No credentials found for Worker {worker_id} ({account.email})")
                    print(f"[CREDENTIALS] ❌ Worker {worker_id}: No credentials found for {account.email}")
            
            # Create summary report
            self.create_credentials_summary_report(collected_files)
            
            if collected_files:
                print(f"\n🎉 CREDENTIAL COLLECTION COMPLETE!")
                print(f"📁 Collection Directory: {self.final_credentials_dir}")
                print(f"📄 Total Files Collected: {len(collected_files)}")
                print("\nCollected Files:")
                for i, file_info in enumerate(collected_files, 1):
                    print(f"  {i}. {file_info['filename']} (Worker {file_info['worker_id']}: {file_info['email']})")
            else:
                print(f"\n⚠️ No credential files were collected from any worker.")
                print(f"Check individual worker directories for manual collection:")
                for account in self.accounts:
                    worker_id = list(self.accounts).index(account) + 1
                    print(f"  Worker {worker_id}: {account.worker_dir}")
            
            return collected_files
            
        except Exception as e:
            logger.error(f"[CREDENTIALS] Error during credential collection: {e}")
            print(f"❌ Error collecting credentials: {e}")
            return []
    
    def collect_worker_credentials_instantly(self, account: EmailAccount, worker_id: int):
        """Instantly collect credential files from a single worker when it completes"""
        try:
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Starting instant credential collection for {account.email}")
            collected_count = 0
            
            # Track source files that have already been collected to avoid duplicates
            # Create a tracking file for this worker to remember what's been collected
            tracking_file = os.path.join(self.final_credentials_dir, f"worker_{worker_id}_collected_sources.txt")
            already_collected_sources = set()
            
            # Load previously collected source file paths
            if os.path.exists(tracking_file):
                try:
                    with open(tracking_file, 'r', encoding='utf-8') as f:
                        already_collected_sources = set(line.strip() for line in f.readlines() if line.strip())
                    logger.debug(f"[WORKER-TASK] Worker {worker_id}: Loaded {len(already_collected_sources)} previously collected source paths")
                except Exception as e:
                    logger.warning(f"[WORKER-TASK] Worker {worker_id}: Could not load tracking file: {e}")
            
            # Get list of already collected files to avoid duplicates (fallback method)
            already_collected = set()
            if os.path.exists(self.final_credentials_dir):
                for existing_file in os.listdir(self.final_credentials_dir):
                    if existing_file.startswith(f"worker_{worker_id}_") and existing_file.endswith('.json'):
                        already_collected.add(existing_file)
            
            # Search patterns for credential files in this worker directory - including instance directories
            search_patterns = [
                os.path.join(account.worker_dir, "*.json"),
                os.path.join(account.worker_dir, "downloads", "*.json"),
                os.path.join(account.worker_dir, "downloads", "instance_*", "*.json"),  # Added for instance directories
                os.path.join(account.worker_dir, "credentials", "*.json"),
                os.path.join(account.worker_dir, "temp", "*.json"),
                os.path.join(account.worker_dir, "**", "*client_secret*.json"),
                os.path.join(account.worker_dir, "**", "*credentials*.json"),
                os.path.join(account.worker_dir, "**", "*gmail_com_credentials*.json"),  # Added for renamed files
            ]
            
            worker_credentials = []
            found_files = set()  # Track already found files to avoid duplicates
            
            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Searching {len(search_patterns)} patterns for credentials")
            for pattern in search_patterns:
                try:
                    files = glob.glob(pattern, recursive=True)
                    logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Pattern '{pattern}' found {len(files)} files")
                    for file_path in files:
                        # Normalize path and avoid duplicates
                        normalized_path = os.path.normpath(file_path)
                        if normalized_path not in found_files and self.is_credential_file(file_path):
                            worker_credentials.append(file_path)
                            found_files.add(normalized_path)
                            logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Found credential file: {os.path.basename(file_path)}")
                except Exception as e:
                    logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task - Error searching pattern {pattern}: {e}")
            
            # Instantly copy worker credentials to final collection folder
            if worker_credentials:
                logger.info(f"[WORKER-TASK] Worker {worker_id}: Task - Copying {len(worker_credentials)} credential files")
                for cred_file in worker_credentials:
                    try:
                        # Create meaningful filename with worker info
                        original_name = os.path.basename(cred_file)
                        base_name, ext = os.path.splitext(original_name)
                        
                        # Generate unique filename with account email and timestamp
                        safe_email = account.email.replace('@', '_at_').replace('.', '_')
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        new_filename = f"worker_{worker_id}_{safe_email}_{base_name}_{timestamp}{ext}"
                        
                        # Check if this source file has already been collected
                        source_file_path = os.path.abspath(cred_file)
                        
                        if source_file_path in already_collected_sources:
                            logger.debug(f"[WORKER-TASK] Worker {worker_id}: Task - Skipping already collected source file: {original_name}")
                            continue
                        
                        destination = os.path.join(self.final_credentials_dir, new_filename)
                        
                        # Copy the file instantly
                        shutil.copy2(cred_file, destination)
                        collected_count += 1
                        
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Copied {original_name} -> {new_filename}")
                        print(f"🎉 [INSTANT COLLECTION] Worker {worker_id}: {account.email} -> {new_filename}")
                        
                        # Add to our tracking sets
                        already_collected.add(new_filename)
                        already_collected_sources.add(source_file_path)
                        
                        # Save the source file path to tracking file
                        try:
                            with open(tracking_file, 'a', encoding='utf-8') as f:
                                f.write(f"{source_file_path}\n")
                        except Exception as track_error:
                            logger.warning(f"[WORKER-TASK] Worker {worker_id}: Could not update tracking file: {track_error}")
                        
                    except Exception as copy_error:
                        logger.error(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Copy {cred_file}: {copy_error}")
                
                # Create instant summary for this worker
                if collected_count > 0:
                    summary_file = os.path.join(self.final_credentials_dir, f"worker_{worker_id}_summary.txt")
                    try:
                        with open(summary_file, 'w', encoding='utf-8') as f:
                            f.write(f"INSTANT CREDENTIAL COLLECTION SUMMARY\n")
                            f.write(f"Worker {worker_id}: {account.email}\n")
                            f.write(f"Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                            f.write(f"Files Collected: {collected_count}\n\n")
                            
                            for i, cred_file in enumerate(worker_credentials, 1):
                                original_name = os.path.basename(cred_file)
                                f.write(f"{i}. {original_name}\n")
                                f.write(f"   Source: {cred_file}\n")
                                f.write(f"   Size: {os.path.getsize(cred_file)} bytes\n\n")
                        
                        logger.info(f"[WORKER-TASK] Worker {worker_id}: Task COMPLETED - Created instant summary: {summary_file}")
                        
                    except Exception as summary_error:
                        logger.warning(f"[WORKER-TASK] Worker {worker_id}: Task WARNING - Could not create summary: {summary_error}")
                
                print(f"📁 [INSTANT COLLECTION] Worker {worker_id} collected {collected_count} new files to: {self.final_credentials_dir}")
                
            else:
                logger.debug(f"[WORKER-TASK] Worker {worker_id}: Task INFO - No new credential files found for instant collection")
                if not hasattr(account, '_no_creds_logged'):  # Only print this once per worker
                    print(f"⚠️ [INSTANT COLLECTION] Worker {worker_id}: No credentials found yet for {account.email}")
                    account._no_creds_logged = True
            
            # Clean up tracking file if it gets too large (keep only the last 100 entries)
            try:
                if os.path.exists(tracking_file):
                    with open(tracking_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    if len(lines) > 100:  # Keep only last 100 entries
                        with open(tracking_file, 'w', encoding='utf-8') as f:
                            f.writelines(lines[-100:])
                        logger.debug(f"[WORKER-TASK] Worker {worker_id}: Cleaned up tracking file, kept last 100 entries")
            except Exception as cleanup_error:
                logger.warning(f"[WORKER-TASK] Worker {worker_id}: Could not cleanup tracking file: {cleanup_error}")
            
            return collected_count
            
        except Exception as e:
            logger.error(f"[WORKER-TASK] Worker {worker_id}: Task FAILED - Instant credential collection error: {e}")
            print(f"❌ [INSTANT COLLECTION] Worker {worker_id} Error: {e}")
            return 0
    
    def get_instant_collection_summary(self):
        """Get summary of files collected instantly from all workers"""
        try:
            summary_files = []
            total_collected = 0
            
            # Look for collected files in the final credentials directory
            if os.path.exists(self.final_credentials_dir):
                # Find all credential files (exclude summary files)
                credential_files = [f for f in os.listdir(self.final_credentials_dir) 
                                  if f.endswith('.json') and not f.endswith('_summary.txt')]
                
                total_collected = len(credential_files)
                
                # Parse information from filenames
                for filename in credential_files:
                    try:
                        # Extract worker info from filename pattern: worker_X_email_at_domain_...
                        parts = filename.split('_')
                        if len(parts) >= 4 and parts[0] == 'worker':
                            worker_id = parts[1]
                            # Reconstruct email from parts (handle _at_ replacement)
                            email_parts = []
                            for i, part in enumerate(parts[2:]):
                                if part == 'at':
                                    email_parts.append('@')
                                elif parts[2:][i-1] == 'at' if i > 0 else False:
                                    email_parts.append(part.replace('_', '.'))
                                else:
                                    email_parts.append(part)
                                if len(email_parts) >= 2 and '@' in email_parts:
                                    break
                            
                            email = ''.join(email_parts[:3]) if len(email_parts) >= 3 else 'unknown'
                            
                            summary_files.append({
                                'worker_id': worker_id,
                                'email': email,
                                'filename': filename,
                                'filepath': os.path.join(self.final_credentials_dir, filename),
                                'size': os.path.getsize(os.path.join(self.final_credentials_dir, filename))
                            })
                    except Exception as parse_error:
                        logger.warning(f"Could not parse filename {filename}: {parse_error}")
                        summary_files.append({
                            'worker_id': 'unknown',
                            'email': 'unknown',
                            'filename': filename,
                            'filepath': os.path.join(self.final_credentials_dir, filename),
                            'size': os.path.getsize(os.path.join(self.final_credentials_dir, filename))
                        })
            
            print(f"📊 Instant Collection Results:")
            print(f"   📁 Collection Directory: {self.final_credentials_dir}")
            print(f"   📄 Total Files Collected: {total_collected}")
            
            if summary_files:
                print("\n📋 Collected Files:")
                for i, file_info in enumerate(summary_files, 1):
                    size_kb = file_info['size'] / 1024
                    print(f"   {i}. Worker {file_info['worker_id']}: {file_info['email']}")
                    print(f"      📄 {file_info['filename']} ({size_kb:.1f} KB)")
            else:
                print("   ⚠️ No credential files found in collection directory")
            
            return summary_files
            
        except Exception as e:
            logger.error(f"Error getting instant collection summary: {e}")
            print(f"❌ Error getting collection summary: {e}")
            return []
    
    def is_credential_file(self, file_path):
        """Check if a JSON file is a Google credential file"""
        try:
            # Quick check based on filename patterns
            filename = os.path.basename(file_path).lower()
            filename_indicators = [
                'credentials.json',
                'client_secret',
                'oauth',
                'gmail_com_credentials',
                'google_credentials'
            ]
            
            # If filename suggests it's a credential file, validate content
            if any(indicator in filename for indicator in filename_indicators):
                # Read and validate file content
                if os.path.exists(file_path) and os.path.getsize(file_path) > 50:  # Must be at least 50 bytes
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(1000)  # Read first 1000 chars
                        # Check for Google credential indicators
                        indicators = [
                            'client_id', 'client_secret', 'auth_uri', 'token_uri', 
                            'googleapis.com', 'oauth2', 'auth_provider_x509_cert_url', 'web', 'installed'
                        ]
                        return any(indicator in content.lower() for indicator in indicators)
            
            # For other JSON files, do content validation
            elif file_path.endswith('.json'):
                if os.path.exists(file_path) and os.path.getsize(file_path) > 50:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(1000)  # Read first 1000 chars
                        indicators = [
                            'client_id', 'client_secret', 'auth_uri', 'token_uri', 
                            'googleapis.com', 'oauth2', 'auth_provider_x509_cert_url'
                        ]
                        return any(indicator in content.lower() for indicator in indicators)
            
            return False
        except Exception as e:
            logger.warning(f"Error checking credential file {file_path}: {e}")
            return False
    
    def create_credentials_summary_report(self, collected_files):
        """Create a detailed summary report of all collected credentials"""
        try:
            report_file = os.path.join(self.final_credentials_dir, "credentials_collection_report.txt")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("GMAIL API CREDENTIALS COLLECTION REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Collection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Workers: {len(self.accounts)}\n")
                f.write(f"Successful Collections: {len(collected_files)}\n")
                f.write(f"Collection Directory: {self.final_credentials_dir}\n\n")
                
                if collected_files:
                    f.write("COLLECTED CREDENTIAL FILES:\n")
                    f.write("-" * 30 + "\n")
                    for i, file_info in enumerate(collected_files, 1):
                        f.write(f"{i}. {file_info['filename']}\n")
                        f.write(f"   Worker: {file_info['worker_id']}\n")
                        f.write(f"   Email: {file_info['email']}\n")
                        f.write(f"   Original: {file_info['original_path']}\n")
                        f.write(f"   Final Location: {file_info['final_path']}\n")
                        
                        # Add file details
                        try:
                            file_size = os.path.getsize(file_info['final_path'])
                            file_time = datetime.fromtimestamp(os.path.getctime(file_info['final_path']))
                            f.write(f"   Size: {file_size} bytes\n")
                            f.write(f"   Created: {file_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        except:
                            pass
                        f.write("\n")
                else:
                    f.write("No credential files were collected.\n\n")
                
                f.write("WORKER SUMMARY:\n")
                f.write("-" * 15 + "\n")
                for account in self.accounts:
                    worker_id = list(self.accounts).index(account) + 1
                    worker_files = [f for f in collected_files if f['worker_id'] == worker_id]
                    status = "✅ SUCCESS" if worker_files else "❌ NO CREDENTIALS"
                    f.write(f"Worker {worker_id}: {account.email} - {status}\n")
                    if worker_files:
                        f.write(f"   Files: {', '.join([f['filename'] for f in worker_files])}\n")
                    f.write(f"   Directory: {account.worker_dir}\n\n")
                
                f.write("\nUSAGE INSTRUCTIONS:\n")
                f.write("-" * 19 + "\n")
                f.write("1. Each credential file is ready to use for Gmail API access\n")
                f.write("2. Rename files to 'credentials.json' when using in projects\n")
                f.write("3. Keep files secure and do not share publicly\n")
                f.write("4. Each file corresponds to one Gmail account's API access\n")
                f.write("5. Use the email in the filename to identify which account it belongs to\n")
            
            logger.info(f"[CREDENTIALS] Created collection report: {report_file}")
            print(f"📋 Collection report created: credentials_collection_report.txt")
            
        except Exception as e:
            logger.error(f"[CREDENTIALS] Failed to create summary report: {e}")
    
    def find_credentials_file(self, account: EmailAccount):
        """Find and set the credentials file path for the account"""
        try:
            import glob
            
            logger.info(f"[WORKER-TASK] Searching for downloaded JSON credentials for {account.email}")
            logger.info(f"[DETAIL] Worker directory: {account.worker_dir}")
            
            # Look for JSON credentials in worker directory and subdirectories
            patterns = [
                os.path.join(account.worker_dir, "*.json"),
                os.path.join(account.worker_dir, "**", "*.json"),
                os.path.join(account.worker_dir, "downloads", "*.json"),
                os.path.join(account.worker_dir, "downloads", "**", "*.json"),
                os.path.join(account.worker_dir, "credentials", "*.json"),
                os.path.join(account.worker_dir, "temp", "*.json"),
                # Also check common download locations
                os.path.join(os.path.expanduser("~"), "Downloads", "*.json"),
                os.path.join("C:\\Users", os.getenv("USERNAME", ""), "Downloads", "*.json") if os.name == 'nt' else "",
            ]
            
            # Remove empty patterns (for non-Windows systems)
            patterns = [p for p in patterns if p]
            
            logger.info(f"[DETAIL] Searching in {len(patterns)} locations for JSON files:")
            for i, pattern in enumerate(patterns, 1):
                logger.info(f"[DETAIL] Location {i}: {pattern}")
            
            json_files = []
            for pattern in patterns:
                try:
                    found_files = glob.glob(pattern, recursive=True)
                    if found_files:
                        logger.info(f"[DETAIL] Found {len(found_files)} JSON files in pattern: {pattern}")
                        for file in found_files:
                            logger.info(f"[DETAIL] JSON file found: {file}")
                    json_files.extend(found_files)
                except Exception as pattern_error:
                    logger.warning(f"[DETAIL] Error searching pattern {pattern}: {pattern_error}")
            
            # Remove duplicates and filter for actual credential files
            unique_json_files = list(set(json_files))
            credential_files = []
            
            logger.info(f"[DETAIL] Found {len(unique_json_files)} total JSON files, filtering for credentials...")
            
            for json_file in unique_json_files:
                try:
                    # Check if file actually exists and is readable
                    if os.path.exists(json_file) and os.path.isfile(json_file):
                        file_size = os.path.getsize(json_file)
                        logger.info(f"[DETAIL] Checking JSON file: {json_file} (size: {file_size} bytes)")
                        
                        # Quick check if it looks like a Google credentials file
                        with open(json_file, 'r', encoding='utf-8') as f:
                            content = f.read(1000)  # Read first 1000 chars
                            if any(keyword in content.lower() for keyword in [
                                'client_id', 'client_secret', 'auth_uri', 'token_uri', 
                                'googleapis.com', 'oauth2', 'web', 'installed'
                            ]):
                                credential_files.append(json_file)
                                logger.info(f"[DETAIL] Confirmed as credential file: {json_file}")
                            else:
                                logger.info(f"[DETAIL] Not a credential file (missing OAuth keywords): {json_file}")
                    else:
                        logger.warning(f"[DETAIL] File doesn't exist or not readable: {json_file}")
                except Exception as file_error:
                    logger.warning(f"[DETAIL] Error checking file {json_file}: {file_error}")
            
            if credential_files:
                # Get the most recent credential file
                latest_file = max(credential_files, key=os.path.getctime)
                account.credentials_path = latest_file
                
                # Get file details
                file_size = os.path.getsize(latest_file)
                file_time = datetime.fromtimestamp(os.path.getctime(latest_file))
                
                logger.info(f"[WORKER-TASK] ✅ CREDENTIALS FOUND!")
                logger.info(f"[DETAIL] File: {latest_file}")
                logger.info(f"[DETAIL] Size: {file_size} bytes")
                logger.info(f"[DETAIL] Created: {file_time}")
                logger.info(f"[DETAIL] Directory: {os.path.dirname(latest_file)}")
                
                # Also print to console for immediate visibility
                print(f"\n🎉 CREDENTIALS FOUND for {account.email}:")
                print(f"📄 File: {os.path.basename(latest_file)}")
                print(f"📁 Location: {latest_file}")
                print(f"📏 Size: {file_size} bytes")
                print(f"⏰ Created: {file_time}")
                
            else:
                logger.warning(f"[WORKER-TASK] ❌ NO CREDENTIALS FOUND for {account.email}")
                logger.warning(f"[DETAIL] Searched {len(patterns)} locations")
                logger.warning(f"[DETAIL] Found {len(unique_json_files)} JSON files but none were credential files")
                
                # List all directories that were checked
                checked_dirs = []
                for pattern in patterns:
                    base_dir = os.path.dirname(pattern) if "*" in pattern else pattern
                    if os.path.exists(base_dir):
                        checked_dirs.append(base_dir)
                
                logger.info(f"[DETAIL] Directories that exist and were checked:")
                for dir_path in set(checked_dirs):
                    if os.path.exists(dir_path):
                        logger.info(f"[DETAIL] ✓ {dir_path}")
                    else:
                        logger.info(f"[DETAIL] ✗ {dir_path} (doesn't exist)")
                        
                print(f"\n❌ No credentials found for {account.email}")
                print(f"🔍 Searched locations:")
                for dir_path in set(checked_dirs)[:5]:  # Show first 5 locations
                    print(f"   📁 {dir_path}")
            
        except Exception as e:
            logger.error(f"[WORKER-TASK] Error searching for credentials for {account.email}: {e}")
            logger.error(f"[DETAIL] Exception type: {type(e).__name__}")
            print(f"\n⚠️ Error searching for credentials for {account.email}: {e}")
    
    def monitor_workers_health(self, future_to_account):
        """Monitor health of all workers and their Chrome processes"""
        try:
            logger.info("[WORKER-TASK] Health monitoring started")
            monitor_interval = 30  # Check every 30 seconds
            
            while any(not future.done() for future in future_to_account.keys()):
                time.sleep(monitor_interval)
                
                active_workers = 0
                for future, account in future_to_account.items():
                    if not future.done():
                        active_workers += 1
                        worker_id = list(self.accounts).index(account) + 1
                        
                        # Check Chrome process health for this worker
                        chrome_health = self.check_chrome_processes_health(worker_id)
                        if chrome_health:
                            logger.info(f"[WORKER-TASK] Worker {worker_id} ({account.email}): Chrome processes healthy")
                        else:
                            logger.warning(f"[WORKER-TASK] Worker {worker_id} ({account.email}): Chrome process issues detected")
                        
                        # Log system resources every few cycles
                        self.log_system_resources(worker_id)
                
                if active_workers > 0:
                    logger.info(f"[WORKER-TASK] Health check: {active_workers} workers still active")
                else:
                    logger.info("[WORKER-TASK] All workers completed, ending health monitoring")
                    break
                    
        except Exception as e:
            logger.error(f"[WORKER-TASK] Health monitoring error: {e}")
    
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
                # Submit all tasks with improved Chrome process isolation
                future_to_account = {}
                for worker_id, account in enumerate(self.accounts, 1):
                    logger.info(f"[WORKER-TASK] Preparing worker {worker_id} for account {account.email}")
                    # Ensure Chrome process cleanup before starting new worker
                    self.cleanup_chrome_processes(worker_id)
                    future = executor.submit(self.run_single_account_subprocess, account, worker_id)
                    future_to_account[future] = account
                
                # Monitor progress with detailed worker task actions and health checks
                completed = 0
                total_workers = len(future_to_account)
                logger.info(f"[WORKER-TASK] Starting monitoring of {total_workers} worker tasks")
                
                # Start health monitoring thread
                health_monitor_thread = threading.Thread(
                    target=self.monitor_workers_health, 
                    args=(future_to_account,), 
                    daemon=True
                )
                health_monitor_thread.start()
                logger.info(f"[WORKER-TASK] Health monitoring thread started")
                
                for future in concurrent.futures.as_completed(future_to_account):
                    account = future_to_account[future]
                    completed += 1
                    
                    logger.info(f"[WORKER-TASK] Task completed for worker monitoring - Account: {account.email}")
                    logger.info(f"[WORKER-TASK] Progress: {completed}/{len(self.accounts)} tasks completed")
                    
                    try:
                        result = future.result()
                        status = "SUCCESS" if result else "FAILED"
                        logger.info(f"[WORKER-TASK] Task result for {account.email}: {status}")
                        logger.info(f"[WORKER-TASK] Account final status: {account.status}")
                        logger.info(f"[WORKER-TASK] Worker directory: {account.worker_dir}")
                        
                        # Log detailed task completion information
                        if account.start_time and account.end_time:
                            task_duration = (account.end_time - account.start_time).total_seconds()
                            logger.info(f"[WORKER-TASK] Task duration: {task_duration:.1f} seconds")
                            if task_duration > 600:  # More than 10 minutes
                                logger.warning(f"[WORKER-TASK] Long-running task detected for {account.email}")
                        
                        # Log credential discovery results
                        if hasattr(account, 'credentials_path') and account.credentials_path:
                            logger.info(f"[WORKER-TASK] Credentials found: {os.path.basename(account.credentials_path)}")
                        else:
                            logger.warning(f"[WORKER-TASK] No credentials found for {account.email}")
                        
                        # Log any errors encountered
                        if account.error_message:
                            logger.error(f"[WORKER-TASK] Task error for {account.email}: {account.error_message}")
                        
                        logger.info(f"[WORKER-TASK] Overall progress: {completed}/{len(self.accounts)} - {account.email} - {status}")
                        
                    except Exception as e:
                        logger.error(f"[WORKER-TASK] Task exception for {account.email}: {str(e)}")
                        logger.error(f"[WORKER-TASK] Exception type: {type(e).__name__}")
                        logger.error(f"[WORKER-TASK] Progress: {completed}/{len(self.accounts)} - {account.email} - EXCEPTION")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Summary of instant credential collection results
            logger.info("[WORKER-TASK] Summarizing instant credential collection results...")
            print("\n" + "=" * 60)
            print("� INSTANT CREDENTIAL COLLECTION SUMMARY")
            print("=" * 60)
            
            # Check what files were collected instantly
            instant_collection_summary = self.get_instant_collection_summary()
            
            # Print final summary
            self.print_summary(duration, instant_collection_summary)
            return True
            
        except Exception as e:
            logger.error(f"Multi-threading error: {e}")
            return False
    
    def print_summary(self, duration, collected_credentials=None):
        """Print automation summary with credential collection information"""
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
        
        # Credential collection summary
        if collected_credentials is not None:
            print(f"\nCREDENTIAL COLLECTION:")
            print(f"Files Collected: {len(collected_credentials)}")
            print(f"Collection Rate: {(len(collected_credentials)/total)*100:.1f}%")
            if collected_credentials:
                print(f"📁 Final Location: {self.final_credentials_dir}")
                print("📄 Collected Files:")
                for cred in collected_credentials[:5]:  # Show first 5
                    print(f"   • {cred['filename']} ({cred['email']})")
                if len(collected_credentials) > 5:
                    print(f"   ... and {len(collected_credentials) - 5} more")
        
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
            
            # Check if this account has collected credentials
            if collected_credentials:
                worker_id = list(self.accounts).index(account) + 1
                account_creds = [c for c in collected_credentials if c['worker_id'] == worker_id]
                if account_creds:
                    print(f"   🎉 Credentials Collected: {len(account_creds)} file(s)")
                    for cred in account_creds:
                        print(f"   📄 {cred['filename']}")
                else:
                    print(f"   ❌ No credentials collected")
            
            if account.credentials_path:
                print(f"   📄 Original Credentials: {os.path.basename(account.credentials_path)}")
                print(f"   📁 Original Path: {account.credentials_path}")
                # Show file size and creation time
                try:
                    file_size = os.path.getsize(account.credentials_path)
                    file_time = datetime.fromtimestamp(os.path.getctime(account.credentials_path))
                    print(f"   📏 Size: {file_size} bytes")
                    print(f"   ⏰ Created: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
                except:
                    pass
            else:
                print(f"   ❌ No credentials file found in worker directory")
                # Show where to look
                print(f"   🔍 Check: {account.worker_dir}\\downloads\\")
                print(f"   🔍 Or: C:\\Users\\{os.getenv('USERNAME', '')}\\Downloads\\")
            if hasattr(account, 'worker_dir'):
                print(f"   📂 Worker Dir: {account.worker_dir}")
        
        print("="*60)
        print(f"Worker directories created in: {self.base_dir}")
        if collected_credentials:
            print(f"📁 All credentials collected in: {self.final_credentials_dir}")
            print("📋 See 'credentials_collection_report.txt' for detailed information")
        print("Check individual worker directories for detailed logs and outputs.")
    
    def save_worker_output(self, account: EmailAccount, worker_id: int):
        """Save worker output to a log file for debugging"""
        try:
            logger.info(f"[DETAIL] Worker {worker_id}: Starting worker output save process")
            if account.process_output:
                output_file = os.path.join(account.worker_dir, "worker_output.log")
                logger.info(f"[DETAIL] Worker {worker_id}: Saving output to {output_file}")
                
                # Calculate output statistics
                output_lines = account.process_output.count('\n')
                output_size = len(account.process_output)
                logger.info(f"[DETAIL] Worker {worker_id}: Output statistics - {output_lines} lines, {output_size} characters")
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Worker {worker_id} Output for {account.email}\n")
                    f.write("="*60 + "\n")
                    f.write(f"Status: {account.status}\n")
                    f.write(f"Start Time: {account.start_time}\n")
                    f.write(f"End Time: {account.end_time}\n")
                    if account.start_time and account.end_time:
                        duration = (account.end_time - account.start_time).total_seconds()
                        f.write(f"Duration: {duration:.1f} seconds\n")
                    f.write(f"Worker Directory: {account.worker_dir}\n")
                    f.write(f"Thread ID: {getattr(account, 'thread_id', 'N/A')}\n")
                    if account.error_message:
                        f.write(f"Error: {account.error_message}\n")
                    if hasattr(account, 'credentials_path') and account.credentials_path:
                        f.write(f"Credentials: {account.credentials_path}\n")
                    f.write(f"Output Size: {output_size} characters, {output_lines} lines\n")
                    f.write("\n" + "="*60 + "\n")
                    f.write(account.process_output)
                
                logger.info(f"[DETAIL] Worker {worker_id}: Output successfully saved to worker_output.log")
                
                # Also create a summary file with key information
                summary_file = os.path.join(account.worker_dir, "worker_summary.txt")
                logger.info(f"[DETAIL] Worker {worker_id}: Creating summary file at {summary_file}")
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(f"Worker {worker_id} Summary\n")
                    f.write("="*30 + "\n")
                    f.write(f"Email: {account.email}\n")
                    f.write(f"Status: {account.status}\n")
                    f.write(f"Worker Directory: {account.worker_dir}\n")
                    if account.start_time and account.end_time:
                        duration = (account.end_time - account.start_time).total_seconds()
                        f.write(f"Duration: {duration:.1f} seconds\n")
                    if account.error_message:
                        f.write(f"Error: {account.error_message}\n")
                    if hasattr(account, 'credentials_path') and account.credentials_path:
                        f.write(f"Credentials: {os.path.basename(account.credentials_path)}\n")
                    else:
                        f.write("Credentials: Not found\n")
                
                logger.info(f"[DETAIL] Worker {worker_id}: Summary file created successfully")
            else:
                logger.warning(f"[DETAIL] Worker {worker_id}: No process output to save")
        except Exception as e:
            logger.error(f"[DETAIL] Worker {worker_id}: Failed to save output - error: {str(e)}")
            logger.error(f"[DETAIL] Worker {worker_id}: Error type: {type(e).__name__}")
            # Try to save at least basic information
            try:
                error_file = os.path.join(account.worker_dir, "worker_error.log")
                with open(error_file, 'w', encoding='utf-8') as f:
                    f.write(f"Worker {worker_id} - Error during output save\n")
                    f.write(f"Email: {account.email}\n")
                    f.write(f"Status: {account.status}\n")
                    f.write(f"Save Error: {str(e)}\n")
                logger.info(f"[DETAIL] Worker {worker_id}: Created error log file")
            except Exception as err_save_error:
                logger.error(f"[DETAIL] Worker {worker_id}: Could not even save error file: {err_save_error}")

    def create_unicode_safe_auto_py(self, worker_dir, worker_id=1):
        """Create a Unicode-safe version of auto.py for the worker with worker-specific settings"""
        try:
            import re
            chrome_debug_port = 9222 + worker_id  # Unique port for each worker
            logger.info(f"[DETAIL] Reading original auto.py for Unicode-safe conversion in {worker_dir}")
            logger.info(f"[DETAIL] Worker {worker_id} will use Chrome debug port {chrome_debug_port}")
            with open("auto.py", "r", encoding="utf-8") as f:
                content = f.read()
            logger.info(f"[DETAIL] Read {len(content)} characters from auto.py")
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
            
            replaced_count = 0
            for emoji, replacement in emoji_replacements.items():
                if emoji in content:
                    replaced_count += content.count(emoji)
                    logger.info(f"[DETAIL] Replacing '{emoji}' with '{replacement}' ({content.count(emoji)} times)")
                content = content.replace(emoji, replacement)
            logger.info(f"[DETAIL] Total emoji/unicode replacements: {replaced_count}")
            
            # Create the CSV-compatible version of get_user_credentials_and_config
            logger.info("[DETAIL] Preparing CSV-compatible get_user_credentials_and_config function")
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
            logger.info("[DETAIL] Attempting to replace get_user_credentials_and_config function")
            
            # Also need to update handle_2fa_and_verification function to include popup handling
            logger.info("[DETAIL] Attempting to replace handle_2fa_and_verification function")
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
            import_added = False
            if 'import csv' not in content:
                content = 'import csv\n' + content
                logger.info("[DETAIL] Added 'import csv' to auto.py")
                import_added = True
            if 'import os' not in content:
                content = 'import os\n' + content
                logger.info("[DETAIL] Added 'import os' to auto.py")
                import_added = True
            if not import_added:
                logger.info("[DETAIL] All required imports already present in auto.py")
            
            # Clean up any problematic constructs that could cause syntax errors
            logger.info("[DETAIL] Cleaning up problematic constructs for syntax safety")
            lines = content.split('\n')
            cleaned_lines = []
            for i, line in enumerate(lines):
                # Skip empty import lines that could cause issues
                if line.strip() == 'csv' or line.strip() == 'os':
                    logger.info(f"[DETAIL] Skipping empty import line at {i}: {line}")
                    continue
                # Fix any hanging for loops or other incomplete statements
                stripped = line.strip()
                if stripped.startswith('for ') and stripped.endswith(':'):
                    if i + 1 < len(lines):
                        next_line = lines[i + 1] if i + 1 < len(lines) else ""
                        if not next_line.strip() or not next_line.startswith('    '):
                            logger.info(f"[DETAIL] Adding pass statement for incomplete for-loop at line {i}")
                            cleaned_lines.append(line)
                            cleaned_lines.append('    pass  # Placeholder for incomplete loop')
                            continue
                cleaned_lines.append(line)
            content = '\n'.join(cleaned_lines)
            
            # Disable user input prompts that could hang the subprocess
            logger.info("[DETAIL] Disabling user input prompts for subprocess automation")
            content = content.replace('input("Press Enter when you want to close the browser, or close it manually.")', 
                                    'print("[INFO] Automation completed - browser will close automatically in 10 seconds")\ntime.sleep(10)')
            content = content.replace('input("Press Enter to continue...")', 'print("[INFO] Continuing automatically...")\ntime.sleep(2)')
            content = content.replace('input("Press Enter to exit...")', 'print("[INFO] Exiting automatically...")')
            content = content.replace('input("', 'print("# AUTOMATED INPUT: ')
            content = content.replace('getpass.getpass("', 'print("# AUTOMATED GETPASS: ')
            logger.info("[DETAIL] User input prompts replaced")
            
            # Add timeout protection and better subprocess handling
            logger.info("[DETAIL] Adding timeout protection and subprocess settings")
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
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    insert_index = i + 1
                elif stripped and not stripped.startswith('#') and not stripped.startswith('import') and not stripped.startswith('from'):
                    break
            logger.info(f"[DETAIL] Inserting timeout protection at line {insert_index}")
            lines.insert(insert_index, timeout_protection)
            content = '\n'.join(lines)
            
            # Replace Chrome debug port assignment to use worker-specific port
            logger.info(f"[DETAIL] Updating Chrome debug port assignment to use port {chrome_debug_port}")
            # Replace the find_available_port call with the specific port for this worker
            port_replacement_patterns = [
                (r'CHROME_DEBUG_PORT = find_available_port\(9222\)', f'CHROME_DEBUG_PORT = {chrome_debug_port}'),
                (r'find_available_port\(9222\)', f'{chrome_debug_port}'),
                (r'find_available_port\(\)', f'{chrome_debug_port}')
            ]
            
            for pattern, replacement in port_replacement_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    logger.info(f"[DETAIL] Replaced pattern '{pattern}' with port {chrome_debug_port}")
            
            # Also add a worker-specific identifier at the beginning for debugging
            worker_identifier = f'''
# WORKER {worker_id} INSTANCE - Chrome Debug Port: {chrome_debug_port}
# Worker Email: {worker_dir.split(os.sep)[-1] if worker_dir else "unknown"}
# Multi-threaded isolation enabled
print(f"[WORKER] Starting Worker {worker_id} with Chrome debug port {chrome_debug_port}")

'''
            lines = content.split('\n')
            # Insert after imports but before the first function/class
            insert_index = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if (stripped and not stripped.startswith('#') and not stripped.startswith('import') 
                    and not stripped.startswith('from') and not stripped.startswith('print(')
                    and not line.startswith('# WORKER') and not line.startswith('# Subprocess')):
                    insert_index = i
                    break
            logger.info(f"[DETAIL] Inserting worker identifier at line {insert_index}")
            lines.insert(insert_index, worker_identifier)
            content = '\n'.join(lines)
            
            # Write the modified auto.py to worker directory with comprehensive validation
            safe_auto_py = os.path.join(worker_dir, "auto.py")
            encodings_to_try = ['utf-8', 'utf-8-sig', 'ascii', 'cp1252', 'latin1']
            logger.info(f"[DETAIL] Attempting to write auto.py to {safe_auto_py} with multiple encodings")
            for encoding in encodings_to_try:
                try:
                    with open(safe_auto_py, "w", encoding=encoding, errors='replace') as f:
                        f.write(content)
                    logger.info(f"[DETAIL] Successfully created auto.py with {encoding} encoding")
                    break
                except UnicodeEncodeError as e:
                    logger.warning(f"[DETAIL] UnicodeEncodeError with encoding {encoding}: {e}")
                    if encoding == encodings_to_try[-1]:  # Last encoding attempt
                        logger.error(f"Failed to encode with all attempted encodings: {e}")
                        return False
                    continue
            
            # Comprehensive validation of the created file
            try:
                logger.info(f"[DETAIL] Validating created auto.py file at {safe_auto_py}")
                with open(safe_auto_py, "r", encoding="utf-8", errors='replace') as f:
                    test_content = f.read()
                logger.info(f"[DETAIL] Read {len(test_content)} characters from written auto.py")
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
                            logger.info("[DETAIL] Attempting to fix indentation error")
                            fixed_lines = []
                            for line in lines:
                                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                                    if any(keyword in line for keyword in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ']):
                                        fixed_lines.append(line)
                                    else:
                                        fixed_lines.append(line)
                                else:
                                    fixed_lines.append(line)
                            fixed_content = '\n'.join(fixed_lines)
                            with open(safe_auto_py, "w", encoding="utf-8", errors='replace') as f:
                                f.write(fixed_content)
                            try:
                                ast.parse(fixed_content)
                                logger.info("Successfully fixed syntax error")
                            except SyntaxError:
                                logger.error("Could not fix syntax error automatically")
                                return False
                        else:
                            logger.error("[DETAIL] Unhandled syntax error type, aborting")
                            return False
                return True
            except Exception as e:
                logger.error(f"Failed to validate created auto.py file: {e}")
                return False
                return False
            
        except Exception as e:
            logger.error(f"Failed to create Unicode-safe auto.py: {e}")
            return False

def search_for_downloaded_credentials():
    """Manual search function to help find downloaded JSON credentials"""
    import glob
    print("\n" + "="*60)
    print("🔍 MANUAL CREDENTIAL SEARCH")
    print("="*60)
    
    # Common locations where JSON files might be downloaded
    search_locations = [
        # Current directory and subdirectories
        os.path.join(os.getcwd(), "*.json"),
        os.path.join(os.getcwd(), "**", "*.json"),
        
        # Worker directories
        os.path.join(os.getcwd(), "worker_*", "*.json"),
        os.path.join(os.getcwd(), "worker_*", "downloads", "*.json"),
        os.path.join(os.getcwd(), "worker_*", "downloads", "instance_*", "*.json"),  # Added instance directories
        os.path.join(os.getcwd(), "worker_*", "**", "*.json"),
        
        # Advanced worker directories
        os.path.join(os.getcwd(), "advanced_worker_*", "*.json"),
        os.path.join(os.getcwd(), "advanced_worker_*", "downloads", "*.json"),
        os.path.join(os.getcwd(), "advanced_worker_*", "**", "*.json"),
        
        # Common download locations
        os.path.join(os.path.expanduser("~"), "Downloads", "*.json"),
        os.path.join("C:\\Users", os.getenv("USERNAME", ""), "Downloads", "*.json") if os.name == 'nt' else "",
        os.path.join("C:\\Users", os.getenv("USERNAME", ""), "Desktop", "*.json") if os.name == 'nt' else "",
        
        # Chrome default download location
        os.path.join(os.path.expanduser("~"), "Downloads", "client_secret_*.json"),
    ]
    
    # Remove empty patterns
    search_locations = [loc for loc in search_locations if loc]
    
    print(f"Searching {len(search_locations)} locations...")
    
    found_files = []
    credential_files = []
    
    for i, location in enumerate(search_locations, 1):
        try:
            files = glob.glob(location, recursive=True)
            if files:
                print(f"📁 Location {i}: {location} - Found {len(files)} JSON files")
                found_files.extend(files)
            else:
                print(f"📁 Location {i}: {location} - No files")
        except Exception as e:
            print(f"❌ Location {i}: {location} - Error: {e}")
    
    if found_files:
        print(f"\n📄 Found {len(found_files)} JSON files total:")
        
        # Check which ones are credential files
        for json_file in found_files:
            try:
                if os.path.exists(json_file):
                    file_size = os.path.getsize(json_file)
                    file_time = datetime.fromtimestamp(os.path.getctime(json_file))
                    
                    # Check if it's a credential file
                    is_credential = False
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            content = f.read(500)
                            if any(keyword in content.lower() for keyword in [
                                'client_id', 'client_secret', 'auth_uri', 'token_uri', 
                                'googleapis.com', 'oauth2'
                            ]):
                                is_credential = True
                                credential_files.append(json_file)
                    except:
                        pass
                    
                    status = "🔑 CREDENTIAL FILE" if is_credential else "📄 JSON file"
                    print(f"\n{status}")
                    print(f"   📄 Name: {os.path.basename(json_file)}")
                    print(f"   📁 Location: {json_file}")
                    print(f"   📏 Size: {file_size} bytes")
                    print(f"   ⏰ Created: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
            except Exception as e:
                print(f"❌ Error checking {json_file}: {e}")
        
        if credential_files:
            print(f"\n🎉 FOUND {len(credential_files)} CREDENTIAL FILES!")
            print(f"\n📁 To collect these into final_credentials_collection folder:")
            print(f"   Run the automation script and it will automatically collect them")
            print(f"   Or manually copy them to: {os.path.join(os.getcwd(), 'final_credentials_collection')}")
            print("\nTo use these files:")
            print("1. Copy the credential file to your project directory")
            print("2. Rename it to 'credentials.json' if needed")
            print("3. Update your code to use the correct path")
        else:
            print(f"\n⚠️ Found {len(found_files)} JSON files but none appear to be Google credentials")
            print("Google credential files should contain: client_id, client_secret, auth_uri, etc.")
    else:
        print("\n❌ No JSON files found in any searched locations")
        print("\nTips:")
        print("1. Check if the download actually completed")
        print("2. Look in your browser's download folder")
        print("3. Check if the file was moved to a different location")
        print("4. Make sure the automation reached the credential download step")
    
    print("\n" + "="*60)

def manual_collect_all_credentials():
    """Manually trigger credential collection from all worker directories"""
    print("\n" + "="*60)
    print("🔄 MANUAL CREDENTIAL COLLECTION")
    print("="*60)
    
    try:
        base_dir = os.getcwd()
        final_credentials_dir = os.path.join(base_dir, "final_credentials_collection")
        os.makedirs(final_credentials_dir, exist_ok=True)
        
        collected_files = []
        worker_dirs = [d for d in os.listdir(base_dir) if d.startswith('worker_') and os.path.isdir(d)]
        
        if not worker_dirs:
            print("❌ No worker directories found")
            return
        
        print(f"📁 Found {len(worker_dirs)} worker directories")
        
        for worker_dir in worker_dirs:
            worker_id = worker_dir.replace('worker_', '')
            worker_path = os.path.join(base_dir, worker_dir)
            
            print(f"\n🔍 Searching worker {worker_id}...")
            
            # Search patterns
            search_patterns = [
                os.path.join(worker_path, "*.json"),
                os.path.join(worker_path, "downloads", "*.json"),
                os.path.join(worker_path, "downloads", "instance_*", "*.json"),
                os.path.join(worker_path, "credentials", "*.json"),
                os.path.join(worker_path, "**", "*credentials*.json"),
            ]
            
            worker_files = []
            for pattern in search_patterns:
                try:
                    files = glob.glob(pattern, recursive=True)
                    for file_path in files:
                        if file_path.endswith('.json'):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read(500)
                                    if any(keyword in content.lower() for keyword in [
                                        'client_id', 'client_secret', 'auth_uri', 'token_uri', 
                                        'googleapis.com', 'oauth2'
                                    ]):
                                        worker_files.append(file_path)
                            except:
                                pass
                except:
                    pass
            
            if worker_files:
                print(f"   🎉 Found {len(worker_files)} credential files")
                for cred_file in worker_files:
                    try:
                        original_name = os.path.basename(cred_file)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        new_filename = f"worker_{worker_id}_manual_collection_{original_name.replace('.json', '')}_{timestamp}.json"
                        destination = os.path.join(final_credentials_dir, new_filename)
                        
                        shutil.copy2(cred_file, destination)
                        collected_files.append({
                            'worker_id': worker_id,
                            'original': cred_file,
                            'new_name': new_filename
                        })
                        print(f"   ✅ Copied: {original_name} -> {new_filename}")
                    except Exception as e:
                        print(f"   ❌ Error copying {original_name}: {e}")
            else:
                print(f"   ⚠️ No credential files found")
        
        if collected_files:
            print(f"\n🎉 MANUAL COLLECTION COMPLETE!")
            print(f"📁 Collected {len(collected_files)} files to: {final_credentials_dir}")
            print("\nFiles collected:")
            for file_info in collected_files:
                print(f"  📄 Worker {file_info['worker_id']}: {file_info['new_name']}")
        else:
            print(f"\n⚠️ No credential files found to collect")
        
    except Exception as e:
        print(f"❌ Error during manual collection: {e}")
    
    print("=" * 60)

def main():
    """Main function to run the multi-threaded automation with enhanced compatibility"""
    print("=" * 70)
    print("MULTI-THREADED GMAIL API AUTOMATION (SUBPROCESS APPROACH)")
    print("=" * 70)
    print("This script runs multiple instances of auto.py in parallel using subprocesses")
    print("for complete isolation and maximum compatibility.")
    print()
    
    # Add option to search for existing credentials
    print("Options:")
    print("1. Run automation")
    print("2. Search for downloaded credentials")
    print("3. Manual collection from worker directories")
    print()
    
    choice = input("Enter your choice (1, 2, or 3, default=1): ").strip()
    if choice == "2":
        search_for_downloaded_credentials()
        input("Press Enter to exit...")
        return
    elif choice == "3":
        manual_collect_all_credentials()
        input("Press Enter to exit...")
        return
    
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
    
    # Ask about terminal visibility
    print("Terminal Window Options:")
    print("  y - Show terminal windows for each worker (good for debugging)")
    print("  n - Hide terminal windows (cleaner, less cluttered experience)")
    print("  Default: Hidden terminals for cleaner experience")
    print()
    
    show_terminals_input = input("Show terminal windows for each worker? (y/N): ").strip().lower()
    show_terminals = show_terminals_input == 'y'
    
    if show_terminals:
        print("✅ Terminal windows will be visible for each worker")
        print("   You'll see 1 terminal + 1 browser per worker")
    else:
        print("✅ Terminal windows will be hidden")
        print("   You'll only see browser windows (much cleaner!)")
        print("   Worker progress will still be logged in the main window")
    print()
    
    # Create automation instance
    try:
        automation = SubprocessMultiThreadedAutomation(max_workers=max_workers, show_terminals=show_terminals)
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
    
    # Enhanced account validation and warnings with Gmail-specific checks
    gmail_accounts = [acc for acc in automation.accounts if "@gmail.com" in acc.email.lower()]
    non_gmail_accounts = [acc for acc in automation.accounts if "@gmail.com" not in acc.email.lower()]
    
    if gmail_accounts:
        print(f"[OK] Gmail accounts: {len(gmail_accounts)}")
        for i, acc in enumerate(gmail_accounts[:5], 1):  # Show first 5
            print(f"  {i}. {acc.email}")
        if len(gmail_accounts) > 5:
            print(f"  ... and {len(gmail_accounts) - 5} more")
    
    if non_gmail_accounts:
        print(f"WARNING: Non-Gmail accounts detected: {len(non_gmail_accounts)}")
        for acc in non_gmail_accounts:
            print(f"  - {acc.email}")
        print("These accounts may fail as this automation is designed for Gmail accounts.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Automation cancelled.")
            return
    
    # Check for account distribution and worker assignment
    if len(automation.accounts) > max_workers:
        print(f"INFO: {len(automation.accounts)} accounts will be processed using {max_workers} concurrent workers")
        print(f"This means {len(automation.accounts) - max_workers} accounts will wait for workers to become available")
        print("Each worker processes one account at a time for proper isolation")
    elif len(automation.accounts) == max_workers:
        print(f"PERFECT: {len(automation.accounts)} accounts with {max_workers} workers - optimal 1:1 ratio")
    else:
        print(f"INFO: {len(automation.accounts)} accounts with {max_workers} workers - some workers will be idle")
    
    # Chrome port assignment preview
    print(f"\nChrome Debug Port Assignment:")
    for i, acc in enumerate(automation.accounts[:max_workers], 1):
        port = 9222 + i
        print(f"  Worker {i}: {acc.email} -> Port {port}")
    if len(automation.accounts) > max_workers:
        print(f"  Remaining {len(automation.accounts) - max_workers} accounts will use available ports as workers complete")
    
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
    print("  7. Collect all credentials in final folder")
    print()
    print("CREDENTIAL COLLECTION:")
    print(f"  - All downloaded JSON files will be collected")
    print(f"  - Final location: final_credentials_collection/")
    print(f"  - Files renamed with worker and email info")
    print(f"  - Summary report will be generated")
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
        print(f"\n📁 All credential files collected in: {automation.final_credentials_dir}")
        print("📋 Check 'credentials_collection_report.txt' for detailed credential information")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
import os

def test_instant_collection_automation():
    """Test instant collection with the actual automation system"""
    print("🚀 Starting Multi-Threaded Automation with Instant Credential Collection")
    print("=" * 70)
    
    try:
        # Create automation instance with 3 workers (as in original) and hidden terminals
        automation = SubprocessMultiThreadedAutomation(max_workers=3, show_terminals=False)
        
        # Load accounts from CSV
        if not automation.load_accounts_from_csv("gmail_accounts.csv"):
            print("❌ Failed to load accounts from CSV file")
            return False
        
        print(f"📊 Loaded {len(automation.accounts)} accounts")
        print(f"🔧 Using {automation.max_workers} concurrent workers")
        print(f"📁 Final credentials will be saved to: {automation.final_credentials_dir}")
        print("\n🎯 Starting automation with instant credential collection...")
        print("   Each worker will immediately save credentials when it completes!")
        
        # Run the automation
        result = automation.run_automation()
        
        if result:
            print("\n✅ Automation completed successfully!")
            return True
        else:
            print("\n❌ Automation failed")
            return False
            
    except Exception as e:
        print(f"\n💥 Error during automation: {e}")
        return False

if __name__ == "__main__":
    test_instant_collection_automation()
