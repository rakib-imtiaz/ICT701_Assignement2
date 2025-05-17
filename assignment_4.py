"""
Smart Fitness Management System (SFMS)
ICT701 Assignment 4

A comprehensive fitness tracking application with both GUI and Text interfaces.
Features include user profiles, workout tracking, nutrition monitoring,
goal setting, and performance analytics.

Author: Emon
Student ID: 20031890
Date: October 2023
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
# Make tkcalendar optional
try:
    from tkcalendar import Calendar
    has_tkcalendar = True
except ImportError:
    has_tkcalendar = False
    # Define a simple fallback if tkcalendar isn't available
    class Calendar:
        def __init__(self, *args, **kwargs):
            pass
import re
import hashlib

class User:
    """
    User class that stores all user profile information and related health/fitness data.
    Includes methods to convert to/from dictionary format for data storage.
    """
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
    """
    Workout class to store details of individual workout sessions.
    Tracks type, duration, calories, date and notes.
    """
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
    """
    Meal class to store nutrition information for tracked meals.
    Tracks macro nutrients (proteins, carbs, fats), calories and date.
    """
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
    """
    Goal class to track fitness and health goals.
    Stores goal details, deadlines and completion status.
    """
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
    """
    Data persistence layer responsible for loading/saving user data.
    Provides CRUD operations for user management and data storage.
    """
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

class FitnessModeSelector:
    """
    Initial screen that allows users to select between GUI or text interface.
    Serves as the entry point to the application.
    """
    def __init__(self, root):  # root is now a mandatory argument
        self.root = root
        
        self.root.title("Smart Fitness Management System - Mode Selection")
        self.root.geometry("400x200")
        self.root.configure(bg="#f0f0f0")
        
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.center_window()
        
        label = tk.Label(self.root, text="Select Interface Mode", font=("Arial", 16, "bold"), bg="#f0f0f0")
        label.pack(pady=20)
        
        gui_button = tk.Button(self.root, text="GUI Mode", command=self.launch_gui, 
                            width=15, height=2, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        gui_button.pack(pady=5)
        
        text_button = tk.Button(self.root, text="Text Mode", command=self.launch_text, 
                             width=15, height=2, bg="#2196F3", fg="white", font=("Arial", 10, "bold"))
        text_button.pack(pady=5)
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def launch_gui(self):
        self.root.destroy()
        root = tk.Tk()
        app = SFMSApplication(root)
        root.mainloop()
        
    def launch_text(self):
        self.root.destroy()
        # Launch text-based interface
        TextInterface().run()
        
    def mainloop(self):
        self.root.mainloop()

class TextInterface:
    """
    Text-based command line interface for the Smart Fitness Management System.
    Provides all functionality through a console-based menu system.
    """
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

    def workout_management(self):
        """Manage workouts in text interface: view, add, edit, delete"""
        while True:
            print("\n----- Workout Management -----")
            print("1. View All Workouts")
            print("2. Log New Workout")
            print("3. Edit Workout")
            print("4. Delete Workout")
            print("5. Return to Main Menu")
            
            choice = input("Enter your choice (1-5): ")
            
            if choice == "1":
                self.view_workouts()
            elif choice == "2":
                self.add_workout()
            elif choice == "3":
                self.edit_workout()
            elif choice == "4":
                self.delete_workout()
            elif choice == "5":
                return
            else:
                print("Invalid choice. Please try again.")
                
    def view_workouts(self):
        """Display all workouts for the current user"""
        print("\n----- Your Workouts -----")
        
        if not self.current_user.workouts:
            print("You haven't logged any workouts yet.")
            return
            
        # Sort workouts by date, most recent first
        workouts = sorted(self.current_user.workouts, 
                        key=lambda w: datetime.datetime.strptime(w.date, "%Y-%m-%d"), 
                        reverse=True)
        
        print(f"{'Date':<12} {'Type':<15} {'Duration (min)':<15} {'Calories':<10} {'Notes':<20}")
        print("-" * 70)
        
        for i, workout in enumerate(workouts, 1):
            # Truncate notes if too long
            notes = workout.notes[:17] + "..." if len(workout.notes) > 20 else workout.notes
            print(f"{workout.date:<12} {workout.workout_type:<15} {workout.duration:<15} {workout.calories_burned:<10} {notes:<20}")
    
    def add_workout(self):
        """Add a new workout in text interface"""
        print("\n----- Log New Workout -----")
        
        # Get workout details
        date = input("Date (YYYY-MM-DD): ")
        
        # Validate date format
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
            
        workout_type = input("Workout Type: ")
        
        try:
            duration = int(input("Duration (minutes): "))
            if duration <= 0:
                print("Duration must be a positive number.")
                return
        except ValueError:
            print("Duration must be a number.")
            return
            
        try:
            calories = int(input("Calories Burned: "))
            if calories < 0:
                print("Calories cannot be negative.")
                return
        except ValueError:
            print("Calories must be a number.")
            return
            
        notes = input("Notes (optional): ")
        
        # Create and add the workout
        new_workout = Workout(workout_type, duration, calories, date, notes)
        self.current_user.workouts.append(new_workout)
        
        # Save changes
        self.data_manager.update_user(self.current_user)
        print("Workout logged successfully!")
    
    def edit_workout(self):
        """Edit an existing workout in text interface"""
        if not self.current_user.workouts:
            print("You haven't logged any workouts yet.")
            return
            
        self.view_workouts()
        
        try:
            index = int(input("\nEnter the number of the workout to edit (1, 2, etc.): ")) - 1
            
            # Sort workouts by date, most recent first (same as in view_workouts)
            workouts = sorted(self.current_user.workouts, 
                           key=lambda w: datetime.datetime.strptime(w.date, "%Y-%m-%d"), 
                           reverse=True)
            
            if index < 0 or index >= len(workouts):
                print("Invalid workout number.")
                return
                
            workout = workouts[index]
            
            print(f"\nEditing workout on {workout.date} ({workout.workout_type})")
            print("Leave field empty to keep current value.")
            
            # Get updated values
            date_input = input(f"Date ({workout.date}): ")
            date = date_input if date_input.strip() else workout.date
            
            # Validate date if changed
            if date != workout.date:
                try:
                    datetime.datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    print("Invalid date format. Workout not updated.")
                    return
            
            type_input = input(f"Workout Type ({workout.workout_type}): ")
            workout_type = type_input if type_input.strip() else workout.workout_type
            
            duration_input = input(f"Duration ({workout.duration} minutes): ")
            if duration_input.strip():
                try:
                    duration = int(duration_input)
                    if duration <= 0:
                        print("Duration must be a positive number. Workout not updated.")
                        return
                except ValueError:
                    print("Duration must be a number. Workout not updated.")
                    return
            else:
                duration = workout.duration
                
            calories_input = input(f"Calories Burned ({workout.calories_burned}): ")
            if calories_input.strip():
                try:
                    calories = int(calories_input)
                    if calories < 0:
                        print("Calories cannot be negative. Workout not updated.")
                        return
                except ValueError:
                    print("Calories must be a number. Workout not updated.")
                    return
            else:
                calories = workout.calories_burned
                
            notes_input = input(f"Notes ({workout.notes}): ")
            notes = notes_input if notes_input.strip() else workout.notes
            
            # Update workout
            workout.date = date
            workout.workout_type = workout_type
            workout.duration = duration
            workout.calories_burned = calories
            workout.notes = notes
            
            # Save changes
            self.data_manager.update_user(self.current_user)
            print("Workout updated successfully!")
            
        except ValueError:
            print("Please enter a valid number.")
    
    def delete_workout(self):
        """Delete a workout in text interface"""
        if not self.current_user.workouts:
            print("You haven't logged any workouts yet.")
            return
            
        self.view_workouts()
        
        try:
            index = int(input("\nEnter the number of the workout to delete (1, 2, etc.): ")) - 1
            
            # Sort workouts by date, most recent first (same as in view_workouts)
            workouts = sorted(self.current_user.workouts, 
                           key=lambda w: datetime.datetime.strptime(w.date, "%Y-%m-%d"), 
                           reverse=True)
            
            if index < 0 or index >= len(workouts):
                print("Invalid workout number.")
                return
                
            workout = workouts[index]
            
            confirm = input(f"Are you sure you want to delete the {workout.workout_type} workout on {workout.date}? (y/n): ")
            if confirm.lower() != 'y':
                print("Deletion cancelled.")
                return
                
            # Remove workout
            self.current_user.workouts.remove(workout)
            
            # Save changes
            self.data_manager.update_user(self.current_user)
            print("Workout deleted successfully!")
            
        except ValueError:
            print("Please enter a valid number.")
            
    def goal_management(self):
        """Manage goals in text interface: view, add, edit, delete, mark as completed"""
        while True:
            print("\n----- Goal Management -----")
            print("1. View All Goals")
            print("2. Set New Goal")
            print("3. Edit Goal")
            print("4. Delete Goal")
            print("5. Mark Goal as Completed")
            print("6. Return to Main Menu")
            
            choice = input("Enter your choice (1-6): ")
            
            if choice == "1":
                self.view_goals()
            elif choice == "2":
                self.add_goal()
            elif choice == "3":
                self.edit_goal()
            elif choice == "4":
                self.delete_goal()
            elif choice == "5":
                self.complete_goal()
            elif choice == "6":
                return
            else:
                print("Invalid choice. Please try again.")
                
    def view_goals(self):
        """Display all goals for the current user"""
        print("\n----- Your Goals -----")
        
        if not self.current_user.goals:
            print("You haven't set any goals yet.")
            return
            
        # Sort goals by deadline
        goals = sorted(self.current_user.goals, 
                     key=lambda g: datetime.datetime.strptime(g.deadline, "%Y-%m-%d"))
        
        print(f"{'#':<3} {'Goal Type':<15} {'Target':<15} {'Deadline':<12} {'Status':<10}")
        print("-" * 60)
        
        for i, goal in enumerate(goals, 1):
            status = "Completed" if goal.completed else "Active"
            print(f"{i:<3} {goal.goal_type:<15} {goal.target_value:<15} {goal.deadline:<12} {status:<10}")
    
    def add_goal(self):
        """Add a new goal in text interface"""
        print("\n----- Set New Goal -----")
        
        # Get goal details
        goal_type = input("Goal Type (e.g., Weight Loss, Distance Run): ")
        target = input("Target Value (e.g., lose 5kg, run 10km): ")
        
        date = input("Deadline (YYYY-MM-DD): ")
        
        # Validate date format
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
            
        # Create and add the goal
        new_goal = Goal(goal_type, target, date)
        self.current_user.goals.append(new_goal)
        
        # Save changes
        self.data_manager.update_user(self.current_user)
        print("Goal set successfully!")
    
    def edit_goal(self):
        """Edit an existing goal in text interface"""
        if not self.current_user.goals:
            print("You haven't set any goals yet.")
            return
            
        self.view_goals()
        
        try:
            index = int(input("\nEnter the number of the goal to edit (1, 2, etc.): ")) - 1
            
            # Sort goals by deadline (same as in view_goals)
            goals = sorted(self.current_user.goals, 
                         key=lambda g: datetime.datetime.strptime(g.deadline, "%Y-%m-%d"))
            
            if index < 0 or index >= len(goals):
                print("Invalid goal number.")
                return
                
            goal = goals[index]
            
            print(f"\nEditing goal: {goal.goal_type} - {goal.target_value}")
            print("Leave field empty to keep current value.")
            
            # Get updated values
            type_input = input(f"Goal Type ({goal.goal_type}): ")
            goal_type = type_input if type_input.strip() else goal.goal_type
            
            target_input = input(f"Target Value ({goal.target_value}): ")
            target = target_input if target_input.strip() else goal.target_value
            
            date_input = input(f"Deadline ({goal.deadline}): ")
            date = date_input if date_input.strip() else goal.deadline
            
            # Validate date if changed
            if date != goal.deadline:
                try:
                    datetime.datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    print("Invalid date format. Goal not updated.")
                    return
                    
            # Update goal
            goal.goal_type = goal_type
            goal.target_value = target
            goal.deadline = date
            
            # Save changes
            self.data_manager.update_user(self.current_user)
            print("Goal updated successfully!")
            
        except ValueError:
            print("Please enter a valid number.")
    
    def delete_goal(self):
        """Delete a goal in text interface"""
        if not self.current_user.goals:
            print("You haven't set any goals yet.")
            return
            
        self.view_goals()
        
        try:
            index = int(input("\nEnter the number of the goal to delete (1, 2, etc.): ")) - 1
            
            # Sort goals by deadline (same as in view_goals)
            goals = sorted(self.current_user.goals, 
                         key=lambda g: datetime.datetime.strptime(g.deadline, "%Y-%m-%d"))
            
            if index < 0 or index >= len(goals):
                print("Invalid goal number.")
                return
                
            goal = goals[index]
            
            confirm = input(f"Are you sure you want to delete the goal '{goal.goal_type} - {goal.target_value}'? (y/n): ")
            if confirm.lower() != 'y':
                print("Deletion cancelled.")
                return
                
            # Remove goal
            self.current_user.goals.remove(goal)
            
            # Save changes
            self.data_manager.update_user(self.current_user)
            print("Goal deleted successfully!")
            
        except ValueError:
            print("Please enter a valid number.")
    
    def complete_goal(self):
        """Mark a goal as completed in text interface"""
        # Filter out already completed goals
        active_goals = [g for g in self.current_user.goals if not g.completed]
        
        if not active_goals:
            print("You don't have any active goals to mark as completed.")
            return
            
        print("\n----- Mark Goal as Completed -----")
        print(f"{'#':<3} {'Goal Type':<15} {'Target':<15} {'Deadline':<12}")
        print("-" * 50)
        
        # Sort goals by deadline
        active_goals = sorted(active_goals, 
                            key=lambda g: datetime.datetime.strptime(g.deadline, "%Y-%m-%d"))
        
        for i, goal in enumerate(active_goals, 1):
            print(f"{i:<3} {goal.goal_type:<15} {goal.target_value:<15} {goal.deadline:<12}")
            
        try:
            index = int(input("\nEnter the number of the goal to mark as completed (1, 2, etc.): ")) - 1
            
            if index < 0 or index >= len(active_goals):
                print("Invalid goal number.")
                return
                
            goal = active_goals[index]
            
            # Mark as completed
            goal.completed = True
            
            # Save changes
            self.data_manager.update_user(self.current_user)
            print(f"Goal '{goal.goal_type} - {goal.target_value}' marked as completed. Congratulations!")
            
        except ValueError:
            print("Please enter a valid number.")
            
    def nutrition_management(self):
        """Manage meals in text interface: view, log, edit, delete"""
        while True:
            print("\n----- Nutrition Management -----")
            print("1. View Meal Log")
            print("2. Log New Meal")
            print("3. Edit Meal")
            print("4. Delete Meal")
            print("5. Nutrition Summary")
            print("6. Return to Main Menu")
            
            choice = input("Enter your choice (1-6): ")
            
            if choice == "1":
                self.view_meals()
            elif choice == "2":
                self.add_meal()
            elif choice == "3":
                self.edit_meal()
            elif choice == "4":
                self.delete_meal()
            elif choice == "5":
                self.nutrition_summary()
            elif choice == "6":
                return
            else:
                print("Invalid choice. Please try again.")
                
    def view_meals(self):
        """Display meals for the current user, optionally filtered by date"""
        print("\n----- Meal Log -----")
        
        # Option to filter by date
        filter_option = input("Filter by date? (y/n): ")
        
        if filter_option.lower() == 'y':
            date = input("Enter date (YYYY-MM-DD): ")
            try:
                # Validate date format
                datetime.datetime.strptime(date, "%Y-%m-%d")
                # Filter meals
                meals = [m for m in self.current_user.meals if m.date == date]
            except ValueError:
                print("Invalid date format. Showing all meals.")
                meals = self.current_user.meals
        else:
            meals = self.current_user.meals
            
        if not meals:
            print("No meals logged yet.")
            return
            
        # Sort meals by date (newest first)
        meals = sorted(meals, key=lambda m: (m.date, m.meal_type), reverse=True)
        
        print(f"{'#':<3} {'Date':<12} {'Meal Type':<10} {'Name':<20} {'Calories':<8} {'Protein':<8} {'Carbs':<8} {'Fats':<8}")
        print("-" * 80)
        
        for i, meal in enumerate(meals, 1):
            name_display = meal.name[:17] + "..." if len(meal.name) > 20 else meal.name
            print(f"{i:<3} {meal.date:<12} {meal.meal_type:<10} {name_display:<20} {meal.calories:<8} {meal.proteins:<8} {meal.carbs:<8} {meal.fats:<8}")
    
    def add_meal(self):
        """Add a new meal in text interface"""
        print("\n----- Log New Meal -----")
        
        # Get meal details
        date = input("Date (YYYY-MM-DD): ")
        
        # Validate date format
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
            
        # Meal type
        print("\nMeal Type:")
        print("1. Breakfast")
        print("2. Lunch")
        print("3. Dinner")
        print("4. Snack")
        
        meal_choice = input("Choose meal type (1-4): ")
        meal_types = {"1": "Breakfast", "2": "Lunch", "3": "Dinner", "4": "Snack"}
        
        if meal_choice not in meal_types:
            print("Invalid choice. Using 'Other' as meal type.")
            meal_type = "Other"
        else:
            meal_type = meal_types[meal_choice]
            
        name = input("Meal Name: ")
        
        try:
            calories = int(input("Calories: "))
            if calories < 0:
                print("Calories cannot be negative.")
                return
        except ValueError:
            print("Calories must be a number.")
            return
            
        try:
            proteins = float(input("Protein (g): "))
            if proteins < 0:
                print("Protein cannot be negative.")
                return
        except ValueError:
            print("Protein must be a number.")
            return
            
        try:
            carbs = float(input("Carbohydrates (g): "))
            if carbs < 0:
                print("Carbohydrates cannot be negative.")
                return
        except ValueError:
            print("Carbohydrates must be a number.")
            return
            
        try:
            fats = float(input("Fats (g): "))
            if fats < 0:
                print("Fats cannot be negative.")
                return
        except ValueError:
            print("Fats must be a number.")
            return
            
        # Create and add the meal
        new_meal = Meal(meal_type, name, calories, proteins, carbs, fats, date)
        self.current_user.meals.append(new_meal)
        
        # Save changes
        self.data_manager.update_user(self.current_user)
        print("Meal logged successfully!")
    
    def edit_meal(self):
        """Edit an existing meal in text interface"""
        if not self.current_user.meals:
            print("You haven't logged any meals yet.")
            return
            
        self.view_meals()
        
        try:
            index = int(input("\nEnter the number of the meal to edit (1, 2, etc.): ")) - 1
            
            # Sort meals by date (newest first), same as in view_meals
            meals = sorted(self.current_user.meals, 
                         key=lambda m: (m.date, m.meal_type), 
                         reverse=True)
            
            if index < 0 or index >= len(meals):
                print("Invalid meal number.")
                return
                
            meal = meals[index]
            
            print(f"\nEditing meal: {meal.name} ({meal.meal_type} on {meal.date})")
            print("Leave field empty to keep current value.")
            
            # Get updated values
            date_input = input(f"Date ({meal.date}): ")
            date = date_input if date_input.strip() else meal.date
            
            # Validate date if changed
            if date != meal.date:
                try:
                    datetime.datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    print("Invalid date format. Meal not updated.")
                    return
            
            # Meal type
            print("\nMeal Type:")
            print(f"Current: {meal.meal_type}")
            print("1. Breakfast")
            print("2. Lunch")
            print("3. Dinner")
            print("4. Snack")
            print("5. Keep current")
            
            meal_choice = input("Choose meal type (1-5): ")
            meal_types = {"1": "Breakfast", "2": "Lunch", "3": "Dinner", "4": "Snack"}
            
            if meal_choice == "5":
                meal_type = meal.meal_type
            elif meal_choice in meal_types:
                meal_type = meal_types[meal_choice]
            else:
                print("Invalid choice. Keeping current meal type.")
                meal_type = meal.meal_type
                
            name_input = input(f"Meal Name ({meal.name}): ")
            name = name_input if name_input.strip() else meal.name
            
            calories_input = input(f"Calories ({meal.calories}): ")
            if calories_input.strip():
                try:
                    calories = int(calories_input)
                    if calories < 0:
                        print("Calories cannot be negative. Meal not updated.")
                        return
                except ValueError:
                    print("Calories must be a number. Meal not updated.")
                    return
            else:
                calories = meal.calories
                
            proteins_input = input(f"Protein ({meal.proteins} g): ")
            if proteins_input.strip():
                try:
                    proteins = float(proteins_input)
                    if proteins < 0:
                        print("Protein cannot be negative. Meal not updated.")
                        return
                except ValueError:
                    print("Protein must be a number. Meal not updated.")
                    return
            else:
                proteins = meal.proteins
                
            carbs_input = input(f"Carbohydrates ({meal.carbs} g): ")
            if carbs_input.strip():
                try:
                    carbs = float(carbs_input)
                    if carbs < 0:
                        print("Carbohydrates cannot be negative. Meal not updated.")
                        return
                except ValueError:
                    print("Carbohydrates must be a number. Meal not updated.")
                    return
            else:
                carbs = meal.carbs
                
            fats_input = input(f"Fats ({meal.fats} g): ")
            if fats_input.strip():
                try:
                    fats = float(fats_input)
                    if fats < 0:
                        print("Fats cannot be negative. Meal not updated.")
                        return
                except ValueError:
                    print("Fats must be a number. Meal not updated.")
                    return
            else:
                fats = meal.fats
                
            # Update meal
            meal.date = date
            meal.meal_type = meal_type
            meal.name = name
            meal.calories = calories
            meal.proteins = proteins
            meal.carbs = carbs
            meal.fats = fats
            
            # Save changes
            self.data_manager.update_user(self.current_user)
            print("Meal updated successfully!")
            
        except ValueError:
            print("Please enter a valid number.")
    
    def delete_meal(self):
        """Delete a meal in text interface"""
        if not self.current_user.meals:
            print("You haven't logged any meals yet.")
            return
            
        self.view_meals()
        
        try:
            index = int(input("\nEnter the number of the meal to delete (1, 2, etc.): ")) - 1
            
            # Sort meals by date (newest first), same as in view_meals
            meals = sorted(self.current_user.meals, 
                         key=lambda m: (m.date, m.meal_type), 
                         reverse=True)
            
            if index < 0 or index >= len(meals):
                print("Invalid meal number.")
                return
                
            meal = meals[index]
            
            confirm = input(f"Are you sure you want to delete '{meal.name}' from {meal.date}? (y/n): ")
            if confirm.lower() != 'y':
                print("Deletion cancelled.")
                return
                
            # Remove meal
            self.current_user.meals.remove(meal)
            
            # Save changes
            self.data_manager.update_user(self.current_user)
            print("Meal deleted successfully!")
            
        except ValueError:
            print("Please enter a valid number.")
    
    def nutrition_summary(self):
        """Display nutrition summary for a specific date or time range"""
        print("\n----- Nutrition Summary -----")
        
        print("Time Range:")
        print("1. Today")
        print("2. Yesterday")
        print("3. Last 7 days")
        print("4. Last 30 days")
        print("5. Specific date")
        
        choice = input("Choose time range (1-5): ")
        
        today = datetime.datetime.now().date()
        
        if choice == "1":
            # Today
            start_date = today
            end_date = today
            date_str = today.strftime("%Y-%m-%d")
        elif choice == "2":
            # Yesterday
            start_date = today - datetime.timedelta(days=1)
            end_date = start_date
            date_str = start_date.strftime("%Y-%m-%d")
        elif choice == "3":
            # Last 7 days
            start_date = today - datetime.timedelta(days=6)
            end_date = today
            date_str = f"{start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
        elif choice == "4":
            # Last 30 days
            start_date = today - datetime.timedelta(days=29)
            end_date = today
            date_str = f"{start_date.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
        elif choice == "5":
            # Specific date
            date_str = input("Enter date (YYYY-MM-DD): ")
            try:
                start_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                end_date = start_date
            except ValueError:
                print("Invalid date format.")
                return
        else:
            print("Invalid choice.")
            return
            
        # Filter meals by date range
        meals = [m for m in self.current_user.meals if 
               start_date <= datetime.datetime.strptime(m.date, "%Y-%m-%d").date() <= end_date]
        
        if not meals:
            print(f"No meals logged for {date_str}.")
            return
            
        # Calculate totals
        total_calories = sum(m.calories for m in meals)
        total_proteins = sum(m.proteins for m in meals)
        total_carbs = sum(m.carbs for m in meals)
        total_fats = sum(m.fats for m in meals)
        
        num_days = (end_date - start_date).days + 1
        
        print(f"\nNutrition Summary for {date_str}")
        print("-" * 40)
        print(f"Total Meals: {len(meals)}")
        print(f"Total Calories: {total_calories} kcal")
        
        if num_days > 1:
            print(f"Average Daily Calories: {total_calories / num_days:.1f} kcal")
            
        print("\nMacronutrient Breakdown:")
        print(f"Protein: {total_proteins:.1f} g ({total_proteins * 4:.1f} kcal)")
        print(f"Carbohydrates: {total_carbs:.1f} g ({total_carbs * 4:.1f} kcal)")
        print(f"Fats: {total_fats:.1f} g ({total_fats * 9:.1f} kcal)")
        
        # Calculate percentages if there are calories
        if total_calories > 0:
            protein_pct = (total_proteins * 4 / total_calories) * 100
            carbs_pct = (total_carbs * 4 / total_calories) * 100
            fats_pct = (total_fats * 9 / total_calories) * 100
            
            print("\nMacronutrient Percentages:")
            print(f"Protein: {protein_pct:.1f}%")
            print(f"Carbohydrates: {carbs_pct:.1f}%")
            print(f"Fats: {fats_pct:.1f}%")
            
        # Show distribution by meal type
        meal_types = {}
        for meal in meals:
            if meal.meal_type not in meal_types:
                meal_types[meal.meal_type] = 0
            meal_types[meal.meal_type] += meal.calories
            
        if len(meal_types) > 1:  # Only show if more than one meal type
            print("\nCalorie Distribution by Meal Type:")
            for meal_type, cals in meal_types.items():
                pct = (cals / total_calories) * 100
                print(f"{meal_type}: {cals} kcal ({pct:.1f}%)")
                
    def reports_management(self):
        """Generate and view reports in text interface"""
        while True:
            print("\n----- Reports and Analytics -----")
            print("1. Fitness Report")
            print("2. Nutrition Report")
            print("3. Performance Analysis")
            print("4. Return to Main Menu")
            
            choice = input("Enter your choice (1-4): ")
            
            if choice == "1":
                self.fitness_report()
            elif choice == "2":
                self.nutrition_report()
            elif choice == "3":
                self.performance_analysis()
            elif choice == "4":
                return
            else:
                print("Invalid choice. Please try again.")
                
    def fitness_report(self):
        """Generate fitness report in text interface"""
        print("\n----- Fitness Report -----")
        
        # Choose time range
        print("Time Range:")
        print("1. Last 7 Days")
        print("2. Last 30 Days")
        print("3. Last 3 Months")
        print("4. Last Year")
        print("5. All Time")
        
        choice = input("Choose time range (1-5): ")
        
        today = datetime.datetime.now().date()
        
        if choice == "1":
            # Last 7 Days
            start_date = today - datetime.timedelta(days=7)
            time_range = "Last 7 Days"
        elif choice == "2":
            # Last 30 Days
            start_date = today - datetime.timedelta(days=30)
            time_range = "Last 30 Days"
        elif choice == "3":
            # Last 3 Months
            start_date = today - datetime.timedelta(days=90)
            time_range = "Last 3 Months"
        elif choice == "4":
            # Last Year
            start_date = today - datetime.timedelta(days=365)
            time_range = "Last Year"
        elif choice == "5":
            # All Time
            start_date = datetime.datetime.strptime("2000-01-01", "%Y-%m-%d").date()
            time_range = "All Time"
        else:
            print("Invalid choice.")
            return
            
        # Filter workouts by date range
        workouts = [w for w in self.current_user.workouts if 
                   datetime.datetime.strptime(w.date, "%Y-%m-%d").date() >= start_date]
        
        if not workouts:
            print(f"No workout data found for {time_range}.")
            return
            
        # Calculate summary stats
        total_workouts = len(workouts)
        total_duration = sum(w.duration for w in workouts)
        total_calories = sum(w.calories_burned for w in workouts)
        avg_duration = total_duration / total_workouts if total_workouts > 0 else 0
        
        # Count workout types
        workout_types = {}
        for workout in workouts:
            workout_types[workout.workout_type] = workout_types.get(workout.workout_type, 0) + 1
            
        most_common_type = max(workout_types.items(), key=lambda x: x[1])[0] if workout_types else "N/A"
        
        # Display summary
        print(f"\nFitness Report ({time_range})")
        print("-" * 40)
        print(f"Total Workouts: {total_workouts}")
        print(f"Total Duration: {total_duration} minutes")
        print(f"Total Calories Burned: {total_calories} kcal")
        print(f"Average Workout Duration: {avg_duration:.1f} minutes")
        print(f"Most Common Workout Type: {most_common_type}")
        
        # Display workout type distribution
        print("\nWorkout Type Distribution:")
        for workout_type, count in sorted(workout_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_workouts) * 100
            print(f"{workout_type}: {count} workouts ({percentage:.1f}%)")
        
        # Calculate trends if enough data
        if len(workouts) >= 2:
            print("\nTrend Analysis:")
            
            # Sort workouts by date
            workouts_sorted = sorted(workouts, key=lambda w: w.date)
            
            # Calculate days between first and last workout
            first_date = datetime.datetime.strptime(workouts_sorted[0].date, "%Y-%m-%d").date()
            last_date = datetime.datetime.strptime(workouts_sorted[-1].date, "%Y-%m-%d").date()
            days_tracking = (last_date - first_date).days + 1
            
            if days_tracking > 0:
                weekly_avg = len(workouts) * 7 / days_tracking
                print(f"Weekly Workout Average: {weekly_avg:.1f} workouts")
            
            # Split workouts into two halves to compare progress
            midpoint = len(workouts_sorted) // 2
            early_workouts = workouts_sorted[:midpoint]
            recent_workouts = workouts_sorted[midpoint:]
            
            early_calories_avg = sum(w.calories_burned for w in early_workouts) / len(early_workouts)
            recent_calories_avg = sum(w.calories_burned for w in recent_workouts) / len(recent_workouts)
            
            calories_change = ((recent_calories_avg - early_calories_avg) / early_calories_avg * 100
                              if early_calories_avg > 0 else 0)
            
            print(f"Early Calories Burned Average: {early_calories_avg:.1f} kcal")
            print(f"Recent Calories Burned Average: {recent_calories_avg:.1f} kcal")
            print(f"Calories Burned Change: {calories_change:+.1f}%")
            
            early_duration_avg = sum(w.duration for w in early_workouts) / len(early_workouts)
            recent_duration_avg = sum(w.duration for w in recent_workouts) / len(recent_workouts)
            
            duration_change = ((recent_duration_avg - early_duration_avg) / early_duration_avg * 100
                              if early_duration_avg > 0 else 0)
            
            print(f"Early Duration Average: {early_duration_avg:.1f} minutes")
            print(f"Recent Duration Average: {recent_duration_avg:.1f} minutes")
            print(f"Duration Change: {duration_change:+.1f}%")
    
    def nutrition_report(self):
        """Generate nutrition report in text interface"""
        print("\n----- Nutrition Report -----")
        
        # Choose time range
        print("Time Range:")
        print("1. Last 7 Days")
        print("2. Last 30 Days")
        print("3. Last 3 Months")
        print("4. All Time")
        
        choice = input("Choose time range (1-4): ")
        
        today = datetime.datetime.now().date()
        
        if choice == "1":
            # Last 7 Days
            start_date = today - datetime.timedelta(days=7)
            time_range = "Last 7 Days"
        elif choice == "2":
            # Last 30 Days
            start_date = today - datetime.timedelta(days=30)
            time_range = "Last 30 Days"
        elif choice == "3":
            # Last 3 Months
            start_date = today - datetime.timedelta(days=90)
            time_range = "Last 3 Months"
        elif choice == "4":
            # All Time
            start_date = datetime.datetime.strptime("2000-01-01", "%Y-%m-%d").date()
            time_range = "All Time"
        else:
            print("Invalid choice.")
            return
            
        # Filter meals by date range
        meals = [m for m in self.current_user.meals if 
               datetime.datetime.strptime(m.date, "%Y-%m-%d").date() >= start_date]
        
        if not meals:
            print(f"No meal data found for {time_range}.")
            return
            
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
        
        # Count unique dates to get number of days
        unique_dates = len(set(m.date for m in meals))
        avg_calories_day = total_calories / unique_dates if unique_dates > 0 else 0
        
        # Display summary
        print(f"\nNutrition Report ({time_range})")
        print("-" * 40)
        print(f"Total Meals: {total_meals}")
        print(f"Days with Recorded Meals: {unique_dates}")
        print(f"Total Calories: {total_calories} kcal")
        print(f"Average Daily Calories: {avg_calories_day:.1f} kcal")
        print(f"Average Calories per Meal: {avg_calories:.1f} kcal")
        
        print("\nMacronutrients Summary:")
        print(f"Total Protein: {total_protein:.1f} g")
        print(f"Total Carbohydrates: {total_carbs:.1f} g")
        print(f"Total Fats: {total_fats:.1f} g")
        
        print("\nAverage Macronutrients per Meal:")
        print(f"Protein: {avg_protein:.1f} g")
        print(f"Carbohydrates: {avg_carbs:.1f} g")
        print(f"Fats: {avg_fats:.1f} g")
        
        # Macronutrient percentages
        total_macro_calories = (total_protein * 4) + (total_carbs * 4) + (total_fats * 9)
        
        if total_macro_calories > 0:
            protein_pct = (total_protein * 4 / total_macro_calories) * 100
            carbs_pct = (total_carbs * 4 / total_macro_calories) * 100
            fats_pct = (total_fats * 9 / total_macro_calories) * 100
            
            print("\nMacronutrient Distribution:")
            print(f"Protein: {protein_pct:.1f}%")
            print(f"Carbohydrates: {carbs_pct:.1f}%")
            print(f"Fats: {fats_pct:.1f}%")
        
        # Meal type distribution
        meal_types = {}
        for meal in meals:
            if meal.meal_type not in meal_types:
                meal_types[meal.meal_type] = 0
            meal_types[meal.meal_type] += meal.calories
            
        if len(meal_types) > 1:
            print("\nCalorie Distribution by Meal Type:")
            for meal_type, cals in sorted(meal_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (cals / total_calories) * 100
                print(f"{meal_type}: {cals} kcal ({percentage:.1f}%)")
    
    def performance_analysis(self):
        """Generate performance analysis report in text interface"""
        print("\n----- Performance Analysis -----")
        print("Analyzing your fitness data and goals...\n")
        
        # Check if user has any data
        if not self.current_user.workouts and not self.current_user.goals:
            print("No workout data or goals available for analysis.")
            print("Log workouts and set goals to see your performance analysis.")
            return
            
        # Analyze workout trends
        if self.current_user.workouts:
            # Sort workouts by date
            workouts = sorted(self.current_user.workouts, 
                            key=lambda w: datetime.datetime.strptime(w.date, "%Y-%m-%d"))
            
            # Calculate trends
            if len(workouts) >= 2:
                earliest_date = datetime.datetime.strptime(workouts[0].date, "%Y-%m-%d").date()
                latest_date = datetime.datetime.strptime(workouts[-1].date, "%Y-%m-%d").date()
                days_tracking = (latest_date - earliest_date).days + 1
                
                print("----- Workout Trend Analysis -----")
                print(f"Days Tracking: {days_tracking} days")
                
                if days_tracking > 0:
                    weekly_avg = len(workouts) * 7 / days_tracking
                    print(f"Weekly Workout Average: {weekly_avg:.1f} workouts")
                    
                # Compare first and last workouts (or groups if many)
                if len(workouts) > 5:
                    n_compare = min(3, len(workouts) // 2)
                    first_workouts = workouts[:n_compare]
                    last_workouts = workouts[-n_compare:]
                    
                    early_calories_avg = sum(w.calories_burned for w in first_workouts) / n_compare
                    recent_calories_avg = sum(w.calories_burned for w in last_workouts) / n_compare
                    
                    early_duration_avg = sum(w.duration for w in first_workouts) / n_compare
                    recent_duration_avg = sum(w.duration for w in last_workouts) / n_compare
                    
                    calories_change = ((recent_calories_avg - early_calories_avg) / early_calories_avg * 100 
                                     if early_calories_avg > 0 else 0)
                    duration_change = ((recent_duration_avg - early_duration_avg) / early_duration_avg * 100 
                                     if early_duration_avg > 0 else 0)
                    
                    print(f"Early Calories Average: {early_calories_avg:.0f} kcal")
                    print(f"Recent Calories Average: {recent_calories_avg:.0f} kcal")
                    print(f"Calories Burn Change: {calories_change:+.1f}%")
                    print(f"Early Duration Average: {early_duration_avg:.0f} min")
                    print(f"Recent Duration Average: {recent_duration_avg:.0f} min")
                    print(f"Duration Change: {duration_change:+.1f}%")
            else:
                print("Not enough workout data for trend analysis.")
                print("Log more workouts to see trends over time.")
        else:
            print("No workout data available.")
            print("Log workouts to see trend analysis.")
            
        # Analyze goals
        if self.current_user.goals:
            total_goals = len(self.current_user.goals)
            completed_goals = sum(1 for g in self.current_user.goals if g.completed)
            completion_rate = (completed_goals / total_goals) * 100 if total_goals > 0 else 0
            active_goals = [g for g in self.current_user.goals if not g.completed]
            
            print("\n----- Goal Progress Summary -----")
            print(f"Total Goals: {total_goals}")
            print(f"Completed Goals: {completed_goals}")
            print(f"Completion Rate: {completion_rate:.1f}%")
            print(f"Active Goals: {len(active_goals)}")
            
            # Show active goals
            if active_goals:
                print("\nActive Goals:")
                for goal in sorted(active_goals, 
                                key=lambda g: datetime.datetime.strptime(g.deadline, "%Y-%m-%d")):
                    print(f"• {goal.goal_type}: {goal.target_value} (Deadline: {goal.deadline})")
        else:
            print("\nNo goals set.")
            print("Set fitness goals to track your progress.")
            
        # General recommendations
        print("\n----- Recommendations -----")
        print("• Maintain a consistent workout schedule for better results.")
        print("• Balance cardio and strength training for overall fitness.")
        print("• Set realistic goals and track your progress regularly.")
        print("• Ensure proper nutrition and hydration to support your workouts.")
        print("• Include rest days in your routine for recovery.")

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
            pass  # Icon not found, continue without it
            
        # Set custom fonts
        self.title_font = ("Helvetica", 16, "bold")
        self.header_font = ("Helvetica", 14, "bold")
        self.normal_font = ("Helvetica", 10)
        self.small_font = ("Helvetica", 9)
        
        self.data_manager = DataManager()
        self.current_user = None
        
        self.show_login_frame()
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def show_login_frame(self):
        # Clear existing frames
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create frame in the root window, but pass self (the application) as the controller
        self.login_frame = LoginFrame(self.root, self)
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        
    def show_register_frame(self):
        # Clear existing frames
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create frame in the root window, but pass self (the application) as the controller
        self.register_frame = RegisterFrame(self.root, self)
        self.register_frame.pack(fill=tk.BOTH, expand=True)
        
    def show_main_app(self):
        # Clear existing frames
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create main app components
        self.main_frame = MainAppFrame(self.root, self.current_user, self.logout_callback)
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
        
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Login Failed", "Please enter both username and password")
            return
            
        # Use the controller to call login_callback
        self.controller.login_callback(username, password)
        
    def show_register(self, event=None):
        # Use the controller to navigate to register frame
        self.controller.show_register_frame()
        
class RegisterFrame(tk.Frame):
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
        # Use the controller to navigate back to login frame
        self.controller.show_login_frame()

class MainAppFrame(tk.Frame):
    def __init__(self, parent, user, logout_callback):
        super().__init__(parent, bg="#f5f7fa")
        self.parent = parent
        self.user = user
        self.logout_callback = logout_callback
        self.data_manager = DataManager()
        self.create_layout()
        
    def create_layout(self):
        self.main_container = tk.Frame(self, bg="#f5f7fa")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self.sidebar = tk.Frame(self.main_container, bg="#2c3e50", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        self.content_area = tk.Frame(self.main_container, bg="#ffffff", bd=0) # Changed to white background
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10) # Added padding
        
        self.create_sidebar()
        self.show_profile()
        
    def create_sidebar(self):
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
        super().__init__(parent, bg="#f5f7fa") # Main background for the frame itself
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        
        title_frame = tk.Frame(self, bg="#f5f7fa", pady=15) # pady adjusted
        title_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(title_frame, text="Profile", font=("Arial", 20, "bold"), fg="#2c3e50", bg="#f5f7fa") # colored title
        title_label.pack(side=tk.LEFT)
        
        content_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20) # White content box
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))
        
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
        edit_button.pack(pady=(20, 5))
        
        # Delete button
        delete_button = tk.Button(info_frame, text="Delete Profile", command=self.delete_profile, 
                                bg="#f44336", fg="white", font=("Arial", 10), pady=5)
        delete_button.pack(pady=(5, 20))
        
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
            
    def delete_profile(self):
        """Delete the current user's profile after confirmation"""
        # Ask for confirmation
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "Are you sure you want to delete your profile? This action cannot be undone.",
            icon='warning'
        )
        
        if not confirm:
            return
            
        # Double-check with password confirmation for security
        password = simpledialog.askstring(
            "Password Confirmation", 
            "Please enter your password to confirm account deletion:", 
            show='*'
        )
        
        if not password:
            return
            
        # Verify password
        if password != self.user.password:  # In a real app, use proper password verification
            messagebox.showerror("Error", "Incorrect password. Profile not deleted.")
            return
            
        # Delete the user
        if self.data_manager.delete_user(self.user.username):
            messagebox.showinfo("Success", "Your profile has been deleted successfully.")
            # Return to login screen
            for widget in self.winfo_toplevel().winfo_children():
                widget.destroy()
            # Get the controller (SFMSApplication instance) and call logout
            self.master.master.logout_callback()
        else:
            messagebox.showerror("Error", "Failed to delete profile. Please try again.")

