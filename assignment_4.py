import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
from tkcalendar import Calendar
import re
import hashlib

class User:
    def __init__(self, username, password, name, age, gender, height, weight, goals=None):
        self.username = username
        self.password = password  # In production, this should be hashed
        self.name = name
        self.age = age
        self.gender = gender
        self.height = height
        self.weight = weight
        self.goals = goals or []
        self.workouts = []
        self.meals = []
        
    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'goals': self.goals,
            'workouts': self.workouts,
            'meals': self.meals
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls(
            data['username'],
            data['password'],
            data['name'],
            data['age'],
            data['gender'],
            data['height'],
            data['weight'],
            data.get('goals', [])
        )
        user.workouts = data.get('workouts', [])
        user.meals = data.get('meals', [])
        return user

class Workout:
    def __init__(self, workout_type, duration, calories_burned, date, notes=""):
        self.workout_type = workout_type
        self.duration = duration  # in minutes
        self.calories_burned = calories_burned
        self.date = date
        self.notes = notes
        
    def to_dict(self):
        return {
            'workout_type': self.workout_type,
            'duration': self.duration,
            'calories_burned': self.calories_burned,
            'date': self.date,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data['workout_type'],
            data['duration'],
            data['calories_burned'],
            data['date'],
            data.get('notes', "")
        )

class Meal:
    def __init__(self, meal_type, name, calories, proteins, carbs, fats, date):
        self.meal_type = meal_type  # breakfast, lunch, dinner, snack
        self.name = name
        self.calories = calories
        self.proteins = proteins  # in grams
        self.carbs = carbs  # in grams
        self.fats = fats  # in grams
        self.date = date
        
    def to_dict(self):
        return {
            'meal_type': self.meal_type,
            'name': self.name,
            'calories': self.calories,
            'proteins': self.proteins,
            'carbs': self.carbs,
            'fats': self.fats,
            'date': self.date
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            data['meal_type'],
            data['name'],
            data['calories'],
            data['proteins'],
            data['carbs'],
            data['fats'],
            data['date']
        )

class Goal:
    def __init__(self, goal_type, target_value, deadline, start_date=None):
        self.goal_type = goal_type  # e.g., 'weight_loss', 'distance_run', etc.
        self.target_value = target_value
        self.deadline = deadline
        self.start_date = start_date or datetime.datetime.now().strftime("%Y-%m-%d")
        self.completed = False
        
    def to_dict(self):
        return {
            'goal_type': self.goal_type,
            'target_value': self.target_value,
            'deadline': self.deadline,
            'start_date': self.start_date,
            'completed': self.completed
        }
    
    @classmethod
    def from_dict(cls, data):
        goal = cls(
            data['goal_type'],
            data['target_value'],
            data['deadline'],
            data.get('start_date')
        )
        goal.completed = data.get('completed', False)
        return goal

class DataManager:
    def __init__(self, data_file="fitness_data.json"):
        self.data_file = data_file
        self.users = {}
        self.load_data()
        
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for username, user_data in data.items():
                        # Convert workouts, meals, and goals from dict to objects
                        user_data['workouts'] = [Workout.from_dict(w) for w in user_data.get('workouts', [])]
                        user_data['meals'] = [Meal.from_dict(m) for m in user_data.get('meals', [])]
                        user_data['goals'] = [Goal.from_dict(g) for g in user_data.get('goals', [])]
                        self.users[username] = User.from_dict(user_data)
            except (json.JSONDecodeError, FileNotFoundError):
                self.users = {}
                
    def save_data(self):
        # Convert objects to dictionaries before saving to JSON
        data = {}
        for username, user in self.users.items():
            user_dict = user.to_dict()
            user_dict['workouts'] = [w.to_dict() for w in user.workouts]
            user_dict['meals'] = [m.to_dict() for m in user.meals]
            user_dict['goals'] = [g.to_dict() for g in user.goals]
            data[username] = user_dict
            
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
            
    def add_user(self, user):
        if user.username in self.users:
            return False  # User already exists
        self.users[user.username] = user
        self.save_data()
        return True
        
    def update_user(self, user):
        if user.username not in self.users:
            return False  # User doesn't exist
        self.users[user.username] = user
        self.save_data()
        return True
        
    def delete_user(self, username):
        if username not in self.users:
            return False  # User doesn't exist
        del self.users[username]
        self.save_data()
        return True
    
    def get_user(self, username):
        return self.users.get(username)
    
    def authenticate_user(self, username, password):
        user = self.get_user(username)
        if user and user.password == password:  # In production, use proper password verification
            return user
        return None

