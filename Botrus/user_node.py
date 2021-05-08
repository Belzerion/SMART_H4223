import asyncio
from event import Event
from basenode import BaseNode, NodeInfos
import pickle

class UserNode(BaseNode):
    """
    This class adds some specific methods used by users. 
    It inherits the BaseNode class for receiving and sending messages, and maintaining connections.
    """

    def __init__(self, port=8888):

        """
        Constructor for the User class.
        Calls super-constructor and sets port.
        """
        super().__init__()
        self.port = port       
    

    async def add_contributor(self, address):

        """
        Connects to a known contributor.
        BaseNode methods will be used to maintain all connections.
        Relay nodes give information on known nodes, but User nodes have to manage down contributors.
        """
        try:
            reader, writer = await asyncio.open_connection(
                                    address, self.port)
            node = NodeInfos(address, self.port, writer, reader)
            self.nodes[node.id] = node
            print(node.ip, node.port, node.id)
            asyncio.get_event_loop().create_task(self.receive_coro(reader, writer))
            return True, node.id
        except Exception as e:
            print(e)
            return False

    async def start(self):
        """Starts the User node."""
        #await self.add_contributor(server)
        #await self.connect_relay(self.relay_address)
        



if __name__ == "__main__":
    """
    If the class file is called as the main class,
    creates a user and starts on a default address.
    """

    async def main():
        """
        """
        u = UserNode("127.0.0.1")
        await u.start("127.0.0.1")

    asyncio.get_event_loop().create_task(main())
    asyncio.get_event_loop().run_forever()