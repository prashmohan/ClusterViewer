#!/usr/bin/env python

import re
import tos # uses a modified version of tos!!!
import Queue
import sys
from threading import Thread
import MySQLdb

# These are the USB receivers for the ACmes
DEVICES = ['serial@/dev/ttyUSB0:115200', 'serial@/dev/ttyUSB1:115200', 'serial@/dev/ttyUSB2:115200']

# Possible central bottleneck. But given the data rate, this should not be an issue.
DATA_QUEUE = Queue.Queue()

RESTART = False

def get_energy(input_line):
    """Extract energy from the output line of tos"""
    start_extract = input_line.find('[')
    stop_extract =  input_line.find(']')
    if stop_extract == -1 or start_extract == -1:
        return 0
    data = input_line[start_extract+1:stop_extract]
    values = data.split(', ')
    
    energy = int(values[2]) * (2**24) + int(values[3]) * (2**16) + int(values[4]) * (2**8) + int(values[5])
    energy = float(energy)/3
    regex = re.compile('.*source: (\d+).*')
    matches = regex.match(input_line)
    if matches == None:
        return 0
    groups = matches.groups()
    if groups == None:
        return 0
    src = groups[0]
    
    return (src, energy,)
    

class DevReader(Thread):
    def __init__(self, dev):
        Thread.__init__(self)
        self.dev = dev
        self.am = tos.AM(dev)        
        
    def run(self):
        """Retrieve values from the device"""
        while not RESTART:
            try:
                input_lines = self.am.read()
                for input_line in input_lines.__str__().splitlines():
                    energy_tuple = get_energy(input_line)
                    DATA_QUEUE.put(energy_tuple)
            except:
                RESTART = True
                raise

class ValPoster(Thread):
    def run(self):
        """Post values in the queue into the MySQL database"""
        while not RESTART:
            try:
                item = DATA_QUEUE.get()
                cursor = conn.cursor()
                stmt = "INSERT INTO loclu_power VALUES(" + item[0] + ", " + str(item[1]) + ", NOW())"
                cursor.execute(stmt)
                cursor.close()
            except:
                RESTART = True
                raise

if __name__ == '__main__':
    # d = DevReader(DEVICES[0])
    # d.run()
    while True:
        threads = Queue.Queue()
        for device in DEVICES:
            thread = DevReader(device)
            threads.put(thread)
            thread.start()
        thread = ValPoster()
        thread.start()
        threads.append(thread)
        for thread in threads:
            thread.join()
