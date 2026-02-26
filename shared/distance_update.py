import json
import time
from collections import deque
from shared.mqtt import batch_queue,priority_queue
from shared.device import Device


dus1_distances = deque()
dus2_distances = deque()
persons = 0
_alarm_sent = False


def add_distance(distance,code):
    if code == 'dus1':
        if len(dus1_distances) == 3:
            dus1_distances.popleft()
        dus1_distances.append(distance)
        print(dus1_distances)
    else:
        if len(dus2_distances) == 3:
            dus2_distances.popleft()
        dus2_distances.append(distance)
        print(dus2_distances)


def update_persons(settings: Device):
    global _alarm_sent

    direction = check_distance(settings.code)
    if direction is None:
        return

    # ── Update count first ─────────────────────────────────────────────
    update_person_count(direction, settings.code)
    send_update(settings)

    # ── Alarm only when last person leaves ─────────────────────────────
    if persons == 0 and direction == 'leaving':
        if not _alarm_sent:
            send_alarm(settings)
            _alarm_sent = True
    else:
        _alarm_sent = False
    
def check_distance(code):
    distances = deque()
    if code == 'dpir1':
        distances = dus1_distances
    else:
        distances = dus2_distances
    direction = check_direction(distances)
    return direction
    

def check_direction(distances):
    if len(distances) < 3:
        return None
    if distances[0] > distances[1] > distances[2]:
        print("Person entering")
        return 'enter'
    elif distances[0] < distances[1] < distances [2]:
        print("Person leaving")
        return 'leaving'
    else:
        return None
    
def update_person_count(direction,code):
    global persons
    if direction == 'enter':
        persons += 1
    elif direction == 'leaving' and persons > 0:
        persons -= 1
    print(f'Current persons number {persons}')
def send_update(settings : Device):
    payload = {
        'measurement' : 'persons',
        'device_name' : settings.device_name,
        'code' : 'persons',
        'value' : persons,
    }
    batch_queue.put(payload)

def send_alarm(settings:Device):
    payload = {
        'measurement' : 'alarm',
        'device_name' : settings.device_name,
        'code' : settings.code,
        'value' : 1,
    }
    priority_queue.put(payload)