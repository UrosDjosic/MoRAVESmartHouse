    // ── Clock ──────────────────────────────────────────────────────────────────
function updateClock() {
  document.getElementById('clock').textContent = new Date().toTimeString().slice(0, 8);
}
setInterval(updateClock, 1000);
updateClock();

// ── PI Tab switching ───────────────────────────────────────────────────────
let currentDevice = 'pi1';

function switchPI(n) {
  document.querySelectorAll('.pi-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel-view').forEach(p => p.classList.remove('active'));
  document.querySelector(`.pi-tab[data-pi="${n}"]`).classList.add('active');
  document.getElementById(`panel-${n}`).classList.add('active');
  currentDevice = `pi${n}`;
}

function showAlarmPopup(code) {
  const popup = document.getElementById('alarmPopup');
  const text  = document.getElementById('alarmText');

  text.textContent = `🚨 ALARM, DEVICE ${code.toUpperCase()} IS ON ALARM!`;

  popup.classList.remove('hidden');

  setTimeout(() => {
    popup.classList.add('hidden');
  }, 5000);
}
function hideAlarm() {
  const el = document.getElementById(`alarmPopup`);
  if (el) el.remove();
}
// ── Helpers ────────────────────────────────────────────────────────────────
function setEl(id, text, color) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = text;
  if (color) el.style.color = color;
}

function setIndicator(id, state) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = 'status-indicator ' + { on: 'status-on', off: 'status-off', alert: 'status-alert' }[state];
}

function flashCard(code) {
  const card = document.getElementById(`card-${code}`);
  if (!card) return;
  card.classList.remove('updated');
  void card.offsetWidth; // reflow to restart animation
  card.classList.add('updated');
}

function fmtTime(ts) {
  return new Date(parseFloat(ts) * 1000).toLocaleTimeString();
}

function updateRoomTemp(dotId, valId, temp) {
  const dot = document.getElementById(dotId);
  const val = document.getElementById(valId);
  if (dot) dot.style.background = 'var(--green)';
  if (val) val.textContent = temp + '°C';
}

