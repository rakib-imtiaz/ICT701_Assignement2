"""
Smart Fitness Management System (SFMS) - GUI Frames
ICT701 Assignment 4

This module contains the various frame classes for the GUI interface.
Includes frames for profile, workouts, goals, nutrition and reports.

Author: Emon
Student ID: 20031890
Date: October 2023
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging

from data_manager import DataManager
from models import User, Workout, Meal, Goal

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ProfileFrame(tk.Frame):
    """Profile screen UI component"""
    def __init__(self, parent, user, data_manager):
        super().__init__(parent, bg="#f5f7fa")
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        
        # Create a simple placeholder frame for now
        title = tk.Label(self, text="Profile Frame", font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        info = tk.Label(self, text=f"User: {user.name}\nUsername: {user.username}", 
                      font=("Arial", 12))
        info.pack(pady=10)
        
        self.delete_profile = self._delete_profile  # Placeholder for method reference
        
    def _delete_profile(self):
        """Placeholder for profile deletion logic"""
        pass


class WorkoutFrame(tk.Frame):
    """Workout management screen UI component"""
    def __init__(self, parent, user, data_manager):
        super().__init__(parent, bg="#f5f7fa")
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        
        # Create a simple placeholder frame for now
        title = tk.Label(self, text="Workout Frame", font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        info = tk.Label(self, text=f"Total workouts: {len(user.workouts)}", 
                      font=("Arial", 12))
        info.pack(pady=10)


class GoalFrame(tk.Frame):
    """Goal management screen UI component"""
    def __init__(self, parent, user, data_manager):
        super().__init__(parent, bg="#f5f7fa")
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        
        # Create a simple placeholder frame for now
        title = tk.Label(self, text="Goal Frame", font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        info = tk.Label(self, text=f"Total goals: {len(user.goals)}", 
                      font=("Arial", 12))
        info.pack(pady=10)


class NutritionFrame(tk.Frame):
    """Nutrition management screen UI component"""
    def __init__(self, parent, user, data_manager):
        super().__init__(parent, bg="#f5f7fa")
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        
        # Create a simple placeholder frame for now
        title = tk.Label(self, text="Nutrition Frame", font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        info = tk.Label(self, text=f"Total meals logged: {len(user.meals)}", 
                      font=("Arial", 12))
        info.pack(pady=10)


class ReportFrame(tk.Frame):
    """Reports and analytics screen UI component"""
    def __init__(self, parent, user, data_manager):
        super().__init__(parent, bg="#f5f7fa")
        self.parent = parent
        self.user = user
        self.data_manager = data_manager
        
        # Create a simple placeholder frame for now
        title = tk.Label(self, text="Report Frame", font=("Arial", 20, "bold"))
        title.pack(pady=20)
        
        info = tk.Label(self, text=f"Reports for {user.name}", 
                      font=("Arial", 12))
        info.pack(pady=10) 