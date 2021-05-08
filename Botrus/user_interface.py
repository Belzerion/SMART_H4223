from event import Event
import tkinter as tk
from PIL import Image
import os
import asyncio
from user import User
import threading
import queue



class Application(tk.Frame):

    def create_cluster(self):

        contributors = self.contributors_list.curselection()
        if len(contributors) < 1:
            tk.messagebox.showerror(title="You must select at least one worker")
            return
        
        for i in range(len(contributors)):
            current_address = self.contributors_list.get(contributors[i])
            self.contributors_labels[current_address] = tk.Label(text=str("Connecting to " + current_address))
            self.contributors_labels[current_address].pack()
            asyncio.run_coroutine_threadsafe(self.user.add_contributor(current_address), self.user_loop)
    
    def messageHandler(self):

        while self.queue.qsize():
            try:

                print("Handling messages")
                
                event : Event = self.queue.get(0)

                event_name = event.name

                print(event_name)

                if event_name == "contributors_fetched":

                    self.contributors_list = tk.Listbox(self, selectmode=tk.MULTIPLE)
                    self.contributors_list.pack()
                    self.create_cluster_button = tk.Button(self, text="Create cluster", command=self.create_cluster)
                    self.create_cluster_button.pack()
                    self.contributors_list.delete(0, tk.END)
                    for ip in event.data:
                        self.contributors_list.insert(tk.END, ip)
                elif event_name == "contributor_connected":
                    
                    label = self.contributors_labels[event.data["address"]]

                    if event.data["success"]:
                       label["text"] = "Connected to " + event.data["address"] + ". Sending work proposal."
                       asyncio.run_coroutine_threadsafe(self.user.send_proposal(event.data["node_id"]), self.user_loop)
                    else:           
                        label["text"] = "Connection to " + event.data["address"] + " failed."
                
                elif event_name == "worker_accepted":
                    label = self.contributors_labels[event.data["address"]]

                    if event.data["success"]:
                       label["text"] = "Worker @" + event.data["address"] + " has accepted proposal. Sending parameters."
                       asyncio.run_coroutine_threadsafe(self.user.send_parameters(event.data["node_id"]), self.user_loop)
                    else:           
                        label["text"] = "Worker @" + event.data["address"] + " refused proposal."

                elif event_name == "worker_ready":
                    label = self.contributors_labels[event.data["address"]]
                    label["text"] = "Worker @"+event.data["address"]+"is connected and ready to go."

                elif event_name == "everyone_ready":
                    self.everyone_ready_label = tk.Label(text=str("All workers are ready, spark instance available at " + event.data["master_address"]))
                    self.everyone_ready_label.pack()

            except Exception as e:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                print(e)
                break


        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(100, self.messageHandler)


    def user_thread(self, event_loop):
        asyncio.set_event_loop(event_loop)
        self.user = User(self.relay_host.get(), self.advertise_ip.get(), self.listen_ip.get(), self.queue)
        event_loop.create_task(self.user.start())
        event_loop.run_forever()

    def launch_user(self):
        
        threading.Thread(target=self.user_thread, args=(self.user_loop, )).start()
        

    def create_widgets(self):
        #self.logoimg = tk.PhotoImage(file="grape.png")
        self.title = tk.Label(self, text="Botrus", bg="white")
        self.title.pack(side="top")

        self.relay_host_label = tk.Label(self, text="Host of the relay")
        self.relay_host =tk.Entry(self)
        self.relay_host.insert(0, "51.178.137.119")

        self.advertise_ip_label = tk.Label(self, text="Public IP on which master is reacheable")
        self.advertise_ip =tk.Entry(self)
        self.advertise_ip.insert(0, "77.192.119.214")

        self.listen_ip_label = tk.Label(self, text="IP on which the master is listening. If behind a router this a private ip else it is the same as the public")
        self.listen_ip =tk.Entry(self)
        self.listen_ip.insert(0, "192.168.0.15")

        self.relay_host_label.pack()
        self.relay_host.pack()
        self.advertise_ip_label.pack()
        self.advertise_ip.pack()
        self.listen_ip_label.pack()
        self.listen_ip.pack()
        
        self.connect_button = tk.Button(self, text="Connect", command=self.launch_user)
        self.connect_button.pack()




        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        super().config(bg="white")
        self.pack()
        self.create_widgets()
        self.user_loop = asyncio.new_event_loop()
        self.user : User
        self.queue = queue.Queue()
        self.running = 1
        self.contributors_labels = {}
        self.messageHandler()



root = tk.Tk()
app = Application(master=root)
app.mainloop()
