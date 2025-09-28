# from flask import send_file
# import os
# from flask import Flask, render_template, request, jsonify
# from flask_socketio import SocketIO
# from src.chat.chat_manager import ChatManager
# import threading
# import time

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'web-navigator-secret-key'
# socketio = SocketIO(app, cors_allowed_origins="*")

# # Global chat manager
# chat_manager = ChatManager()

# @app.route('/')
# def index():
#     return render_template('index.html')

# @socketio.on('connect')
# def handle_connect():
#     print('Client connected')
#     # Start new conversation for this client
#     conv_id = chat_manager.start_new_conversation()
#     socketio.emit('conversation_started', {'conversation_id': conv_id})

# @socketio.on('disconnect')
# def handle_disconnect():
#     print('Client disconnected')

# @socketio.on('send_message')
# def handle_message(data):
#     user_input = data.get('message', '').strip()
#     conversation_id = data.get('conversation_id')
    
#     if not user_input:
#         socketio.emit('error', {'message': 'Empty message'})
#         return
    
#     # Send typing indicator
#     socketio.emit('typing_start')
    
#     # Process message (with small delay to show typing)
#     time.sleep(1)
    
#     try:
#         result = chat_manager.process_message(user_input, conversation_id)
        
#         # Send response
#         socketio.emit('message_response', {
#             'response': result['response'],
#             'type': result.get('type', 'chat'),
#             'success': result.get('success', False),
#             'conversation_id': result['conversation_id']
#         })
        
#     except Exception as e:
#         socketio.emit('error', {'message': f'Error processing message: {str(e)}'})
    
#     finally:
#         socketio.emit('typing_stop')

# @socketio.on('new_conversation')
# def handle_new_conversation():
#     conv_id = chat_manager.start_new_conversation()
#     conversation = chat_manager.get_current_conversation()
    
#     socketio.emit('conversation_started', {
#         'conversation_id': conv_id,
#         'welcome_message': conversation.messages[0]['content'] if conversation.messages else ''
#     })

# @app.route('/api/conversations', methods=['GET'])
# def get_conversations():
#     conversations = chat_manager.get_conversation_list()
#     return jsonify(conversations)

# @app.route('/api/conversation/<conversation_id>', methods=['GET'])
# def get_conversation(conversation_id):
#     conversation = chat_manager.conversations.get(conversation_id)
#     if conversation:
#         return jsonify(conversation.to_dict())
#     return jsonify({'error': 'Conversation not found'}), 404



# @app.route('/download')
# def download_file():
#     file_path = request.args.get('file', '')
    
#     # Security check - ensure the file is within the outputs directory
#     if not file_path or not file_path.startswith('outputs/'):
#         return jsonify({'error': 'Invalid file path'}), 400
    
#     if not os.path.exists(file_path):
#         return jsonify({'error': 'File not found'}), 404
    
#     try:
#         return send_file(file_path, as_attachment=True)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # Also update the handle_message function to emit file_ready event
# @socketio.on('send_message')
# def handle_message(data):
#     user_input = data.get('message', '').strip()
#     conversation_id = data.get('conversation_id')
    
#     if not user_input:
#         socketio.emit('error', {'message': 'Empty message'})
#         return
    
#     # Send typing indicator
#     socketio.emit('typing_start')
    
#     # Process message (with small delay to show typing)
#     time.sleep(1)
    
#     try:
#         result = chat_manager.process_message(user_input, conversation_id)
        
#         # Send response
#         socketio.emit('message_response', {
#             'response': result['response'],
#             'type': result.get('type', 'chat'),
#             'success': result.get('success', False),
#             'conversation_id': result['conversation_id'],
#             'metadata': result.get('metadata', {})
#         })
        
#         # If file was created, send file_ready event
#         if result.get('metadata', {}).get('file_created'):
#             socketio.emit('file_ready', {
#                 'name': result['metadata']['file_name'],
#                 'path': result['metadata']['file_path'],
#                 'format': result['metadata']['output_format']
#             })
        
#     except Exception as e:
#         socketio.emit('error', {'message': f'Error processing message: {str(e)}'})
    
