import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import os
import sys
import threading
import time
from typing import Dict, List, Tuple
from dotenv import load_dotenv
import subprocess
from database_connector.query_service import QueryService
from pattern.kmp import kmp_search
from pattern.bm import boyer_moore_search
from pattern.fuzzy import fuzzy_search_all

# Add parent directory to path to import from other folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract.cv_extractor import CVExtractor
from extract.regex import parse_cv_sections
from gui.summary_window import SummaryWindow

class CVAnalyzerApp:
    def __init__(self):
        load_dotenv()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("LinkedOut")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        self.query_service = QueryService()
        self.current_file_paths: List[str] = []
        self.analysis_results: Dict[str, dict] = {}
        self.applicant_data: Dict[str, dict] = {}
        self.search_algorithm = "KMP"  # Default to KMP
        
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
        
        # Search input
        self.search_entry = ctk.CTkEntry(
            search_row, 
            placeholder_text="Enter keywords (e.g., React, Tailwind, HTML)", 
            font=ctk.CTkFont(size=14, family="Helvetica"), 
            height=40, 
            width=400
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        # Number of matches input
        self.matches_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Number of matches",
            font=ctk.CTkFont(size=14, family="Helvetica"),
            height=40,
            width=150
        )
        self.matches_entry.pack(side="left", padx=(0, 10))
        self.matches_entry.insert(0, "5")  # Default value
        
        # Algorithm selection
        self.algorithm_var = ctk.StringVar(value="KMP")
        algorithm_frame = ctk.CTkFrame(search_row, fg_color="transparent")
        algorithm_frame.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            algorithm_frame,
            text="Algorithm:",
            font=ctk.CTkFont(size=14, family="Helvetica")
        ).pack(side="left", padx=(0, 5))
        
        # Replace radio buttons with segmented button
        self.algorithm_selector = ctk.CTkSegmentedButton(
            algorithm_frame,
            values=["KMP", "BM"],
            variable=self.algorithm_var,
            font=ctk.CTkFont(size=14, family="Helvetica"),
            height=35,
            width=200,
            fg_color="#2B2B2B",
            selected_color="#4A90E2",
            selected_hover_color="#357ABD",
            unselected_color="#1A1A1A",
            unselected_hover_color="#2B2B2B",
            command=self.update_algorithm_label
        )
        self.algorithm_selector.pack(side="left", padx=(0, 10))
        
        # Add label to show current algorithm
        self.algorithm_label = ctk.CTkLabel(
            algorithm_frame,
            text="(Knuth-Morris-Pratt)",
            font=ctk.CTkFont(size=12, family="Helvetica"),
            text_color="#A0A0A0"
        )
        self.algorithm_label.pack(side="left")
        
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
        
        # Upload section
        upload_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=("#2B2B2B", "#1A1A1A"))
        upload_frame.pack(fill="x", pady=(0, 25))
        self.upload_btn = ctk.CTkButton(
            upload_frame, 
            text="Upload CVs (PDF)", 
            font=ctk.CTkFont(size=16, weight="bold", family="Helvetica"), 
            height=50, 
            corner_radius=25, 
            fg_color="#4A90E2", 
            hover_color="#357ABD", 
            command=self.upload_files
        )
        self.upload_btn.pack(pady=20)
        self.file_info_label = ctk.CTkLabel(
            upload_frame, 
            text="No files selected", 
            font=ctk.CTkFont(size=12, family="Helvetica"), 
            text_color="#A0A0A0"
        )
        self.file_info_label.pack(pady=(0, 20))
        
        # Results section
        self.results_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=("#2B2B2B", "#1A1A1A"))
        self.results_frame.pack(fill="both", expand=True)
        
        # Initial message
        self.show_initial_message()
        
    def show_initial_message(self):
        message_label = ctk.CTkLabel(
            self.results_frame,
            text="Upload CVs and search for matches to see results",
            font=ctk.CTkFont(size=16),
            text_color="#A0A0A0"
        )
        message_label.place(relx=0.5, rely=0.5, anchor="center")
        
    def upload_files(self):
        file_paths = filedialog.askopenfilenames(title="Select CV PDF Files", filetypes=[("PDF files", "*.pdf")])
        if file_paths:
            self.current_file_paths = list(file_paths)
            self.file_info_label.configure(text=f"Selected: {len(file_paths)} files")
            self.upload_btn.configure(text="Analyzing...", state="disabled", fg_color="#666666")
            
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
                
                # Get applicant data from database
                try:
                    applicant_data = self.query_service.get_applicant_by_cv_path(file_path)
                    if applicant_data:
                        self.applicant_data[file_path] = applicant_data
                    else:
                        # If no applicant found, use default values
                        self.applicant_data[file_path] = {
                            'first_name': 'Unknown',
                            'last_name': 'Unknown',
                            'date_of_birth': 'Unknown',
                            'address': 'Unknown',
                            'phone_number': 'Unknown',
                            'cv_path': file_path
                        }
                except Exception as e:
                    print(f"Error getting applicant data: {str(e)}")
                    # Use default values on error
                    self.applicant_data[file_path] = {
                        'first_name': 'Unknown',
                        'last_name': 'Unknown',
                        'date_of_birth': 'Unknown',
                        'address': 'Unknown',
                        'phone_number': 'Unknown',
                        'cv_path': file_path
                    }
                
                self.root.after(0, self.update_file_status, file_path, "✓")
        except Exception as e:
            print(f"Error in analyze_cvs: {str(e)}")
            self.root.after(0, self.show_error, str(e))
        finally:
            self.root.after(0, self.reset_upload_button)
    
    def update_file_status(self, file_path: str, status: str):
        """Update the status of a file in the list"""
        self.file_info_label.configure(text=f"Processed: {len(self.analysis_results)}/{len(self.current_file_paths)} files")
    
    def reset_upload_button(self):
        self.upload_btn.configure(text="Upload CVs (PDF)", state="normal", fg_color="#4A90E2")
    
    def show_error(self, error_message):
        messagebox.showerror("Analysis Error", f"An error occurred: {error_message}")
    
    def calculate_match_score(self, text: str, keywords: List[str]) -> Tuple[float, Dict[str, int], float, float]:
        """Calculate match score using selected pattern matching algorithm and fuzzy matching
        Returns: (total_score, keyword_matches, exact_time, fuzzy_time)"""
        text = text.lower()
        total_score = 0
        keyword_matches = {k.lower(): 0 for k in keywords}  # Track matches per keyword
        exact_matches = set()  # Track which keywords had exact matches
        
        # Get selected algorithm
        selected_algo = self.algorithm_var.get()
        print(f"Using algorithm: {selected_algo}")
        
        # Measure exact matching time
        exact_start_time = time.time()
        
        # First try exact matching
        for keyword in keywords:
            keyword = keyword.lower()
            # Use selected algorithm for pattern matching
            if selected_algo == "KMP":
                matches = kmp_search(text, keyword)
            else:  # Boyer-Moore
                matches = boyer_moore_search(text, keyword)
            
            if matches:  # If exact matches found
                exact_matches.add(keyword)
                keyword_matches[keyword] = len(matches)
                print(f"Found {len(matches)} matches for '{keyword}' using {selected_algo}")
                # Calculate score based on number of matches and context
                for match_pos in matches:
                    # Get context around the match
                    context_start = max(0, match_pos - 50)
                    context_end = min(len(text), match_pos + len(keyword) + 50)
                    context = text[context_start:context_end]
                    
                    # Calculate score based on context length
                    score = 1.0 / (1.0 + len(context))
                    total_score += score
        
        exact_time = time.time() - exact_start_time
        
        # Measure fuzzy matching time
        fuzzy_time = 0
        unmatched_keywords = [k for k in keywords if k not in exact_matches]
        if unmatched_keywords:
            print(f"Trying fuzzy matching for: {unmatched_keywords}")
            fuzzy_start_time = time.time()
            fuzzy_results = fuzzy_search_all(text, unmatched_keywords, threshold=0.8)
            for keyword, matches in fuzzy_results.items():
                keyword_matches[keyword] = len(matches)
                for match_pos, similarity in matches:
                    # Get context around the match
                    context_start = max(0, match_pos - 50)
                    context_end = min(len(text), match_pos + len(keyword) + 50)
                    context = text[context_start:context_end]
                    
                    # Calculate score based on context length and similarity
                    # Use similarity score directly from fuzzy search
                    score = (similarity * 0.5) / (1.0 + len(context))  # Reduce weight of fuzzy matches
                    total_score += score
            fuzzy_time = time.time() - fuzzy_start_time
        
        return total_score, keyword_matches, exact_time, fuzzy_time

    def search_keywords(self):
        if not self.current_file_paths:
            messagebox.showwarning("Warning", "Please upload and analyze CVs first.")
            return
            
        keywords_input = self.search_entry.get().strip()
        if not keywords_input:
            messagebox.showwarning("Warning", "Please enter keywords to search.")
            return
            
        try:
            num_matches = int(self.matches_entry.get())
            if num_matches <= 0:
                raise ValueError("Number of matches must be positive")
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid number of matches.")
            return
            
        keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
        
        # Calculate match scores for each file
        file_scores = []
        total_exact_time = 0
        total_fuzzy_time = 0
        
        for file_path in self.current_file_paths:
            if file_path in self.analysis_results:
                results = self.analysis_results[file_path]
                if 'text' in results:
                    score, keyword_matches, exact_time, fuzzy_time = self.calculate_match_score(results['text'], keywords)
                    total_exact_time += exact_time
                    total_fuzzy_time += fuzzy_time
                    if score > 0:
                        file_scores.append((file_path, score, keyword_matches))
        
        # Sort by score and take top matches
        file_scores.sort(key=lambda x: x[1], reverse=True)
        top_matches = file_scores[:num_matches]
        
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if top_matches:
            # Create scrollable frame for cards
            cards_frame = ctk.CTkScrollableFrame(self.results_frame, fg_color="transparent")
            cards_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Add timing information
            timing_frame = ctk.CTkFrame(cards_frame, fg_color="transparent")
            timing_frame.pack(fill="x", pady=(0, 10))
            
            # Exact matching time
            exact_time_label = ctk.CTkLabel(
                timing_frame,
                text=f"Exact Matching Time ({self.algorithm_var.get()}): {total_exact_time:.3f} seconds",
                font=ctk.CTkFont(size=12, family="Helvetica"),
                text_color="#4A90E2"
            )
            exact_time_label.pack(side="left", padx=(0, 20))
            
            # Fuzzy matching time
            if total_fuzzy_time > 0:
                fuzzy_time_label = ctk.CTkLabel(
                    timing_frame,
                    text=f"Fuzzy Matching Time: {total_fuzzy_time:.3f} seconds",
                    font=ctk.CTkFont(size=12, family="Helvetica"),
                    text_color="#4A90E2"
                )
                fuzzy_time_label.pack(side="left")
            
            # Create cards for each match
            for file_path, score, keyword_matches in top_matches:
                card = self.create_match_card(cards_frame, file_path, score, keyword_matches)
                card.pack(fill="x", pady=10)
        else:
            # Show no matches message
            message_label = ctk.CTkLabel(
                self.results_frame,
                text="No matches found",
                font=ctk.CTkFont(size=16),
                text_color="#A0A0A0"
            )
            message_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def create_match_card(self, parent, file_path: str, score: float, keyword_matches: Dict[str, int]) -> ctk.CTkFrame:
        """Create a card for displaying a match"""
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=("#2B2B2B", "#1A1A1A"))
        
        # Get applicant data
        applicant_data = self.applicant_data.get(file_path, {})
        name = f"{applicant_data.get('first_name', 'Unknown')} {applicant_data.get('last_name', 'Unknown')}"
        
        # Card content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Name and score
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        name_label = ctk.CTkLabel(
            header_frame,
            text=name,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        name_label.pack(side="left")
        
        # Score and matches info
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(side="right")
        
        score_label = ctk.CTkLabel(
            info_frame,
            text=f"Match Score: {score:.2f}",
            font=ctk.CTkFont(size=14),
            text_color="#4A90E2"
        )
        score_label.pack(side="top", pady=(0, 5))
        
        # Total matches
        total_matches = sum(keyword_matches.values())
        matches_label = ctk.CTkLabel(
            info_frame,
            text=f"Total Matches: {total_matches}",
            font=ctk.CTkFont(size=14),
            text_color="#4A90E2"
        )
        matches_label.pack(side="top", pady=(0, 5))
        
        # Detailed matches per keyword
        matches_detail = ctk.CTkFrame(content_frame, fg_color="transparent")
        matches_detail.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            matches_detail,
            text="Matches per keyword:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#A0A0A0"
        ).pack(anchor="w", pady=(0, 5))
        
        for keyword, count in keyword_matches.items():
            if count > 0:  # Only show keywords that have matches
                match_row = ctk.CTkFrame(matches_detail, fg_color="transparent")
                match_row.pack(fill="x", pady=2)
                
                ctk.CTkLabel(
                    match_row,
                    text=f"• {keyword.capitalize()}:",
                    font=ctk.CTkFont(size=12),
                    text_color="#A0A0A0"
                ).pack(side="left")
                
                ctk.CTkLabel(
                    match_row,
                    text=f"{count} matches",
                    font=ctk.CTkFont(size=12),
                    text_color="#4A90E2"
                ).pack(side="left", padx=(5, 0))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        view_summary_btn = ctk.CTkButton(
            buttons_frame,
            text="View Summary",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=35,
            width=120,
            fg_color="#4A90E2",
            hover_color="#357ABD",
            command=lambda: self.show_summary(file_path)
        )
        view_summary_btn.pack(side="left", padx=(0, 10))
        
        view_cv_btn = ctk.CTkButton(
            buttons_frame,
            text="View CV",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=35,
            width=120,
            fg_color="#2B2B2B",
            hover_color="#1A1A1A",
            command=lambda: self.open_cv(file_path)
        )
        view_cv_btn.pack(side="left")
        
        return card
    
    def show_summary(self, file_path: str):
        """Show summary window for a CV"""
        if file_path in self.analysis_results and file_path in self.applicant_data:
            SummaryWindow(
                self.root,
                self.analysis_results[file_path],
                self.applicant_data[file_path],
                file_path
            )
    
    def open_cv(self, file_path: str):
        """Open CV file"""
        try:
            if os.path.exists(file_path):
                if os.name == 'nt':  # Windows
                    os.startfile(file_path)
                else:  # Linux/Mac
                    subprocess.run(['xdg-open', file_path])
            else:
                messagebox.showerror("Error", "CV file not found")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open CV: {str(e)}")

    def update_algorithm_label(self, value):
        """Update the algorithm description label"""
        if value == "KMP":
            self.algorithm_label.configure(text="(Knuth-Morris-Pratt)")
        else:
            self.algorithm_label.configure(text="(Boyer-Moore)")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CVAnalyzerApp()
    app.run()