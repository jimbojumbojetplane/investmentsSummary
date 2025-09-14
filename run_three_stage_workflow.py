#!/usr/bin/env python3
"""
Three-Stage Workflow Orchestrator
Coordinates the execution of all three stages:
1. Stage 1: Cursor Agent Function (Manual) - RBC Holdings Collection
2. Stage 2: Benefits Data Collection (Automated)
3. Stage 3: Data Integration & Processing (Automated)
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

# Import stage modules
from stage2_benefits_data_collection import Stage2BenefitsDataCollector
from stage3_data_integration_processing import Stage3DataIntegrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / "data" / "three_stage_workflow.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ThreeStageWorkflowOrchestrator:
    """Orchestrates the three-stage workflow"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.input_dir = self.project_root / "data" / "input" / "downloaded_files"
        self.output_dir = self.project_root / "data" / "output"
    
    def check_stage1_completion(self):
        """Check if Stage 1 (Cursor Agent) has been completed"""
        try:
            logger.info("🔍 Checking Stage 1 completion...")
            
            # Check for recent CSV files in input directory
            csv_files = list(self.input_dir.glob("Holdings *.csv"))
            
            if not csv_files:
                logger.warning("⚠️  No CSV files found in input directory")
                logger.info("💡 Please run Stage 1 (Cursor Agent) first:")
                logger.info("   1. Use the MCP runbook: /Users/jgf/mcp/RBC_HOLDINGS_EXPORT_RUNBOOK_v3.md")
                logger.info("   2. Run the Cursor agent function to download RBC holdings")
                logger.info("   3. Ensure files are saved to: data/input/downloaded_files/")
                return False
            
            # Check file timestamps (files should be recent)
            recent_files = []
            cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)  # 24 hours ago
            
            for file in csv_files:
                if file.stat().st_mtime > cutoff_time:
                    recent_files.append(file)
            
            if not recent_files:
                logger.warning("⚠️  CSV files found but they are older than 24 hours")
                logger.info("💡 Consider running Stage 1 again for fresh data")
                return False
            
            logger.info(f"✅ Stage 1 completed: Found {len(recent_files)} recent CSV files")
            for file in recent_files:
                logger.info(f"   - {file.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking Stage 1: {e}")
            return False
    
    def run_stage2(self):
        """Run Stage 2: Benefits Data Collection"""
        try:
            logger.info("🏢 Running Stage 2: Benefits Data Collection")
            logger.info("-" * 50)
            
            collector = Stage2BenefitsDataCollector()
            success = collector.run_stage2()
            
            if success:
                logger.info("✅ Stage 2 completed successfully")
                return True
            else:
                logger.error("❌ Stage 2 failed")
                return False
                
        except Exception as e:
            logger.error(f"Error running Stage 2: {e}")
            return False
    
    def run_stage3(self):
        """Run Stage 3: Data Integration & Processing"""
        try:
            logger.info("🔄 Running Stage 3: Data Integration & Processing")
            logger.info("-" * 50)
            
            integrator = Stage3DataIntegrator()
            success = integrator.run_stage3()
            
            if success:
                logger.info("✅ Stage 3 completed successfully")
                return True
            else:
                logger.error("❌ Stage 3 failed")
                return False
                
        except Exception as e:
            logger.error(f"Error running Stage 3: {e}")
            return False
    
    def run_workflow(self, skip_stage1_check=False):
        """Run the complete three-stage workflow"""
        try:
            logger.info("🚀 Starting Three-Stage Workflow")
            logger.info("=" * 60)
            logger.info("Stage 1: Cursor Agent Function (Manual) - RBC Holdings Collection")
            logger.info("Stage 2: Benefits Data Collection (Automated)")
            logger.info("Stage 3: Data Integration & Processing (Automated)")
            logger.info("=" * 60)
            
            # Check Stage 1 completion (unless skipped)
            if not skip_stage1_check:
                if not self.check_stage1_completion():
                    logger.error("❌ Workflow aborted: Stage 1 not completed")
                    return False
            
            # Run Stage 2
            if not self.run_stage2():
                logger.error("❌ Workflow aborted: Stage 2 failed")
                return False
            
            # Run Stage 3
            if not self.run_stage3():
                logger.error("❌ Workflow aborted: Stage 3 failed")
                return False
            
            logger.info("🎉 Three-Stage Workflow completed successfully!")
            logger.info("📊 Comprehensive holdings file ready for dashboard")
            return True
            
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            return False

def main():
    """Main function to run the three-stage workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run the three-stage workflow')
    parser.add_argument('--skip-stage1-check', action='store_true', 
                       help='Skip Stage 1 completion check')
    parser.add_argument('--stage2-only', action='store_true',
                       help='Run only Stage 2 (Benefits Data Collection)')
    parser.add_argument('--stage3-only', action='store_true',
                       help='Run only Stage 3 (Data Integration & Processing)')
    
    args = parser.parse_args()
    
    orchestrator = ThreeStageWorkflowOrchestrator()
    
    if args.stage2_only:
        print("🏢 Running Stage 2 only...")
        success = orchestrator.run_stage2()
    elif args.stage3_only:
        print("🔄 Running Stage 3 only...")
        success = orchestrator.run_stage3()
    else:
        print("🚀 Running complete three-stage workflow...")
        success = orchestrator.run_workflow(skip_stage1_check=args.skip_stage1_check)
    
    if success:
        print("\n✅ Workflow completed successfully!")
        return True
    else:
        print("\n❌ Workflow failed!")
        return False

if __name__ == "__main__":
    main()
