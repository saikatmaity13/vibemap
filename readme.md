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

##  Installation & Local Setup

Want to run this locally? Follow these steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/vibemap-portfolio.git](https://github.com/YOUR_USERNAME/vibemap-portfolio.git)
cd vibemap-portfolio


Engineering Challenges & Solutions
1. The "Memory Wall" on Free Cloud Tier
Challenge: The initial AI model (en_core_web_md) required too much RAM, causing the app to crash immediately upon deployment to Render's free tier (Error 137).

Solution: I optimized the NLP pipeline to use the lightweight en_core_web_sm model and streamlined the build process, reducing memory usage by 60% without sacrificing core intent recognition.

2. Context-Aware Search Logic
Challenge: A simple keyword search for "Quiet" returned cafes, which are often loud and busy.

Solution: I engineered a custom "Vibe Dictionary" in Python that acts as a strict filter. It maps "Quiet" specifically to tags like library, museum, yoga, and park, ensuring the results actually match the user's intent.

3. Handling Large Datasets
Challenge: Visualizing the entire database (2,000+ points) froze the browser.

Solution: Implemented a "Show All" feature that fetches data in optimized JSON batches and uses efficient marker rendering in Leaflet.js to keep the UI smooth.

 Future Improvements
User Reviews: Allow users to rate the "vibe" of a place to crowd-source accuracy.

Real-time Traffic: Integrate Google Maps API to show live busyness levels.

Social Sharing: Allow users to share their "Vibe Crawl" routes with friends.

 Contributing
Contributions are welcome! Feel free to fork the repo and submit a pull request.

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request
Built with ❤️ by SAIKAT MAITY
