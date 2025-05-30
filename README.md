# Haruko Discord Bot  

A feature-rich Discord bot for **secure server management**, **terminal access**, and **advanced moderation** with cyberpunk aesthetics.

---

## ✨ Features

### 🔒 **Security & System**
| Command           | Description                          | Restricted |
|-------------------|--------------------------------------|------------|
| `/cyberterm`      | Execute terminal commands            | ✅         |
| `/neurostat`      | View system vitals (CPU/RAM/Disk)    | ❌         |
| `/neuroshutdown`  | Initiate system shutdown             | ✅         |
| `/data_backup`    | Create encrypted system backups      | ✅         |

### ⚖️ **Moderation**
- **User Control**: `/kick`, `/ban`, `/mute`, `/warn`
- **Role Management**: `/addrole`, `/removerole`
- **Logging**: `/setup_logging` (configure audit channels)
- **Cleanup**: `/clear [amount]` (bulk delete messages)

### 🛠️ **Utility**
- `/help` - Interactive command list
- Customizable prefix (via config)
- Multi-language support (i18n ready)

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Discord Developer Portal access
- `sudo` privileges (for terminal commands)

```bash
# Clone & Setup
git clone https://github.com/yourusername/haruko-bot.git
cd haruko-bot
pip install -r requirements.txt
