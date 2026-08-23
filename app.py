from flask import Flask, render_template_string, request

from airbnb_ops.brief_routes import bp as airbnb_brief_bp
from airbnb_ops.dashboard_routes import bp as airbnb_dashboard_bp
from airbnb_ops.finance_routes import bp as airbnb_finance_bp
from airbnb_ops.routes import bp as airbnb_ops_bp
from chief_of_staff.dashboard import bp as chief_of_staff_dashboard_bp

app = Flask(__name__)
app.register_blueprint(airbnb_ops_bp)
app.register_blueprint(airbnb_finance_bp)
app.register_blueprint(airbnb_dashboard_bp)
app.register_blueprint(airbnb_brief_bp)
app.register_blueprint(chief_of_staff_dashboard_bp)

CAUSAL_DB = {
    'btc': {'prediction': "BTC hits $165k by Q2 2026. Causal chain: Fed cuts → liquidity surge → crypto adoption → price explosion. Counterfactual: If no cut, $90k max.", 'branch': "Strong hold timeline."},
    'me': {'prediction': "Built from phone. No Mac. No hype. Pure temporal grind.", 'branch': "Mobile-first reality."},
    'elon': {'prediction': "Tesla + xAI merge? Valuation 10× in alt branch. Causal: AI autonomy → robotaxi dominance → energy grid shift.", 'branch': "Godfather-approved moonshot."}
}


@app.route('/')
def home():
    run = request.args.get('run')
    query = request.args.get('query')
    if run in CAUSAL_DB:
        data = CAUSAL_DB[run]
        return f"<h1>$TIMEŒ – Time AI Godfather</h1><p><strong>Run: {run.upper()}</strong></p><p>{data['prediction']}</p><p><em>Strongest branch:</em> {data['branch']}</p>"
    if query == "tracker app" or query == "build a habit tracker app":
        return """<h1>Habit Forge</h1><p>Your daily chains start here.</p><form method="GET" action="/"><input type="text" name="habit" placeholder="meditate"><input type="hidden" name="query" value="tracker app"><button>Start</button></form>"""
    return render_template_string("""<!DOCTYPE html><html><body style="background:#111;color:#0f0;font-family:monospace;padding:20px;"><h1>$TIMEŒ Engine</h1><p><a href="/chief-of-staff" style="color:#0f0;">Open TIMEŒ Command Center →</a></p><p><a href="/airbnb/command-center" style="color:#0f0;">Open Airbnb Command Center →</a></p><p><a href="/airbnb/brief" style="color:#0f0;">Open Chief of Staff Brief →</a></p><form method="GET"><input type="text" name="query" placeholder="Ask anything" style="width:400px;"><button>Go</button></form></body></html>""")


@app.route('/track')
def track():
    habit = request.args.get('habit')
    try:
        streak = int(request.args.get(f"streak_{habit}")) + 1
    except (TypeError, ValueError):
        streak = 1
    return (
        f'<h1>🔥 {habit}</h1><p>Day {streak}. Don’t break it.</p>'
        f'<p>Streak: <strong>{streak}</strong></p>'
        '<a href="/?query=tracker%20app">← Back</a> '
        f'<a href="/track?habit={habit}&streak_{habit}={streak}">Done →</a>'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
