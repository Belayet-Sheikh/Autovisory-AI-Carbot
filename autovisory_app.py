# -*- coding: utf-8 -*-
"""Autovisory-AI-Carbot.ipynb




# used car
import kagglehub

# Download latest version
path = kagglehub.dataset_download("austinreese/craigslist-carstrucks-data")

print("Path to dataset files:", path)

# European car
import kagglehub

# Download latest version
path = kagglehub.dataset_download("alemazz11/europe-car-prices")

print("Path to dataset files:", path)

# Gas Car
import kagglehub

# Download latest version
path = kagglehub.dataset_download("CooperUnion/cardataset")

print("Path to dataset files:", path)

# EV
import kagglehub

# Download latest version
path = kagglehub.dataset_download("gunapro/electric-vehicle-population-data")

print("Path to dataset files:", path)





# Step 1 Installing all the dependencies


!pip install -q -U google-generativeai pandas

import google.generativeai as genai
import pandas as pd
import json
import numpy as np
import re
from google.colab import userdata

# Load API Key from Colab Secrets
try:
    GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    print("API Key loaded successfully from Colab Secrets!")
except Exception as e:
    print("Could not load API key. Make sure 'GOOGLE_API_KEY' is set in Colab Secrets.")
    raise e


# STEP 2: LOADING & PREPARING FULL DATASETS

print("\n--- Building Master Databases from Full Datasets ---")
try:

    df_gas = pd.read_csv('/kaggle/input/cardataset/data.csv')
    df_ev = pd.read_csv('/kaggle/input/electric-vehicle-population-data/Electric_Vehicle_Population_Data.csv')
    df_used_us = pd.read_csv('/kaggle/input/craigslist-carstrucks-data/vehicles.csv')
    df_used_europe = pd.read_csv('/kaggle/input/europe-car-prices/car_prices.csv')

    # --- Data Cleaning & Prep ---
    df_gas.columns = df_gas.columns.str.replace(' ', '_').str.lower()
    df_gas = df_gas.rename(columns={'msrp': 'price'})
    df_gas['fuel_type'] = 'Gasoline'
    df_gas['electric_range'] = 0

    df_ev.columns = df_ev.columns.str.replace(' ', '_').str.lower()
    df_ev = df_ev.rename(columns={'model_year': 'year'})
    df_ev['price'] = np.nan
    df_ev['engine_hp'] = np.nan
    df_ev['city_mpg'] = np.nan
    df_ev['fuel_type'] = 'Electric'
    df_ev['vehicle_style'] = 'Electric'

    cols = ['make', 'model', 'year', 'price', 'vehicle_style', 'engine_hp', 'city_mpg', 'fuel_type', 'electric_range']
    df_new_us_master = pd.concat([df_gas[cols], df_ev[cols]], ignore_index=True)
    df_new_us_master = df_new_us_master.dropna(subset=['year', 'make', 'model'])
    df_new_us_master['year'] = df_new_us_master['year'].astype(int)
    print("✅ New US Car Master Dataset created.")

    df_used_us = df_used_us.rename(columns={'manufacturer': 'make'})
    used_us_cols = ['make', 'model', 'year', 'price', 'odometer']
    df_used_us_master = df_used_us[used_us_cols].dropna()
    df_used_us_master = df_used_us_master[df_used_us_master['price'].between(100, 250000)]
    df_used_us_master['year'] = df_used_us_master['year'].astype(int)
    df_used_us_master['odometer'] = df_used_us_master['odometer'].astype(int)
    print("✅ Used US Car Master Dataset created.")

    df_used_europe = df_used_europe.rename(columns={
        'Brand': 'make', 'Model': 'model', 'Year': 'year', 'Price': 'price', 'Kilometers': 'odometer'})
    used_europe_cols = ['make', 'model', 'year', 'price', 'odometer']
    df_used_europe_master = df_used_europe[used_europe_cols].dropna()
    df_used_europe_master['year'] = pd.to_numeric(df_used_europe_master['year'], errors='coerce')
    df_used_europe_master['odometer'] = pd.to_numeric(df_used_europe_master['odometer'], errors='coerce')
    df_used_europe_master = df_used_europe_master.dropna()
    df_used_europe_master['year'] = df_used_europe_master['year'].astype(int)
    df_used_europe_master['odometer'] = df_used_europe_master['odometer'].astype(int)
    print("✅ Used Europe Car Master Dataset created.")

except FileNotFoundError as e:
    print(f"ERROR: Missing file - {e}. Ensure Kaggle datasets are accessible in this environment.")


# STEP 3: AI INTENT & RESPONSE LOGIC

model = genai.GenerativeModel('gemini-1.5-flash')

def determine_next_action(history, user_query):
    history_str = "\n".join([f"{h['role']}: {h['parts']}" for h in history])


    prompt = f"""
    You are Autovisory, a helpful and conversational AI car advisor. Your goal is to classify the user's most recent query into a specific action.

    Based on the user's most recent query, determine the primary intent by following these rules IN ORDER:

    1.  **Small Talk:** If the query is a simple greeting ('hi', 'hello'), farewell ('bye'), expression of gratitude ('thanks', 'thank you'), or other common pleasantries that DO NOT contain a car request, your action is "small_talk". Generate an appropriate, polite response.
        - Example for "thanks": {{"action": "small_talk", "response": "You're very welcome! Is there anything else I can help you analyze or compare?"}}
        - Example for "hello": {{"action": "small_talk", "response": "Hello! How can I help you with your car search today?"}}

    2.  **Clarify:** If the query is a vague car-related request (e.g., "I need a car"), your action is "clarify".
        - JSON: {{"action": "clarify", "response": "To give you the best recommendation, I need a little more information. Could you tell me about your budget, primary use, and priorities?"}}

    3.  **Recommend:** If the user provides details for a recommendation OR asks to modify previous criteria (e.g., "what about something cheaper?", "change my preference to sport cars"), your action is "recommend".
        - JSON: {{"action": "recommend", "response": "Okay, based on your new preferences, I'm finding some options for you..."}}

    4.  **Analyze:** If the user asks for details about ONE specific car model, your action is "analyze".
        - JSON: {{"action": "analyze", "response": "Let me pull up the details for that model."}}

    5.  **Compare:** If the user asks to compare TWO OR MORE specific car models, your action is "compare".
        - JSON: {{"action": "compare", "response": "Excellent comparison. Let me put the specs side-by-side."}}

    6.  **Answer General:** If the user asks a general knowledge question about cars (e.g., "What is a hybrid?"), your action is "answer_general".
        - JSON: {{"action": "answer_general", "response": "That's a great question. Here's an explanation..."}}

    7.  **Reject:** If the query is CLEARLY not about cars (e.g., "What's the weather?"), your action is "reject".
        - JSON: {{"action": "reject", "response": "I'm designed to only answer questions about cars. Could we stick to that topic?"}}

    Conversation History:
    {history_str}

    User's Latest Query: "{user_query}"

    Return only the single, valid JSON object for your chosen action.
    """
    for attempt in range(2):
        try:
            response = model.generate_content(prompt)
            text = re.search(r'\{.*\}', response.text, re.DOTALL).group(0)
            return json.loads(text)
        except Exception:
            continue
    return {"action": "error", "response": "Sorry, I had trouble understanding that. Could you please rephrase?"}


def extract_car_models(text):
    pattern = r'(?:\b(?:vs|versus|compare|between|and)\b\s)?([A-Z][a-zA-Z0-9-]+\s(?:[A-Z][a-zA-Z0-9-]+-?)+|[A-Z][a-zA-Z0-9-]+\s[A-Z][a-zA-Z0-9-]+|[A-Z][a-zA-Z0-9-]+)'
    models = re.findall(pattern, text)
    stop_words = {'Compare', 'Between', 'And', 'The', 'A'}
    return [model.strip() for model in models if model.strip() not in stop_words]


def get_recommendations_and_analysis(full_context_query):

    prompt = f"""
    You're an expert AI Car Analyst. Based on the user's request, recommend 3 cars and provide an analysis.

    FULL CONVERSATION CONTEXT:
    {full_context_query}

    *** CRITICAL INSTRUCTION ON BUDGET INTERPRETATION ***
    When a user provides a budget, you must interpret it as a target price point, not just a maximum limit. A user with a high budget (e.g., $100,000) is interested in the luxury, performance, or high-end vehicles that fit that price range. Do NOT recommend entry-level or mass-market vehicles to a user with a high budget. Your recommendations should be appropriate for the market segment implied by the budget.

    INSTRUCTIONS:
    1.  Analyze the user's needs from the context, paying special attention to the budget as a target.
    2.  Select 3 car models from your knowledge that are the best fit for that market segment.
    3.  For each car, provide a compelling summary and an estimated price range.
    4.  You MUST respond in a valid JSON object like this example. Price must be an integer.

    EXAMPLE JSON RESPONSE:
    {{
      "recommendations": [
        {{
          "make": "BMW",
          "model": "X5",
          "summary": "The BMW X5 is a benchmark for luxury midsize SUVs, offering a powerful engine lineup, a premium interior, and engaging driving dynamics. It's a great choice for those who want performance and practicality without compromise.",
          "price_range": {{
            "min_price": 65000,
            "max_price": 85000,
            "type": "New"
          }}
        }},
        {{
          "make": "Porsche",
          "model": "Cayenne",
          "summary": "For the ultimate in performance SUVs, the Porsche Cayenne delivers a sports-car-like experience with the utility of an SUV. Its handling is exceptional, and the interior is crafted with high-quality materials.",
          "price_range": {{
            "min_price": 80000,
            "max_price": 110000,
            "type": "New"
          }}
        }}
      ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        text = re.search(r'\{.*\}', response.text, re.DOTALL).group(0)
        return json.loads(text)
    except Exception as e:
        return {"error": str(e), "recommendations": []}


def compare_cars_with_ai(full_context_query):

    prompt = f"""
    You are a car expert AI. The user is trying to decide between two or more vehicles.
    Based on this conversation, create a side-by-side comparison.

    FULL CONVERSATION CONTEXT:
    {full_context_query}

    INSTRUCTIONS:
    1. Identify the car models the user wants to compare.
    2. Provide a brief summary for each model.
    3. List 2-3 key strengths and 2-3 key weaknesses for each.
    4. Respond ONLY with a valid JSON object like the example below.

    EXAMPLE JSON RESPONSE:
    {{
      "comparison": [
        {{
          "model": "Honda Civic",
          "summary": "A compact car known for its sporty handling, fuel efficiency, and high reliability ratings. It's a great all-rounder for singles or small families.",
          "strengths": ["Fun-to-drive dynamics", "Excellent fuel economy", "High resale value"],
          "weaknesses": ["Road noise can be high at speed", "Base model is light on features"]
        }},
        {{
          "model": "Toyota Corolla",
          "summary": "The Corolla's reputation is built on reliability, comfort, and safety. It prioritizes a smooth ride and ease of use over sporty performance.",
          "strengths": ["Legendary reliability", "Standard safety features", "Comfortable ride"],
          "weaknesses": ["Uninspired engine performance", "Less engaging to drive than rivals"]
        }}
      ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        text = re.search(r'\{.*\}', response.text, re.DOTALL).group(0)
        return json.loads(text)
    except Exception as e:
        return {"error": str(e), "comparison": []}


def analyze_specific_car_model(car_model):

    prompt = f"""
    You are an expert automotive analyst. Give a clear, concise analysis of the following car model.

    MODEL TO ANALYZE: "{car_model}"

    INSTRUCTIONS:
    1.  Provide a one-paragraph overview of what the car is known for.
    2.  List 3 distinct pros and 3 distinct cons.
    3.  Describe the target audience for this vehicle.
    4.  Provide a typical market price range.
    5.  Respond ONLY in the following valid JSON format.

    EXAMPLE JSON RESPONSE:
    {{
      "model": "Tesla Model Y",
      "overview": "The Tesla Model Y is a fully electric compact SUV that has become incredibly popular for its blend of long-range capability, cutting-edge technology, and impressive performance. It shares many components with the Model 3 sedan but offers more practicality with its hatchback design and available third-row seat.",
      "pros": ["Impressive real-world battery range", "Access to Tesla's reliable Supercharger network", "Quick acceleration and nimble handling"],
      "cons": ["Stiff ride quality, especially on larger wheels", "Reliance on the touchscreen for most controls can be distracting", "Build quality can be inconsistent compared to legacy automakers"],
      "audience": "Tech-savvy individuals and families looking for a practical EV with a focus on performance and access to the best charging infrastructure.",
      "price_estimate_usd": "$45,000 - $60,000"
    }}
    """
    try:
        response = model.generate_content(prompt)
        text = re.search(r'\{.*\}', response.text, re.DOTALL).group(0)
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}



# STEP 4: CHAT LOOP (SYNCED WITH LIVE APP LOGIC)

def start_autovisory_conversation():
    print("\n--- Autovisory - AI Based Global Car Market Analyst ---")
    print("Ask me anything about cars (Type 'exit' to quit)")
    history = []
    try:
        while True:
            user = input("You: ")
            if user.lower() == 'exit':
                print("\nAutovisory: Goodbye!")
                break

            print("\nAutovisory: Thinking...")
            gemini_history = [{"role": "user" if msg.get("role") == "user" else "model", "parts": [msg.get("parts")]} for msg in history]

            action_data = determine_next_action(gemini_history, user)
            action = action_data.get("action", "error")

            if action in ["reject", "clarify", "answer_general", "small_talk"]:
                print("Autovisory:", action_data.get("response"))

            elif action == "recommend":
                full_context = "\n".join([f"{msg['role']}: {msg['parts']}" for msg in history] + [f"user: {user}"])
                print("Autovisory: Let me find some great options for that budget...")
                recs = get_recommendations_and_analysis(full_context)
                if recs.get("recommendations"):
                    print("Autovisory: Based on your preferences, here are 3 solid options:")
                    for r in recs["recommendations"]:
                        print(f"\n🚗 {r.get('make')} {r.get('model')}")
                        print(f"   Summary: {r.get('summary', 'N/A')}")


                        price_info = r.get('price_range', {})
                        min_p = price_info.get('min_price', 0)
                        max_p = price_info.get('max_price', 0)
                        type_p = price_info.get('type', 'N/A')

                        if min_p > 0 and max_p > 0:
                            print(f"   Estimated Price: ${min_p:,} - ${max_p:,} ({type_p})")
                        else:
                            print("   Estimated Price: Not available")
                else:
                    print("Autovisory: Sorry, I couldn't find good options with the provided details.")

            elif action == "analyze":
                candidates = extract_car_models(user)
                model_name = candidates[0] if candidates else ""
                if model_name:
                    analysis = analyze_specific_car_model(model_name)
                    if analysis.get("model"):
                        print(f"Autovisory: Here's a detailed analysis of the {analysis['model']}:")
                        print(f"  Overview: {analysis.get('overview', 'N/A')}")
                        print(f"  Pros: {', '.join(analysis.get('pros', []))}")
                        print(f"  Cons: {', '.join(analysis.get('cons', []))}")
                        print(f"  Ideal For: {analysis.get('audience', 'N/A')}")
                        print(f"  Estimated Price: {analysis.get('price_estimate_usd', 'N/A')}")
                    else:
                        print("Autovisory: Sorry, I couldn't analyze that model.")
                else:
                    print("Autovisory: I couldn't identify a model to analyze. Please be more specific.")

            elif action == "compare":
                full_context = "\n".join([f"{msg['role']}: {msg['parts']}" for msg in history] + [f"user: {user}"])
                result = compare_cars_with_ai(full_context)
                if result.get("comparison"):
                    print("Autovisory: Here's a comparison of your choices:")
                    for car in result["comparison"]:
                        print(f"\n  🚘 {car['model']}")
                        print(f"     Summary: {car.get('summary', 'N/A')}")
                        print(f"     Strengths: {', '.join(car.get('strengths', []))}")
                        print(f"     Weaknesses: {', '.join(car.get('weaknesses', []))}")
                else:
                    print("Autovisory: Sorry, I couldn't generate a comparison. Please mention at least two models clearly.")

            else:
                print("Autovisory:", action_data.get("response", "I encountered an issue. Please try again."))

            history.append({"role": "user", "parts": user})

            history.append({"role": "assistant", "parts": "Okay, proceeding with that."})

    except (EOFError, KeyboardInterrupt):
        print("\nAutovisory: Session ended. Goodbye!")


start_autovisory_conversation()

