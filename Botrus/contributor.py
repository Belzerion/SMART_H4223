from contributor_node import ContributorNode
import asyncio
import argparse
from event import Event
import platform
import psutil
import sys
import requests
import streamlit as st 
import docker
from PIL import Image


class Contributor():

    async def job_proposal_handler(self, event: Event):
        if self.working == True:
            nodeId = event.sender
            await self.node.send(Event("job_reponse", {'accepted': False}), nodeId)

        else:
            nodeId = event.sender
            await self.node.send(Event("job_reponse", {'accepted': True}), nodeId)
            self.current_master = nodeId

    async def job_parameters_handler(self, event: Event):

        if event.sender == self.current_master:
            self.swarm_token = event.data["swarm_token"]
            self.network_name = event.data["network_name"]
            self.docker_name = event.data["docker_name"]
            advertise_ip = event.data["advertise_ip"]
            # TODO
            # set-up docker and launch spark-woker

            self.client.swarm.leave(force=True)
            try:
                self.client.containers.list(filters={"name": self.docker_name}, all=True)[0].remove(force=True)
            except:
                print('nothing to kill')

            self.client.swarm.join(remote_addrs=[self.node.nodes[event.sender].ip],
                                   join_token=self.swarm_token, advertise_addr=advertise_ip, listen_addr=self.LISTEN_IP)
            self.client.containers.run(image='bde2020/spark-worker:3.1.1-hadoop3.2',
                                       detach=True,
                                       name=self.docker_name,
                                       environment=["SPARK_PUBLIC_DNS=" + self.node.nodes[event.sender].ip],
                ports={
                                        8081: 8081
                          },
                hostname=self.docker_name,
                network="spark-net",
                auto_remove=True)
            await self.send_worker_ready()

    async def send_worker_ready(self):

        await self.node.send(Event("worker_ready", {}), self.current_master)

    async def start(self):
        requests.post("http://" + self.relay_address + ":8889", json=self.systemInfo)

    async def handle_deconnection(self, node_id):
        print("Disconnedted from master, available again")
        self.working = False

    """Constructor for the contributor class"""

    def __init__(self, relay_address: str, listen_ip: str, nickname: str):
        self.node = ContributorNode()
        asyncio.create_task(self.node.start())
        self.working = False
        self.node.on('job_proposal', self.job_proposal_handler)
        self.node.on("job_parameters", self.job_parameters_handler)
        self.systemInfo = {}
        self.relay_address = relay_address
        self.current_master = ""
        self.swarm_token = ""
        self.network_name = "spark-net"
        self.docker_name = ""
        self.nickname = ""
        self.node.handle_deconnection = self.handle_deconnection
        self.client = docker.from_env()
        self.LISTEN_IP = listen_ip

    """getSystemInfo add cpu, ram and gpu specs to systemInfo"""

    
    def getSystemInfo(self):
        self.systemInfo['processor']=platform.processor()
        self.systemInfo['cpu_core']=psutil.cpu_count(logical=False)
        self.systemInfo['cpu_thread']=psutil.cpu_count(logical=True)
        
        cpu_frequency = psutil.cpu_freq()
        self.systemInfo['cpu_max_freq_mghz']=cpu_frequency.current
        self.systemInfo['cpu_min_freq_mghz']=cpu_frequency.min

        #battery = psutil.sensors_battery()
        #self.systemInfo['battery_percentage']=round(battery.percent, 1)
        #Par default, cette fonctionnalité est désactivé sur windows10, donc pas utilisé ici.
        #self.systemInfo['battery_time_left_hr']=round(battery.secsleft,2)
        #self.systemInfo['power_pluged']=battery.power_plugged
        
        self.systemInfo['total_ram_gb']=round(psutil.virtual_memory().total/(1024.0 **3))


if __name__ == "__main__":

    st.title("Botrus contributing")
    image = Image.open('grape.jpg')

    st.image(image, caption='Using peer to peer technology to train large models',width=100) 




    # gives a single float value
    nickname_ui = st.text_input("Nickname", "")
    relay_host_ui = st.text_input("IP of the relay host", "") 
    listen_ip_ui = st.text_input("Listen IP", "")
    parser = argparse.ArgumentParser(description='Worker Information')
    parser.add_argument('--nickname', dest='nickname', type=str,
                        help='Nickname of the future slav... euh worker sorry', default="")
    parser.add_argument('--relay_host', dest='relay_host',
                        type=str, help='IP of the relay host', default='127.0.0.1')
    parser.add_argument('--listen_ip', dest='listen_ip',
                        type=str, help='Listen IP', default="")

    args = parser.parse_args()
    relay_host = args.relay_host
    nickname = args.nickname
    listen_ip = args.listen_ip

    print("Nickname : "+nickname)
    print("Relay host : "+relay_host)
    print("Listen IP : "+listen_ip)
    if st.button("report to the network"):
        relay_host = relay_host_ui
        nickname = nickname_ui
        listen_ip = listen_ip_ui
        async def main():
            """
            """
            c = Contributor(relay_host, listen_ip, nickname)
            c.getSystemInfo()
            print(c.systemInfo)
            await c.start()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.get_event_loop().create_task(main())
        asyncio.get_event_loop().run_forever()

     
