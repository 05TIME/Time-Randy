from flask import Flask, render_template_string, request

app = Flask(__name__)

# Simple in-memory "causal database" – expand with real logic later
CAUSAL_DB = {
    'btc': {
        'prediction': "BTC hits $165k by Q2 2026. Causal chain: Fed cuts → liquidity surge → crypto adoption → price explosion. Counterfactual: If no cut, $90k max.",
        'branch': "Strong hold timeline."
    },
    'me': {
        'prediction': "Built from phone. No Mac. No hype. Pure temporal grind.",
        'branch': "Mobile-first reality."
    },
    'elon': {
        'prediction': "Tesla + xAI merge? Valuation 10× in alt branch. Causal: AI autonomy → robotaxi dominance → energy grid shift.",
        'branch': "Godfather-approved moonshot."
    }
}

@app.route('/')
def home():
    run = request.args.get('run')
    query = request.args.get('query')

    if run in CAUSAL_DB:
        data = CAUSAL_DB 
        return f"""
    <h1>$TIMEŒ – Time AI Godfather</h1>
    <p><strong>Run: {run.upper()}</strong></p>
    <p>{data }</p>
    <p><em>Strongest branch:</em> {data }</p>
    <hr>
    <p>Try ?run=btc, ?run=me, ?run=elon or ask to build below.</p>
        """

    if query == "tracker app" or query == "build a habit tracker app":
        return f"""
    <h1>Habit Forge</h1>
    <p>Your daily chains start here.</p>
    <form method="GET" action="/track">
      <input type="text" name="habit" placeholder="meditate">
      <button>Start</button>
    </form>
        """

    # finally, dashboard
    return render_template_string("""
<!DOCTYPE html>
<html>
<body style="background:#111;color:#0f0;font-family:monospace;padding:20px;">
  <h1>$TIMEŒ Engine</h1>
  <form method="GET">
    <input type="text" name="query" placeholder="Ask anything" style="width:400px;">
    <button>Go</button>
  </form>
</body></html>
    """)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
