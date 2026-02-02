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
    if run in CAUSAL_DB:
        data = CAUSAL_DB['btc']
        return f"""
<h1>$TIMEŒ – Time AI Godfather</h1>
<p><strong>Run: {run.upper()}</strong></p>
<p>{data }</p>
<p><em>Strongest branch:</em> {data['branch']}</p>
<hr>
<p>Try ?run=btc, ?run=me, ?run=elon or ask to build an app below.</p>
        """
 if query == "build a habit tracker app" or query == "tracker app":
    return f"""
    <h1>Habit Forge</h1>
    <p>Your daily chains start here.</p>
    <ul>
      <li>Add habit → Track streak → Break cycle.</li>
    </ul>
    <form method="GET" action="/track">
      <input type="text" name="habit" placeholder="e.g., meditate" style="width:200px;">
      <button>Start</button>
    </form>
    <p>Or say: 'add habit: read 10 pages'.</p>
    """   
    # rest of dashboard code—no extra spaces before HTML
    return render_template_string("""
<!DOCTYPE html>
...
""", query=request.args.get('query'))
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
