import socket
import random

nb = 1  # 0- HIT-"139.162.222.115", 1 - open HiveMQ - broker.hivemq.com
brokers = [str(socket.gethostbyname('vmm1.saaintertrade.com')), str(socket.gethostbyname('broker.hivemq.com'))]
ports = ['80', '1883']
usernames = ['MATZI', '']  # should be modified for HIT
passwords = ['MATZI', '']  # should be modified for HIT

broker_ip = brokers[nb]
broker_port = ports[nb]
port = ports[nb]
username = usernames[nb]
password = passwords[nb]

mzs = ['matzi/', '']

sub_topics = [mzs[nb] + '#', '#']
pub_topics = [mzs[nb] + 'test', 'test']

sub_topic = sub_topics[nb]
pub_topic = pub_topics[nb]

conn_time = 0  # 0 stands for endless loop
topic_prefix = 'pr/home/SmartAquarium'
manag_time = 10  


# SENSOR ID:
r = random.randint(1,10000000)
device_serial_number = 'Smart Aquarium Device '+str(r)  # acquired on purchase

#Chlorine level-ppm = parts per million
base_chlorine = 3.0  
chlorine_max = 4.0 
chlorine_min = 2.0

# Turbidity-NTU unit 
base_turbidity = 0.4  
turbidity_max = 1.0  

# # water pH
# ph_value_max = 8
# ph_value_min = 7
# base_ph_value = 7.2 

# aquarium water temperature - in celsius
base_temperature = 30 
temperature_max = 40 
temperature_min = 20 
