const widget = document.getElementById("chat-widget");
const toggle = document.getElementById("chat-toggle");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const messages = document.getElementById("chat-messages");

toggle.addEventListener("click", () => {
  widget.classList.toggle("closed");
});

const RESPONSES = [
  { keys: ["park", "parking", "car"], reply: "Yes, we have free on-site parking for all guests — no need to book in advance." },
  { keys: ["breakfast", "food", "eat"], reply: "Breakfast is included with every room, served 7:30–10:30am in the garden room." },
  { keys: ["pet", "dog", "cat"], reply: "We're pet-friendly in the Loft Retreat and Garden Room — just let us know when booking." },
  { keys: ["cancel", "refund"], reply: "Free cancellation up to 48 hours before arrival, no questions asked." },
  { keys: ["price", "cost", "rate", "night"], reply: "Rooms start from £145/night for the Garden Room. Want me to check availability for specific dates?" },
  { keys: ["check-in", "checkin", "check in", "arrival"], reply: "Check-in is from 3pm and check-out is by 11am. Early check-in may be available on request." },
  { keys: ["book", "availability", "room"], reply: "I can help with that — what dates are you looking at, and how many guests?" },
];

function botReply(text) {
  const lower = text.toLowerCase();
  const match = RESPONSES.find(r => r.keys.some(k => lower.includes(k)));
  return match ? match.reply : "Thanks for your message! One of our team will follow up shortly — or you can call us on 01234 567890.";
}

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = "msg " + sender;
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  addMessage(text, "user");
  input.value = "";
  setTimeout(() => addMessage(botReply(text), "bot"), 500);
});

if (new URLSearchParams(window.location.search).get("seed") === "1") {
  const script = [
    ["user", "Do you have parking?"],
    ["bot", botReply("parking")],
    ["user", "Is breakfast included?"],
    ["bot", botReply("breakfast")],
  ];
  script.forEach(([sender, text], i) => {
    setTimeout(() => addMessage(text, sender), 300 * (i + 1));
  });
}
