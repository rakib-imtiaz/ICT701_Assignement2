"""
Smart Fitness Management System (SFMS)
ICT701 Assignment 4

Main entry point for the Smart Fitness Management System application.
Launches the mode selector for choosing between GUI and text interfaces.

Author: Emon
Student ID: 20031890
Date: October 2023
"""

import tkinter as tk
import logging
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sfms.log"),
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
    
    # Import here to avoid circular imports
    from cli import FitnessModeSelector
    
    # Initialize the mode selector
    app = FitnessModeSelector(root)
    
    # Start the application main loop
    app.mainloop()


if __name__ == "__main__":
    main() 