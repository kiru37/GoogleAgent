import sys
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-02-a26999767c1c"

SEEDED_DESTINATIONS = [
    {
        "id": "kyoto-japan",
        "name": "Kyoto",
        "location": "Japan",
        "description": "Historical heart of Japan renowned for classical Buddhist temples, gardens, imperial palaces, and traditional wooden houses.",
        "price_level": "$$$",
        "recommended_activities": [
            "Visit Fushimi Inari Shrine",
            "Explore Arashiyama Bamboo Grove",
            "Experience traditional tea ceremony in Gion",
            "Walk through Kinkaku-ji (Golden Pavilion)"
        ]
    },
    {
        "id": "santorini-greece",
        "name": "Santorini",
        "location": "Greece",
        "description": "Picturesque Aegean island famous for white whitewashed buildings with blue domes, dramatic volcanic caldera views, and stunning sunsets.",
        "price_level": "$$$$",
        "recommended_activities": [
            "Watch sunset from Oia village",
            "Catamaran cruise around the volcanic caldera",
            "Visit Red Beach and Akrotiri archaeological site",
            "Sample local Assyrtiko wines"
        ]
    },
    {
        "id": "cusco-peru",
        "name": "Cusco & Machu Picchu",
        "location": "Peru",
        "description": "Ancient capital of the Inca Empire nestled in the Andes mountains, serving as the gateway to the sacred citadel of Machu Picchu.",
        "price_level": "$$",
        "recommended_activities": [
            "Hike the Inca Trail to Machu Picchu",
            "Explore Sacsayhuamán fortress",
            "Shop at San Pedro local market",
            "Stroll through San Blas artisan neighborhood"
        ]
    },
    {
        "id": "banff-canada",
        "name": "Banff National Park",
        "location": "Alberta, Canada",
        "description": "Canada's oldest national park in the Rocky Mountains, featuring turquoise glacial lakes, majestic alpine peaks, and abundant wildlife.",
        "price_level": "$$$",
        "recommended_activities": [
            "Canoe on Lake Louise and Moraine Lake",
            "Ride the Banff Gondola to Sulphur Mountain",
            "Drive along the Icefields Parkway",
            "Soak in Banff Upper Hot Springs"
        ]
    },
    {
        "id": "cape-town-south-africa",
        "name": "Cape Town",
        "location": "South Africa",
        "description": "Vibrant coastal city framed by Table Mountain, boasting pristine beaches, botanical gardens, and rich historical heritage.",
        "price_level": "$$",
        "recommended_activities": [
            "Take the cable car to Table Mountain summit",
            "See penguins at Boulders Beach",
            "Drive along Chapman's Peak Drive to Cape Point",
            "Explore the Victoria & Alfred Waterfront"
        ]
    }
]

def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("destinations")

    for dest in SEEDED_DESTINATIONS:
        doc_id = dest["id"]
        doc_data = {
            "name": dest["name"],
            "location": dest["location"],
            "description": dest["description"],
            "price_level": dest["price_level"],
            "recommended_activities": dest["recommended_activities"],
        }
        collection_ref.document(doc_id).set(doc_data)
        print(f"Seeded destination: {dest['name']} ({doc_id})")

    print("\nFirestore 'destinations' collection successfully seeded!")

if __name__ == "__main__":
    seed_database()
