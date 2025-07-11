# Auto Email Responder Frontend

## Overview

This is the frontend for the Auto Email Responder application. It provides a user interface for interacting with the backend API to manage emails, policies, and system settings.

## Files

- `index.html`: The main HTML file containing the UI structure and styling
- `api.js`: JavaScript module for API integration with the backend
- `app.js`: JavaScript for UI interactions and event handling

## Features

- **Dashboard**: View system statistics and recent activity
- **Inbox**: View, process, and respond to emails
- **Compose**: Send single emails or process batch emails
- **Policies**: Add, search, and manage company policies
- **Settings**: Configure system settings and view system status

## Setup

1. Ensure the backend API is running (default: http://localhost:8000)
2. Open `index.html` in a web browser

## API Integration

The frontend integrates with the following backend endpoints:

- `/emails/send`: Send a single email
- `/emails/batch`: Send batch emails
- `/emails/inbox`: Get inbox emails
- `/emails/process-inbox`: Process inbox emails
- `/policies/add`: Add a new policy
- `/policies/search`: Search policies
- `/policies/all`: Get all policies
- `/cache/stats`: Get cache statistics
- `/cache/clear`: Clear cache
- `/health`: System health check

## Usage

1. Navigate between sections using the tabs at the top
2. Use the forms to interact with the system
3. View feedback in the notification messages

## Development

To modify the frontend:

1. Edit `index.html` for UI structure and styling
2. Edit `api.js` for API integration
3. Edit `app.js` for UI interactions and event handling