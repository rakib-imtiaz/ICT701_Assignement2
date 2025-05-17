"""
Smart Fitness Management System (SFMS) - Main Application
ICT701 Assignment 4

This module contains the main application controller and core frame classes.
Handles the application navigation and user authentication flow.

Author: Emon
Student ID: 20031890
Date: October 2023
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging

from data_manager import DataManager
from models import User
from gui.frames import ProfileFrame, WorkoutFrame, GoalFrame, NutritionFrame, ReportFrame

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class SFMSApplication:
    """
    Main GUI application controller for the Smart Fitness Management System.
    Manages navigation between screens and user authentication.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Fitness Management System")
        self.root.geometry("1200x700")
        # Change background color to a nicer shade
        self.root.configure(bg="#f5f7fa")
        self.center_window()
        
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Add application icon if available
        try:
            self.root.iconbitmap("fitness_icon.ico")
        except:
            logging.debug("Icon file not found, continuing without it")
            
        # Set custom fonts
        self.title_font = ("Helvetica", 16, "bold")
        self.header_font = ("Helvetica", 14, "bold")
        self.normal_font = ("Helvetica", 10)
        self.small_font = ("Helvetica", 9)
        
        self.data_manager = DataManager()
        self.current_user = None
        
        self.show_login_frame()
        
    def center_window(self):
        """Center the application window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def show_login_frame(self):
        """Display the login screen"""
        # Clear existing frames
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create frame in the root window, but pass self (the application) as the controller
        self.login_frame = LoginFrame(self.root, self)
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
    def show_register_frame(self):
        """Display the registration screen"""
        # Clear existing frames
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create frame in the root window, but pass self (the application) as the controller
        self.register_frame = RegisterFrame(self.root, self)
        self.register_frame.pack(fill=tk.BOTH, expand=True)
        
    def show_main_app(self):
        """Display the main application screen after successful login"""
        # Clear existing frames
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create main app components
        self.main_frame = MainAppFrame(self.root, self.current_user, self.logout_callback)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
    def login_callback(self, username, password):
        """Handle login authentication"""
        user = self.data_manager.authenticate_user(username, password)
        if user:
            self.current_user = user
            logging.info(f"User {username} logged in successfully")
            self.show_main_app()
            return True
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            logging.warning(f"Failed login attempt for username: {username}")
            return False
            
    def register_callback(self, user_data):
        """Handle new user registration"""
        if self.data_manager.get_user(user_data["username"]):
            messagebox.showerror("Registration Failed", "Username already exists")
            return False
            
        # Create new user
        new_user = User(
            user_data["username"],
            user_data["password"],
            user_data["name"],
            user_data["age"],
            user_data["gender"],
            user_data["height"],
            user_data["weight"]
        )
        
        if self.data_manager.add_user(new_user):
            messagebox.showinfo("Registration Successful", "Your account has been created successfully")
            self.current_user = new_user
            self.show_main_app()
            return True
        else:
            messagebox.showerror("Registration Failed", "Failed to create account")
            return False
            
    def logout_callback(self):
        """Handle user logout"""
        self.current_user = None
        logging.info("User logged out")
        self.show_login_frame()


class LoginFrame(tk.Frame):
    """Login screen UI component"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f7fa")
        self.parent = parent
        self.controller = controller  # Store the application controller
        
        container = tk.Frame(self, bg="#ffffff", padx=50, pady=50, 
                           highlightbackground="#dddddd", highlightthickness=1)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        logo_label = tk.Label(container, text="SFMS", font=("Arial", 36, "bold"), 
                            fg="#4CAF50", bg="#ffffff")
        logo_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))
        
        title_label = tk.Label(container, text="Smart Fitness Management System", 
                             font=("Arial", 16), fg="#2196F3", bg="#ffffff")
        title_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        subtitle_label = tk.Label(container, text="Login to your account", 
                                font=("Arial", 12), bg="#ffffff")
        subtitle_label.grid(row=2, column=0, columnspan=2, pady=(0, 30))
        
        username_frame = tk.Frame(container, bg="#ffffff")
        username_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 15))
        
        username_icon = tk.Label(username_frame, text="👤", font=("Arial", 12), bg="#ffffff")
        username_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        username_label = tk.Label(username_frame, text="Username:", font=("Arial", 10), bg="#ffffff")
        username_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.username_entry = tk.Entry(username_frame, width=25, font=("Arial", 10), 
                                     relief=tk.SOLID, bd=1)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        password_frame = tk.Frame(container, bg="#ffffff")
        password_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 25))
        
        password_icon = tk.Label(password_frame, text="🔒", font=("Arial", 12), bg="#ffffff")
        password_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        password_label = tk.Label(password_frame, text="Password:", font=("Arial", 10), bg="#ffffff")
        password_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.password_entry = tk.Entry(password_frame, width=25, show="*", font=("Arial", 10), 
                                     relief=tk.SOLID, bd=1)
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        login_button = tk.Button(container, text="Login", command=self.login, 
                              width=15, height=2, bg="#4CAF50", fg="white", 
                              font=("Arial", 11, "bold"), bd=0, cursor="hand2")
        login_button.grid(row=5, column=0, columnspan=2, pady=(0, 20))
        
        register_frame = tk.Frame(container, bg="#ffffff")
        register_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        register_label = tk.Label(register_frame, text="Don't have an account?", 
                                font=("Arial", 10), bg="#ffffff")
        register_label.pack(side=tk.LEFT)
        
        register_link = tk.Label(register_frame, text="Sign Up", font=("Arial", 10, "bold"), 
                              fg="#2196F3", cursor="hand2", bg="#ffffff")
        register_link.pack(side=tk.LEFT, padx=(5, 0))
        register_link.bind("<Button-1>", self.show_register)
        
        # Add Enter key binding for login
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda event: self.login())
        
        # Set initial focus
        self.username_entry.focus_set()
        
    def login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Login Failed", "Please enter both username and password")
            return
            
        # Use the controller to call login_callback
        self.controller.login_callback(username, password)
        
    def show_register(self, event=None):
        """Navigate to registration screen"""
        # Use the controller to navigate to register frame
        self.controller.show_register_frame()


