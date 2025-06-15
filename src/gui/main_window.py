import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import sys
import threading

# Tambahkan path ke direktori induk agar bisa mengimpor dari folder lain
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract.cv_extractor import CVExtractor
from pattern.matching import kmp_search, boyer_moore_search

class CVAnalyzerApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("LinkedOut")
        self.root.geometry("1200x800") # Lebarkan window untuk 2 kolom
        self.root.minsize(1000, 700)
        
        # --- Inisialisasi Properti Kelas ---
        self.cv_extractor = CVExtractor()
        self.current_file_path = None
        self.current_algorithm = "KMP"
        self.current_text_for_pattern_matching = "" # Teks bersih untuk KMP/BM
        
        self.setup_ui()
        
    def setup_ui(self):
        # ... (Bagian Header dan Search Frame tetap sama) ...
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
        ctk.CTkLabel(header_frame, text="Analyze CV Easily", font=ctk.CTkFont(size=14, family="Helvetica"), text_color="#A0A0A0").place(relx=0.5, rely=0.75, anchor="center")
        
        # Search section
        search_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=("#2B2B2B", "#1A1A1A"))
        search_frame.pack(fill="x", pady=(0, 25))
        search_row = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_row.pack(pady=30)
        self.search_entry = ctk.CTkEntry(search_row, placeholder_text="Enter keywords (e.g., React, Tailwind, HTML)", font=ctk.CTkFont(size=14, family="Helvetica"), height=40, width=400)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_btn = ctk.CTkButton(search_row, text="Search", font=ctk.CTkFont(size=14, weight="bold", family="Helvetica"), height=40, width=100, fg_color="#4A90E2", hover_color="#357ABD", command=self.search_keywords)
        self.search_btn.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(search_row, text="KMP", font=ctk.CTkFont(size=12, family="Helvetica"), text_color="#A0A0A0").pack(side="left", padx=(0, 5))
        self.algorithm_switch = ctk.CTkSwitch(search_row, text="", width=50, command=self.toggle_algorithm, onvalue=True, offvalue=False)
        self.algorithm_switch.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(search_row, text="BM", font=ctk.CTkFont(size=12, family="Helvetica"), text_color="#A0A0A0").pack(side="left")
        
        # Upload section
        upload_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=("#2B2B2B", "#1A1A1A"))
        upload_frame.pack(fill="x", pady=(0, 25))
        self.upload_btn = ctk.CTkButton(upload_frame, text="Upload CV (PDF)", font=ctk.CTkFont(size=16, weight="bold", family="Helvetica"), height=50, corner_radius=25, fg_color="#4A90E2", hover_color="#357ABD", command=self.upload_file)
        self.upload_btn.pack(pady=20)
        self.file_info_label = ctk.CTkLabel(upload_frame, text="No file selected", font=ctk.CTkFont(size=12, family="Helvetica"), text_color="#A0A0A0")
        self.file_info_label.pack(pady=(0, 20))
        
        # --- PERUBAHAN UTAMA: DUA KOLOM TEKS ---
        # Results section - sekarang menjadi container untuk dua kolom
        results_container = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=("#2B2B2B", "#1A1A1A"))
        results_container.pack(fill="both", expand=True)

        # Kolom Kiri (Regex)
        left_column = ctk.CTkFrame(results_container, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(20, 10), pady=20)
        ctk.CTkLabel(left_column, text="Teks untuk Regex & Highlighting", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
        self.regex_textbox = ctk.CTkTextbox(left_column, wrap="word", font=ctk.CTkFont(size=12, family="Helvetica"))
        self.regex_textbox.pack(fill="both", expand=True)
        self.regex_textbox.tag_config("highlight", background="yellow", foreground="black")

        # Kolom Kanan (Pattern Matching)
        right_column = ctk.CTkFrame(results_container, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=20)
        ctk.CTkLabel(right_column, text="Teks untuk Pattern Matching (KMP/BM)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
        self.pattern_textbox = ctk.CTkTextbox(right_column, wrap="word", font=ctk.CTkFont(size=12, family="Helvetica"))
        self.pattern_textbox.pack(fill="both", expand=True)
        
        self.show_initial_message()
        
    def show_initial_message(self):
        for textbox in [self.regex_textbox, self.pattern_textbox]:
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("1.0", "Upload a CV to see the extracted text.")
            textbox.configure(state="disabled")
        
    def upload_file(self):
        file_path = filedialog.askopenfilename(title="Select CV PDF File", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.current_file_path = file_path
            filename = os.path.basename(file_path)
            self.file_info_label.configure(text=f"Selected: {filename}")
            self.upload_btn.configure(text="Analyzing...", state="disabled", fg_color="#666666")
            threading.Thread(target=self.analyze_cv, daemon=True).start()
    
    def analyze_cv(self):
        try:
            results = self.cv_extractor.analyze_cv(self.current_file_path)
            # Simpan teks bersih untuk digunakan nanti oleh fungsi search
            self.current_text_for_pattern_matching = results.get('text_for_pattern_matching', '')
            self.root.after(0, self.display_results, results)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            self.root.after(0, self.reset_upload_button)
    
    def reset_upload_button(self):
        self.upload_btn.configure(text="Upload CV (PDF)", state="normal", fg_color="#4A90E2")
    
    def show_error(self, error_message):
        messagebox.showerror("Analysis Error", f"An error occurred: {error_message}")
    
    def display_results(self, results):
        # Mengisi kolom kiri (Regex)
        self.regex_textbox.configure(state="normal")
        self.regex_textbox.delete("1.0", "end")
        if 'text_for_regex' in results:
            self.regex_textbox.insert("1.0", results['text_for_regex'])
        elif 'error' in results:
            self.regex_textbox.insert("1.0", f"Error: {results['error']}")
        self.regex_textbox.configure(state="disabled")

        # Mengisi kolom kanan (Pattern Matching)
        self.pattern_textbox.configure(state="normal")
        self.pattern_textbox.delete("1.0", "end")
        if 'text_for_pattern_matching' in results:
            self.pattern_textbox.insert("1.0", results['text_for_pattern_matching'])
        elif 'error' in results:
            self.pattern_textbox.insert("1.0", f"Error: {results['error']}")
        self.pattern_textbox.configure(state="disabled")

    def toggle_algorithm(self):
        self.current_algorithm = "Boyer-Moore" if self.algorithm_switch.get() else "KMP"
    
    def search_keywords(self):
        if not self.current_text_for_pattern_matching:
            messagebox.showwarning("Warning", "Please upload and analyze a CV first.")
            return
            
        keywords_input = self.search_entry.get().strip()
        if not keywords_input:
            messagebox.showwarning("Warning", "Please enter keywords to search.")
            return
            
        keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
        search_algorithm = boyer_moore_search if self.algorithm_switch.get() else kmp_search
        
        # Aktifkan textbox KIRI untuk highlighting
        self.regex_textbox.configure(state="normal")
        self.regex_textbox.tag_remove("highlight", "1.0", "end")

        total_matches = 0
        match_summary = []

        for keyword in keywords:
            # Lakukan pencarian pada teks yang BERSIH
            matches_indices = search_algorithm(self.current_text_for_pattern_matching, keyword.lower())
            
            if matches_indices:
                total_matches += len(matches_indices)
                match_summary.append(f"'{keyword}': {len(matches_indices)} found")
                
                # Highlight dilakukan pada textbox KIRI (yang mudah dibaca)
                start_pos = '1.0'
                while True:
                    start_pos = self.regex_textbox.search(keyword, start_pos, stopindex='end', nocase=True)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(keyword)}c"
                    self.regex_textbox.tag_add("highlight", start_pos, end_pos)
                    start_pos = end_pos
        
        self.regex_textbox.configure(state="disabled")

        if total_matches > 0:
            summary_text = f"Total {total_matches} matches found.\n\n" + "\n".join(match_summary)
            messagebox.showinfo("Search Results", f"Algorithm: {self.current_algorithm}\n\n{summary_text}")
        else:
            messagebox.showinfo("Search Results", f"No matches found for the given keywords using {self.current_algorithm}.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CVAnalyzerApp()
    app.run()