import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_travel_plan(user_input: str) -> dict:
    prompt = f"""
You are an AI Travel Booking & Arrival Assistant.

Create a practical, structured travel plan in STRICT JSON format.

LANGUAGE RULE:
You MUST follow the user's preferred language exactly.
- If Preferred language is Chinese (Simplified), ALL JSON values must be in Simplified Chinese.
- If Preferred language is English, ALL JSON values must be in English.
- If Preferred language is Bilingual English + Chinese, include both English and Chinese in every value.
- JSON keys must stay in English.

TRIP RULES:
- Strictly follow the user's route segments and selected transport modes.
- Do not replace a driving segment with a flight.
- Do not replace a flight segment with driving.
- If a day includes a flight, include flight details in that day's itinerary.
- If a day includes accommodation check-in or hotel change, include accommodation in that day's itinerary.
- If the same accommodation continues for multiple nights, do not repeat it every day.
- If a day includes meals, attractions, fuel, EV charging, rest stops, or booking notes, include them inside that day's itinerary.
- Each day must be self-contained and practical.

DRIVING RULES:
- Short drives (under 2h/day): maximum 2 hours driving per day.
- Moderate (2–4h/day): keep driving within 2–4 hours per day.
- Long drives acceptable (4–6h/day): keep driving within 4–6 hours per day.
- If a driving segment is longer than the daily limit, split it into multiple days and suggest overnight stops.
- Include estimated driving time, route summary, rest stops, fuel or EV charging stops where relevant.

BOOKING RULES:
- Flight and hotel prices are estimates only unless connected to a real booking API.
- Do not claim real-time availability.
- Do not invent confirmed bookings.

Return ONLY valid JSON. Do not include markdown.

JSON structure:

{{
  "trip_overview": {{
    "destination": "",
    "summary": "",
    "budget_comment": "",
    "family_suitability": "",
    "fatigue_level": ""
  }},
  "flight_options": [
    {{
      "route": "",
      "airline": "",
      "departure_time": "",
      "arrival_time": "",
      "duration": "",
      "stops": "",
      "price_estimate": "",
      "booking_tip": ""
    }}
  ],
  "hotel_options": [
    {{
      "name": "",
      "area": "",
      "price_estimate": "",
      "family_friendly": "",
      "booking_tip": ""
    }}
  ],
  "road_trip_camping_plan": {{
    "trip_style": "",
    "suggested_route": "",
    "daily_driving_time": "",
    "overnight_stops": "",
    "camping_or_holiday_park_suggestions": "",
    "fuel_grocery_notes": "",
    "road_safety_notes": "",
    "family_suitability": "",
    "route_feasibility": "",
    "segments_analysis": [
      {{
        "segment": "",
        "transport_mode": "",
        "estimated_total_travel_time": "",
        "daily_limit": "",
        "driving_days_required": "",
        "suggested_overnight_stops": "",
        "feasibility_comment": ""
      }}
    ]
  }},
  "vehicle_plan": {{
    "vehicle_type": "",
    "vehicle_source": "",
    "route_strategy": "",
    "fuel_or_charging_strategy": "",
    "daily_driving_advice": "",
    "ev_specific_notes": "",
    "campervan_or_motorhome_notes": "",
    "notes": ""
  }},
  "daily_itinerary": [
    {{
      "day": 1,
      "title": "",
      "morning": "",
      "lunch": "",
      "afternoon": "",
      "dinner": "",
      "transport_note": "",
      "overnight_location": "",
      "accommodation_suggestion": "",
      "morning_activity": "",
      "lunch_recommendation": "",
      "afternoon_activity": "",
      "dinner_recommendation": "",
      "transport_mode": "",
      "route_summary": "",
      "estimated_driving_or_travel_time": "",
      "fuel_or_charging_stop": "",
      "rest_stop_or_playground": "",
      "estimated_cost_today": "",
      "family_notes": "",
      "booking_or_navigation_notes": ""
    }}
  ],
  "attractions": {{
    "cultural_heritage": [],
    "nature_scenic": [],
    "family_kids": []
  }},
  "dining": [],
  "airport_arrival": {{
    "public_transport": "",
    "taxi_or_rideshare": "",
    "car_rental": "",
    "family_notes": ""
  }},
  "multilingual_phrases": [],
  "booking_notes": {{
    "flights": "",
    "accommodation": "",
    "car_rental": ""
  }}
}}

User request:
{user_input}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Return valid JSON only. All JSON values must follow the user's preferred language."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "error": "The AI response was not valid JSON.",
            "raw_response": content
        }
