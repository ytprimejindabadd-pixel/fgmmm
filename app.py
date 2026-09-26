from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# ============================================
# 🔒 HIDDEN API URLs (Backend Only)
# ============================================
API_TG = "https://rtf-api-server.onrender.com/api?types=telegram&key=RTFSERVER&spell={spell}"
API_ADV = "https://bronx-ultra-king.duckdns.org/api/custom/search?key=8509&num={num}"

# ============================================
# 🔧 Helper: TG Info nikalna
# ============================================
def get_tg_info(spell):
    try:
        url = API_TG.format(spell=spell)
        r = requests.get(url, timeout=15)
        data = r.json()

        # Handle list ya dict dono
        if isinstance(data, list):
            data = data[0] if data else {}

        number = data.get("Number") or data.get("number")
        country = data.get("Country") or data.get("country")
        country_code = data.get("Country Code") or data.get("countryCode")

        return {
            "success": True,
            "number": number,
            "country": country,
            "country_code": country_code,
            "raw": data
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================
# 🔧 Helper: Advance Info
# ============================================
def get_advance_info(num):
    try:
        url = API_ADV.format(num=num)
        r = requests.get(url, timeout=20)
        return {"success": True, "data": r.json()}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================
# 🌐 ROUTE 1 — TG Info
# ============================================
@app.route("/api/tginfo")
def api_tginfo():
    spell = request.args.get("spell", "@ftgamer2")
    result = get_tg_info(spell)
    return jsonify(result)

# ============================================
# 🌐 ROUTE 2 — Advance (TG → Number → Advance)
# ============================================
@app.route("/api/advance")
def api_advance():
    spell = request.args.get("spell", "@ftgamer2")

    # Step 1: TG Info se number nikalo
    tg = get_tg_info(spell)
    if not tg.get("success"):
        return jsonify({"success": False, "error": "TG API fail", "detail": tg})

    number = tg.get("number")
    if not number:
        return jsonify({"success": False, "error": "Number nahi mila", "tg": tg})

    # Step 2: Advance API me bhejo
    adv = get_advance_info(number)

    return jsonify({
        "success": True,
        "number": number,
        "country": tg.get("country"),
        "country_code": tg.get("country_code"),
        "advance": adv
    })

# ============================================
# 🎨 FRONTEND — HTML (Single File Me)
# ============================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🔍 RTF Rander Tool</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }
  body {
    background: linear-gradient(135deg,#0f0c29,#302b63,#24243e);
    color:#fff; min-height:100vh; padding:20px;
  }
  .container { max-width:800px; margin:auto; }
  h1 { text-align:center; margin-bottom:20px; font-size:1.8rem;
       background:linear-gradient(90deg,#00f2fe,#4facfe);
       -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
  .card {
    background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1);
    border-radius:15px; padding:20px; margin-bottom:20px;
    backdrop-filter:blur(10px);
  }
  input {
    width:100%; padding:14px; border-radius:10px; border:none; outline:none;
    background:rgba(255,255,255,0.1); color:#fff; font-size:1rem; margin-bottom:15px;
  }
  input::placeholder { color:#aaa; }
  .btn-row { display:flex; gap:10px; flex-wrap:wrap; }
  button {
    flex:1; padding:14px; border:none; border-radius:10px; cursor:pointer;
    font-weight:bold; font-size:1rem; transition:0.3s;
    background:linear-gradient(90deg,#00f2fe,#4facfe); color:#000;
    min-width:140px;
  }
  button:hover { transform:translateY(-2px); box-shadow:0 5px 20px rgba(0,242,254,0.4); }
  button.adv { background:linear-gradient(90deg,#f093fb,#f5576c); color:#fff; }
  pre {
    background:#0a0a0a; padding:15px; border-radius:10px; overflow-x:auto;
    font-size:0.85rem; color:#0f0; border:1px solid #333; white-space:pre-wrap;
    word-break:break-word;
  }
  .loader { text-align:center; padding:10px; color:#4facfe; display:none; }
  .loader.show { display:block; }
  .badge {
    display:inline-block; padding:4px 10px; border-radius:20px;
    background:rgba(0,242,254,0.2); color:#00f2fe; font-size:0.75rem;
    margin-bottom:10px;
  }
</style>
</head>
<body>
<div class="container">
  <h1>🔍 RTF Rander Tool</h1>

  <div class="card">
    <span class="badge">🔒 APIs Hidden</span>
    <input id="spell" placeholder="@ftgamer2" value="@ftgamer2">
    <div class="btn-row">
      <button onclick="callApi('tginfo')">📱 TG Info</button>
      <button class="adv" onclick="callApi('advance')">🚀 Advance</button>
    </div>
  </div>

  <div class="loader" id="loader">⏳ Loading...</div>

  <div class="card">
    <pre id="output">Result yahan aayega...</pre>
  </div>
</div>

<script>
async function callApi(type) {
  const spell = document.getElementById('spell').value.trim();
  const out = document.getElementById('output');
  const loader = document.getElementById('loader');

  if (!spell) { out.textContent = "❌ Spell daalo"; return; }

  loader.classList.add('show');
  out.textContent = "⏳ Fetching...";

  try {
    const res = await fetch(`/api/${type}?spell=${encodeURIComponent(spell)}`);
    const data = await res.json();
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = "❌ Error: " + e.message;
  } finally {
    loader.classList.remove('show');
  }
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

# ============================================
# 🚀 RUN
# ============================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
