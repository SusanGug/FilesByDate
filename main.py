import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from logic import FileManagementLogic
import os

class FileChooserApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("📁 File Management Application")
        self.geometry("800x600")
        self.configure(bg='#f0f0f0')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.folder_organize_path = tk.StringVar()
        self.project_folder_path = tk.StringVar()
        self.dropdown_var = tk.StringVar(value="DD-MM-YYYY")
        self.file_management_logic = None
        
        # Status variables
        self.status_var = tk.StringVar(value="Ready to organize files")
        self.progress_var = tk.DoubleVar()
        
        self.create_widgets()
        self.center_window()

    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Create main container with scrollbar
        main_container = tk.Frame(self, bg='#f0f0f0')
        main_container.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(main_container, bg='#f0f0f0', highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')
        
        # Configure scrollable frame
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create canvas window - center the content
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Update canvas window position when canvas size changes
        def _configure_canvas(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.canvas.bind('<Configure>', _configure_canvas)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.bind_mousewheel()
        
        # Main frame is now the scrollable frame
        main_frame = self.scrollable_frame
        
        # Title
        title_label = tk.Label(main_frame, text="📁 File Management Application", 
                              font=('Arial', 18, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = tk.Label(main_frame, 
                             text="Organize your files by creation date into date-based folders",
                             font=('Arial', 10), bg='#f0f0f0', fg='#7f8c8d')
        desc_label.pack(pady=(0, 20))
        
        # Process explanation
        process_frame = tk.Frame(main_frame, bg='#e8f4fd', relief=tk.SOLID, bd=1)
        process_frame.pack(fill=tk.X, pady=(0, 20))
        
        process_title = tk.Label(process_frame, text="💡 How It Works:", 
                                font=('Arial', 11, 'bold'), bg='#e8f4fd', fg='#2c3e50')
        process_title.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        process_steps = tk.Label(process_frame, 
                                text="1. Select a source folder with files to organize\n"
                                     "2. Choose a destination folder for organized date-folders\n"
                                     "3. Pick your preferred date format\n"
                                     "4. Click Copy (keeps originals) or Move (removes originals)\n"
                                     "5. Use Undo if you need to reverse the operation",
                                font=('Arial', 9), bg='#e8f4fd', fg='#34495e', justify=tk.LEFT)
        process_steps.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # Settings Frame
        settings_frame = tk.LabelFrame(main_frame, text="⚙️ Settings", 
                                      font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        settings_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Source Folder
        source_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        source_frame.pack(fill=tk.X, padx=15, pady=10)
        
        source_label = tk.Label(source_frame, text="📂 Source Folder:", 
                               font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        source_label.pack(anchor=tk.W)
        
        # Source folder explanation
        source_explanation = tk.Label(source_frame, 
                                     text="This is the folder containing files you want to organize by date (e.g., your Photos folder)",
                                     font=('Arial', 9), bg='#f0f0f0', fg='#7f8c8d', wraplength=500)
        source_explanation.pack(anchor=tk.W, pady=(0, 5))
        
        source_input_frame = tk.Frame(source_frame, bg='#f0f0f0')
        source_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.source_entry = tk.Entry(source_input_frame, textvariable=self.folder_organize_path, 
                                   font=('Arial', 10), bg='white', relief=tk.SOLID, bd=1)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.source_button = tk.Button(source_input_frame, text="Browse", 
                                     command=self.choose_folder1, bg='#3498db', fg='white',
                                     font=('Arial', 9, 'bold'), relief=tk.FLAT, padx=15)
        self.source_button.pack(side=tk.RIGHT)
        
        # Destination Folder
        dest_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        dest_frame.pack(fill=tk.X, padx=15, pady=10)
        
        dest_label = tk.Label(dest_frame, text="📁 Destination Folder:", 
                             font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        dest_label.pack(anchor=tk.W)
        
        # Destination folder explanation
        dest_explanation = tk.Label(dest_frame, 
                                   text="This is where organized date-folders will be created (e.g., your Organized Photos folder)",
                                   font=('Arial', 9), bg='#f0f0f0', fg='#7f8c8d', wraplength=500)
        dest_explanation.pack(anchor=tk.W, pady=(0, 5))
        
        dest_input_frame = tk.Frame(dest_frame, bg='#f0f0f0')
        dest_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.dest_entry = tk.Entry(dest_input_frame, textvariable=self.project_folder_path, 
                                 font=('Arial', 10), bg='white', relief=tk.SOLID, bd=1)
        self.dest_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.dest_button = tk.Button(dest_input_frame, text="Browse", 
                                   command=self.choose_folder2, bg='#3498db', fg='white',
                                   font=('Arial', 9, 'bold'), relief=tk.FLAT, padx=15)
        self.dest_button.pack(side=tk.RIGHT)
        
        # Date Format
        format_frame = tk.Frame(settings_frame, bg='#f0f0f0')
        format_frame.pack(fill=tk.X, padx=15, pady=10)
        
        format_label = tk.Label(format_frame, text="📅 Date Format:", 
                               font=('Arial', 10, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        format_label.pack(anchor=tk.W)
        
        # Date format explanation
        format_explanation = tk.Label(format_frame, 
                                     text="Choose how date folders will be named (e.g., 15-01-2024, 01-15-2024, or 2024-01-15)",
                                     font=('Arial', 9), bg='#f0f0f0', fg='#7f8c8d', wraplength=500)
        format_explanation.pack(anchor=tk.W, pady=(0, 5))
        
        format_input_frame = tk.Frame(format_frame, bg='#f0f0f0')
        format_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.format_dropdown = ttk.Combobox(format_input_frame, textvariable=self.dropdown_var,
                                           values=["DD-MM-YYYY", "MM-DD-YYYY", "YYYY-MM-DD"],
                                           font=('Arial', 10), state="readonly", width=20)
        self.format_dropdown.pack(anchor=tk.W)
        
        # File Info Frame
        self.info_frame = tk.LabelFrame(main_frame, text="📊 File Information", 
                                       font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        self.info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File info explanation
        info_explanation = tk.Label(self.info_frame, 
                                   text="This shows how many files are in your source folder and will be organized",
                                   font=('Arial', 9), bg='#f0f0f0', fg='#7f8c8d', wraplength=500)
        info_explanation.pack(anchor=tk.W, padx=15, pady=(5, 0))
        
        self.file_count_label = tk.Label(self.info_frame, text="No source folder selected", 
                                        font=('Arial', 10), bg='#f0f0f0', fg='#7f8c8d')
        self.file_count_label.pack(pady=10)
        
        # Actions Frame
        actions_frame = tk.LabelFrame(main_frame, text="🚀 Actions", 
                                     font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        actions_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Actions explanation
        actions_explanation = tk.Label(actions_frame, 
                                      text="Choose how you want to organize your files:",
                                      font=('Arial', 9), bg='#f0f0f0', fg='#7f8c8d', wraplength=500)
        actions_explanation.pack(anchor=tk.W, padx=15, pady=(5, 0))
        
        # Buttons
        buttons_frame = tk.Frame(actions_frame, bg='#f0f0f0')
        buttons_frame.pack(pady=20)
        
        self.copy_button = tk.Button(buttons_frame, text="📋 Copy Files", 
                                   command=self.copy_action, bg='#27ae60', fg='white',
                                   font=('Arial', 11, 'bold'), relief=tk.FLAT, padx=25, pady=10)
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        
        self.move_button = tk.Button(buttons_frame, text="📤 Move Files", 
                                   command=self.move_action, bg='#e74c3c', fg='white',
                                   font=('Arial', 11, 'bold'), relief=tk.FLAT, padx=25, pady=10)
        self.move_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.undo_button = tk.Button(buttons_frame, text="↩️ Undo Last", 
                                   command=self.undo_action, bg='#f39c12', fg='white',
                                   font=('Arial', 11, 'bold'), relief=tk.FLAT, padx=25, pady=10)
        self.undo_button.pack(side=tk.LEFT)
        
        # Recent Operations Frame
        self.operations_frame = tk.LabelFrame(main_frame, text="Recent Operations", 
                                             font=('Arial', 12, 'bold'), bg='#f0f0f0', fg='#2c3e50')
        self.operations_frame.pack(fill=tk.BOTH, expand=True)
        
        # Operations explanation
        operations_explanation = tk.Label(self.operations_frame, 
                                         text="This log shows all recent operations and their results",
                                         font=('Arial', 9), bg='#f0f0f0', fg='#7f8c8d', wraplength=500)
        operations_explanation.pack(anchor=tk.W, padx=15, pady=(5, 0))
        
        # Operations text widget - create a frame for text and scrollbar
        operations_text_frame = tk.Frame(self.operations_frame, bg='#f0f0f0')
        operations_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.operations_text = tk.Text(operations_text_frame, height=15, font=('Consolas', 9),
                                      bg='#2c3e50', fg='#ecf0f1', relief=tk.FLAT, bd=0, wrap=tk.WORD)
        self.operations_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for operations text
        operations_scrollbar = tk.Scrollbar(operations_text_frame, orient=tk.VERTICAL, 
                                          command=self.operations_text.yview)
        operations_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.operations_text.config(yscrollcommand=operations_scrollbar.set)
        
        # Initial button states
        self.update_button_states()
        
        # Bind events
        self.folder_organize_path.trace('w', self.on_folder_change)
        self.project_folder_path.trace('w', self.on_folder_change)

    def bind_mousewheel(self):
        """Bind mousewheel events to canvas for scrolling"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
            
        # Bind mouse wheel events
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)

    def update_button_states(self):
        """Update button states based on current state"""
        has_source = bool(self.folder_organize_path.get())
        has_dest = bool(self.project_folder_path.get())
        has_operation = hasattr(self, 'file_management_logic') and self.file_management_logic
        
        # Enable/disable action buttons
        self.copy_button.config(state=tk.NORMAL if (has_source and has_dest) else tk.DISABLED)
        self.move_button.config(state=tk.NORMAL if (has_source and has_dest) else tk.DISABLED)
        self.undo_button.config(state=tk.NORMAL if has_operation else tk.DISABLED)
        
        # Update button colors based on state
        if has_source and has_dest:
            self.copy_button.config(bg='#27ae60')
            self.move_button.config(bg='#e74c3c')
        else:
            self.copy_button.config(bg='#bdc3c7')
            self.move_button.config(bg='#bdc3c7')
            
        if has_operation:
            self.undo_button.config(bg='#f39c12')
        else:
            self.undo_button.config(bg='#bdc3c7')

    def on_folder_change(self, *args):
        """Called when folder paths change"""
        self.update_button_states()
        self.update_file_info()

    def update_file_info(self):
        """Update file count and information display"""
        source_path = self.folder_organize_path.get()
        if source_path and os.path.exists(source_path):
            try:
                files = [f for f in os.listdir(source_path) 
                        if os.path.isfile(os.path.join(source_path, f))]
                count = len(files)
                self.file_count_label.config(
                    text=f"📁 Source folder contains {count} file(s)",
                    fg='#27ae60' if count > 0 else '#e74c3c'
                )
            except Exception as e:
                self.file_count_label.config(text=f"Error reading folder: {str(e)}", fg='#e74c3c')
        else:
            self.file_count_label.config(text="No source folder selected", fg='#7f8c8d')

    def log_operation(self, message):
        """Log operation to the operations text widget"""
        self.operations_text.insert(tk.END, f"{message}\n")
        self.operations_text.see(tk.END)
        
        # Keep only last 50 lines
        lines = self.operations_text.get("1.0", tk.END).split('\n')
        if len(lines) > 50:
            self.operations_text.delete("1.0", tk.END)
            self.operations_text.insert(tk.END, '\n'.join(lines[-50:]))

    def choose_folder1(self):
        folder_path = filedialog.askdirectory(title="Select Source Folder")
        if folder_path:
            self.folder_organize_path.set(folder_path)
            self.log_operation(f"Source folder selected: {folder_path}")

    def choose_folder2(self):
        folder_path = filedialog.askdirectory(title="Select Destination Folder")
        if folder_path:
            self.project_folder_path.set(folder_path)
            self.log_operation(f"Destination folder selected: {folder_path}")

    def undo_action(self):
        if hasattr(self, 'file_management_logic') and self.file_management_logic:
            success = self.file_management_logic.undo_last_action()
            if success:
                self.log_operation("Undo operation completed successfully")
                self.file_management_logic = None  # Reset after undo
                self.update_button_states()
            else:
                messagebox.showwarning("Warning", "No operation to undo or undo operation failed. Check console for details.")
                self.log_operation("Undo operation failed")
        else:
            messagebox.showwarning("Warning", "No file operation has been performed yet.")
            self.log_operation("No operation to undo")

    def copy_action(self):
        self._perform_operation('copy', "Copying files...")

    def move_action(self):
        self._perform_operation('move', "Moving files...")

    def _perform_operation(self, operation_type, status_message):
        target_folder = self.folder_organize_path.get()
        project_folder = self.project_folder_path.get()
        format_type = self.dropdown_var.get()

        if not target_folder or not project_folder:
            messagebox.showwarning("Warning", "Please select both source and destination folders.")
            return

        # Update UI
        self.log_operation(f"Starting {operation_type} operation...")
        
        try:
            self.file_management_logic = FileManagementLogic(target_folder, project_folder, format_type)
            
            # Get file count for progress
            file_count = self.file_management_logic.get_target_folder_files_count()
            if file_count == 0:
                messagebox.showwarning("Warning", "Source folder is empty!")
                self.log_operation("Source folder is empty")
                return
            
            
            # Perform operation
            if operation_type == 'copy':
                result = self.file_management_logic.copy()
            else:
                result = self.file_management_logic.move()
            
            
            if result:
                processed_files, errors = result
                if errors:
                    messagebox.showwarning("Warning", f"Some files could not be {operation_type}d. Check console for details.")
                    self.log_operation(f"⚠️ {operation_type} completed with {len(errors)} errors")
                else:
                    messagebox.showinfo("Success", f"Successfully {operation_type}d {len(processed_files)} files to their respective date folders.")
                    self.log_operation(f"✅ {operation_type} operation completed: {len(processed_files)} files processed")
                
                # Update button states
                self.update_button_states()
            else:
                messagebox.showerror("Error", f"{operation_type} operation failed!")
                self.log_operation(f"❌ {operation_type} operation failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.log_operation(f"Error during {operation_type}: {str(e)}")

if __name__ == '__main__':
    app = FileChooserApp()
    app.mainloop()