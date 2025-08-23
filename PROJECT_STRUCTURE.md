# P2P Mesh Chat - Modular Architecture

A clean, modular implementation of a decentralized peer-to-peer chat application built with Python and Tkinter.

## 🏗️ Project Structure

```
PeerChat/
├── main.py              # Main application entry point and coordinator
├── network_manager.py   # P2P networking, connections, and message routing
├── message_handler.py   # Message processing, commands, and file handling
├── user_interface.py    # GUI components and user interactions
├── __init__.py          # Package initialization
└── README.md           # This documentation
```

## 📦 Module Overview

### `main.py` - Application Coordinator
- **Purpose**: Entry point and central coordination
- **Responsibilities**: 
  - Initialize all components
  - Handle inter-module communication
  - Manage application lifecycle
- **Key Classes**: `P2PChatApp`

### `network_manager.py` - P2P Network Layer  
- **Purpose**: All networking functionality
- **Responsibilities**:
  - TCP socket management
  - Peer connections and handshakes
  - Message broadcasting and flooding
  - Loop prevention and peer discovery
- **Key Classes**: `NetworkManager`

### `message_handler.py` - Message Processing
- **Purpose**: Message and command processing
- **Responsibilities**:
  - Parse and route user input
  - Handle slash commands
  - Process file transfers
  - Format messages with timestamps
- **Key Classes**: `MessageHandler`

### `user_interface.py` - GUI Layer
- **Purpose**: All user interface components
- **Responsibilities**:
  - Create and manage Tkinter widgets
  - Handle user interactions
  - Display messages and status updates
  - Manage UI state and styling
- **Key Classes**: `UserInterface`

## 🎯 Key Features

### Core P2P Functionality
- **True Mesh Network**: Direct peer-to-peer connections
- **Decentralized**: No central server required
- **Message Flooding**: Automatic message propagation with loop prevention
- **Peer Discovery**: Automatic network expansion when peers connect
- **Dynamic Topology**: Peers can join and leave freely

### User Features
- **Real-time Chat**: Instant messaging across the mesh network
- **File Transfer**: Send files directly between peers
- **Nickname Support**: Changeable display names
- **Command System**: Built-in slash commands for network management
- **Emoji Support**: Express yourself with emoji reactions

### Technical Features
- **Modular Design**: Clean separation of concerns
- **Event-Driven**: Component communication via callbacks
- **Thread-Safe**: Non-blocking GUI with background networking
- **JSON Protocol**: Structured message format with type safety
- **Error Handling**: Robust connection management and recovery

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)

### Installation
1. Clone or download this repository
2. Navigate to the PeerChat directory
3. Run the application:
   ```bash
   python main.py
   ```

### Quick Start
1. **Set Nickname**: Enter your display name when prompted
2. **Start Listening**: Choose a port and click "Start Listening"
3. **Connect to Peers**: Enter IP:Port of other peers to join the network
4. **Start Chatting**: Type messages and they'll propagate through the mesh!

## 🔧 Available Commands

- `/help` - Show all available commands
- `/nick <name>` - Change your nickname
- `/peers` - Display network topology and peer list
- `/connect <ip> <port>` - Connect to a specific peer
- `/exit` - Quit the application gracefully

## 🌐 Network Architecture

### Mesh Topology
Each peer maintains direct connections to other peers, creating a mesh where messages can flow through multiple paths:

```
    Alice ←→ Bob
      ↑       ↓
      ↑     Charlie ←→ Dave
      ↑       ↓       ↗
    Emma ←→ Frank ←→ Grace
```

### Message Flow
1. **User Input**: Message entered in GUI
2. **Processing**: MessageHandler processes and formats
3. **Broadcasting**: NetworkManager floods message to all connected peers  
4. **Reception**: Receiving peers display and forward to their connections
5. **Loop Prevention**: Message IDs prevent infinite circulation

## 💾 Component Communication

The modular design uses a clean event-driven architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   UserInterface │    │   P2PChatApp     │    │  NetworkManager │
│                 │◄──►│   (Coordinator)  │◄──►│                 │
│   • GUI Events  │    │   • Events       │    │   • Connections │
│   • Display     │    │   • State        │    │   • Messages    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ MessageHandler  │    │   Application    │    │   Peer Network  │
│                 │    │     State        │    │                 │
│  • Commands     │    │  • Nickname      │    │   Alice ←→ Bob  │
│  • File Handling│    │  • Port          │    │     ↑       ↓   │
└─────────────────┘    └──────────────────┘    │   Charlie ←→... │
                                               └─────────────────┘
```

## 🧪 Testing the Modular Version

### Single Computer Testing
1. Start multiple instances: `python main.py` (in separate terminals)
2. Use different ports: 12345, 12346, 12347, etc.
3. Connect peers in a chain or star topology
4. Test message broadcasting and file transfers

### Multi-Computer Testing  
1. Run on different machines in your network
2. Use actual IP addresses instead of 127.0.0.1
3. Ensure firewall allows the application
4. Test network resilience by disconnecting peers

## 🛠️ Development Benefits

### Maintainability
- **Single Responsibility**: Each module has a clear, focused purpose
- **Loose Coupling**: Components interact through well-defined interfaces
- **Easy Testing**: Individual modules can be tested in isolation
- **Clear Dependencies**: Import structure shows component relationships

### Extensibility
- **New Features**: Add functionality without modifying core modules
- **Different UIs**: Swap UserInterface module for web/mobile versions
- **Protocol Changes**: Modify NetworkManager without affecting UI
- **Additional Commands**: Extend MessageHandler with new slash commands

### Code Quality
- **Readability**: Smaller, focused files are easier to understand
- **Reusability**: Modules can be reused in other P2P applications
- **Documentation**: Each module has clear docstrings and purpose
- **Version Control**: Changes are isolated to relevant modules

## 📁 Module Dependencies

```
main.py
├── network_manager.py
├── message_handler.py
└── user_interface.py

network_manager.py
├── socket, threading, json
├── uuid, time, base64
└── (no internal dependencies)

message_handler.py  
├── datetime, os, base64
├── tkinter.filedialog, tkinter.messagebox
└── (interacts with app via callbacks)

user_interface.py
├── tkinter, ttk, scrolledtext
├── simpledialog, messagebox
└── (calls app methods for actions)
```

## 🎉 What's Better Now?

### Before (Monolithic)
- ❌ 600+ lines in single file
- ❌ Mixed responsibilities 
- ❌ Hard to test individual features
- ❌ Difficult to modify without breaking other parts
- ❌ Poor code organization

### After (Modular)  
- ✅ Clean separation into 4 focused modules
- ✅ Each module has single responsibility
- ✅ Easy to test, modify, and extend
- ✅ Clear interfaces between components
- ✅ Professional code organization
- ✅ Maintainable and scalable architecture

## 🔮 Future Enhancements

The modular architecture makes it easy to add:
- **Encryption Module**: Add security without changing networking
- **Database Module**: Persistent message history
- **Discovery Module**: Automatic peer finding (mDNS, broadcasting)
- **Plugin System**: User-contributed extensions
- **Web Interface**: Replace Tkinter UI with web interface
- **Mobile Support**: Add mobile UI module

## 📝 License

This project is open source and available under the MIT License.

---

**Enjoy your clean, modular P2P mesh chat application!** 🚀
