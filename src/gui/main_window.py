# gui/main_window.py
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk
import os
import sys
import threading
import time
import json
import webbrowser

# Menambahkan path ke direktori induk
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract.cv_extractor import CVExtractor
from pattern.matching import kmp_search, boyer_moore_search, levenshtein_distance
from database_connector.query_service import insert_full_applicant, get_all_applicants_with_details

class CVAnalyzerApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("LinkedOut - Applicant Tracker")
        self.root.geometry("1400x900")
        
        self.cv_extractor = CVExtractor()
        self.all_applicants = []
        
        self.setup_ui()
        self.load_applicants()

    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # --- Top Frame for Controls ---
        top_frame = ctk.CTkFrame(self.root, corner_radius=0)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(1, weight=1)

        # Upload Button
        self.upload_btn = ctk.CTkButton(top_frame, text="Upload New CV", command=self.upload_cv_flow)
        self.upload_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # Search Entry
        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="Search by keywords (e.g., python, react, manager)...", width=400)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Search Button
        self.search_btn = ctk.CTkButton(top_frame, text="Search", command=self.start_search_thread)
        self.search_btn.grid(row=0, column=2, padx=10, pady=10)

        # --- Search Options Frame ---
        options_frame = ctk.CTkFrame(top_frame)
        options_frame.grid(row=0, column=3, padx=10, pady=10)
        
        ctk.CTkLabel(options_frame, text="Algorithm:").pack(side="left", padx=(10, 5))
        self.algo_dropdown = ctk.CTkComboBox(options_frame, values=["Boyer-Moore", "KMP"])
        self.algo_dropdown.set("Boyer-Moore")
        self.algo_dropdown.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(options_frame, text="Max Results:").pack(side="left", padx=(10, 5))
        self.results_count_entry = ctk.CTkEntry(options_frame, width=50)
        self.results_count_entry.insert(0, "10")
        self.results_count_entry.pack(side="left", padx=(0, 10))


        # --- Main Frame for Results ---
        self.main_frame = ctk.CTkScrollableFrame(self.root, label_text="Applicant Database")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # --- Status Bar ---
        self.status_bar = ctk.CTkLabel(self.root, text="Ready.", anchor="w")
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

    def load_applicants(self):
        self.status_bar.configure(text="Loading applicants from database...")
        self.all_applicants = get_all_applicants_with_details()
        self.display_applicants(self.all_applicants)
        self.status_bar.configure(text=f"Ready. {len(self.all_applicants)} applicants loaded.")

    def display_applicants(self, applicants_to_display):
        # Clear previous results
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        if not applicants_to_display:
            ctk.CTkLabel(self.main_frame, text="No applicants found.").pack(pady=20)
            return

        for i, applicant in enumerate(applicants_to_display):
            match_count = applicant.get('match_count', 0)
            
            card = ctk.CTkFrame(self.main_frame, corner_radius=10)
            card.pack(fill="x", padx=10, pady=5)

            name_text = f"{applicant['first_name']} {applicant['last_name']}"
            role_text = f"Role: {applicant['application_role']}"
            
            ctk.CTkLabel(card, text=name_text, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=(10, 0))
            ctk.CTkLabel(card, text=role_text, text_color="gray").pack(anchor="w", padx=15)
            
            if match_count > 0:
                match_text = f"Matches: {match_count}"
                ctk.CTkLabel(card, text=match_text, text_color="#4A90E2").pack(anchor="w", padx=15, pady=(0,10))

            details_btn = ctk.CTkButton(card, text="View Details", command=lambda a=applicant: self.show_applicant_summary(a))
            details_btn.place(relx=0.98, rely=0.5, anchor="e", relwidth=0.15)


    def upload_cv_flow(self):
        file_path = filedialog.askopenfilename(title="Select CV PDF", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        first_name = simpledialog.askstring("Input", "Enter Applicant's First Name:", parent=self.root)
        if not first_name: return
        last_name = simpledialog.askstring("Input", "Enter Applicant's Last Name:", parent=self.root)
        if not last_name: return
        role = simpledialog.askstring("Input", "Enter Role Applied For:", parent=self.root)
        if not role: return

        self.status_bar.configure(text=f"Analyzing CV: {os.path.basename(file_path)}...")
        self.root.update_idletasks()

        try:
            # Di cv_extractor, text diekstrak dulu
            text_for_regex = self.cv_extractor._extract_text_for_regex(file_path)
            
            # Baru panggil extract_all_info dengan nama
            # Ini memerlukan modifikasi kecil pada `cv_extractor.py` atau `info_extractor.py`
            # Untuk simplicity, kita modifikasi panggilan di sini.
            # Impor extract_all_info secara langsung untuk tujuan ini
            from extract.info_extractor import extract_all_info
            
            structured_info = extract_all_info(text_for_regex, first_name, last_name)
            
            insert_full_applicant(structured_info, role, file_path)
            
            messagebox.showinfo("Success", "Applicant has been successfully added to the database.")
            self.load_applicants() # Refresh list
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process and save CV.\n{e}")
            self.status_bar.configure(text="Error during upload.")


    def start_search_thread(self):
        keywords_str = self.search_entry.get().strip()
        if not keywords_str:
            self.load_applicants() # If search is cleared, show all
            return

        self.search_btn.configure(text="Searching...", state="disabled")
        self.status_bar.configure(text="Searching...")
        
        # Jalankan pencarian di thread terpisah agar UI tidak freeze
        threading.Thread(target=self.perform_search, daemon=True).start()


    def perform_search(self):
        keywords_str = self.search_entry.get().strip().lower()
        keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
        
        algo_name = self.algo_dropdown.get()
        search_algorithm = boyer_moore_search if algo_name == "Boyer-Moore" else kmp_search
        
        max_results = int(self.results_count_entry.get())

        # --- Exact Match Search ---
        start_time_exact = time.time()
        
        results = []
        found_keywords = set()

        for applicant in self.all_applicants:
            match_count = 0
            # Gabungkan semua text-based field menjadi satu string besar untuk dicari
            searchable_text = " ".join([
                str(applicant.get('summary', '')),
                " ".join(applicant.get('skills', [])),
                str(applicant.get('experience', '')),
                str(applicant.get('education', ''))
            ]).lower()

            for keyword in keywords:
                matches = search_algorithm(searchable_text, keyword)
                if matches:
                    match_count += len(matches)
                    found_keywords.add(keyword)
            
            if match_count > 0:
                applicant_copy = applicant.copy()
                applicant_copy['match_count'] = match_count
                results.append(applicant_copy)
        
        time_exact = time.time() - start_time_exact

        # --- Fuzzy Match Search (jika diperlukan) ---
        time_fuzzy = 0
        unfound_keywords = [k for k in keywords if k not in found_keywords]
        
        if unfound_keywords:
            start_time_fuzzy = time.time()
            for applicant in self.all_applicants:
                # Cek apakah pelamar sudah ada di 'results'
                res_applicant = next((res for res in results if res['applicant_id'] == applicant['applicant_id']), None)
                
                if not res_applicant: # Jika belum, tambahkan ke results agar bisa diupdate
                    res_applicant = applicant.copy()
                    res_applicant['match_count'] = 0
                    results.append(res_applicant)

                searchable_text_tokens = " ".join([
                    str(applicant.get('summary', '')),
                    " ".join(applicant.get('skills', [])),
                    str(applicant.get('experience', '')),
                    str(applicant.get('education', ''))
                ]).lower().split()
                
                fuzzy_match_count = 0
                for keyword in unfound_keywords:
                    for token in searchable_text_tokens:
                        # Jarak Levenshtein <= 2 dianggap relevan
                        if levenshtein_distance(keyword, token) <= 2:
                            fuzzy_match_count += 1
                
                res_applicant['match_count'] += fuzzy_match_count

            time_fuzzy = time.time() - start_time_fuzzy

        # --- Finalize and Display ---
        # Hapus pelamar yang tidak punya match sama sekali
        final_results = [r for r in results if r.get('match_count', 0) > 0]
        
        # Urutkan berdasarkan jumlah match terbanyak
        final_results.sort(key=lambda x: x['match_count'], reverse=True)
        
        # Batasi jumlah hasil
        final_results = final_results[:max_results]
        
        # Update UI di main thread
        self.root.after(0, self.update_ui_after_search, final_results, time_exact, time_fuzzy)

    def update_ui_after_search(self, results, time_exact, time_fuzzy):
        self.display_applicants(results)
        
        status_text = f"Found {len(results)} applicants. "
        status_text += f"Exact search ({self.algo_dropdown.get()}) took: {time_exact:.4f}s. "
        if time_fuzzy > 0:
            status_text += f"Fuzzy search (Levenshtein) took: {time_fuzzy:.4f}s."
            
        self.status_bar.configure(text=status_text)
        self.search_btn.configure(text="Search", state="normal")

    def show_applicant_summary(self, applicant):
        summary_window = ctk.CTkToplevel(self.root)
        summary_window.title(f"Summary: {applicant['first_name']} {applicant['last_name']}")
        summary_window.geometry("800x600")

        scroll_frame = ctk.CTkScrollableFrame(summary_window)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Helper function to create sections
        def create_section(parent, title, content):
            ctk.CTkLabel(parent, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=5, pady=(10, 2))
            
            if isinstance(content, list):
                content_text = "\n".join([f"- {item}" for item in content])
            elif isinstance(content, str):
                content_text = content
            else:
                content_text = str(content) # Fallback

            ctk.CTkLabel(parent, text=content_text, wraplength=700, justify="left").pack(anchor="w", padx=15)
            ctk.CTkFrame(parent, height=2, fg_color="gray").pack(fill="x", padx=5, pady=10)

        # Displaying info
        create_section(scroll_frame, "Applicant Name", f"{applicant['first_name']} {applicant['last_name']}")
        create_section(scroll_frame, "Contact", f"Email: {applicant['email']}\nPhone: {applicant['phone_number']}")
        create_section(scroll_frame, "Role Applied For", applicant['application_role'])
        create_section(scroll_frame, "Summary", applicant['summary'])
        
        # Format skills, experience, education
        skills_str = ", ".join(applicant.get('skills', ['N/A']))
        create_section(scroll_frame, "Skills", skills_str)

        exp_list = [f"{e['title']} at {e['company']} ({e['date_range']})" for e in applicant.get('experience', [])]
        create_section(scroll_frame, "Work Experience", exp_list if exp_list else ["N/A"])

        edu_list = [f"{e['degree']} from {e['institution']} ({e['date_range']})" for e in applicant.get('education', [])]
        create_section(scroll_frame, "Education", edu_list if edu_list else ["N/A"])

        # Button to open CV
        cv_path = applicant.get('cv_path')
        if cv_path and os.path.exists(cv_path):
            open_cv_btn = ctk.CTkButton(summary_window, text="Open Original CV File", command=lambda p=cv_path: webbrowser.open(p))
            open_cv_btn.pack(pady=10)


    def run(self):
        self.root.mainloop()