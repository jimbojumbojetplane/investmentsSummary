#!/usr/bin/env python3
"""
Update holdings data with automated ETF enrichment
"""

import json
import pandas as pd
from pathlib import Path
from automated_etf_enrichment import AutomatedETFEnricher
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_current_holdings():
    """Load the current enriched holdings data"""
    output_dir = Path('data/output')
    
    # Find the most recent consolidated file (prioritize non-enriched files with latest timestamp)
    consolidated_files = list(output_dir.glob('consolidated_holdings_RBC_only_20250913_*.json'))
    enriched_files = list(output_dir.glob('consolidated_holdings_RBC_only_enriched_*.json'))
    
    # Prioritize non-enriched files if they exist
    if consolidated_files:
        latest_file = max(consolidated_files, key=lambda f: f.stat().st_mtime)
    elif enriched_files:
        latest_file = max(enriched_files, key=lambda f: f.stat().st_mtime)
    else:
        logger.error("No RBC holdings files found!")
        return None
    logger.info(f"Loading current data from: {latest_file.name}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return data

def update_holdings_with_automated_enrichment():
    """Update holdings with automated ETF enrichment"""
    
    # Load current data
    current_data = load_current_holdings()
    if not current_data:
        return
    
    holdings_data = current_data.get('holdings', [])
    metadata = current_data.get('metadata', {})
    
    logger.info(f"Found {len(holdings_data)} holdings to process")
    
    # Initialize automated enricher
    enricher = AutomatedETFEnricher()
    
    # Process each holding
    updated_holdings = []
    
    for i, holding in enumerate(holdings_data):
        symbol = holding.get('Symbol', '')
        etf_name = holding.get('Name', '')
        
        logger.info(f"Processing {i+1}/{len(holdings_data)}: {symbol} - {etf_name}")
        
        if not symbol:
            updated_holdings.append(holding)
            continue
        
        # Check if we need to enrich this holding
        needs_enrichment = (
            holding.get('Sector') == 'Unknown' or 
            holding.get('Industry') == 'Unknown' or
            holding.get('Listing_Country') == 'Unknown' or
            not holding.get('Sector') or
            not holding.get('Industry') or
            not holding.get('Listing_Country')
        )
        
        if needs_enrichment:
            logger.info(f"Enriching {symbol} - missing data detected")
            try:
                # Get automated enrichment
                enrichment = enricher.enrich_symbol(symbol, etf_name, force_search=True)
                
                # Merge with existing holding data
                updated_holding = holding.copy()
                
                # Update fields with enriched data
                for key, value in enrichment.items():
                    if key not in ['symbol'] and value:
                        # Map enrichment fields to holding fields
                        field_mapping = {
                            'sector': 'Sector',
                            'industry': 'Industry',
                            'region': 'Issuer_Region',
                            'listing_country': 'Listing_Country',
                            'currency': 'Currency',
                            'exchange': 'Exchange',
                            'market_cap': 'Market_Cap',
                            'business_summary': 'Business_Summary',
                            'website': 'Website'
                            # Note: Removed 'product_name' mapping to avoid duplication with existing 'Name' field
                        }
                        
                        if key in field_mapping:
                            holding_field = field_mapping[key]
                            updated_holding[holding_field] = value
                        else:
                            updated_holding[key] = value
                
                # Update classification source
                updated_holding['Classification_Source'] = 'automated_enrichment'
                updated_holding['Enrichment_Confidence'] = enrichment.get('enrichment_confidence', 0.8)
                updated_holding['Last_Verified_Date'] = enrichment.get('last_verified_date', pd.Timestamp.now().strftime('%Y-%m-%d'))
                
                # Add enrichment sources
                enrichment_sources = enrichment.get('enrichment_sources', [])
                if enrichment_sources:
                    updated_holding['Enrichment_Sources'] = ', '.join(enrichment_sources)
                
                updated_holdings.append(updated_holding)
                logger.info(f"✅ Enriched {symbol}: {updated_holding.get('Sector')} / {updated_holding.get('Industry')}")
                
            except Exception as e:
                logger.error(f"❌ Failed to enrich {symbol}: {e}")
                updated_holdings.append(holding)
        else:
            logger.info(f"Skipping {symbol} - already has complete data")
            updated_holdings.append(holding)
    
    # Create updated metadata
    updated_metadata = metadata.copy()
    updated_metadata['enrichment_fields'] = len(updated_holdings[0]) if updated_holdings else 0
    updated_metadata['created_at'] = pd.Timestamp.now().isoformat()
    updated_metadata['enrichment_method'] = 'automated_multi_source'
    
    # Save updated data (preserve cash balances from original file)
    output_data = {
        'metadata': updated_metadata,
        'holdings': updated_holdings,
        'cash_balances': current_data.get('cash_balances', [])  # Preserve cash balances
    }
    
    # Generate filename with timestamp
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f'consolidated_holdings_RBC_only_automated_enriched_{timestamp}.json'
    output_path = Path('data/output') / output_filename
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    logger.info(f"✅ Updated holdings saved to: {output_filename}")
    
    # Show summary
    enriched_count = sum(1 for h in updated_holdings if h.get('Classification_Source') == 'automated_enrichment')
    logger.info(f"📊 Summary:")
    logger.info(f"   Total holdings: {len(updated_holdings)}")
    logger.info(f"   Newly enriched: {enriched_count}")
    logger.info(f"   Already complete: {len(updated_holdings) - enriched_count}")
    
    return output_path

if __name__ == "__main__":
    update_holdings_with_automated_enrichment()
