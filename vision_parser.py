import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _image_to_data_url(uploaded_file) -> str:
    image_bytes = uploaded_file.getvalue()
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    mime_type = uploaded_file.type or "image/png"
    return f"data:{mime_type};base64,{encoded}"


def _parse_screenshot(uploaded_file, booking_type: str, schema_instruction: str) -> dict:
    image_data_url = _image_to_data_url(uploaded_file)

    prompt = f"""
You are a booking screenshot parser.

Task:
Extract the key booking information from this {booking_type} screenshot.

Rules:
- Return ONLY valid JSON.
- Do not include markdown.
- If a field is not visible, use an empty string.
- Do not invent missing information.
- Preserve dates, times, prices, and names exactly as shown where possible.
- If the screenshot is not relevant to {booking_type}, set "is_relevant" to false and explain briefly in "notes".

JSON structure:
{schema_instruction}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You extract structured booking details from screenshots. Return valid JSON only."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url
                        }
                    }
                ]
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "is_relevant": False,
            "error": "The screenshot parser did not return valid JSON.",
            "raw_response": content
        }


def parse_flight_screenshot(uploaded_file) -> dict:
    schema = """
{
  "is_relevant": true,
  "booking_type": "flight",
  "airline": "",
  "flight_number": "",
  "departure_city_or_airport": "",
  "arrival_city_or_airport": "",
  "departure_date": "",
  "arrival_date": "",
  "departure_time": "",
  "arrival_time": "",
  "duration": "",
  "stops": "",
  "baggage": "",
  "travellers": "",
  "price": "",
  "currency": "",
  "booking_platform": "",
  "fare_type": "",
  "notes": "",
  "summary": ""
}
"""
    return _parse_screenshot(uploaded_file, "flight booking", schema)


def parse_hotel_screenshot(uploaded_file) -> dict:
    schema = """
{
  "is_relevant": true,
  "booking_type": "hotel",
  "hotel_name": "",
  "address_or_area": "",
  "check_in_date": "",
  "check_out_date": "",
  "nights": "",
  "room_type": "",
  "guests": "",
  "breakfast": "",
  "cancellation_policy": "",
  "price": "",
  "currency": "",
  "booking_platform": "",
  "rating": "",
  "family_friendly_notes": "",
  "notes": "",
  "summary": ""
}
"""
    return _parse_screenshot(uploaded_file, "hotel booking", schema)


def parse_car_screenshot(uploaded_file) -> dict:
    schema = """
{
  "is_relevant": true,
  "booking_type": "car_rental",
  "rental_company": "",
  "vehicle_model_or_class": "",
  "pickup_location": "",
  "dropoff_location": "",
  "pickup_date": "",
  "pickup_time": "",
  "dropoff_date": "",
  "dropoff_time": "",
  "transmission": "",
  "fuel_or_ev_type": "",
  "included_mileage": "",
  "insurance_or_excess": "",
  "child_seat": "",
  "price": "",
  "currency": "",
  "booking_platform": "",
  "notes": "",
  "summary": ""
}
"""
    return _parse_screenshot(uploaded_file, "car rental booking", schema)


def booking_dict_to_text(data: dict) -> str:
    if not data:
        return ""

    booking_type = data.get("booking_type", "booking")
    summary = data.get("summary", "")

    lines = [f"{booking_type.upper()} DETAILS"]

    if summary:
        lines.append(f"Summary: {summary}")

    for key, value in data.items():
        if key in ["is_relevant", "booking_type", "summary"]:
            continue
        if value:
            label = key.replace("_", " ").title()
            lines.append(f"{label}: {value}")

    return "\n".join(lines)