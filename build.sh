#!/usr/bin/env bash
set -o errexit

echo "Current directory:"
pwd

echo "Files:"
ls

echo "Requirements:"
cat requirements.txt

python manage.py collectstatic --no-input