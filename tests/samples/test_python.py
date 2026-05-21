"""
Sample Python code for testing the AI Code Reviewer.
This file contains intentional issues for testing purposes.
"""

import os
import pickle
import sqlite3

# Hardcoded credentials (security issue)
API_KEY = "sk_live_1234567890abcdef"
DATABASE_PASSWORD = "admin123"

# Global variable (code smell)
global_counter = 0

def process_user_input(user_input):
    # Missing docstring
    # SQL injection vulnerability
    query = "SELECT * FROM users WHERE username = '" + user_input + "'"
    
    # Using eval (security issue)
    result = eval(user_input)
    
    # Bare except (bad practice)
    try:
        data = pickle.loads(user_input)
    except:
        pass
    
    return result

def calculate_sum(numbers):
    # Missing docstring
    # Inefficient algorithm
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    
    # Unused variable
    unused_var = 42
    
    return total

class UserManager:
    # Missing docstring
    def __init__(self):
        self.users = []
    
    def add_user(self, username, password):
        # Missing docstring
        # Storing plain passwords (security issue)
        self.users.append({
            'username': username,
            'password': password
        })
    
    def get_user(self, username):
        # Missing docstring
        for user in self.users:
            if user['username'] == username:
                return user
        return None

def fetch_data(url):
    # Missing docstring
    # Command injection vulnerability
    os.system("curl " + url)
    
    # Missing input validation
    response = ""
    return response

# Long line that exceeds 120 characters - this is intentionally long to test the line length check in the code reviewer
very_long_variable_name = "This is a very long string that when combined with the variable name and assignment operator will exceed the recommended line length limit"

def complex_function(a, b, c, d, e, f):
    # Too many parameters (code smell)
    # High complexity
    result = 0
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        result = a + b + c + d + e + f
                    else:
                        result = a + b + c + d
                else:
                    result = a + b + c
            else:
                result = a + b
        else:
            result = a
    return result

# Multiple statements on one line
def bad_style(): x = 1; y = 2; z = 3; return x + y + z

if __name__ == "__main__":
    # This should not be in production code
    print("Running test code")
    process_user_input("test")