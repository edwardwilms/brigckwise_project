# Brickwise Invest

## Project Overview
Brickwise Invest is a tool that helps real estate professionals analyze the financial aspects of a project. It integrates with a Google Sheets spreadsheet to perform calculations and data management.

## Backend
The backend is a FastAPI-based API that interacts with the Google Sheets spreadsheet. It has two main endpoints:

- `/update-excel`: Accepts input data and updates the corresponding cells in the spreadsheet.
- `/read-excel`: Reads data from the spreadsheet and returns it as a JSON response.

The API includes helper functions to handle currency and percentage formatting.

## Google Sheets setup
### Local Development
When running the application in local development, you need to uncomment the following lines and provide the path to your downloaded JSON key file:

```python
SERVICE_ACCOUNT_FILE = 'C:/Users/wilmsedw/Documents/brickwise_project/backend/brickwise-450120-69ac0aa13cfa.json'
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
```

### Deployment
When deploying the application, you should comment out the `SERVICE_ACCOUNT_FILE` line and instead set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable on the deployment platform with the content of the same JSON key file.

```python
# SERVICE_ACCOUNT_FILE = 'C:/Users/wilmsedw/Documents/brickwise_project/backend/brickwise-450120-69ac0aa13cfa.json'
credentials = service_account.Credentials.from_service_account_file(
    os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"), scopes=SCOPES)
```

This ensures that the correct credentials are used for both local development and deployment environments.

## Running the Application Locally
To run the application locally, follow these steps:

1. Create a virtual environment (venv) for the project:
   - Open a terminal and navigate to the root of the project directory.
   - Run the following command to create a new virtual environment:
     ```
     python -m venv venv
     ```
   - Activate the virtual environment:
     - On Windows: `venv\Scripts\activate`
     - On macOS/Linux: `source venv/bin/activate`

2. Install the backend requirements:
   ```
   pip install -r backend/requirements.txt
   ```

3. Install the frontend requirements:
   ```
   cd frontend
   npm install
   ```

4. Start the backend server:
   ```
   uvicorn backend.main:app --reload
   ```

5. In a separate terminal, start the frontend development server:
   ```
   cd frontend
   npm run dev
   ```

This will set up the local development environment, install the necessary dependencies, and start both the backend and frontend components, allowing you to interact with the Brickwise Invest application locally.

## Frontend
The frontend is a React-based dashboard component that renders input fields and output cards. The dashboard fetches data from the backend API, updates the UI accordingly, and handles user input changes to trigger the calculation process. The dashboard uses various UI components to create the user interface.

## Setup and Usage
Instructions for setting up the development environment, including installing dependencies and running the backend and frontend components.

Guidance on how to use the Brickwise Invest tool, including inputting data, triggering calculations, and interpreting the output.

## Contributing
Guidelines for contributing to the project, including instructions for submitting bug reports, feature requests, and pull requests.

## License
Information about the project's license and any relevant copyright or attribution details.