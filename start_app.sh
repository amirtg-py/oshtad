#!/usr/bin/env bash
set -e

echo "Starting Medical Store Application..."

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Setup Python virtual environment
if [ ! -d venv ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r backend/requirements.txt

# Wait for MongoDB to be available
until nc -z localhost 27017; do
  echo "Waiting for MongoDB on port 27017..."
  sleep 2
done
echo "MongoDB is up."

# Start backend server in the background
(
  cd backend
  uvicorn server:app --host 0.0.0.0 --port 8000 &
)

# Navigate to frontend and start development server
cd frontend
npm install --force
npm start

