import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def update_plan_with_selected_bookings(
    original_plan: dict,
    selected_bookings: dict,
    user_input: str
) -> dict:
    prompt = f"""
You are an AI Travel Booking & Arrival Assistant.

Update the existing travel plan using the user's selected booking details.

Selected booking details may include:
- selected flight from screenshot
- selected hotel from screenshot
- selected car rental from screenshot
- selected campervan or campsite details

Rules:
- Return ONLY valid JSON.
- Keep the same JSON structure as the original plan.
- Do not invent confirmations or details not provided.
- Use the selected booking details inside the relevant daily itinerary item.
- If a selected flight includes arrival time, update the arrival day timing and airport transfer notes.
- If a selected hotel covers multiple nights, include it only on the check-in day or when accommodation changes.
- If a selected car rental includes pickup/drop-off time and location, update transport notes and road trip days.
- If selected booking details conflict with the current plan, adjust the plan around the selected booking.
- Keep every day self-contained with accommodation, transport, meals, practical stops, and notes.
- Preserve the user's preferred language from the original request.

Original user request:
{user_input}

Current travel plan:
{json.dumps(original_plan, ensure_ascii=False)}

Selected booking details:
{json.dumps(selected_bookings, ensure_ascii=False)}

Return ONLY valid JSON.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You update travel plans using selected booking details. Return valid JSON only."
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
            "error": "The updated plan was not valid JSON.",
            "raw_response": content
        }