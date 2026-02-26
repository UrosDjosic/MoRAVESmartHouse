from collections import deque
latest_dht = deque()


def add_to_latest(code, temp, hum):
    # Remove existing record with the same code
    global latest_dht
    latest_dht = deque([record for record in latest_dht if record['code'] != code])
    
    # Append the new record
    latest_dht.append({
        'code': code,
        'temp': temp,
        'hum': hum
    })


def get_latest_by_code():
    for record in reversed(latest_dht):  # reversed to get most recent first
        return record