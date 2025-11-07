import argparse
import socket
import threading
import time
import platform
import uuid

PORT = 50000
INTERVAL = 1.0
BUFFER = 4096

def get_local_ips():
    """Try multiple ways to collect likely local IP addresses (IPv4)."""
    ips = set()

    # 1) hostname-derived
    try:
        hostname = socket.gethostname()
        for entry in socket.getaddrinfo(hostname, None):
            addr = entry[4][0]
            if ":" not in addr:  # ignore IPv6
                ips.add(addr)
    except Exception:
        pass

    # 2) try creating a UDP socket to a public IP to learn the outbound IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # doesn't actually send data
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass

    # 3) loopback
    ips.add("127.0.0.1")

    return ips

def make_recv_socket(port):
    """Create and return a socket bound for receiving broadcasts."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Allow address reuse (works differently on Windows vs Unix; both options set)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception:
        pass
    try:
        # On some systems, SO_REUSEPORT helps but isn't available everywhere
        s.setsockopt(socket.SOL_SOCKET, getattr(socket, "SO_REUSEPORT", 0), 1)
    except Exception:
        pass

    # Bind to all interfaces on the chosen port
    s.bind(('', port))
    return s

def make_send_socket():
    """Create and return a socket usable for broadcast sending."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return s

def sender_thread_func(port, interval, stop_event, identity):
    sock = make_send_socket()
    broadcast_addr = ('255.255.255.255', port)

    count = 0
    while not stop_event.is_set():
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msg = f"UDP-BROADCAST-TEST|{identity}|{ts}|count={count}"
        try:
            sock.sendto(msg.encode('utf-8'), broadcast_addr)
        except Exception as e:
            print(f"[send error] {e}")
        count += 1
        stop_event.wait(interval)
    sock.close()

def listener_thread_func(port, stop_event, local_ips):
    sock = make_recv_socket(port)
    sock.settimeout(1.0)
    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(BUFFER)
            src_ip, src_port = addr[0], addr[1]
            # ignore messages from ourselves
            if src_ip in local_ips:
                continue
            try:
                text = data.decode('utf-8', errors='replace')
            except Exception:
                text = repr(data)
            print(f"[recv] {src_ip}:{src_port} -> {text}")
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[recv error] {e}")
            break
    sock.close()

def main():
    parser = argparse.ArgumentParser(description="UDP broadcast test (send+listen).")
    parser.add_argument('--port', type=int, default=PORT)
    parser.add_argument('--interval', type=float, default=INTERVAL, help="seconds between broadcasts")
    parser.add_argument('--mode', choices=['send','listen','both'], default='both')
    args = parser.parse_args()

    # Identity string uses hostname + uuid fragment (helps see which machine)
    host = socket.gethostname()
    identity = f"{host}-{platform.system()}-{str(uuid.getnode())[-6:]}"

    local_ips = get_local_ips()
    print("Local IPs detected (will ignore these):", ", ".join(sorted(local_ips)))
    print(f"Running in mode={args.mode}, port={args.port}, interval={args.interval}s")
    stop_event = threading.Event()
    threads = []

    try:
        if args.mode in ('both','send'):
            t = threading.Thread(target=sender_thread_func, args=(args.port,args.interval,stop_event,identity), daemon=True)
            threads.append(t)
            t.start()
        if args.mode in ('both','listen'):
            t = threading.Thread(target=listener_thread_func, args=(args.port,stop_event,local_ips), daemon=True)
            threads.append(t)
            t.start()

        # keep main thread alive until Ctrl+C
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping...")
        stop_event.set()
        for t in threads:
            t.join(timeout=2)
        print("Stopped.")

if __name__ == '__main__':
    main()