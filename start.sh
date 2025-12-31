#!/bin/bash

# Run database migrations
echo "Running migrations..."
python migrations/migration.py

# Start the application
echo "Starting application..."
exec gunicorn app:app
