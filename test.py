metric = ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co', 'temperature', 'pressure', 'humidity', 'wind']

newlist = []
for i in range(len(metric)):
    newlist.append(metric.pop())

print(newlist)