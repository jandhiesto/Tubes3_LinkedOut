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
            text="📁 Upload CV (PDF)",
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
            # Update UI in main thread
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
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CVAnalyzerApp()
    app.run() 