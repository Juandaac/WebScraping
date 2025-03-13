from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS
from serpapi import GoogleSearch

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Clave de SerpAPI (reemplaza con tu clave real)
SERPAPI_API_KEY = "389b6761114c8b4b8bea3c8a76f692882d3d7485e134a904945b926320c52c79"

# Lista de etiquetas HTML relevantes para buscar palabras clave
TAGS_TO_SEARCH = ["p", "div", "span", "article", "section", "h1", "h2", "h3", "h4", "h5", "h6"]

# Lista de clases/IDs que queremos excluir
EXCLUDED_CLASSES = ["sidebar", "nav", "menu", "footer", "header", "advertisement"]

# Lista de etiquetas HTML que deben eliminarse antes del scraping
EXCLUDED_TAGS = ["nav", "aside", "footer", "header", "menu"]

def scrape_site(url, keywords):
    """
    Extrae los fragmentos de texto de un sitio web donde aparecen las palabras clave,
    evitando elementos irrelevantes como navegación o menús.
    """
    try:
        response = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        })
        if response.status_code != 200:
            return {"url": url, "error": f"HTTP {response.status_code}"}

        soup = BeautifulSoup(response.text, 'html.parser')

        # Eliminar elementos irrelevantes del DOM
        for tag in EXCLUDED_TAGS:
            for element in soup.find_all(tag):
                element.decompose()

        extracted_texts = []

        # Intentar obtener el contenido más relevante
        main_content = soup.find("main") or soup.find("article") or soup.find("div", {"class": "content"})
        if main_content:
            soup = main_content  # Reducimos el scope a esta sección

        # Buscar en etiquetas HTML
        for tag in TAGS_TO_SEARCH:
            elements = soup.find_all(tag)
            for element in elements:
                # Evitar elementos con clases o IDs irrelevantes
                if any(cls in element.get("class", []) for cls in EXCLUDED_CLASSES):
                    continue
                
                text = element.get_text().strip()

                # Filtrar texto muy corto o con demasiados saltos de línea
                if len(text) < 20 or text.count("\n") > 5:
                    continue

                if any(keyword.lower() in text.lower() for keyword in keywords):
                    extracted_texts.append({
                        "tag": tag,
                        "class": element.get("class", ""),
                        "id": element.get("id", ""),
                        "text": text
                    })

        return {"url": url, "matches": extracted_texts}

    except Exception as e:
        return {"url": url, "error": str(e)}

@app.route('/scrape', methods=['POST'])
def scrape():
    """
    Endpoint que recibe un JSON con URLs y palabras clave para hacer Web Scraping.
    """
    data = request.get_json()
    urls = data.get("urls", [])
    keywords = data.get("keywords", [])

    if not urls or not keywords:
        return jsonify({"error": "Se requieren listas de 'urls' y 'keywords'"}), 400

    results = []

    # Uso de múltiples hilos para procesar las URLs en paralelo
    with ThreadPoolExecutor(max_workers=min(10, len(urls))) as executor:
        futures = {executor.submit(scrape_site, url, keywords): url for url in urls}
        for future in futures:
            results.append(future.result())

    return jsonify({"results": results})

@app.route('/search', methods=['GET'])
def search():
    """
    Endpoint que utiliza la Google Search API (SerpAPI) para obtener URLs a partir de un término de búsqueda.
    """
    query = request.args.get("query")
    if not query:
        return jsonify({"urls": []})

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    urls = [result.get("link") for result in results.get("organic_results", []) if result.get("link")]
    return jsonify({"urls": urls})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
