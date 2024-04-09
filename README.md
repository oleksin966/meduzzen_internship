# meduzzen_internship
## Prerequisites

Before starting the application, ensure you have the following installed:

- Python (version 3.8)
- Pip (version 20.2.1)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/oleksin966/meduzzen_internship.git
    ```

2. Navigate to the project directory:
    ```bash
    cd meduzzen_internship
    ```

3. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Unix/Mac
    # or
    .\venv\Scripts\activate   # For Windows
    ```

4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1. Navigate to the app directory:
    ```bash
    cd app
    ```

2. To start the application, run the following command:
```bash
uvicorn main:app --reload

```

The application will start running on http://localhost:8000 by default. You can access the API endpoints using a web browser.