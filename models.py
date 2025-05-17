"""
Smart Fitness Management System (SFMS) - Models
ICT701 Assignment 4

This module contains the data models used throughout the application:
- User: Stores user profile and fitness data
- Workout: Tracks individual workout sessions
- Meal: Stores nutrition information
- Goal: Tracks fitness and health goals

Author: Emon
Student ID: 20031890
Date: October 2023
"""

import datetime


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
        """Convert user object to dictionary for JSON serialization"""
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
        """Create user object from dictionary data (deserialization)"""
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
        """Convert workout object to dictionary for JSON serialization"""
        return {
            'workout_type': self.workout_type,
            'duration': self.duration,
            'calories_burned': self.calories_burned,
            'date': self.date,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create workout object from dictionary data (deserialization)"""
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
        """Convert meal object to dictionary for JSON serialization"""
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
        """Create meal object from dictionary data (deserialization)"""
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
        """Convert goal object to dictionary for JSON serialization"""
        return {
            'goal_type': self.goal_type,
            'target_value': self.target_value,
            'deadline': self.deadline,
            'start_date': self.start_date,
            'completed': self.completed
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create goal object from dictionary data (deserialization)"""
        goal = cls(
            data['goal_type'],
            data['target_value'],
            data['deadline'],
            data.get('start_date')
        )
        goal.completed = data.get('completed', False)
        return goal 