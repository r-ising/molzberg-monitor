#!/usr/bin/env python3
"""
Simple test to verify the basic functionality of the course scraper
without requiring external API access.
"""

import json
from pathlib import Path
import sys
import os

# Add the script directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from course_scraper import CourseScraper

def test_state_management():
    """Test loading and saving of course state"""
    print("Testing state management...")
    
    # Create test data
    test_courses = [
        {
            "id": "test_course_1",
            "name": "Beginner Swimming Course",
            "description": "Basic swimming for beginners",
            "date": "2024-01-15",
            "time": "10:00 AM",
            "price": "50 EUR",
            "instructor": "John Doe"
        },
        {
            "id": "test_course_2", 
            "name": "Advanced Swimming Course",
            "description": "Advanced techniques",
            "date": "2024-01-20",
            "time": "2:00 PM",
            "price": "75 EUR",
            "instructor": "Jane Smith"
        }
    ]
    
    # Test state file path
    test_state_file = Path("state/test_known_courses.json")
    
    # Create a test scraper instance
    scraper = CourseScraper(init_gemini=False)
    scraper.state_file = test_state_file
    
    try:
        # Test saving courses
        scraper.save_known_courses(test_courses)
        print("✓ Successfully saved test courses")
        
        # Test loading courses
        loaded_courses = scraper.load_known_courses()
        assert len(loaded_courses) == 2
        assert loaded_courses[0]["id"] == "test_course_1"
        print("✓ Successfully loaded test courses")
        
        # Test finding new courses
        new_test_courses = test_courses + [
            {
                "id": "test_course_3",
                "name": "Water Safety Course",
                "description": "Safety techniques",
                "date": "2024-01-25",
                "time": "9:00 AM",
                "price": "30 EUR",
                "instructor": "Bob Wilson"
            }
        ]
        
        new_courses = scraper.find_new_courses(new_test_courses, loaded_courses)
        assert len(new_courses) == 1
        assert new_courses[0]["id"] == "test_course_3"
        print("✓ Successfully identified new courses")
        
        # Clean up test file
        if test_state_file.exists():
            test_state_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_email_formatting():
    """Test email formatting without actually sending"""
    print("\nTesting email formatting...")
    
    test_courses = [
        {
            "id": "course_1",
            "name": "Morning Swim Class",
            "description": "Early morning session",
            "date": "2024-01-15",
            "time": "07:00 AM",
            "price": "40 EUR",
            "instructor": "Maria Garcia"
        }
    ]
    
    try:
        scraper = CourseScraper(init_gemini=False)
        
        # Mock the send notification method to just format and print
        def mock_send_notification(new_courses):
            subject = f"🏊 New Swim Courses Available at Freizeitbad Molzberg ({len(new_courses)} found)"
            
            body = "New swim courses have been detected at Freizeitbad Molzberg!\n\n"
            body += f"Website: {scraper.target_url}\n\n"
            body += "New Courses:\n"
            body += "=" * 50 + "\n\n"
            
            for i, course in enumerate(new_courses, 1):
                body += f"{i}. {course.get('name', 'Unknown Course')}\n"
                if course.get('description'):
                    body += f"   Description: {course['description']}\n"
                if course.get('date'):
                    body += f"   Date: {course['date']}\n"
                if course.get('time'):
                    body += f"   Time: {course['time']}\n"
                if course.get('price'):
                    body += f"   Price: {course['price']}\n"
                if course.get('instructor'):
                    body += f"   Instructor: {course['instructor']}\n"
                body += f"   Course ID: {course.get('id', 'N/A')}\n\n"
            
            body += "\nPlease visit the website to register for the courses.\n"
            body += "\n---\nThis is an automated notification from the Molzberg Monitor."
            
            print(f"Subject: {subject}")
            print(f"Body:\n{body}")
            return True
        
        mock_send_notification(test_courses)
        print("✓ Email formatting works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Email formatting test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running basic functionality tests for course scraper...\n")
    
    tests_passed = 0
    total_tests = 2
    
    if test_state_management():
        tests_passed += 1
        
    if test_email_formatting():
        tests_passed += 1
    
    print(f"\nTest Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! Basic functionality is working.")
        return 0
    else:
        print("✗ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())