/**
 * Sample JavaScript code with intentional issues for testing the code reviewer.
 * This file contains various security vulnerabilities, code smells, and style issues.
 */

// Hardcoded credentials (SECURITY ISSUE)
const API_KEY = "sk_live_1234567890abcdef";
const SECRET_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";

// Using var instead of let/const (CODE SMELL)
var globalCounter = 0;
var unusedVariable = "I'm not used";

// Eval usage (CRITICAL SECURITY ISSUE)
function unsafeEval(userInput) {
    return eval(userInput);
}

// InnerHTML usage (XSS RISK)
function setHTML(elementId, userContent) {
    document.getElementById(elementId).innerHTML = userContent;
}

// SQL Injection pattern in string (if used with backend)
const query = "SELECT * FROM users WHERE id = " + userId;

// Console.log in production code (CODE SMELL)
console.log("Debug message that should be removed");
console.warn("Another debug message");

// Missing error handling on Promise
fetch('/api/data')
    .then(response => response.json())
    .then(data => console.log(data));
// No .catch() handler

// Async function without await
async function fetchData() {
    fetch('/api/users');
    // Missing await
    return "done";
}

// Loose equality operators (CODE SMELL)
function checkValue(val) {
    if (val == 0) {
        return "zero";
    }
    if (val == false) {
        return "false";
    }
    if (val == "") {
        return "empty";
    }
    return val;
}

// Multiple issues in one function
function problematicFunction(input) {
    var result = eval(input);
    console.log(result);
    document.getElementById('output').innerHTML = result;
    
    if (result == null) {
        return undefined;
    }
    
    return result;
}

// Missing semicolons (STYLE ISSUE)
const missingSemicolon = "test"
const anotherMissing = "test2"

// Long line (STYLE ISSUE)
const veryLongLineThatExceedsRecommendedLength = "This is a very long string that should be broken into multiple lines for better readability and maintainability of the code";

// Magic numbers (CODE SMELL)
function calculateArea(radius) {
    return 3.14159 * radius * radius;
}

function calculateTax(amount) {
    return amount * 0.08;
}

// Deeply nested code (COMPLEXITY ISSUE)
function nestedCode(data) {
    if (data) {
        for (let i = 0; i < data.length; i++) {
            if (data[i].active) {
                for (let j = 0; j < data[i].items.length; j++) {
                    if (data[i].items[j].valid) {
                        if (data[i].items[j].value > 0) {
                            console.log(data[i].items[j].value);
                        }
                    }
                }
            }
        }
    }
}

// Duplicate code blocks (CODE SMELL)
function processUser1(users) {
    const activeUsers = [];
    for (let i = 0; i < users.length; i++) {
        if (users[i].isActive) {
            activeUsers.push(users[i]);
        }
    }
    return activeUsers;
}

function processUser2(users) {
    const activeUsers = [];
    for (let i = 0; i < users.length; i++) {
        if (users[i].isActive) {
            activeUsers.push(users[i]);
        }
    }
    return activeUsers;
}

// Unsafe function constructor (SECURITY ISSUE)
const dynamicFunction = new Function('a', 'b', 'return a + b');

// Document.write (XSS RISK)
function writeContent(content) {
    document.write(content);
}

// Command injection via shell (if used with Node.js)
const { exec } = require('child_process');
function runCommand(userCommand) {
    exec(userCommand, (error, stdout, stderr) => {
        console.log(stdout);
    });
}

// Unhandled promise rejection
Promise.resolve().then(() => {
    throw new Error('Unhandled error');
});

// Memory leak pattern
function createListener() {
    const element = document.getElementById('myElement');
    element.addEventListener('click', function handler() {
        // This creates a closure that prevents garbage collection
        const largeData = new Array(1000000).fill('data');
        console.log(largeData);
    });
    // Never removes event listener
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        unsafeEval,
        setHTML,
        checkValue,
        calculateArea
    };
}