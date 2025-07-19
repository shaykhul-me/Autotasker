#!/usr/bin/env python3
"""
Test the instant credential collection with real automation
"""

from multi_threaded_subprocess import SubprocessMultiThreadedAutomation
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
