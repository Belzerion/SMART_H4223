# Accept and maintain connections
# Advertise self to relays so new users can connect
import asyncio
import pickle
from event import Event
from basenode import BaseNode, NodeInfos


class ContributorNode(BaseNode):
    """
    This class adds some specific methods used by contributors. 
    It inherits the BaseNode class for receiving and sending messages, and maintaining connections.
    """

    def __init__(self, port=8888, interface="0.0.0.0"):
        """
        Constructor for the Contributor class.
        Calls super-constructor and sets port, interface, relay address and initializes user list.
        """
        super().__init__()
        self.port = port
        self.interface = interface


    async def handle_connection(self, reader, writer):
        """
        Handler method for new connections.
        Adds the new node in the node dictionary and creates a task to handle messsages from the new node.
        """
        addr = writer.get_extra_info('peername')
        node = NodeInfos(addr[0], addr[1], writer, reader)
        self.nodes[node.id] = node
        print(node.ip, node.port, node.id)
        await asyncio.create_task(self.receive_coro(reader, writer))

    async def start(self):

        """
        Starts the contributor node with the connection handler method and network parameters.
        """
        server = await asyncio.start_server(
            self.handle_connection, self.interface, self.port)
        self.server = server
        
        #await self.connect_relay(self.relay_address)

        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    """
    If the class file is called as the main class,
    creates a contributor and starts on a default address.
    """

    async def main():
        c = ContributorNode("127.0.0.1")
        await c.start()

    asyncio.run(main())
