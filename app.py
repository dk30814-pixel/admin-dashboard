from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"[DB] ERROR: {e}")
        return None

@app.route('/')
def dashboard():
    """Admin dashboard homepage"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Campus Canteen - Admin Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            .header {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 30px;
                text-align: center;
            }
            .header h1 {
                font-size: 36px;
                color: #333;
                margin-bottom: 10px;
            }
            .header p {
                color: #666;
                font-size: 18px;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
            }
            .stat-card .icon {
                font-size: 48px;
                margin-bottom: 15px;
            }
            .stat-card .value {
                font-size: 32px;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 10px;
            }
            .stat-card .label {
                color: #666;
                font-size: 16px;
            }
            .chart-container {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                margin-bottom: 30px;
            }
            .chart-container h2 {
                margin-bottom: 20px;
                color: #333;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background: #f5f5f5;
                font-weight: 600;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            .refresh-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                margin-bottom: 20px;
            }
            .refresh-btn:hover {
                background: #5568d3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🍽️ Campus Canteen Admin Dashboard</h1>
                <p>Real-time Analytics & Transaction Monitoring</p>
            </div>

            <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="icon">💰</div>
                    <div class="value" id="totalRevenue">Loading...</div>
                    <div class="label">Total Revenue Today</div>
                </div>
                <div class="stat-card">
                    <div class="icon">🍔</div>
                    <div class="value" id="totalItems">Loading...</div>
                    <div class="label">Items Sold Today</div>
                </div>
                <div class="stat-card">
                    <div class="icon">⚡</div>
                    <div class="value" id="avgConfidence">Loading...</div>
                    <div class="label">Avg AI Confidence</div>
                </div>
                <div class="stat-card">
                    <div class="icon">🔥</div>
                    <div class="value" id="topItem">Loading...</div>
                    <div class="label">Top Item Today</div>
                </div>
            </div>

            <div class="chart-container">
                <h2>📊 Popular Items Today</h2>
                <table id="popularItems">
                    <thead>
                        <tr>
                            <th>Food Item</th>
                            <th>Quantity Sold</th>
                            <th>Total Revenue</th>
                            <th>Avg Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="4" class="loading">Loading data...</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="chart-container">
                <h2>🕒 Recent Transactions</h2>
                <table id="recentTransactions">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Food Item</th>
                            <th>Price</th>
                            <th>Calories</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="5" class="loading">Loading data...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            async function loadData() {
                try {
                    // Load stats
                    const statsRes = await fetch('/api/stats');
                    const stats = await statsRes.json();
                    
                    document.getElementById('totalRevenue').textContent = stats.total_revenue + ' MKD';
                    document.getElementById('totalItems').textContent = stats.total_items;
                    document.getElementById('avgConfidence').textContent = stats.avg_confidence + '%';
                    document.getElementById('topItem').textContent = stats.top_item;

                    // Load popular items
                    const popularRes = await fetch('/api/popular-items');
                    const popular = await popularRes.json();
                    
                    const popularTable = document.getElementById('popularItems').querySelector('tbody');
                    popularTable.innerHTML = popular.map(item => `
                        <tr>
                            <td>${item.food_name}</td>
                            <td>${item.quantity}</td>
                            <td>${item.revenue} MKD</td>
                            <td>${item.avg_confidence}%</td>
                        </tr>
                    `).join('');

                    // Load recent transactions
                    const recentRes = await fetch('/api/recent-transactions');
                    const recent = await recentRes.json();
                    
                    const recentTable = document.getElementById('recentTransactions').querySelector('tbody');
                    recentTable.innerHTML = recent.map(t => `
                        <tr>
                            <td>${new Date(t.created_at).toLocaleTimeString()}</td>
                            <td>${t.food_name}</td>
                            <td>${t.price} MKD</td>
                            <td>${t.calories} kcal</td>
                            <td>${t.confidence}%</td>
                        </tr>
                    `).join('');

                } catch (error) {
                    console.error('Error loading data:', error);
                }
            }

            // Load data on page load
            loadData();

            // Auto-refresh every 30 seconds
            setInterval(loadData, 30000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/api/stats')
def get_stats():
    """Get today's statistics"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get today's date range
        today = datetime.now().date()
        
        # Total revenue today
        cur.execute("""
            SELECT COALESCE(SUM(price), 0) as total_revenue
            FROM food_transactions
            WHERE DATE(created_at) = %s
        """, (today,))
        total_revenue = cur.fetchone()['total_revenue']
        
        # Total items sold today
        cur.execute("""
            SELECT COUNT(*) as total_items
            FROM food_transactions
            WHERE DATE(created_at) = %s
        """, (today,))
        total_items = cur.fetchone()['total_items']
        
        # Average confidence today
        cur.execute("""
            SELECT COALESCE(ROUND(AVG(confidence), 1), 0) as avg_confidence
            FROM food_transactions
            WHERE DATE(created_at) = %s
        """, (today,))
        avg_confidence = cur.fetchone()['avg_confidence']
        
        # Top item today
        cur.execute("""
            SELECT food_name, COUNT(*) as count
            FROM food_transactions
            WHERE DATE(created_at) = %s
            GROUP BY food_name
            ORDER BY count DESC
            LIMIT 1
        """, (today,))
        top_result = cur.fetchone()
        top_item = top_result['food_name'] if top_result else 'N/A'
        
        cur.close()
        conn.close()
        
        return jsonify({
            'total_revenue': float(total_revenue),
            'total_items': total_items,
            'avg_confidence': float(avg_confidence),
            'top_item': top_item
        })
    
    except Exception as e:
        print(f"[API] Error in get_stats: {e}")
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/popular-items')
def get_popular_items():
    """Get popular items today"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        today = datetime.now().date()
        
        cur.execute("""
            SELECT 
                food_name,
                COUNT(*) as quantity,
                ROUND(SUM(price), 2) as revenue,
                ROUND(AVG(confidence), 1) as avg_confidence
            FROM food_transactions
            WHERE DATE(created_at) = %s
            GROUP BY food_name
            ORDER BY quantity DESC
            LIMIT 10
        """, (today,))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify([dict(row) for row in results])
    
    except Exception as e:
        print(f"[API] Error in get_popular_items: {e}")
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/recent-transactions')
def get_recent_transactions():
    """Get recent transactions"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                food_name,
                price,
                calories,
                confidence,
                created_at
            FROM food_transactions
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert datetime to string
        for row in results:
            row['created_at'] = row['created_at'].isoformat()
        
        return jsonify([dict(row) for row in results])
    
    except Exception as e:
        print(f"[API] Error in get_recent_transactions: {e}")
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check"""
    return jsonify({"status": "healthy", "service": "admin-dashboard"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
