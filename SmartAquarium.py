import os
import sys
import random
from datetime import datetime
import json
from colorama import Fore
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt

from init import *
from icecream import ic


# from PyQt5.QtCore import QTimer

global current_chlorine, current_turbidity, current_ph_value, current_temperature_value
r = random.randrange(1, 10000000)
update_rate = 5000  # in msec


# Creating a unique Client name 
def generate_client_id(device_id):
    return "IOT_client_SmartAquarium_id" + device_id + '-' + str(r)


def generate_topic(device_id):
    return topic_prefix + '/' + device_id + '/sts'


def display_number(num):
    return format(num, '.2f')


class MqttClient:
    def __init__(self):
        # broker IP adress:
        self.broker = ''
        self.topic = ''
        self.port = ''
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.subscribeTopic = ''
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_connected_to_form = ''
        self.on_disconnected_to_form = ''
        self.CONNECTED = False

    # Setters and getters
    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

    def set_on_disconnected_to_form(self, on_disconnected_to_form):
        self.on_disconnected_to_form = on_disconnected_to_form

    def get_broker(self):
        return self.broker

    def set_broker(self, value):
        self.broker = value

    def get_port(self):
        return self.port

    def set_port(self, value):
        self.port = value

    def get_clientName(self):
        return self.clientname

    def set_clientName(self, value):
        self.clientname = value

    def get_username(self):
        return self.username

    def set_username(self, value):
        self.username = value

    def get_password(self):
        return self.password

    def set_password(self, value):
        self.password = value

    def get_subscribe_topic(self):
        return self.subscribeTopic

    def set_subscribe_topic(self, value):
        self.subscribeTopic = value

    def get_publish_topic(self):
        return self.publishTopic

    def set_publish_topic(self, value):
        self.publishTopic = value

    def get_publish_message(self):
        return self.publishMessage

    def set_publish_message(self, value):
        self.publishMessage = value

    def on_log(self, client, userdata, level, buf):
        print("log: " + buf)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
            self.CONNECTED = True
            self.on_connected_to_form()
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        self.CONNECTED = False
        self.on_disconnected_to_form()
        print("DisConnected result code " + str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("message from:" + topic, m_decode)
        main.subscribeDock.update_mess_win(m_decode)

    def connect_to(self):
        # Init paho mqtt client class
        self.client = mqtt.Client(self.clientname, clean_session=True)  # create new client instance
        self.client.on_connect = self.on_connect  # bind call back function
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)  # connect to broker

    def disconnect_from(self):
        self.client.disconnect()

    def is_connected(self):
        return self.CONNECTED

    def start_listening(self):
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()

    def subscribe_to(self, topic):
        if self.CONNECTED:
            self.client.subscribe(topic)
        else:
            print("Can't subscribe. Connection should be established first")

    def publish_to(self, topic, message):
        if self.CONNECTED:
            self.client.publish(topic, message)
        else:
            print("Can't publish. Connection should be established first")


