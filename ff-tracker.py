import socket
import threading
import time

# Configuration
PROXY_PORT = 8080
DNS_PORT = 53
GAME_DOMAINS = ['ff.garena.com', 'gs.ff.garena.com', 'dlff.garena.com']

def handle_dns_query(data, addr, sock):
    """Simple DNS interceptor"""
    try:
        # Parse domain (very simplified)
        domain_start = data[12:].find(b'\x00')
        domain = data[12:12+domain_start].decode(errors='ignore')
        
        if any(game in domain for game in GAME_DOMAINS):
            # Redirect to our proxy
            response = data[:2] + b'\x81\x80' + data[4:6] + b'\x00\x01' + data[8:] + b'\xc0\x0c' + b'\x00\x01\x00\x01\x00\x00\x00\x3c' + b'\x00\x04' + socket.inet_aton("127.0.0.1")
            sock.sendto(response, addr)
            print(f"[DNS] Intercepted: {domain} -> 127.0.0.1")
        else:
            # Forward to real DNS
            sock.sendto(data, ("8.8.8.8", 53))
    except Exception as e:
        pass

def dns_server():
    """UDP DNS server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', DNS_PORT))
    print(f"[DNS] Listening on port {DNS_PORT}")
    
    while True:
        data, addr = sock.recvfrom(512)
        threading.Thread(target=handle_dns_query, args=(data, addr, sock)).start()

def proxy_server():
    """TCP proxy for game traffic"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', PROXY_PORT))
    server.listen(10)
    print(f"[PROXY] Listening on port {PROXY_PORT}")
    
    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_proxy, args=(client,)).start()

def handle_proxy(client):
    """Handle proxy connection"""
    try:
        # This is where packet interception would happen
        data = client.recv(4096)
        
        # For now, just echo (replace with actual interception)
        client.send(data)
    except Exception as e:
        pass
    finally:
        client.close()

if __name__ == "__main__":
    print("╔══════════════════════════════════════╗")
    print("║   FF Tracker - GitHub Codespaces      ║")
    print("║   Temporary DNS Interceptor           ║")
    print("╚══════════════════════════════════════╝")
    print(f"DNS Port: {DNS_PORT}")
    print(f"Proxy Port: {PROXY_PORT}")
    print("Note: This is a testing setup")
    print("GitHub public URL will be shown in terminal")
    print("-" * 40)
    
    # Start DNS in background
    dns_thread = threading.Thread(target=dns_server, daemon=True)
    dns_thread.start()
    
    # Start proxy in foreground
    proxy_server()
