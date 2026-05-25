"""
Sample Python code with intentional issues for testing the code reviewer.
This file contains various security vulnerabilities, code smells, and style issues.
"""

import os
import pickle
import sqlite3

# Hardcoded credentials (SECURITY ISSUE)
API_KEY = "sk_live_1234567890abcdef"
DATABASE_PASSWORD = "admin123"

# Global variable (CODE SMELL)
global_counter = 0

def unsafe_eval(user_input):
    """Evaluate user input directly - DANGEROUS!"""
    # Using eval with user input (CRITICAL SECURITY ISSUE)
    result = eval(user_input)
    return result

def sql_injection_example(user_id):
    """Example of SQL injection vulnerability."""
    # SQL Injection (CRITICAL SECURITY ISSUE)
    query = "SELECT * FROM users WHERE id = " + user_id
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def command_injection_example(filename):
    """Example of command injection vulnerability."""
    # Command Injection (CRITICAL SECURITY ISSUE)
    os.system("cat " + filename)

def insecure_deserialization(data):
    """Example of insecure deserialization."""
    # Insecure deserialization (HIGH SECURITY ISSUE)
    return pickle.loads(data)

def bare_except_example():
    """Example of bare except clause."""
    try:
        result = 10 / 0
    except:  # Bare except (CODE SMELL)
        pass

def missing_docstring(x, y):
    """Function with missing docstring."""
    return x + y

def too_many_arguments(a, b, c, d, e, f, g, h, i, j):
    """Function with too many arguments."""
    # Too many parameters (CODE SMELL)
    return a + b + c + d + e + f + g + h + i + j

def long_function():
    """This function is too long and should be refactored."""
    # Long function (CODE SMELL)
    x = 1
    y = 2
    z = 3
    a = x + y
    b = y + z
    c = a + b
    d = c * 2
    e = d - 1
    f = e + 10
    g = f * 3
    h = g / 2
    i = h + 5
    j = i - 3
    k = j * 4
    l = k + 7
    m = l / 3
    n = m - 2
    o = n + 8
    p = o * 5
    q = p / 4
    r = q + 1
    s = r - 4
    t = s * 6
    u = t / 5
    v = u + 9
    w = v - 6
    result = w * 7
    return result

class InsecureClass:
    """A class with security issues."""
    
    def __init__(self):
        # Hardcoded secret (SECURITY ISSUE)
        self.secret_key = "my-secret-key-123"
    
    def unsafe_method(self, user_input):
        """Method that uses exec."""
        # Using exec (CRITICAL SECURITY ISSUE)
        exec(user_input)

def unused_variable_example():
    """Example with unused variables."""
    x = 10  # Unused variable
    y = 20
    z = y + 5
    return z

def magic_numbers_example():
    """Example with magic numbers."""
    # Magic numbers (CODE SMELL)
    area = 3.14159 * 10 * 10
    circumference = 2 * 3.14159 * 10
    return area, circumference

def duplicate_code_example1():
    """Example of code duplication."""
    # Duplicate code (CODE SMELL)
    items = [1, 2, 3, 4, 5]
    result = []
    for item in items:
        if item % 2 == 0:
            result.append(item * 2)
    return result

def duplicate_code_example2():
    """Another example of code duplication."""
    # Duplicate code (CODE SMELL)
    items = [1, 2, 3, 4, 5]
    result = []
    for item in items:
        if item % 2 == 0:
            result.append(item * 2)
    return result

if __name__ == "__main__":
    # This should not be in production code
    print("Running test code")
    unsafe_eval("1 + 1")