import os
import shutil
from datetime import datetime


# Get the folder and count the number of files in it
class FileManagementLogic:

    def __init__(self, target_folder_path, project_folder_path, format_type):
        self.target_folder_path = target_folder_path
        self.destination_folder_path = project_folder_path
        self.format_type = format_type
        self.last_operation = None  # Track the last operation for undo
        self.operation_history = []  # Store operation history

    def undo_last_action(self):
        """
        Undo the last file operation (move or copy).
        Returns True if successful, False if no operation to undo.
        """
        if not self.last_operation:
            print("No operation to undo.")
            return False

        try:
            operation_type = self.last_operation['type']
            files_info = self.last_operation['files']

            print(f"Undoing last {operation_type} operation...")

            if operation_type == 'move':
                # For move operations, move files back to source
                return self._undo_move_operation(files_info)
            elif operation_type == 'copy':
                # For copy operations, remove copied files from destination
                return self._undo_copy_operation(files_info)
            else:
                print(f"Unknown operation type: {operation_type}")
                return False

        except Exception as e:
            print(f"Error during undo operation: {str(e)}")
            return False

    def _undo_move_operation(self, files_info):
        """Undo a move operation by moving files back to source."""
        try:
            moved_back = 0
            folders_to_check = set()  # Track folders to check for emptiness

            for file_info in files_info:
                source_path = file_info['from']
                current_path = file_info['to']

                # Check if file still exists at destination
                if os.path.exists(current_path):
                    # Move file back to source
                    shutil.move(current_path, source_path)
                    moved_back += 1
                    print(f"Moved back: {os.path.basename(file_info['file'])}")

                    # Add the folder path to check later
                    folder_path = os.path.dirname(current_path)
                    folders_to_check.add(folder_path)
                else:
                    print(
                        f"Warning: File not found at destination: {current_path}")

            # Check and remove empty folders
            self._remove_empty_folders(folders_to_check)

            print(
                f"Successfully moved back {moved_back} files to source folder.")

            # Clear the last operation after successful undo
            self.last_operation = None
            return True

        except Exception as e:
            print(f"Error undoing move operation: {str(e)}")
            return False

    def _undo_copy_operation(self, files_info):
        """Undo a copy operation by removing copied files from destination."""
        try:
            removed = 0
            folders_to_check = set()  # Track folders to check for emptiness

            for file_info in files_info:
                current_path = file_info['to']

                # Check if copied file exists at destination
                if os.path.exists(current_path):
                    # Remove the copied file
                    os.remove(current_path)
                    removed += 1
                    print(
                        f"Removed copied file: {
                            os.path.basename(
                                file_info['file'])}")

                    # Add the folder path to check later
                    folder_path = os.path.dirname(current_path)
                    folders_to_check.add(folder_path)
                else:
                    print(
                        f"Warning: Copied file not found at destination: {current_path}")

            # Check and remove empty folders
            self._remove_empty_folders(folders_to_check)

            print(
                f"Successfully removed {removed} copied files from destination.")

            # Clear the last operation after successful undo
            self.last_operation = None
            return True

        except Exception as e:
            print(f"Error undoing copy operation: {str(e)}")
            return False

    def _remove_empty_folders(self, folders_to_check):
        """
        Check and remove empty folders from the destination directory.
        Only removes folders that are completely empty.
        """
        try:
            removed_folders = 0

            for folder_path in folders_to_check:
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    # Check if folder is empty (no files, no subdirectories)
                    try:
                        contents = os.listdir(folder_path)
                        if not contents:  # Folder is empty
                            os.rmdir(folder_path)
                            removed_folders += 1
                            print(
                                f"Removed empty folder: {
                                    os.path.basename(folder_path)}")
                        else:
                            print(
                                f"Folder not empty, keeping: {
                                    os.path.basename(folder_path)} ({
                                    len(contents)} items)")
                    except OSError as e:
                        print(
                            f"Warning: Could not check folder {folder_path}: {
                                str(e)}")
                        continue

            if removed_folders > 0:
                print(f"Cleaned up {removed_folders} empty folders.")
            else:
                print("No empty folders to remove.")

        except Exception as e:
            print(f"Warning: Error during folder cleanup: {str(e)}")

    def _track_operation(self, operation_type, files_info):
        """Track an operation for potential undo."""
        self.last_operation = {
            'type': operation_type,
            'files': files_info,
            'timestamp': datetime.now()
        }
        self.operation_history.append(self.last_operation.copy())

        # Keep only last 10 operations in history
        if len(self.operation_history) > 10:
            self.operation_history.pop(0)

    # Get the number of files in the target folder
    def get_target_folder_files_count(self):
        return len([name for name in os.listdir(self.target_folder_path)
                   if os.path.isfile(os.path.join(self.target_folder_path, name))])

    def get_target_files(self):
        return os.listdir(self.target_folder_path)

    def get_file_date_info(self, file_name):
        """
        Get detailed date information for a file, showing the source of the date.
        Returns a dictionary with date and source information.
        """
        file_path = os.path.join(self.target_folder_path, file_name)
        file_stats = os.stat(file_path)

        # Try to get EXIF date for image files first
        photo_date = self._get_exif_date(file_path)
        if photo_date:
            return {
                'date': photo_date.strftime(self.format_date()),
                'source': 'EXIF data',
                'original_date': photo_date,
                'datetime_original': photo_date.strftime('%Y-%m-%d %H:%M:%S')
            }

        # Fall back to modification time
        mtime = datetime.fromtimestamp(file_stats.st_mtime)
        return {
            'date': mtime.strftime(self.format_date()),
            'source': 'File modification time',
            'original_date': mtime,
            'datetime_original': mtime.strftime('%Y-%m-%d %H:%M:%S')
        }

    def read_file_date_properties(self, file_name):
        """
        Read the actual date from a file, prioritizing EXIF data for images.
        Falls back to modification time, then creation time.
        """
        file_path = os.path.join(self.target_folder_path, file_name)
        file_stats = os.stat(file_path)

        # Try to get EXIF date for image files first
        photo_date = self._get_exif_date(file_path)
        if photo_date:
            return photo_date.strftime(self.format_date())

        # Fall back to modification time (usually more accurate than creation
        # time)
        mtime = datetime.fromtimestamp(file_stats.st_mtime)
        return mtime.strftime(self.format_date())

    def _get_exif_date(self, file_path):
        """
        Extract date from EXIF data for image files.
        Returns datetime object if successful, None otherwise.
        """
        try:
            # Check if it's an image file
            image_extensions = {
                '.jpg',
                '.jpeg',
                '.png',
                '.gif',
                '.bmp',
                '.tiff',
                '.tif'}
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext not in image_extensions:
                return None

            # Try to import PIL for EXIF reading
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
            except ImportError:
                # PIL not available, skip EXIF reading
                return None

            # Open image and extract EXIF data
            with Image.open(file_path) as img:
                exif_data = img._getexif()
                if exif_data is None:
                    return None

                # Look for date fields in EXIF
                date_fields = [
                    36867,  # DateTimeOriginal
                    36868,  # DateTime
                    306,    # DateTime
                    50971,  # DateTimeDigitized
                ]

                for field_id in date_fields:
                    if field_id in exif_data:
                        date_str = exif_data[field_id]
                        if date_str:
                            # Parse EXIF date format (usually YYYY:MM:DD
                            # HH:MM:SS)
                            try:
                                # Handle different EXIF date formats
                                if ':' in date_str:
                                    # Format: YYYY:MM:DD HH:MM:SS
                                    # Replace first two colons
                                    date_str = date_str.replace(':', '-', 2)
                                    # Replace third colon with space
                                    date_str = date_str.replace(':', ' ', 1)
                                    return datetime.strptime(
                                        date_str, '%Y-%m-%d %H:%M:%S')
                                else:
                                    # Try other common formats
                                    for fmt in [
                                            '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d']:
                                        try:
                                            return datetime.strptime(
                                                date_str, fmt)
                                        except ValueError:
                                            continue
                            except ValueError:
                                continue

                return None

        except Exception as e:
            # If any error occurs during EXIF reading, fall back to file stats
            print(
                f"Warning: Could not read EXIF data from {
                    os.path.basename(file_path)}: {
                    str(e)}")
            return None

    def create_folder_with_date(self):
        for file_name in self.get_target_files():
            file_date = self.read_file_date_properties(file_name)
            folder_path = os.path.join(self.destination_folder_path, file_date)
            # TODO: Check if the folder already exists, if exists, do not
            # create the folder or overwrite the folder
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

    def format_date(self):
        if self.format_type == "DD-MM-YYYY":
            return '%d-%m-%Y'
        elif self.format_type == "MM-DD-YYYY":
            return '%m-%d-%Y'
        elif self.format_type == "YYYY-MM-DD":
            return '%Y-%m-%d'
        else:
            return '%Y-%m-%d'

    def move_files_to_destination_folder(self):
        """
        Move each file to a folder named after its creation date.
        Creates separate folders for each unique date and moves files accordingly.
        """
        moved_files = []
        errors = []

        for file_name in self.get_target_files():
            try:
                # Get the file's date information
                file_date_info = self.get_file_date_info(file_name)
                file_date = file_date_info['date']

                # Create the destination folder path for this specific date
                folder_path = os.path.join(
                    self.destination_folder_path, file_date)

                # Create the folder if it doesn't exist
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    print(f"Created folder: {folder_path}")

                # Define source and destination paths
                source_path = os.path.join(self.target_folder_path, file_name)
                destination_path = os.path.join(folder_path, file_name)

                # Check if source file exists
                if not os.path.exists(source_path):
                    error_msg = f"Source file not found: {source_path}"
                    print(error_msg)
                    errors.append(error_msg)
                    continue

                # Check if destination file already exists
                if os.path.exists(destination_path):
                    # Handle duplicate filename by adding a counter
                    base_name, extension = os.path.splitext(file_name)
                    counter = 1
                    while os.path.exists(destination_path):
                        new_name = f"{base_name}_{counter}{extension}"
                        destination_path = os.path.join(folder_path, new_name)
                        counter += 1

                # Move the file to its date-specific folder
                shutil.move(str(source_path), str(destination_path))
                moved_files.append({
                    'file': file_name,
                    'from': source_path,
                    'to': destination_path,
                    'date_folder': file_date,
                    'date_source': file_date_info['source']
                })
                print(
                    f"Moved '{file_name}' to '{file_date}' folder (Date source: {
                        file_date_info['source']})")

            except Exception as e:
                error_msg = f"Error processing file '{file_name}': {str(e)}"
                print(error_msg)
                errors.append(error_msg)
                continue

        # Print summary
        print(f"\nFile move operation completed:")
        print(f"Successfully moved {len(moved_files)} files")
        if errors:
            print(f"Encountered {len(errors)} errors")
            for error in errors:
                print(f"  - {error}")

        # Track operation for undo functionality
        if moved_files:
            self._track_operation('move', moved_files)

        return moved_files, errors

    def copy_files_to_destination_folder(self):
        """
        Copy each file to a folder named after its creation date.
        Creates separate folders for each unique date and copies files accordingly.
        """
        copied_files = []
        errors = []

        for file_name in self.get_target_files():
            try:
                # Get the file's date information
                file_date_info = self.get_file_date_info(file_name)
                file_date = file_date_info['date']

                # Create the destination folder path for this specific date
                folder_path = os.path.join(
                    self.destination_folder_path, file_date)

                # Create the folder if it doesn't exist
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    print(f"Created folder: {folder_path}")

                # Define source and destination paths
                source_path = os.path.join(self.target_folder_path, file_name)
                destination_path = os.path.join(folder_path, file_name)

                # Check if source file exists
                if not os.path.exists(source_path):
                    error_msg = f"Source file not found: {source_path}"
                    print(error_msg)
                    errors.append(error_msg)
                    continue

                # Check if destination file already exists
                if os.path.exists(destination_path):
                    # Handle duplicate filename by adding a counter
                    base_name, extension = os.path.splitext(file_name)
                    counter = 1
                    while os.path.exists(destination_path):
                        new_name = f"{base_name}_{counter}{extension}"
                        destination_path = os.path.join(folder_path, new_name)
                        counter += 1

                # Copy the file to its date-specific folder
                shutil.copy(str(source_path), str(destination_path))
                copied_files.append({
                    'file': file_name,
                    'from': source_path,
                    'to': destination_path,
                    'date_folder': file_date,
                    'date_source': file_date_info['source']
                })
                print(
                    f"Copied '{file_name}' to '{file_date}' folder (Date source: {
                        file_date_info['source']})")

            except Exception as e:
                error_msg = f"Error processing file '{file_name}': {str(e)}"
                print(error_msg)
                errors.append(error_msg)
                continue

        # Print summary
        print(f"\nFile copy operation completed:")
        print(f"Successfully copied {len(copied_files)} files")
        if errors:
            print(f"Encountered {len(errors)} errors")
            for error in errors:
                print(f"  - {error}")

        # Track operation for undo functionality
        if copied_files:
            self._track_operation('copy', copied_files)

        return copied_files, errors

    def preview_organization(self):
        """
        Preview how files will be organized without actually moving them.
        Returns a dictionary showing which files will go to which date folders.
        """
        print(f"Preview of file organization:")
        print(f"Source folder: {self.target_folder_path}")
        print(f"Destination folder: {self.destination_folder_path}")
        print(f"Date format: {self.format_type}")

        # Get all files and their dates
        files_with_dates = []
        for file_name in self.get_target_files():
            try:
                file_date_info = self.get_file_date_info(file_name)
                files_with_dates.append({
                    'name': file_name,
                    'date': file_date_info['date'],
                    'source': file_date_info['source'],
                    'source_path': os.path.join(self.target_folder_path, file_name)
                })
            except Exception as e:
                print(f"Error reading date for '{file_name}': {str(e)}")
                continue

        # Group files by date
        date_groups = {}
        for file_info in files_with_dates:
            date = file_info['date']
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(file_info)

        print(f"\nFiles will be organized as follows:")
        print(f"Total files: {len(files_with_dates)}")
        print(f"Date folders to be created: {len(date_groups)}")

        for date in sorted(date_groups.keys()):
            files = date_groups[date]
            print(f"\n  📁 {date}/ ({len(files)} files):")
            for file_info in files:
                print(
                    f"    �� {
                        file_info['name']} (Source: {
                        file_info['source']})")

        return date_groups

    def organize_files_by_date(self):
        """
        Advanced organization method that groups files by date and provides detailed feedback.
        This method ensures each file goes to its own date-specific folder.
        """
        print(f"Starting file organization...")
        print(f"Source folder: {self.target_folder_path}")
        print(f"Destination folder: {self.destination_folder_path}")
        print(f"Date format: {self.format_type}")

        # Get all files and their dates
        files_with_dates = []
        for file_name in self.get_target_files():
            try:
                file_date_info = self.get_file_date_info(file_name)
                files_with_dates.append({
                    'name': file_name,
                    'date': file_date_info['date'],
                    'source': file_date_info['source'],
                    'source_path': os.path.join(self.target_folder_path, file_name)
                })
            except Exception as e:
                print(f"Error reading date for '{file_name}': {str(e)}")
                continue

        # Group files by date
        date_groups = {}
        for file_info in files_with_dates:
            date = file_info['date']
            if date not in date_groups:
                date_groups[date] = []
            date_groups[date].append(file_info)

        print(
            f"\nFound {
                len(files_with_dates)} files to organize into {
                len(date_groups)} date folders:")
        for date, files in date_groups.items():
            print(f"  {date}: {len(files)} files")

        # Create folders and move files
        return self.move_files_to_destination_folder()

    # First get all the file, then read all the file date properties
    # and create folder with the date and move the file to the folder matching
    # the date
    def move(self):
        """
        Main method to organize and move files by their creation dates.
        Creates separate folders for each unique date and moves files accordingly.
        """
        return self.organize_files_by_date()

    def copy(self):
        """
        Main method to organize and copy files by their creation dates.
        Creates separate folders for each unique date and copies files accordingly.
        """
        self.create_folder_with_date()
        return self.copy_files_to_destination_folder()
