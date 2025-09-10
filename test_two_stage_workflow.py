#!/usr/bin/env python3
"""
Test script for the two-stage workflow
Tests the components without actually running the full workflow
"""

import sys
from pathlib import Path

# Setup project paths
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT / "src"))

def test_stage1_components():
    """Test Stage 1 components"""
    print("🧪 Testing Stage 1: MCP Data Collection Components")
    print("=" * 50)
    
    try:
        # Import Stage 1 components
        from stage1_mcp_data_collection import Stage1MCPDataCollector
        
        # Create collector instance
        collector = Stage1MCPDataCollector()
        
        # Test 1: Generate MCP script
        print("📝 Test 1: Generating MCP script...")
        script = collector.generate_mcp_script()
        print(f"✅ Script generated ({len(script)} characters)")
        
        # Test 2: Verify account configuration
        print("📋 Test 2: Verifying account configuration...")
        print(f"✅ Configured {len(collector.accounts)} accounts:")
        for account in collector.accounts:
            print(f"   - {account['number']} ({account['type']}): {account['value']}")
        
        # Test 3: Check directory structure
        print("📁 Test 3: Checking directory structure...")
        download_dir = PROJECT_ROOT / "data" / "input" / "downloaded_files"
        if download_dir.exists():
            print(f"✅ Download directory exists: {download_dir}")
        else:
            print(f"❌ Download directory missing: {download_dir}")
            return False
        
        print("✅ Stage 1 components test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Stage 1 test failed: {e}")
        return False

def test_stage2_components():
    """Test Stage 2 components"""
    print("\n🧪 Testing Stage 2: Data Processing Components")
    print("=" * 50)
    
    try:
        # Import Stage 2 components
        from stage2_data_processing import check_input_files
        
        # Test 1: Check input files function
        print("📁 Test 1: Testing input files check...")
        files_available = check_input_files()
        if files_available:
            print("✅ Input files check passed")
        else:
            print("⚠️ No input files found (expected if Stage 1 hasn't run)")
        
        # Test 2: Check data directories
        print("📂 Test 2: Checking data directories...")
        input_dir = PROJECT_ROOT / "data" / "input" / "downloaded_files"
        output_dir = PROJECT_ROOT / "data" / "output"
        
        if input_dir.exists():
            print(f"✅ Input directory exists: {input_dir}")
        else:
            print(f"❌ Input directory missing: {input_dir}")
            return False
        
        if output_dir.exists():
            print(f"✅ Output directory exists: {output_dir}")
        else:
            print(f"❌ Output directory missing: {output_dir}")
            return False
        
        print("✅ Stage 2 components test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Stage 2 test failed: {e}")
        return False

def test_workflow_orchestrator():
    """Test the workflow orchestrator"""
    print("\n🧪 Testing Workflow Orchestrator")
    print("=" * 50)
    
    try:
        # Check if orchestrator file exists
        orchestrator_file = PROJECT_ROOT / "run_two_stage_workflow.py"
        if orchestrator_file.exists():
            print("✅ Workflow orchestrator file exists")
        else:
            print("❌ Workflow orchestrator file missing")
            return False
        
        # Check if all stage files exist
        stage1_file = PROJECT_ROOT / "stage1_mcp_data_collection.py"
        stage2_file = PROJECT_ROOT / "stage2_data_processing.py"
        
        if stage1_file.exists():
            print("✅ Stage 1 file exists")
        else:
            print("❌ Stage 1 file missing")
            return False
        
        if stage2_file.exists():
            print("✅ Stage 2 file exists")
        else:
            print("❌ Stage 2 file missing")
            return False
        
        print("✅ Workflow orchestrator test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Workflow orchestrator test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Two-Stage Workflow Components")
    print("=" * 60)
    
    stage1_success = test_stage1_components()
    stage2_success = test_stage2_components()
    orchestrator_success = test_workflow_orchestrator()
    
    print(f"\n📊 Test Results")
    print("=" * 60)
    print(f"Stage 1 Components: {'✅ PASS' if stage1_success else '❌ FAIL'}")
    print(f"Stage 2 Components: {'✅ PASS' if stage2_success else '❌ FAIL'}")
    print(f"Workflow Orchestrator: {'✅ PASS' if orchestrator_success else '❌ FAIL'}")
    
    if stage1_success and stage2_success and orchestrator_success:
        print("\n🎉 All tests passed! Two-stage workflow is ready to use.")
        print("\n📋 Next steps:")
        print("1. Run Stage 1: python3 stage1_mcp_data_collection.py")
        print("2. Run Stage 2: python3 stage2_data_processing.py")
        print("3. Or run both: python3 run_two_stage_workflow.py")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
