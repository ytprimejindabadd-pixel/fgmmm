from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ============================================
# 🔒 HIDDEN APIs
# ============================================
API_TG = "https://rtf-api-server.onrender.com/api?types=telegram&key=RTFSERVER&spell={spell}"
API_ADV = "https://bronx-ultra-king.duckdns.org/api/custom/search?key=8509&num={num}"

# ============================================
# 🔧 TG Info — sirf 3 fields return karega
# ============================================
def get_tg_info(spell):
    try:
        url = API_TG.format(spell=spell)
        r = requests.get(url, timeout=15)
        data = r.json()

        # result ke andar data hai
        result = data.get("result", {}) if isinstance(data, dict) else {}

        return {
            "Number": result.get("Number"),
            "Country": result.get("Country"),
            "Country Code": result.get("Country Code")
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================
# 🔧 Advance Info
# ============================================
def get_advance_info(num):
    try:
        url = API_ADV.format(num=num)
        r = requests.get(url, timeout=20)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ============================================
# 🌐 MAIN ROUTE — /tg=@username  ya  /tg?adv=
# ============================================
@app.route("/tg", methods=["GET"])
@app.route("/tg=", methods=["GET"])
def tg_route():
    # ---- Mode 1: Advance ----
    if "adv" in request.args:
        # spell nikalna — ya to ?adv=@user ya ?adv=6624927061
        spell = request.args.get("adv", "").strip()
        if not spell:
            return jsonify({"error": "adv parameter khali hai"}), 400

        # TG se number lo
        tg = get_tg_info(spell)
        num = tg.get("Number")
        if not num:
            return jsonify({"error": "Number nahi mila", "tg": tg}), 404

        # Advance API me bhejo
        adv = get_advance_info(num)
        return jsonify(adv)

    # ---- Mode 2: TG Info ----
    # URL: /tg=@username  ya  /tg=6624927061
    spell = request.args.get("spell") or request.args.get("q")

    # Agar path se aaya (jaise /tg=@user)
    if not spell:
        # raw path se nikalne ki koshish
        raw = request.full_path.rstrip("?")
        if raw.startswith("/tg="):
            spell = raw[4:]
        elif raw.startswith("/tg"):
            spell = ""

    if not spell:
        return jsonify({"error": "Spell daalo — /tg=@username ya /tg?adv=@username"}), 400

    # Agar number diya (6624927061) to @ laga do? Nahi, API jaisa hai waisa bhejo
    tg = get_tg_info(spell)
    return jsonify(tg)

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
