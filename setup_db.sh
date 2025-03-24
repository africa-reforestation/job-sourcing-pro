#!/bin/bash

# Create database
sudo -u postgres psql -c "CREATE DATABASE jobsourcingpro;"

# Create user and grant privileges
sudo -u postgres psql -c "CREATE USER jobsourcingpro WITH PASSWORD 'jobsourcingpro';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE jobsourcingpro TO jobsourcingpro;"

# Set environment variables
export PGUSER=jobsourcingpro
export PGPASSWORD=jobsourcingpro
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=jobsourcingpro
export DATABASE_URL="postgresql://jobsourcingpro:jobsourcingpro@localhost:5432/jobsourcingpro"

echo "Database setup complete. Environment variables have been set."
echo "You can now run the application with: streamlit run app.py" 