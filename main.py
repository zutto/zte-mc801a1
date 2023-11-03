import os
import socket
import time
import select
import argparse
import datetime
from mc801a import MC801A
from zte_crypto import hex_md5

STATE=True
#
# toggles the state between 5g/4g/3g and 5g nsa-only
def switch_pref(password, device_ip):
    global STATE
    mc = MC801A(password=password, device_ip=device_ip)
    response = mc.perform_backdoor()

    STATE = True
    if STATE:
        STATE = False
        return mc.change_mode(BearerPreference="LTE_AND_5G", AD=hex_md5(hex_md5(mc.get_version())+mc.get_rd()))
    else:
        STATE = True
        return mc.change_mode(BearerPreference="WL_AND_5G", AD=hex_md5(hex_md5(mc.get_version())+mc.get_rd()))

def init_socket(remote_host, port, timeout=2):
    socket.setdefaulttimeout(timeout)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.settimeout(timeout)
    sock.connect((remote_host, port))
    return sock

def main():
    parser = argparse.ArgumentParser(description='ZTE Main Program')
    parser.add_argument('--zte-password', type=str, required=True, help='ZTE Password')
    parser.add_argument('--zte-host', type=str, required=True, help='ZTE Host')
    parser.add_argument('--zte-remote-host', type=str, default="google.com", help='ZTE Remote Host')
    parser.add_argument('--zte-remote-port', type=int, default=80, help='ZTE Remote Port')
    parser.add_argument('--pause-after-switch', type=int, default=15, help='How long to pause after switching bearer preference')
    args = parser.parse_args()

    if switch_pref(args.zte_password, args.zte_host).lower() != "success":
        print("Incorrect password or wrong ZTE model? (the crypto is not cross compatible)")
        print(f"also ensure that you're not banned on the modem after too many login attempts http://{args.zte_host}/index.html#login")
        return
    remote_host = args.zte_remote_host
    port = args.zte_remote_port
    
    print("Monitoring connection started.")
    socket = None
    start_time = time.time()
    attempt = 0
    while True:
        try:
            current_time = time.time()

            #re-open the connection every 30 seconds, this should probably be a parameter.
            if current_time - start_time >= 30:
                if socket is not None:
                    socket.close()
                socket = None
                start_time = current_time

            if socket is None:
                socket = init_socket(remote_host, port)
       
            # send and receive dummy data..
            r, w, error = select.select([socket], [socket], [], 1)
            if len(r) > 0:
                data = socket.recv(1)
                if not data:
                    raise "DC"
            if len(w) > 0:
                socket.send(b'0')
        except Exception as e:
            print(f"error detected: {e}")
            print(switch_pref(args.zte_password, args.zte_host))
            time.sleep(1)
            print(switch_pref(args.zte_password, args.zte_host))
            current_datetime = datetime.datetime.now()
            print(f"[{current_datetime}]autofix done")
            socket = None

            print(f"sleeping for {args.pause_after_switch + ( 5 * attempt)} (backoff counter: {attempt})")
            time.sleep(args.pause_after_switch +  (5 * attempt))
            attempt += 1
            continue
        attempt = 0
        time.sleep(0.5)

if __name__ == "__main__":
    main()
