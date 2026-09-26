from flask import Flask, request, jsonify, redirect
import requests

app = Flask(__name__)

# ============================================
# 🔒 HIDDEN APIs
# ============================================
API_TG = "https://rtf-api-server.onrender.com/api?types=telegram&key=RTFSERVER&spell={spell}"
API_ADV = "https://bronx-ultra-king.duckdns.org/api/custom/search?key=8509&num={num}"

# ============================================
# 🔧 TG Info — sirf 3 fields
# ============================================
def get_tg_info(spell):
    try:
        url = API_TG.format(spell=spell)
        r = requests.get(url, timeout=15)
        data = r.json()

        result = data.get("result", {}) if isinstance(data, dict) else {}

        return {
            "Number": result.get("Number"),
            "Country": result.get("Country"),
            "Country Code": result.get("Country Code")
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================
# 🔧 Advance
# ============================================
def get_advance_info(num):
    try:
        url = API_ADV.format(num=num)
        r = requests.get(url, timeout=20)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ============================================
# 🔥 HOOK — /tg=@user  aur  /tg?adv=@user handle karega
# ============================================
@app.before_request
def catch_tg_equals():
    path = request.path

    # Case 1: /tg=@username  (path me = ke saath)
    if path.startswith("/tg="):
        spell = path[4:]  # "@username" ya "6624927061"
        spell = spell.strip()

        if not spell:
            return jsonify({"error": "Spell khali hai"}), 400

        # Agar adv chahiye? URL: /tg=@user?adv=1
        if "adv" in request.args:
            tg = get_tg_info(spell)
            num = tg.get("Number")
            if not num:
                return jsonify({"error": "Number nahi mila", "tg": tg}), 404
            return jsonify(get_advance_info(num))

        # Normal TG Info
        return jsonify(get_tg_info(spell))

    # Case 2: /tg?adv=@username  (query me adv ke saath)
    if path == "/tg" and "adv" in request.args:
        spell = request.args.get("adv", "").strip()
        if not spell:
            return jsonify({"error": "adv khali hai"}), 400

        tg = get_tg_info(spell)
        num = tg.get("Number")
        if not num:
            return jsonify({"error": "Number nahi mila", "tg": tg}), 404
        return jsonify(get_advance_info(num))

    # Case 3: /tg?spell=@user  ya  /tg?q=@user
    if path == "/tg":
        spell = request.args.get("spell") or request.args.get("q")
        if spell:
            return jsonify(get_tg_info(spell.strip()))

# ============================================
# 🏠 HOME
# ============================================
@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "usage": {
            "tg_info": "/tg=@username  ya  /tg=6624927061",
            "advance": "/tg?adv=@username  ya  /tg?adv=6624927061"
        }
    })

# ============================================
# 🚀 RUN
# ============================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
