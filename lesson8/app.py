"""
Simple Flask Application for CI/CD Demo
Demonstrates database connectivity, API endpoints, and health checks
"""

from flask import Flask, jsonify, request, render_template_string
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import sys

app = Flask(__name__)

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'db')
DB_NAME = os.getenv('POSTGRES_DB', 'appdb')
DB_USER = os.getenv('POSTGRES_USER', 'appuser')
DB_PASS = os.getenv('POSTGRES_PASSWORD', 'apppass')

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}", file=sys.stderr)
        return None

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    text VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}", file=sys.stderr)
        finally:
            cur.close()
            conn.close()

# Initialize database on startup
init_db()

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>CI/CD Demo App</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        .status {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 30px 0;
        }
        .status-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            text-align: center;
        }
        .status-card.healthy {
            border-left-color: #10b981;
        }
        .status-label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 5px;
        }
        .status-value {
            font-size: 1.3rem;
            font-weight: bold;
            color: #333;
        }
        .api-section {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 2px solid #eee;
        }
        .api-section h2 {
            font-size: 1.2rem;
            color: #333;
            margin-bottom: 15px;
        }
        .message-item {
            background: #f0f4ff;
            padding: 12px;
            margin: 10px 0;
            border-radius: 6px;
            border-left: 3px solid #667eea;
        }
        .message-text {
            font-weight: 500;
            color: #333;
            margin-bottom: 5px;
        }
        .message-time {
            font-size: 0.8rem;
            color: #999;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 1rem;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            width: 100%;
            margin-top: 10px;
            transition: background 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        .endpoints {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 0.9rem;
        }
        .endpoint {
            margin: 8px 0;
            font-family: monospace;
            color: #667eea;
        }
        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 20px;
            font-size: 0.95rem;
        }
        .badge {
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 CI/CD Demo Application <span class="badge">LIVE</span></h1>
        <p class="subtitle">Docker + Jenkins + GitHub + PostgreSQL</p>
        
        <div class="status">
            <div class="status-card healthy">
                <div class="status-label">Application</div>
                <div class="status-value">✅ Running</div>
            </div>
            <div class="status-card healthy">
                <div class="status-label">Database</div>
                <div class="status-value">✅ Connected</div>
            </div>
        </div>
        
        <div class="api-section">
            <h2>📝 Leave a Message</h2>
            <input type="text" id="messageInput" placeholder="Type a message..." />
            <button onclick="sendMessage()">Send Message</button>
        </div>
        
        <div class="api-section">
            <h2>💬 Messages</h2>
            <div id="messages"></div>
        </div>
        
        <div class="endpoints">
            <strong>Available Endpoints:</strong>
            <div class="endpoint">GET /api/messages - Get all messages</div>
            <div class="endpoint">POST /api/messages - Add new message</div>
            <div class="endpoint">DELETE /api/messages/:id - Delete message</div>
            <div class="endpoint">GET /health - Health check</div>
        </div>
    </div>

    <script>
        // Load messages on page load
        window.onload = loadMessages;

        function loadMessages() {
            fetch('/api/messages')
                .then(r => r.json())
                .then(data => {
                    const container = document.getElementById('messages');
                    if (data.messages.length === 0) {
                        container.innerHTML = '<p style="color: #999;">No messages yet. Be the first!</p>';
                    } else {
                        container.innerHTML = data.messages.map(msg => `
                            <div class="message-item">
                                <div class="message-text">${escapeHtml(msg.text)}</div>
                                <div class="message-time">${new Date(msg.created_at).toLocaleString()}</div>
                            </div>
                        `).join('');
                    }
                });
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const text = input.value.trim();
            
            if (!text) {
                alert('Please enter a message');
                return;
            }
            
            fetch('/api/messages', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text})
            })
            .then(r => r.json())
            .then(data => {
                input.value = '';
                loadMessages();
            })
            .catch(e => alert('Error: ' + e));
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
'''

# ============================================
# HEALTH CHECK ENDPOINT
# ============================================
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    conn = get_db_connection()
    db_healthy = conn is not None
    if conn:
        conn.close()
    
    return jsonify({
        'status': 'healthy' if db_healthy else 'unhealthy',
        'app': 'running',
        'database': 'connected' if db_healthy else 'disconnected',
        'timestamp': datetime.now().isoformat()
    }), 200 if db_healthy else 503

# ============================================
# API ENDPOINTS
# ============================================
@app.route('/', methods=['GET'])
def index():
    """Serve the web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get all messages from database"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT id, text, created_at FROM messages ORDER BY created_at DESC LIMIT 50')
        messages = cur.fetchall()
        cur.close()
        
        return jsonify({
            'messages': [dict(msg) for msg in messages],
            'count': len(messages)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/messages', methods=['POST'])
def add_message():
    """Add a new message to database"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Message text is required'}), 400
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            'INSERT INTO messages (text) VALUES (%s) RETURNING id, text, created_at',
            (text,)
        )
        message = cur.fetchone()
        conn.commit()
        cur.close()
        
        return jsonify({
            'success': True,
            'message': dict(message)
        }), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/messages/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    """Delete a message"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute('DELETE FROM messages WHERE id = %s', (msg_id,))
        conn.commit()
        
        if cur.rowcount == 0:
            return jsonify({'error': 'Message not found'}), 404
        
        cur.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get application statistics"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM messages')
        count = cur.fetchone()[0]
        cur.close()
        
        return jsonify({
            'total_messages': count,
            'app_version': '1.0.0',
            'environment': os.getenv('FLASK_ENV', 'production'),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
