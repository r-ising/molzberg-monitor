#!/usr/bin/env python3
"""
Molzberg Swim Course Scraper

This script scrapes the Freizeitbad Molzberg website for swim courses,
uses Google Gemini AI to parse the HTML content, and sends email notifications
via Mailjet when new courses are detected.
"""

import json
import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict, Any

import requests
import google.generativeai as genai


class CourseScraperError(Exception):
    """Custom exception for course scraper errors"""
    pass


class CourseScraper:
    """Main class for scraping and managing swim course data"""
    
    def __init__(self, init_gemini=True):
        self.target_url = "https://www.freizeitbad-molzberg.com/anfangerkurs"
        self.state_file = Path("state/known_courses.json")
        if init_gemini:
            self.setup_gemini()
        
    def setup_gemini(self):
        """Initialize Gemini API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise CourseScraperError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def fetch_website_content(self) -> str:
        """Fetch HTML content from the target website"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(self.target_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise CourseScraperError(f"Failed to fetch website content: {e}")
    
    def parse_courses_with_gemini(self, html_content: str) -> List[Dict[str, Any]]:
        """Use Gemini to parse HTML and extract course information"""
        prompt = """
        Please analyze the following HTML content from a swim course website and extract all available swim courses.
        
        Return the result as a valid JSON array containing objects with the following structure:
        [
            {
                "course_id": "",
                "price": "",
                "date_time": "",
                "location": "",
                "participants": "",
                "booking_status": "",
                "booking_link": ""
            }
        ]
        
        Important:
        - The "course_id" field should be a unique identifier extracted from the course (like "KINDERKURS KSK00-00")
        - Extract exact price format including currency symbol (like "10,00 €")
        - Include full date and time information in "date_time" field
        - Include location/pool information in "location" field
        - Extract participant limits in "participants" field
        - Include booking instructions or status in "booking_status" field
        - Include any PDF form links or registration links in "booking_link" field
        - If certain information is not available, use null or an empty string
        - Only return valid JSON, no additional text or explanation
        - Focus on actual swim courses for beginners/anfänger and children/kinder
        - Under no circumstances should you make up data.
        
        HTML Content:
        """ + html_content
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            # Parse JSON
            courses = json.loads(content.strip())
            
            # Validate structure
            if not isinstance(courses, list):
                raise ValueError("Response is not a list")
            
            for course in courses:
                if not isinstance(course, dict) or 'course_id' not in course:
                    raise ValueError("Invalid course structure")
            
            return courses
            
        except (json.JSONDecodeError, ValueError) as e:
            raise CourseScraperError(f"Failed to parse Gemini response: {e}")
        except Exception as e:
            raise CourseScraperError(f"Gemini API error: {e}")
    
    def load_known_courses(self) -> List[Dict[str, Any]]:
        """Load previously known courses from state file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load known courses: {e}")
            return []
    
    def save_known_courses(self, courses: List[Dict[str, Any]]):
        """Save courses to state file"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(courses, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise CourseScraperError(f"Failed to save known courses: {e}")
    
    def find_new_courses(self, current_courses: List[Dict[str, Any]], 
                        known_courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compare current courses with known courses to find new ones"""
        known_ids = {course.get('course_id') for course in known_courses}
        new_courses = []
        
        for course in current_courses:
            course_id = course.get('course_id')
            if course_id and course_id not in known_ids:
                new_courses.append(course)
        
        return new_courses
    
    def send_notification(self, new_courses: List[Dict[str, Any]]):
        """Send email notification via Mailjet SMTP"""
        # Get email configuration from environment
        mailjet_public = os.getenv('MAILJET_API_KEY_PUBLIC')
        mailjet_private = os.getenv('MAILJET_API_KEY_PRIVATE')
        sender_email = os.getenv('MAILJET_SENDER_EMAIL')
        recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        if not all([mailjet_public, mailjet_private, sender_email, recipient_email]):
            raise CourseScraperError("Missing required email configuration environment variables")
        
        # Create email content
        subject = f"🏊 New Swim Courses Available at Freizeitbad Molzberg ({len(new_courses)} found)"
        
        body = "New swim courses have been detected at Freizeitbad Molzberg!\n\n"
        body += f"Website: {self.target_url}\n\n"
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
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Send email via Mailjet SMTP
        try:
            with smtplib.SMTP('in-v3.mailjet.com', 587) as server:
                server.starttls()
                server.login(mailjet_public, mailjet_private)
                server.send_message(msg)
            
            print(f"Email notification sent successfully to {recipient_email}")
            
        except smtplib.SMTPException as e:
            raise CourseScraperError(f"Failed to send email notification: {e}")
    
    def run(self):
        """Main method to run the course scraping process"""
        try:
            print("Starting course scraper...")
            
            # Step 1: Fetch website content
            print("Fetching website content...")
            html_content = self.fetch_website_content()
            print(f"Fetched {len(html_content)} characters of HTML content")
            
            # Step 2: Parse courses with Gemini
            print("Analyzing content with Gemini AI...")
            current_courses = self.parse_courses_with_gemini(html_content)
            print(f"Found {len(current_courses)} courses")
            
            # Step 3: Load known courses
            print("Loading previously known courses...")
            known_courses = self.load_known_courses()
            print(f"Loaded {len(known_courses)} known courses")
            
            # Step 4: Find new courses
            new_courses = self.find_new_courses(current_courses, known_courses)
            print(f"Detected {len(new_courses)} new courses")
            
            # Step 5: Send notification if new courses found
            if new_courses:
                print("Sending email notification...")
                self.send_notification(new_courses)
                
                # Step 6: Update state file only when new course IDs are found
                print("Updating known courses state...")
                self.save_known_courses(current_courses)
                print("State file updated successfully")
            else:
                print("No new courses detected. No notification sent.")
                print("State file not updated (only updates when course IDs change)")
            
            print("Course scraper completed successfully!")
            return len(new_courses) > 0
            
        except CourseScraperError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Entry point for the script"""
    scraper = CourseScraper()
    scraper.run()


if __name__ == "__main__":
    main()