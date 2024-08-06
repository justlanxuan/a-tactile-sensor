import serial
import pandas as pd

filter_name = 'moving_average'
boundary_name = 'test'
COM = 'COM4'
RATE = 115200
NAIVE_DELAY = 2
PERIOD = 5
INIT = 10 # initial distance
HIGH = 30 # anomaly distance
BOUNDARY = 9
BUFF_COUNT = 5
ES_ALPHA = 0.5

def anomaly(number):
    strange = False
    if(number > HIGH):
        strange = True
    return strange
def boundary_selector(name):
    def test(number,buff):
        print(number)
        return buff
    def none(number,buff):
        if number > BOUNDARY:
            print("touching!")
        else:
            print("Normal")
        return buff
    def buff(number,buff):
        if number < BOUNDARY:
            buff += 1
            if buff > BUFF_COUNT:
                print("Touching!")
            else: # change
                print("Normal")
        else:
            buff = 0
            print("Normal")
        return buff
    
    if name == 'none':
        boundary_f = none
    if name == 'test':
        boundary_f = test
    if name == 'buff':
        boundary_f = buff
    return boundary_f


def filter_selector(name):
    def none(number,last_d): # special case of naive
        new_d = last_d[1:]
        new_d.append(number)
        return new_d
    def naive(number,last_d):
        if len(last_d) < NAIVE_DELAY:
            new_d = last_d
            new_d.append(number)
        if len(last_d) >= NAIVE_DELAY:
            new_d = last_d[1:]
            new_d.append(number)
        else:
            print("DEBUG: NAIVE")
        return new_d
    def balance_moving_average(number,last_d):
        new_distance = (last_d[0] * (PERIOD - 1) + number)/PERIOD
        new_d = last_d[1:]
        new_d.append(new_distance)
        return new_d
    def moving_average(number,last_d):
        new_d = last_d
        while(len(new_d) < PERIOD):
            new_d.append(INIT)
        new_d.append(number)
        new_d[0] = new_d[0] + (new_d[-1]-new_d[1])/PERIOD
        new_d[1:] = new_d[2:]        
        return new_d
    def exponential_smoothing(number,last_d):
        new_d = last_d[1:]
        new_d.append(ES_ALPHA*last_d[0] + (1-ES_ALPHA*number))
        return new_d     
    if name == 'none':
        filter_f = none
    if name == 'naive':
        filter_f = naive
    if name == 'balance_moving_average':
        filter_f = balance_moving_average
    if name == 'moving_average':
        filter_f = moving_average
    if name == 'exponential_smoothing':
        filter_f = exponential_smoothing
    return filter_f

# open com
ser = serial.Serial(COM, RATE, bytesize=8, parity='N', stopbits=1, timeout=1)

# filter and boundary functions
filter_f = filter_selector(filter_name)
boundary_f = boundary_selector(boundary_name)
distances = [INIT]
original_data = []
processed_data = []
buff = 0
COUNT = 1000
count = 0
while count < COUNT:
    received_string = ser.readline().decode('utf-8').strip()

    start_index = received_string.find(':') + 1
    end_index = received_string.find('mm')

    if start_index != -1 and end_index != -1:
        number_str = received_string[start_index:end_index].strip()
        try:
            #TOUCH~~
            if count % 100 == 50:
                print("RELEASE ----------------------------------------------------------------------------------------------RELEASE")
            number = int(number_str)
            original_data.append(number)
            print("Original Data: ",number)
            # anomaly detection
            # if (anomaly(number)):
            #    print("STRANGE_VALUE: ",number)
            #    number = INIT

            # filter
            distances = filter_f(number,distances)
            number = distances[0]
            print("Processed Data: ",number)
            # output
            # buff = boundary_f(number,buff)
            processed_data.append(number)
            count += 1
                
        except ValueError:
            print("Error: Could not convert the extracted value to an integer")
    # else:
    #     print("Error: Pattern not found in the received string")
processed_datas = pd.DataFrame(processed_data)
original_datas = pd.DataFrame(original_data)

original_datas.to_csv('original_slice_touch_03.csv', index=False)
processed_datas.to_csv('moving_average_slice_touch_03.csv', index=False)
ser.close()