class RegisterFrame(tk.Frame):
    """Registration screen UI component"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f5f7fa")
        self.parent = parent
        self.controller = controller  # Store the application controller
        
        container_frame = tk.Frame(self, bg="#ffffff", padx=40, pady=30,
                                highlightbackground="#dddddd", highlightthickness=1)
        container_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        title_label = tk.Label(container_frame, text="Smart Fitness Management System", 
                             font=("Arial", 18, "bold"), fg="#2196F3", bg="#ffffff")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        subtitle_label = tk.Label(container_frame, text="Create a new account", 
                               font=("Arial", 14), fg="#2c3e50",bg="#ffffff")
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        username_label = tk.Label(container_frame, text="Username:", font=("Arial", 10), bg="#ffffff")
        username_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 12))
        
        self.username_entry = tk.Entry(container_frame, width=30, font=("Arial", 10))
        self.username_entry.grid(row=2, column=1, pady=(0, 12), padx=(10, 0))
        
        password_label = tk.Label(container_frame, text="Password:", font=("Arial", 10), bg="#ffffff")
        password_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 12))
        
        self.password_entry = tk.Entry(container_frame, width=30, show="*", font=("Arial", 10))
        self.password_entry.grid(row=3, column=1, pady=(0, 12), padx=(10, 0))
        
        confirm_password_label = tk.Label(container_frame, text="Confirm Password:", 
                                      font=("Arial", 10), bg="#ffffff")
        confirm_password_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 12))
        
        self.confirm_password_entry = tk.Entry(container_frame, width=30, show="*", font=("Arial", 10))
        self.confirm_password_entry.grid(row=4, column=1, pady=(0, 12), padx=(10, 0))
        
        name_label = tk.Label(container_frame, text="Full Name:", font=("Arial", 10), bg="#ffffff")
        name_label.grid(row=5, column=0, sticky=tk.W, pady=(0, 12))
        
        self.name_entry = tk.Entry(container_frame, width=30, font=("Arial", 10))
        self.name_entry.grid(row=5, column=1, pady=(0, 12), padx=(10, 0))
        
        age_label = tk.Label(container_frame, text="Age:", font=("Arial", 10), bg="#ffffff")
        age_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 12))
        
        self.age_entry = tk.Entry(container_frame, width=30, font=("Arial", 10))
        self.age_entry.grid(row=6, column=1, pady=(0, 12), padx=(10, 0))
        
        gender_label = tk.Label(container_frame, text="Gender:", font=("Arial", 10), bg="#ffffff")
        gender_label.grid(row=7, column=0, sticky=tk.W, pady=(0, 12))
        
        self.gender_var = tk.StringVar(value="Male")
        gender_frame = tk.Frame(container_frame, bg="#ffffff")
        gender_frame.grid(row=7, column=1, sticky=tk.W, pady=(0, 12), padx=(10, 0))
        
        tk.Radiobutton(gender_frame, text="Male", variable=self.gender_var, value="Male", 
                     bg="#ffffff").pack(side=tk.LEFT)
        tk.Radiobutton(gender_frame, text="Female", variable=self.gender_var, value="Female", 
                     bg="#ffffff").pack(side=tk.LEFT, padx=(10, 0))
        tk.Radiobutton(gender_frame, text="Other", variable=self.gender_var, value="Other", 
                     bg="#ffffff").pack(side=tk.LEFT, padx=(10, 0))
        
        height_label = tk.Label(container_frame, text="Height (cm):", font=("Arial", 10), bg="#ffffff")
        height_label.grid(row=8, column=0, sticky=tk.W, pady=(0, 12))
        
        self.height_entry = tk.Entry(container_frame, width=30, font=("Arial", 10))
        self.height_entry.grid(row=8, column=1, pady=(0, 12), padx=(10, 0))
        
        weight_label = tk.Label(container_frame, text="Weight (kg):", font=("Arial", 10), bg="#ffffff")
        weight_label.grid(row=9, column=0, sticky=tk.W, pady=(0, 20))
        
        self.weight_entry = tk.Entry(container_frame, width=30, font=("Arial", 10))
        self.weight_entry.grid(row=9, column=1, pady=(0, 20), padx=(10, 0))
        
        register_button = tk.Button(container_frame, text="Register", command=self.register, 
                                 width=15, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                                 relief=tk.RAISED, bd=1)
        register_button.grid(row=10, column=0, columnspan=2, pady=(5, 20))
        
        login_frame = tk.Frame(container_frame, bg="#ffffff")
        login_frame.grid(row=11, column=0, columnspan=2, pady=(0, 10))
        
        login_label = tk.Label(login_frame, text="Already have an account?", 
                            font=("Arial", 10), bg="#ffffff")
        login_label.pack(side=tk.LEFT)
        
        login_link = tk.Label(login_frame, text="Log In", font=("Arial", 10, "bold"), 
                          fg="#2196F3", cursor="hand2", bg="#ffffff")
        login_link.pack(side=tk.LEFT, padx=(5, 0))
        login_link.bind("<Button-1>", self.show_login)
    
    def register(self):
        """Handle registration button click"""
        # Get form data
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        name = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()
        gender = self.gender_var.get()
        height_str = self.height_entry.get().strip()
        weight_str = self.weight_entry.get().strip()
        
        # Validate form data
        if not (username and password and confirm_password and name and age_str and height_str and weight_str):
            messagebox.showerror("Registration Failed", "All fields are required")
            return
            
        if password != confirm_password:
            messagebox.showerror("Registration Failed", "Passwords do not match")
            return
            
        try:
            age = int(age_str)
            if age <= 0 or age > 120:
                messagebox.showerror("Registration Failed", "Please enter a valid age (1-120)")
                return
        except ValueError:
            messagebox.showerror("Registration Failed", "Age must be a number")
            return
            
        try:
            height = float(height_str)
            if height <= 0 or height > 300:
                messagebox.showerror("Registration Failed", "Please enter a valid height (1-300 cm)")
                return
        except ValueError:
            messagebox.showerror("Registration Failed", "Height must be a number")
            return
            
        try:
            weight = float(weight_str)
            if weight <= 0 or weight > 500:
                messagebox.showerror("Registration Failed", "Please enter a valid weight (1-500 kg)")
                return
        except ValueError:
            messagebox.showerror("Registration Failed", "Weight must be a number")
            return
            
        # Prepare user data
        user_data = {
            "username": username,
            "password": password,
            "name": name,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight
        }
        
        # Call register callback
        self.controller.register_callback(user_data)
        
    def show_login(self, event=None):
        """Navigate back to login screen"""
        # Use the controller to navigate back to login frame
        self.controller.show_login_frame()


class MainAppFrame(tk.Frame):
    """Main application UI container with sidebar navigation"""
    def __init__(self, parent, user, logout_callback):
        super().__init__(parent, bg="#f5f7fa")
        self.parent = parent
        self.user = user
        self.logout_callback = logout_callback
        self.data_manager = DataManager()
        self.create_layout()
        
    def create_layout(self):
        """Create the main application layout with sidebar and content area"""
        self.main_container = tk.Frame(self, bg="#f5f7fa")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self.sidebar = tk.Frame(self.main_container, bg="#2c3e50", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        self.content_area = tk.Frame(self.main_container, bg="#ffffff", bd=0)  # Changed to white background
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)  # Added padding
        
        self.create_sidebar()
        self.show_profile()
        
    def create_sidebar(self):
        """Create the sidebar navigation menu"""
        # App title
        title_label = tk.Label(self.sidebar, text="SFMS", font=("Arial", 24, "bold"), 
                             bg="#2c3e50", fg="white", pady=25)
        title_label.pack(fill=tk.X)
        
        # User info with better styling
        user_frame = tk.Frame(self.sidebar, bg="#2c3e50", pady=15)
        user_frame.pack(fill=tk.X)
        
        user_icon = tk.Label(user_frame, text="👤", font=("Arial", 32), bg="#2c3e50", fg="white")
        user_icon.pack()
        
        user_name = tk.Label(user_frame, text=self.user.name, font=("Arial", 12, "bold"), 
                           bg="#2c3e50", fg="white")
        user_name.pack(pady=(5, 10))
        
        # Add separator
        sep = tk.Frame(self.sidebar, height=1, bg="#3d566e")
        sep.pack(fill=tk.X, padx=15, pady=5)
        
        # Menu items with improved styling
        menu_items = [
            ("👤 Profile", self.show_profile),
            ("🏋️‍♂️ Workouts", self.show_workouts),
            ("🎯 Goals", self.show_goals),
            ("🍎 Nutrition", self.show_nutrition),
            ("📊 Reports", self.show_reports),
            ("🚪 Logout", self.logout_callback)
        ]
        
        # Menu container
        menu_container = tk.Frame(self.sidebar, bg="#2c3e50")
        menu_container.pack(fill=tk.X, pady=20)
        
        for text, command in menu_items:
            btn = tk.Button(menu_container, text=text, font=("Arial", 11), 
                          bg="#2c3e50", fg="white", bd=0, pady=12,
                          activebackground="#34495e", activeforeground="white", 
                          highlightthickness=0, width=20, anchor=tk.W, padx=25,
                          command=command, cursor="hand2")
            btn.pack(fill=tk.X)
        
    def clear_content(self):
        """Clear all widgets from the content area"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
    def show_profile(self):
        """Display the profile screen"""
        self.clear_content()
        ProfileFrame(self.content_area, self.user, self.data_manager).pack(fill=tk.BOTH, expand=True)
        
    def show_workouts(self):
        """Display the workouts screen"""
        self.clear_content()
        WorkoutFrame(self.content_area, self.user, self.data_manager).pack(fill=tk.BOTH, expand=True)
        
    def show_goals(self):
        """Display the goals screen"""
        self.clear_content()
        GoalFrame(self.content_area, self.user, self.data_manager).pack(fill=tk.BOTH, expand=True)
        
    def show_nutrition(self):
        """Display the nutrition screen"""
        self.clear_content()
        NutritionFrame(self.content_area, self.user, self.data_manager).pack(fill=tk.BOTH, expand=True)
        
    def show_reports(self):
        """Display the reports screen"""
        self.clear_content()
        ReportFrame(self.content_area, self.user, self.data_manager).pack(fill=tk.BOTH, expand=True) 