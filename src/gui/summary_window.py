import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import os
import subprocess
from typing import Dict

class SummaryWindow:
    def __init__(self, parent, cv_data: Dict, applicant_data: Dict, file_path: str):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("CV Summary")
        self.window.geometry("1200x800")
        self.window.minsize(1000, 600)
        
        self.cv_data = cv_data
        self.applicant_data = applicant_data
        self.file_path = file_path
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.window, corner_radius=0, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header with applicant info
        header_frame = ctk.CTkFrame(main_frame, height=150, corner_radius=20, fg_color=("#2B2B2B", "#1A1A1A"))
        header_frame.pack(fill="x", pady=(0, 25))
        header_frame.pack_propagate(False)
        
        # Applicant info
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Name
        name_label = ctk.CTkLabel(
            info_frame, 
            text=f"{self.applicant_data['first_name']} {self.applicant_data['last_name']}", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        name_label.pack(anchor="w", pady=(0, 10))
        
        # Other details in a grid
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.pack(fill="x")
        
        # Date of Birth
        dob_label = ctk.CTkLabel(
            details_frame,
            text=f"Date of Birth: {self.applicant_data['date_of_birth']}",
            font=ctk.CTkFont(size=14)
        )
        dob_label.grid(row=0, column=0, padx=(0, 20), pady=5, sticky="w")
        
        # Phone
        phone_label = ctk.CTkLabel(
            details_frame,
            text=f"Phone: {self.applicant_data['phone_number']}",
            font=ctk.CTkFont(size=14)
        )
        phone_label.grid(row=0, column=1, padx=(0, 20), pady=5, sticky="w")
        
        # Address
        address_label = ctk.CTkLabel(
            details_frame,
            text=f"Address: {self.applicant_data['address']}",
            font=ctk.CTkFont(size=14)
        )
        address_label.grid(row=1, column=0, columnspan=2, pady=5, sticky="w")
        
        # View CV button
        view_cv_btn = ctk.CTkButton(
            header_frame,
            text="View CV",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=120,
            fg_color="#4A90E2",
            hover_color="#357ABD",
            command=self.open_cv
        )
        view_cv_btn.place(relx=0.95, rely=0.5, anchor="e")
        
        # Content sections
        content_frame = ctk.CTkFrame(main_frame, corner_radius=20, fg_color=("#2B2B2B", "#1A1A1A"))
        content_frame.pack(fill="both", expand=True)
        
        # Create columns for different sections
        columns = [
            ("Summary", "summary"),
            ("Skills", "skills"),
            ("Experience", "experience"),
            ("Education", "education")
        ]
        
        self.info_textboxes = {}
        for title, key in columns:
            column_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            column_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            ctk.CTkLabel(
                column_frame, 
                text=title, 
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=(0, 10))
            
            textbox = ctk.CTkTextbox(
                column_frame, 
                wrap="word", 
                font=ctk.CTkFont(size=12, family="Helvetica")
            )
            textbox.pack(fill="both", expand=True)
            self.info_textboxes[key] = textbox
            
        self.display_results()
        
    def display_results(self):
        for key in self.info_textboxes:
            self.info_textboxes[key].configure(state="normal")
            self.info_textboxes[key].delete("1.0", "end")
            self.info_textboxes[key].insert("1.0", self.cv_data.get(key, 'N/A'))
            self.info_textboxes[key].configure(state="disabled")
            
    def open_cv(self):
        """Open CV file"""
        try:
            if os.path.exists(self.file_path):
                if os.name == 'nt':  # Windows
                    os.startfile(self.file_path)
                else:  # Linux/Mac
                    subprocess.run(['xdg-open', self.file_path])
            else:
                messagebox.showerror("Error", "CV file not found")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open CV: {str(e)}") 