class ConnectionDock(QDockWidget):
    """Main """

    def __init__(self, mc):
        QDockWidget.__init__(self)

        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.mc.set_on_disconnected_to_form(self.on_disconnected)
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)

        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)

        self.eDeviceID = QLineEdit()
        self.eDeviceID.setText(device_serial_number)  # init device

        self.eUserName = QLineEdit()
        self.eUserName.setText(username)

        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)

        self.eKeepAlive = QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")

        self.eSSL = QCheckBox()

        self.eCleanSession = QCheckBox()
        self.eCleanSession.setChecked(True)

        self.eConnectBtn = QPushButton("Enable/Connect", self)
        self.eConnectBtn.setToolTip("click me to dis/connect")
        self.eConnectBtn.clicked.connect(self.on_button_connect_click)
        self.eConnectBtn.setStyleSheet("background-color: grey")

        self.Chlorine = QLineEdit()
        self.Chlorine.setText('')

        # self.Ph = QLineEdit()
        # self.Ph.setText('')

        self.Turbidity = QLineEdit()
        self.Turbidity.setText('')

        self.Temperature = QLineEdit()
        self.Temperature.setText('')

        formLayout = QFormLayout()
        formLayout.addRow("Device Serial #", self.eDeviceID)
        # formLayout.addRow("pH", self.Ph)
        formLayout.addRow("Temperature (°C)", self.Temperature)
        # formLayout.addRow("Chlorine-ppm", self.Chlorine)
        formLayout.addRow("Turbidity-NTU", self.Turbidity)
        formLayout.addRow("Power", self.eConnectBtn)

        widget = QWidget(self)
        widget.setLayout(formLayout)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle(" ")

    def on_connected(self):
        self.eConnectBtn.setStyleSheet("background-color: green")
        self.setWindowTitle("Connected")

    def on_disconnected(self):
        self.eConnectBtn.setStyleSheet("background-color: red")
        self.setWindowTitle("Disconnected")

    def on_button_connect_click(self):
        if self.mc.is_connected():
            print('disconnecting...')
            self.mc.stop_listening()
            self.mc.disconnect_from()
        else:
            print('connecting...')
            self.mc.set_broker(self.eHostInput.text())
            self.mc.set_port(int(self.ePort.text()))
            clientname = generate_client_id(self.eDeviceID.text())
            print('client name is ' + clientname)
            self.mc.set_clientName(clientname)
            self.mc.set_username(self.eUserName.text())
            self.mc.set_password(self.ePassword.text())
            self.mc.connect_to()
            self.mc.start_listening()


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # Init of Mqtt_client class
        self.mc = MqttClient()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(update_rate)  
        self.setUnifiedTitleAndToolBarOnMac(True)
        self.setGeometry(1000, 200, 400, 150)
        self.setWindowTitle('My Smart Aquarium')
        self.connectionDock = ConnectionDock(self.mc)

        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)

    def update_data(self):
        if not self.mc.is_connected():
            print('not connected, dont send data')
            return

        # chlorine_level = display_number(base_chlorine + random.randrange(-40, 50) / 30)
        # ph_level = display_number(base_ph_value + random.randrange(0, 30) / 30)  # 0->1
        turbidity_level = display_number(base_turbidity + random.randrange(-30, 40) / 60)  # 0->0.5
        temperature_level = display_number(base_temperature + random.randrange(-20, 20))

        # re-render UI
        self.connectionDock.Temperature.setText(temperature_level)
        self.connectionDock.Turbidity.setText(turbidity_level)
        # self.connectionDock.Chlorine.setText(chlorine_level)
        # self.connectionDock.Ph.setText(ph_level)
        
        
        
        if (int(float(temperature_level)) > temperature_max or int(float(temperature_level)) < temperature_min):
            self.connectionDock.Temperature.setStyleSheet("background-color: red")
        else:
            self.connectionDock.Temperature.setStyleSheet("background-color: white")

        # if (int(float(chlorine_level)) > chlorine_max or int(float(chlorine_level)) < chlorine_min):
        #     self.connectionDock.Chlorine.setStyleSheet("background-color: red")
        # else:
        #     self.connectionDock.Chlorine.setStyleSheet("background-color: white")

        if (int(float(turbidity_level)) > temperature_max or int(float(turbidity_level) < 0.2)):
            self.connectionDock.Turbidity.setStyleSheet("background-color: red")
        else:
            self.connectionDock.Turbidity.setStyleSheet("background-color: white")



        

        message = {"turbidity": float(turbidity_level), "temperature": float(temperature_level),
                #    "ph": float(ph_level),"chlorine": float(chlorine_level), 
                   "time": datetime.now().isoformat()}
        

        

        self.send_data(message)
        

    def send_data(self, message):
        msg_json = json.dumps(message)
        topic = generate_topic(self.connectionDock.eDeviceID.text())
        ic(topic, message)
        self.mc.publish_to(topic, msg_json)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
