# WellMate Chatbot

WellMate is an intelligent healthcare chatbot designed to provide medical information and assistance. It leverages advanced AI models and vector databases to offer personalized and context-aware responses, simulating a conversation with an experienced physician.

## Features

*   **AI-Powered Conversations:** Utilizes Groq's powerful language models for natural and engaging interactions.
*   **Contextual Understanding:** Employs Pinecone for efficient retrieval of relevant medical information, ensuring accurate and context-aware responses.
*   **Personalized Experience:** Maintains chat history and patient information (name, age, gender, language) to tailor responses.
*   **Physician Persona:** The chatbot, "Dr. Black," acts as a female physician with 30 years of experience, providing professional and empathetic guidance.
*   **Constraint Enforcement:** Implements rules to ensure safe and appropriate medical advice, including dosage instructions for prescriptions and avoiding certain phrases.
*   **Dockerized Deployment:** Easily deployable using Docker and Docker Compose for consistent environments.
*   **Supabase Integration:** Manages guest user data and chat histories using Supabase.
*   **Static File Serving:** Serves a classic web interface for user interaction.

## Technologies Used

*   **Backend:** FastAPI (Python)
*   **AI/ML:**
    *   Groq (for LLM inference)
    *   LangChain (for orchestrating LLM applications)
    *   HuggingFace Embeddings (for text embeddings)
    *   Pinecone (Vector Database for RAG)
*   **Database:** Supabase
*   **Containerization:** Docker, Docker Compose
*   **Frontend:** HTML, CSS, JavaScript (served statically)
*   **Dependencies Management:** `requirements.txt`

## Setup and Installation

Follow these steps to set up and run the WellMate Chatbot locally using Docker Compose:

### Prerequisites

*   Docker and Docker Compose installed on your system.
*   A Groq API Key.
*   A Pinecone API Key and environment.
*   A Supabase project with appropriate table setup .

### Environment Variables

Create a `.env` file in the root directory of the project with the following variables:

```
GROQ_API_KEY="your_groq_api_key"
PINECONE_API_KEY="your_pinecone_api_key"
PINECONE_ENVIRONMENT="your_pinecone_environment" # e.g., us-west-2
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_anon_key"
SECRET_KEY="a_strong_random_secret_key_for_fastapi_sessions"
```

### Running the Application

1.  **Build and Run with Docker Compose:**
    Navigate to the root directory of the project in your terminal and run:

    ```bash
    docker-compose up --build
    ```

    This command will:
    *   Build the Docker image for the `wellmate` service.
    *   Start the `wellmate` container.
    *   Map port `8083` on your host to port `8000` inside the container.

2.  **Access the Application:**
    Once the containers are running, open your web browser and go to:

    ```
    http://localhost:8083
    ```

    You should see the login page for the WellMate Chatbot.

## Usage

*   **Login Page:** Start by interacting with the login page.
*   **New Chat Session:** The application allows for new guest chat sessions.
*   **Patient Information:** You can update patient information, which helps the chatbot provide more personalized responses.
*   **Chat Interface:** Engage in conversations with "Dr. Black" and receive medical guidance.

## Project Structure

*   `main.py`: The main FastAPI application, handling API routes, static file serving, and integration with the chatbot and Supabase.
*   `chatbot.py`: Contains the core chatbot logic, including LLM integration (Groq), vector store management (Pinecone), and response generation with enforced constraints.
*   `supabase_client.py`: Handles interactions with the Supabase database for managing guest user data and chat histories.
*   `static/`: Directory containing static frontend files (HTML, CSS, JavaScript) for the web interface.
*   `Dockerfile`: Defines the Docker image for the application.
*   `docker-compose.yml`: Configures the Docker Compose setup for easy local deployment.
*   `requirements.txt`: Lists all Python dependencies.
*   `.env`: Environment variables for API keys and configurations (not committed to Git).

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## License

This project is licensed under the MIT License.