// ── Update UI from data object ─────────────────────────────────────────────
function updateUI(data) {

  // DS1
  if (data.ds1 !== undefined) {
    const open = data.ds1.value === 1;
    setEl('ds1-value', open ? 'OPEN' : 'CLOSED', open ? 'var(--red)' : 'var(--green)');
    setIndicator('ds1-indicator', open ? 'alert' : 'on');
    setEl('ds1-text', open ? 'Door open!' : 'Normal state');
    setEl('ds1-time', 'Updated ' + fmtTime(data.ds1.time));
    flashCard('ds1');
  }

  // DS2
  if (data.ds2 !== undefined) {
    const open = data.ds2.value === 1;
    setEl('ds2-value', open ? 'OPEN' : 'CLOSED', open ? 'var(--red)' : 'var(--green)');
    setIndicator('ds2-indicator', open ? 'alert' : 'on');
    setEl('ds2-text', open ? 'Door open!' : 'Normal state');
    setEl('ds2-time', 'Updated ' + fmtTime(data.ds2.time));
    flashCard('ds2');
  }

  // DUS1
  if (data.dus1 !== undefined) {
    document.getElementById('dus1-value').innerHTML =
      parseFloat(data.dus1.value).toFixed(1) + '<span class="card-unit">cm</span>';
    setIndicator('dus1-indicator', 'on');
    setEl('dus1-text', 'Live reading');
    setEl('dus1-time', 'Updated ' + fmtTime(data.dus1.time));
    flashCard('dus1');
  }

  // DUS2
  if (data.dus2 !== undefined) {
    document.getElementById('dus2-value').innerHTML =
      parseFloat(data.dus2.value).toFixed(1) + '<span class="card-unit">cm</span>';
    setIndicator('dus2-indicator', 'on');
    setEl('dus2-text', 'Live reading');
    setEl('dus2-time', 'Updated ' + fmtTime(data.dus2.time));
    flashCard('dus2');
  }

  // DPIR1
  if (data.dpir1 !== undefined) {
    const motion = data.dpir1.value === 1;
    setEl('dpir1-value', motion ? 'MOTION' : 'IDLE', motion ? 'var(--accent3)' : 'var(--muted)');
    setIndicator('dpir1-indicator', motion ? 'alert' : 'off');
    setEl('dpir1-text', motion ? 'Movement detected!' : 'No movement');
    setEl('dpir1-time', 'Updated ' + fmtTime(data.dpir1.time));
    if (motion) setEl('lastDetect', fmtTime(data.dpir1.time) + ' · DPIR1');
    flashCard('dpir1');
  }

  // DPIR2
  if (data.dpir2 !== undefined) {
    const motion = data.dpir2.value === 1;
    setEl('dpir2-value', motion ? 'MOTION' : 'IDLE', motion ? 'var(--accent3)' : 'var(--muted)');
    setIndicator('dpir2-indicator', motion ? 'alert' : 'off');
    setEl('dpir2-text', motion ? 'Movement detected!' : 'No movement');
    setEl('dpir2-time', 'Updated ' + fmtTime(data.dpir2.time));
    flashCard('dpir2');
  }

  // DPIR3
  if (data.dpir3 !== undefined) {
    const motion = data.dpir3.value === 1;
    setEl('dpir3-value', motion ? 'MOTION' : 'IDLE', motion ? 'var(--accent3)' : 'var(--muted)');
    setIndicator('dpir3-indicator', motion ? 'alert' : 'off');
    setEl('dpir3-text', motion ? 'Movement detected!' : 'No movement');
    setEl('dpir3-time', 'Updated ' + fmtTime(data.dpir3.time));
    flashCard('dpir3');
  }

  // DL
  if (data.dl !== undefined) {
    const on = data.dl.value === 1;
    setEl('dl-value', on ? 'ON' : 'OFF', on ? 'var(--green)' : 'var(--muted)');
    setIndicator('dl-indicator', on ? 'on' : 'off');
    setEl('dl-text', on ? 'Light ON' : 'Light OFF');
    document.getElementById('dl-toggle').checked = on;
    setEl('dl-time', 'Updated ' + fmtTime(data.dl.time));
    flashCard('dl');
  }

  // DB
  if (data.db !== undefined) {
    const on = data.db.value === 1;
    setEl('db-value', on ? 'BUZZING' : 'SILENT', on ? 'var(--red)' : 'var(--muted)');
    setIndicator('db-indicator', on ? 'alert' : 'off');
    setEl('db-text', on ? 'Buzzer active!' : 'Silent');
    document.getElementById('db-toggle').checked = on;
    setEl('db-time', 'Updated ' + fmtTime(data.db.time));
    flashCard('db');
  }

  Object.entries(data).forEach(([code, sensor]) => {
    console.log(sensor);
    if (sensor.measurement === 'alarm' && sensor.value === 1) {
        showAlarmPopup(code);
    }
  });
  // DMS
  if (data.dms !== undefined) {
    setEl('dms-value', String(data.dms.key));
    setIndicator('dms-indicator', 'on');
    setEl('dms-text', 'Input received');
    setEl('dms-time', 'Updated ' + fmtTime(data.dms.time));
    flashCard('dms');
  }
  const dhtSensors = [
    { id: 'dht1', roomTemp: 'room-bedroom', roomTempVal: 'room-bedroom-val' },
    { id: 'dht2', roomTemp: 'room-master', roomTempVal: 'room-master-val' },
    { id: 'dht3', roomTemp: 'room-kitchen', roomTempVal: 'room-kitchen-val' }
  ];
  dhtSensors.forEach(sensor => {
    const dataSensor = data[sensor.id];
    if (dataSensor !== undefined) {
      const tempRaw = parseFloat(dataSensor.temperature);
      const humRaw  = parseFloat(dataSensor.humidity);

      if (!isNaN(tempRaw) && !isNaN(humRaw)) {
        const temp = tempRaw.toFixed(1);
        const hum  = humRaw.toFixed(0);

        document.getElementById(`${sensor.id}-temp`).innerHTML = temp + '<span class="card-unit">°C</span>';
        document.getElementById(`${sensor.id}-hum`).innerHTML  = hum + '<span class="card-unit">%</span>';

        setIndicator(`${sensor.id}-indicator`, 'on');
        setEl(`${sensor.id}-text`, 'Normal');
        setEl(`${sensor.id}-time`, 'Updated ' + fmtTime(dataSensor.time));

        updateRoomTemp(sensor.roomTemp, sensor.roomTempVal, temp);

        lcdData[sensor.id] = temp;
        lcdData[`hum${sensor.id.slice(-1)}`] = hum;

        flashCard(sensor.id);
      }
    }
  });

  // BTN
  if (data.btn !== undefined) {
    const pressed = data.btn.value === 1;
    setEl('btn-value', pressed ? 'PRESSED' : 'NOT PRESSED', pressed ? 'var(--accent3)' : 'var(--muted)');
    setEl('btn-time', 'Updated ' + fmtTime(data.btn.time));
    flashCard('btn');
  }
  if (data['4sd'] !== undefined) {
    document.getElementById('timerDisplay').textContent = data['4sd'].timer;
  }

  // GSG
  if (data.gsg !== undefined) {
    const g = data.gsg;
    const fmt = v => v !== undefined ? parseFloat(v).toFixed(3) : '--';

    document.getElementById('gsg-ax').textContent = fmt(g.accel_x);
    document.getElementById('gsg-ay').textContent = fmt(g.accel_y);
    document.getElementById('gsg-az').textContent = fmt(g.accel_z);
    document.getElementById('gsg-gx').textContent = fmt(g.gyro_x);
    document.getElementById('gsg-gy').textContent = fmt(g.gyro_y);
    document.getElementById('gsg-gz').textContent = fmt(g.gyro_z);

    setIndicator('gsg-indicator', 'on');
    setEl('gsg-text', 'Live reading');
    setEl('gsg-time', 'Updated ' + fmtTime(g.time));
    flashCard('gsg');
  }

  // IR
  if (data.ir !== undefined) {
    setEl('ir-value', 'SIGNAL: ' + data.ir.value, 'var(--pi3)');
    setIndicator('ir-indicator', 'on');
    setEl('ir-text', 'Signal received');
    setEl('ir-time', 'Updated ' + fmtTime(data.ir.time));
    flashCard('ir');
  }

  // Persons count
  if (data.persons !== undefined) {
    const val = String(data.persons.value).padStart(2, '0');
    const device = data.persons.device_name;

    if (device === 'pi2') {
      document.getElementById('personCount2').textContent = val;
    } else {
      document.getElementById('personCount').textContent = val;
    }
  }
  
}

