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
        self.root.title("LinkedOut")
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
            text="CV Analysis Results",
            font=ctk.CTkFont(size=20, weight="bold", family="Helvetica"),
            text_color="#4A90E2"
        )
        results_title.pack(pady=(20, 15))
        
        # Create tabs for different sections
        self.tabview = ctk.CTkTabview(results_frame)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Add tabs
        self.tabview.add("All")
        self.tabview.add("Summary")
        self.tabview.add("Skills")
        self.tabview.add("Experience")
        self.tabview.add("Education")
        
        # Create text areas for each tab
        self.all_text = ctk.CTkTextbox(
            self.tabview.tab("All"),
            wrap="word",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            fg_color=("#333333", "#222222"),
            text_color="#FFFFFF",
            height=400
        )
        self.all_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.summary_text = ctk.CTkTextbox(
            self.tabview.tab("Summary"),
            wrap="word",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            fg_color=("#333333", "#222222"),
            text_color="#FFFFFF",
            height=400
        )
        self.summary_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.skills_text = ctk.CTkTextbox(
            self.tabview.tab("Skills"),
            wrap="word",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            fg_color=("#333333", "#222222"),
            text_color="#FFFFFF",
            height=400
        )
        self.skills_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.experience_text = ctk.CTkTextbox(
            self.tabview.tab("Experience"),
            wrap="word",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            fg_color=("#333333", "#222222"),
            text_color="#FFFFFF",
            height=400
        )
        self.experience_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.education_text = ctk.CTkTextbox(
            self.tabview.tab("Education"),
            wrap="word",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            fg_color=("#333333", "#222222"),
            text_color="#FFFFFF",
            height=400
        )
        self.education_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Show initial message
        self.show_initial_message()
        
    def show_initial_message(self):
        """Show initial message in results area"""
        initial_message = "Upload a CV to see the analysis results"
        for text_widget in [self.all_text, self.summary_text, self.skills_text, self.experience_text, self.education_text]:
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", initial_message)
            text_widget.configure(state="disabled")
        
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
            
            # Start analysis thread
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
        if 'error' in results:
            self.show_error(results['error'])
            return
            
        # Enable all text widgets
        for text_widget in [self.all_text, self.summary_text, self.skills_text, self.experience_text, self.education_text]:
            text_widget.configure(state="normal")
            text_widget.delete("1.0", "end")
        
        # Display All (raw extracted text)
        if results.get('text'):
            self.all_text.insert("1.0", results['text'])
        else:
            self.all_text.insert("1.0", "No raw text found")
        
        # Display Summary
        if results.get('summary'):
            self.summary_text.insert("1.0", "\n".join(results['summary']))
        else:
            self.summary_text.insert("1.0", "No summary found")
            
        # Display Skills
        if results.get('skills'):
            self.skills_text.insert("1.0", "\n".join(results['skills']))
        else:
            self.skills_text.insert("1.0", "No skills found")
            
        # Display Work Experience
        if results.get('work_experience'):
            experience_text = "\n".join(results['work_experience'])
            self.experience_text.insert("1.0", experience_text)
        else:
            self.experience_text.insert("1.0", "No work experience found")
            
        # Display Education
        if results.get('education'):
            self.education_text.insert("1.0", "\n".join(results['education']))
        else:
            self.education_text.insert("1.0", "No education information found")
            
        # Disable all text widgets
        for text_widget in [self.all_text, self.summary_text, self.skills_text, self.experience_text, self.education_text]:
            text_widget.configure(state="disabled")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = CVAnalyzerApp()
    app.run() 