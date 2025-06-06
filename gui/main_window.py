import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import sys
import threading

# Add the parent directory to the path to import from extract folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from extract.cv_extractor import CVExtractor

class CVAnalyzerApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("CV Regex Extractor")
        self.root.geometry("1000x700")
        self.root.minsize(1000, 700)
        
        self.cv_extractor = CVExtractor()
        self.current_file_path = None
        self.current_algorithm = "KMP"  # Default algorithm
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main 
        self.main_scrollable = ctk.CTkScrollableFrame(
            self.root,
            corner_radius=0,
            fg_color="transparent"
        )
        self.main_scrollable.pack(fill="both", expand=True)
        
        # Main container
        main_frame = ctk.CTkFrame(
            self.main_scrollable, 
            corner_radius=0, 
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header section
        header_frame = ctk.CTkFrame(
            main_frame, 
            height=100, 
            corner_radius=20,
            fg_color=("#2B2B2B", "#1A1A1A")
        )
        header_frame.pack(fill="x", pady=(0, 25))
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="LinkedOut",
            font=ctk.CTkFont(size=32, weight="bold", family="Helvetica"),
            text_color="#4A90E2"
        )
        title_label.place(relx=0.5, rely=0.35, anchor="center")
    
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Analyze CV Easily",
            font=ctk.CTkFont(size=14, family="Helvetica"),
            text_color="#A0A0A0"
        )
        subtitle_label.place(relx=0.5, rely=0.75, anchor="center")
        
        # Search section
        search_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=20,
            fg_color=("#2B2B2B", "#1A1A1A")
        )
        search_frame.pack(fill="x", pady=(0, 25))
        
        # Gabungkan search bar, tombol, dan toggle dalam satu baris
        search_row = ctk.CTkFrame(
            search_frame,
            fg_color="transparent"
        )
        search_row.pack(pady=30)
        
        # Search input
        self.search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Enter keywords (e.g., React, Tailwind, HTML)",
            font=ctk.CTkFont(size=14, family="Helvetica"),
            height=40,
            width=400
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        # Search button
        self.search_btn = ctk.CTkButton(
            search_row,
            text="Search",
            font=ctk.CTkFont(size=14, weight="bold", family="Helvetica"),
            height=40,
            width=100,
            fg_color="#4A90E2",
            hover_color="#357ABD",
            command=self.search_keywords
        )
        self.search_btn.pack(side="left", padx=(0, 20))
        
        # Label KMP
        algorithm_kmp_label = ctk.CTkLabel(
            search_row,
            text="KMP",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color="#A0A0A0"
        )
        algorithm_kmp_label.pack(side="left", padx=(0, 5))
        
        # Algorithm toggle
        self.algorithm_switch = ctk.CTkSwitch(
            search_row,
            text="",
            width=50,
            command=self.toggle_algorithm,
            onvalue=True,
            offvalue=False
        )
        self.algorithm_switch.pack(side="left", padx=(0, 5))
        
        # Label BM
        algorithm_bm_label = ctk.CTkLabel(
            search_row,
            text="BM",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color="#A0A0A0"
        )
        algorithm_bm_label.pack(side="left")
        
        # Upload section
        upload_frame = ctk.CTkFrame(
            main_frame, 
            corner_radius=20,
            fg_color=("#2B2B2B", "#1A1A1A")
        )
        upload_frame.pack(fill="x", pady=(0, 25))
        
        # Upload button 
        self.upload_btn = ctk.CTkButton(
            upload_frame,
            text="Upload CV (PDF)",
            font=ctk.CTkFont(size=16, weight="bold", family="Helvetica"),
            height=50,
            corner_radius=25,
            fg_color="#4A90E2",
            hover_color="#357ABD",
            command=self.upload_file
        )
        self.upload_btn.pack(pady=20)
        
        # File info label 
        self.file_info_label = ctk.CTkLabel(
            upload_frame,
            text="No file selected",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color="#A0A0A0"
        )
        self.file_info_label.pack(pady=(0, 20))
        
        # Results section
        results_frame = ctk.CTkFrame(
            main_frame, 
            corner_radius=20,
            fg_color=("#2B2B2B", "#1A1A1A")
        )
        results_frame.pack(fill="both", expand=True)
        
        # Results title
        results_title = ctk.CTkLabel(
            results_frame,
            text="Extracted Text",
            font=ctk.CTkFont(size=20, weight="bold", family="Helvetica"),
            text_color="#4A90E2"
        )
        results_title.pack(pady=(20, 15))
        
        # Results text area
        self.results_text = ctk.CTkTextbox(
            results_frame,
            wrap="word",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            fg_color=("#333333", "#222222"),
            text_color="#FFFFFF",
            height=400
        )
        self.results_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Show initial message
        self.show_initial_message()
        
    def show_initial_message(self):
        """Show initial message in results area"""
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", "Upload a CV to see the extracted text")
        self.results_text.configure(state="disabled")
        
    def upload_file(self):
        """Handle file upload"""
        file_path = filedialog.askopenfilename(
            title="Select CV PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.current_file_path = file_path
            filename = os.path.basename(file_path)
            self.file_info_label.configure(text=f"Selected: {filename}")
            
            # Start analysis thread info ui
            self.upload_btn.configure(
                text="Analyzing...", 
                state="disabled",
                fg_color="#666666"
            )
            threading.Thread(target=self.analyze_cv, daemon=True).start()
    
    def analyze_cv(self):
        try:
            results = self.cv_extractor.analyze_cv(self.current_file_path)
            # Update ui in main thread
            self.root.after(0, lambda: self.display_results(results))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))
        finally:
            self.root.after(0, self.reset_upload_button)
    
    def reset_upload_button(self):
        self.upload_btn.configure(
            text="Upload CV (PDF)", 
            state="normal",
            fg_color="#4A90E2"
        )
    
    def show_error(self, error_message):
        messagebox.showerror("Analysis Error", f"An error occurred: {error_message}")
    
    def display_results(self, results):
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        
        if 'error' in results:
            self.results_text.insert("1.0", f"Error: {results['error']}")
        elif 'text' in results:
            self.results_text.insert("1.0", results['text'])
        
        self.results_text.configure(state="disabled")
    
    def toggle_algorithm(self):
        self.current_algorithm = "Boyer-Moore" if self.algorithm_switch.get() else "KMP"
    
    def search_keywords(self):
        if not self.current_file_path:
            messagebox.showwarning("Warning", "Please upload a CV first")
            return
            
        keywords = self.search_entry.get().strip()
        if not keywords:
            messagebox.showwarning("Warning", "Please enter keywords to search")
            return
            
        # TODO: Implement search using selected algorithm
        messagebox.showinfo("Search", f"Searching for '{keywords}' using {self.current_algorithm} algorithm")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CVAnalyzerApp()
    app.run() 