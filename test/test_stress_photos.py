import os
import shutil
import unittest
from logic import FileManagementLogic
from generate_test_images import generate_test_images

class TestStressPhotoCopy(unittest.TestCase):
    def setUp(self):
        self.source_dir = 'test_stress_photos'
        self.dest_dir = 'test_stress_photos_dest'
        os.makedirs(self.dest_dir, exist_ok=True)
        # Generate 1000 test images
        generate_test_images(self.source_dir, 5000)

    def tearDown(self):
        shutil.rmtree(self.source_dir, ignore_errors=True)
        shutil.rmtree(self.dest_dir, ignore_errors=True)

    def test_copy_many_photos(self):
        logic = FileManagementLogic(self.source_dir, self.dest_dir, 'DD-MM-YYYY')
        copied_files, errors = logic.copy()
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(copied_files), 1000)

if __name__ == "__main__":
    unittest.main()
