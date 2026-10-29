import os

from flask import Flask, render_template, request, jsonify, Response

app = Flask(__name__)

# Optional password gate — set SITE_PASSWORD in the host's environment and the
# whole site asks for a password (any username works). Leave it unset for open
# access. This is how you keep the demo link to just your client.
SITE_PASSWORD = os.environ.get("SITE_PASSWORD", "")


@app.before_request
def _require_password():
    if not SITE_PASSWORD:
        return  # open access
    auth = request.authorization
    if not auth or auth.password != SITE_PASSWORD:
        return Response(
            "Please sign in to view this demo.", 401,
            {"WWW-Authenticate": 'Basic realm="Willowbrook Demo"'},
        )

HOTEL_NAME = "The Willowbrook Inn"
HOTEL_TAGLINE = "A boutique stay in the heart of the Cotswolds"

# Third-party integrations, read from the environment so no account IDs are
# hard-coded into the repo. Drop in the values and the widgets activate; leave
# them blank and the page shows a labelled placeholder instead.
#
# Chat widget -> our own AI chatbot service (free, runs locally via Ollama).
# The chatbot backend lives in ../chatbot and answers from this hotel's
# documents. Point CHATBOT_API_URL at wherever that service runs, and
# CHATBOT_HOTEL_ID at this hotel's knowledge base (ingested as "willowbrook").
#   CHATBOT_API_URL   full URL of the chatbot /chat endpoint
#   CHATBOT_HOTEL_ID  which hotel's documents to use
#
# Booking calendar + enquiry form -> GoHighLevel (GHL)
#   GHL_CALENDAR_ID       Calendars -> the calendar you want to embed
#   GHL_FORM_ID           Sites -> Forms -> the enquiry form you want to embed
# The widget now calls THIS app's own /chat route (same origin), which proxies
# to the hosted Hugging Face Gradio Space below. So nothing needs to run
# locally except this website — the chatbot lives on Hugging Face.
CHATBOT_HF_SPACE = os.environ.get("CHATBOT_HF_SPACE", "karthi78/hotel-agent")

CHATBOT = {
    "api_url": os.environ.get("CHATBOT_API_URL", "/chat"),
    "hotel_id": os.environ.get("CHATBOT_HOTEL_ID", "willowbrook"),
    # Profile picture shown in the chat header and next to the assistant's
    # replies. Defaults to the site's hero image.
    "avatar_url": os.environ.get("CHATBOT_AVATAR_URL", "/static/img/hero.jpg"),
}

GHL = {
    "calendar_id": os.environ.get("GHL_CALENDAR_ID", ""),
    "form_id": os.environ.get("GHL_FORM_ID", ""),
}


@app.context_processor
def inject_integrations():
    # Makes `chatbot` and `ghl` available to every template, including base.html.
    return {"chatbot": CHATBOT, "ghl": GHL}


# ---- Chatbot proxy -> Hugging Face Gradio Space -----------------------------
# Connects once, lazily (so startup stays fast and works offline until first
# use). The Space may take ~20-30s to wake from sleep on the first request.
_hf_client = None


def _chat_client():
    global _hf_client
    if _hf_client is None:
        from gradio_client import Client
        _hf_client = Client(CHATBOT_HF_SPACE)
    return _hf_client


@app.route("/chat", methods=["POST"])
def chat():
    """The widget posts {message, ...}; we forward to the HF Space and return
    {answer, sources} so the existing front-end needs no changes."""
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"answer": "Please type a question.", "sources": []}), 400
    try:
        answer = _chat_client().predict(message, api_name="/chat")
    except Exception:
        return jsonify({
            "answer": "Sorry, I had trouble connecting. Please try again, "
                      "or call reception on 01234 567890.",
            "sources": [],
        }), 502
    return jsonify({"answer": answer, "sources": []})


@app.route("/")
def home():
    return render_template("index.html", hotel_name=HOTEL_NAME, tagline=HOTEL_TAGLINE)


@app.route("/whatsapp")
def whatsapp():
    return render_template("whatsapp.html", hotel_name=HOTEL_NAME)


@app.route("/inbox")
def inbox():
    return render_template("inbox.html", hotel_name=HOTEL_NAME)


@app.route("/missed-call")
def missed_call():
    return render_template("missed_call.html", hotel_name=HOTEL_NAME)


if __name__ == "__main__":
    # debug stays OFF unless you explicitly set FLASK_DEBUG=1 locally. Never run
    # with debug on in public hosting — it exposes an interactive code console.
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
