# Store known contributors and give a list on user request
import asyncio
from basenode import BaseNode
from basenode import NodeInfos
from event import Event
from bottle import route, run, post, get, request


class Relay():

    # async def contributor_available_coro(self, event):
        
    #     self.contributors[event.sender] = self.nodes[event.sender]
    #     print("Added contributor", event.sender)

    # async def user_connected_coro(self, event):

    #     contributors_data = {}

    #     for contributor_id in self.contributors:
    #         data = {"ip": self.contributors[contributor_id].ip}
    #         contributors_data[contributor_id] = data

    #     print(contributors_data)

    #     available = Event("available_contributors", contributors_data)
    #     await self.send(available, event.sender)
    #     print("Sent contributors to", event.sender)

    def __init__(self, port=8889, interface="0.0.0.0"):
        super().__init__()
        self.port = port
        self.interface = interface
        self.contributors = {}
        # self.on("contributor_available", self.contributor_available_coro)
        # self.on("user_connected", self.user_connected_coro)

    def add_contributor(self,ip,json):
        self.contributors[ip] = {"ip" : ip}
        self.contributors[ip]["systemInfo"]=json

    

    # async def handle_connection(self, reader, writer):
    #     """
    #     Handler method for new connections.
    #     Adds the new node in the node dictionary and creates a task to handle messsages from the new node.
    #     """
    #     addr = writer.get_extra_info('peername')
    #     node = NodeInfos(addr[0], addr[1], writer, reader)
    #     self.nodes[node.id] = node
    #     print(node.ip, node.port, node.id)
    #     await asyncio.create_task(self.receive_coro(reader, writer))

    # async def start(self):

    #     """
    #     Starts the contributor node with the connection handler method and network parameters.
    #     """
    #     server = await asyncio.start_server(
    #         self.handle_connection, self.interface, self.port)
    #     self.server = server
    #     async with server:
    #         await server.serve_forever()


if __name__ == "__main__":
    """
    If the class file is called as the main class,
    creates a contributor and starts on a default address.
    """


    r = Relay()

    @get("/")
    def send_contributors():
        return r.contributors

    @post("/")
    def handle_contributor():
        ip = request.environ.get('REMOTE_ADDR')
        systemInfo=request.json
        r.add_contributor(ip,systemInfo)
        print(r.contributors)
        
    print('r')
    run(host='0.0.0.0', port=8889, debug=True)
