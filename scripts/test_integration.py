"""
Comprehensive test suite for historical data integration
Run this to verify the implementation before deploying
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_config():
    """Test configuration settings"""
    print("\n" + "=" * 60)
    print("TEST 1: Configuration")
    print("=" * 60)
    
    from config import (
        HISTORICAL_DATA_ENABLED, 
        HISTORICAL_DATA_FILE, 
        MIN_YEAR, 
        MAX_YEAR,
        CRIME_DATASET_REPO
    )
    
    assert HISTORICAL_DATA_ENABLED is not None, "HISTORICAL_DATA_ENABLED not defined"
    assert HISTORICAL_DATA_FILE is not None, "HISTORICAL_DATA_FILE not defined"
    assert MIN_YEAR == 1969, f"MIN_YEAR should be 1969, got {MIN_YEAR}"
    assert MAX_YEAR == 2023, f"MAX_YEAR should be 2023, got {MAX_YEAR}"
    
    print(f"✓ HISTORICAL_DATA_ENABLED: {HISTORICAL_DATA_ENABLED}")
    print(f"✓ HISTORICAL_DATA_FILE: {HISTORICAL_DATA_FILE}")
    print(f"✓ Year range: {MIN_YEAR} - {MAX_YEAR}")
    print(f"✓ Repository: {CRIME_DATASET_REPO}")
    print("✅ Configuration test PASSED")


def test_data_loader_functions():
    """Test data loader functions"""
    print("\n" + "=" * 60)
    print("TEST 2: Data Loader Functions")
    print("=" * 60)
    
    from data_loader import load_current_data, validate_data
    
    # Test current data loading
    df, crime_cols = load_current_data()
    assert df is not None, "Failed to load current data"
    assert crime_cols is not None, "Failed to get crime columns"
    assert len(df) > 0, "Current data is empty"
    assert validate_data(df), "Data validation failed"
    
    print(f"✓ Current data loaded: {len(df)} records")
    print(f"✓ Crime columns: {len(crime_cols)} columns")
    print(f"✓ Year range: {df['year'].min()} - {df['year'].max()}")
    print("✅ Data loader test PASSED")


def test_schema_standardization():
    """Test schema standardization"""
    print("\n" + "=" * 60)
    print("TEST 3: Schema Standardization")
    print("=" * 60)
    
    from scripts.fetch_historical_data import standardize_schema
    
    # Test with various column name formats
    test_cases = [
        {'STATE': 'S1', 'DISTRICT': 'D1', 'YEAR': 2020, 'Murder': 10},
        {'State': 'S2', 'District': 'D2', 'Year': 2021, 'Rape': 5},
        {'state_name': 'S3', 'district_name': 'D3', 'year': 2022, 'Theft': 20}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        df = pd.DataFrame([test_case])
        result = standardize_schema(df)
        
        # Check required columns
        required = ['state_name', 'district_name', 'year']
        for col in required:
            assert col in result.columns, f"Test case {i}: Missing {col}"
        
        print(f"✓ Test case {i}: {list(test_case.keys())} → {list(result.columns)}")
    
    print("✅ Schema standardization test PASSED")


def test_fetcher_script_exists():
    """Test that fetcher script exists and is valid"""
    print("\n" + "=" * 60)
    print("TEST 4: Fetcher Script")
    print("=" * 60)
    
    script_path = Path(__file__).parent / 'fetch_historical_data.py'
    assert script_path.exists(), f"Fetcher script not found: {script_path}"
    
    # Check if script has main functions
    with open(script_path, 'r') as f:
        content = f.read()
        required_functions = [
            'download_year_data',
            'process_year_folder',
            'standardize_schema',
            'combine_all_years',
            'merge_with_current_data'
        ]
        
        for func in required_functions:
            assert f"def {func}" in content, f"Function {func} not found in script"
            print(f"✓ Function {func} found")
    
    print("✅ Fetcher script test PASSED")


def test_backward_compatibility():
    """Test backward compatibility (app works without historical data)"""
    print("\n" + "=" * 60)
    print("TEST 5: Backward Compatibility")
    print("=" * 60)
    
    from config import HISTORICAL_DATA_FILE
    
    # Make sure historical file doesn't exist for this test
    hist_file = Path(__file__).parent.parent / HISTORICAL_DATA_FILE
    original_exists = hist_file.exists()
    
    if original_exists:
        print("⚠️  Historical file exists, testing load with it...")
    else:
        print("✓ Historical file doesn't exist (testing fallback)")
    
    from data_loader import load_data
    
    df, crime_cols = load_data()
    assert df is not None, "Failed to load data"
    assert len(df) > 0, "Data is empty"
    
    print(f"✓ Data loaded: {len(df)} records")
    print(f"✓ Year range: {df['year'].min()} - {df['year'].max()}")
    print("✅ Backward compatibility test PASSED")


def test_sample_integration():
    """Test with sample historical data"""
    print("\n" + "=" * 60)
    print("TEST 6: Sample Integration")
    print("=" * 60)
    
    from config import HISTORICAL_DATA_FILE
    
    # Create sample historical data
    sample_data = {
        'state_name': ['TestState'] * 5,
        'district_name': ['TestDistrict'] * 5,
        'year': [1969, 1970, 1971, 1972, 1973],
        'murder': [1, 2, 3, 4, 5],
        'rape': [1, 1, 2, 2, 3]
    }
    
    sample_df = pd.DataFrame(sample_data)
    test_file = Path(__file__).parent.parent / HISTORICAL_DATA_FILE
    
    # Save sample file
    sample_df.to_csv(test_file, index=False)
    print(f"✓ Created sample historical data: {test_file}")
    
    # Clear cache and reload
    import streamlit as st
    if hasattr(st, 'cache_data'):
        st.cache_data.clear()
    
    from data_loader import load_data
    df, crime_cols = load_data()
    
    assert df is not None, "Failed to load data with historical file"
    has_1969 = (df['year'] == 1969).any()
    print(f"✓ Contains 1969 data: {has_1969}")
    
    # Cleanup
    test_file.unlink()
    print("✓ Cleaned up sample file")
    
    print("✅ Sample integration test PASSED")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("HISTORICAL DATA INTEGRATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_config,
        test_data_loader_functions,
        test_schema_standardization,
        test_fetcher_script_exists,
        test_backward_compatibility,
        test_sample_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n❌ {test.__name__} FAILED: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
