"""
Message Handler Module
Handles all message-related functionality including commands, formatting, and processing.
"""

import datetime
import os
import base64
from tkinter import filedialog, messagebox


class MessageHandler:
    def __init__(self, app):
        self.app = app
    
    def process_message(self, msg):
        """Process a message input - either command or regular message"""
        msg = msg.strip()
        if not msg:
            return
            
        if msg.startswith("/"):
            self.handle_command(msg)
        else:
            self.send_regular_message(msg)
    
    def send_regular_message(self, msg):
        """Send a regular chat message"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {self.app.nickname}: {msg}"
        
        # Display locally
        self.app.ui.update_chat(full_msg, 'self')
        
        # Send to network
        self.app.network.send_chat_message(full_msg, self.app.nickname)
    
    def handle_command(self, command):
        """Handle slash commands"""
        if command == "/exit":
            self.app.on_closing()
        elif command == "/help":
            help_text = """Available Commands:
/help - Show this help
/nick <name> - Change nickname
/peers - Show peer list
/connect <ip> <port> - Connect to a peer
/exit - Quit application"""
            self.app.ui.update_chat(help_text, 'system')
        elif command.startswith("/nick "):
            new_nick = command[6:].strip()
            if new_nick:
                self.change_nickname(new_nick)
        elif command == "/peers":
            self.show_peer_list()
        elif command.startswith("/connect "):
            parts = command[9:].strip().split()
            if len(parts) >= 2:
                self.connect_to_peer(parts[0], parts[1])
            else:
                self.app.ui.update_chat("[System] Usage: /connect <ip> <port>", 'system')
        else:
            self.app.ui.update_chat(f"[System] Unknown command: {command}. Type /help for available commands", 'system')
    
    def change_nickname(self, new_nick):
        """Change the user's nickname"""
        old_nickname = self.app.nickname
        self.app.nickname = new_nick
        
        # Broadcast nickname change if we have connections
        if self.app.network.peer_connections:
            self.app.network.send_nickname_change(old_nickname, new_nick)
        
        self.app.ui.update_chat(f"[System] Nickname changed to {new_nick}", 'system')
    
    def show_peer_list(self):
        """Show list of connected and known peers"""
        peer_info = self.app.network.get_peer_list_info()
        messagebox.showinfo("Peer List", peer_info)
    
    def connect_to_peer(self, ip, port_str):
        """Connect to a peer via command"""
        try:
            port = int(port_str)
            success, message = self.app.network.connect_to_peer(ip, port, self.app.my_port, self.app.nickname)
            if success:
                self.app.ui.update_chat(f"[System] {message}", 'system')
                self.app.ui.update_peer_count()
            else:
                self.app.ui.update_chat(f"[System] {message}", 'system')
        except ValueError:
            self.app.ui.update_chat("[System] Invalid port number", 'system')
    
    def send_file(self):
        """Handle file sending"""
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
            
        filename = os.path.basename(file_path)
        try:
            # Read file data
            with open(file_path, "rb") as file:
                file_data = file.read()
            
            # Send through network
            success, message = self.app.network.send_file(filename, file_data)
            self.app.ui.update_chat(f"[System] {message}", 'system')
            
        except Exception as e:
            self.app.ui.update_chat(f"[Error] File send failed: {str(e)}", 'error')
    
    def handle_file_received(self, filename, file_data_b64):
        """Handle received file"""
        try:
            # Decode file data
            file_data = base64.b64decode(file_data_b64.encode('utf-8'))
            
            # Ask user where to save
            save_path = filedialog.asksaveasfilename(initialfile=filename)
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(file_data)
                self.app.ui.update_chat(f"[System] File received and saved: {os.path.basename(save_path)}", 'system')
            else:
                self.app.ui.update_chat(f"[System] File {filename} received but not saved", 'system')
                
        except Exception as e:
            self.app.ui.update_chat(f"[Error] Failed to receive file {filename}: {str(e)}", 'error')
    
    def format_timestamp_message(self, message, sender):
        """Format a message with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] {sender}: {message}"
