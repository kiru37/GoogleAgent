# GlobeTrotter Travel Planner

GlobeTrotter is an AI-powered conversational travel concierge agent built with Google's Agent Development Kit (ADK), the Agent-to-Agent (A2A) protocol, and a modern FastAPI web frontend supporting Google Agent User Interface (A2UI) rendering.

---

## Key Features & Capabilities

GlobeTrotter provides personalized, end-to-end travel planning by integrating live external APIs, database persistence, generative AI media creation, and cross-session memory.

### 🧭 Travel Intelligence & Location Tools
* **Firestore Destination Catalog**: Search existing destinations (`search_destinations`) or save new places (`add_destination`) in Google Cloud Firestore.
* **Live Weather Integration**: Fetch real-time temperature and weather conditions (`get_current_weather`) for any destination.
* **Geocoding & Location Resolution**: Convert location names or addresses into latitude and longitude coordinates (`geocode_address`) using the Google Geocoding API.
* **Nearby Places Search**: Discover nearby attractions, restaurants, museums, and lodging (`find_nearby_places`) using the Google Places API (New).

### 🎨 Generative AI Media Creation
* **Destination Photo Generation**: Generate custom promotional images (`generate_destination_image`) using Vertex AI `gemini-3.1-flash-lite-image`. Images are saved to the ADK Playground panel and uploaded to Google Cloud Storage with public HTTPS URLs.
* **Destination Video Preview**: Generate short travel preview clips (`generate_destination_video`) using Vertex AI `gemini-omni-flash-preview` via the Interactions API. Videos are saved as artifacts and uploaded to Google Cloud Storage.

### 🧠 Cross-Session Memory & Code Execution
* **ADK Memory Bank Integration**: Retains traveler preferences, budget limits, dietary restrictions, and travel styles across chat sessions using `PreloadMemoryTool` and post-turn session memory callbacks.
* **Python Code Execution Sandbox**: Executes Python calculations (`AgentEngineSandboxCodeExecutor`) for travel budget estimation, currency conversions, and date/time math.

### 🖥️ A2UI & Custom Web Interface
* **A2UI Render Engine**: Formats recommendations into structured UI components (Cards, Columns, Rows, Text, Images) using the Google A2UI Schema Manager (`v0.8`).
* **FastAPI Proxy**: Proxies browser requests using Google Application Default Credentials (ADC) to the deployed agent over the A2A protocol (`a2a-sdk`).
* **Modern Chat Frontend**: A responsive, themed web interface (`frontend/static/index.html`) featuring prompt suggestion chips, typing indicators, avatars, and inline A2UI card rendering.

---

## Integrated Google Cloud & Google Services

* **Google Cloud Vertex AI**: Gemini 2.5 Flash (Core Agent Reasoning), Gemini 3.1 Flash Lite Image (Image Gen), Gemini Omni Flash Preview (Video Gen).
* **Google Cloud Firestore**: NoSQL document database for the destination collection.
* **Google Cloud Storage**: Public static asset storage for generated images and videos.
* **Google Maps Platform**: Geocoding API and Places API (New).
* **Vertex AI Agent Engine / Agent Runtime**: Cloud execution environment and secure code execution sandbox.

---

## Planned vs. Implemented Features

* **Implemented**: Firestore destination CRUD, live weather, geocoding, nearby places, image generation, video generation, Memory Bank, code sandbox, A2UI cards, A2A proxy frontend.
* **Consolidated / Planned**:
  * Budget calculation function is executed dynamically via the Python code execution sandbox rather than a standalone dedicated tool wrapper.
  * Favorite trip persistence is managed via Firestore destination catalog and Memory Bank preference recall.

---

## Local Setup & Development

### Prerequisites
1. Python 3.10 or higher.
2. `uv` or `pip`.
3. Google Cloud SDK (`gcloud`) authenticated with Application Default Credentials:
   ```bash
   gcloud auth application-default login
   ```

### Running the Frontend Locally

1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set required environment variables:
   ```bash
   export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<REASONING_ENGINE_ID>"
   export AGENT_DIRECTORY="app"
   export GOOGLE_MAPS_API_KEY="your-google-maps-api-key"
   ```

4. Launch the local web server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

5. Open your web browser and navigate to port `8080` on your host.

---

## Deployment to Google Cloud Run

To deploy the frontend proxy to Cloud Run:

```bash
gcloud run deploy globetrotter-frontend \
  --source ./frontend \
  --region us-central1 \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<REASONING_ENGINE_ID>",AGENT_DIRECTORY="app" \
  --allow-unauthenticated
```

Grant the Cloud Run service account access to reach the agent:

```bash
PROJECT_NUMBER=$(gcloud projects describe <PROJECT_ID> --format="value(projectNumber)")
gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```
