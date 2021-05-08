# Swarm user guide

This project uses Docker swarms to create abstract networks used by Spark nodes

## Table of contents

* [Opened ports](#openedports)
* [Creating the swarm](#creatingtheswarm)
* [Creating an overlay network](#creatinganoverlaynetwork)
* [Launching Apache Spark](#launchingapachespark)

<a name="openedports"/>

## Opened ports

Using swarms needs the following ports to be open and publicly accessible on every server/computer that will be part of the system : 

* **TCP** `2377`
* **TCP** / **UDP** `7946`
* **UDP** `4789`

Furthermore, Spark Web UIs need the following ports :

* For master nodes, **TCP** ``` 8080``` and ```4040```
* For worker nodes, **TCP** ```8081```

<a name="creatingtheswarm"/>

## Creating the swarm

Two scenarios have been identified for creating a swarm.

* The computer has a public IP on one of its interfaces

```bash
docker swarm init --advertise-addr $ADVERTISE_IP --listen-addr $LISTEN_IP
```

```python
client.swarm.init(advertise_addr=ADVERTISE_IP,
                 listen_addr=LISTEN_IP)
```

where ```$ADVERTISE_IP``` and ```$LISTEN_IP``` contain the public IP of the server 

* The computer is hidden behind a router

```bash
docker swarm init --advertise-addr $ADVERTISE_IP --listen-addr $LISTEN_IP
```

```python
client.swarm.init(advertise_addr=ADVERTISE_IP,
                 listen_addr=LISTEN_IP)
```

where ```$ADVERTISE_IP``` contains the public IP of the router and ```$LISTEN_IP``` contains the private IP of the computer.

```swarm init``` will produce an output similar to this (where ```$ADVERTISE_IP``` is the IP address used in the ```--advertise-addr``` option :

```
Swarm initialized: current node (abcdefghijklmnopqrstuv) is now a manager.

To add a worker to this swarm, run the following command:

    docker swarm join --token xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx $ADVERTISE_IP:2377

To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.

```

```python
# Manager side
client.swarm.attrs['JoinTokens']['Worker'] # Contains the join token

# Worker side
client.swarm.join(remote_addrs=[SWARM_MANAGER_IP], join_token=JOIN_TOKEN, advertise_addr=ADVERTISE_IP, listen_addr=LISTEN_IP)
```



The command has to be executed on any server which is needed to join the swarm.

If the server is hidden behind a router, it's required to add ```--advertise-addr $ROUTER_PUBLIC_IP``` in the ```docker swarm join``` command.

<a name="creatinganoverlaynetwork"/>

## Creating an overlay network

The overlay network will allow a seamless communication between swarm node.

```bash
docker network create --driver=overlay --attachable spark-net
```

```python
client.networks.create(name="spark-net", driver="overlay", attachable=True)
```

The ```--attachable``` tag makes the network available for future containers.

<a name="launchingapachespark"/>

## Launching Apache Spark 

### Launching a master node

* The computer has a public IP on one of its interfaces

```bash
docker run --name spark-master \
		--network spark-net \
		-p 8080:8080 \
		-p 4040:4040 \ 
		-h spark-master \
		-e SPARK_PUBLIC_DNS=$PUBLIC_IP \
		-e SPARK_MASTER_HOST=spark-master \
		-d bde2020/spark-master:3.1.1-hadoop3.2

```



* The computer is hidden behind a router

```bash
docker run --name spark-master \
		--network spark-net \
		-p 8080:8080 \
		-p 4040:4040 \ 
		-h spark-master \
		-e SPARK_PUBLIC_DNS=$ROUTER_PUBLIC_IP \
		-e SPARK_MASTER_HOST=spark-master \
		-d bde2020/spark-master:3.1.1-hadoop3.2

```

```python
client.containers.run(image='bde2020/spark-master:3.1.1-hadoop3.2',
                      detach=True,
                      name="spark-master",
                      environment=["SPARK_PUBLIC_DNS=" + "82.65.210.78", 
                                   "SPARK_MASTER_HOST=spark-master"],
                      ports={
                          		8080:8080,
                          		4040:4040
                            },
                      hostname="spark-master",
                      network="spark-net")
                      
```



### Launching a worker node

* The computer has a public IP on one of its interfaces

```bash
docker run --name $SPARK_WORKER_NAME \
		--network spark-net \
		-p 8081:8081 \
		-h $SPARK_WORKER_NAME \
		-e SPARK_PUBLIC_DNS=$PUBLIC_IP \
		-d bde2020/spark-worker:3.1.1-hadoop3.2
```

```python
client.containers.run(image='bde2020/spark-worker:3.1.1-hadoop3.2',
                      detach=True,
                      name="spark-worker",
                      environment=["SPARK_PUBLIC_DNS=" + "146.59.150.169"],
                      ports={
                          		8081:8081
                            },
                      hostname="spark-worker",
                      network="spark-net")
                      
```



* The computer is hidden behind a router

```bash
docker run --name $SPARK_WORKER_NAME \
		--network spark-net \
		-p 8081:8081 \
		-h $SPARK_WORKER_NAME \
		-e SPARK_PUBLIC_DNS=$ROUTER_PUBLIC_IP \
		-d bde2020/spark-worker:3.1.1-hadoop3.2
```



