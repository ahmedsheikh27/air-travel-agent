from pydantic import BaseModel

class AirlineAgentContext(BaseModel):
    passenger_name: str | None = None
    confirmation_number: str | None = None
    seat_number: str | None = None
    flight_number: str | None = None
    departure: str | None = None
    destination: str | None = None
    date_of_flight: str | None = None
    pdf_url: str | None = None 