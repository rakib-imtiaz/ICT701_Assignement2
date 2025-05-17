"""
Unit tests for the DataManager class
Tests the data persistence functionality of the SFMS application
"""

import unittest
import os
import json
import tempfile
from models import User, Workout, Meal, Goal
from data_manager import DataManager


class TestDataManager(unittest.TestCase):
    """Test cases for DataManager class"""
    
    def setUp(self):
        """Set up test environment before each test method"""
        # Create a temporary file for test data
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_filename = self.temp_file.name
        self.temp_file.close()
        
        # Create a test data manager
        self.data_manager = DataManager(data_file=self.temp_filename)
        
        # Create a test user
        self.test_user = User("testuser", "password", "Test User", 25, "Male", 175.0, 70.0)
        
        # Add some test data to the user
        self.test_user.workouts.append(
            Workout("Running", 30, 350, "2023-10-15", "Morning run")
        )
        self.test_user.meals.append(
            Meal("Breakfast", "Oatmeal with fruit", 350, 12, 45, 10, "2023-10-15")
        )
        self.test_user.goals.append(
            Goal("Weight loss", "Lose 5kg", "2023-12-31", "2023-10-15")
        )
        
    def tearDown(self):
        """Clean up after each test method"""
        # Delete the temporary file
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)
    
    def test_add_user(self):
        """Test adding a user to the data manager"""
        # Add the test user
        result = self.data_manager.add_user(self.test_user)
        
        # Verify the result
        self.assertTrue(result)
        self.assertIn("testuser", self.data_manager.users)
        self.assertEqual(self.data_manager.users["testuser"].name, "Test User")
        
        # Verify it was saved to the file
        with open(self.temp_filename, 'r') as f:
            data = json.load(f)
            self.assertIn("testuser", data)
            self.assertEqual(data["testuser"]["name"], "Test User")
    
    def test_add_duplicate_user(self):
        """Test adding a user with an existing username"""
        # Add the test user first
        self.data_manager.add_user(self.test_user)
        
        # Try to add another user with the same username
        duplicate_user = User("testuser", "different", "Another User", 30, "Female", 165.0, 60.0)
        result = self.data_manager.add_user(duplicate_user)
        
        # Verify the result
        self.assertFalse(result)
        self.assertEqual(self.data_manager.users["testuser"].name, "Test User")  # Original user unchanged
    
    def test_update_user(self):
        """Test updating an existing user"""
        # Add the test user first
        self.data_manager.add_user(self.test_user)
        
        # Modify the user and update
        self.test_user.name = "Updated Name"
        self.test_user.age = 26
        result = self.data_manager.update_user(self.test_user)
        
        # Verify the result
        self.assertTrue(result)
        self.assertEqual(self.data_manager.users["testuser"].name, "Updated Name")
        self.assertEqual(self.data_manager.users["testuser"].age, 26)
        
        # Verify it was saved to the file
        with open(self.temp_filename, 'r') as f:
            data = json.load(f)
            self.assertEqual(data["testuser"]["name"], "Updated Name")
            self.assertEqual(data["testuser"]["age"], 26)
    
    def test_update_nonexistent_user(self):
        """Test updating a user that doesn't exist"""
        # Try to update a user without adding it first
        result = self.data_manager.update_user(self.test_user)
        
        # Verify the result
        self.assertFalse(result)
    
    def test_delete_user(self):
        """Test deleting a user"""
        # Add the test user first
        self.data_manager.add_user(self.test_user)
        
        # Delete the user
        result = self.data_manager.delete_user("testuser")
        
        # Verify the result
        self.assertTrue(result)
        self.assertNotIn("testuser", self.data_manager.users)
        
        # Verify it was removed from the file
        with open(self.temp_filename, 'r') as f:
            data = json.load(f)
            self.assertNotIn("testuser", data)
    
    def test_delete_nonexistent_user(self):
        """Test deleting a user that doesn't exist"""
        # Try to delete a user without adding it first
        result = self.data_manager.delete_user("testuser")
        
        # Verify the result
        self.assertFalse(result)
    
    def test_get_user(self):
        """Test retrieving a user by username"""
        # Add the test user first
        self.data_manager.add_user(self.test_user)
        
        # Get the user
        user = self.data_manager.get_user("testuser")
        
        # Verify the result
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.name, "Test User")
        
        # Get a nonexistent user
        nonexistent_user = self.data_manager.get_user("nonexistentuser")
        self.assertIsNone(nonexistent_user)
    
    def test_authenticate_user(self):
        """Test authenticating a user with username and password"""
        # Add the test user first
        self.data_manager.add_user(self.test_user)
        
        # Authenticate with correct credentials
        user = self.data_manager.authenticate_user("testuser", "password")
        
        # Verify the result
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        
        # Authenticate with incorrect password
        user = self.data_manager.authenticate_user("testuser", "wrongpassword")
        self.assertIsNone(user)
        
        # Authenticate with nonexistent username
        user = self.data_manager.authenticate_user("nonexistentuser", "password")
        self.assertIsNone(user)
    
    def test_password_hashing(self):
        """Test that passwords are hashed before storage"""
        # Add the test user
        self.data_manager.add_user(self.test_user)
        
        # Verify the password was hashed
        self.assertNotEqual(self.data_manager.users["testuser"].password, "password")
        
        # Verify authentication still works with the original password
        user = self.data_manager.authenticate_user("testuser", "password")
        self.assertIsNotNone(user)


if __name__ == "__main__":
    unittest.main() 