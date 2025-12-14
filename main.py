import os
from flask import Flask, jsonify, request
from database import Database
from knowledge_manager import KnowledgeManager

app = Flask(__name__)
db = Database()
ai = KnowledgeManager()

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Priyanka AI - Knowledge Base</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: auto; }
            .card { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0; }
            .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            input, textarea { width: 100%; padding: 10px; margin: 5px 0; }
        </style>
    </head>
    <body>
        <h1>🤖 Priyanka AI Knowledge Base</h1>
        <div class="card">
            <h3>Add New Knowledge</h3>
            <input type="text" id="question" placeholder="Question (e.g., What is your name?)">
            <textarea id="answer" placeholder="Answer (e.g., My name is Priyanka! ❤️)" rows="3"></textarea>
            <button class="btn" onclick="addKnowledge()">Add Knowledge</button>
        </div>
        
        <div class="card">
            <h3>Search Knowledge</h3>
            <input type="text" id="search" placeholder="Search query..." onkeyup="searchKnowledge()">
            <div id="searchResults"></div>
        </div>
        
        <div class="card">
            <h3>Statistics</h3>
            <div id="stats">Loading...</div>
        </div>
        
        <script>
            async function addKnowledge() {
                const question = document.getElementById('question').value;
                const answer = document.getElementById('answer').value;
                
                const response = await fetch('/api/knowledge', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question, answer})
                });
                
                if(response.ok) {
                    alert('Knowledge added!');
                    document.getElementById('question').value = '';
                    document.getElementById('answer').value = '';
                    loadStats();
                }
            }
            
            async function searchKnowledge() {
                const query = document.getElementById('search').value;
                if(query.length < 2) return;
                
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                const results = await response.json();
                
                document.getElementById('searchResults').innerHTML = 
                    results.map(r => `<div><b>Q:</b> ${r.question}<br><b>A:</b> ${r.answer}</div>`).join('');
            }
            
            async function loadStats() {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('stats').innerHTML = `
                    <p>Total Knowledge: ${stats.knowledge_count}</p>
                    <p>Total Conversations: ${stats.conversation_count}</p>
                    <p>Last Updated: ${stats.last_updated}</p>
                `;
            }
            
            // Load stats on page load
            loadStats();
        </script>
    </body>
    </html>
    """

@app.route('/api/knowledge', methods=['GET', 'POST'])
def handle_knowledge():
    if request.method == 'GET':
        knowledge = db.get_all_knowledge()
        return jsonify(knowledge)
    else:
        data = request.json
        result = db.add_knowledge(
            data['question'],
            data['answer'],
            data.get('category', 'general'),
            data.get('language', 'hindi')
        )
        return jsonify(result)

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    # Simple search - in production, use better search
    all_knowledge = db.get_all_knowledge()
    results = []
    
    for item in all_knowledge:
        if query.lower() in item['question'].lower():
            results.append(item)
    
    return jsonify(results[:10])  # Limit to 10 results

@app.route('/api/stats')
def stats():
    return jsonify(db.get_statistics())

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    response = ai.get_response(data['message'])
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
