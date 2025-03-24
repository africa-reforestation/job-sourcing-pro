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

- Python 3.8+
- PostgreSQL 12+
- Virtual environment (recommended)

## Installation

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
DATABASE_URL=postgresql://username:password@localhost:5432/dbname
GROQ_API_KEY=your_groq_api_key
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Access the web interface at `http://localhost:8501`

## Project Structure

```
job-sourcing-pro/
├── app.py                 # Main Streamlit application
├── init_db.py            # Database initialization script
├── crud.py               # Database operations
├── scraper/              # Job scraping modules
├── models/               # Database models
├── utils/                # Utility functions
└── requirements.txt      # Project dependencies
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