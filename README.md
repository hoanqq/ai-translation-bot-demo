# AI Translation Bot

This project is a demo repository for an AI Bot that helps with translation. The bot is hosted in a FastAPI app and can be accessed from a simple website built with Streamlit or Gradio. The frontend allows users to select two languages (to/from) from the available options: English, Spanish, Chinese, and Japanese. The app targets the OpenAI GPT-4o-mini model hosted in Azure for translation.

## Setup and Run the Project

### Prerequisites

- Python 3.7 or higher
- Azure account with access to OpenAI GPT-4o-mini
- API keys for Azure OpenAI

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/githubnext/workspace-blank.git
   cd workspace-blank
   ```

2. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running the FastAPI App

1. Navigate to the `app` directory:
   ```sh
   cd app
   ```

2. Start the FastAPI server:
   ```sh
   uvicorn main:app --reload
   ```

### Running the Frontend

1. Navigate to the `frontend` directory:
   ```sh
   cd frontend
   ```

2. Start the Streamlit or Gradio app:
   ```sh
   streamlit run app.py  # For Streamlit
   # or
   python app.py  # For Gradio
   ```

### Using the Makefile

You can use the provided `Makefile` to run the frontend and backend simultaneously.

1. To run the frontend:
   ```sh
   make frontend
   ```

2. To run the backend:
   ```sh
   make backend
   ```

3. To run both frontend and backend:
   ```sh
   make both
   ```

### Development Environment

This project includes a `.devcontainer` setup for development environments. The `.devcontainer` directory contains the necessary configuration files to set up a development container using Visual Studio Code and Docker.

### Feedback Functionality

The project includes feedback functionality implemented in both the backend and frontend. Users can provide feedback on translations using thumbs up or thumbs down buttons.

### Testing API Endpoints

You can use the `test.rest` file to test the API endpoints. The file contains sample requests for the translation and feedback endpoints.

### Dependencies

The `requirements.txt` file lists all the dependencies for the project. Make sure to install them using the following command:
   ```sh
   pip install -r requirements.txt
   ```

### Usage

1. Open your web browser and go to `http://localhost:8501` for Streamlit or the appropriate URL for Gradio.
2. Select the languages for translation (to/from).
3. Input the text you want to translate and submit the form.
4. View the translated text on the frontend.
5. Provide feedback with thumbs up or thumbs down.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
