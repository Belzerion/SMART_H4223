# Jupyter user guide

The project uses a custom Jupyter docker image to make deploying works more easily. As the Spark master and workers use Python 3.7 and Jupyter images use 3.8 by default, we have to add an additional step to ensure compatibility. 

## Introduction

After creating a swarm and introducing workers, the master node launches a Jupyter instances. Thus, the user has access to a simple web interface to submit Python jobs.

## Build the image

Go to ```heptasmart/jupyter-pyspark-37``` and run the following command to build the custom Docker image :

```bash
docker build . -t jupyter/pyspark-notebook:python37
```

Once done, the image will be stored locally.

## Launch a container

This step has to be done after having set up the Swarm, overlay network and Spark instances.

### Command line interface

```bash
docker run -d \
		--network spark-net \
		-p $JUPYTER_PORT:8888 \
		-v $JUPYTER_MOUNT_DIR:/home/jovyan/work/mnt \
		--name "jupyter" \
		-e JUPYTER_TOKEN=$JUPYTER_TOKEN \
		jupyter/pyspark-notebook:python37

```

### docker-py

```python
client.containers.run(image='jupyter/pyspark-notebook:python37',
                      detach=True,
                      name="jupyter",
                      environment=["JUPYTER_TOKEN=" + jupyter_token],
                      ports={
                          		jupyter_port:8888
                      },
                      volumes={
						jupyter_mount_dir: {
                            'bind':'/home/jovyan/work/mnt',
                            'mode':'rw'
                        }                      	    
                      },
                      network="spark-net")
```

## Usage

Open a browser and go to ```$MASTER_IP:$JUPYTER_PORT/?token=$JUPYTER_TOKEN```. You should land on Jupyter's main web page.

In the ```work``` folder, you'll find a file called ```spark_context_example.py```. It contains a basic block of code used to create a connection to an Apache Spark master with hostname ```spark-master```.

The needed kernel for interacting with Spark instances is called ```python37```. You can either select it when creating a notebook, or by going into ```Kernel -> Change kernel``` in the notebook menu bar.

## Installing dependencies

Dependencies can be installed either with ```pip``` or ```conda```. Both instruction blocks have to be run in the notebook itself.

(This part is fully based on a great article by Jake van der Plas, which can be found [here](https://jakevdp.github.io/blog/2017/12/05/installing-python-packages-from-jupyter/))

### With ```pip```

```python
import sys
!{sys.executable} -m pip install $PACKAGE_NAME
```

### With ```conda```

```python
import sys
!conda install --yes --prefix {sys.prefix} $PACKAGE_NAME
```

