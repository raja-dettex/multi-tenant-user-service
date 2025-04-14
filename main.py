# 

from ticket.server import app
from ticket.models import TicketRepo, Ticket
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # not ["*"]!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uvicorn.run(app=app, host='0.0.0.0', port=8080)