class FitnessModeSelector(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Fitness Management System - Mode Selection")
        self.geometry("400x200")
        self.configure(bg="#f0f0f0")
        self.center_window()
        
        label = tk.Label(self, text="Select Interface Mode", font=("Arial", 16, "bold"), bg="#f0f0f0")
        label.pack(pady=20)
        
        gui_button = tk.Button(self, text="GUI Mode", command=self.launch_gui, 
                            width=15, height=2, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        gui_button.pack(pady=5)
        
        text_button = tk.Button(self, text="Text Mode", command=self.launch_text, 
                             width=15, height=2, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        text_button.pack(pady=5)
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def launch_gui(self):
        self.destroy()
        app = SFMSApplication()
        app.mainloop()
        
    def launch_text(self):
        self.destroy()
        # Launch text-based interface
        TextInterface().run()

class TextInterface:
    def __init__(self):
        self.data_manager = DataManager()
        self.current_user = None
        
    def run(self):
        print("\n===== Smart Fitness Management System - Text Mode =====")
        while True:
            if not self.current_user:
                self.show_login_menu()
            else:
                self.show_main_menu()
                
    def show_login_menu(self):
        print("\n----- Login Menu -----")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            self.login()
        elif choice == "2":
            self.register()
        elif choice == "3":
            print("Thank you for using SFMS. Goodbye!")
            exit()
        else:
            print("Invalid choice. Please try again.")
    
    def login(self):
        username = input("Username: ")
        password = input("Password: ")
        
        user = self.data_manager.authenticate_user(username, password)
        if user:
            self.current_user = user
            print(f"Welcome back, {user.name}!")
        else:
            print("Invalid username or password.")
    
    def register(self):
        # Implementation for text-based registration
        username = input("Username: ")
        if self.data_manager.get_user(username):
            print("Username already exists.")
            return
            
        password = input("Password: ")
        name = input("Full Name: ")
        
        while True:
            try:
                age = int(input("Age: "))
                break
            except ValueError:
                print("Please enter a valid number for age.")
        
        gender = input("Gender (M/F/Other): ")
        
        while True:
            try:
                height = float(input("Height (cm): "))
                break
            except ValueError:
                print("Please enter a valid number for height.")
        
        while True:
            try:
                weight = float(input("Weight (kg): "))
                break
            except ValueError:
                print("Please enter a valid number for weight.")
        
        user = User(username, password, name, age, gender, height, weight)
        if self.data_manager.add_user(user):
            print("Registration successful!")
            self.current_user = user
        else:
            print("Registration failed.")
            
    def show_main_menu(self):
        print(f"\n----- Main Menu ({self.current_user.name}) -----")
        print("1. View/Update Profile")
        print("2. Workout Management")
        print("3. Goal Tracking")
        print("4. Nutrition Tracking")
        print("5. Reports and Analytics")
        print("6. Logout")
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == "1":
            self.profile_management()
        elif choice == "2":
            self.workout_management()
        elif choice == "3":
            self.goal_management()
        elif choice == "4":
            self.nutrition_management()
        elif choice == "5":
            self.reports_management()
        elif choice == "6":
            self.current_user = None
            print("Logged out successfully.")
        else:
            print("Invalid choice. Please try again.")
            
    # Other text-based interface methods would go here
    # (profile_management, workout_management, etc.)
    
    def profile_management(self):
        # Basic implementation for demo purposes
        print(f"\n----- Profile Management -----")
        print(f"Username: {self.current_user.username}")
        print(f"Name: {self.current_user.name}")
        print(f"Age: {self.current_user.age}")
        print(f"Gender: {self.current_user.gender}")
        print(f"Height: {self.current_user.height} cm")
        print(f"Weight: {self.current_user.weight} kg")
        
        # Additional functionality would be implemented here

class SFMSApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Fitness Management System")
        self.geometry("1200x700")
        self.configure(bg="#f0f0f0")
        self.center_window()
        
        self.data_manager = DataManager()
        self.current_user = None
        
        # Set application icon
        try:
            self.iconbitmap("fitness_icon.ico")
        except:
            pass  # Icon not found, continue without it
        
        self.show_login_frame()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def show_login_frame(self):
        # Clear existing frames
        for widget in self.winfo_children():
            widget.destroy()
            
        self.login_frame = LoginFrame(self, self.login_callback)
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
    def show_register_frame(self):
        # Clear existing frames
        for widget in self.winfo_children():
            widget.destroy()
            
        self.register_frame = RegisterFrame(self, self.register_callback)
        self.register_frame.pack(fill=tk.BOTH, expand=True)
        
    def show_main_app(self):
        # Clear existing frames
        for widget in self.winfo_children():
            widget.destroy()
            
        # Create main app components
        self.main_frame = MainAppFrame(self, self.current_user, self.logout_callback)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
    def login_callback(self, username, password):
        user = self.data_manager.authenticate_user(username, password)
        if user:
            self.current_user = user
            self.show_main_app()
            return True
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
            return False
            
    def register_callback(self, user_data):
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
        self.current_user = None
        self.show_login_frame()

class LoginFrame(tk.Frame):
    def __init__(self, parent, login_callback):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.login_callback = login_callback
        
        # Create a container frame
        container = tk.Frame(self, bg="#ffffff", padx=40, pady=40)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        title_label = tk.Label(container, text="Smart Fitness Management System", 
                              font=("Arial", 18, "bold"), bg="#ffffff")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Subtitle
        subtitle_label = tk.Label(container, text="Login to your account", 
                                font=("Arial", 12), bg="#ffffff")
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Username
        username_label = tk.Label(container, text="Username:", font=("Arial", 10), bg="#ffffff")
        username_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        self.username_entry = tk.Entry(container, width=30, font=("Arial", 10))
        self.username_entry.grid(row=2, column=1, pady=(0, 10), padx=(10, 0))
        
        # Password
        password_label = tk.Label(container, text="Password:", font=("Arial", 10), bg="#ffffff")
        password_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 20))
        
        self.password_entry = tk.Entry(container, width=30, show="*", font=("Arial", 10))
        self.password_entry.grid(row=3, column=1, pady=(0, 20), padx=(10, 0))
        
        # Login button
        login_button = tk.Button(container, text="Login", command=self.login, 
                               width=10, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        login_button.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # Register link
        register_frame = tk.Frame(container, bg="#ffffff")
        register_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        register_label = tk.Label(register_frame, text="Don't have an account?", 
                                 font=("Arial", 10), bg="#ffffff")
        register_label.pack(side=tk.LEFT)
        
        register_link = tk.Label(register_frame, text="Sign Up", font=("Arial", 10, "bold"), 
                               fg="#2196F3", cursor="hand2", bg="#ffffff")
        register_link.pack(side=tk.LEFT, padx=(5, 0))
        register_link.bind("<Button-1>", self.show_register)
        
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Login Failed", "Please enter both username and password")
            return
            
        self.login_callback(username, password)
        
    def show_register(self, event=None):
        self.parent.show_register_frame()
        
class RegisterFrame(tk.Frame):
    def __init__(self, parent, register_callback):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.register_callback = register_callback
        
        # Create scrollable frame
        self.canvas = tk.Canvas(self, bg="#f0f0f0", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#ffffff", padx=40, pady=40)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Title
        title_label = tk.Label(self.scrollable_frame, text="Smart Fitness Management System", 
                              font=("Arial", 18, "bold"), bg="#ffffff")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Subtitle
        subtitle_label = tk.Label(self.scrollable_frame, text="Create a new account", 
                                font=("Arial", 12), bg="#ffffff")
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Username
        username_label = tk.Label(self.scrollable_frame, text="Username:", font=("Arial", 10), bg="#ffffff")
        username_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        self.username_entry = tk.Entry(self.scrollable_frame, width=30, font=("Arial", 10))
        self.username_entry.grid(row=2, column=1, pady=(0, 10), padx=(10, 0))
        
        # Password
        password_label = tk.Label(self.scrollable_frame, text="Password:", font=("Arial", 10), bg="#ffffff")
        password_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        self.password_entry = tk.Entry(self.scrollable_frame, width=30, show="*", font=("Arial", 10))
        self.password_entry.grid(row=3, column=1, pady=(0, 10), padx=(10, 0))
        
        # Confirm Password
        confirm_password_label = tk.Label(self.scrollable_frame, text="Confirm Password:", 
                                       font=("Arial", 10), bg="#ffffff")
        confirm_password_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 10))
        
        self.confirm_password_entry = tk.Entry(self.scrollable_frame, width=30, show="*", font=("Arial", 10))
        self.confirm_password_entry.grid(row=4, column=1, pady=(0, 10), padx=(10, 0))
        
        # Full Name
        name_label = tk.Label(self.scrollable_frame, text="Full Name:", font=("Arial", 10), bg="#ffffff")
        name_label.grid(row=5, column=0, sticky=tk.W, pady=(0, 10))
        
        self.name_entry = tk.Entry(self.scrollable_frame, width=30, font=("Arial", 10))
        self.name_entry.grid(row=5, column=1, pady=(0, 10), padx=(10, 0))
        
        # Age
        age_label = tk.Label(self.scrollable_frame, text="Age:", font=("Arial", 10), bg="#ffffff")
        age_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 10))
        
        self.age_entry = tk.Entry(self.scrollable_frame, width=30, font=("Arial", 10))
        self.age_entry.grid(row=6, column=1, pady=(0, 10), padx=(10, 0))
        
        # Gender
        gender_label = tk.Label(self.scrollable_frame, text="Gender:", font=("Arial", 10), bg="#ffffff")
        gender_label.grid(row=7, column=0, sticky=tk.W, pady=(0, 10))
        
        self.gender_var = tk.StringVar(value="Male")
        gender_frame = tk.Frame(self.scrollable_frame, bg="#ffffff")
        gender_frame.grid(row=7, column=1, sticky=tk.W, pady=(0, 10), padx=(10, 0))
        
        tk.Radiobutton(gender_frame, text="Male", variable=self.gender_var, value="Male", 
                      bg="#ffffff").pack(side=tk.LEFT)
        tk.Radiobutton(gender_frame, text="Female", variable=self.gender_var, value="Female", 
                      bg="#ffffff").pack(side=tk.LEFT, padx=(10, 0))
        tk.Radiobutton(gender_frame, text="Other", variable=self.gender_var, value="Other", 
                      bg="#ffffff").pack(side=tk.LEFT, padx=(10, 0))
        
        # Height
        height_label = tk.Label(self.scrollable_frame, text="Height (cm):", font=("Arial", 10), bg="#ffffff")
        height_label.grid(row=8, column=0, sticky=tk.W, pady=(0, 10))
        
        self.height_entry = tk.Entry(self.scrollable_frame, width=30, font=("Arial", 10))
        self.height_entry.grid(row=8, column=1, pady=(0, 10), padx=(10, 0))
        
        # Weight
        weight_label = tk.Label(self.scrollable_frame, text="Weight (kg):", font=("Arial", 10), bg="#ffffff")
        weight_label.grid(row=9, column=0, sticky=tk.W, pady=(0, 20))
        
        self.weight_entry = tk.Entry(self.scrollable_frame, width=30, font=("Arial", 10))
        self.weight_entry.grid(row=9, column=1, pady=(0, 20), padx=(10, 0))
        
        # Register button
        register_button = tk.Button(self.scrollable_frame, text="Register", command=self.register, 
                                  width=10, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        register_button.grid(row=10, column=0, columnspan=2, pady=(0, 10))
        
        # Login link
        login_frame = tk.Frame(self.scrollable_frame, bg="#ffffff")
        login_frame.grid(row=11, column=0, columnspan=2, pady=(10, 0))
        
        login_label = tk.Label(login_frame, text="Already have an account?", 
                             font=("Arial", 10), bg="#ffffff")
        login_label.pack(side=tk.LEFT)
        
        login_link = tk.Label(login_frame, text="Log In", font=("Arial", 10, "bold"), 
                           fg="#2196F3", cursor="hand2", bg="#ffffff")
        login_link.pack(side=tk.LEFT, padx=(5, 0))
        login_link.bind("<Button-1>", self.show_login)
        
    def register(self):
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
        self.register_callback(user_data)
        
    def show_login(self, event=None):
        self.parent.show_login_frame()

class MainAppFrame(tk.Frame):
    def __init__(self, parent, user, logout_callback):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.user = user
        self.logout_callback = logout_callback
        self.data_manager = DataManager()
        
        # Create sidebar and content area
        self.create_layout()
        
    def create_layout(self):
        # Main container with two columns (sidebar and content)
        self.main_container = tk.Frame(self, bg="#f0f0f0")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar = tk.Frame(self.main_container, bg="#2c3e50", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)  # Prevent sidebar from shrinking
        
        # Content area
        self.content_area = tk.Frame(self.main_container, bg="#f0f0f0")
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Add sidebar items
        self.create_sidebar()
        
        # Default view is profile
        self.show_profile()
        
    def create_sidebar(self):
        # App title
        title_label = tk.Label(self.sidebar, text="SFMS", font=("Arial", 20, "bold"), 
                             bg="#2c3e50", fg="white", pady=20)
        title_label.pack(fill=tk.X)
        
        # User info
        user_frame = tk.Frame(self.sidebar, bg="#2c3e50", pady=10)
        user_frame.pack(fill=tk.X)
        
        user_icon = tk.Label(user_frame, text="👤", font=("Arial", 24), bg="#2c3e50", fg="white")
        user_icon.pack()
        
        user_name = tk.Label(user_frame, text=self.user.name, font=("Arial", 10, "bold"), 
                           bg="#2c3e50", fg="white")
        user_name.pack()
        
        # Menu items
        menu_items = [
            ("Profile", self.show_profile),
            ("Workouts", self.show_workouts),
            ("Goals", self.show_goals),
            ("Nutrition", self.show_nutrition),
            ("Reports", self.show_reports),
            ("Logout", self.logout_callback)
        ]
        
        # Menu container
        menu_container = tk.Frame(self.sidebar, bg="#2c3e50")
        menu_container.pack(fill=tk.X, pady=20)
        
        for text, command in menu_items:
            btn = tk.Button(menu_container, text=text, font=("Arial", 10), 
                          bg="#2c3e50", fg="white", bd=0, pady=10,
                          activebackground="#34495e", activeforeground="white", 
                          highlightthickness=0, width=20, anchor=tk.W, padx=20,
                          command=command)
            btn.pack(fill=tk.X)
            
    def clear_content(self):
        # Clear all widgets from content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
    def show_profile(self):
        self.clear_content()
        ProfileFrame(self.content_area, self.user, self.data_manager).pack(fill=tk.BOTH, expand=True)
        
    def show_workouts(self):
        self.clear_content()
        WorkoutFrame(self.content_area, self.user, self.data_manager).pack(fill=tk.BOTH, expand=True)
        
    def show_goals(self):
        self.clear_content()
        GoalFrame(self.content_area, self.user, self.data_manager).pack(fill=tk.BOTH, expand=True)
        
    def show_nutrition(self):
        self.clear_content()
        NutritionFrame(self.content_area, self.user, self.data_manager).pack(fill=tk.BOTH, expand=True)
        
    def show_reports(self):
        self.clear_content()
        ReportFrame(self.content_area, self.user, self.data_manager).pack(fill=tk.BOTH, expand=True)

class ProfileFrame(tk.Frame):
    def __init__(self, parent, user, data_manager):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        
        # Title
        title_frame = tk.Frame(self, bg="#f0f0f0", pady=20)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, text="Profile", font=("Arial", 18, "bold"), bg="#f0f0f0")
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Content in two columns
        content_frame = tk.Frame(self, bg="white", padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left column - User info
        info_frame = tk.Frame(content_frame, bg="white")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # User icon
        user_icon = tk.Label(info_frame, text="👤", font=("Arial", 48), bg="white")
        user_icon.pack(pady=(0, 20))
        
        # User details
        details = [
            ("Name:", self.user.name),
            ("Age:", str(self.user.age)),
            ("Gender:", self.user.gender),
            ("Height:", f"{self.user.height} cm"),
            ("Weight:", f"{self.user.weight} kg")
        ]
        
        for label_text, value in details:
            row = tk.Frame(info_frame, bg="white", pady=5)
            row.pack(fill=tk.X)
            
            label = tk.Label(row, text=label_text, font=("Arial", 10, "bold"), 
                           bg="white", width=15, anchor=tk.W)
            label.pack(side=tk.LEFT)
            
            value_label = tk.Label(row, text=value, font=("Arial", 10), bg="white", anchor=tk.W)
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
        # Edit button
        edit_button = tk.Button(info_frame, text="Edit Profile", command=self.edit_profile, 
                              bg="#2196F3", fg="white", font=("Arial", 10), pady=5)
        edit_button.pack(pady=20)
        
        # Right column - Stats
        stats_frame = tk.Frame(content_frame, bg="white")
        stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Stats title
        stats_title = tk.Label(stats_frame, text="Your Statistics", font=("Arial", 14, "bold"), bg="white")
        stats_title.pack(pady=(0, 20))
        
        # Basic stats
        self.create_stats_section(stats_frame)
        
    def create_stats_section(self, parent):
        # Calculate BMI
        bmi = self.user.weight / ((self.user.height / 100) ** 2)
        
        # Calculate total workouts
        total_workouts = len(self.user.workouts)
        
        # Calculate total calories burned
        total_calories = sum(workout.calories_burned for workout in self.user.workouts)
        
        # Stats to display
        stats = [
            ("BMI:", f"{bmi:.1f}", self.get_bmi_category(bmi)),
            ("Total Workouts:", str(total_workouts), ""),
            ("Calories Burned:", f"{total_calories} kcal", "")
        ]
        
        for label_text, value, note in stats:
            row = tk.Frame(parent, bg="white", pady=10)
            row.pack(fill=tk.X)
            
            label = tk.Label(row, text=label_text, font=("Arial", 10, "bold"), 
                           bg="white", width=15, anchor=tk.W)
            label.pack(side=tk.LEFT)
            
            value_label = tk.Label(row, text=value, font=("Arial", 10), bg="white", anchor=tk.W)
            value_label.pack(side=tk.LEFT)
            
            if note:
                note_label = tk.Label(row, text=f"({note})", font=("Arial", 8), 
                                    bg="white", fg="#666", anchor=tk.W)
                note_label.pack(side=tk.LEFT, padx=(5, 0))
                
        # Goals progress section
        if self.user.goals:
            goals_frame = tk.Frame(parent, bg="white", pady=20)
            goals_frame.pack(fill=tk.X)
            
            goals_title = tk.Label(goals_frame, text="Goals Progress", 
                                  font=("Arial", 12, "bold"), bg="white")
            goals_title.pack(anchor=tk.W)
            
            for goal in self.user.goals[:3]:  # Show up to 3 goals
                self.create_goal_progress_bar(goals_frame, goal)
                
    def create_goal_progress_bar(self, parent, goal):
        # For demonstration, calculate progress randomly
        # In a real app, this would be calculated based on user's actual progress
        import random
        progress = random.uniform(0.1, 1.0)
        
        row = tk.Frame(parent, bg="white", pady=5)
        row.pack(fill=tk.X)
        
        label = tk.Label(row, text=f"{goal.goal_type}:", font=("Arial", 9), 
                       bg="white", width=15, anchor=tk.W)
        label.pack(side=tk.LEFT)
        
        # Progress bar frame
        bar_frame = tk.Frame(row, bg="#e0e0e0", height=15, width=200)
        bar_frame.pack(side=tk.LEFT)
        bar_frame.pack_propagate(False)
        
        # Progress fill
        progress_width = int(200 * progress)
        progress_fill = tk.Frame(bar_frame, bg="#4CAF50", height=15, width=progress_width)
        progress_fill.pack(side=tk.LEFT, anchor=tk.W)
        
        # Percentage
        percentage = tk.Label(row, text=f"{int(progress * 100)}%", font=("Arial", 9), 
                            bg="white", padx=5)
        percentage.pack(side=tk.LEFT)
        
    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"
            
    def edit_profile(self):
        # Create a top-level window for editing
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Profile")
        edit_window.geometry("400x400")
        edit_window.configure(bg="white")
        
        # Make window modal
        edit_window.grab_set()
        
        # Title
        title_label = tk.Label(edit_window, text="Edit Profile", font=("Arial", 16, "bold"), bg="white")
        title_label.pack(pady=20)
        
        # Form container
        form_frame = tk.Frame(edit_window, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Form fields
        fields = [
            ("Name:", "name", self.user.name),
            ("Age:", "age", str(self.user.age)),
            ("Height (cm):", "height", str(self.user.height)),
            ("Weight (kg):", "weight", str(self.user.weight))
        ]
        
        entries = {}
        for i, (label_text, field_name, value) in enumerate(fields):
            label = tk.Label(form_frame, text=label_text, font=("Arial", 10), bg="white")
            label.grid(row=i, column=0, sticky=tk.W, pady=10)
            
            entry = tk.Entry(form_frame, font=("Arial", 10))
            entry.insert(0, value)
            entry.grid(row=i, column=1, sticky=tk.W+tk.E, padx=10, pady=10)
            
            entries[field_name] = entry
            
        # Gender
        gender_label = tk.Label(form_frame, text="Gender:", font=("Arial", 10), bg="white")
        gender_label.grid(row=len(fields), column=0, sticky=tk.W, pady=10)
        
        gender_var = tk.StringVar(value=self.user.gender)
        gender_frame = tk.Frame(form_frame, bg="white")
        gender_frame.grid(row=len(fields), column=1, sticky=tk.W, pady=10)
        
        genders = ["Male", "Female", "Other"]
        for i, g in enumerate(genders):
            rb = tk.Radiobutton(gender_frame, text=g, variable=gender_var, value=g, bg="white")
            rb.pack(side=tk.LEFT, padx=(0 if i == 0 else 10, 0))
            
        # Buttons
        button_frame = tk.Frame(edit_window, bg="white")
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        save_button = tk.Button(button_frame, text="Save", bg="#4CAF50", fg="white", 
                              command=lambda: self.save_profile(entries, gender_var, edit_window))
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", bg="#f44336", fg="white", 
                                command=edit_window.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def save_profile(self, entries, gender_var, window):
        try:
            name = entries["name"].get().strip()
            age = int(entries["age"].get())
            height = float(entries["height"].get())
            weight = float(entries["weight"].get())
            gender = gender_var.get()
            
            # Validation
            if not name:
                messagebox.showerror("Error", "Name cannot be empty", parent=window)
                return
                
            if age <= 0 or age > 120:
                messagebox.showerror("Error", "Age must be between 1 and 120", parent=window)
                return
                
            if height <= 0 or height > 300:
                messagebox.showerror("Error", "Height must be between 1 and 300 cm", parent=window)
                return
                
            if weight <= 0 or weight > 500:
                messagebox.showerror("Error", "Weight must be between 1 and 500 kg", parent=window)
                return
                
            # Update user data
            self.user.name = name
            self.user.age = age
            self.user.height = height
            self.user.weight = weight
            self.user.gender = gender
            
            # Save to database
            self.data_manager.update_user(self.user)
            
            # Refresh profile view
            self.parent.winfo_children()[0].destroy()
            ProfileFrame(self.parent, self.user, self.data_manager).pack(fill=tk.BOTH, expand=True)
            
            # Close window
            window.destroy()
            
            # Show success message
            messagebox.showinfo("Success", "Profile updated successfully")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for age, height and weight", parent=window)

class WorkoutFrame(tk.Frame):
    def __init__(self, parent, user, data_manager):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        self.custom_start_date = None
        self.custom_end_date = None
        
        # Title
        title_frame = tk.Frame(self, bg="#f0f0f0", pady=20)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, text="Workout Tracking", font=("Arial", 18, "bold"), bg="#f0f0f0")
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Add workout button
        add_button = tk.Button(title_frame, text="Log New Workout", command=self.add_workout, 
                             bg="#4CAF50", fg="white", font=("Arial", 10))
        add_button.pack(side=tk.RIGHT, padx=20)
        
        # Workout history frame
        self.history_frame = tk.Frame(self, bg="white")
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create filter options
        self.create_filter_options()
        
        # Create workout history table
        self.create_workout_table()
        
    def create_filter_options(self):
        filter_frame = tk.Frame(self.history_frame, bg="white", padx=20, pady=10)
        filter_frame.pack(fill=tk.X)
        
        # Title
        filter_label = tk.Label(filter_frame, text="Filter Workouts:", font=("Arial", 12, "bold"), bg="white")
        filter_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10), columnspan=6)
        
        # Date range
        date_label = tk.Label(filter_frame, text="Date Range:", font=("Arial", 10), bg="white")
        date_label.grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        
        self.date_var = tk.StringVar(value="All Time")
        date_options = ["All Time", "Today", "This Week", "This Month", "Custom"]
        date_dropdown = ttk.Combobox(filter_frame, textvariable=self.date_var, values=date_options, width=15)
        date_dropdown.grid(row=1, column=1, pady=5, padx=(0, 20))
        date_dropdown.bind("<<ComboboxSelected>>", self.on_date_filter_change)
        
        # Workout type
        type_label = tk.Label(filter_frame, text="Workout Type:", font=("Arial", 10), bg="white")
        type_label.grid(row=1, column=2, sticky=tk.W, pady=5, padx=(0, 10))
        
        self.type_var = tk.StringVar(value="All Types")
        # Get unique workout types from user's workouts
        workout_types = ["All Types"]
        if self.user.workouts:
            workout_types.extend(list(set(w.workout_type for w in self.user.workouts)))
        type_dropdown = ttk.Combobox(filter_frame, textvariable=self.type_var, values=workout_types, width=15)
        type_dropdown.grid(row=1, column=3, pady=5, padx=(0, 20))
        type_dropdown.bind("<<ComboboxSelected>>", self.filter_workouts)
        
        # Filter button
        filter_button = tk.Button(filter_frame, text="Apply Filters", command=self.filter_workouts, 
                                bg="#2196F3", fg="white", font=("Arial", 10))
        filter_button.grid(row=1, column=4, pady=5, padx=(0, 10))
        
        # Reset button
        reset_button = tk.Button(filter_frame, text="Reset", command=self.reset_filters, 
                               bg="#f44336", fg="white", font=("Arial", 10))
        reset_button.grid(row=1, column=5, pady=5)
        
    def create_workout_table(self):
        # Table container
        table_frame = tk.Frame(self.history_frame, bg="white", padx=20, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Table header
        header_frame = tk.Frame(table_frame, bg="#f5f5f5")
        header_frame.pack(fill=tk.X)
        
        headers = ["Date", "Workout Type", "Duration (min)", "Calories Burned", "Actions"]
        widths = [150, 200, 120, 120, 100]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            header_label = tk.Label(header_frame, text=header, font=("Arial", 10, "bold"), 
                                  bg="#f5f5f5", width=width//10, anchor=tk.W)
            header_label.grid(row=0, column=i, padx=10, pady=10, sticky=tk.W)
            
        # Table content - scrollable
        self.table_canvas = tk.Canvas(table_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table_canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.table_canvas, bg="white")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.table_canvas.configure(
                scrollregion=self.table_canvas.bbox("all")
            )
        )
        
        self.table_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.table_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.table_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate with workouts
        self.populate_workout_table()
        
    def populate_workout_table(self, filtered_workouts=None):
        # Clear existing rows
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Get workouts to display
        workouts = filtered_workouts if filtered_workouts is not None else self.user.workouts
        
        # Sort workouts by date (most recent first)
        workouts = sorted(workouts, key=lambda w: datetime.datetime.strptime(w.date, "%Y-%m-%d"), reverse=True)
        
        if not workouts:
            # Show empty message
            empty_label = tk.Label(self.scrollable_frame, text="No workouts found", 
                                 font=("Arial", 12), bg="white", fg="#666")
            empty_label.pack(pady=30)
            return
            
        # Create rows for each workout
        for i, workout in enumerate(workouts):
            row_bg = "#f9f9f9" if i % 2 == 0 else "white"
            row_frame = tk.Frame(self.scrollable_frame, bg=row_bg)
            row_frame.pack(fill=tk.X)
            
            # Date
            date_label = tk.Label(row_frame, text=workout.date, font=("Arial", 10), 
                                bg=row_bg, width=15, anchor=tk.W)
            date_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
            
            # Workout Type
            type_label = tk.Label(row_frame, text=workout.workout_type, font=("Arial", 10), 
                                bg=row_bg, width=20, anchor=tk.W)
            type_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
            
            # Duration
            duration_label = tk.Label(row_frame, text=str(workout.duration), font=("Arial", 10), 
                                    bg=row_bg, width=12, anchor=tk.W)
            duration_label.grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
            
            # Calories
            calories_label = tk.Label(row_frame, text=str(workout.calories_burned), font=("Arial", 10), 
                                    bg=row_bg, width=12, anchor=tk.W)
            calories_label.grid(row=0, column=3, padx=10, pady=10, sticky=tk.W)
            
            # Actions (View/Edit/Delete)
            actions_frame = tk.Frame(row_frame, bg=row_bg)
            actions_frame.grid(row=0, column=4, padx=10, pady=5, sticky=tk.W)
            
            # View button
            view_button = tk.Button(actions_frame, text="👁️", command=lambda w=workout: self.view_workout(w), 
                                  bg="#2196F3", fg="white", width=2, font=("Arial", 8))
            view_button.pack(side=tk.LEFT, padx=(0, 5))
            
            # Edit button
            edit_button = tk.Button(actions_frame, text="✏️", command=lambda w=workout: self.edit_workout(w), 
                                  bg="#FF9800", fg="white", width=2, font=("Arial", 8))
            edit_button.pack(side=tk.LEFT, padx=(0, 5))
            
            # Delete button
            delete_button = tk.Button(actions_frame, text="🗑️", command=lambda w=workout: self.delete_workout(w), 
                                    bg="#f44336", fg="white", width=2, font=("Arial", 8))
            delete_button.pack(side=tk.LEFT)
            
    def on_date_filter_change(self, event=None):
        if self.date_var.get() == "Custom":
            self.show_date_picker()
        else:
            self.filter_workouts()
            
    def show_date_picker(self):
        # Create a top-level window for date range selection
        date_window = tk.Toplevel(self)
        date_window.title("Select Date Range")
        date_window.geometry("400x400")
        date_window.configure(bg="white")
        
        # Make window modal
        date_window.grab_set()
        
        # Title
        title_label = tk.Label(date_window, text="Select Date Range", font=("Arial", 16, "bold"), bg="white")
        title_label.pack(pady=20)
        
        # Date container
        date_frame = tk.Frame(date_window, bg="white")
        date_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Start date
        start_label = tk.Label(date_frame, text="Start Date:", font=("Arial", 10, "bold"), bg="white")
        start_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Use simple date entry for simplicity (in a real app, use a date picker)
        start_frame = tk.Frame(date_frame, bg="white")
        start_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 20))
        
        # Year
        self.start_year_var = tk.StringVar(value=datetime.datetime.now().year)
        start_year_label = tk.Label(start_frame, text="Year:", font=("Arial", 10), bg="white")
        start_year_label.pack(side=tk.LEFT, padx=(0, 5))
        start_year_entry = tk.Entry(start_frame, textvariable=self.start_year_var, width=6)
        start_year_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Month
        self.start_month_var = tk.StringVar(value=datetime.datetime.now().month)
        start_month_label = tk.Label(start_frame, text="Month:", font=("Arial", 10), bg="white")
        start_month_label.pack(side=tk.LEFT, padx=(0, 5))
        start_month_entry = tk.Entry(start_frame, textvariable=self.start_month_var, width=4)
        start_month_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Day
        self.start_day_var = tk.StringVar(value=1)
        start_day_label = tk.Label(start_frame, text="Day:", font=("Arial", 10), bg="white")
        start_day_label.pack(side=tk.LEFT, padx=(0, 5))
        start_day_entry = tk.Entry(start_frame, textvariable=self.start_day_var, width=4)
        start_day_entry.pack(side=tk.LEFT)
        
        # End date
        end_label = tk.Label(date_frame, text="End Date:", font=("Arial", 10, "bold"), bg="white")
        end_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        end_frame = tk.Frame(date_frame, bg="white")
        end_frame.grid(row=3, column=0, sticky=tk.W)
        
        # Year
        self.end_year_var = tk.StringVar(value=datetime.datetime.now().year)
        end_year_label = tk.Label(end_frame, text="Year:", font=("Arial", 10), bg="white")
        end_year_label.pack(side=tk.LEFT, padx=(0, 5))
        end_year_entry = tk.Entry(end_frame, textvariable=self.end_year_var, width=6)
        end_year_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Month
        self.end_month_var = tk.StringVar(value=datetime.datetime.now().month)
        end_month_label = tk.Label(end_frame, text="Month:", font=("Arial", 10), bg="white")
        end_month_label.pack(side=tk.LEFT, padx=(0, 5))
        end_month_entry = tk.Entry(end_frame, textvariable=self.end_month_var, width=4)
        end_month_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Day
        self.end_day_var = tk.StringVar(value=datetime.datetime.now().day)
        end_day_label = tk.Label(end_frame, text="Day:", font=("Arial", 10), bg="white")
        end_day_label.pack(side=tk.LEFT, padx=(0, 5))
        end_day_entry = tk.Entry(end_frame, textvariable=self.end_day_var, width=4)
        end_day_entry.pack(side=tk.LEFT)
        
        # Buttons
        button_frame = tk.Frame(date_window, bg="white")
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        apply_button = tk.Button(button_frame, text="Apply", 
                               command=lambda: self.apply_date_filter(date_window), 
                               bg="#4CAF50", fg="white", font=("Arial", 10))
        apply_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", 
                                command=lambda: self.cancel_date_filter(date_window), 
                                bg="#f44336", fg="white", font=("Arial", 10))
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def apply_date_filter(self, window):
        try:
            start_year = int(self.start_year_var.get())
            start_month = int(self.start_month_var.get())
            start_day = int(self.start_day_var.get())
            
            end_year = int(self.end_year_var.get())
            end_month = int(self.end_month_var.get())
            end_day = int(self.end_day_var.get())
            
            # Validate dates
            start_date = datetime.datetime(start_year, start_month, start_day)
            end_date = datetime.datetime(end_year, end_month, end_day)
            
            if start_date > end_date:
                messagebox.showerror("Error", "Start date cannot be after end date", parent=window)
                return
                
            # Set custom date range and close window
            self.custom_start_date = start_date.strftime("%Y-%m-%d")
            self.custom_end_date = end_date.strftime("%Y-%m-%d")
            window.destroy()
            
            # Apply filter
            self.filter_workouts()
            
        except (ValueError, TypeError) as e:
            messagebox.showerror("Error", "Please enter valid dates", parent=window)
            
    def cancel_date_filter(self, window):
        self.date_var.set("All Time")
        window.destroy()
        self.filter_workouts()
        
    def filter_workouts(self, event=None):
        date_filter = self.date_var.get()
        type_filter = self.type_var.get()
        
        # Get today's date
        today = datetime.datetime.now().date()
        
        # Filter by date
        filtered_by_date = []
        for workout in self.user.workouts:
            workout_date = datetime.datetime.strptime(workout.date, "%Y-%m-%d").date()
            
            if date_filter == "All Time":
                filtered_by_date.append(workout)
            elif date_filter == "Today":
                if workout_date == today:
                    filtered_by_date.append(workout)
            elif date_filter == "This Week":
                # Calculate start of week (Monday)
                start_of_week = today - datetime.timedelta(days=today.weekday())
                if workout_date >= start_of_week:
                    filtered_by_date.append(workout)
            elif date_filter == "This Month":
                if workout_date.month == today.month and workout_date.year == today.year:
                    filtered_by_date.append(workout)
            elif date_filter == "Custom":
                # Custom date range
                start_date = datetime.datetime.strptime(self.custom_start_date, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(self.custom_end_date, "%Y-%m-%d").date()
                
                if start_date <= workout_date <= end_date:
                    filtered_by_date.append(workout)
        
        # Filter by type
        filtered_workouts = []
        for workout in filtered_by_date:
            if type_filter == "All Types" or workout.workout_type == type_filter:
                filtered_workouts.append(workout)
                
        # Update table
        self.populate_workout_table(filtered_workouts)
        
    def reset_filters(self):
        self.date_var.set("All Time")
        self.type_var.set("All Types")
        self.filter_workouts()
        
    def add_workout(self):
        self.workout_form(None)
        
    def edit_workout(self, workout):
        self.workout_form(workout)
        
    def view_workout(self, workout):
        # Create a top-level window to view workout details
        view_window = tk.Toplevel(self)
        view_window.title("Workout Details")
        view_window.geometry("400x300")
        view_window.configure(bg="white")
        
        # Make window modal
        view_window.grab_set()
        
        # Title
        title_label = tk.Label(view_window, text="Workout Details", font=("Arial", 16, "bold"), bg="white")
        title_label.pack(pady=20)
        
        # Details container
        details_frame = tk.Frame(view_window, bg="white")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Workout details
        details = [
            ("Date:", workout.date),
            ("Workout Type:", workout.workout_type),
            ("Duration:", f"{workout.duration} minutes"),
            ("Calories Burned:", f"{workout.calories_burned} kcal")
        ]
        
        for i, (label_text, value) in enumerate(details):
            label = tk.Label(details_frame, text=label_text, font=("Arial", 10, "bold"), 
                           bg="white", anchor=tk.W)
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            
            value_label = tk.Label(details_frame, text=value, font=("Arial", 10), 
                                 bg="white", anchor=tk.W)
            value_label.grid(row=i, column=1, sticky=tk.W, pady=5, padx=10)
            
        # Notes
        notes_label = tk.Label(details_frame, text="Notes:", font=("Arial", 10, "bold"), 
                             bg="white", anchor=tk.W)
        notes_label.grid(row=len(details), column=0, sticky=tk.W, pady=5)
        
        notes_text = tk.Text(details_frame, height=4, width=30, font=("Arial", 10), wrap=tk.WORD)
        notes_text.insert(tk.END, workout.notes)
        notes_text.configure(state="disabled")  # Make read-only
        notes_text.grid(row=len(details), column=1, sticky=tk.W, pady=5, padx=10)
        
        # Close button
        close_button = tk.Button(view_window, text="Close", command=view_window.destroy, 
                               bg="#2196F3", fg="white", font=("Arial", 10))
        close_button.pack(pady=10)
        
    def delete_workout(self, workout):
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this workout?"):
            # Remove workout from user's list
            self.user.workouts.remove(workout)
            
            # Save to database
            self.data_manager.update_user(self.user)
            
            # Refresh workout table
            self.filter_workouts()
            
            # Show success message
            messagebox.showinfo("Success", "Workout deleted successfully")
            
    def workout_form(self, workout=None):
        # Create a top-level window for adding/editing workout
        is_edit = workout is not None
        form_window = tk.Toplevel(self)
        form_window.title("Edit Workout" if is_edit else "Log New Workout")
        form_window.geometry("400x450")
        form_window.configure(bg="white")
        
        # Make window modal
        form_window.grab_set()
        
        # Title
        title_label = tk.Label(form_window, text="Edit Workout" if is_edit else "Log New Workout", 
                             font=("Arial", 16, "bold"), bg="white")
        title_label.pack(pady=20)
        
        # Form container
        form_frame = tk.Frame(form_window, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Date
        date_label = tk.Label(form_frame, text="Date:", font=("Arial", 10, "bold"), bg="white")
        date_label.grid(row=0, column=0, sticky=tk.W, pady=10)
        
        date_var = tk.StringVar(value=workout.date if is_edit else datetime.datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(form_frame, textvariable=date_var, font=("Arial", 10), width=20)
        date_entry.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        date_format_label = tk.Label(form_frame, text="(YYYY-MM-DD)", font=("Arial", 8), fg="#666", bg="white")
        date_format_label.grid(row=0, column=2, sticky=tk.W, pady=10, padx=5)
        
        # Workout Type
        type_label = tk.Label(form_frame, text="Workout Type:", font=("Arial", 10, "bold"), bg="white")
        type_label.grid(row=1, column=0, sticky=tk.W, pady=10)
        
        # Common workout types
        workout_types = ["Running", "Walking", "Cycling", "Swimming", "Weight Training", 
                        "Yoga", "HIIT", "Cardio", "Other"]
        
        type_var = tk.StringVar(value=workout.workout_type if is_edit else "")
        type_dropdown = ttk.Combobox(form_frame, textvariable=type_var, values=workout_types, width=18)
        type_dropdown.grid(row=1, column=1, sticky=tk.W, pady=10)
        
        # Duration
        duration_label = tk.Label(form_frame, text="Duration (min):", font=("Arial", 10, "bold"), bg="white")
        duration_label.grid(row=2, column=0, sticky=tk.W, pady=10)
        
        duration_var = tk.StringVar(value=workout.duration if is_edit else "")
        duration_entry = tk.Entry(form_frame, textvariable=duration_var, font=("Arial", 10), width=20)
        duration_entry.grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # Calories Burned
        calories_label = tk.Label(form_frame, text="Calories Burned:", font=("Arial", 10, "bold"), bg="white")
        calories_label.grid(row=3, column=0, sticky=tk.W, pady=10)
        
        calories_var = tk.StringVar(value=workout.calories_burned if is_edit else "")
        calories_entry = tk.Entry(form_frame, textvariable=calories_var, font=("Arial", 10), width=20)
        calories_entry.grid(row=3, column=1, sticky=tk.W, pady=10)
        
        # Notes
        notes_label = tk.Label(form_frame, text="Notes:", font=("Arial", 10, "bold"), bg="white")
        notes_label.grid(row=4, column=0, sticky=tk.W, pady=10)
        
        notes_text = tk.Text(form_frame, height=5, width=30, font=("Arial", 10))
        if is_edit and workout.notes:
            notes_text.insert(tk.END, workout.notes)
        notes_text.grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=10)
        
        # Buttons
        button_frame = tk.Frame(form_window, bg="white")
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        save_button = tk.Button(button_frame, text="Save", 
                              command=lambda: self.save_workout(
                                  date_var.get(),
                                  type_var.get(),
                                  duration_var.get(),
                                  calories_var.get(),
                                  notes_text.get("1.0", tk.END).strip(),
                                  form_window,
                                  workout if is_edit else None
                              ), 
                              bg="#4CAF50", fg="white", font=("Arial", 10))
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=form_window.destroy, 
                                bg="#f44336", fg="white", font=("Arial", 10))
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def save_workout(self, date, workout_type, duration, calories, notes, window, existing_workout=None):
        # Validate inputs
        if not date or not workout_type or not duration or not calories:
            messagebox.showerror("Error", "All fields except notes are required", parent=window)
            return
            
        try:
            duration = int(duration)
            if duration <= 0:
                messagebox.showerror("Error", "Duration must be a positive number", parent=window)
                return
        except ValueError:
            messagebox.showerror("Error", "Duration must be a number", parent=window)
            return
            
        try:
            calories = int(calories)
            if calories < 0:
                messagebox.showerror("Error", "Calories must be a non-negative number", parent=window)
                return
        except ValueError:
            messagebox.showerror("Error", "Calories must be a number", parent=window)
            return
            
        try:
            # Validate date format
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format", parent=window)
            return
            
        if existing_workout:
            # Update existing workout
            existing_workout.date = date
            existing_workout.workout_type = workout_type
            existing_workout.duration = duration
            existing_workout.calories_burned = calories
            existing_workout.notes = notes
        else:
            # Create new workout
            new_workout = Workout(workout_type, duration, calories, date, notes)
            self.user.workouts.append(new_workout)
            
        # Save to database
        self.data_manager.update_user(self.user)
        
        # Close form
        window.destroy()
        
        # Refresh workout table
        self.filter_workouts()
        
        # Show success message
        messagebox.showinfo("Success", 
                          "Workout updated successfully" if existing_workout else "Workout logged successfully")

# Goal tracking and nutrition interfaces to be continued in next sections

class GoalFrame(tk.Frame):
    def __init__(self, parent, user, data_manager):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        
        # Title
        title_frame = tk.Frame(self, bg="#f0f0f0", pady=20)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, text="Goal Tracking", font=("Arial", 18, "bold"), bg="#f0f0f0")
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Add goal button
        add_button = tk.Button(title_frame, text="Set New Goal", command=self.add_goal, 
                             bg="#4CAF50", fg="white", font=("Arial", 10))
        add_button.pack(side=tk.RIGHT, padx=20)
        
        # Create content frame with two sections: Active Goals and Progress
        content_frame = tk.Frame(self, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create goals list
        self.create_goals_section(content_frame)
        
    def create_goals_section(self, parent):
        # Goals container
        goals_frame = tk.LabelFrame(parent, text="Your Fitness Goals", font=("Arial", 12, "bold"), 
                                 bg="white", padx=20, pady=15)
        goals_frame.pack(fill=tk.BOTH, expand=True)
        
        if not self.user.goals:
            # No goals message
            no_goals_label = tk.Label(goals_frame, text="You don't have any goals set yet. Click 'Set New Goal' to get started!", 
                                    font=("Arial", 10), bg="white", fg="#666")
            no_goals_label.pack(pady=30)
        else:
            # Create scrollable container for goals
            canvas = tk.Canvas(goals_frame, bg="white", highlightthickness=0)
            scrollbar = ttk.Scrollbar(goals_frame, orient="vertical", command=canvas.yview)
            
            scrollable_frame = tk.Frame(canvas, bg="white")
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Sort goals by deadline
            sorted_goals = sorted(self.user.goals, 
                                key=lambda g: datetime.datetime.strptime(g.deadline, "%Y-%m-%d"))
            
            # Create a card for each goal
            for i, goal in enumerate(sorted_goals):
                self.create_goal_card(scrollable_frame, goal, i)
                
    def create_goal_card(self, parent, goal, index):
        # Calculate progress
        progress = self.calculate_goal_progress(goal)
        
        # Card frame
        card_bg = "#f5f5f5" if index % 2 == 0 else "white"
        card = tk.Frame(parent, bg=card_bg, padx=15, pady=15, bd=1, relief=tk.SOLID)
        card.pack(fill=tk.X, pady=10)
        
        # Goal type and deadline
        header_frame = tk.Frame(card, bg=card_bg)
        header_frame.pack(fill=tk.X)
        
        goal_type_label = tk.Label(header_frame, text=goal.goal_type, font=("Arial", 12, "bold"), bg=card_bg)
        goal_type_label.pack(side=tk.LEFT)
        
        deadline_label = tk.Label(header_frame, text=f"Deadline: {goal.deadline}", 
                                font=("Arial", 10), bg=card_bg, fg="#666")
        deadline_label.pack(side=tk.RIGHT)
        
        # Target value
        target_frame = tk.Frame(card, bg=card_bg, pady=5)
        target_frame.pack(fill=tk.X)
        
        target_label = tk.Label(target_frame, text=f"Target: {goal.target_value}", 
                              font=("Arial", 10), bg=card_bg)
        target_label.pack(side=tk.LEFT)
        
        # Progress bar
        progress_frame = tk.Frame(card, bg=card_bg, pady=10)
        progress_frame.pack(fill=tk.X)
        
        bar_frame = tk.Frame(progress_frame, bg="#e0e0e0", height=15, width=300)
        bar_frame.pack(side=tk.LEFT)
        bar_frame.pack_propagate(False)
        
        # Progress fill
        progress_width = int(300 * progress)
        progress_fill = tk.Frame(bar_frame, bg="#4CAF50", height=15, width=progress_width)
        progress_fill.pack(side=tk.LEFT, anchor=tk.W)
        
        # Percentage
        percentage_label = tk.Label(progress_frame, text=f"{int(progress * 100)}%", 
                                  font=("Arial", 10), bg=card_bg, padx=10)
        percentage_label.pack(side=tk.LEFT)
        
        # Actions
        actions_frame = tk.Frame(card, bg=card_bg, pady=5)
        actions_frame.pack(fill=tk.X)
        
        edit_button = tk.Button(actions_frame, text="Edit", command=lambda: self.edit_goal(goal), 
                              bg="#2196F3", fg="white", font=("Arial", 8))
        edit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_button = tk.Button(actions_frame, text="Delete", command=lambda: self.delete_goal(goal), 
                                bg="#f44336", fg="white", font=("Arial", 8))
        delete_button.pack(side=tk.LEFT, padx=(0, 5))
        
        if progress >= 1.0 and not goal.completed:
            complete_button = tk.Button(actions_frame, text="Mark as Completed", 
                                      command=lambda: self.mark_as_completed(goal), 
                                      bg="#4CAF50", fg="white", font=("Arial", 8))
            complete_button.pack(side=tk.LEFT)
            
        if goal.completed:
            completed_label = tk.Label(actions_frame, text="✓ Completed", 
                                     font=("Arial", 10, "bold"), bg=card_bg, fg="#4CAF50")
            completed_label.pack(side=tk.RIGHT)
            
    def calculate_goal_progress(self, goal):
        # This is a simplified version for the demo
        # In a real app, this would calculate actual progress based on workouts and goal type
        import random
        return random.uniform(0, 1.0) if not goal.completed else 1.0
        
    def add_goal(self):
        self.goal_form(None)
        
    def edit_goal(self, goal):
        self.goal_form(goal)
        
    def delete_goal(self, goal):
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this goal?"):
            # Remove goal from user's list
            self.user.goals.remove(goal)
            
            # Save to database
            self.data_manager.update_user(self.user)
            
            # Refresh goals view
            self.refresh()
            
    def mark_as_completed(self, goal):
        goal.completed = True
        
        # Save to database
        self.data_manager.update_user(self.user)
        
        # Refresh goals view
        self.refresh()
        
        # Show congratulations message
        messagebox.showinfo("Congratulations!", "You've achieved your goal! Great job!")
        
    def goal_form(self, goal=None):
        # Create a top-level window for adding/editing goal
        is_edit = goal is not None
        form_window = tk.Toplevel(self)
        form_window.title("Edit Goal" if is_edit else "Set New Goal")
        form_window.geometry("400x350")
        form_window.configure(bg="white")
        
        # Make window modal
        form_window.grab_set()
        
        # Title
        title_label = tk.Label(form_window, text="Edit Goal" if is_edit else "Set New Goal", 
                             font=("Arial", 16, "bold"), bg="white")
        title_label.pack(pady=20)
        
        # Form container
        form_frame = tk.Frame(form_window, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Goal Type
        type_label = tk.Label(form_frame, text="Goal Type:", font=("Arial", 10, "bold"), bg="white")
        type_label.grid(row=0, column=0, sticky=tk.W, pady=10)
        
        # Goal types
        goal_types = ["Weight Loss", "Distance Run", "Workouts Per Week", "Calories Burned", 
                    "Strength Target", "Weight Lift", "Other"]
        
        type_var = tk.StringVar(value=goal.goal_type if is_edit else "")
        type_dropdown = ttk.Combobox(form_frame, textvariable=type_var, values=goal_types, width=18)
        type_dropdown.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        # Target Value
        target_label = tk.Label(form_frame, text="Target Value:", font=("Arial", 10, "bold"), bg="white")
        target_label.grid(row=1, column=0, sticky=tk.W, pady=10)
        
        target_var = tk.StringVar(value=goal.target_value if is_edit else "")
        target_entry = tk.Entry(form_frame, textvariable=target_var, font=("Arial", 10), width=20)
        target_entry.grid(row=1, column=1, sticky=tk.W, pady=10)
        
        # Target description (optional)
        target_desc_label = tk.Label(form_frame, text="(e.g., lose 5kg, run 10km, etc.)", 
                                   font=("Arial", 8), fg="#666", bg="white")
        target_desc_label.grid(row=1, column=2, sticky=tk.W, pady=10)
        
        # Deadline
        deadline_label = tk.Label(form_frame, text="Deadline:", font=("Arial", 10, "bold"), bg="white")
        deadline_label.grid(row=2, column=0, sticky=tk.W, pady=10)
        
        deadline_var = tk.StringVar(value=goal.deadline if is_edit else 
                                 (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
        deadline_entry = tk.Entry(form_frame, textvariable=deadline_var, font=("Arial", 10), width=20)
        deadline_entry.grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # Buttons
        button_frame = tk.Frame(form_window, bg="white")
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        save_button = tk.Button(button_frame, text="Save", 
                              command=lambda: self.save_goal(
                                  type_var.get(),
                                  target_var.get(),
                                  deadline_var.get(),
                                  form_window,
                                  goal if is_edit else None
                              ), 
                              bg="#4CAF50", fg="white", font=("Arial", 10))
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=form_window.destroy, 
                                bg="#f44336", fg="white", font=("Arial", 10))
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def save_goal(self, goal_type, target_value, deadline, window, existing_goal=None):
        # Validate inputs
        if not goal_type or not target_value or not deadline:
            messagebox.showerror("Error", "All fields are required", parent=window)
            return
            
        try:
            # Validate date format
            datetime.datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Deadline must be in YYYY-MM-DD format", parent=window)
            return
            
        if existing_goal:
            # Update existing goal
            existing_goal.goal_type = goal_type
            existing_goal.target_value = target_value
            existing_goal.deadline = deadline
        else:
            # Create new goal
            new_goal = Goal(goal_type, target_value, deadline)
            self.user.goals.append(new_goal)
            
        # Save to database
        self.data_manager.update_user(self.user)
        
        # Close form
        window.destroy()
        
        # Refresh goals view
        self.refresh()
        
        # Show success message
        messagebox.showinfo("Success", 
                          "Goal updated successfully" if existing_goal else "Goal set successfully")
                          
    def refresh(self):
        # Destroy current frame contents
        for widget in self.winfo_children():
            widget.destroy()
            
        # Rebuild the frame
        self.__init__(self.parent, self.user, self.data_manager)

# Nutrition and Reports classes to be continued in the next edits

class NutritionFrame(tk.Frame):
    def __init__(self, parent, user, data_manager):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        
        # Title
        title_frame = tk.Frame(self, bg="#f0f0f0", pady=20)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, text="Nutrition Tracking", font=("Arial", 18, "bold"), bg="#f0f0f0")
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Add meal button
        add_button = tk.Button(title_frame, text="Log New Meal", command=self.add_meal, 
                             bg="#4CAF50", fg="white", font=("Arial", 10))
        add_button.pack(side=tk.RIGHT, padx=20)
        
        # Create container for nutrition content
        content_frame = tk.Frame(self, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create left panel (nutrition summary) and right panel (meal log)
        left_panel = tk.Frame(content_frame, bg="white", width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        right_panel = tk.Frame(content_frame, bg="white")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create summary and meal log
        self.create_nutrition_summary(left_panel)
        self.create_meal_log(right_panel)
        
    def create_nutrition_summary(self, parent):
        # Summary title
        summary_title = tk.Label(parent, text="Today's Nutrition Summary", 
                               font=("Arial", 14, "bold"), bg="white")
        summary_title.pack(pady=(0, 20))
        
        # Calculate today's totals
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_meals = [meal for meal in self.user.meals if meal.date == today]
        
        total_calories = sum(meal.calories for meal in today_meals)
        total_proteins = sum(meal.proteins for meal in today_meals)
        total_carbs = sum(meal.carbs for meal in today_meals)
        total_fats = sum(meal.fats for meal in today_meals)
        
        # Display nutrition stats
        stats_frame = tk.Frame(parent, bg="white")
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Calories
        calories_frame = tk.LabelFrame(stats_frame, text="Calories", font=("Arial", 10, "bold"), 
                                     bg="white", padx=10, pady=10)
        calories_frame.pack(fill=tk.X, pady=5)
        
        calories_label = tk.Label(calories_frame, text=f"{total_calories} kcal", 
                                font=("Arial", 14), bg="white")
        calories_label.pack()
        
        # Macronutrients
        macros_frame = tk.LabelFrame(stats_frame, text="Macronutrients", font=("Arial", 10, "bold"), 
                                   bg="white", padx=10, pady=10)
        macros_frame.pack(fill=tk.X, pady=5)
        
        # Proteins
        protein_row = tk.Frame(macros_frame, bg="white")
        protein_row.pack(fill=tk.X, pady=5)
        
        protein_label = tk.Label(protein_row, text="Protein:", font=("Arial", 10), bg="white")
        protein_label.pack(side=tk.LEFT)
        
        protein_value = tk.Label(protein_row, text=f"{total_proteins}g", font=("Arial", 10, "bold"), bg="white")
        protein_value.pack(side=tk.RIGHT)
        
        # Carbs
        carbs_row = tk.Frame(macros_frame, bg="white")
        carbs_row.pack(fill=tk.X, pady=5)
        
        carbs_label = tk.Label(carbs_row, text="Carbohydrates:", font=("Arial", 10), bg="white")
        carbs_label.pack(side=tk.LEFT)
        
        carbs_value = tk.Label(carbs_row, text=f"{total_carbs}g", font=("Arial", 10, "bold"), bg="white")
        carbs_value.pack(side=tk.RIGHT)
        
        # Fats
        fats_row = tk.Frame(macros_frame, bg="white")
        fats_row.pack(fill=tk.X, pady=5)
        
        fats_label = tk.Label(fats_row, text="Fats:", font=("Arial", 10), bg="white")
        fats_label.pack(side=tk.LEFT)
        
        fats_value = tk.Label(fats_row, text=f"{total_fats}g", font=("Arial", 10, "bold"), bg="white")
        fats_value.pack(side=tk.RIGHT)
        
        # Nutrition tips
        tips_frame = tk.LabelFrame(parent, text="Nutrition Tips", font=("Arial", 10, "bold"), 
                                 bg="white", padx=10, pady=10)
        tips_frame.pack(fill=tk.X, pady=(20, 5))
        
        tips = [
            "Aim for a balanced diet with proteins, carbs, and healthy fats.",
            "Stay hydrated by drinking at least 8 glasses of water daily.",
            "Include a variety of fruits and vegetables in your meals.",
            "Limit processed foods and added sugars."
        ]
        
        for tip in tips:
            tip_row = tk.Frame(tips_frame, bg="white")
            tip_row.pack(fill=tk.X, pady=5)
            
            bullet = tk.Label(tip_row, text="•", font=("Arial", 10, "bold"), bg="white")
            bullet.pack(side=tk.LEFT, padx=(0, 5))
            
            tip_text = tk.Label(tip_row, text=tip, font=("Arial", 9), bg="white", 
                              wraplength=250, justify=tk.LEFT)
            tip_text.pack(side=tk.LEFT, fill=tk.X)
        
    def create_meal_log(self, parent):
        # Log title
        log_title = tk.Label(parent, text="Meal Log", font=("Arial", 14, "bold"), bg="white")
        log_title.pack(pady=(0, 10))
        
        # Date filter
        filter_frame = tk.Frame(parent, bg="white")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        date_label = tk.Label(filter_frame, text="Date:", font=("Arial", 10), bg="white")
        date_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.date_var = tk.StringVar(value=datetime.datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(filter_frame, textvariable=self.date_var, font=("Arial", 10), width=12)
        date_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        date_format_label = tk.Label(filter_frame, text="(YYYY-MM-DD)", font=("Arial", 8), fg="#666", bg="white")
        date_format_label.pack(side=tk.LEFT, padx=(0, 10))
        
        filter_button = tk.Button(filter_frame, text="Filter", command=self.filter_meals, 
                                bg="#2196F3", fg="white", font=("Arial", 9))
        filter_button.pack(side=tk.LEFT, padx=(0, 5))
        
        reset_button = tk.Button(filter_frame, text="Today", command=self.reset_filter, 
                               bg="#FF9800", fg="white", font=("Arial", 9))
        reset_button.pack(side=tk.LEFT)
        
        # Create meal log table
        self.create_meal_table(parent)
        
    def create_meal_table(self, parent):
        # Table container
        table_frame = tk.Frame(parent, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Table header
        header_frame = tk.Frame(table_frame, bg="#f5f5f5")
        header_frame.pack(fill=tk.X)
        
        headers = ["Meal Type", "Name", "Calories", "Protein (g)", "Carbs (g)", "Fats (g)", "Actions"]
        widths = [80, 150, 70, 70, 70, 70, 80]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            header_label = tk.Label(header_frame, text=header, font=("Arial", 10, "bold"), 
                                  bg="#f5f5f5", width=width//10, anchor=tk.W)
            header_label.grid(row=0, column=i, padx=5, pady=10, sticky=tk.W)
            
        # Table content - scrollable
        self.table_canvas = tk.Canvas(table_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table_canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.table_canvas, bg="white")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.table_canvas.configure(
                scrollregion=self.table_canvas.bbox("all")
            )
        )
        
        self.table_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.table_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.table_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate with meals (default today)
        self.populate_meal_table()
        
    def populate_meal_table(self, date=None):
        # Clear existing rows
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Get meals to display
        filter_date = date or datetime.datetime.now().strftime("%Y-%m-%d")
        meals = [meal for meal in self.user.meals if meal.date == filter_date]
        
        # Sort meals by type (breakfast, lunch, dinner, snack)
        meal_type_order = {"Breakfast": 0, "Lunch": 1, "Dinner": 2, "Snack": 3}
        meals = sorted(meals, key=lambda m: meal_type_order.get(m.meal_type, 4))
        
        if not meals:
            # Show empty message
            empty_label = tk.Label(self.scrollable_frame, text="No meals logged for this date", 
                                 font=("Arial", 10), bg="white", fg="#666")
            empty_label.pack(pady=30)
            return
            
        # Create rows for each meal
        for i, meal in enumerate(meals):
            row_bg = "#f9f9f9" if i % 2 == 0 else "white"
            row_frame = tk.Frame(self.scrollable_frame, bg=row_bg)
            row_frame.pack(fill=tk.X)
            
            # Meal Type
            type_label = tk.Label(row_frame, text=meal.meal_type, font=("Arial", 9), 
                                bg=row_bg, width=8, anchor=tk.W)
            type_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            
            # Name
            name_label = tk.Label(row_frame, text=meal.name, font=("Arial", 9), 
                                bg=row_bg, width=15, anchor=tk.W)
            name_label.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
            
            # Calories
            calories_label = tk.Label(row_frame, text=str(meal.calories), font=("Arial", 9), 
                                    bg=row_bg, width=7, anchor=tk.W)
            calories_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
            
            # Protein
            protein_label = tk.Label(row_frame, text=str(meal.proteins), font=("Arial", 9), 
                                   bg=row_bg, width=7, anchor=tk.W)
            protein_label.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
            
            # Carbs
            carbs_label = tk.Label(row_frame, text=str(meal.carbs), font=("Arial", 9), 
                                 bg=row_bg, width=7, anchor=tk.W)
            carbs_label.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
            
            # Fats
            fats_label = tk.Label(row_frame, text=str(meal.fats), font=("Arial", 9), 
                                bg=row_bg, width=7, anchor=tk.W)
            fats_label.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
            
            # Actions (Edit/Delete)
            actions_frame = tk.Frame(row_frame, bg=row_bg)
            actions_frame.grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
            
            # Edit button
            edit_button = tk.Button(actions_frame, text="✏️", command=lambda m=meal: self.edit_meal(m), 
                                  bg="#FF9800", fg="white", width=2, font=("Arial", 8))
            edit_button.pack(side=tk.LEFT, padx=(0, 5))
            
            # Delete button
            delete_button = tk.Button(actions_frame, text="🗑️", command=lambda m=meal: self.delete_meal(m), 
                                    bg="#f44336", fg="white", width=2, font=("Arial", 8))
            delete_button.pack(side=tk.LEFT)
            
    def filter_meals(self):
        date = self.date_var.get().strip()
        try:
            # Validate date format
            datetime.datetime.strptime(date, "%Y-%m-%d")
            self.populate_meal_table(date)
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
            
    def reset_filter(self):
        self.date_var.set(datetime.datetime.now().strftime("%Y-%m-%d"))
        self.populate_meal_table()
        
    def add_meal(self):
        self.meal_form(None)
        
    def edit_meal(self, meal):
        self.meal_form(meal)
        
    def delete_meal(self, meal):
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this meal?"):
            # Remove meal from user's list
            self.user.meals.remove(meal)
            
            # Save to database
            self.data_manager.update_user(self.user)
            
            # Refresh meal table and summary
            self.refresh()
            
    def meal_form(self, meal=None):
        # Create a top-level window for adding/editing meal
        is_edit = meal is not None
        form_window = tk.Toplevel(self)
        form_window.title("Edit Meal" if is_edit else "Log New Meal")
        form_window.geometry("400x450")
        form_window.configure(bg="white")
        
        # Make window modal
        form_window.grab_set()
        
        # Title
        title_label = tk.Label(form_window, text="Edit Meal" if is_edit else "Log New Meal", 
                             font=("Arial", 16, "bold"), bg="white")
        title_label.pack(pady=20)
        
        # Form container
        form_frame = tk.Frame(form_window, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Date
        date_label = tk.Label(form_frame, text="Date:", font=("Arial", 10, "bold"), bg="white")
        date_label.grid(row=0, column=0, sticky=tk.W, pady=10)
        
        date_var = tk.StringVar(value=meal.date if is_edit else datetime.datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(form_frame, textvariable=date_var, font=("Arial", 10), width=15)
        date_entry.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        date_format_label = tk.Label(form_frame, text="(YYYY-MM-DD)", font=("Arial", 8), fg="#666", bg="white")
        date_format_label.grid(row=0, column=2, sticky=tk.W, pady=10)
        
        # Meal Type
        type_label = tk.Label(form_frame, text="Meal Type:", font=("Arial", 10, "bold"), bg="white")
        type_label.grid(row=1, column=0, sticky=tk.W, pady=10)
        
        meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
        
        type_var = tk.StringVar(value=meal.meal_type if is_edit else "")
        type_dropdown = ttk.Combobox(form_frame, textvariable=type_var, values=meal_types, width=13)
        type_dropdown.grid(row=1, column=1, sticky=tk.W, pady=10)
        
        # Meal Name
        name_label = tk.Label(form_frame, text="Meal Name:", font=("Arial", 10, "bold"), bg="white")
        name_label.grid(row=2, column=0, sticky=tk.W, pady=10)
        
        name_var = tk.StringVar(value=meal.name if is_edit else "")
        name_entry = tk.Entry(form_frame, textvariable=name_var, font=("Arial", 10), width=20)
        name_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=10)
        
        # Calories
        calories_label = tk.Label(form_frame, text="Calories:", font=("Arial", 10, "bold"), bg="white")
        calories_label.grid(row=3, column=0, sticky=tk.W, pady=10)
        
        calories_var = tk.StringVar(value=meal.calories if is_edit else "")
        calories_entry = tk.Entry(form_frame, textvariable=calories_var, font=("Arial", 10), width=10)
        calories_entry.grid(row=3, column=1, sticky=tk.W, pady=10)
        
        calories_unit = tk.Label(form_frame, text="kcal", font=("Arial", 9), bg="white")
        calories_unit.grid(row=3, column=2, sticky=tk.W, pady=10)
        
        # Protein
        protein_label = tk.Label(form_frame, text="Protein:", font=("Arial", 10, "bold"), bg="white")
        protein_label.grid(row=4, column=0, sticky=tk.W, pady=10)
        
        protein_var = tk.StringVar(value=meal.proteins if is_edit else "")
        protein_entry = tk.Entry(form_frame, textvariable=protein_var, font=("Arial", 10), width=10)
        protein_entry.grid(row=4, column=1, sticky=tk.W, pady=10)
        
        protein_unit = tk.Label(form_frame, text="grams", font=("Arial", 9), bg="white")
        protein_unit.grid(row=4, column=2, sticky=tk.W, pady=10)
        
        # Carbs
        carbs_label = tk.Label(form_frame, text="Carbohydrates:", font=("Arial", 10, "bold"), bg="white")
        carbs_label.grid(row=5, column=0, sticky=tk.W, pady=10)
        
        carbs_var = tk.StringVar(value=meal.carbs if is_edit else "")
        carbs_entry = tk.Entry(form_frame, textvariable=carbs_var, font=("Arial", 10), width=10)
        carbs_entry.grid(row=5, column=1, sticky=tk.W, pady=10)
        
        carbs_unit = tk.Label(form_frame, text="grams", font=("Arial", 9), bg="white")
        carbs_unit.grid(row=5, column=2, sticky=tk.W, pady=10)
        
        # Fats
        fats_label = tk.Label(form_frame, text="Fats:", font=("Arial", 10, "bold"), bg="white")
        fats_label.grid(row=6, column=0, sticky=tk.W, pady=10)
        
        fats_var = tk.StringVar(value=meal.fats if is_edit else "")
        fats_entry = tk.Entry(form_frame, textvariable=fats_var, font=("Arial", 10), width=10)
        fats_entry.grid(row=6, column=1, sticky=tk.W, pady=10)
        
        fats_unit = tk.Label(form_frame, text="grams", font=("Arial", 9), bg="white")
        fats_unit.grid(row=6, column=2, sticky=tk.W, pady=10)
        
        # Buttons
        button_frame = tk.Frame(form_window, bg="white")
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        save_button = tk.Button(button_frame, text="Save", 
                              command=lambda: self.save_meal(
                                  date_var.get(),
                                  type_var.get(),
                                  name_var.get(),
                                  calories_var.get(),
                                  protein_var.get(),
                                  carbs_var.get(),
                                  fats_var.get(),
                                  form_window,
                                  meal if is_edit else None
                              ), 
                              bg="#4CAF50", fg="white", font=("Arial", 10))
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=form_window.destroy, 
                                bg="#f44336", fg="white", font=("Arial", 10))
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def save_meal(self, date, meal_type, name, calories, proteins, carbs, fats, window, existing_meal=None):
        # Validate inputs
        if not date or not meal_type or not name or not calories or not proteins or not carbs or not fats:
            messagebox.showerror("Error", "All fields are required", parent=window)
            return
            
        try:
            # Validate date format
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format", parent=window)
            return
            
        try:
            calories = int(calories)
            if calories < 0:
                messagebox.showerror("Error", "Calories must be a non-negative number", parent=window)
                return
        except ValueError:
            messagebox.showerror("Error", "Calories must be a number", parent=window)
            return
            
        try:
            proteins = float(proteins)
            if proteins < 0:
                messagebox.showerror("Error", "Protein must be a non-negative number", parent=window)
                return
        except ValueError:
            messagebox.showerror("Error", "Protein must be a number", parent=window)
            return
            
        try:
            carbs = float(carbs)
            if carbs < 0:
                messagebox.showerror("Error", "Carbohydrates must be a non-negative number", parent=window)
                return
        except ValueError:
            messagebox.showerror("Error", "Carbohydrates must be a number", parent=window)
            return
            
        try:
            fats = float(fats)
            if fats < 0:
                messagebox.showerror("Error", "Fats must be a non-negative number", parent=window)
                return
        except ValueError:
            messagebox.showerror("Error", "Fats must be a number", parent=window)
            return
            
        if existing_meal:
            # Update existing meal
            existing_meal.date = date
            existing_meal.meal_type = meal_type
            existing_meal.name = name
            existing_meal.calories = calories
            existing_meal.proteins = proteins
            existing_meal.carbs = carbs
            existing_meal.fats = fats
        else:
            # Create new meal
            new_meal = Meal(meal_type, name, calories, proteins, carbs, fats, date)
            self.user.meals.append(new_meal)
            
        # Save to database
        self.data_manager.update_user(self.user)
        
        # Close form
        window.destroy()
        
        # Refresh meal table and summary
        self.refresh()
        
        # Show success message
        messagebox.showinfo("Success", 
                          "Meal updated successfully" if existing_meal else "Meal logged successfully")
                          
    def refresh(self):
        # Destroy current frame contents
        for widget in self.winfo_children():
            widget.destroy()
            
        # Rebuild the frame
        self.__init__(self.parent, self.user, self.data_manager)

# Reports class to be continued in next edit

class ReportFrame(tk.Frame):
    def __init__(self, parent, user, data_manager):
        super().__init__(parent, bg="#f0f0f0")
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        
        # Title
        title_frame = tk.Frame(self, bg="#f0f0f0", pady=20)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, text="Reports & Analytics", font=("Arial", 18, "bold"), bg="#f0f0f0")
        title_label.pack(side=tk.LEFT, padx=20)
        
        # Create notebook (tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create report tabs
        fitness_tab = tk.Frame(notebook, bg="white")
        nutrition_tab = tk.Frame(notebook, bg="white")
        performance_tab = tk.Frame(notebook, bg="white")
        
        notebook.add(fitness_tab, text="Fitness Report")
        notebook.add(nutrition_tab, text="Nutrition Report")
        notebook.add(performance_tab, text="Performance Analysis")
        
        # Create content for each tab
        self.create_fitness_report(fitness_tab)
        self.create_nutrition_report(nutrition_tab)
        self.create_performance_analysis(performance_tab)
        
    def create_fitness_report(self, parent):
        # Report options
        options_frame = tk.Frame(parent, bg="white", padx=20, pady=10)
        options_frame.pack(fill=tk.X)
        
        # Time range
        range_label = tk.Label(options_frame, text="Time Range:", font=("Arial", 10, "bold"), bg="white")
        range_label.grid(row=0, column=0, sticky=tk.W, pady=10, padx=(0, 10))
        
        self.time_range_var = tk.StringVar(value="Last 7 Days")
        range_options = ["Last 7 Days", "Last 30 Days", "Last 3 Months", "Last Year", "All Time"]
        range_dropdown = ttk.Combobox(options_frame, textvariable=self.time_range_var, values=range_options, width=15)
        range_dropdown.grid(row=0, column=1, pady=10, padx=(0, 20))
        range_dropdown.bind("<<ComboboxSelected>>", self.update_fitness_report)
        
        # Generate button
        generate_button = tk.Button(options_frame, text="Generate Report", command=self.update_fitness_report, 
                                  bg="#4CAF50", fg="white", font=("Arial", 10))
        generate_button.grid(row=0, column=2, pady=10)
        
        # Container for report content
        self.fitness_report_frame = tk.Frame(parent, bg="white")
        self.fitness_report_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Initial report
        self.generate_fitness_report()
        
    def update_fitness_report(self, event=None):
        # Clear current report
        for widget in self.fitness_report_frame.winfo_children():
            widget.destroy()
            
        # Generate new report
        self.generate_fitness_report()
        
    def generate_fitness_report(self):
        # Get time range
        time_range = self.time_range_var.get()
        
        # Get start date based on time range
        today = datetime.datetime.now().date()
        if time_range == "Last 7 Days":
            start_date = today - datetime.timedelta(days=7)
        elif time_range == "Last 30 Days":
            start_date = today - datetime.timedelta(days=30)
        elif time_range == "Last 3 Months":
            start_date = today - datetime.timedelta(days=90)
        elif time_range == "Last Year":
            start_date = today - datetime.timedelta(days=365)
        else:  # All Time
            start_date = datetime.datetime.strptime("2000-01-01", "%Y-%m-%d").date()
            
        # Filter workouts by date range
        workouts = [w for w in self.user.workouts if 
                   datetime.datetime.strptime(w.date, "%Y-%m-%d").date() >= start_date]
        
        if not workouts:
            # No data message
            no_data = tk.Label(self.fitness_report_frame, text="No workout data found for the selected time range.", 
                             font=("Arial", 12), fg="#666", bg="white")
            no_data.pack(pady=50)
            return
            
        # Summary stats
        summary_frame = tk.LabelFrame(self.fitness_report_frame, text="Workout Summary", 
                                    font=("Arial", 12, "bold"), bg="white", padx=15, pady=15)
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Calculate summary stats
        total_workouts = len(workouts)
        total_duration = sum(w.duration for w in workouts)
        total_calories = sum(w.calories_burned for w in workouts)
        avg_duration = total_duration / total_workouts if total_workouts > 0 else 0
        
        # Workout types
        workout_types = {}
        for workout in workouts:
            workout_types[workout.workout_type] = workout_types.get(workout.workout_type, 0) + 1
            
        most_common_type = max(workout_types.items(), key=lambda x: x[1])[0] if workout_types else "N/A"
        
        # Display summary stats
        stats = [
            ("Total Workouts:", str(total_workouts)),
            ("Total Duration:", f"{total_duration} minutes"),
            ("Total Calories Burned:", f"{total_calories} kcal"),
            ("Average Workout Duration:", f"{avg_duration:.1f} minutes"),
            ("Most Common Workout Type:", most_common_type)
        ]
        
        # Create stats grid
        for i, (label_text, value) in enumerate(stats):
            row = i // 3
            col = i % 3 * 2
            
            label = tk.Label(summary_frame, text=label_text, font=("Arial", 10, "bold"), bg="white")
            label.grid(row=row, column=col, sticky=tk.W, pady=10, padx=(10 if col > 0 else 0, 5))
            
            value_label = tk.Label(summary_frame, text=value, font=("Arial", 10), bg="white")
            value_label.grid(row=row, column=col+1, sticky=tk.W, pady=10)
            
        # Charts
        charts_frame = tk.Frame(self.fitness_report_frame, bg="white")
        charts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left chart: Workout type distribution
        left_chart_frame = tk.Frame(charts_frame, bg="white")
        left_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        left_chart_title = tk.Label(left_chart_frame, text="Workout Types Distribution", 
                                  font=("Arial", 10, "bold"), bg="white")
        left_chart_title.pack(pady=(0, 10))
        
        self.create_pie_chart(left_chart_frame, workout_types)
        
        # Right chart: Calories burned over time
        right_chart_frame = tk.Frame(charts_frame, bg="white")
        right_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        right_chart_title = tk.Label(right_chart_frame, text="Calories Burned Over Time", 
                                   font=("Arial", 10, "bold"), bg="white")
        right_chart_title.pack(pady=(0, 10))
        
        self.create_line_chart(right_chart_frame, workouts)
        
    def create_pie_chart(self, parent, workout_types):
        if not workout_types:
            no_data = tk.Label(parent, text="No data available", font=("Arial", 10), fg="#666", bg="white")
            no_data.pack(pady=50)
            return
            
        # Create matplotlib figure
        fig = plt.Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create pie chart
        labels = workout_types.keys()
        sizes = workout_types.values()
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_line_chart(self, parent, workouts):
        if not workouts:
            no_data = tk.Label(parent, text="No data available", font=("Arial", 10), fg="#666", bg="white")
            no_data.pack(pady=50)
            return
            
        # Create matplotlib figure
        fig = plt.Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Aggregate calories by date
        calories_by_date = {}
        for workout in workouts:
            date = workout.date
            calories_by_date[date] = calories_by_date.get(date, 0) + workout.calories_burned
            
        # Sort by date
        sorted_dates = sorted(calories_by_date.keys())
        calories = [calories_by_date[date] for date in sorted_dates]
        
        # Plot line chart
        ax.plot(sorted_dates, calories, marker='o', linestyle='-')
        
        # Format chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Calories Burned')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        fig.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_nutrition_report(self, parent):
        # Report options
        options_frame = tk.Frame(parent, bg="white", padx=20, pady=10)
        options_frame.pack(fill=tk.X)
        
        # Time range
        range_label = tk.Label(options_frame, text="Time Range:", font=("Arial", 10, "bold"), bg="white")
        range_label.grid(row=0, column=0, sticky=tk.W, pady=10, padx=(0, 10))
        
        self.nutrition_range_var = tk.StringVar(value="Last 7 Days")
        range_options = ["Last 7 Days", "Last 30 Days", "Last 3 Months", "All Time"]
        range_dropdown = ttk.Combobox(options_frame, textvariable=self.nutrition_range_var, 
                                    values=range_options, width=15)
        range_dropdown.grid(row=0, column=1, pady=10, padx=(0, 20))
        range_dropdown.bind("<<ComboboxSelected>>", self.update_nutrition_report)
        
        # Generate button
        generate_button = tk.Button(options_frame, text="Generate Report", command=self.update_nutrition_report, 
                                  bg="#4CAF50", fg="white", font=("Arial", 10))
        generate_button.grid(row=0, column=2, pady=10)
        
        # Container for report content
        self.nutrition_report_frame = tk.Frame(parent, bg="white")
        self.nutrition_report_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Initial report
        self.generate_nutrition_report()
        
    def update_nutrition_report(self, event=None):
        # Clear current report
        for widget in self.nutrition_report_frame.winfo_children():
            widget.destroy()
            
        # Generate new report
        self.generate_nutrition_report()
        
    def generate_nutrition_report(self):
        # Get time range
        time_range = self.nutrition_range_var.get()
        
        # Get start date based on time range
        today = datetime.datetime.now().date()
        if time_range == "Last 7 Days":
            start_date = today - datetime.timedelta(days=7)
        elif time_range == "Last 30 Days":
            start_date = today - datetime.timedelta(days=30)
        elif time_range == "Last 3 Months":
            start_date = today - datetime.timedelta(days=90)
        else:  # All Time
            start_date = datetime.datetime.strptime("2000-01-01", "%Y-%m-%d").date()
            
        # Filter meals by date range
        meals = [m for m in self.user.meals if 
                datetime.datetime.strptime(m.date, "%Y-%m-%d").date() >= start_date]
        
        if not meals:
            # No data message
            no_data = tk.Label(self.nutrition_report_frame, text="No meal data found for the selected time range.", 
                             font=("Arial", 12), fg="#666", bg="white")
            no_data.pack(pady=50)
            return
            
        # Summary stats
        summary_frame = tk.LabelFrame(self.nutrition_report_frame, text="Nutrition Summary", 
                                    font=("Arial", 12, "bold"), bg="white", padx=15, pady=15)
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Calculate summary stats
        total_meals = len(meals)
        total_calories = sum(m.calories for m in meals)
        total_protein = sum(m.proteins for m in meals)
        total_carbs = sum(m.carbs for m in meals)
        total_fats = sum(m.fats for m in meals)
        
        avg_calories = total_calories / total_meals if total_meals > 0 else 0
        avg_protein = total_protein / total_meals if total_meals > 0 else 0
        avg_carbs = total_carbs / total_meals if total_meals > 0 else 0
        avg_fats = total_fats / total_meals if total_meals > 0 else 0
        
        # Display summary stats
        stats = [
            ("Total Meals:", str(total_meals)),
            ("Total Calories:", f"{total_calories} kcal"),
            ("Avg. Calories per Meal:", f"{avg_calories:.1f} kcal"),
            ("Total Protein:", f"{total_protein:.1f} g"),
            ("Total Carbs:", f"{total_carbs:.1f} g"),
            ("Total Fats:", f"{total_fats:.1f} g")
        ]
        
        # Create stats grid
        for i, (label_text, value) in enumerate(stats):
            row = i // 3
            col = i % 3 * 2
            
            label = tk.Label(summary_frame, text=label_text, font=("Arial", 10, "bold"), bg="white")
            label.grid(row=row, column=col, sticky=tk.W, pady=10, padx=(10 if col > 0 else 0, 5))
            
            value_label = tk.Label(summary_frame, text=value, font=("Arial", 10), bg="white")
            value_label.grid(row=row, column=col+1, sticky=tk.W, pady=10)
            
        # Charts
        charts_frame = tk.Frame(self.nutrition_report_frame, bg="white")
        charts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Macronutrient distribution chart
        left_chart_frame = tk.Frame(charts_frame, bg="white")
        left_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        left_chart_title = tk.Label(left_chart_frame, text="Macronutrient Distribution", 
                                  font=("Arial", 10, "bold"), bg="white")
        left_chart_title.pack(pady=(0, 10))
        
        # Create macronutrient distribution pie chart
        macros = {
            "Protein": total_protein * 4,  # 4 calories per gram
            "Carbs": total_carbs * 4,      # 4 calories per gram
            "Fats": total_fats * 9         # 9 calories per gram
        }
        self.create_pie_chart(left_chart_frame, macros)
        
        # Calories over time chart
        right_chart_frame = tk.Frame(charts_frame, bg="white")
        right_chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        right_chart_title = tk.Label(right_chart_frame, text="Calories Consumed Over Time", 
                                   font=("Arial", 10, "bold"), bg="white")
        right_chart_title.pack(pady=(0, 10))
        
        # Create calories over time line chart
        self.create_nutrition_line_chart(right_chart_frame, meals)
        
    def create_nutrition_line_chart(self, parent, meals):
        if not meals:
            no_data = tk.Label(parent, text="No data available", font=("Arial", 10), fg="#666", bg="white")
            no_data.pack(pady=50)
            return
            
        # Create matplotlib figure
        fig = plt.Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Aggregate calories by date
        calories_by_date = {}
        for meal in meals:
            date = meal.date
            calories_by_date[date] = calories_by_date.get(date, 0) + meal.calories
            
        # Sort by date
        sorted_dates = sorted(calories_by_date.keys())
        calories = [calories_by_date[date] for date in sorted_dates]
        
        # Plot line chart
        ax.plot(sorted_dates, calories, marker='o', linestyle='-', color='orange')
        
        # Format chart
        ax.set_xlabel('Date')
        ax.set_ylabel('Calories Consumed')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Adjust layout
        fig.tight_layout()
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_performance_analysis(self, parent):
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title and intro
        title_frame = tk.Frame(scrollable_frame, bg="white", padx=20, pady=10)
        title_frame.pack(fill=tk.X)
        
        title_label = tk.Label(title_frame, text="Performance Analysis", 
                             font=("Arial", 14, "bold"), bg="white")
        title_label.pack(anchor=tk.W)
        
        intro_text = "This analysis shows your fitness performance over time, helping you track your progress and identify trends."
        intro_label = tk.Label(title_frame, text=intro_text, font=("Arial", 10), bg="white", 
                             wraplength=800, justify=tk.LEFT)
        intro_label.pack(anchor=tk.W, pady=(5, 20))
        
        # If user has no data
        if not self.user.workouts and not self.user.goals:
            no_data = tk.Label(scrollable_frame, text="No workout data available for analysis.\n"
                             "Log workouts and set goals to see your performance analysis.", 
                             font=("Arial", 12), fg="#666", bg="white")
            no_data.pack(pady=50, padx=20)
            return
            
        # Trend analysis
        trend_frame = tk.LabelFrame(scrollable_frame, text="Workout Trend Analysis", 
                                  font=("Arial", 12, "bold"), bg="white", padx=15, pady=15)
        trend_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # If there are workouts, analyze trends
        if self.user.workouts:
            # Sort workouts by date
            sorted_workouts = sorted(self.user.workouts, 
                                   key=lambda w: datetime.datetime.strptime(w.date, "%Y-%m-%d"))
            
            # Calculate trends (simple version)
            if len(sorted_workouts) >= 2:
                earliest_date = datetime.datetime.strptime(sorted_workouts[0].date, "%Y-%m-%d").date()
                latest_date = datetime.datetime.strptime(sorted_workouts[-1].date, "%Y-%m-%d").date()
                days_tracking = (latest_date - earliest_date).days + 1
                
                weekly_avg = len(sorted_workouts) * 7 / days_tracking if days_tracking > 0 else 0
                
                # First and last 3 workouts for comparison (or all if less than 6)
                n_compare = min(3, len(sorted_workouts) // 2)
                first_workouts = sorted_workouts[:n_compare]
                last_workouts = sorted_workouts[-n_compare:]
                
                early_calories_avg = sum(w.calories_burned for w in first_workouts) / n_compare
                recent_calories_avg = sum(w.calories_burned for w in last_workouts) / n_compare
                
                early_duration_avg = sum(w.duration for w in first_workouts) / n_compare
                recent_duration_avg = sum(w.duration for w in last_workouts) / n_compare
                
                calories_change = ((recent_calories_avg - early_calories_avg) / early_calories_avg * 100 
                                 if early_calories_avg > 0 else 0)
                duration_change = ((recent_duration_avg - early_duration_avg) / early_duration_avg * 100 
                                 if early_duration_avg > 0 else 0)
                
                # Display trend stats
                trend_stats = [
                    ("Days Tracking:", f"{days_tracking} days"),
                    ("Weekly Workout Average:", f"{weekly_avg:.1f} workouts"),
                    ("Early Calories Average:", f"{early_calories_avg:.0f} kcal"),
                    ("Recent Calories Average:", f"{recent_calories_avg:.0f} kcal"),
                    ("Calories Burn Change:", f"{calories_change:+.1f}%"),
                    ("Early Duration Average:", f"{early_duration_avg:.0f} min"),
                    ("Recent Duration Average:", f"{recent_duration_avg:.0f} min"),
                    ("Duration Change:", f"{duration_change:+.1f}%")
                ]
                
                # Create trend grid (2 columns)
                for i, (label_text, value) in enumerate(trend_stats):
                    row = i // 2
                    col = (i % 2) * 2
                    
                    label = tk.Label(trend_frame, text=label_text, font=("Arial", 10, "bold"), bg="white")
                    label.grid(row=row, column=col, sticky=tk.W, pady=10, padx=(10 if col > 0 else 0, 5))
                    
                    value_label = tk.Label(trend_frame, text=value, font=("Arial", 10), bg="white")
                    value_label.grid(row=row, column=col+1, sticky=tk.W, pady=10)
            else:
                # Not enough data
                not_enough = tk.Label(trend_frame, text="Not enough workout data for trend analysis.\n"
                                    "Log more workouts to see trends over time.", 
                                    font=("Arial", 10), fg="#666", bg="white")
                not_enough.pack(pady=20)
        else:
            # No workouts
            no_workouts = tk.Label(trend_frame, text="No workout data available.\n"
                                 "Log workouts to see trend analysis.", 
                                 font=("Arial", 10), fg="#666", bg="white")
            no_workouts.pack(pady=20)
        
        # Goal progress
        goal_frame = tk.LabelFrame(scrollable_frame, text="Goal Progress Summary", 
                                 font=("Arial", 12, "bold"), bg="white", padx=15, pady=15)
        goal_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        if self.user.goals:
            # Calculate goal stats
            total_goals = len(self.user.goals)
            completed_goals = sum(1 for g in self.user.goals if g.completed)
            completion_rate = completed_goals / total_goals * 100 if total_goals > 0 else 0
            
            # Active goals
            active_goals = [g for g in self.user.goals if not g.completed]
            
            # Display goal stats
            goal_stats_frame = tk.Frame(goal_frame, bg="white")
            goal_stats_frame.pack(fill=tk.X, pady=(0, 10))
            
            goal_stats = [
                ("Total Goals:", str(total_goals)),
                ("Completed Goals:", str(completed_goals)),
                ("Completion Rate:", f"{completion_rate:.1f}%"),
                ("Active Goals:", str(len(active_goals)))
            ]
            
            # Create goal stats grid (2 columns)
            for i, (label_text, value) in enumerate(goal_stats):
                label = tk.Label(goal_stats_frame, text=label_text, font=("Arial", 10, "bold"), bg="white")
                label.grid(row=0, column=i*2, sticky=tk.W, pady=10, padx=(10 if i > 0 else 0, 5))
                
                value_label = tk.Label(goal_stats_frame, text=value, font=("Arial", 10), bg="white")
                value_label.grid(row=0, column=i*2+1, sticky=tk.W, pady=10, padx=(0, 15))
                
            # Active goals list
            if active_goals:
                active_goals_label = tk.Label(goal_frame, text="Active Goals:", 
                                           font=("Arial", 10, "bold"), bg="white")
                active_goals_label.pack(anchor=tk.W, pady=(10, 5))
                
                for goal in active_goals:
                    goal_row = tk.Frame(goal_frame, bg="white")
                    goal_row.pack(fill=tk.X, pady=2)
                    
                    bullet = tk.Label(goal_row, text="•", font=("Arial", 10, "bold"), bg="white")
                    bullet.pack(side=tk.LEFT, padx=(10, 5))
                    
                    goal_text = tk.Label(goal_row, 
                                       text=f"{goal.goal_type}: {goal.target_value} (Deadline: {goal.deadline})", 
                                       font=("Arial", 10), bg="white", anchor=tk.W)
                    goal_text.pack(side=tk.LEFT, fill=tk.X)
        else:
            # No goals
            no_goals = tk.Label(goal_frame, text="No goals set.\n"
                              "Set fitness goals to track your progress.", 
                              font=("Arial", 10), fg="#666", bg="white")
            no_goals.pack(pady=20)
            
        # Recommendations
        rec_frame = tk.LabelFrame(scrollable_frame, text="Recommendations", 
                                font=("Arial", 12, "bold"), bg="white", padx=15, pady=15)
        rec_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Generate some generic recommendations
        recommendations = [
            "Maintain a consistent workout schedule for better results.",
            "Balance cardio and strength training for overall fitness.",
            "Set realistic goals and track your progress regularly.",
            "Ensure proper nutrition and hydration to support your workouts.",
            "Include rest days in your routine for recovery."
        ]
        
        for rec in recommendations:
            rec_row = tk.Frame(rec_frame, bg="white")
            rec_row.pack(fill=tk.X, pady=5)
            
            bullet = tk.Label(rec_row, text="•", font=("Arial", 10, "bold"), bg="white")
            bullet.pack(side=tk.LEFT, padx=(0, 5))
            
            rec_text = tk.Label(rec_row, text=rec, font=("Arial", 10), bg="white", 
                              wraplength=700, justify=tk.LEFT, anchor=tk.W)
            rec_text.pack(side=tk.LEFT, fill=tk.X, expand=True)

def main():
    # Create and run the application
    app = FitnessModeSelector()
    app.mainloop()

if __name__ == "__main__":
    main()
