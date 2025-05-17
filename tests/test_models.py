"""
Unit tests for the SFMS models
Tests the functionality of User, Workout, Meal, and Goal classes
"""

import unittest
import datetime
from models import User, Workout, Meal, Goal


class TestUser(unittest.TestCase):
    """Test cases for User class"""
    
    def test_init(self):
        """Test User initialization"""
        user = User("testuser", "password", "Test User", 25, "Male", 175.0, 70.0)
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.password, "password")
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.age, 25)
        self.assertEqual(user.gender, "Male")
        self.assertEqual(user.height, 175.0)
        self.assertEqual(user.weight, 70.0)
        self.assertEqual(user.goals, [])
        self.assertEqual(user.workouts, [])
        self.assertEqual(user.meals, [])
        
    def test_to_dict(self):
        """Test User to_dict serialization"""
        user = User("testuser", "password", "Test User", 25, "Male", 175.0, 70.0)
        user_dict = user.to_dict()
        
        self.assertEqual(user_dict["username"], "testuser")
        self.assertEqual(user_dict["password"], "password")
        self.assertEqual(user_dict["name"], "Test User")
        self.assertEqual(user_dict["age"], 25)
        self.assertEqual(user_dict["gender"], "Male")
        self.assertEqual(user_dict["height"], 175.0)
        self.assertEqual(user_dict["weight"], 70.0)
        
    def test_from_dict(self):
        """Test User from_dict deserialization"""
        user_dict = {
            "username": "testuser",
            "password": "password",
            "name": "Test User",
            "age": 25,
            "gender": "Male",
            "height": 175.0,
            "weight": 70.0,
            "workouts": [],
            "meals": [],
            "goals": []
        }
        
        user = User.from_dict(user_dict)
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.password, "password")
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.age, 25)
        self.assertEqual(user.gender, "Male")
        self.assertEqual(user.height, 175.0)
        self.assertEqual(user.weight, 70.0)


class TestWorkout(unittest.TestCase):
    """Test cases for Workout class"""
    
    def test_init(self):
        """Test Workout initialization"""
        workout = Workout("Running", 30, 350, "2023-10-15", "Morning run")
        
        self.assertEqual(workout.workout_type, "Running")
        self.assertEqual(workout.duration, 30)
        self.assertEqual(workout.calories_burned, 350)
        self.assertEqual(workout.date, "2023-10-15")
        self.assertEqual(workout.notes, "Morning run")
        
    def test_to_dict(self):
        """Test Workout to_dict serialization"""
        workout = Workout("Running", 30, 350, "2023-10-15", "Morning run")
        workout_dict = workout.to_dict()
        
        self.assertEqual(workout_dict["workout_type"], "Running")
        self.assertEqual(workout_dict["duration"], 30)
        self.assertEqual(workout_dict["calories_burned"], 350)
        self.assertEqual(workout_dict["date"], "2023-10-15")
        self.assertEqual(workout_dict["notes"], "Morning run")
        
    def test_from_dict(self):
        """Test Workout from_dict deserialization"""
        workout_dict = {
            "workout_type": "Running",
            "duration": 30,
            "calories_burned": 350,
            "date": "2023-10-15",
            "notes": "Morning run"
        }
        
        workout = Workout.from_dict(workout_dict)
        
        self.assertEqual(workout.workout_type, "Running")
        self.assertEqual(workout.duration, 30)
        self.assertEqual(workout.calories_burned, 350)
        self.assertEqual(workout.date, "2023-10-15")
        self.assertEqual(workout.notes, "Morning run")


class TestMeal(unittest.TestCase):
    """Test cases for Meal class"""
    
    def test_init(self):
        """Test Meal initialization"""
        meal = Meal("Breakfast", "Oatmeal with fruit", 350, 12, 45, 10, "2023-10-15")
        
        self.assertEqual(meal.meal_type, "Breakfast")
        self.assertEqual(meal.name, "Oatmeal with fruit")
        self.assertEqual(meal.calories, 350)
        self.assertEqual(meal.proteins, 12)
        self.assertEqual(meal.carbs, 45)
        self.assertEqual(meal.fats, 10)
        self.assertEqual(meal.date, "2023-10-15")
        
    def test_to_dict(self):
        """Test Meal to_dict serialization"""
        meal = Meal("Breakfast", "Oatmeal with fruit", 350, 12, 45, 10, "2023-10-15")
        meal_dict = meal.to_dict()
        
        self.assertEqual(meal_dict["meal_type"], "Breakfast")
        self.assertEqual(meal_dict["name"], "Oatmeal with fruit")
        self.assertEqual(meal_dict["calories"], 350)
        self.assertEqual(meal_dict["proteins"], 12)
        self.assertEqual(meal_dict["carbs"], 45)
        self.assertEqual(meal_dict["fats"], 10)
        self.assertEqual(meal_dict["date"], "2023-10-15")
        
    def test_from_dict(self):
        """Test Meal from_dict deserialization"""
        meal_dict = {
            "meal_type": "Breakfast",
            "name": "Oatmeal with fruit",
            "calories": 350,
            "proteins": 12,
            "carbs": 45,
            "fats": 10,
            "date": "2023-10-15"
        }
        
        meal = Meal.from_dict(meal_dict)
        
        self.assertEqual(meal.meal_type, "Breakfast")
        self.assertEqual(meal.name, "Oatmeal with fruit")
        self.assertEqual(meal.calories, 350)
        self.assertEqual(meal.proteins, 12)
        self.assertEqual(meal.carbs, 45)
        self.assertEqual(meal.fats, 10)
        self.assertEqual(meal.date, "2023-10-15")


class TestGoal(unittest.TestCase):
    """Test cases for Goal class"""
    
    def test_init(self):
        """Test Goal initialization"""
        goal = Goal("Weight loss", "Lose 5kg", "2023-12-31", "2023-10-15")
        
        self.assertEqual(goal.goal_type, "Weight loss")
        self.assertEqual(goal.target_value, "Lose 5kg")
        self.assertEqual(goal.deadline, "2023-12-31")
        self.assertEqual(goal.start_date, "2023-10-15")
        self.assertFalse(goal.completed)
        
        # Test default start_date
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        goal2 = Goal("Weight loss", "Lose 5kg", "2023-12-31")
        self.assertEqual(goal2.start_date, today)
        
    def test_to_dict(self):
        """Test Goal to_dict serialization"""
        goal = Goal("Weight loss", "Lose 5kg", "2023-12-31", "2023-10-15")
        goal_dict = goal.to_dict()
        
        self.assertEqual(goal_dict["goal_type"], "Weight loss")
        self.assertEqual(goal_dict["target_value"], "Lose 5kg")
        self.assertEqual(goal_dict["deadline"], "2023-12-31")
        self.assertEqual(goal_dict["start_date"], "2023-10-15")
        self.assertFalse(goal_dict["completed"])
        
    def test_from_dict(self):
        """Test Goal from_dict deserialization"""
        goal_dict = {
            "goal_type": "Weight loss",
            "target_value": "Lose 5kg",
            "deadline": "2023-12-31",
            "start_date": "2023-10-15",
            "completed": True
        }
        
        goal = Goal.from_dict(goal_dict)
        
        self.assertEqual(goal.goal_type, "Weight loss")
        self.assertEqual(goal.target_value, "Lose 5kg")
        self.assertEqual(goal.deadline, "2023-12-31")
        self.assertEqual(goal.start_date, "2023-10-15")
        self.assertTrue(goal.completed)


if __name__ == "__main__":
    unittest.main() 