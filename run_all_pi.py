import subprocess
import json
import time
import sys
import shutil
import threading

processes = []

def pipe_output(pi, proc):
    for line in proc.stdout:
        print(f"[PI{pi}] {line}", end='')

def run_all_pis(settings_path='settings.json'):
    for pi in [1, 2, 3]:
        pi_settings = f'settings_pi{pi}.json'
        shutil.copy(settings_path, pi_settings)

        with open(pi_settings, 'r') as f:
            s = json.load(f)
        s['pi'] = pi
        s['device_name'] = f'pi{pi}'
        s['mqtt']['client_id'] = f'pi{pi}_sender'  # ← unique sender
        s['mqtt']['topic'] = f'pi{pi}'  
        with open(pi_settings, 'w') as f:
            json.dump(s, f, indent=2)

        proc = subprocess.Popen(
            [sys.executable, 'main.py', '--settings', pi_settings],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append((pi, proc))
        print(f"✅ PI {pi} started (PID {proc.pid})")

        # ── each process gets its own reader thread ────────────────────────
        t = threading.Thread(target=pipe_output, args=(pi, proc), daemon=True)
        t.start()

        time.sleep(1)

    print("\n🚀 All PIs running. Press Ctrl+C to stop all.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all PIs...")
        for pi, proc in processes:
            proc.terminate()
        for pi, proc in processes:
            proc.wait()
            print(f"❌ PI {pi} stopped")

if __name__ == "__main__":
    run_all_pis()