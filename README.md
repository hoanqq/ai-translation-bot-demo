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

2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
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
