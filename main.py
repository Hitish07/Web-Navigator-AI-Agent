import sys

def main():
    print("Web Navigator AI Agent - Choose Interface:")
    print("1. Console Chat Interface (Recommended)")
    print("2. Web Interface")
    print("3. Original Command-line Interface")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        from chat_console import main as console_main
        console_main()
    elif choice == "2":
        print("Starting web server...")
        print("Access the interface at: http://localhost:5000")
        from web_app import socketio, app
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    # elif choice == "3":
    #     from original_main import main as original_main
    #     original_main()
    else:
        print("Invalid choice. Starting console chat...")
        from chat_console import main as console_main
        console_main()

if __name__ == "__main__":
    main()