#     finally:
#         socketio.emit('typing_stop')
# if __name__ == '__main__':
#     print("Starting Web Navigator AI Chat Server...")
#     print("Access the chat interface at: http://localhost:5000")
#     socketio.run(app, debug=True, host='0.0.0.0', port=5000)


from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO
from src.chat.chat_manager import ChatManager
import os
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'web-navigator-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global chat manager
chat_manager = ChatManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download')
def download_file():
    file_path = request.args.get('file', '')
    
    # Security check - ensure the file is within the outputs directory
    if not file_path or 'outputs' not in file_path:
        return jsonify({'error': 'Invalid file path'}), 400
    
    # Get absolute path
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(abs_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        filename = os.path.basename(abs_path)
        return send_file(abs_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files')
def list_files():
    """List all available files in outputs directory"""
    try:
        output_dir = 'outputs'
        if not os.path.exists(output_dir):
            return jsonify([])
        
        files = []
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                files.append({
                    'name': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'created': os.path.getctime(file_path)
                })
        
        # Sort by creation time, newest first
        files.sort(key=lambda x: x['created'], reverse=True)
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Start new conversation for this client
    conv_id = chat_manager.start_new_conversation()
    socketio.emit('conversation_started', {'conversation_id': conv_id})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('send_message')
def handle_message(data):
    user_input = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')
    
    if not user_input:
        socketio.emit('error', {'message': 'Empty message'})
        return
    
    # Send typing indicator
    socketio.emit('typing_start')
    
    # Process message (with small delay to show typing)
    time.sleep(1)
    
    try:
        result = chat_manager.process_message(user_input, conversation_id)
        
        # Prepare response data
        response_data = {
            'response': result['response'],
            'type': result.get('type', 'chat'),
            'success': result.get('success', False),
            'conversation_id': result['conversation_id'],
            'metadata': result.get('metadata', {})
        }
        
        # If file was created, add file information
        if result.get('file_created'):
            response_data['file_created'] = True
            response_data['file_path'] = result.get('file_path')
            response_data['file_name'] = result.get('file_name')
            response_data['output_format'] = result.get('output_format')
            
            # Emit file ready event
            socketio.emit('file_ready', {
                'name': result['file_name'],
                'path': result['file_path'],
                'format': result['output_format']
            })
        
        # Send response
        socketio.emit('message_response', response_data)
        
    except Exception as e:
        socketio.emit('error', {'message': f'Error processing message: {str(e)}'})
    
    finally:
        socketio.emit('typing_stop')

@socketio.on('new_conversation')
def handle_new_conversation():
    conv_id = chat_manager.start_new_conversation()
    conversation = chat_manager.get_current_conversation()
    
    socketio.emit('conversation_started', {
        'conversation_id': conv_id,
        'welcome_message': conversation.messages[0]['content'] if conversation.messages else ''
    })

@socketio.on('get_files')
def handle_get_files():
    """Send list of available files to client"""
    try:
        output_dir = 'outputs'
        if not os.path.exists(output_dir):
            socketio.emit('files_list', [])
            return
        
        files = []
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            if os.path.isfile(file_path):
                files.append({
                    'name': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'created': os.path.getctime(file_path),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getctime(file_path)))
                })
        
        # Sort by creation time, newest first
        files.sort(key=lambda x: x['created'], reverse=True)
        socketio.emit('files_list', files)
    except Exception as e:
        socketio.emit('error', {'message': f'Error getting files: {str(e)}'})

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    conversations = chat_manager.get_conversation_list()
    return jsonify(conversations)

@app.route('/api/conversation/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    conversation = chat_manager.conversations.get(conversation_id)
    if conversation:
        return jsonify(conversation.to_dict())
    return jsonify({'error': 'Conversation not found'}), 404

if __name__ == '__main__':
    # Create outputs directory if it doesn't exist
    os.makedirs('outputs', exist_ok=True)
    print("Starting Web Navigator AI Chat Server...")
    print("Access the chat interface at: http://localhost:5000")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)