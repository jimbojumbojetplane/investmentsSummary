#!/usr/bin/env python3
"""
Analyze the enrichment process by comparing consolidated RBC holdings with enriched file
"""

import json
from pathlib import Path

def main():
    print("=== ANALYZING ENRICHMENT PROCESS ===")
    
    # Load the consolidated RBC holdings file
    output_dir = Path('data/output')
    consolidated_files = list(output_dir.glob('consolidated_holdings_RBC_only_*.json'))
    
    if not consolidated_files:
        print("No consolidated RBC holdings files found!")
        return
    
    latest_consolidated = max(consolidated_files, key=lambda f: f.stat().st_mtime)
    print(f"Consolidated file: {latest_consolidated.name}")
    
    with open(latest_consolidated, 'r') as f:
        consolidated_data = json.load(f)
    
    # Load the most recent enriched file
    enriched_files = list(output_dir.glob('holdings_detailed_*.json'))
    if enriched_files:
        latest_enriched = max(enriched_files, key=lambda f: f.stat().st_mtime)
        print(f"Enriched file: {latest_enriched.name}")
        
        with open(latest_enriched, 'r') as f:
            enriched_data = json.load(f)
    else:
        print("No enriched files found!")
        return
    
    print(f"\n=== FILE COMPARISON ===")
    print(f"Consolidated holdings: {len(consolidated_data.get('holdings', []))}")
    print(f"Enriched holdings: {len(enriched_data)}")
    
    # Get sample holdings from both files
    consolidated_holdings = consolidated_data.get('holdings', [])
    if not consolidated_holdings:
        print("No holdings in consolidated file!")
        return
    
    # Find matching holdings by symbol and account
    consolidated_sample = consolidated_holdings[0]  # First holding
    print(f"\n=== SAMPLE HOLDING ANALYSIS ===")
    print(f"Sample consolidated holding: {consolidated_sample.get('Symbol')} - {consolidated_sample.get('Name', 'Unknown')}")
    
    # Find matching holding in enriched file
    matching_enriched = None
    for h in enriched_data:
        if (h.get('Symbol') == consolidated_sample.get('Symbol') and 
            h.get('Account_Number') == consolidated_sample.get('Account_Number')):
            matching_enriched = h
            break
    
    if not matching_enriched:
        print("No matching holding found in enriched file!")
        return
    
    print(f"Sample enriched holding: {matching_enriched.get('Symbol')} - {matching_enriched.get('Name', 'Unknown')}")
    
    # Compare fields
    print(f"\n=== FIELD COMPARISON ===")
    
    consolidated_fields = set(consolidated_sample.keys())
    enriched_fields = set(matching_enriched.keys())
    
    print(f"Consolidated fields: {len(consolidated_fields)}")
    print(f"Enriched fields: {len(enriched_fields)}")
    
    # Fields added by enrichment
    added_fields = enriched_fields - consolidated_fields
    print(f"\nFields added by enrichment: {len(added_fields)}")
    for field in sorted(added_fields):
        print(f"  + {field}: {matching_enriched.get(field, 'N/A')}")
    
    # Fields that exist in both
    common_fields = consolidated_fields & enriched_fields
    print(f"\nFields in both files: {len(common_fields)}")
    
    # Check for data changes in common fields
    changed_fields = []
    unchanged_fields = []
    
    for field in common_fields:
        consolidated_value = consolidated_sample.get(field)
        enriched_value = matching_enriched.get(field)
        
        if consolidated_value != enriched_value:
            changed_fields.append(field)
        else:
            unchanged_fields.append(field)
    
    print(f"\nFields with changed data: {len(changed_fields)}")
    for field in sorted(changed_fields):
        print(f"  ~ {field}:")
        print(f"    Consolidated: {consolidated_sample.get(field)}")
        print(f"    Enriched: {matching_enriched.get(field)}")
    
    print(f"\nFields with unchanged data: {len(unchanged_fields)}")
    for field in sorted(unchanged_fields):
        print(f"  = {field}: {consolidated_sample.get(field)}")
    
    # Analyze enrichment sources
    print(f"\n=== ENRICHMENT SOURCES ===")
    enrichment_sources = {}
    for h in enriched_data:
        source = h.get('Classification_Source', 'Unknown')
        if source not in enrichment_sources:
            enrichment_sources[source] = 0
        enrichment_sources[source] += 1
    
    for source, count in enrichment_sources.items():
        print(f"  {source}: {count} holdings")
    
    # Check for LLM reasoning
    llm_holdings = [h for h in enriched_data if h.get('LLM_Reasoning')]
    print(f"\nHoldings with LLM reasoning: {len(llm_holdings)}")
    
    if llm_holdings:
        print("Sample LLM reasoning:")
        sample_llm = llm_holdings[0]
        print(f"  Symbol: {sample_llm.get('Symbol')}")
        print(f"  Reasoning: {sample_llm.get('LLM_Reasoning', 'N/A')[:200]}...")
    
    # Summary of enrichment impact
    print(f"\n=== ENRICHMENT SUMMARY ===")
    print(f"Total holdings processed: {len(enriched_data)}")
    print(f"Fields added: {len(added_fields)}")
    print(f"Fields modified: {len(changed_fields)}")
    print(f"Fields unchanged: {len(unchanged_fields)}")
    
    # Show all added fields in detail
    print(f"\n=== DETAILED ADDED FIELDS ===")
    for field in sorted(added_fields):
        sample_value = matching_enriched.get(field, 'N/A')
        print(f"{field}: {sample_value}")

if __name__ == "__main__":
    main()
