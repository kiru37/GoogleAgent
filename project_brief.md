# My agent: GlobeTrotter Travel Planner

One-liner: A conversational travel concierge agent that helps travelers explore destinations, generate custom daily itineraries, and save favorite trips to a personal collection.

## Tool coverage:
- **Memory**: Remembers user travel preferences (budget, travel style, dietary preferences, favorite climate, past trips).
- **Tools**:
  - `search_destinations(query, budget, style)`: Searches a curated destination database for matching spots.
  - `create_itinerary(destination, days, interests)`: Generates a day-by-day travel plan.
  - `save_favorite_trip(trip_data)` / `get_favorite_trips()`: Stores and retrieves saved trips from structured storage (Firestore).
  - `calculate_trip_budget(daily_cost, days, travelers)`: Calculates estimated total trip budget and expense breakdown.
- **Catalog/UI**: Interactive destination cards and daily itinerary cards with rich formatting (A2UI).
- **Image gen**: Generates postcard-style preview images or visuals for destinations and itineraries (`gemini-3.1-flash-lite-image`).
- **Sandbox**: Computes travel budget calculations, currency conversions, and duration estimations in a Python sandbox.

Recommended for every project: memory, storage, tools, image generation, A2UI.
Agent-specific / stretch (pick what fits): Code sandbox for budget math, live weather lookup tool, Google Maps links integration.
