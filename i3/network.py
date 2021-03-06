import subprocess
from i3pystatus import IntervalModule
from urllib.request import urlopen
import urllib

def internet_on():
    try:
        urlopen('https://baidu.com')
        return True
    except urllib.error.URLError as err:
        return False

def run_command(cmd):
    return subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE).stdout.read().strip().decode('utf-8')

def current_network_connection():
    default_ni = 'down'
    command = "nmcli device status |grep -E -v 'disconnected|docker|bridge' |grep -E 'connected|conectado' |awk '{print $4}'"
    cmd_ni = run_command(command)
    if not cmd_ni:
        return default_ni
    return cmd_ni

def connect_to_network():
    command = "bm-net"
    run_command(command)

class CurrentNetworkConnection(IntervalModule):
    """
    Shows current network interface

    .. rubric:: Available formatters

    * {current_network_interface}

    Requires psutil (from PyPI)
    """

    format = "{current_network_interface}"
    divisor = 1024 ** 2
    color = "#00FF00"
    warn_color = "#FFFF00"
    alert_color = "#FF0000"
    round_size = 1
    down_time = 0
    zombie_time = 0

    settings = (
        ("current_network_interface", "the name of current network connection."),
        ("color", "standard color"),
        ("warn_color",
         "defines the color used when warn percentage is exceeded"),
        ("alert_color",
         "defines the color used when alert percentage is exceeded"),
        ("round_size", "defines number of digits in round"))

    def run(self):
        ni = current_network_connection()
        result = ni
        if ni == 'down':
            color = self.alert_color
            self.down_time = self.down_time + 1
            if self.down_time > 6:
                connect_to_network()
        else:
            self.down_time = 0
            if not internet_on():
                self.zombie_time = self.zombie_time + 1
                if self.zombie_time % 2 == 1:
                   connect_to_network()
            color = self.color

        if self.down_time != 0:
            result = "conn %s for %d secs" % (ni, self.down_time * 5)

        cdict = {
            "current_network_interface": " " + result
        }

        self.data = cdict
        self.output = {
            "full_text": self.format.format(**cdict),
            "color": color
        }
