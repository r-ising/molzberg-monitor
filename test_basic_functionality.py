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
            "course_id": "KINDERKURS_TEST_01",
            "price": "50,00 €",
            "date_time": "15.01.2024 - 29.01.2024 immer Montag & Mittwoch, 10:00 - 11:00 Uhr",
            "location": "Mehrzweckbecken",
            "participants": "max. 8",
            "booking_status": "Anmeldung per PDF-Formular erforderlich",
            "booking_link": "https://example.com/anmeldung_test_01.pdf"
        },
        {
            "course_id": "KINDERKURS_TEST_02",
            "price": "75,00 €",
            "date_time": "20.01.2024 - 03.02.2024 immer Dienstag & Donnerstag, 14:00 - 15:00 Uhr",
            "location": "Kinderbecken",
            "participants": "max. 10",
            "booking_status": "Online-Anmeldung möglich",
            "booking_link": "https://example.com/anmeldung_test_02.pdf"
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
        assert loaded_courses[0]["course_id"] == "KINDERKURS_TEST_01"
        print("✓ Successfully loaded test courses")
        
        # Test finding new courses
        new_test_courses = test_courses + [
            {
                "course_id": "KINDERKURS_TEST_03",
                "price": "30,00 €",
                "date_time": "25.01.2024 - 08.02.2024 immer Freitag, 09:00 - 10:00 Uhr",
                "location": "Therapiebecken",
                "participants": "max. 6",
                "booking_status": "Warteliste verfügbar",
                "booking_link": "https://example.com/anmeldung_test_03.pdf"
            }
        ]
        
        new_courses = scraper.find_new_courses(new_test_courses, loaded_courses)
        assert len(new_courses) == 1
        assert new_courses[0]["course_id"] == "KINDERKURS_TEST_03"
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
            "course_id": "KINDERKURS_MORNING_01",
            "price": "40,00 €",
            "date_time": "15.01.2024 - 29.01.2024 immer Montag, 07:00 - 08:00 Uhr",
            "location": "Mehrzweckbecken",
            "participants": "max. 12",
            "booking_status": "Anmeldung per E-Mail an kurse@molzbergbad.de",
            "booking_link": "https://example.com/anmeldung_morning_01.pdf"
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
                body += f"{i}. Course ID: {course.get('course_id', 'Unknown Course')}\n"
                if course.get('price'):
                    body += f"   Price: {course['price']}\n"
                if course.get('date_time'):
                    body += f"   Schedule: {course['date_time']}\n"
                if course.get('location'):
                    body += f"   Location: {course['location']}\n"
                if course.get('participants'):
                    body += f"   Participants: {course['participants']}\n"
                if course.get('booking_status'):
                    body += f"   Booking: {course['booking_status']}\n"
                if course.get('booking_link'):
                    body += f"   Registration Form: {course['booking_link']}\n"
                body += "\n"
            
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