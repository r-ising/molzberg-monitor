# molzberg-monitor

An automated daily swim course monitoring system for Freizeitbad Molzberg.

## Overview

This project automatically scrapes the [Freizeitbad Molzberg website](https://www.freizeitbad-molzberg.com/anfangerkurs) daily to detect new swim courses and sends email notifications when new courses are found.

## Features

- **Daily Automated Scraping**: Runs every day at 8:00 AM UTC via GitHub Actions
- **AI-Powered Parsing**: Uses Google Gemini API to intelligently parse HTML content and extract course information
- **Smart Change Detection**: Tracks previously seen courses and only notifies about new ones
- **Email Notifications**: Sends detailed email notifications via Mailjet when new courses are detected
- **State Management**: Automatically maintains course state in the repository
- **Manual Triggering**: Can be run manually via GitHub Actions UI

## Setup

### 1. Required GitHub Secrets

Configure the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

- `GEMINI_API_KEY`: Your Google Gemini API key (get it from [Google AI Studio](https://makersuite.google.com/app/apikey))
- `MAILJET_API_KEY_PUBLIC`: Your Mailjet public API key
- `MAILJET_API_KEY_PRIVATE`: Your Mailjet private API key
- `MAILJET_SENDER_EMAIL`: The verified email address to send notifications from
- `RECIPIENT_EMAIL`: The email address to receive notifications

### 2. Mailjet Setup

1. Create a free account at [Mailjet](https://www.mailjet.com/)
2. Verify your sender email address in Mailjet
3. Get your API keys from the Mailjet dashboard
4. Add the API keys and email addresses to GitHub Secrets

### 3. Google Gemini API Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add the API key to GitHub Secrets as `GEMINI_API_KEY`

## How It Works

1. **Scheduled Execution**: GitHub Actions runs the scraper daily at 8:00 AM UTC
2. **Website Scraping**: Fetches HTML content from the Freizeitbad Molzberg anfängerkurs page
3. **AI Analysis**: Google Gemini API analyzes the HTML and extracts structured course data
4. **Change Detection**: Compares new courses against the stored state in `state/known_courses.json`
5. **Notification**: If new courses are found, sends an email via Mailjet
6. **State Update**: Updates the known courses state and commits it back to the repository

## Manual Usage

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_gemini_api_key"
export MAILJET_API_KEY_PUBLIC="your_mailjet_public_key"
export MAILJET_API_KEY_PRIVATE="your_mailjet_private_key"
export MAILJET_SENDER_EMAIL="your_verified_sender@example.com"
export RECIPIENT_EMAIL="recipient@example.com"

# Run the scraper
python course_scraper.py
```

### Running Tests

```bash
# Run basic functionality tests
python test_basic_functionality.py
```

### Manual Trigger via GitHub Actions

1. Go to the "Actions" tab in your GitHub repository
2. Select "Daily Swim Course Checker" workflow
3. Click "Run workflow" and choose the branch

## Project Structure

```
molzberg-monitor/
├── .github/workflows/
│   └── course_checker.yml      # GitHub Actions workflow
├── state/
│   └── known_courses.json      # Stored course state (auto-managed)
├── course_scraper.py           # Main scraper script
├── test_basic_functionality.py # Basic tests
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Email Notification Format

When new courses are detected, you'll receive an email with:

- Subject: "🏊 New Swim Courses Available at Freizeitbad Molzberg (X found)"
- Detailed information for each new course including:
  - Course name
  - Description (if available)
  - Date and time (if available)
  - Price (if available)
  - Instructor (if available)
  - Unique course ID

## Troubleshooting

### No Email Received

1. Check that all GitHub Secrets are correctly configured
2. Verify your sender email is properly verified in Mailjet
3. Check the GitHub Actions logs for any error messages
4. Ensure your Mailjet account is active and has sending quota

### Script Errors

1. Check the GitHub Actions logs under the "Actions" tab
2. Verify that all required secrets are set
3. Ensure your Gemini API key is valid and has quota remaining

### State File Issues

The `state/known_courses.json` file is automatically managed. If you need to reset it:

1. Delete the file content and replace with `[]`
2. Commit the change - the next run will treat all courses as new

## Contributing

This is a personal monitoring tool, but feel free to fork and adapt it for your own use cases.

## License

This project is provided as-is for personal use.