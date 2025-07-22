#!/usr/bin/env python3
"""
Competitive Intelligence Agent

Single entry point to run the competitive intelligence agent.
Supports both CLI arguments and direct execution with defaults.
"""

import os
import asyncio
import sys
import argparse
from datetime import datetime
from typing import List
from dotenv import load_dotenv

from agents.competitive_intelligence_agent import create_competitive_intelligence_agent

load_dotenv()


async def run_agent(companies: List[str], days_back: int = 7, verbose: bool = False):
    """Run the competitive intelligence agent"""
    
    if verbose:
        print("🤖 COMPETITIVE INTELLIGENCE AGENT")
        print("=" * 60)
        print("Powered by LangGraph - Autonomous AI Agent")
        print("")
    
    # Create the agent
    agent = create_competitive_intelligence_agent()
    
    # Generate unique thread ID
    thread_id = f"cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if verbose:
        print(f"🧠 Agent ID: {thread_id}")
        print(f"📋 Companies: {', '.join(companies)}")
        print(f"📅 Days back: {days_back}")
        print("")
    
    try:
        # Run the agent analysis
        result = await agent.run_analysis(
            companies=companies,
            days_back=days_back,
            thread_id=thread_id
        )
        
        # Display results
        if verbose:
            print("\n🎯 AGENT COMPLETED")
            print("=" * 40)
        
        status = result.get('status', 'unknown')
        progress = result.get('progress', 'No status available')
        
        print(f"Status: {status.upper()}")
        print(f"Result: {progress}")
        
        # Show summary if available
        if result.get("results") and "summary" in result["results"]:
            summary = result["results"]["summary"]
            print(f"\n📊 Summary:")
            print(f"  Companies: {summary.get('total_companies', 0)}")
            print(f"  Articles: {summary.get('total_articles', 0)}")
            print(f"  Signals: {summary.get('total_signals', 0)}")
            
            if summary.get('processing_errors', 0) > 0:
                print(f"  ⚠️  Errors: {summary['processing_errors']}")
        
        # Show high-impact signals
        if (result.get("results") and "high_impact_signals" in result["results"] 
            and result["results"]["high_impact_signals"]):
            
            high_impact = result["results"]["high_impact_signals"][:5]
            print(f"\n🚨 High-Impact Signals:")
            for signal in high_impact:
                print(f"  • {signal['company']}: {signal['title']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


async def main():
    """Main execution function for direct runs (no CLI args)"""
    print("🤖 COMPETITIVE INTELLIGENCE AGENT")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    default_companies = ["Microsoft", "Salesforce", "Databricks", "Stripe", "OpenAI", "Figma"]
    days_back = 30
    
    try:
        result = await run_agent(
            companies=default_companies,
            days_back=days_back,
            verbose=True
        )
        
        if result and result.get("status") in ["complete", "completed"]:
            print("\n✅ Agent execution completed successfully!")
            return 0
        else:
            print(f"\n❌ Agent execution failed")
            return 1
        
    except Exception as e:
        print(f"\n❌ AGENT EXECUTION FAILED: {str(e)}")
        return 1


def cli_main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Run the Competitive Intelligence Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --companies "Salesforce" "OpenAI"
  python main.py --companies "Stripe" "Databricks" --days 14 --verbose
  python main.py --quick
        """
    )
    
    parser.add_argument(
        "--companies", 
        nargs="+", 
        help="List of company names to analyze"
    )
    parser.add_argument(
        "--days", 
        type=int, 
        default=7, 
        help="Number of days to look back (default: 7)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    parser.add_argument(
        "--quick", 
        action="store_true", 
        help="Quick demo with default companies"
    )
    
    args = parser.parse_args()
    
    # Default companies for quick demo
    if args.quick:
        companies = ["Salesforce", "OpenAI", "Databricks"]
        args.verbose = True
    elif args.companies:
        companies = args.companies
    else:
        print("❌ Error: Please provide --companies or use --quick")
        parser.print_help()
        return 1
    
    # Validate environment
    if not os.environ.get("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        return 1
    
    # Run the agent
    try:
        result = asyncio.run(run_agent(companies, args.days, args.verbose))
        if result and result.get("status") in ["complete", "completed"]:
            print("\n✅ Agent execution completed successfully!")
            return 0
        else:
            print(f"\n❌ Agent execution failed")
            return 1
    except Exception as e:
        print(f"\n❌ AGENT EXECUTION FAILED: {str(e)}")
        return 1


def sync_main():
    """Synchronous wrapper for direct execution"""
    return asyncio.run(main())


if __name__ == "__main__":
    # Check if any command line arguments are provided
    if len(sys.argv) > 1:
        # Use CLI interface
        exit_code = cli_main()
    else:
        # Use direct execution with defaults
        exit_code = sync_main()
    
    sys.exit(exit_code)
