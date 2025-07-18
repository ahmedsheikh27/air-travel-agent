import random
import string
from agents import function_tool, RunContextWrapper
from models.context import AirlineAgentContext
from io import BytesIO

def generate_flight_number():
    prefix = random.choice(['A', 'B', 'C', 'D', 'E'])
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    return f"{prefix}-{suffix}"

def generate_confirmation_number():
    prefix = random.choice(['u', 'i', 'j', 'b'])
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    return f"{prefix}-{suffix}"

@function_tool
async def update_seat(
    context: RunContextWrapper[AirlineAgentContext], new_seat: str, departure: str, destination: str, date_of_flight: str, passenger_name: str
) -> str:
    """
    Book a seat for the user, generating a random confirmation and flight number.
    Args:
        new_seat: The new seat to update to.
        departure: The departure city.
        destination: The destination city.
        date_of_flight: The date of the flight.
    """
    # Generate and update context
    confirmation_number = generate_confirmation_number()
    flight_number = generate_flight_number()
    context.context.confirmation_number = confirmation_number
    context.context.seat_number = new_seat
    context.context.flight_number = flight_number
    context.context.departure = departure
    context.context.destination = destination
    context.context.date_of_flight = date_of_flight
    context.context.passenger_name = passenger_name
    print("Context after update_seat:", context.context.dict())
    passenger_name = context.context.passenger_name
    return (
        f"Booking confirmed!\n"
        f"Passenger Name: {passenger_name}\n"
        f"Confirmation Number: {confirmation_number}\n"
        f"Flight Number: {flight_number}\n"
        f"Route: {departure} to {destination}\n"
        f"Date of Flight: {date_of_flight}\n"
        f"Seat Number: {new_seat}"
    )

def generate_ticket_pdf(context: AirlineAgentContext):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    import qrcode
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Flight Ticket")

    # Passenger and flight details
    c.setFont("Helvetica", 12)
    y = height - 100
    c.drawString(50, y, f"Passenger Name: {context.passenger_name or 'Unknown'}")
    y -= 25
    c.drawString(50, y, f"Confirmation Number: {context.confirmation_number or '-'}")
    y -= 25
    c.drawString(50, y, f"Flight Number: {context.flight_number or '-'}")
    y -= 25
    c.drawString(50, y, f"Route: {context.departure or '-'} to {context.destination or '-'}")
    y -= 25
    c.drawString(50, y, f"Date of Flight: {context.date_of_flight or '-'}")
    y -= 25
    c.drawString(50, y, f"Seat Number: {context.seat_number or '-'}")

    # Generate QR code for ticket URL
    ticket_url = f"http://localhost:8000/tickets/{context.confirmation_number}.pdf"
    qr = qrcode.make(ticket_url)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_img = ImageReader(qr_buffer)
    # Place QR code on the right side of the ticket details
    qr_size = 120
    c.drawImage(qr_img, width - qr_size - 50, height - qr_size - 60, qr_size, qr_size)

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Thank you for booking with us. Have a safe flight!")

    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# Old version for backward compatibility (if needed elsewhere)
def generate_ticket_pdf_file(context: AirlineAgentContext):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import os

    os.makedirs("tickets", exist_ok=True)
    filename = f"tickets/ticket_{context.confirmation_number}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Flight Ticket")

    # Passenger and flight details
    c.setFont("Helvetica", 12)
    y = height - 100
    c.drawString(50, y, f"Passenger Name: {context.passenger_name or 'Unknown'}")
    y -= 25
    c.drawString(50, y, f"Confirmation Number: {context.confirmation_number or '-'}")
    y -= 25
    c.drawString(50, y, f"Flight Number: {context.flight_number or '-'}")
    y -= 25
    c.drawString(50, y, f"Route: {context.departure or '-'} to {context.destination or '-'}")
    y -= 25
    c.drawString(50, y, f"Date of Flight: {context.date_of_flight or '-'}")
    y -= 25
    c.drawString(50, y, f"Seat Number: {context.seat_number or '-'}")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Thank you for booking with us. Have a safe flight!")

    c.save()
    return filename 