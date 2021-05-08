###PySpark User guide

##Installation

You must install PySpark on your computer. The version must match the Spark version used (currently 3.1.1).
For PySpark to work, a recent version of java must also be installed.

##Usage

#Get a Spark Session

To create your spark session you must set your spark master to "spark://localhost:7077"
Here is a code snippet for getting a session :
``` 
from pyspark import SparkContext, SparkConf 
appName = "testsparkapp" 
master = "spark://localhost:7077" 
conf = SparkConf().setAppName(appName).setMaster(master)
sc = SparkContext(conf=conf) 

```
#Submit jobs

After that you should be able to use PySpark as you normally do.
