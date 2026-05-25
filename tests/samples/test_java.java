/**
 * Sample Java code with intentional issues for testing the code reviewer.
 * This file contains various security vulnerabilities, code smells, and style issues.
 */

import java.sql.*;
import java.util.*;
import java.io.*;

public class test_java {
    
    // Hardcoded credentials (SECURITY ISSUE)
    private static final String DB_PASSWORD = "admin123";
    private static final String API_KEY = "sk_live_1234567890abcdef";
    
    // Public mutable static field (CODE SMELL)
    public static int globalCounter = 0;
    
    // Unused import would be here if we had one
    
    // Missing class documentation
    class InnerClass {
        // Empty class
    }
    
    // SQL Injection vulnerability (CRITICAL SECURITY ISSUE)
    public ResultSet sqlInjectionExample(Connection conn, String userId) throws SQLException {
        String query = "SELECT * FROM users WHERE id = " + userId;
        Statement stmt = conn.createStatement();
        return stmt.executeQuery(query);
    }
    
    // Command Injection vulnerability (CRITICAL SECURITY ISSUE)
    public void commandInjectionExample(String userPath) throws Exception {
        Runtime runtime = Runtime.getRuntime();
        runtime.exec("cat " + userPath);
    }
    
    // Missing null check (LOGIC ERROR)
    public String getValue(Optional<String> optional) {
        return optional.get().toUpperCase();
    }
    
    // Uninitialized variable (LOGIC ERROR)
    public void uninitializedVariable() {
        int x;
        int y;
        // Using without initialization
        System.out.println(x);
    }
    
    // Long method (CODE SMELL)
    public void longMethod() {
        int a = 1;
        int b = 2;
        int c = 3;
        int d = a + b;
        int e = b + c;
        int f = d + e;
        int g = f * 2;
        int h = g - 1;
        int i = h + 10;
        int j = i * 3;
        int k = j / 2;
        int l = k + 5;
        int m = l - 3;
        int n = m * 4;
        int o = n + 7;
        int p = o / 3;
        int q = p - 2;
        int r = q + 8;
        int s = r * 5;
        int t = s / 4;
        int u = t + 1;
        int v = u - 4;
        int w = v * 6;
        System.out.println(w);
    }
    
    // Too many parameters (CODE SMELL)
    public void tooManyParameters(int a, int b, int c, int d, int e, 
                                  int f, int g, int h, int i, int j) {
        System.out.println(a + b + c + d + e + f + g + h + i + j);
    }
    
    // Empty catch block (CODE SMELL)
    public void emptyCatch() {
        try {
            int result = 10 / 0;
        } catch (ArithmeticException e) {
            // Empty catch
        }
    }
    
    // Catching generic Exception (CODE SMELL)
    public void genericCatch() {
        try {
            int result = 10 / 0;
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    // Magic numbers (CODE SMELL)
    public double calculateArea(double radius) {
        return 3.14159 * radius * radius;
    }
    
    public double calculateTax(double amount) {
        return amount * 0.08;
    }
    
    // Deeply nested code (COMPLEXITY ISSUE)
    public void nestedCode(List<List<List<Integer>>> data) {
        for (List<List<Integer>> outer : data) {
            for (List<Integer> middle : outer) {
                for (Integer inner : middle) {
                    if (inner > 0) {
                        if (inner < 100) {
                            if (inner % 2 == 0) {
                                System.out.println(inner);
                            }
                        }
                    }
                }
            }
        }
    }
    
    // Duplicate code blocks (CODE SMELL)
    public List<Integer> filterEven1(List<Integer> numbers) {
        List<Integer> result = new ArrayList<>();
        for (Integer num : numbers) {
            if (num % 2 == 0) {
                result.add(num);
            }
        }
        return result;
    }
    
    public List<Integer> filterEven2(List<Integer> numbers) {
        List<Integer> result = new ArrayList<>();
        for (Integer num : numbers) {
            if (num % 2 == 0) {
                result.add(num);
            }
        }
        return result;
    }
    
    // Missing override annotation
    public String toString() {
        return "test_java";
    }
    
    // Non-private final static field (SECURITY ISSUE - could be exploited via reflection)
    public static final String SECRET = "my-secret-key";
    
    // Insecure random (SECURITY ISSUE)
    public int generateToken() {
        Random random = new Random();
        return random.nextInt();
    }
    
    // Resource leak (CODE SMELL)
    public void resourceLeak() throws Exception {
        FileInputStream fis = new FileInputStream("file.txt");
        // Never closed
        int data = fis.read();
        System.out.println(data);
    }
    
    // Synchronization on non-final field (CODE SMELL)
    private Object lock = new Object();
    
    public void synchronizedMethod() {
        synchronized (lock) {
            System.out.println("Synchronized");
        }
    }
    
    // Cloneable without proper implementation (CODE SMELL)
    class BadClone implements Cloneable {
        @Override
        protected Object clone() throws CloneNotSupportedException {
            return super.clone();
        }
    }
    
    // Finalize method (DEPRECATED)
    @Override
    protected void finalize() throws Throwable {
        super.finalize();
    }
    
    // Main method for testing
    public static void main(String[] args) {
        System.out.println("Test Java code with issues");
    }
}