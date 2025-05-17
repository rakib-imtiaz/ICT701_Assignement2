"""
Smart Fitness Management System (SFMS) - Data Management
ICT701 Assignment 4

This module handles data persistence for the SFMS application.
Manages loading and saving user data via JSON files.

Author: Emon
Student ID: 20031890
Date: October 2023
"""

import json
import os
import logging
import hashlib
from models import User, Workout, Meal, Goal

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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
        """Load user data from JSON file with improved error handling"""
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
                    logging.info(f"Successfully loaded data for {len(self.users)} users from {self.data_file}")
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {self.data_file}: {e}")
                self.users = {}
                # Create backup of corrupted file
                if os.path.getsize(self.data_file) > 0:
                    backup_file = f"{self.data_file}.bak"
                    try:
                        os.rename(self.data_file, backup_file)
                        logging.info(f"Created backup of corrupted data file: {backup_file}")
                    except OSError as e:
                        logging.error(f"Failed to create backup file: {e}")
            except FileNotFoundError:
                logging.warning(f"Data file {self.data_file} not found, starting with empty database")
                self.users = {}
            except Exception as e:
                logging.error(f"Unexpected error loading data: {e}")
                self.users = {}
        else:
            logging.info(f"Data file {self.data_file} does not exist, starting with empty database")
            self.users = {}
                
    def save_data(self):
        """Save user data to JSON file with error handling and backup"""
        # Create backup of current file if it exists
        if os.path.exists(self.data_file):
            try:
                backup_file = f"{self.data_file}.bak"
                with open(self.data_file, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
                logging.info(f"Created backup of data file: {backup_file}")
            except Exception as e:
                logging.error(f"Failed to create backup before saving: {e}")
        
        try:
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
                
            logging.info(f"Successfully saved data for {len(self.users)} users to {self.data_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving data: {e}")
            return False
            
    def add_user(self, user):
        """Add a new user to the database"""
        if user.username in self.users:
            logging.warning(f"Failed to add user: Username {user.username} already exists")
            return False  # User already exists
            
        # Hash the password before storage
        user.password = self._hash_password(user.password)
        self.users[user.username] = user
        success = self.save_data()
        if success:
            logging.info(f"Added new user: {user.username}")
        return success
        
    def update_user(self, user):
        """Update an existing user in the database"""
        if user.username not in self.users:
            logging.warning(f"Failed to update user: Username {user.username} not found")
            return False  # User doesn't exist
            
        # If password has changed (not a hash), hash it before storage
        current_user = self.users[user.username]
        if user.password != current_user.password and not self._is_hashed(user.password):
            user.password = self._hash_password(user.password)
            
        self.users[user.username] = user
        success = self.save_data()
        if success:
            logging.info(f"Updated user: {user.username}")
        return success
        
    def delete_user(self, username):
        """Delete a user from the database"""
        if username not in self.users:
            logging.warning(f"Failed to delete user: Username {username} not found")
            return False  # User doesn't exist
        del self.users[username]
        success = self.save_data()
        if success:
            logging.info(f"Deleted user: {username}")
        return success
    
    def get_user(self, username):
        """Retrieve a user by username"""
        return self.users.get(username)
    
    def authenticate_user(self, username, password):
        """Authenticate a user with username and password"""
        user = self.get_user(username)
        if not user:
            logging.warning(f"Authentication failed: Username {username} not found")
            return None
            
        # Check if the password is already hashed (for backward compatibility)
        if self._is_hashed(user.password):
            # Hash the provided password and compare
            hashed_password = self._hash_password(password)
            if user.password == hashed_password:
                logging.info(f"User authenticated: {username}")
                return user
        else:
            # Plain text comparison (legacy support)
            if user.password == password:
                # Update to hashed password for future logins
                user.password = self._hash_password(password)
                self.update_user(user)
                logging.info(f"User authenticated (password upgraded to hash): {username}")
                return user
                
        logging.warning(f"Authentication failed: Invalid password for {username}")
        return None
        
    def _hash_password(self, password):
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def _is_hashed(self, password):
        """Check if a password appears to be hashed"""
        # SHA-256 hashes are 64 characters long and hexadecimal
        if len(password) == 64:
            try:
                int(password, 16)  # Check if it's valid hexadecimal
                return True
            except ValueError:
                pass
        return False 