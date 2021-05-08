from user_node import UserNode
import asyncio
from event import Event
import sys
import requests
import docker
import argparse
import queue

class User():

    async def job_response_handler(self, event: Event):
        if event.data['accepted'] == True:
            self.accepted_workers[event.sender] = {
                "accepted": True, "ready": False}

            self.app_queue.put(Event("worker_accepted", {"address" : self.node.nodes[event.sender].ip, "success" : True}))
            await self.send_parameters(event.sender)
        else:
            self.accepted_workers.pop(event.sender, None)
            self.app_queue.put(Event("worker_accepted", {"address" : self.node.nodes[event.sender].ip, "success" : False}))

    async def send_proposal(self, node_id=None):
        if node_id != None:
            await self.node.send(Event("job_proposal", {}), node_id)
        else:
            for node_id in self.node.nodes:
                await self.node.send(Event("job_proposal", {}), node_id)

    async def send_parameters(self, node_id=None):
        if node_id != None:
            await self.node.send(Event("job_parameters", {"advertise_ip" : self.node.nodes[node_id].ip, "swarm_token": self.client.swarm.attrs['JoinTokens']['Worker'], "network_name": "spark-net", "docker_name": node_id}), node_id)
        else:
            for node_id in self.accepted_workers:
                await self.node.send(Event("job_parameters", {"advertise_ip" : self.node.nodes[node_id].ip, "swarm_token": self.client.swarm.attrs['JoinTokens']['Worker'], "network_name": "spark-net", "docker_name": node_id}), node_id)

    async def worker_ready_handler(self, event: Event):

        if event.sender in self.accepted_workers:
            self.accepted_workers[event.sender]["ready"] = True
            self.app_queue.put(Event("worker_ready", {"address" : self.node.nodes[event.sender].ip}))

        everyone_is_ready = True

        for node_id in self.accepted_workers:
            if self.accepted_workers[node_id] == False:
                everyone_is_ready = False
                break

        if everyone_is_ready:
            print("Every worker is ready. Spark master instance is accesible at : spark://localhost:7077")
            self.app_queue.put(Event("everyone_ready", {"master_address" : "spark://localhost:7077"}))

    async def add_contributor(self, address):
        print("Adding contributor at", address)
        success, node_id= await self.node.add_contributor(address)
        
        if success == True:
            self.app_queue.put(Event("contributor_connected", {"address": address, "success" : True, "node_id": node_id}))
            print("event sent")
        else:
            self.app_queue.put(Event("contributor_connected", {"address": address, "success" : False}))

    async def handle_deconnection(self, node_id):
        print("Disconneted from", node_id, ".Attempting to reconnected")
        reconnection_tries = 5
        for i in range(reconnection_tries):
                if await self.node.add_contributor(self.node.nodes[node_id].ip):
                    print("Re-connection suceeded on attempt ", i)
                    await self.send_proposal(node_id)
                    return True
                else:
                    await asyncio.sleep(2)
           
        
        print("Failed to re-connect")
        return False

    async def start(self):

        print("User starting")
        print("Requesting users from relay")
        contributors = requests.get(
            "http://" + self.relay_address + ":8889").json()
        print(asyncio.get_event_loop())
        self.app_queue.put(Event("contributors_fetched", contributors))
        # for node_id in contributors:
        #     await self.node.add_contributor(contributors[node_id]["ip"])

        # await self.send_proposal()
        # TODO
        # Start up the docker image, create swarm, create network
        self.client.swarm.leave(force=True)
        try:
            self.client.containers.list(filters ={ "name": "spark-master"}, all=True)[0].remove(force=True)
        except :
            print('got no image to kill')
        self.client.swarm.init(advertise_addr=self.ADVERTISE_IP, listen_addr=self.LISTEN_IP)
        self.client.networks.create(name="spark-net", driver="overlay", attachable=True)
        self.client.containers.run(image='bde2020/spark-master:3.1.1-hadoop3.2',
                      detach=True,
                      name="spark-master",
                      environment=["SPARK_PUBLIC_DNS=" + self.ADVERTISE_IP, 
                                   "SPARK_MASTER_HOST=spark-master"],
                      ports={
                          		8080:8080,
                          		4040:4040,
                                7077:7077
                            },
                      hostname="spark-master",
                      network="spark-net",
                      auto_remove=True)

    def __init__(self, relay_address: str, advertise_ip:str, listen_ip:str, app_queue : queue.Queue):
        self.node = UserNode()
        self.relay_address = relay_address
        self.accepted_workers = {}
        self.node.on('job_reponse', self.job_response_handler)
        self.node.on("worker_ready", self.worker_ready_handler)
        self.swarm_token = ""
        self.network_name = ""
        self.ADVERTISE_IP = advertise_ip
        self.LISTEN_IP = listen_ip
        self.node.handle_deconnection = self.handle_deconnection
        self.client=docker.from_env()
        self.app_queue = app_queue
        



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Master Information')
    parser.add_argument('--advertise_ip', dest='advertise_ip', type=str,
                        help='Public IP on which master is reacheable', default="", required=True)
    parser.add_argument('--relay_host', dest='relay_host',
                        type=str, help='IP of the relay host', default='127.0.0.1')
    parser.add_argument('--listen_ip', dest='listen_ip',
                        type=str, help='Listen IP', default="", required=True)

    args = parser.parse_args()
    relay_host = args.relay_host
    advertise_ip = args.advertise_ip
    listen_ip = args.listen_ip

    async def main():
        """
        """
        u = User(relay_host, advertise_ip, listen_ip)
        await u.start()

    asyncio.get_event_loop().create_task(main())
    asyncio.get_event_loop().run_forever()
from user_interface import Application