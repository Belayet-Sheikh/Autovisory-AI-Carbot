# 🚗 Autovisory - AI Car Market Analyst

**Autovisory** is an interactive, AI-powered chatbot designed to be your expert guide in the complex world of cars. Powered by Google's Gemini Pro, this app helps users get clear, data-driven recommendations, comparisons, and analyses for new and used cars across the US and European markets.

**[➡️ View the Live App Here](https://autovisory-demo-app.streamlit.app/)**  <!-- ## 👈 PASTE YOUR LIVE APP LINK HERE! ## -->

### Project Screenshots

![Screenshot 1 of the Autovisory application](https://github.com/user-attachments/assets/bef8b8b4-224d-47f8-8106-99afe5e9a9d4)

![Screenshot 2 of the Autovisory application](https://github.com/user-attachments/assets/397c4506-5c5c-4f75-a939-a4d2bfbd7bea)

![Screenshot 3 of the Autovisory application](https://github.com/user-attachments/assets/229b0abe-675d-41ed-ae03-cba8fd312eca)

![Screenshot 4 of the Autovisory application](https://github.com/user-attachments/assets/9a863173-ecc8-4a5d-afc5-6aab099cf522)
---

## ✨ Key Features

This application understands user intent and provides tailored responses:

*   **🗣️ Clarification:** If a user is unsure where to start (e.g., "I need a car"), the app asks clarifying questions about budget, lifestyle, and priorities.
*   **✅ Recommendations:** Provides 3 tailored car recommendations based on a user's specific needs, including market price estimates.
*   **🆚 Side-by-Side Comparisons:** Generates a structured comparison of two or more car models, highlighting their respective strengths and weaknesses.
*   **📊 Detailed Analysis:** Delivers a comprehensive overview of a specific car model, including its pros, cons, target audience, and key specifications.
*   **🌍 Global Data:** Leverages datasets from both the US and European car markets to provide a broader perspective.

---

## 🛠️ Tech Stack & Data

*   **Frontend:** [Streamlit](https://streamlit.io/)
*   **Language:** Python
*   **LLM:** [Google Gemini Pro](https://ai.google.dev/)
*   **Core Libraries:** Pandas, NumPy, Google Generative AI SDK

### 📈 Data Sources
The analysis is powered by several datasets from Kaggle:
*   [Kaggle Car Features and MSRP](https://www.kaggle.com/datasets/CooperUnion/cardataset)
*   [Electric Vehicle Population Data](https://www.kaggle.com/datasets/geoffnel/electric-vehicle-population-data)
*   [Craigslist Used Cars Data](https://www.kaggle.com/datasets/austinreese/craigslist-carstrucks-data)
*   [Used Car Prices in Europe](https://www.kaggle.com/datasets/kplaur20/used-car-prices-in-europe)

---

## 🚀 How to Run Locally

To run this application on your own machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/autovisory-streamlit-app.git
    cd autovisory-streamlit-app
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your API Key:**
    *   Create a folder in the root directory: `.streamlit`
    *   Inside that folder, create a file: `secrets.toml`
    *   Add your Google API key to the secrets file like this:
        ```toml
        GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
        ```

4.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
