# 

from ticket.server import app
from ticket.models import TicketRepo, Ticket
import uvicorn



uvicorn.run(app=app, host='0.0.0.0', port=8080)
