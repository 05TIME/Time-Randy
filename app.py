from flask import Flask, render_template_string, request

from airbnb_ops.brief_routes import bp as airbnb_brief_bp
from airbnb_ops.dashboard_routes import bp as airbnb_dashboard_bp
from airbnb_ops.finance_routes import bp as airbnb_finance_bp
from airbnb_ops.github_webhook import bp as github_webhook_bp
from airbnb_ops.routes import bp as airbnb_ops_bp
from chief_of_staff.dashboard import bp as chief_of_staff_dashboard_bp

app = Flask(__name__)
app.register_blueprint(airbnb_ops_bp)
app.register_blueprint(airbnb_finance_bp)
app.register_blueprint(airbnb_dashboard_bp)
app.register_blueprint(airbnb_brief_bp)
app.register_blueprint(github_webhook_bp)
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
    return render_template_string("""<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>TIMEŒ – RANDY</title><style>body{margin:0;background:#090b10;color:#f5f7fa;font-family:-apple-system,BlinkMacSystemFont,Inter,system-ui,sans-serif}.wrap{max-width:760px;margin:auto;padding:28px 18px}.brand{color:#35f36b;font-weight:900;letter-spacing:.06em;font-size:14px}.hero{padding:42px 0 26px}h1{font-size:42px;line-height:1.05;margin:0 0 12px}.muted{color:#98a2b1;line-height:1.6}.links{display:grid;gap:12px;margin:24px 0}.link{display:block;padding:18px;border:1px solid #29313d;border-radius:16px;background:#11151c;color:#f5f7fa;text-decoration:none}.link b{display:block;margin-bottom:5px}.link span{color:#35f36b;font-size:13px}.search{display:flex;gap:8px;margin-top:20px}.search input{flex:1;min-width:0;padding:13px;border-radius:12px;border:1px solid #303846;background:#11151c;color:white}.search button{padding:13px 16px;border:0;border-radius:12px;background:#35f36b;font-weight:800}.social{margin-top:28px;padding-top:18px;border-top:1px solid #252c36;color:#8993a2;font-size:13px}.social a{color:#35f36b;text-decoration:none;font-weight:700}</style></head><body><main class="wrap"><div class="brand">$TIMEŒ – RANDY</div><section class="hero"><h1>Temporal intelligence for operations.</h1><p class="muted">Your command centers, Airbnb operations, and AI workflows in one mobile-first workspace.</p></section><nav class="links"><a class="link" href="/airbnb/dashboard"><b>Airbnb Turnover Monitor</b><span>Open the live operations dashboard →</span></a><a class="link" href="/airbnb/command-center"><b>Airbnb Command Center API</b><span>Open live business data →</span></a><a class="link" href="/chief-of-staff"><b>TIMEŒ Command Center</b><span>Open chief of staff →</span></a><a class="link" href="/airbnb/brief"><b>Chief of Staff Brief</b><span>Open the latest brief →</span></a></nav><form class="search" method="GET"><input name="query" placeholder="Ask anything"><button>Go</button></form><div class="social">Follow TIMEŒ – RANDY on TikTok: <a href="https://www.tiktok.com/@kubani.time" target="_blank" rel="noopener">@kubani.time →</a></div></main></body></html>""")


@app.route('/track')
def track():
    habit = request.args.get('habit')
    try:
        streak = int(request.args.get(f"streak_{habit}")) + 1
    except (TypeError, ValueError):
        streak = 1
    return f'<h1>🔥 {habit}</h1><p>Day {streak}. Don’t break it.</p><p>Streak: <strong>{streak}</strong></p><a href="/?query=tracker%20app">← Back</a> <a href="/track?habit={habit}&streak_{habit}={streak}">Done →</a>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
