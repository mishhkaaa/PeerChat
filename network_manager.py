"""
Network Manager Module
Handles all P2P networking functionality including connections, message handling, and peer management.
"""

import socket
import threading
import json
import uuid
import time
import base64


class NetworkManager:
    def __init__(self, app):
        self.app = app
        self.listen_socket = None
        self.peer_connections = {}  # {(ip, port): socket}
        self.known_peers = set()    # {(ip, port)}
        self.running = False
        self.message_cache = set()  # To prevent message loops
        
    def get_local_ip(self):
        """Get the local IP address"""
        try:
            # Connect to a remote server to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
    
    def start_listening(self, port):
        """Start listening for incoming peer connections"""
        try:
            self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.listen_socket.bind(('0.0.0.0', port))
            self.listen_socket.listen(10)
            
            self.running = True
            threading.Thread(target=self.accept_connections, daemon=True).start()
            
            return True, f"Listening on {self.get_local_ip()}:{port}"
            
        except Exception as e:
            return False, f"Failed to start listening: {str(e)}"

    def connect_to_peer(self, peer_ip, peer_port, my_port, nickname):
        """Connect to a specific peer"""
        try:
            peer_addr = (peer_ip, peer_port)
            
            # Don't connect to ourselves
            if peer_ip == self.get_local_ip() and peer_port == my_port:
                return False, "Cannot connect to yourself"
                
            # Don't connect if already connected
            if peer_addr in self.peer_connections:
                return False, f"Already connected to {peer_ip}:{peer_port}"
                
            # Create connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(peer_addr)
            
            # Send handshake
            handshake = {
                "type": "handshake",
                "nickname": nickname,
                "my_port": my_port,
                "known_peers": list(self.known_peers)
            }
            self.send_json_message(sock, handshake)
            
            # Add to connections
            self.peer_connections[peer_addr] = sock
            self.known_peers.add(peer_addr)
            
            # Start handling this connection
            threading.Thread(target=self.handle_peer_connection, args=(sock, peer_addr), daemon=True).start()
            
            return True, f"Connected to {peer_ip}:{peer_port}"
            
        except Exception as e:
            return False, f"Failed to connect to peer: {str(e)}"

    def accept_connections(self):
        """Accept incoming peer connections"""
        while self.running:
            try:
                sock, addr = self.listen_socket.accept()
                # Handle the new connection in a separate thread
                threading.Thread(target=self.handle_new_peer, args=(sock, addr), daemon=True).start()
                
            except Exception as e:
                if self.running:
                    pass  # Connection handling error, continue listening
                break

    def handle_new_peer(self, sock, addr):
        """Handle initial handshake with a new peer"""
        try:
            # Receive handshake
            data = self.receive_json_message(sock)
            if data and data.get("type") == "handshake":
                peer_nickname = data.get("nickname", "Unknown")
                peer_listening_port = data.get("my_port", addr[1])
                peer_known_peers = data.get("known_peers", [])
                
                peer_addr = (addr[0], peer_listening_port)
                
                # Don't add ourselves or already connected peers
                my_addr = (self.get_local_ip(), self.app.my_port)
                if peer_addr not in self.peer_connections and peer_addr != my_addr:
                    self.peer_connections[peer_addr] = sock
                    self.known_peers.add(peer_addr)
                    
                    # Send our handshake response
                    response = {
                        "type": "handshake_response",
                        "nickname": self.app.nickname,
                        "my_port": self.app.my_port,
                        "known_peers": list(self.known_peers)
                    }
                    self.send_json_message(sock, response)
                    
                    # Merge peer lists
                    for known_peer in peer_known_peers:
                        if tuple(known_peer) not in self.known_peers and tuple(known_peer) != my_addr:
                            self.known_peers.add(tuple(known_peer))
                    
                    # Start handling this connection
                    threading.Thread(target=self.handle_peer_connection, args=(sock, peer_addr), daemon=True).start()
                    
                    # Notify the app
                    self.app.on_peer_joined(peer_nickname, addr[0], peer_listening_port)
                    
        except Exception as e:
            sock.close()

    def handle_peer_connection(self, sock, peer_addr):
        """Handle messages from a connected peer"""
        while self.running:
            try:
                data = self.receive_json_message(sock)
                if not data:
                    break
                    
                msg_type = data.get("type")
                
                if msg_type == "chat_message":
                    self.handle_chat_message(data, peer_addr)
                elif msg_type == "nickname_change":
                    self.handle_nickname_change(data, peer_addr)
                elif msg_type == "file_transfer":
                    self.handle_file_transfer_message(data, peer_addr)
                elif msg_type == "peer_list_update":
                    self.handle_peer_list_update(data, peer_addr)
                    
            except Exception as e:
                break
        
        # Clean up connection
        if peer_addr in self.peer_connections:
            del self.peer_connections[peer_addr]
        if peer_addr in self.known_peers:
            self.known_peers.remove(peer_addr)
        sock.close()
        
        # Notify the app
        self.app.on_peer_disconnected(peer_addr[0], peer_addr[1])

    def handle_chat_message(self, data, sender_addr):
        """Handle incoming chat messages"""
        message_id = data.get("message_id")
        message = data.get("message", "")
        
        # Prevent message loops
        if message_id in self.message_cache:
            return
        
        self.message_cache.add(message_id)
        
        # Display message
        self.app.on_message_received(message, 'peer')
        
        # Broadcast to other peers (flooding)
        self.broadcast_message(data, exclude_addr=sender_addr)

    def handle_nickname_change(self, data, sender_addr):
        """Handle nickname change messages"""
        message_id = data.get("message_id")
        old_nick = data.get("old_nickname", "Unknown")
        new_nick = data.get("new_nickname", "Unknown")
        
        # Prevent message loops
        if message_id in self.message_cache:
            return
            
        self.message_cache.add(message_id)
        
        # Display nickname change
        self.app.on_message_received(f"[System] {old_nick} changed nickname to {new_nick}", 'system')
        
        # Broadcast to other peers
        self.broadcast_message(data, exclude_addr=sender_addr)

    def handle_file_transfer_message(self, data, sender_addr):
        """Handle file transfer messages"""
        message_id = data.get("message_id")
        
        # Prevent message loops
        if message_id in self.message_cache:
            return
            
        self.message_cache.add(message_id)
        
        filename = data.get("filename", "unknown")
        file_data_b64 = data.get("file_data", "")
        
        # Notify the app about file transfer
        self.app.on_file_received(filename, file_data_b64)
        
        # Broadcast to other peers
        self.broadcast_message(data, exclude_addr=sender_addr)

    def handle_peer_list_update(self, data, sender_addr):
        """Handle peer list updates"""
        new_peers = data.get("peers", [])
        
        # Add new peers to our known peers list
        my_addr = (self.get_local_ip(), self.app.my_port)
        for peer_info in new_peers:
            peer_addr = tuple(peer_info)
            if peer_addr not in self.known_peers and peer_addr != my_addr:
                self.known_peers.add(peer_addr)

    def broadcast_message(self, message_data, exclude_addr=None):
        """Broadcast a message to all connected peers except the excluded one"""
        disconnected_peers = []
        
        for peer_addr, sock in self.peer_connections.items():
            if peer_addr != exclude_addr:
                try:
                    self.send_json_message(sock, message_data)
                except Exception as e:
                    disconnected_peers.append(peer_addr)
        
        # Clean up disconnected peers
        for peer_addr in disconnected_peers:
            if peer_addr in self.peer_connections:
                self.peer_connections[peer_addr].close()
                del self.peer_connections[peer_addr]
            if peer_addr in self.known_peers:
                self.known_peers.remove(peer_addr)
        
        if disconnected_peers:
            self.app.on_peer_count_changed()

    def send_chat_message(self, message, nickname):
        """Send a chat message to all connected peers"""
        if self.peer_connections:
            message_data = {
                "type": "chat_message",
                "message_id": str(uuid.uuid4()),
                "timestamp": time.time(),
                "message": message
            }
            self.broadcast_message(message_data)

    def send_nickname_change(self, old_nickname, new_nickname):
        """Send nickname change to all connected peers"""
        if self.peer_connections:
            message_data = {
                "type": "nickname_change",
                "message_id": str(uuid.uuid4()),
                "timestamp": time.time(),
                "old_nickname": old_nickname,
                "new_nickname": new_nickname
            }
            self.broadcast_message(message_data)

    def send_file(self, filename, file_data):
        """Send a file to all connected peers"""
        if not self.peer_connections:
            return False, "No peers connected. Connect to peers first."
            
        try:
            # Encode file data in base64 for JSON transmission
            file_data_b64 = base64.b64encode(file_data).decode('utf-8')
            
            # Create file transfer message
            message_data = {
                "type": "file_transfer",
                "message_id": str(uuid.uuid4()),
                "timestamp": time.time(),
                "filename": filename,
                "file_data": file_data_b64
            }
            
            # Broadcast to all peers
            self.broadcast_message(message_data)
            return True, f"File {filename} sent to all peers"
            
        except Exception as e:
            return False, f"File send failed: {str(e)}"

    def send_json_message(self, sock, data):
        """Send a JSON message to a socket"""
        try:
            message = json.dumps(data).encode('utf-8')
            length = len(message)
            sock.sendall(length.to_bytes(4, byteorder='big'))
            sock.sendall(message)
        except Exception as e:
            raise

    def receive_json_message(self, sock):
        """Receive a JSON message from a socket"""
        try:
            # First receive the length
            length_bytes = self.receive_all(sock, 4)
            if not length_bytes:
                return None
            length = int.from_bytes(length_bytes, byteorder='big')
            
            # Then receive the message
            message_bytes = self.receive_all(sock, length)
            if not message_bytes:
                return None
                
            return json.loads(message_bytes.decode('utf-8'))
        except Exception as e:
            return None

    def receive_all(self, sock, length):
        """Receive exactly 'length' bytes from socket"""
        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def get_peer_count(self):
        """Get the number of connected peers"""
        return len(self.peer_connections)

    def get_peer_list_info(self):
        """Get formatted peer list information"""
        peer_info = "Connected Peers:\n"
        for peer_addr in self.peer_connections.keys():
            peer_info += f"  • {peer_addr[0]}:{peer_addr[1]}\n"
        
        peer_info += "\nKnown Peers:\n"
        for peer_addr in self.known_peers:
            status = "Connected" if peer_addr in self.peer_connections else "Disconnected"
            peer_info += f"  • {peer_addr[0]}:{peer_addr[1]} ({status})\n"
        
        return peer_info

    def shutdown(self):
        """Shutdown the network manager"""
        self.running = False
        
        # Close all peer connections
        for sock in self.peer_connections.values():
            try:
                sock.close()
            except:
                pass
        
        # Close listening socket
        if self.listen_socket:
            try:
                self.listen_socket.close()
            except:
                pass
        
        self.peer_connections.clear()
        self.known_peers.clear()