class WorkoutFrame(tk.Frame):
    def __init__(self, parent, user, data_manager):
        super().__init__(parent, bg="#f5f7fa")
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        self.custom_start_date = None
        self.custom_end_date = None
        
        title_frame = tk.Frame(self, bg="#f5f7fa", pady=15)
        title_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(title_frame, text="Workout Tracking", font=("Arial", 20, "bold"), fg="#2c3e50", bg="#f5f7fa")
        title_label.pack(side=tk.LEFT)
        
        add_button = tk.Button(title_frame, text="Log New Workout", command=self.add_workout, 
                             bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), relief=tk.RAISED, bd=1)
        add_button.pack(side=tk.RIGHT)
        
        self.history_frame = tk.Frame(self, bg="#ffffff")
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0,20))
        
        self.create_filter_options()
        self.create_workout_table()
        
    def create_filter_options(self):
        filter_frame = tk.Frame(self.history_frame, bg="white", padx=20, pady=10)
        filter_frame.pack(fill=tk.X)
        
        filter_label = tk.Label(filter_frame, text="Filter Workouts:", font=("Arial", 12, "bold"), bg="white")
        filter_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10), columnspan=6)
        
        date_label = tk.Label(filter_frame, text="Date Range:", font=("Arial", 10), bg="white")
        date_label.grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        
        self.date_var = tk.StringVar(value="All Time")
        date_options = ["All Time", "Today", "This Week", "This Month", "Custom"]
        date_dropdown = ttk.Combobox(filter_frame, textvariable=self.date_var, values=date_options, width=15)
        date_dropdown.grid(row=1, column=1, pady=5, padx=(0, 20))
        date_dropdown.bind("<<ComboboxSelected>>", self.on_date_filter_change)
        
        type_label = tk.Label(filter_frame, text="Workout Type:", font=("Arial", 10), bg="white")
        type_label.grid(row=1, column=2, sticky=tk.W, pady=5, padx=(0, 10))
        
        self.type_var = tk.StringVar(value="All Types")
        workout_types = ["All Types"]
        if self.user.workouts:
            workout_types.extend(list(set(w.workout_type for w in self.user.workouts)))
        type_dropdown = ttk.Combobox(filter_frame, textvariable=self.type_var, values=workout_types, width=15)
        type_dropdown.grid(row=1, column=3, pady=5, padx=(0, 20))
        type_dropdown.bind("<<ComboboxSelected>>", self.filter_workouts)
        
        filter_button = tk.Button(filter_frame, text="Apply Filters", command=self.filter_workouts, 
                                bg="#2196F3", fg="white", font=("Arial", 10))
        filter_button.grid(row=1, column=4, pady=5, padx=(0, 10))
        
        reset_button = tk.Button(filter_frame, text="Reset", command=self.reset_filters, 
                               bg="#f44336", fg="white", font=("Arial", 10))
        reset_button.grid(row=1, column=5, pady=5)
        
    def create_workout_table(self):
        table_frame = tk.Frame(self.history_frame, bg="white", padx=20, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = tk.Frame(table_frame, bg="#f5f5f5")
        header_frame.pack(fill=tk.X)
        
        headers = ["Date", "Workout Type", "Duration (min)", "Calories Burned", "Actions"]
        widths = [150, 200, 120, 120, 100]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            header_label = tk.Label(header_frame, text=header, font=("Arial", 10, "bold"), 
                                  bg="#f5f5f5", width=width//10, anchor=tk.W)
            header_label.grid(row=0, column=i, padx=10, pady=10, sticky=tk.W)
            
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
        
        self.populate_workout_table()
        
    def populate_workout_table(self, filtered_workouts=None):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        workouts = filtered_workouts if filtered_workouts is not None else self.user.workouts
        
        workouts = sorted(workouts, key=lambda w: datetime.datetime.strptime(w.date, "%Y-%m-%d"), reverse=True)
        
        if not workouts:
            empty_label = tk.Label(self.scrollable_frame, text="No workouts found", 
                                 font=("Arial", 12), bg="white", fg="#666")
            empty_label.pack(pady=30)
            return
            
        for i, workout in enumerate(workouts):
            row_bg = "#f9f9f9" if i % 2 == 0 else "white"
            row_frame = tk.Frame(self.scrollable_frame, bg=row_bg)
            row_frame.pack(fill=tk.X)
            
            date_label = tk.Label(row_frame, text=workout.date, font=("Arial", 10), 
                                bg=row_bg, width=15, anchor=tk.W)
            date_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
            
            type_label = tk.Label(row_frame, text=workout.workout_type, font=("Arial", 10), 
                                bg=row_bg, width=20, anchor=tk.W)
            type_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)
            
            duration_label = tk.Label(row_frame, text=str(workout.duration), font=("Arial", 10), 
                                    bg=row_bg, width=12, anchor=tk.W)
            duration_label.grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
            
            calories_label = tk.Label(row_frame, text=str(workout.calories_burned), font=("Arial", 10), 
                                    bg=row_bg, width=12, anchor=tk.W)
            calories_label.grid(row=0, column=3, padx=10, pady=10, sticky=tk.W)
            
            actions_frame = tk.Frame(row_frame, bg=row_bg)
            actions_frame.grid(row=0, column=4, padx=10, pady=5, sticky=tk.W)
            
            
            view_button = tk.Button(actions_frame, text="👁️", command=lambda w=workout: self.view_workout(w), 
                                  bg="#2196F3", fg="white", width=2, font=("Arial", 8))
            view_button.pack(side=tk.LEFT, padx=(0, 5))
            
            edit_button = tk.Button(actions_frame, text="✏️", command=lambda w=workout: self.edit_workout(w), 
                                  bg="#FF9800", fg="white", width=2, font=("Arial", 8))
            edit_button.pack(side=tk.LEFT, padx=(0, 5))
            
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
                              bg="#4CAF50", fg="white", font=("Arial", 11),
                              width=10, bd=0, padx=10, pady=5, cursor="hand2")
        save_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=form_window.destroy, 
                                bg="#f44336", fg="white", font=("Arial", 11),
                                width=10, bd=0, padx=10, pady=5, cursor="hand2")
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
        
        # Nutrition advice
        advice_frame = tk.LabelFrame(parent, text="Personalized Nutrition Tips", font=("Arial", 10, "bold"), 
                                   bg="white", padx=10, pady=10)
        advice_frame.pack(fill=tk.X, pady=(20, 5))
        
        # Generate personalized advice based on macro intake
        advice_list = self.generate_nutrition_advice(total_calories, total_proteins, total_carbs, total_fats)
        
        for advice in advice_list:
            tip_row = tk.Frame(advice_frame, bg="white")
            tip_row.pack(fill=tk.X, pady=5)
            
            
            bullet = tk.Label(tip_row, text="•", font=("Arial", 10, "bold"), bg="white")
            bullet.pack(side=tk.LEFT, padx=(0, 5))
            
            tip_text = tk.Label(tip_row, text=advice, font=("Arial", 9), bg="white", 
                              wraplength=250, justify=tk.LEFT)
            tip_text.pack(side=tk.LEFT, fill=tk.X)
    
    def generate_nutrition_advice(self, calories, proteins, carbs, fats):
        """Generate personalized nutrition advice based on user's macro intake"""
        advice = []
        
        # Weight in kg and height in cm used for calculations
        weight_kg = self.user.weight
        height_cm = self.user.height
        age = self.user.age
        gender = self.user.gender
        
        # Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation
        if gender.lower() in ['male', 'm']:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        
        # Assume moderate activity level (PAL 1.55)
        tdee = bmr * 1.55  # Total Daily Energy Expenditure
        
        # Recommended macros distribution (standard values)
        recommended_protein_g = 0.8 * weight_kg  # 0.8g per kg is minimum RDA
        athlete_protein_g = 1.6 * weight_kg      # For active individuals
        
        # For active people who workout regularly
        if len(self.user.workouts) > 0:
            recommended_protein_g = athlete_protein_g
        
        # Macro recommendations (simplified)
        ideal_carbs_pct = 50  # % of calories from carbs
        ideal_protein_pct = 25  # % of calories from protein
        ideal_fats_pct = 25  # % of calories from fat
        
        # Calculate actual percentages if calories exist
        if calories > 0:
            actual_protein_pct = (proteins * 4 / calories) * 100
            actual_carbs_pct = (carbs * 4 / calories) * 100
            actual_fats_pct = (fats * 9 / calories) * 100
            
            # Add advice based on current intake
            
            # Calorie advice
            if calories < tdee * 0.7:
                advice.append("Your calorie intake today appears low. Consider adding healthy snacks to reach your energy needs.")
            elif calories > tdee * 1.2:
                if len(self.user.goals) > 0 and any("weight loss" in g.goal_type.lower() for g in self.user.goals):
                    advice.append("Your calorie intake is relatively high for weight loss. Consider reducing portion sizes slightly.")
            
            # Protein advice
            if proteins < recommended_protein_g:
                advice.append(f"Your protein intake is below recommendations ({recommended_protein_g:.0f}g). Consider adding lean proteins like chicken, fish, tofu, or legumes.")
            elif actual_protein_pct < ideal_protein_pct - 5:
                advice.append("Your protein intake is proportionally low. Try including protein in each meal.")
            
            # Carbs advice
            if actual_carbs_pct > ideal_carbs_pct + 15:
                advice.append("Your carbohydrate intake is higher than recommended. Focus on complex carbs like whole grains and reduce simple sugars.")
            elif actual_carbs_pct < ideal_carbs_pct - 15:
                advice.append("Your carbohydrate intake is low. Complex carbs provide important energy for your workouts.")
            
            # Fats advice
            if actual_fats_pct > ideal_fats_pct + 10:
                advice.append("Your fat intake is relatively high. Focus on healthy fats like avocados, nuts, and olive oil.")
            elif actual_fats_pct < ideal_fats_pct - 10:
                advice.append("Your fat intake is low. Healthy fats are essential for hormone production and vitamin absorption.")
        
        # General advice if not enough data
        if not advice:
            advice = [
                "Aim for a balanced diet with proteins, carbs, and healthy fats.",
                "Stay hydrated by drinking at least 8 glasses of water daily.",
                "Include a variety of fruits and vegetables in your meals.",
                "Limit processed foods and added sugars."
            ]
        
        return advice
        
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
        
        # Use current date as default if adding new, otherwise use meal's date
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        date_var = tk.StringVar(value=meal.date if is_edit else today)
        date_entry = tk.Entry(form_frame, textvariable=date_var, font=("Arial", 10), width=15)
        date_entry.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        date_format_label = tk.Label(form_frame, text="(YYYY-MM-DD)", font=("Arial", 8), fg="#666", bg="white")
        date_format_label.grid(row=0, column=2, sticky=tk.W, pady=10)
        
        # Add date format example for clarity
        date_example = tk.Label(form_frame, text="Example: 2023-10-25", font=("Arial", 7), fg="#888", bg="white")
        date_example.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Meal Type
        type_label = tk.Label(form_frame, text="Meal Type:", font=("Arial", 10, "bold"), bg="white")
        type_label.grid(row=2, column=0, sticky=tk.W, pady=10)
        
        meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
        
        type_var = tk.StringVar(value=meal.meal_type if is_edit else meal_types[0])  # Default to Breakfast
        type_dropdown = ttk.Combobox(form_frame, textvariable=type_var, values=meal_types, width=13)
        type_dropdown.grid(row=2, column=1, sticky=tk.W, pady=10)
        
        # Meal Name
        name_label = tk.Label(form_frame, text="Meal Name:", font=("Arial", 10, "bold"), bg="white")
        name_label.grid(row=3, column=0, sticky=tk.W, pady=10)
        
        name_var = tk.StringVar(value=meal.name if is_edit else "")
        name_entry = tk.Entry(form_frame, textvariable=name_var, font=("Arial", 10), width=20)
        name_entry.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=10)
        
        # Calories
        calories_label = tk.Label(form_frame, text="Calories:", font=("Arial", 10, "bold"), bg="white")
        calories_label.grid(row=4, column=0, sticky=tk.W, pady=10)
        
        calories_var = tk.StringVar(value=meal.calories if is_edit else "")
        calories_entry = tk.Entry(form_frame, textvariable=calories_var, font=("Arial", 10), width=10)
        calories_entry.grid(row=4, column=1, sticky=tk.W, pady=10)
        
        calories_unit = tk.Label(form_frame, text="kcal", font=("Arial", 9), bg="white")
        calories_unit.grid(row=4, column=2, sticky=tk.W, pady=10)
        
        # Protein
        protein_label = tk.Label(form_frame, text="Protein:", font=("Arial", 10, "bold"), bg="white")
        protein_label.grid(row=5, column=0, sticky=tk.W, pady=10)
        
        protein_var = tk.StringVar(value=meal.proteins if is_edit else "")
        protein_entry = tk.Entry(form_frame, textvariable=protein_var, font=("Arial", 10), width=10)
        protein_entry.grid(row=5, column=1, sticky=tk.W, pady=10)
        
        protein_unit = tk.Label(form_frame, text="grams", font=("Arial", 9), bg="white")
        protein_unit.grid(row=5, column=2, sticky=tk.W, pady=10)
        
        # Carbs
        carbs_label = tk.Label(form_frame, text="Carbohydrates:", font=("Arial", 10, "bold"), bg="white")
        carbs_label.grid(row=6, column=0, sticky=tk.W, pady=10)
        
        carbs_var = tk.StringVar(value=meal.carbs if is_edit else "")
        carbs_entry = tk.Entry(form_frame, textvariable=carbs_var, font=("Arial", 10), width=10)
        carbs_entry.grid(row=6, column=1, sticky=tk.W, pady=10)
        
        carbs_unit = tk.Label(form_frame, text="grams", font=("Arial", 9), bg="white")
        carbs_unit.grid(row=6, column=2, sticky=tk.W, pady=10)
        
        # Fats
        fats_label = tk.Label(form_frame, text="Fats:", font=("Arial", 10, "bold"), bg="white")
        fats_label.grid(row=7, column=0, sticky=tk.W, pady=10)
        
        fats_var = tk.StringVar(value=meal.fats if is_edit else "")
        fats_entry = tk.Entry(form_frame, textvariable=fats_var, font=("Arial", 10), width=10)
        fats_entry.grid(row=7, column=1, sticky=tk.W, pady=10)
        
        fats_unit = tk.Label(form_frame, text="grams", font=("Arial", 9), bg="white")
        fats_unit.grid(row=7, column=2, sticky=tk.W, pady=10)
        
        # Buttons - complete rewrite with minimal styling
        button_frame = tk.Frame(form_window, bg="white")
        button_frame.pack(fill=tk.X, padx=20, pady=(15, 20))
        
        # Create simpler buttons with fixed height and width
        save_button = tk.Button(
            button_frame, 
            text="Save", 
            command=lambda: self.save_meal(
                date_var.get(), type_var.get(), name_var.get(),
                calories_var.get(), protein_var.get(), carbs_var.get(), fats_var.get(),
                form_window, meal if is_edit else None
            ), 
            bg="#4CAF50", 
            fg="white",
            font=("Arial", 9),  # Smaller font
            width=8,           # Fixed character width
            height=1,          # Fixed character height
            relief=tk.FLAT,    # Flat relief
            bd=0               # No border
        )
        save_button.pack(side=tk.RIGHT, padx=10)
        
        cancel_button = tk.Button(
            button_frame, 
            text="Cancel", 
            command=form_window.destroy,
            bg="#f44336", 
            fg="white",
            font=("Arial", 9),  # Smaller font
            width=8,           # Fixed character width
            height=1,          # Fixed character height
            relief=tk.FLAT,    # Flat relief 
            bd=0               # No border
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def save_meal(self, date, meal_type, name, calories, proteins, carbs, fats, window, existing_meal=None):
        # Validate inputs
        if not date.strip() or not meal_type.strip() or not name.strip() or not calories or not proteins or not carbs or not fats:
            messagebox.showerror("Error", "All fields are required", parent=window)
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
            
        # Validate date format more carefully
        try:
            # Try to parse the date
            parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            
            # Check if the parsed date makes sense (prevent dates like 2015-25-25)
            if parsed_date.month > 12 or parsed_date.day > 31:
                messagebox.showerror("Error", "Invalid date values. Please use format YYYY-MM-DD with valid month (1-12) and day values", parent=window)
                return
                
            # Use the properly formatted date
            formatted_date = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format (e.g., 2023-10-25)", parent=window)
            return
            
        if existing_meal:
            # Update existing meal
            existing_meal.date = formatted_date
            existing_meal.meal_type = meal_type
            existing_meal.name = name
            existing_meal.calories = calories
            existing_meal.proteins = proteins
            existing_meal.carbs = carbs
            existing_meal.fats = fats
        else:
            # Create new meal
            new_meal = Meal(meal_type, name, calories, proteins, carbs, fats, formatted_date)
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
            
        # Recreate frame components properly
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
        range_dropdown.bind("<<ComboboxSelected>>", self.update_fitness_report) # Re-bind combobox
        
        # Container for report content
        self.fitness_report_frame = tk.Frame(parent, bg="white")
        self.fitness_report_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Initial report
        self.generate_fitness_report()
        
    def update_fitness_report(self, event=None):
        print("DEBUG: update_fitness_report called") # Diagnostic print
        # Clear current report
        for widget in self.fitness_report_frame.winfo_children():
            widget.destroy()
            
        # Generate new report
        self.generate_fitness_report()
        
    def generate_fitness_report(self):
        # Clear current report content first
        for widget in self.fitness_report_frame.winfo_children():
            widget.destroy()

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
            no_data_label = tk.Label(self.fitness_report_frame, text="No workout data found for the selected time range.", 
                                     font=("Arial", 12), fg="#666", bg="white")
            no_data_label.pack(pady=50)
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
        workout_types_data = {}
        for workout in workouts:
            workout_types_data[workout.workout_type] = workout_types_data.get(workout.workout_type, 0) + 1
            
        most_common_type = max(workout_types_data.items(), key=lambda x: x[1])[0] if workout_types_data else "N/A"
        
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
        charts_frame.pack(fill=tk.X, expand=False, pady=(10,0))
        
        # Left chart: Workout type distribution
        left_chart_frame = tk.Frame(charts_frame, bg="white")
        left_chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        left_chart_title = tk.Label(left_chart_frame, text="Workout Types Distribution", 
                                  font=("Arial", 10, "bold"), bg="white")
        left_chart_title.pack(pady=(0, 10))
        
        self.create_pie_chart(left_chart_frame, workout_types_data) # Use workout_types_data
        
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
            no_data.pack(pady=20, padx=10)
            return
            
        # Create matplotlib figure with smaller size
        fig = plt.Figure(figsize=(2.6, 2.2), dpi=75) # Further reduced size
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
            no_data.pack(pady=20, padx=10)
            return
            
        # Create matplotlib figure with smaller size
        fig = plt.Figure(figsize=(2.6, 2.2), dpi=75) # Further reduced size
        ax = fig.add_subplot(111)
        
        # Aggregate calories by date
        calories_by_date = {}
        for workout in workouts:
            date = workout.date
            calories_by_date[date] = calories_by_date.get(date, 0) + workout.calories_burned
            
        # Sort by date
        sorted_dates = sorted(calories_by_date.keys())
        calories = [calories_by_date[date] for date in sorted_dates]
        
        # If too many dates, show only a subset
        if len(sorted_dates) > 10:
            step = len(sorted_dates) // 5
            display_dates = sorted_dates[::step]
            display_indices = [sorted_dates.index(date) for date in display_dates]
            ax.plot(range(len(sorted_dates)), calories, marker='o', linestyle='-', markersize=3)
            ax.set_xticks([i for i in display_indices])
            ax.set_xticklabels([sorted_dates[i] for i in display_indices], rotation=45, fontsize=7)
        else:
            ax.plot(range(len(sorted_dates)), calories, marker='o', linestyle='-', markersize=3)
            ax.set_xticks(range(len(sorted_dates)))
            ax.set_xticklabels(sorted_dates, rotation=45, fontsize=7)
        
        # Format chart
        ax.set_xlabel('Date', fontsize=8)
        ax.set_ylabel('Calories Burned', fontsize=8)
        ax.tick_params(axis='both', labelsize=7)
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
        range_dropdown.bind("<<ComboboxSelected>>", self.update_nutrition_report) # Re-bind combobox
        
        # Container for report content
        self.nutrition_report_frame = tk.Frame(parent, bg="white")
        self.nutrition_report_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Initial report
        self.generate_nutrition_report()
        
    def update_nutrition_report(self, event=None):
        print("DEBUG: update_nutrition_report called") # Diagnostic print
        # Clear current report
        for widget in self.nutrition_report_frame.winfo_children():
            widget.destroy()
            
        # Generate new report
        self.generate_nutrition_report()
        
    def generate_nutrition_report(self):
        # Clear current report content first
        for widget in self.nutrition_report_frame.winfo_children():
            widget.destroy()

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
            no_data_label = tk.Label(self.nutrition_report_frame, text="No meal data found for the selected time range.", 
                                     font=("Arial", 12), fg="#666", bg="white")
            no_data_label.pack(pady=50)
            return
            
        # Summary stats
        summary_frame = tk.LabelFrame(self.nutrition_report_frame, text="Nutrition Summary", 
                                    font=("Arial", 12, "bold"), bg="white", padx=15, pady=15)
        summary_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Calculate summary stats
        total_meals_count = len(meals)
        total_calories_val = sum(m.calories for m in meals)
        total_protein_val = sum(m.proteins for m in meals)
        total_carbs_val = sum(m.carbs for m in meals)
        total_fats_val = sum(m.fats for m in meals)
        
        avg_calories_per_meal = total_calories_val / total_meals_count if total_meals_count > 0 else 0
        # avg_protein_per_meal = total_protein_val / total_meals_count if total_meals_count > 0 else 0 # Not used in original detailed view
        # avg_carbs_per_meal = total_carbs_val / total_meals_count if total_meals_count > 0 else 0 # Not used
        # avg_fats_per_meal = total_fats_val / total_meals_count if total_meals_count > 0 else 0 # Not used

        # Display summary stats
        stats = [
            ("Total Meals:", str(total_meals_count)),
            ("Total Calories:", f"{total_calories_val} kcal"),
            ("Avg. Calories per Meal:", f"{avg_calories_per_meal:.1f} kcal"),
            ("Total Protein:", f"{total_protein_val:.1f} g"),
            ("Total Carbs:", f"{total_carbs_val:.1f} g"),
            ("Total Fats:", f"{total_fats_val:.1f} g")
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
        macros_data = {
            "Protein": total_protein_val * 4 if total_protein_val else 0,  # 4 calories per gram
            "Carbs": total_carbs_val * 4 if total_carbs_val else 0,      # 4 calories per gram
            "Fats": total_fats_val * 9 if total_fats_val else 0         # 9 calories per gram
        }
        # Filter out zero values to prevent pie chart errors
        macros_data = {k: v for k, v in macros_data.items() if v > 0}
        self.create_pie_chart(left_chart_frame, macros_data) # Pass macros_data
        
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
            no_data.pack(pady=20, padx=10)
            return
            
        # Create matplotlib figure with smaller size
        fig = plt.Figure(figsize=(2.6, 2.2), dpi=75) # Further reduced size
        ax = fig.add_subplot(111)
        
        # Aggregate calories by date
        calories_by_date = {}
        for meal in meals:
            date = meal.date
            calories_by_date[date] = calories_by_date.get(date, 0) + meal.calories
            
        # Sort by date
        sorted_dates = sorted(calories_by_date.keys())
        calories = [calories_by_date[date] for date in sorted_dates]
        
        # If too many dates, show only a subset
        if len(sorted_dates) > 10:
            step = len(sorted_dates) // 5
            display_dates = sorted_dates[::step]
            display_indices = [sorted_dates.index(date) for date in display_dates]
            ax.plot(range(len(sorted_dates)), calories, marker='o', linestyle='-', color='orange', markersize=3)
            ax.set_xticks([i for i in display_indices])
            ax.set_xticklabels([sorted_dates[i] for i in display_indices], rotation=45, fontsize=7)
        else:
            ax.plot(range(len(sorted_dates)), calories, marker='o', linestyle='-', color='orange', markersize=3)
            ax.set_xticks(range(len(sorted_dates)))
            ax.set_xticklabels(sorted_dates, rotation=45, fontsize=7)
        
        # Format chart
        ax.set_xlabel('Date', fontsize=8)
        ax.set_ylabel('Calories Consumed', fontsize=8)
        ax.tick_params(axis='both', labelsize=7)
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

# Fix the main function to prevent duplicate windows
def main():
    # Create the main Tkinter window instance FIRST
    root = tk.Tk()

    # Now, apply styling
    try:
        from tkinter import ttk
        style = ttk.Style() # This will now use the existing 'root' if it needs a root context
        style.theme_use('clam')  # 'clam', 'alt', 'default', 'classic'
        
        # Configure ttk styles
        style.configure("TButton", font=("Arial", 10))
        style.configure("TEntry", padding=5)
        style.configure("TCombobox", padding=5)
    except:
        pass  # Continue if styling fails
    
    # Initialize the first screen/mode selector with this root
    app = FitnessModeSelector(root)
    
    # Start the Tkinter event loop
    app.mainloop() # This calls self.root.mainloop() via FitnessModeSelector.mainloop

if __name__ == "__main__":
    main()
