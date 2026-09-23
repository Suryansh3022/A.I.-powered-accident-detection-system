# AI-Powered Accident Detection System

An AI-powered accident detection system that analyzes uploaded images and identifies potential road accidents using Google's Gemini AI. When an accident is detected, the application can display emergency hospital information and send an SMS alert to a configured emergency contact.

## Features

- AI-based accident detection using Google Gemini
- Image upload and analysis through Streamlit
- Emergency hospital information
- SMS alert using Twilio
- Docker support for easy deployment
- Environment-variable based configuration for sensitive credentials
- Automatic cleanup of uploaded files
- Simple and user-friendly web interface

## Tech Stack

- Python
- Streamlit
- Google Gemini API
- Twilio
- Pillow
- Docker
- TOML
- Python-dotenv

## Project Structure

```text
AI-powered-Accident-Detection-System/
│
├── app.py
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
├── config.toml
│
├── config/
│   └── config_manager.py
│
├── services/
│   ├── accident_detector.py
│   ├── hospital_service.py
│   └── sms_service.py
│
└── uploads/
