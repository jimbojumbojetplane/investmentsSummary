#!/usr/bin/env python3
"""
Two-Stage Workflow Orchestrator
Runs both Stage 1 (MCP data collection) and Stage 2 (data processing) in sequence
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent

def run_stage1():
    """Run Stage 1: MCP Data Collection"""
    print("🚀 Starting Stage 1: MCP Data Collection")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "stage1_mcp_data_collection.py"], 
                              cwd=PROJECT_ROOT, check=True)
        print("✅ Stage 1 completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Stage 1 failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running Stage 1: {e}")
        return False

def run_stage2():
    """Run Stage 2: Data Processing"""
    print("\n🚀 Starting Stage 2: Data Processing")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "stage2_data_processing.py"], 
                              cwd=PROJECT_ROOT, check=True)
        print("✅ Stage 2 completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Stage 2 failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running Stage 2: {e}")
        return False

def main():
    """Main orchestrator function"""
    print("🚀 Two-Stage RBC Portfolio Workflow")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run Stage 1
    stage1_success = run_stage1()
    
    if not stage1_success:
        print("\n❌ Workflow failed at Stage 1")
        return False
    
    # Run Stage 2
    stage2_success = run_stage2()
    
    if not stage2_success:
        print("\n❌ Workflow failed at Stage 2")
        return False
    
    # Success
    print("\n🎉 Two-Stage Workflow Completed Successfully!")
    print("=" * 60)
    print("✅ Stage 1: MCP data collection completed")
    print("✅ Stage 2: Data processing and dashboard update completed")
    print("\n🌐 Your portfolio dashboard is now updated!")
    print("   Run: streamlit run app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    exit(0 if success else 1)
