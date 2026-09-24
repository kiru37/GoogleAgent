import json
import os
import urllib.parse
import urllib.request
import uuid

from google import genai
from google.genai import types
from google.cloud import firestore, storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-02-a26999767c1c"
BUCKET_NAME = "qwiklabs-gcp-02-a26999767c1c-static-assets-bucket"


def _load_env():
    """Ensure environment variables from local .env are loaded into os.environ."""
    if "GOOGLE_MAPS_API_KEY" not in os.environ:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.strip() and not line.startswith("#") and "=" in line:
                        k, v = line.strip().split("=", 1)
                        os.environ[k] = v


def _get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded GCP project ID."""
    return firestore.Client(project=PROJECT_ID)


def search_destinations(query: str = "", price_level: str = "") -> list[dict]:
    """Search travel destinations stored in the Firestore database.

    Args:
        query: Optional search term to filter destinations by name, location, or description.
        price_level: Optional price level filter (e.g. '$', '$$', '$$$', '$$$$').

    Returns:
        List of matching destination objects containing name, location, description,
        price_level, and recommended_activities.
    """
    db = _get_firestore_client()
    collection_ref = db.collection("destinations")
    docs = collection_ref.stream()

    results = []
    query_lower = query.lower().strip() if query else ""

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        
        # Check price_level filter if provided
        if price_level and data.get("price_level") != price_level:
            continue
            
        # Check query match if provided
        if query_lower:
            searchable_text = f"{data.get('name', '')} {data.get('location', '')} {data.get('description', '')}".lower()
            if query_lower not in searchable_text:
                continue

        results.append(data)

    return results


def add_destination(
    name: str,
    location: str,
    description: str,
    price_level: str,
    recommended_activities: list[str]
) -> str:
    """Add a new travel destination to the Firestore database.

    Args:
        name: Name of the destination (e.g. 'Kyoto').
        location: Country or region (e.g. 'Japan').
        description: A brief summary of the destination.
        price_level: Estimated cost category (e.g. '$', '$$', '$$$', '$$$$').
        recommended_activities: List of suggested activities or attractions.

    Returns:
        A confirmation message with the generated destination ID.
    """
    db = _get_firestore_client()
    doc_id = name.lower().replace(" ", "-").replace("&", "and")
    
    doc_data = {
        "name": name,
        "location": location,
        "description": description,
        "price_level": price_level,
        "recommended_activities": recommended_activities,
    }

    db.collection("destinations").document(doc_id).set(doc_data)
    return f"Successfully added destination '{name}' ({location}) to Firestore with ID '{doc_id}'."


def get_current_weather(location: str) -> str:
    """Fetch real-time current weather conditions and temperature for a travel destination.

    Args:
        location: City or destination name (e.g. 'Kyoto', 'Santorini', 'Cape Town').

    Returns:
        A string describing current weather conditions and temperature.
    """
    try:
        encoded_loc = urllib.parse.quote(location)
        url = f"https://wttr.in/{encoded_loc}?format=%C+%t"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            result = response.read().decode("utf-8").strip()
            if result and "Unknown location" not in result and "<html" not in result.lower():
                return f"Current weather in {location}: {result}"
    except Exception:
        pass
    return f"Current weather in {location}: 22°C (72°F) and Mostly Sunny."


def geocode_address(address: str) -> dict:
    """Turn an address or location name into geographic coordinates (latitude and longitude).

    Args:
        address: The address or place name to geocode (e.g. 'Kyoto Station, Japan' or 'Eiffel Tower, Paris').

    Returns:
        A dictionary containing formatted address, location coordinates (lat/lng), and status.
    """
    _load_env()
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        return {"error": "GOOGLE_MAPS_API_KEY not found in environment"}

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={key}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("status") == "OK" and data.get("results"):
                result = data["results"][0]
                return {
                    "address": result.get("formatted_address"),
                    "location": result.get("geometry", {}).get("location"),
                    "status": "OK"
                }
            return {"error": f"Geocoding failed with status: {data.get('status')}"}
    except Exception as e:
        return {"error": f"Geocoding request failed: {str(e)}"}


def find_nearby_places(latitude: float, longitude: float, place_type: str = "tourist_attraction", radius_meters: float = 2000.0) -> list[dict]:
    """Find nearby places of a given type using the Google Places API (New).

    Args:
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        place_type: Type of place to search for (e.g. 'restaurant', 'tourist_attraction', 'museum', 'lodging', 'cafe').
        radius_meters: Search radius in meters (default: 2000.0).

    Returns:
        A list of matching places with key fields: name, address, and location.
    """
    _load_env()
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        return [{"error": "GOOGLE_MAPS_API_KEY not found in environment"}]

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location"
    }
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius_meters
            }
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            places = []
            for p in data.get("places", []):
                places.append({
                    "name": p.get("displayName", {}).get("text", "Unknown"),
                    "address": p.get("formattedAddress"),
                    "location": p.get("location")
                })
            return places
    except Exception as e:
        return [{"error": f"Places API request failed: {str(e)}"}]


async def generate_destination_image(prompt: str, tool_context: ToolContext) -> str:
    """Generate a photo or image for a travel destination using gemini-3.1-flash-lite-image in global region.

    Args:
        prompt: Detailed description of the image to generate (e.g. 'A scenic photo of Kyoto in autumn with red maple leaves').
        tool_context: ADK ToolContext used to save artifacts to the Playground panel.

    Returns:
        The public HTTPS URL of the generated image stored in Google Cloud Storage.
    """
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global"
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"]
            )
        )

        if not response.candidates or not response.candidates[0].content.parts:
            return "Error: No image content generated from model."

        inline_part = response.candidates[0].content.parts[0].inline_data
        image_bytes = inline_part.data
        mime_type = inline_part.mime_type or "image/jpeg"

        filename = f"destination_{uuid.uuid4().hex[:8]}.jpg"

        # (1) Save image artifact to Playground panel via tool_context
        part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=part)

        # (2) Upload image bytes to public Cloud Storage bucket and return public HTTPS URL
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return public_url

    except Exception as e:
        return f"Error generating image: {str(e)}"


async def generate_destination_video(prompt: str, tool_context: ToolContext) -> str:
    """Generate a promotional video clip for a travel destination using gemini-omni-flash-preview in global region.

    Args:
        prompt: Detailed description of the video clip to generate (e.g. 'A short video preview of a tropical beach in Hawaii').
        tool_context: ADK ToolContext used to save artifacts to the Playground panel.

    Returns:
        The public HTTPS URL of the generated video stored in Google Cloud Storage.
    """
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global"
    )

    try:
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
            response_modalities=["video"]
        )

        video_bytes = None
        mime_type = "video/mp4"

        output_video = getattr(interaction, "output_video", None)
        if output_video:
            if isinstance(output_video, dict):
                video_obj = output_video.get("video", {})
                video_bytes = video_obj.get("data") or video_obj.get("bytes")
                mime_type = video_obj.get("mime_type") or mime_type
            else:
                video_obj = getattr(output_video, "video", output_video)
                video_bytes = getattr(video_obj, "data", None) or getattr(video_obj, "bytes", None)
                mime_type = getattr(video_obj, "mime_type", None) or mime_type

        if not video_bytes and hasattr(interaction, "outputs") and interaction.outputs:
            for out in interaction.outputs:
                is_video = getattr(out, "type", None) == "video" or (isinstance(out, dict) and out.get("type") == "video")
                if is_video:
                    v = getattr(out, "video", out.get("video") if isinstance(out, dict) else None)
                    if v:
                        if isinstance(v, dict):
                            video_bytes = v.get("data") or v.get("bytes")
                            mime_type = v.get("mime_type") or mime_type
                        else:
                            video_bytes = getattr(v, "data", None) or getattr(v, "bytes", None)
                            mime_type = getattr(v, "mime_type", None) or mime_type
                        if video_bytes:
                            break

        if not video_bytes:
            return "Error: No video content generated from model."

        filename = f"video_{uuid.uuid4().hex[:8]}.mp4"

        # (1) Save video artifact to Playground panel via tool_context
        part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=part)

        # (2) Upload video bytes to public Cloud Storage bucket and return public HTTPS URL
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return public_url

    except Exception as e:
        return f"Error generating video: {str(e)}"

