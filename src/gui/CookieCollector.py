import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict
import json
import os
from .controller import BrowserController

class CookieCollectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cookie Collector")
        self.root.geometry("600x600")  # Made window taller to accommodate all elements
        
        # Initialize controller
        self.controller = BrowserController()
        
        # Configure style
        style = ttk.Style()
        style.configure("TButton", padding=5)
        style.configure("TLabel", padding=5)
        style.configure("TFrame", padding=5)
        
        # Main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Browser selection
        self.create_browser_section()
        
        # Mode selection
        self.create_mode_section()
        
        # URL input section
        self.create_url_section()
        
        # Settings section
        self.create_settings_section()
        
        # Progress section
        self.create_progress_section()
        
        # Action buttons - now at the bottom
        self.create_action_buttons()
        
        # Load saved settings if they exist
        self.load_settings()

    def create_browser_section(self):
        browser_frame = ttk.LabelFrame(self.main_frame, text="Browser Selection")
        browser_frame.pack(fill='x', padx=5, pady=5)
        
        self.browser_var = tk.StringVar(value="chrome")
        ttk.Radiobutton(browser_frame, text="Chrome", variable=self.browser_var, value="chrome").pack(side='left', padx=5)
        ttk.Radiobutton(browser_frame, text="Firefox", variable=self.browser_var, value="firefox").pack(side='left', padx=5)
        ttk.Radiobutton(browser_frame, text="Edge", variable=self.browser_var, value="edge").pack(side='left', padx=5)

    def create_mode_section(self):
        mode_frame = ttk.LabelFrame(self.main_frame, text="Collection Mode")
        mode_frame.pack(fill='x', padx=5, pady=5)
        
        self.mode_var = tk.StringVar(value="single")
        ttk.Radiobutton(mode_frame, text="Single Site", variable=self.mode_var, 
                       value="single", command=self.update_url_section).pack(side='left', padx=5)
        ttk.Radiobutton(mode_frame, text="Multiple Sites", variable=self.mode_var, 
                       value="multiple", command=self.update_url_section).pack(side='left', padx=5)

    def create_url_section(self):
        self.url_frame = ttk.LabelFrame(self.main_frame, text="URL Input")
        self.url_frame.pack(fill='x', padx=5, pady=5)
        
        # Single URL input
        self.single_url_frame = ttk.Frame(self.url_frame)
        self.single_url_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(self.single_url_frame, text="URL:").pack(side='left', padx=5)
        self.url_entry = ttk.Entry(self.single_url_frame)
        self.url_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Multiple URLs input
        self.multiple_url_frame = ttk.Frame(self.url_frame)
        self.urls_text = tk.Text(self.multiple_url_frame, height=5)
        self.urls_text.pack(fill='both', expand=True, padx=5, pady=5)
        ttk.Label(self.multiple_url_frame, text="Enter one URL per line").pack(side='bottom', pady=2)

    def create_settings_section(self):
        settings_frame = ttk.LabelFrame(self.main_frame, text="Settings")
        settings_frame.pack(fill='x', padx=5, pady=5)
        
        # Wait time setting
        wait_frame = ttk.Frame(settings_frame)
        wait_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(wait_frame, text="Page Load Wait Time (seconds):").pack(side='left', padx=5)
        self.wait_time_var = tk.StringVar(value="3")
        wait_spinbox = ttk.Spinbox(wait_frame, from_=1, to=10, textvariable=self.wait_time_var, width=5)
        wait_spinbox.pack(side='left', padx=5)
        
        # Save cookies checkbox
        self.save_cookies_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Save cookies to database", 
                       variable=self.save_cookies_var).pack(anchor='w', padx=5, pady=2)
        
        # Headless mode checkbox - now default to True
        self.headless_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Run in headless mode (no visible browser)", 
                       variable=self.headless_var).pack(anchor='w', padx=5, pady=2)

    def create_progress_section(self):
        """Create the progress tracking section"""
        progress_frame = ttk.LabelFrame(self.main_frame, text="Progress")
        progress_frame.pack(fill='x', padx=5, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill='x', padx=5, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            progress_frame,
            textvariable=self.status_var
        )
        status_label.pack(fill='x', padx=5)

    def create_action_buttons(self):
        """Create action buttons at the bottom of the window"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill='x', padx=5, pady=10, side='bottom')
        
        # Left-side buttons
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side='left', fill='x', expand=True)
        
        ttk.Button(left_frame, text="Start Collection", command=self.start_collection).pack(side='left', padx=5)
        ttk.Button(left_frame, text="View Database", command=self.show_database_viewer).pack(side='left', padx=5)
        ttk.Button(left_frame, text="Save Settings", command=self.save_settings).pack(side='left', padx=5)
        
        # Right-side button
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side='right')
        
        ttk.Button(right_frame, text="Exit", command=self.root.quit).pack(side='right', padx=5)

    def update_url_section(self):
        if self.mode_var.get() == "single":
            self.multiple_url_frame.pack_forget()
            self.single_url_frame.pack(fill='x', padx=5, pady=5)
        else:
            self.single_url_frame.pack_forget()
            self.multiple_url_frame.pack(fill='both', expand=True, padx=5, pady=5)

    def get_urls(self) -> List[str]:
        if self.mode_var.get() == "single":
            url = self.url_entry.get().strip()
            return [url] if url else []
        else:
            urls = self.urls_text.get("1.0", tk.END).strip().split('\n')
            return [url.strip() for url in urls if url.strip()]

    def get_settings(self) -> Dict:
        return {
            "browser": self.browser_var.get(),
            "mode": self.mode_var.get(),
            "wait_time": int(self.wait_time_var.get()),
            "save_cookies": self.save_cookies_var.get(),
            "headless": self.headless_var.get(),
            "urls": self.get_urls()
        }

    def save_settings(self):
        settings = self.get_settings()
        try:
            with open("data/settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def load_settings(self):
        try:
            if os.path.exists("data/settings.json"):
                with open("data/settings.json", "r") as f:
                    settings = json.load(f)
                
                self.browser_var.set(settings.get("browser", "chrome"))
                self.mode_var.set(settings.get("mode", "single"))
                self.wait_time_var.set(str(settings.get("wait_time", 3)))
                self.save_cookies_var.set(settings.get("save_cookies", True))
                self.headless_var.set(settings.get("headless", True))
                
                urls = settings.get("urls", [])
                if urls and self.mode_var.get() == "single":
                    self.url_entry.insert(0, urls[0])
                elif urls:
                    self.urls_text.insert("1.0", "\n".join(urls))
                
                self.update_url_section()
        except Exception as e:
            messagebox.showwarning("Warning", f"Failed to load settings: {str(e)}")

    def update_progress(self, current_progress: float, total: int, message: str):
        """Update the progress bar and status message"""
        # Update progress bar (current_progress is already 0-100)
        self.progress_var.set(current_progress)
        self.status_var.set(message)
        self.root.update_idletasks()

    def start_collection(self):
        """Start the cookie collection process"""
        settings = self.get_settings()
        urls = settings["urls"]
        
        if not urls:
            messagebox.showerror("Error", "Please enter at least one URL")
            return
        
        # Initialize browser
        success, message = self.controller.initialize_browser(settings)
        if not success:
            messagebox.showerror("Error", message)
            return
        
        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting collection...")
        
        # Start collection
        success, results = self.controller.collect_cookies(
            urls,
            callback=self.update_progress
        )
        
        if success:
            # Show results
            total_cookies = sum(r["count"] for r in results.values())
            successful = sum(1 for r in results.values() if r["success"])
            
            message = f"Collection completed!\n\n" \
                     f"Sites processed: {len(urls)}\n" \
                     f"Successful: {successful}\n" \
                     f"Failed: {len(urls) - successful}\n" \
                     f"Total cookies collected: {total_cookies}"
            
            messagebox.showinfo("Collection Complete", message)
            
            # Show detailed results
            self.show_detailed_results(results)
        else:
            messagebox.showerror("Error", results)
        
        self.status_var.set("Ready")
        self.progress_var.set(0)

    def show_detailed_results(self, results: Dict):
        """Show detailed results in a new window"""
        results_window = tk.Toplevel(self.root)
        results_window.title("Collection Results")
        results_window.geometry("800x600")  # Increased window size
        
        # Create text widget with monospace font for better formatting
        text_widget = tk.Text(results_window, wrap=tk.WORD, font=('Courier', 10))
        text_widget.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(results_window, orient='vertical', command=text_widget.yview)
        scrollbar.pack(side='right', fill='y')
        text_widget['yscrollcommand'] = scrollbar.set
        
        # Insert results
        for url, result in results.items():
            text_widget.insert('end', f"\nURL: {url}\n")
            text_widget.insert('end', f"Status: {'Success' if result['success'] else 'Failed'}\n")
            
            if result['success']:
                text_widget.insert('end', f"Cookies collected: {result['count']}\n")
                if result['count'] > 0:
                    text_widget.insert('end', "Cookies:\n")
                    for cookie in result['cookies']:
                        text_widget.insert('end', "-" * 50 + "\n")
                        for key, value in cookie.items():
                            text_widget.insert('end', f"  {key}: {value}\n")
            else:
                text_widget.insert('end', f"Error: {result['error']}\n")
            
            text_widget.insert('end', "\n" + "="*50 + "\n")
        
        # Add copy button
        copy_button = ttk.Button(
            results_window, 
            text="Copy Results", 
            command=lambda: self.copy_to_clipboard(text_widget.get("1.0", tk.END))
        )
        copy_button.pack(pady=5)
        
        text_widget.configure(state='disabled')  # Make read-only
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Success", "Results copied to clipboard!")

    def show_database_viewer(self):
        """Show the database viewer window"""
        viewer_window = tk.Toplevel(self.root)
        viewer_window.title("Database Viewer")
        viewer_window.geometry("800x600")

        # Create main frame
        main_frame = ttk.Frame(viewer_window)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Create website listbox
        website_frame = ttk.LabelFrame(main_frame, text="Websites")
        website_frame.pack(side='left', fill='y', padx=5)
        
        self.website_listbox = tk.Listbox(website_frame, width=40)
        self.website_listbox.pack(expand=True, fill='both', padx=5, pady=5)
        website_scrollbar = ttk.Scrollbar(website_frame, orient='vertical', command=self.website_listbox.yview)
        website_scrollbar.pack(side='right', fill='y')
        self.website_listbox.config(yscrollcommand=website_scrollbar.set)
        
        # Create cookie display
        cookie_frame = ttk.LabelFrame(main_frame, text="Cookies")
        cookie_frame.pack(side='right', expand=True, fill='both', padx=5)
        
        self.cookie_text = tk.Text(cookie_frame, wrap=tk.WORD, font=('Courier', 10))
        self.cookie_text.pack(expand=True, fill='both', padx=5, pady=5)
        cookie_scrollbar = ttk.Scrollbar(cookie_frame, orient='vertical', command=self.cookie_text.yview)
        cookie_scrollbar.pack(side='right', fill='y')
        self.cookie_text.config(yscrollcommand=cookie_scrollbar.set)
        
        # Create buttons frame
        button_frame = ttk.Frame(viewer_window)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_database_view).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected_website).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Export Selected", command=self.export_selected_cookies).pack(side='left', padx=5)
        
        # Bind selection event
        self.website_listbox.bind('<<ListboxSelect>>', self.on_website_select)
        
        # Initial load
        self.refresh_database_view()

    def refresh_database_view(self):
        """Refresh the database viewer"""
        try:
            # Clear current items
            self.website_listbox.delete(0, tk.END)
            self.cookie_text.delete('1.0', tk.END)
            
            # Get websites from database
            websites = self.controller.db_manager.get_all_websites()
            
            # Add to listbox
            for website in websites:
                self.website_listbox.insert(tk.END, website.url)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load database: {str(e)}")

    def on_website_select(self, event):
        """Handle website selection"""
        try:
            selection = self.website_listbox.curselection()
            if selection:
                url = self.website_listbox.get(selection[0])
                cookies = self.controller.db_manager.get_cookies(url)
                
                self.cookie_text.delete('1.0', tk.END)
                if cookies:
                    for cookie in cookies:
                        self.cookie_text.insert(tk.END, "-" * 50 + "\n")
                        for key, value in cookie.items():
                            self.cookie_text.insert(tk.END, f"{key}: {value}\n")
                else:
                    self.cookie_text.insert(tk.END, "No cookies found for this website.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load cookies: {str(e)}")

    def delete_selected_website(self):
        """Delete the selected website and its cookies"""
        try:
            selection = self.website_listbox.curselection()
            if selection:
                url = self.website_listbox.get(selection[0])
                if messagebox.askyesno("Confirm Delete", f"Delete all cookies for {url}?"):
                    self.controller.db_manager.remove_website(url)
                    self.refresh_database_view()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete website: {str(e)}")

    def export_selected_cookies(self):
        """Export selected website's cookies to a file"""
        try:
            selection = self.website_listbox.curselection()
            if selection:
                url = self.website_listbox.get(selection[0])
                cookies = self.controller.db_manager.get_cookies(url)
                
                if cookies:
                    import json
                    from datetime import datetime
                    
                    filename = f"cookies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w') as f:
                        json.dump(cookies, f, indent=4)
                    messagebox.showinfo("Success", f"Cookies exported to {filename}")
                else:
                    messagebox.showwarning("Warning", "No cookies to export.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export cookies: {str(e)}")

def main():
    root = tk.Tk()
    app = CookieCollectorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 