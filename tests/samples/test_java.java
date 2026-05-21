/**
 * Sample Java code for testing the AI Code Reviewer.
 * This file contains intentional issues for testing purposes.
 */

import java.sql.*;
import java.util.*;
import java.io.*;

// Class naming convention violation (should be TestJavaSamples)
public class test_java {
    
    // Hardcoded credentials
    private static final String DB_PASSWORD = "admin123";
    private static final String API_KEY = "sk_live_abcdef123456";
    
    // Uninitialized variable
    private String userName;
    private int userAge;
    
    // Public mutable static field
    public static List<String> globalList = new ArrayList<>();
    
    // Missing docstring
    public void processUserInput(String input) {
        // SQL injection vulnerability
        String query = "SELECT * FROM users WHERE name = '" + input + "'";
        
        try {
            Statement stmt = connection.createStatement();
            ResultSet rs = stmt.executeQuery(query);
        } catch (SQLException e) {
            // Empty catch block
        }
    }
    
    // Missing docstring
    public Object deserializeObject(byte[] data) {
        // Insecure deserialization
        try {
            ByteArrayInputStream bis = new ByteArrayInputStream(data);
            ObjectInputStream ois = new ObjectInputStream(bis);
            return ois.readObject();
        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        }
        return null;
    }
    
    // Command injection vulnerability
    public void runCommand(String userCommand) {
        try {
            Runtime.getRuntime().exec(userCommand);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    // Too many parameters
    public User createUser(String name, String email, int age, String address, 
                          String phone, String city, String state, String zip) {
        return new User(name, email, age, address, phone, city, state, zip);
    }
    
    // Long method (should be refactored)
    public void processOrder(Order order) {
        // This method is intentionally long
        if (order != null) {
            if (order.getItems() != null) {
                if (!order.getItems().isEmpty()) {
                    double total = 0;
                    for (OrderItem item : order.getItems()) {
                        if (item.getPrice() > 0) {
                            total += item.getPrice() * item.getQuantity();
                        }
                    }
                    if (total > 0) {
                        if (order.getCustomer() != null) {
                            if (order.getCustomer().getId() != null) {
                                // Apply discount
                                if (order.getCustomer().isPremium()) {
                                    total = total * 0.9;
                                }
                                // Add tax
                                total = total * 1.08;
                                // Add shipping
                                total = total + 5.99;
                                order.setTotal(total);
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Missing null check
    public String getUserName(User user) {
        return user.getName().toUpperCase(); // Potential NPE
    }
    
    // Catching generic Exception
    public void riskyOperation() {
        try {
            // Various operations
            throw new RuntimeException("Test");
        } catch (Exception e) {
            // Too broad catch
        }
    }
    
    // Using raw types
    public void processList(List items) {
        for (Object item : items) {
            System.out.println(item);
        }
    }
    
    // Magic numbers
    public double calculatePrice(double basePrice) {
        return basePrice * 1.08 * 0.9 + 5.99;
    }
    
    // Thread safety issue
    private static int counter = 0;
    
    public void incrementCounter() {
        counter++; // Not thread-safe
    }
    
    // Resource leak
    public String readFile(String path) throws IOException {
        FileInputStream fis = new FileInputStream(path);
        byte[] data = new byte[fis.available()];
        fis.read(data);
        // Stream not closed
        return new String(data);
    }
    
    // Inner class should be static
    public class InnerClass {
        private int value;
        
        public int getValue() {
            return value;
        }
    }
    
    // Overly broad visibility
    public static void main(String[] args) {
        test_java app = new test_java();
        app.processUserInput("test");
    }
}

// Helper classes
class User {
    private String name;
    private String email;
    private int age;
    private String address;
    private String phone;
    private String city;
    private String state;
    private String zip;
    
    public User(String name, String email, int age, String address, 
                String phone, String city, String state, String zip) {
        this.name = name;
        this.email = email;
        this.age = age;
        this.address = address;
        this.phone = phone;
        this.city = city;
        this.state = state;
        this.zip = zip;
    }
    
    public String getName() { return name; }
    public String getEmail() { return email; }
    public int getAge() { return age; }
    public boolean isPremium() { return age > 65; }
    public Long getId() { return 1L; }
}

class Order {
    private List<OrderItem> items;
    private User customer;
    private double total;
    
    public List<OrderItem> getItems() { return items; }
    public User getCustomer() { return customer; }
    public double getTotal() { return total; }
    public void setTotal(double total) { this.total = total; }
}

class OrderItem {
    private double price;
    private int quantity;
    
    public double getPrice() { return price; }
    public int getQuantity() { return quantity; }
}