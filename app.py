import urllib.parse
from datetime import date, timedelta

import streamlit as st

from agents.travel_planner import generate_travel_plan
from agents.booking_agent import (
    generate_flight_links,
    generate_hotel_links,
    generate_car_rental_links,
    generate_campervan_links,
    generate_camping_links,
)
from vision.vision_parser import (
    parse_flight_screenshot,
    parse_hotel_screenshot,
    parse_car_screenshot,
    booking_dict_to_text,
)
from agents.plan_updater import update_plan_with_selected_bookings


st.set_page_config(
    page_title="WanderWise AI",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ WanderWise AI")
st.subheader("Segment-based AI Travel Booking & Arrival Assistant")


# -----------------------------
# Session state
# -----------------------------
if "plan" not in st.session_state:
    st.session_state.plan = None

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if "selected_bookings" not in st.session_state:
    st.session_state.selected_bookings = {
        "flights": [],
        "hotels": [],
        "cars": [],
    }

if "segments" not in st.session_state:
    st.session_state.segments = [
        {
            "from": "Adelaide",
            "to": "Brisbane",
            "start_date": date(2026, 7, 10),
            "end_date": date(2026, 7, 12),
            "transport": "Flight",
            "selected_flight": "",
            "selected_hotel": "",
            "selected_car": "",
            "flight_version": 0,
            "hotel_version": 0,
            "car_version": 0,
            "vehicle_type": "No vehicle",
            "vehicle_source": "No vehicle needed",
            "ev_range": "Not applicable",
            "charging_preference": "Not applicable",
            "stop_preferences": [],
            "camping_style": "Not camping",
            "camping_needs": [],
        },
        {
            "from": "Brisbane",
            "to": "Gold Coast",
            "start_date": date(2026, 7, 12),
            "end_date": date(2026, 7, 16),
            "transport": "Rental car / self-drive",
            "selected_flight": "",
            "selected_hotel": "",
            "selected_car": "",
            "flight_version": 0,
            "hotel_version": 0,
            "car_version": 0,
            "vehicle_type": "Petrol car",
            "vehicle_source": "Rental car",
            "ev_range": "Not applicable",
            "charging_preference": "Not applicable",
            "stop_preferences": ["Fuel stop", "Playground", "Lunch break"],
            "camping_style": "Not camping",
            "camping_needs": [],
        },
    ]

if "departure" not in st.session_state:
    st.session_state.departure = "Adelaide"

if "destinations" not in st.session_state:
    st.session_state.destinations = ["Brisbane", "Gold Coast"]

if "travellers" not in st.session_state:
    st.session_state.travellers = ""


# -----------------------------
# Helpers
# -----------------------------
def google_maps_link(query: str) -> str:
    return "https://www.google.com/maps/search/" + urllib.parse.quote(query or "")


def format_date(d):
    if isinstance(d, date):
        return d.strftime("%Y-%m-%d")
    return str(d)


def extract_value_from_template(text: str, field_name: str) -> str:
    if not text:
        return ""

    marker = f"{field_name}:"
    if marker not in text:
        return ""

    return text.split(marker, 1)[-1].split("\n", 1)[0].strip()


def get_clean_segments():
    clean = []

    for seg in st.session_state.segments:
        from_city = seg.get("from", "").strip()
        to_city = seg.get("to", "").strip()

        if from_city and to_city:
            clean.append({
                "from": from_city,
                "to": to_city,
                "start_date": seg.get("start_date"),
                "end_date": seg.get("end_date"),
                "transport": seg.get("transport", ""),
                "selected_flight": seg.get("selected_flight", ""),
                "selected_hotel": seg.get("selected_hotel", ""),
                "selected_car": seg.get("selected_car", ""),
                "vehicle_type": seg.get("vehicle_type", ""),
                "vehicle_source": seg.get("vehicle_source", ""),
                "ev_range": seg.get("ev_range", ""),
                "charging_preference": seg.get("charging_preference", ""),
                "stop_preferences": seg.get("stop_preferences", []),
                "camping_style": seg.get("camping_style", ""),
                "camping_needs": seg.get("camping_needs", []),
            })

    return clean


def get_destinations_from_segments(segments):
    return list(dict.fromkeys([seg["to"] for seg in segments]))


def segments_to_text(segments):
    lines = []

    for i, seg in enumerate(segments):
        line = (
            f"{i + 1}. {seg['from']} → {seg['to']} "
            f"from {format_date(seg['start_date'])} to {format_date(seg['end_date'])} "
            f"by {seg['transport']}"
        )

        if seg.get("selected_flight"):
            line += f"; selected flight: {seg['selected_flight']}"

        if seg.get("selected_hotel"):
            line += f"; selected hotel: {seg['selected_hotel']}"

        if seg.get("selected_car"):
            line += f"; selected car rental: {seg['selected_car']}"

        if seg["transport"] in [
            "Rental car / self-drive",
            "Own car",
            "Campervan / motorhome",
        ]:
            line += (
                f"; vehicle: {seg['vehicle_type']}; "
                f"vehicle source: {seg['vehicle_source']}; "
                f"stops needed: {', '.join(seg['stop_preferences'])}"
            )

        if seg["vehicle_type"] == "Electric vehicle (EV)":
            line += (
                f"; EV range: {seg['ev_range']}; "
                f"charging preference: {seg['charging_preference']}"
            )

        if seg["transport"] == "Campervan / motorhome":
            line += (
                f"; camping style: {seg['camping_style']}; "
                f"camping needs: {', '.join(seg['camping_needs'])}"
            )

        lines.append(line)

    return "\n".join(lines)


def save_selected_booking(kind: str, segment_index: int, data: dict):
    item = {
        "segment_index": segment_index,
        "segment": {
            "from": st.session_state.segments[segment_index].get("from", ""),
            "to": st.session_state.segments[segment_index].get("to", ""),
            "start_date": format_date(st.session_state.segments[segment_index].get("start_date", "")),
            "end_date": format_date(st.session_state.segments[segment_index].get("end_date", "")),
            "transport": st.session_state.segments[segment_index].get("transport", ""),
        },
        "details": data,
    }

    text = booking_dict_to_text(data)

    if kind == "flight":
        st.session_state.selected_bookings["flights"].append(item)
        st.session_state.segments[segment_index]["selected_flight"] = text
        st.session_state.segments[segment_index]["flight_version"] = (
            st.session_state.segments[segment_index].get("flight_version", 0) + 1
        )

    elif kind == "hotel":
        st.session_state.selected_bookings["hotels"].append(item)
        st.session_state.segments[segment_index]["selected_hotel"] = text
        st.session_state.segments[segment_index]["hotel_version"] = (
            st.session_state.segments[segment_index].get("hotel_version", 0) + 1
        )

    elif kind == "car":
        st.session_state.selected_bookings["cars"].append(item)
        st.session_state.segments[segment_index]["selected_car"] = text
        st.session_state.segments[segment_index]["car_version"] = (
            st.session_state.segments[segment_index].get("car_version", 0) + 1
        )


# -----------------------------
# Display Plan
# -----------------------------
def display_plan(plan):
    st.markdown("## Daily Itinerary")

    previous_accommodation = None

    for day in plan.get("daily_itinerary", []):
        title = f"Day {day.get('day', '')} — {day.get('title', '')}"

        with st.expander(title, expanded=True):
            morning = day.get("morning_activity") or day.get("morning", "")
            lunch = day.get("lunch_recommendation") or day.get("lunch", "")
            afternoon = day.get("afternoon_activity") or day.get("afternoon", "")
            dinner = day.get("dinner_recommendation") or day.get("dinner", "")

            st.markdown("### Activities & Food")
            st.write("**Morning:**", morning)
            st.write("**Lunch:**", lunch)
            st.write("**Afternoon:**", afternoon)
            st.write("**Dinner:**", dinner)

            transport_mode = day.get("transport_mode") or day.get("transport_note", "")
            route_summary = day.get("route_summary", "")
            travel_time = day.get("estimated_driving_or_travel_time", "")

            st.markdown("### Transport")
            st.write("**Transport mode:**", transport_mode)
            st.write("**Route:**", route_summary)
            st.write("**Estimated travel/driving time:**", travel_time)

            accommodation = day.get("accommodation_suggestion", "")
            overnight = day.get("overnight_location", "")

            if accommodation and accommodation != previous_accommodation:
                st.markdown("### 🏨 Accommodation")
                st.write("**Overnight location:**", overnight)
                st.write("**Accommodation:**", accommodation)

                hotel_links = generate_hotel_links(
                    destinations=[overnight or accommodation],
                    dates=f"{overnight}",
                    travellers=st.session_state.travellers,
                    hotel_name=accommodation,
                    area=overnight,
                )

                cols = st.columns(len(hotel_links))
                for col, (label, url) in zip(cols, hotel_links.items()):
                    col.link_button(label, url)

                previous_accommodation = accommodation

            if lunch or dinner:
                st.markdown("### 🍽 Dining Search")
                if lunch:
                    st.link_button("Search lunch in Maps", google_maps_link(lunch))
                if dinner:
                    st.link_button("Search dinner in Maps", google_maps_link(dinner))

            if morning or afternoon:
                st.markdown("### 📍 Attraction Navigation")
                if morning:
                    st.link_button("Open morning activity in Maps", google_maps_link(morning))
                if afternoon:
                    st.link_button("Open afternoon activity in Maps", google_maps_link(afternoon))

            fuel_or_charging = day.get("fuel_or_charging_stop", "")
            if fuel_or_charging:
                st.markdown("### ⛽ Fuel / EV Charging")
                st.write(fuel_or_charging)
                st.link_button("Open fuel / charging stop in Maps", google_maps_link(fuel_or_charging))

            rest_stop = day.get("rest_stop_or_playground", "")
            if rest_stop:
                st.markdown("### 🛝 Rest Stop / Playground")
                st.write(rest_stop)
                st.link_button("Open rest stop in Maps", google_maps_link(rest_stop))

            st.markdown("### Notes")
            st.write("**Estimated cost today:**", day.get("estimated_cost_today", ""))
            st.write("**Family notes:**", day.get("family_notes", ""))
            st.write("**Booking / navigation notes:**", day.get("booking_or_navigation_notes", ""))
