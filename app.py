from flask import Flask, render_template

app = Flask(__name__)

HOTEL_NAME = "The Willowbrook Inn"
HOTEL_TAGLINE = "A boutique stay in the heart of the Cotswolds"


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
    app.run(debug=True, port=5050)