// ── SSE connection ─────────────────────────────────────────────────────────
function connectSSE() {
  const dot    = document.getElementById('sseDot');
  const status = document.getElementById('sseStatus');
  const es     = new EventSource('/api/stream');

  es.onopen = () => {
    dot.className    = 'sse-dot connected';
    status.textContent = 'LIVE';
    status.style.color = 'var(--green)';
  };

  es.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (Object.keys(data).length > 0) updateUI(data);
    } catch (e) {
      console.warn('SSE parse error', e);
    }
  };

  es.onerror = () => {
    dot.className      = 'sse-dot error';
    status.textContent = 'RECONNECTING...';
    status.style.color = 'var(--red)';
    // Browser auto-reconnects SSE
  };
}

connectSSE();

// ── Initial REST load (fills cards before first SSE message arrives) ───────
async function initialLoad() {
  for (const device of ['pi1', 'pi2', 'pi3']) {
    try {
      const res  = await fetch(`/api/sensors/${device}`);
      const data = await res.json();
      updateUI(data);
    } catch (e) {
      console.warn('Initial load failed for', device, e);
    }
  }
}

initialLoad();

// ── Actuator toggle ────────────────────────────────────────────────────────
function toggleActuator(code, state) {
  // TODO: POST to /api/actuator/<code> when you add that endpoint
  console.log(`Actuator ${code} → ${state ? 'ON' : 'OFF'}`);
}

// ── Timer ──────────────────────────────────────────────────────────────────
let timerSeconds  = 300;
let timerInterval = null;
let timerRunning  = false;

function formatTime(s) {
  return String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
}

function timerAction(action) {
  if (action === 'start' && !timerRunning && timerSeconds > 0) {
    timerRunning  = true;
    timerInterval = setInterval(() => {
      if (timerSeconds > 0) {
        timerSeconds--;
        document.getElementById('timerDisplay').textContent = formatTime(timerSeconds);
      } else {
        clearInterval(timerInterval);
        let blink = true;
        timerInterval = setInterval(() => {
          document.getElementById('timerDisplay').textContent = blink ? '00:00' : '    ';
          blink = !blink;
        }, 500);
      }
    }, 1000);
  } else if (action === 'stop') {
    clearInterval(timerInterval);
    timerRunning = false;
  } else if (action === 'reset') {
    clearInterval(timerInterval);
    timerRunning  = false;
    timerSeconds  = 300;
    document.getElementById('timerDisplay').textContent = '05:00';
  }
}

function addTime(s) {
  timerSeconds += s;
  if (!timerRunning)
    document.getElementById('timerDisplay').textContent = formatTime(timerSeconds);
}

// Keep track of current color globally
let currentRGBColor = "#ff4500";

