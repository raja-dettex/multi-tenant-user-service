from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from .models import TicketRepo, Ticket
from time import sleep
app = FastAPI()

import asyncio

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
repo = TicketRepo()

async def tickets():
    for i in range(10):
        await repo.add_ticket(Ticket(i, f'oswarld_corp', f'sub{i}', f'desc{i}'))


#asyncio.run(tickets())
import json
import asyncio
from .models import TicketRequest
async def generate_tickets(tenant_name: str):
    print("generating")
    yield ": heartbeat\n\n"
    tickets = await repo.get_all(tenant_name)
    print(tickets)
    if tickets is not None:
        for ticket in tickets:
            ticket_json = json.dumps({'id' : ticket.id, 'tenant_name': ticket.tenant_name, 'subject': ticket.subject
                                      , 'description': ticket.description, 'status': ticket.status})
            yield f"event: TicketEvent\ndata: {ticket_json}\n\n"
            await asyncio.sleep(0.5)
    while True:
        print("enters while")
        ticket_event = await repo.queue.get()
        print('DEBUG type:', type(ticket_event.ticket))
        print('DEBUG dir:', dir(ticket_event.ticket))
        if ticket_event.ticket.tenant_name  != tenant_name:
            continue
        event_name = 'Added' if ticket_event.event == 'added' else 'Updated'
        ticket = ticket_event.ticket
        data = json.dumps({'id' : ticket.id, 'tenant_name': ticket.tenant_name, 'subject': ticket.subject
                                    , 'description': ticket.description, 'status': ticket.status})
        yield f"event: Ticket{event_name}\ndata: {data}\n\n"
        await asyncio.sleep(1)

@app.get('/events/{tenant_name}')
async def get_events(request: Request):
    name = request.path_params.get('tenant_name')
    print(name)
    return StreamingResponse(generate_tickets(name), media_type='text/event-stream')
    

@app.post('/add')
async def add(request: Request):
    print('received request')
    data = await request.json()
    print(data)
    ticket = TicketRequest(
        tenant_name=data["tenant_name"],
        subject=data["subject"],
        description=data["description"],
        status=data['status']
    )
    id = await repo.add_ticket(ticket)
    return JSONResponse(status_code=201, content={'message' : f'ticket has been create with id: {id}'})


@app.post('/add/all')
async def add_all(request: Request):
    tickets_data = await request.json()
    print("tenant name", tickets_data['tenant_name'])
    tickets = [TicketRequest(
        tenant_name=data["tenant_name"],
        subject=data["subject"],
        description=data["description"]
    ) for data in tickets_data['tickets']]
    await repo.add_all(tickets=tickets, tenant_name=tickets_data['tenant_name'])
    return JSONResponse(status_code=201, content={'message' : 'tickets have been created'})


@app.post('/update')
async def update_ticket_status(request: Request):
    data = await request.json()
    print(data)
    await repo.update_status(ticket_id=int(data['ticketId']), tenant_name=data['tenant_name'], status=data['status'])
    return JSONResponse(status_code=201, content={'message' : 'tickets status have been updated'})
    
@app.delete('/delete/{tenant_name}/{ticket_id}')
async def delete_ticket(tenant_name: str,  ticket_id: int):
    await repo.delete(ticket_id=ticket_id, tenant_name=tenant_name)
    return JSONResponse(status_code=200, content={'message' : 'ticket has been deleted'})