# Job Sourcing Pro

A professional job sourcing application that automates the process of scraping, analyzing, and managing job postings from various sources.

## Features

- Automated job scraping from multiple sources
- PostgreSQL database for efficient data storage
- Streamlit web interface for easy interaction
- Advanced job analysis using LLM technology
- Customizable job search criteria
- Export functionality for job data

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- OR
- Python 3.8+
- PostgreSQL 12+
- Virtual environment (recommended)

## Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/job-sourcing-pro.git
cd job-sourcing-pro
```

2. Create a .env file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Build and start the containers:
```bash
docker-compose up -d --build
```

4. Access the application at `http://localhost:8501`

## Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/job-sourcing-pro.git
cd job-sourcing-pro
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
python init_db.py
```

## Configuration

Create a `.env` file with the following variables:
```
DATABASE_URL=postgresql://jobsourcingpro:your_password@localhost:5432/jobsourcingpro
GROQ_API_KEY=your_groq_api_key
DB_PASSWORD=your_database_password
```

## Docker Deployment

The application is containerized using Docker and can be deployed using Docker Compose. The setup includes:

- Application container running Streamlit
- PostgreSQL database container
- Automatic database initialization
- Health checks for both services
- Volume persistence for database and logs
- Secure non-root user execution
- Multi-stage builds for smaller image size

### Docker Commands

Start the application:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f
```

Stop the application:
```bash
docker-compose down
```

Remove volumes (caution - this will delete all data):
```bash
docker-compose down -v
```

## Project Structure

```
job-sourcing-pro/
├── app.py                 # Main Streamlit application
├── init_db.py            # Database initialization script
├── crud.py               # Database operations
├── scraper/              # Job scraping modules
├── models/               # Database models
├── utils/                # Utility functions
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker build instructions
├── init-scripts/         # Database initialization scripts
├── requirements.txt      # Project dependencies
└── .env.example         # Example environment variables
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Streamlit
- Powered by Groq LLM
- PostgreSQL for database management 