import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import sys
import threading
from typing import Dict, List

# Add parent directory to path to import from other folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract.cv_extractor import CVExtractor
from extract.regex import parse_cv_sections

class CVAnalyzerApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("LinkedOut")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        # Initialize class properties
        self.current_file_paths: List[str] = []
        self.analysis_results: Dict[str, dict] = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main Scrollable Frame
        self.main_scrollable = ctk.CTkScrollableFrame(self.root, corner_radius=0, fg_color="transparent")
        self.main_scrollable.pack(fill="both", expand=True)
        
        # Main Container
        main_frame = ctk.CTkFrame(self.main_scrollable, corner_radius=0, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header section
        header_frame = ctk.CTkFrame(main_frame, height=100, corner_radius=20, fg_color=("#2B2B2B", "#1A1A1A"))
        header_frame.pack(fill="x", pady=(0, 25))
        header_frame.pack_propagate(False)
        ctk.CTkLabel(header_frame, text="LinkedOut", font=ctk.CTkFont(size=32, weight="bold", family="Helvetica"), text_color="#4A90E2").place(relx=0.5, rely=0.35, anchor="center")
        ctk.CTkLabel(header_frame, text="Analyze Multiple CVs Easily", font=ctk.CTkFont(size=14, family="Helvetica"), text_color="#A0A0A0").place(relx=0.5, rely=0.75, anchor="center")
        
        # Search section
        search_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=("#2B2B2B", "#1A1A1A"))
        search_frame.pack(fill="x", pady=(0, 25))
        search_row = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_row.pack(pady=30)
        self.search_entry = ctk.CTkEntry(search_row, placeholder_text="Enter keywords (e.g., React, Tailwind, HTML)", font=ctk.CTkFont(size=14, family="Helvetica"), height=40, width=400)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_btn = ctk.CTkButton(search_row, text="Search", font=ctk.CTkFont(size=14, weight="bold", family="Helvetica"), height=40, width=100, fg_color="#4A90E2", hover_color="#357ABD", command=self.search_keywords)
        self.search_btn.pack(side="left", padx=(0, 20))
        
        # Upload section
        upload_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=("#2B2B2B", "#1A1A1A"))
        upload_frame.pack(fill="x", pady=(0, 25))
        self.upload_btn = ctk.CTkButton(upload_frame, text="Upload CVs (PDF)", font=ctk.CTkFont(size=16, weight="bold", family="Helvetica"), height=50, corner_radius=25, fg_color="#4A90E2", hover_color="#357ABD", command=self.upload_files)
        self.upload_btn.pack(pady=20)
        self.file_info_label = ctk.CTkLabel(upload_frame, text="No files selected", font=ctk.CTkFont(size=12, family="Helvetica"), text_color="#A0A0A0")
        self.file_info_label.pack(pady=(0, 20))
        
        # Results section with columns
        results_container = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=("#2B2B2B", "#1A1A1A"))
        results_container.pack(fill="both", expand=True)

        # Left column (File List and Top Matches)
        left_column = ctk.CTkFrame(results_container, fg_color="transparent", width=200)
        left_column.pack(side="left", fill="y", padx=(20, 10), pady=20)
        
        # File List
        ctk.CTkLabel(left_column, text="Uploaded CVs", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
        self.file_listbox = ctk.CTkTextbox(left_column, wrap="word", font=ctk.CTkFont(size=12, family="Helvetica"), width=180, height=200)
        self.file_listbox.pack(fill="x", expand=False)
        self.file_listbox.bind("<<TextSelect>>", self.on_file_select)
        
        # Top Matches
        ctk.CTkLabel(left_column, text="Top Matches", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        self.top_matches_textbox = ctk.CTkTextbox(left_column, wrap="word", font=ctk.CTkFont(size=12, family="Helvetica"), width=180)
        self.top_matches_textbox.pack(fill="both", expand=True)
        self.top_matches_textbox.bind("<<TextSelect>>", self.on_match_select)

        # Right columns (CV Information)
        right_columns = ctk.CTkFrame(results_container, fg_color="transparent")
        right_columns.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=20)
        
        # Create columns for different sections
        columns = [
            ("Summary", "summary"),
            ("Skills", "skills"),
            ("Experience", "experience"),
            ("Education", "education")
        ]
        
        self.info_textboxes = {}
        for title, key in columns:
            column_frame = ctk.CTkFrame(right_columns, fg_color="transparent")
            column_frame.pack(side="left", fill="both", expand=True, padx=5)
            
            ctk.CTkLabel(column_frame, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
            textbox = ctk.CTkTextbox(column_frame, wrap="word", font=ctk.CTkFont(size=12, family="Helvetica"))
            textbox.pack(fill="both", expand=True)
            self.info_textboxes[key] = textbox
        
        self.show_initial_message()
        
    def show_initial_message(self):
        for textbox in self.info_textboxes.values():
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("1.0", "Upload CVs to see the extracted information.")
            textbox.configure(state="disabled")
        
    def upload_files(self):
        file_paths = filedialog.askopenfilenames(title="Select CV PDF Files", filetypes=[("PDF files", "*.pdf")])
        if file_paths:
            self.current_file_paths = list(file_paths)
            self.file_info_label.configure(text=f"Selected: {len(file_paths)} files")
            self.upload_btn.configure(text="Analyzing...", state="disabled", fg_color="#666666")
            
            # Update file list
            self.file_listbox.configure(state="normal")
            self.file_listbox.delete("1.0", "end")
            for path in file_paths:
                self.file_listbox.insert("end", f"{os.path.basename(path)}\n")
            self.file_listbox.configure(state="disabled")
            
            # Start analysis in background
            threading.Thread(target=self.analyze_cvs, daemon=True).start()
    
    def analyze_cvs(self):
        try:
            for file_path in self.current_file_paths:
                print(f"\nProcessing file: {file_path}")
                
                # Extract text using CVExtractor
                cv_extractor = CVExtractor(file_path)
                cv_extractor.process()
                raw_text = cv_extractor.retrieve_raw_text()
                print("\nExtracted text sample:")
                print(raw_text[:500] + "...")
                
                # Extract sections using regex
                sections = parse_cv_sections(raw_text)
                
                # Store results
                results = {
                    'summary': sections['summary'],
                    'skills': sections['skills'],
                    'experience': sections['experience'],
                    'education': sections['education'],
                    'text': raw_text  # Keep raw text for keyword search
                }
                self.analysis_results[file_path] = results
                self.root.after(0, self.update_file_status, file_path, "✓")
        except Exception as e:
            print(f"Error in analyze_cvs: {str(e)}")
            self.root.after(0, self.show_error, str(e))
        finally:
            self.root.after(0, self.reset_upload_button)
    
    def update_file_status(self, file_path: str, status: str):
        """Update the status of a file in the list"""
        self.file_listbox.configure(state="normal")
        content = self.file_listbox.get("1.0", "end")
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if os.path.basename(file_path) in line:
                lines[i] = f"{os.path.basename(file_path)} {status}"
                break
        self.file_listbox.delete("1.0", "end")
        self.file_listbox.insert("1.0", "\n".join(lines))
        self.file_listbox.configure(state="disabled")
    
    def reset_upload_button(self):
        self.upload_btn.configure(text="Upload CVs (PDF)", state="normal", fg_color="#4A90E2")
    
    def show_error(self, error_message):
        messagebox.showerror("Analysis Error", f"An error occurred: {error_message}")
    
    def on_file_select(self, event):
        """Handle file selection from the list"""
        try:
            # Get selected text
            selected_text = self.file_listbox.get("sel.first", "sel.last")
            selected_file = selected_text.strip().split(" ")[0]  # Remove status if present
            
            # Find the full path
            for path in self.current_file_paths:
                if os.path.basename(path) == selected_file:
                    self.display_results(self.analysis_results[path])
                    break
        except:
            pass  # Ignore if no text is selected
    
    def on_match_select(self, event):
        """Handle selection from top matches"""
        try:
            # Get selected text
            selected_text = self.top_matches_textbox.get("sel.first", "sel.last")
            selected_file = selected_text.strip().split(" - ")[0]  # Get filename before match count
            
            # Find the full path and display results
            for path in self.current_file_paths:
                if os.path.basename(path) == selected_file:
                    self.display_results(self.analysis_results[path])
                    break
        except:
            pass  # Ignore if no text is selected
    
    def display_results(self, results):
        for key in self.info_textboxes:
            self.info_textboxes[key].configure(state="normal")
            self.info_textboxes[key].delete("1.0", "end")
            self.info_textboxes[key].insert("1.0", results.get(key, 'N/A'))
            self.info_textboxes[key].configure(state="disabled")

    def search_keywords(self):
        if not self.current_file_paths:
            messagebox.showwarning("Warning", "Please upload and analyze CVs first.")
            return
            
        keywords_input = self.search_entry.get().strip()
        if not keywords_input:
            messagebox.showwarning("Warning", "Please enter keywords to search.")
            return
            
        keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
        
        # Store match counts for each file
        file_matches = []
        
        # Search in all analyzed files
        for file_path in self.current_file_paths:
            if file_path in self.analysis_results:
                results = self.analysis_results[file_path]
                if 'text' in results:
                    text = results['text'].lower()  # Convert to lowercase once
                    total_matches = 0
                    for keyword in keywords:
                        # Use case-insensitive search
                        matches = text.count(keyword.lower())
                        total_matches += matches
                    
                    if total_matches > 0:
                        file_matches.append((os.path.basename(file_path), total_matches, file_path))
        
        # Sort files by match count (descending)
        file_matches.sort(key=lambda x: x[1], reverse=True)
        
        # Update top matches display
        self.top_matches_textbox.configure(state="normal")
        self.top_matches_textbox.delete("1.0", "end")
        
        if file_matches:
            self.top_matches_textbox.insert("1.0", "Top Matching CVs:\n\n")
            for filename, count, _ in file_matches:
                self.top_matches_textbox.insert("end", f"{filename} - {count} matches\n")
            
            # Display the first matching file's information
            first_match_path = file_matches[0][2]
            self.display_results(self.analysis_results[first_match_path])
        else:
            self.top_matches_textbox.insert("1.0", "No matches found.")
            # Clear all columns
            for textbox in self.info_textboxes.values():
                textbox.configure(state="normal")
                textbox.delete("1.0", "end")
                textbox.insert("1.0", "No matches found.")
                textbox.configure(state="disabled")
        
        self.top_matches_textbox.configure(state="disabled")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CVAnalyzerApp()
    app.run()