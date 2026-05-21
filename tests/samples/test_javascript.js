/**
 * Sample JavaScript code for testing the AI Code Reviewer.
 * This file contains intentional issues for testing purposes.
 */

// Hardcoded API key (security issue)
const API_KEY = "sk_live_abcdef123456";
const SECRET_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";

// Using var instead of let/const (outdated)
var globalCounter = 0;
var userData = {};

// Console.log in production code
console.log("Application started");
console.log("User data:", userData);

// Using == instead of === (loose equality)
function checkValue(value) {
    if (value == null) {
        return false;
    }
    if (value == "undefined") {
        return false;
    }
    return true;
}

// eval() usage (security risk)
function executeCode(code) {
    return eval(code);
}

// innerHTML usage (XSS risk)
function displayUserInput(input) {
    document.getElementById('output').innerHTML = input;
}

// Missing error handling on promise
function fetchData(url) {
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log(data);
        });
    // No .catch() handler
}

// Async function without await
async function processItems(items) {
    items.forEach(item => {
        console.log(item);
    });
    // No await used in async function
}

// Unused variables
function calculateTotal(prices) {
    var total = 0;
    var taxRate = 0.08;
    var discount = 0.1;
    var unusedVar = 100;
    
    for (var i = 0; i < prices.length; i++) {
        total += prices[i];
    }
    
    return total;
}

// Function with too many parameters
function createUser(name, email, age, address, phone, city, state, zip, country) {
    return {
        name: name,
        email: email,
        age: age,
        address: address,
        phone: phone,
        city: city,
        state: state,
        zip: zip,
        country: country
    };
}

// Callback hell (anti-pattern)
function loadData() {
    getData(function(err, data) {
        if (!err) {
            processData(data, function(err, result) {
                if (!err) {
                    saveData(result, function(err, saved) {
                        if (!err) {
                            console.log("Done");
                        }
                    });
                }
            });
        }
    });
}

// Missing semicolons (style issue)
function missingSemicolons() {
    var x = 1
    var y = 2
    var z = x + y
    return z
}

// Document.write usage (XSS risk)
function writeContent(content) {
    document.write(content);
}

// Function constructor (security risk)
const dynamicFunction = new Function('a', 'b', 'return a + b');

// Long line exceeding 120 characters
var veryLongVariableNameThatExceedsTheRecommendedLineLength = "This is a very long string value that when combined with the variable declaration will definitely exceed the 120 character limit that is commonly recommended for code readability";

// Multiple statements on one line
function badFormatting() { var a = 1; var b = 2; var c = a + b; return c; }

// Potential memory leak
function attachListeners() {
    var element = document.getElementById('myElement');
    element.addEventListener('click', function() {
        console.log('Clicked');
    });
    // Listener never removed
}

// Magic numbers
function calculatePrice(basePrice) {
    return basePrice * 1.08 * 0.9 + 5.99; // What do these numbers mean?
}

// Deeply nested code
function processOrder(order) {
    if (order) {
        if (order.items) {
            if (order.items.length > 0) {
                if (order.customer) {
                    if (order.customer.id) {
                        return true;
                    }
                }
            }
        }
    }
    return false;
}

module.exports = {
    checkValue,
    executeCode,
    displayUserInput,
    fetchData,
    calculateTotal,
    createUser
};