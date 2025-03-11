import requests
import json
from serpapi import GoogleSearch

API_URL = "http://127.0.0.1:5000/scrape"
API_KEY = "389b6761114c8b4b8bea3c8a76f692882d3d7485e134a904945b926320c52c79"  # Reemplaza con tu clave de SerpAPI

def get_urls_from_google(query):
    """
    Realiza una búsqueda en Google y retorna una lista de URLs de los resultados orgánicos.
    """
    params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    urls = [result.get("link") for result in results.get("organic_results", []) if result.get("link")]
    return urls

def get_user_input():
    """
    Solicita al usuario el término de búsqueda para Google y las palabras clave a analizar.
    Obtiene automáticamente las URLs a partir del término de búsqueda.
    """
    search_query = input("🔎 Ingrese el término de búsqueda para Google: ").strip()
    urls = get_urls_from_google(search_query)
    print(f"\nSe han obtenido {len(urls)} URLs de Google.")

    keywords = []
    print("\n🔑 Ingrese las palabras clave (presione Enter sin escribir nada para finalizar):")
    while True:
        keyword = input("Palabra clave: ").strip()
        if not keyword:
            break
        keywords.append(keyword)
    
    return {"urls": urls, "keywords": keywords}

def send_request(data):
    """
    Envía la solicitud al servicio REST y obtiene los resultados.
    """
    try:
        response = requests.post(API_URL, json=data, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def display_results(results):
    """
    Muestra los resultados obtenidos del scraping de manera estructurada.
    """
    print("\n📌 Resultados del Web Scraping:\n")
    for result in results.get("results", []):
        print(f"🌍 URL: {result['url']}")
        if "error" in result:
            print(f"❌ Error: {result['error']}\n")
            continue
        for match in result["matches"]:
            tag = match["tag"]
            css_class = ", ".join(match["class"]) if match["class"] else "N/A"
            element_id = match["id"] if match["id"] else "N/A"
            text = match["text"]
            print(f"🔹 [{tag}] (class: {css_class}, id: {element_id})")
            print(f"   ✏️ {text}\n")
        print("-" * 80)

if __name__ == "__main__":
    print("🕵️ Cliente de Web Scraping API\n")
    user_data = get_user_input()  # Solicitar datos al usuario
    if not user_data["urls"] or not user_data["keywords"]:
        print("⚠️ Debe obtener al menos una URL y una palabra clave.")
    else:
        print("\n⏳ Enviando solicitud al API...")
        result_data = send_request(user_data)
        display_results(result_data)
