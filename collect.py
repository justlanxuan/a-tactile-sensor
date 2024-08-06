import serial

import csv

COUNT = 100
distances = []
count = 0
while count < COUNT:
    received_string = ser.readline().decode('utf-8').strip()

    start_index = received_string.find(':') + 1
    end_index = received_string.find('mm')

    if start_index != -1 and end_index != -1:
        number_str = received_string[start_index:end_index].strip()
        try:
            number = int(number_str)
            distances.apppend(number)
            count += 1
        except ValueError:
            print("Error: Could not convert the extracted value to an integer")
    # else:
    #     print("Error: Pattern not found in the received string")

with open('distances.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(distances)   # 写入数据

ser.close()