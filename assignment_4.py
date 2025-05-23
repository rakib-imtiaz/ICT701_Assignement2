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

# This file serves as a compatibility wrapper around the new modular structure
# It imports from the refactored modules but maintains the original entry point

import tkinter as tk
import logging
import sys

# Import from modular structure
from models import User, Workout, Meal, Goal
from data_manager import DataManager
from cli import FitnessModeSelector, TextInterface

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


def main():
    """
    Main entry point for the application.
    Creates the initial Tkinter window and launches the mode selector.
    """
    logging.info("Starting Smart Fitness Management System")
    
    # Create the Tkinter root window
    root = tk.Tk()
    root.title("Smart Fitness Management System")
    
    # Initialize the mode selector
    app = FitnessModeSelector(root)
    
    # Start the application main loop
    app.mainloop()


if __name__ == "__main__":
    main()
