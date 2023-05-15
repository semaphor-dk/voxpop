# Voxpop

Django based application for posting and voting on questions.

## Getting started

```bash
# Create a virtual environment
virtualenv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy .env.template to .env and fill in the values
cp voxpop_project/.env.template voxpop_project/.env

# Start postgres via docker-compose
docker-compose up -d

# Run migrations, create a superuser and start the server
./manage.py migrate
./manage.py createsuperuser

# Run the application using uvicorn
uvicorn --log-level debug --reload --timeout-graceful-shutdown 0 voxpop_project.asgi:application
```
