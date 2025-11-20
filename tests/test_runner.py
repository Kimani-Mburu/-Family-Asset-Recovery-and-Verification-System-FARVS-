"""
Test Runner for FARVS

Runs all unit tests and provides a summary report.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_all_tests():
    """Run all test suites and return results."""
    # Discover and load all test modules
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test modules
    try:
        from tests.test_database_models import (
            TestDeceasedModel,
            TestAssetsModel,
            TestClaimsModel,
            TestUsersModel
        )
        suite.addTests(loader.loadTestsFromTestCase(TestDeceasedModel))
        suite.addTests(loader.loadTestsFromTestCase(TestAssetsModel))
        suite.addTests(loader.loadTestsFromTestCase(TestClaimsModel))
        suite.addTests(loader.loadTestsFromTestCase(TestUsersModel))
    except ImportError as e:
        print(f"Warning: Could not import database model tests: {e}")
    
    try:
        from tests.test_ui_components import (
            TestModalDialog,
            TestDatePicker,
            TestStatusBadge,
            TestClaimsProgressTracker
        )
        suite.addTests(loader.loadTestsFromTestCase(TestModalDialog))
        suite.addTests(loader.loadTestsFromTestCase(TestDatePicker))
        suite.addTests(loader.loadTestsFromTestCase(TestStatusBadge))
        suite.addTests(loader.loadTestsFromTestCase(TestClaimsProgressTracker))
    except ImportError as e:
        print(f"Warning: Could not import UI component tests: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)


