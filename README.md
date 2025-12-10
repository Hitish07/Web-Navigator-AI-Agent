Web Navigation & Automation Project
📋 Project Overview
A Python-based web automation system that uses AI to perform browser tasks through natural language commands. Control web browsers intelligently using conversational AI.

🚀 Quick Start
Prerequisites
Python 3.8+

Ollama (for local AI) or OpenAI API key

Installation
# 1. Clone or download the project
# 2. Navigate to project folder
cd your-project-folder

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install browsers
playwright install

**Running the Application**
bash
# Web Interface (Recommended)
python web_app.py
# Then open http://localhost:5000 in your browser

# OR Console Interface
python chat_console.py

🎯 What You Can Do
"Search for Python tutorials on YouTube" - AI will open browser and search

"Get latest news headlines" - Navigate and extract content

"Take a screenshot of this page" - Capture visual data

"Fill out this form with test data" - Automate form interactions

💬 Usage Examples
Start the application: python web_app.py

Open http://localhost:5000

Type commands like:

"Search for AI news on Google"

"Take a screenshot of GitHub"

"Find Python documentation"

⚙️ Configuration
AI Model: Configure in src/llm/ollama_client.py

Browser Settings: Modify src/browser/playwright_controller.py

Output Location: Check config/outputs/

**🛠️ Troubleshooting**

Browsers not installing: Run playwright install

AI not responding: Check Ollama is running (ollama serve)

Port in use: Change port in web_app.py

**📞 Support**
For issues, check:

execution_log.json for error details

Ensure all dependencies in requirements.txt are installed

Verify browsers are properly installed

**Ready to use! Run python web_app.py and start automating web tasks with AI commands.**

