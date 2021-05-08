import asyncio
import hashlib
import pickle
from datetime import datetime

from event import Event


class NodeInfos:
    """
    Class for managing infos of a node.
    """

    def __init__(self, ip, port, writer, reader):
        self.ip = ip
        self.port = port
        self.id = hashlib.sha224((ip + str(port)).encode('utf8')).hexdigest()
        self.writer = writer
        self.reader = reader
        self.lastHeartbeat = datetime.now()
        self.handling_disconnection = False


class BaseNode:
    """
    Base node class for connection handling.
    It can be a contributor or a user.

    This class handles the basic event receiving process. An only event is registered : 'heartbeat'
    The heartbeat assures that the receiving end is alive and responding.

    """

    async def heartbeat_coro(self):
        """
        The heartbeat coroutine. Every self.HEARTBEAT_PERIOD seconds it sends an heartbeat to signal to everyone that it is alive.
        At the same time it checks if someone has not sent an heartbeat for more than self.HEARTBEAT_DISCONNECTED seconds.

        """
        while(True):
            for node_id in list(self.nodes):
                if node_id not in self.nodes :
                    continue
                now = datetime.now()

                if (now - self.nodes[node_id].lastHeartbeat).total_seconds() > self.HEARTBEAT_DISCONNECTED:
                    print(node_id, "seems to be disconnected")
                    await self.disconnected_node(node_id)
                try:
                    await self.send(Event("heartbeat", {"beat": True}), node_id)
                except Exception as e:
                    print(e)   

            await asyncio.sleep(self.HEARTBEAT_PERIOD)

    async def heartbeat_receive(self, event):
        """Used for handling the heartbeat event. Update the last heartbeat of the sender"""

        self.nodes[event.sender].lastHeartbeat = datetime.now()

    def get_node_id(self, addressInfos):
        """Generate an id for a given pair of (address, port)"""
        return hashlib.sha224((addressInfos[0] + str(addressInfos[1])).encode('utf8')).hexdigest()

    async def disconnected_node(self, node_id):
        """Disconnects from the node and remove it from its list."""
        if self.nodes[node_id].handling_disconnection == True:
            return
        self.nodes[node_id].handling_disconnection = True
        writer = self.nodes[node_id].writer
        addr = writer.get_extra_info('peername')
        print(f"Disconnected from {addr!r}")
        writer.close()
        await writer.wait_closed()
        reconnection_tries = 5 
        if self.handle_deconnection:
                if await self.handle_deconnection(node_id):
                    return True
                    self.nodes[node_id].handling_disconnection = False
                else:
                    self.nodes.pop(node_id, None)
                    return False

    async def send(self, event, node_id):
        """
        Send an event to the designed node.
        """

        print("Send", event.name, "to",
              self.nodes[node_id].ip, ':', self.nodes[node_id].port, self.nodes[node_id].id)

        data = pickle.dumps(event)

        writer = self.nodes[node_id].writer

        try:
            writer.write(data)

            await writer.drain()
        except (EOFError, ConnectionResetError) as e:

            addr = writer.get_extra_info('peername')
            node_id = self.get_node_id(addr)
            await self.disconnected_node(node_id)

    async def receive_coro(self, reader, writer):
        """
        Coroutine used for handling the reception of data.
        It tries to transform the data to an event.
        If an event handler is registered for this particular event it is executed with the event as parameter.
        """
        while(True):

            data = await reader.read(1000)
            try:
                event = pickle.loads(data)
            except (EOFError, ConnectionResetError) as e:
                addr = writer.get_extra_info('peername')
                node_id = self.get_node_id(addr)
                await self.disconnected_node(node_id)
                return

            if event.name in self.event_handlers:

                addr = writer.get_extra_info('peername')
                print(f"Received {event.name!r} from {addr!r}")

                node_id = hashlib.sha224(
                    (addr[0] + str(addr[1])).encode('utf8')).hexdigest()
                event.sender = node_id
                await self.event_handlers[event.name](event)

    def on(self, event, coro):
        """Add the coro as the event handler for 'event'"""
        self.event_handlers[event] = coro

    def __init__(self):
        self.event_handlers = {}
        self.nodes = {}
        asyncio.get_event_loop().create_task(self.heartbeat_coro())
        self.on("heartbeat", self.heartbeat_receive)
        self.HEARTBEAT_PERIOD = 5
        self.HEARTBEAT_DISCONNECTED = 10
        self.relay_id = ""
