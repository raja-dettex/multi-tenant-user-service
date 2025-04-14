from typing import Optional, Dict, List
import asyncio

class TicketRequest:
    tenant_name: str
    subject: str
    description: str
    status: str = 'open'
    assignee: Optional[str] = None
    def __init__(self, tenant_name: str, subject: str, description: str, status: str = 'open', assignee: Optional[str] = None):
        self.tenant_name = tenant_name
        self.subject = subject
        self.description = description
        self.status = status
        self.assignee = assignee

class Ticket: 
    id: int
    tenant_name: str
    subject: str
    description: str
    status: str
    assignee: str
    
    def __init__(self, id: int, tenant_name: str, subject: str, description: str, status: str = 'open', assignee: Optional[str] = None):
        self.id = id
        self.tenant_name = tenant_name
        self.subject = subject
        self.description = description
        self.status = status
        self.assignee = assignee

class TicketEvent:
    event: str
    ticket: Ticket
    def __init__(self, event: str, ticket: Ticket):
        self.event = event
        self.ticket = ticket
class TicketRepo:
    def __init__(self):
        self.tickets : Dict[str, List[Ticket]] = {}
        self.queue = asyncio.Queue()
        self.current_id = 1
    async def add_ticket(self, ticket_request: TicketRequest):
        ticket = Ticket(id=self.current_id, tenant_name=ticket_request.tenant_name, subject=ticket_request.subject, description=ticket_request.description, status=ticket_request.status)
        print("adding tickets")
        if not self.tickets.get(ticket.tenant_name):
            print('creating new ticket')
            self.tickets[ticket.tenant_name] = [ticket]
            asyncio.create_task(self.queue.put(TicketEvent('added', ticket)))
            self.current_id += 1
            return ticket.id
        if self.tickets.get(ticket.tenant_name) and all(ticket.id != t.id for t in self.tickets[ticket.tenant_name]):
            print('tenant name', ticket.tenant_name)
            self.tickets.get(ticket.tenant_name).append(ticket)
            print('creating task')
            self.current_id += 1
            print('createing add ticket task')
            asyncio.create_task(self.queue.put(TicketEvent('added', ticket)))
            return ticket.id

    async def update_status(self, ticket_id: int, tenant_name: str, status: str): 
        if not self.tickets.get(tenant_name):
            raise ValueError(f"ticket does not exist with the given id: {ticket_id}")
        for (i, ticket) in enumerate(self.tickets.get(tenant_name)):
            if ticket.id == ticket_id:
                self.tickets.get(tenant_name).pop(i)
                ticket.status = status
                self.tickets.get(tenant_name).append(ticket)
                asyncio.create_task(self.queue.put(TicketEvent('updated', ticket)))
    async def delete(self,  ticket_id : int, tenant_name: str):
        if not self.tickets.get(tenant_name):
            raise ValueError(f"ticket does not exist with the given id: {ticket_id}")
        for (i, ticket) in enumerate(self.tickets.get(tenant_name)):
            if ticket.id == ticket_id:
                self.tickets.get(tenant_name).pop(i)

    async def get_all(self, tenant_name):
        return self.tickets.get(tenant_name)
    async def add_all(self, tenant_name: str, tickets: List[Ticket]):
        print('adding all tickets')
        for ticket in tickets:
            await self.add_ticket(ticket)
               