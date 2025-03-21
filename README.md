# 🚀 AI Wallet Assistant


![Python](https://img.shields.io/badge/python-3.9%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-green)

A sophisticated AI-powered assistant for cryptocurrency wallet management. AI Wallet Assistant understands natural language commands to help you manage your crypto assets with ease.

## ✨ Features

- **Natural Language Processing**: Send commands in plain English like "Send 0.1 ETH to 0x742..."
- **Transaction Management**: Send tokens, check balances, and view transaction history
- **Secure Integration**: Built to work with Web3 wallets like MetaMask
- **Fast & Responsive**: Built on FastAPI for high-performance API responses
- **Session Management**: Maintains secure wallet sessions with automatic cleanup

## 🛠️ Technology Stack

- **FastAPI**: Modern, high-performance web framework
- **Groq LLM**: AI-powered natural language processing
- **Web3.py**: Ethereum blockchain interaction
- **Pydantic**: Data validation and settings management

## 📋 Requirements

- Python 3.9+
- Web3 wallet (like MetaMask)
- Groq API key
- Ethereum node access (optional, uses defaults for testing)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-wallet-assistant.git
cd ai-wallet-assistant

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key
ETHEREUM_NODE_URL=your_infura_project_id  # Optional
```

### Running the Application

```bash
python main.py
```

The API will be available at `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

## 📝 Usage Examples

### Connect Wallet

```bash
curl -X POST "http://localhost:8000/api/v1/connect" \
  -H "Content-Type: application/json" \
  -d '{"address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", "network": "mainnet"}'
```

### Send Command

```bash
curl -X POST "http://localhost:8000/api/v1/command" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your_session_id", "command": "Send 0.1 ETH to 0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

### Check Balance

```bash
curl -X POST "http://localhost:8000/api/v1/command" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your_session_id", "command": "Show my balance"}'
```

## 🧠 AI Command Processing

The assistant understands various natural language commands:

- **Send**: "Send 0.1 ETH to 0x742..."
- **Balance**: "What's my balance?", "Show my portfolio"
- **History**: "Show my transaction history", "What transactions did I make?"
- **Help**: "What commands can I use?", "Help me"

## 🏗️ Project Structure

```
AIwalletASSISTANCE/
├── app/
│   ├── api/          # API routes and dependencies
│   ├── core/         # Core configuration and security
│   ├── models/       # Pydantic models and schemas
│   ├── services/     # Business logic services
│   └── utils/        # Helper functions
├── static/           # Static files
├── templates/        # HTML templates
├── main.py           # Application entry point
├── .env              # Environment variables
└── requirements.txt  # Dependencies
```

## 🧪 Testing

Run the test script to validate functionality:

```bash
python -m app.test_script
```

## 🔒 Security Notes

- Keep your API keys secure and never commit them to version control
- Use HTTPS in production
- Implement proper authentication for production use
- Enable session timeouts to automatically clean up inactive sessions

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📧 Contact

Questions? Reach out to us at your-email@example.com