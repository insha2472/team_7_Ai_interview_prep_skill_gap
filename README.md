# AI Interview Prep Skill Gap Analyzer

This project is a web application that helps users prepare for interviews by analyzing their resume and providing personalized feedback on skill gaps. It uses AI to evaluate the user's skills and suggest areas for improvement.

## Features

- **Resume Upload**: Users can upload their resume for analysis.
- **AI-Powered Skill Analysis**: The system uses AI to identify the user's skills and compare them against job requirements.
- **Skill Gap Detection**: It detects missing skills and provides recommendations for improvement.
- **Interview Preparation**: Offers guidance and resources to help users prepare for interviews.

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository** (or download the source code).

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv env
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     .\env\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source env/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Once the dependencies are installed, you can start the server:

```bash
uvicorn main:app --reload
```

The application will be available at `http://localhost:8000`.

## Usage

1. Open your web browser and navigate to `http://localhost:8000`.
2. Follow the on-screen instructions to upload your resume and get AI-powered feedback.

## Development

### API Endpoints

The application uses FastAPI for its API. Key endpoints include:

- `POST /upload`: Upload a resume for analysis.
- `GET /`: Get a list of all available endpoints.

### Environment Variables

Ensure you have the following environment variables set (if applicable):

- `DATABASE_URL`: Database connection string.
- `GEMINI_API_KEY`: API key for the AI model.

## License

This project is licensed under the terms of the MIT license.