// Called when a color swatch is clicked
function setColor(hex, el) {
  // Update preview
  const preview = document.getElementById('rgbPreview');
  preview.style.background = hex;
  preview.style.boxShadow  = `0 4px 20px ${hex}55`;

  // Update active swatch
  document.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
  el.classList.add('active');

  // Update global
  currentRGBColor = hex;

  // Send MQTT if the light is ON
  const toggle = document.querySelector('.toggle input[type=checkbox]');
  sendRGBCommand(toggle.checked, currentRGBColor);  // ← use actual toggle state
}

// Called when the ON/OFF toggle changes
function toggleRGB(cb) {
  const isOn = cb.checked;
  const color = currentRGBColor;

  // Adjust preview opacity
  const preview = document.getElementById('rgbPreview');
  preview.style.opacity = isOn ? '1' : '0.1';

  // Send MQTT
  sendRGBCommand(isOn, color);
}

// Generic function to send MQTT for BRGB
async function sendRGBCommand(state, color) {
  const hexToName = {
    "#ff4500": "red",
    "#ff6600": "orange",
    "#ffcc00": "yellow",
    "#00ff88": "green",
    "#00e5ff": "cyan",
    "#7c3aed": "purple",
    "#ff1493": "pink",
    "#ffffff": "white"
  };

  try {
    const res = await fetch('/api/mqtt/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: 'actuators', 
        payload: {
          code: 'brgb',
          value: state ? 1 : 0,
          device: currentDevice,
          color: hexToName[color] || 'white',
        }
      })
    });
    const data = await res.json();
    console.log('MQTT sent:', data);
  } catch (err) {
    console.error('Failed to send MQTT', err);
  }
}

// ── LCD cycling ────────────────────────────────────────────────────────────
const lcdData = { dht1: '--', dht2: '--', dht3: '--', hum1: '--', hum2: '--', hum3: '--' };
let lcdIndex  = 0;

const lcdLines = () => [
  [`DHT1: ${lcdData.dht1}°C  ${lcdData.hum1}%RH`, `DHT2: ${lcdData.dht2}°C  ${lcdData.hum2}%RH`],
  [`DHT2: ${lcdData.dht2}°C  ${lcdData.hum2}%RH`, `DHT3: ${lcdData.dht3}°C  ${lcdData.hum3}%RH`],
  [`DHT3: ${lcdData.dht3}°C  ${lcdData.hum3}%RH`, `DHT1: ${lcdData.dht1}°C  ${lcdData.hum1}%RH`],
];

setInterval(() => {
  lcdIndex = (lcdIndex + 1) % 3;
  const lines = lcdLines();
  document.getElementById('lcdLine1').textContent = lines[lcdIndex][0];
  document.getElementById('lcdLine2').textContent = lines[lcdIndex][1];
}, 5000);


function switchGrafana(index, el) {
  document.querySelectorAll('.g-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('grafanaFrame').src = grafanaPanels[index].url;
}

let grafanaPanels = [];

async function buildGrafanaTabs(device) {
  const container = document.getElementById('grafanaTabs');
  if (!container) return;

  try {
    const res = await fetch(`/api/grafana/panels/${device}`);
    grafanaPanels = await res.json();
  } catch (e) {
    console.warn('Failed to load Grafana panels', e);
    return;
  }

  container.innerHTML = '';
  grafanaPanels.forEach((panel, i) => {
    const tab = document.createElement('div');
    tab.className = 'g-tab' + (i === 0 ? ' active' : '');
    tab.textContent = panel.label;
    tab.onclick = () => switchGrafana(i, tab);
    container.appendChild(tab);
  });

  document.getElementById('grafanaFrame').src = grafanaPanels[0].url;
}

// update switchPI to also reload grafana tabs
function switchPI(n) {
  document.querySelectorAll('.pi-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel-view').forEach(p => p.classList.remove('active'));
  document.querySelector(`.pi-tab[data-pi="${n}"]`).classList.add('active');
  document.getElementById(`panel-${n}`).classList.add('active');
  currentDevice = `pi${n}`;
  buildGrafanaTabs(currentDevice);  // ← reload grafana tabs for this PI
}

// initial load for PI1
buildGrafanaTabs('pi1');


//For toggling actuator like a led or brgb or door buzzer
async function toggleActuator(code, state) {
  try {
    const res = await fetch('/api/mqtt/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: 'actuator',   // change to your command topic
        payload: {
          code: code,
          value: state ? 1 : 0,
          device: currentDevice
        }
      })
    });

    const data = await res.json();
    console.log('MQTT sent:', data);

  } catch (err) {
    console.error('Failed to send MQTT', err);
  }
}