import urllib.parse


def make_search_url(base_url: str, query: str) -> str:
    return base_url + urllib.parse.quote(query)


def generate_flight_links(
    departure: str,
    destinations: list[str],
    dates: str,
    travellers: str = "",
    airline: str = "",
    route: str = "",
    departure_time: str = "",
    arrival_time: str = "",
    stops: str = ""
) -> dict:
    destination_text = " ".join(destinations)

    query = (
        f"{departure} to {destination_text} {dates} "
        f"{travellers} {airline} {route} "
        f"departure {departure_time} arrival {arrival_time} {stops}"
    )

    return {
        "Google Flights": make_search_url(
            "https://www.google.com/travel/flights?q=", query
        ),
        "Skyscanner": make_search_url(
            "https://www.skyscanner.com/transport/flights/?search=", query
        ),
        "Kayak": make_search_url(
            "https://www.kayak.com/flights?sort=bestflight_a&query=", query
        ),
        "Expedia Flights": make_search_url(
            "https://www.expedia.com/Flights-Search?trip=roundtrip&leg1=", query
        ),
    }


def generate_hotel_links(
    destinations: list[str],
    dates: str,
    travellers: str = "",
    hotel_name: str = "",
    area: str = ""
) -> dict:
    destination_text = " ".join(destinations)

    query = f"{hotel_name} {area} {destination_text} {dates} {travellers}"

    return {
        "Booking.com": make_search_url(
            "https://www.booking.com/searchresults.html?ss=", query
        ),
        "Agoda": make_search_url(
            "https://www.agoda.com/search?text=", query
        ),
        "Expedia Hotels": make_search_url(
            "https://www.expedia.com/Hotel-Search?destination=", query
        ),
        "Hotels.com": make_search_url(
            "https://www.hotels.com/Hotel-Search?destination=", query
        ),
        "Airbnb": make_search_url(
            "https://www.airbnb.com/s/", query
        ),
    }


def generate_car_rental_links(
    pickup_location: str,
    dates: str,
    vehicle_type: str = "",
    travellers: str = ""
) -> dict:
    query = f"{pickup_location} car rental {dates} {vehicle_type} {travellers}"

    return {
        "Rentalcars.com": make_search_url(
            "https://www.rentalcars.com/SearchResults.do?search=", query
        ),
        "Kayak Cars": make_search_url(
            "https://www.kayak.com/cars/", query
        ),
        "Expedia Cars": make_search_url(
            "https://www.expedia.com/Cars-Search?locn=", query
        ),
    }


def generate_campervan_links(
    pickup_location: str,
    destinations: list[str],
    dates: str,
    camping_style: str = "",
    vehicle_type: str = ""
) -> dict:
    destination_text = " ".join(destinations)

    query = (
        f"{pickup_location} {destination_text} {dates} "
        f"{camping_style} {vehicle_type} campervan motorhome hire"
    )

    return {
        "Camplify": make_search_url(
            "https://www.camplify.com.au/search?keyword=", query
        ),
        "Apollo Camper": make_search_url(
            "https://www.apollocamper.com/search?keyword=", query
        ),
        "Britz": make_search_url(
            "https://www.britz.com/au/en/search?keyword=", query
        ),
        "Maui Motorhomes": make_search_url(
            "https://www.maui-rentals.com/au/en/search?keyword=", query
        ),
    }


def generate_camping_links(
    destinations: list[str],
    dates: str,
    camping_style: str = "",
    camping_needs: list[str] | None = None
) -> dict:
    if camping_needs is None:
        camping_needs = []

    destination_text = " ".join(destinations)
    needs_text = " ".join(camping_needs)

    query = f"{destination_text} {dates} {camping_style} campsite holiday park {needs_text}"

    return {
        "Hipcamp Australia": make_search_url(
            "https://www.hipcamp.com/en-AU/search?query=", query
        ),
        "BIG4 Holiday Parks": make_search_url(
            "https://www.big4.com.au/search?keyword=", query
        ),
        "Discovery Parks": make_search_url(
            "https://www.discoveryholidayparks.com.au/search?keyword=", query
        ),
        "WikiCamps": make_search_url(
            "https://www.google.com/search?q=", f"WikiCamps {query}"
        ),
    }


def summarise_selected_booking(
    selected_flight: str,
    selected_hotel: str,
    selected_car: str = "",
    selected_camping: str = ""
) -> str:
    return f"""
Selected booking details:

Flight:
{selected_flight}

Accommodation:
{selected_hotel}

Car / Vehicle:
{selected_car}

Camping / Holiday Park:
{selected_camping}
"""