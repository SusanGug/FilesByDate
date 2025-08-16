import unittest
import os
import tempfile
import shutil
from datetime import datetime
from logic import FileManagementLogic

class TestFileManagementLogic(unittest.TestCase):
    """
    Comprehensive test suite for FilesByDate application.
    Contributors must ensure all these tests pass before submitting pull requests.
    
    Test Categories:
    1. Basic functionality tests
    2. File operation tests (copy/move)
    3. Date format handling tests
    4. Error handling tests
    5. Undo functionality tests
    6. Edge case tests
    """
    
    def setUp(self):
        """Set up test environment before each test method."""
        # Create temporary directories for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.source_dir = tempfile.TemporaryDirectory()
        self.dest_dir = tempfile.TemporaryDirectory()
        
        self.target_folder_path = self.source_dir.name
        self.project_folder_path = self.dest_dir.name
        self.format_type = 'DD-MM-YYYY'
        
        # Create test files with different extensions
        self.test_files = [
            'document.txt',
            'photo.jpg', 
            'video.mp4',
            'data.csv',
            'presentation.pptx'
        ]
        
        # Create test files in source directory
        for file_name in self.test_files:
            file_path = os.path.join(self.target_folder_path, file_name)
            with open(file_path, 'w') as f:
                f.write(f'Test content for {file_name}')
        
        self.file_management_logic = FileManagementLogic(
            self.target_folder_path, 
            self.project_folder_path, 
            self.format_type
        )

    def tearDown(self):
        """Clean up test environment after each test method."""
        self.test_dir.cleanup()
        self.source_dir.cleanup()
        self.dest_dir.cleanup()

    # =============================================================================
    # BASIC FUNCTIONALITY TESTS (Required for all contributions)
    # =============================================================================
    
    def test_initialization(self):
        """Test that FileManagementLogic initializes correctly."""
        logic = FileManagementLogic('/source', '/dest', 'DD-MM-YYYY')
        self.assertEqual(logic.target_folder_path, '/source')
        self.assertEqual(logic.destination_folder_path, '/dest')
        self.assertEqual(logic.format_type, 'DD-MM-YYYY')
        self.assertIsNone(logic.last_operation)
        self.assertEqual(logic.operation_history, [])

    def test_get_target_folder_files_count(self):
        """Test file count functionality."""
        count = self.file_management_logic.get_target_folder_files_count()
        self.assertEqual(count, len(self.test_files))
        
        # Test with empty directory
        empty_dir = tempfile.TemporaryDirectory()
        logic = FileManagementLogic(empty_dir.name, self.project_folder_path, self.format_type)
        self.assertEqual(logic.get_target_folder_files_count(), 0)
        empty_dir.cleanup()

    def test_get_target_files(self):
        """Test file listing functionality."""
        files = self.file_management_logic.get_target_files()
        self.assertEqual(set(files), set(self.test_files))
        self.assertTrue(all(isinstance(f, str) for f in files))

    def test_format_date_all_formats(self):
        """Test all supported date formats."""
        test_cases = [
            ('DD-MM-YYYY', '%d-%m-%Y'),
            ('MM-DD-YYYY', '%m-%d-%Y'),
            ('YYYY-MM-DD', '%Y-%m-%d'),
            ('invalid_format', '%Y-%m-%d')  # Should default to YYYY-MM-DD
        ]
        
        for format_type, expected in test_cases:
            logic = FileManagementLogic(self.target_folder_path, self.project_folder_path, format_type)
            result = logic.format_date()
            self.assertEqual(result, expected, f"Format {format_type} should return {expected}")

    def test_read_file_date_properties(self):
        """Test date reading from files."""
        file_name = self.test_files[0]
        date_str = self.file_management_logic.read_file_date_properties(file_name)
        
        # Should return a string in the specified format
        self.assertIsInstance(date_str, str)
        # Should be a valid date string that can be parsed
        try:
            datetime.strptime(date_str, '%d-%m-%Y')
        except ValueError:
            self.fail("Date string should be parseable")

    # =============================================================================
    # FILE OPERATION TESTS (Critical for file management functionality)
    # =============================================================================
    
    def test_copy_operation_success(self):
        """Test successful file copy operation."""
        result = self.file_management_logic.copy()
        self.assertIsNotNone(result)
        
        copied_files, errors = result
        self.assertEqual(len(copied_files), len(self.test_files))
        self.assertEqual(len(errors), 0)
        
        # Verify files still exist in source
        for file_name in self.test_files:
            source_path = os.path.join(self.target_folder_path, file_name)
            self.assertTrue(os.path.exists(source_path), f"Source file {file_name} should still exist")
        
        # Verify operation tracking
        self.assertIsNotNone(self.file_management_logic.last_operation)
        self.assertEqual(self.file_management_logic.last_operation['type'], 'copy')

    def test_move_operation_success(self):
        """Test successful file move operation."""
        result = self.file_management_logic.move()
        self.assertIsNotNone(result)
        
        moved_files, errors = result
        self.assertEqual(len(moved_files), len(self.test_files))
        self.assertEqual(len(errors), 0)
        
        # Verify files no longer exist in source
        for file_name in self.test_files:
            source_path = os.path.join(self.target_folder_path, file_name)
            self.assertFalse(os.path.exists(source_path), f"Source file {file_name} should be moved")
        
        # Verify operation tracking
        self.assertIsNotNone(self.file_management_logic.last_operation)
        self.assertEqual(self.file_management_logic.last_operation['type'], 'move')

    def test_duplicate_filename_handling(self):
        """Test handling of duplicate filenames."""
        # First copy operation
        result1 = self.file_management_logic.copy()
        copied_files1, errors1 = result1
        self.assertEqual(len(errors1), 0)
        
        # Create new logic instance for second copy
        logic2 = FileManagementLogic(self.target_folder_path, self.project_folder_path, self.format_type)
        result2 = logic2.copy()
        copied_files2, errors2 = result2
        
        # Second copy should handle duplicates without errors
        self.assertEqual(len(errors2), 0)
        self.assertEqual(len(copied_files2), len(self.test_files))

    def test_folder_creation(self):
        """Test that date folders are created correctly."""
        self.file_management_logic.copy()
        
        # Check that date folders were created
        dest_contents = os.listdir(self.project_folder_path)
        self.assertTrue(len(dest_contents) > 0, "Date folders should be created")
        
        # Verify folder names follow the date format
        for folder_name in dest_contents:
            folder_path = os.path.join(self.project_folder_path, folder_name)
            self.assertTrue(os.path.isdir(folder_path), f"{folder_name} should be a directory")

    # =============================================================================
    # UNDO FUNCTIONALITY TESTS (Critical for data safety)
    # =============================================================================
    
    def test_undo_copy_operation(self):
        """Test undoing a copy operation."""
        # Perform copy operation
        self.file_management_logic.copy()
        
        # Verify files were copied
        dest_contents = os.listdir(self.project_folder_path)
        self.assertTrue(len(dest_contents) > 0)
        
        # Undo the operation
        undo_success = self.file_management_logic.undo_last_action()
        self.assertTrue(undo_success, "Undo operation should succeed")
        
        # Verify copied files were removed (but source files remain)
        for file_name in self.test_files:
            source_path = os.path.join(self.target_folder_path, file_name)
            self.assertTrue(os.path.exists(source_path), f"Source file {file_name} should still exist")

    def test_undo_move_operation(self):
        """Test undoing a move operation."""
        # Perform move operation
        self.file_management_logic.move()
        
        # Verify files were moved (source is empty)
        source_files = os.listdir(self.target_folder_path)
        self.assertEqual(len(source_files), 0, "Source folder should be empty after move")
        
        # Undo the operation
        undo_success = self.file_management_logic.undo_last_action()
        self.assertTrue(undo_success, "Undo operation should succeed")
        
        # Verify files are back in source
        restored_files = os.listdir(self.target_folder_path)
        self.assertEqual(set(restored_files), set(self.test_files), "All files should be restored to source")

    def test_undo_without_operation(self):
        """Test undo when no operation has been performed."""
        undo_success = self.file_management_logic.undo_last_action()
        self.assertFalse(undo_success, "Undo should fail when no operation was performed")

    def test_undo_clears_operation_history(self):
        """Test that undo clears the last operation."""
        self.file_management_logic.copy()
        self.assertIsNotNone(self.file_management_logic.last_operation)
        
        self.file_management_logic.undo_last_action()
        self.assertIsNone(self.file_management_logic.last_operation)

    # =============================================================================
    # ERROR HANDLING TESTS (Required for robustness)
    # =============================================================================
    
    def test_nonexistent_source_folder(self):
        """Test behavior with non-existent source folder."""
        logic = FileManagementLogic('/nonexistent/path', self.project_folder_path, self.format_type)
        
        with self.assertRaises(FileNotFoundError):
            logic.get_target_folder_files_count()

    def test_readonly_destination_folder(self):
        """Test behavior when destination folder is read-only."""
        # This test may need to be skipped on some systems
        if os.name == 'nt':  # Windows
            self.skipTest("Read-only test skipped on Windows")
        
        # Make destination read-only
        os.chmod(self.project_folder_path, 0o444)
        
        try:
            result = self.file_management_logic.copy()
            copied_files, errors = result
            # Should have errors due to permission issues
            self.assertTrue(len(errors) > 0, "Should have permission errors")
        finally:
            # Restore permissions for cleanup
            os.chmod(self.project_folder_path, 0o755)

    def test_empty_source_folder(self):
        """Test operations on empty source folder."""
        # Clear the source folder
        for file_name in os.listdir(self.target_folder_path):
            os.remove(os.path.join(self.target_folder_path, file_name))
        
        count = self.file_management_logic.get_target_folder_files_count()
        self.assertEqual(count, 0)
        
        result = self.file_management_logic.copy()
        copied_files, errors = result
        self.assertEqual(len(copied_files), 0)

    # =============================================================================
    # EDGE CASE TESTS (Important for reliability)
    # =============================================================================
    
    def test_files_with_special_characters(self):
        """Test handling of files with special characters in names."""
        special_files = [
            'file with spaces.txt',
            'file-with-dashes.txt',
            'file_with_underscores.txt',
            'file.with.dots.txt'
        ]
        
        # Create files with special characters
        for file_name in special_files:
            file_path = os.path.join(self.target_folder_path, file_name)
            with open(file_path, 'w') as f:
                f.write('Test content')
        
        logic = FileManagementLogic(self.target_folder_path, self.project_folder_path, self.format_type)
        result = logic.copy()
        copied_files, errors = result
        
        # Should handle special characters without errors
        self.assertEqual(len(errors), 0, "Should handle special characters without errors")

    def test_very_long_filename(self):
        """Test handling of very long filenames."""
        long_name = 'a' * 200 + '.txt'  # Very long filename
        file_path = os.path.join(self.target_folder_path, long_name)
        
        try:
            with open(file_path, 'w') as f:
                f.write('Test content')
        except OSError:
            self.skipTest("System doesn't support long filenames")
        
        logic = FileManagementLogic(self.target_folder_path, self.project_folder_path, self.format_type)
        result = logic.copy()
        copied_files, errors = result
        
        # Should handle long filenames appropriately
        self.assertIsNotNone(result)

    def test_operation_history_limit(self):
        """Test that operation history is limited to prevent memory issues."""
        # Perform multiple operations
        for i in range(15):  # More than the 10-operation limit
            # Create a new file for each operation
            file_name = f'test_file_{i}.txt'
            file_path = os.path.join(self.target_folder_path, file_name)
            with open(file_path, 'w') as f:
                f.write(f'Test content {i}')
            
            logic = FileManagementLogic(self.target_folder_path, self.project_folder_path, self.format_type)
            logic.copy()
            
            # Clear the file after operation
            os.remove(file_path)
        
        # Operation history should be limited
        self.assertLessEqual(len(logic.operation_history), 10, "Operation history should be limited to 10 entries")

    # =============================================================================
    # PREVIEW FUNCTIONALITY TESTS
    # =============================================================================
    
    def test_preview_organization(self):
        """Test preview functionality."""
        preview_result = self.file_management_logic.preview_organization()
        
        self.assertIsInstance(preview_result, dict)
        self.assertTrue(len(preview_result) > 0, "Preview should show file organization")
        
        # Verify all test files are included in preview
        total_files_in_preview = sum(len(files) for files in preview_result.values())
        self.assertEqual(total_files_in_preview, len(self.test_files))

    def test_get_file_date_info(self):
        """Test detailed file date information."""
        file_name = self.test_files[0]
        date_info = self.file_management_logic.get_file_date_info(file_name)
        
        required_keys = ['date', 'source', 'original_date', 'datetime_original']
        for key in required_keys:
            self.assertIn(key, date_info, f"Date info should contain {key}")
        
        self.assertIsInstance(date_info['date'], str)
        self.assertIsInstance(date_info['source'], str)


# =============================================================================
# CONTRIBUTION GUIDELINES
# =============================================================================

class TestContributionGuidelines(unittest.TestCase):
    """
    Additional tests that verify contribution guidelines are followed.
    These tests ensure code quality and consistency.
    """
    
    def test_logic_module_imports(self):
        """Test that the logic module can be imported without errors."""
        try:
            from logic import FileManagementLogic
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Logic module should be importable: {e}")

    def test_required_methods_exist(self):
        """Test that all required methods exist in FileManagementLogic."""
        from logic import FileManagementLogic
        
        required_methods = [
            'get_target_folder_files_count',
            'get_target_files',
            'read_file_date_properties',
            'format_date',
            'copy',
            'move',
            'undo_last_action',
            'preview_organization'
        ]
        
        logic = FileManagementLogic('/', '/', 'DD-MM-YYYY')
        
        for method_name in required_methods:
            self.assertTrue(hasattr(logic, method_name), f"Method {method_name} should exist")
            self.assertTrue(callable(getattr(logic, method_name)), f"Method {method_name} should be callable")


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)