# Smart Fitness Management System (SFMS)

A comprehensive fitness tracking application with both GUI and text-based interfaces. Track workouts, nutrition, set goals, and analyze your fitness progress.

**Author:** Emon  
**Student ID:** 20031890  
**Date:** October 2023

## Features

- **User Profile Management**: Create and manage your fitness profile
- **Workout Tracking**: Log and track different types of workouts
- **Nutrition Monitoring**: Track meals and analyze nutritional intake
- **Goal Setting**: Set fitness goals and track your progress
- **Comprehensive Reports**: Generate fitness and nutrition reports with visual charts
- **Dual Interface**: Choose between a graphical UI or text-based interface

## Installation

1. Ensure you have Python 3.6+ installed
2. Clone this repository or download the source code
3. Install the required dependencies:

```
pip install -r requirements.txt
```

## Dependencies

- tkinter (included with Python)
- matplotlib (for charts and visualizations)
- tkcalendar (optional, for date picker functionality)

## Usage

### Starting the Application

Run the main script to start the application:

```
python main.py
```

This will launch the mode selector screen where you can choose between GUI or Text interface.

### GUI Mode

The GUI mode provides a full-featured interface with:
- Login/registration forms
- Dashboard with user profile information
- Workout tracking and visualization
- Nutrition logging and analysis
- Goal setting and progress tracking
- Reports and performance analytics

### Text Mode

The text mode provides the same functionality through a command-line interface, suitable for:
- Systems without graphical capabilities
- Remote server environments
- Users who prefer keyboard-driven interfaces

## Data Storage

User data is stored in a JSON file (`fitness_data.json`) in the application directory. Passwords are hashed for security.

## Project Structure

```
SFMS/
├── main.py              # Main entry point
├── models.py            # Data models (User, Workout, etc.)
├── data_manager.py      # Data persistence layer
├── cli.py               # Text interface and mode selector
├── gui/
│   ├── __init__.py
│   ├── app.py           # Main GUI application
│   └── frames.py        # GUI components
├── fitness_data.json    # Data storage (created on first run)
├── README.md
└── requirements.txt
```

## Development

To extend the application:

1. Add new features to both GUI and text interfaces
2. Ensure backward compatibility with existing data formats
3. Follow the existing MVC architecture pattern

## License

This project was created for educational purposes as part of ICT701 Assignment 4. 