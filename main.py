"""
P2P Mesh Chat Application - Main Module
A decentralized peer-to-peer chat application with mesh networking.
"""

import tkinter as tk
from network_manager import NetworkManager
from message_handler import MessageHandler
from user_interface import UserInterface


class P2PChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P Mesh Chat")
        self.root.geometry("600x500")
        
        # Application state
        self.nickname = "User"
        self.my_port = 12345
        
        # Initialize components
        self.network = NetworkManager(self)
        self.message_handler = MessageHandler(self)
        self.ui = UserInterface(self)

    # Event handlers called by network manager
    def on_peer_joined(self, nickname, ip, port):
        """Called when a new peer joins the network"""
        self.ui.update_peer_count()
        self.ui.update_chat(f"[System] {nickname} ({ip}:{port}) joined the network", 'system')

    def on_peer_disconnected(self, ip, port):
        """Called when a peer disconnects"""
        self.ui.update_peer_count()
        self.ui.update_chat(f"[System] Peer {ip}:{port} disconnected", 'system')

    def on_message_received(self, message, msg_type):
        """Called when a message is received from the network"""
        self.ui.update_chat(message, msg_type)

    def on_file_received(self, filename, file_data_b64):
        """Called when a file is received from the network"""
        self.message_handler.handle_file_received(filename, file_data_b64)

    def on_peer_count_changed(self):
        """Called when the peer count changes"""
        self.ui.update_peer_count()

    def on_closing(self):
        """Handle application closing"""
        self.network.shutdown()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = P2PChatApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
