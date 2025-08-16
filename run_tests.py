#!/usr/bin/env python3
"""
Test Runner for FilesByDate Contributions

This script runs all required tests that contributors must pass
before submitting pull requests.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --verbose    # Run with detailed output
    python run_tests.py --basic      # Run only basic functionality tests
"""

import sys
import unittest
import argparse
from io import StringIO

def run_tests(test_level='all', verbose=False):
    """
    Run the test suite for FilesByDate.
    
    Args:
        test_level (str): 'all', 'basic', 'operations', 'undo', 'errors'
        verbose (bool): Whether to show verbose output
    
    Returns:
        bool: True if all tests passed, False otherwise
    """
    
    # Capture output
    stream = StringIO()
    
    # Set verbosity level
    verbosity = 2 if verbose else 1
    
    # Create test loader
    loader = unittest.TestLoader()
    
    # Define test modules/classes based on level
    if test_level == 'all':
        # Load all tests
        suite = loader.discover('test', pattern='test_*.py')
    elif test_level == 'basic':
        # Load only basic functionality tests
        from test.test_logic import TestFileManagementLogic
        suite = unittest.TestSuite()
        suite.addTest(TestFileManagementLogic('test_initialization'))
        suite.addTest(TestFileManagementLogic('test_get_target_folder_files_count'))
        suite.addTest(TestFileManagementLogic('test_get_target_files'))
        suite.addTest(TestFileManagementLogic('test_format_date_all_formats'))
        suite.addTest(TestFileManagementLogic('test_read_file_date_properties'))
    elif test_level == 'operations':
        # Load file operation tests
        from test.test_logic import TestFileManagementLogic
        suite = unittest.TestSuite()
        suite.addTest(TestFileManagementLogic('test_copy_operation_success'))
        suite.addTest(TestFileManagementLogic('test_move_operation_success'))
        suite.addTest(TestFileManagementLogic('test_duplicate_filename_handling'))
        suite.addTest(TestFileManagementLogic('test_folder_creation'))
    elif test_level == 'undo':
        # Load undo functionality tests
        from test.test_logic import TestFileManagementLogic
        suite = unittest.TestSuite()
        suite.addTest(TestFileManagementLogic('test_undo_copy_operation'))
        suite.addTest(TestFileManagementLogic('test_undo_move_operation'))
        suite.addTest(TestFileManagementLogic('test_undo_without_operation'))
        suite.addTest(TestFileManagementLogic('test_undo_clears_operation_history'))
    elif test_level == 'errors':
        # Load error handling tests
        from test.test_logic import TestFileManagementLogic
        suite = unittest.TestSuite()
        suite.addTest(TestFileManagementLogic('test_nonexistent_source_folder'))
        suite.addTest(TestFileManagementLogic('test_empty_source_folder'))
    else:
        print(f"❌ Unknown test level: {test_level}")
        return False
    
    # Run tests
    runner = unittest.TextTestRunner(stream=stream, verbosity=verbosity)
    result = runner.run(suite)
    
    # Get output
    output = stream.getvalue()
    
    # Print results
    print("🧪 FilesByDate Test Results")
    print("=" * 50)
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print(f"📊 Tests run: {result.testsRun}")
        print(f"⏱️  Time: {getattr(result, 'time', 'N/A')}")
        
        if verbose:
            print("\n📝 Detailed Output:")
            print(output)
        
        print("\n🎉 Your contribution is ready for pull request!")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"📊 Tests run: {result.testsRun}")
        print(f"💥 Failures: {len(result.failures)}")
        print(f"🚨 Errors: {len(result.errors)}")
        
        print("\n💡 Failed Tests:")
        for test, error in result.failures + result.errors:
            print(f"  ❌ {test}")
            if verbose:
                print(f"     {error}")
        
        print("\n📝 Full Output:")
        print(output)
        
        print("\n🔧 Please fix the failing tests before submitting your pull request.")
        return False

def print_test_summary():
    """Print a summary of available tests."""
    print("🧪 Available Test Categories:")
    print("=" * 50)
    print("📋 basic      - Basic functionality tests")
    print("📁 operations - File copy/move operation tests")
    print("↩️  undo       - Undo functionality tests")
    print("⚠️  errors     - Error handling tests")
    print("🔍 all        - All tests (default)")
    print()
    print("💡 Examples:")
    print("  python run_tests.py --basic")
    print("  python run_tests.py --verbose")
    print("  python run_tests.py operations --verbose")

def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Test runner for FilesByDate contributions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --verbose          # Verbose output
  python run_tests.py basic              # Only basic tests
  python run_tests.py operations -v      # Operations tests with verbose output
        """
    )
    
    parser.add_argument(
        'level', 
        nargs='?', 
        default='all',
        choices=['all', 'basic', 'operations', 'undo', 'errors'],
        help='Test level to run (default: all)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show verbose test output'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show test summary and exit'
    )
    
    args = parser.parse_args()
    
    if args.summary:
        print_test_summary()
        return
    
    # Welcome message
    print("🚀 FilesByDate Contribution Test Runner")
    print("=" * 50)
    print(f"📂 Running {args.level} tests...")
    print()
    
    # Run tests
    success = run_tests(args.level, args.verbose)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
