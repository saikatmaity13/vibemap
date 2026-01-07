# 🌍 VibeMap - The Vibe-First City Explorer

**VibeMap** is a geospatial web application that redefines how we explore cities. Instead of searching by category (e.g., "coffee shop"), users search by **"vibe"** (e.g., "Quiet", "Nature", "Active").

Built with **Python, Flask, and AI**, this project integrates real-time geospatial data with an intelligent chatbot to help users find the perfect spot for their current mood.

🔗 **Live Demo:** https://vibemap-6ya7.onrender.com



---

## ✨ Key Features

* **🎭 Vibe-Based Search:** Filter locations by moods like *Quiet, Nature, Active, Foodie,* and *Nightlife*.
* **🤖 AI Chatbot:** A smart assistant powered by **spaCy NLP** that understands natural language intents (e.g., *"I need coffee"* → Finds cafes; *"I want peace"* → Finds libraries/parks).
* **🗺️ Interactive Map:** Dynamic **Leaflet.js** map with custom markers, heatmaps, and fly-to animations.
* **❤️ Save & Bookmark:** Users can create an account to save their favorite spots to a personal wishlist (stored in MongoDB).
* **🚀 "Show All" Mode:** Efficiently renders 2,000+ data points from the database without browser lag.
* **📍 Smart "Crawl" Generator:** Auto-generates a route (e.g., "Date Night") connecting a restaurant, a park, and a dessert spot.

---

## 🛠️ Tech Stack

| Component | Technology | Use Case |
| :--- | :--- | :--- |
| **Backend** | Python, Flask | Core application logic & API endpoints. |
| **Database** | MongoDB Atlas | Cloud NoSQL database for places & users. |
| **AI / NLP** | spaCy (`en_core_web_sm`) | Intent recognition for the chatbot. |
| **Frontend** | HTML, CSS, JavaScript | Glassmorphism UI & responsive design. |
| **Mapping** | Leaflet.js, OpenStreetMap | Interactive map rendering & geocoding. |
| **Deployment** | Render | Cloud hosting with Gunicorn. |

---


Built  by SAIKAT MAITY
