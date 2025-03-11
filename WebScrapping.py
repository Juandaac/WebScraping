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

def scrape_site(url, keywords):
    """
    Extrae los fragmentos de texto de un sitio web donde aparecen las palabras clave,
    buscando en etiquetas, clases y atributos id.
    """
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return {"url": url, "error": f"HTTP {response.status_code}"}

        soup = BeautifulSoup(response.text, 'html.parser')
        extracted_texts = []

        # Buscar en etiquetas HTML
        for tag in TAGS_TO_SEARCH:
            elements = soup.find_all(tag)
            for element in elements:
                text = element.get_text().strip()
                if any(keyword.lower() in text.lower() for keyword in keywords):
                    extracted_texts.append({
                        "tag": tag,
                        "class": element.get("class", ""),
                        "id": element.get("id", ""),
                        "text": text
                    })

        # Buscar en atributos class e id de cualquier etiqueta
        for element in soup.find_all(True):  # Encuentra cualquier etiqueta HTML
            element_class = element.get("class", "")
            element_id = element.get("id", "")

            if any(keyword.lower() in str(element_class).lower() for keyword in keywords) or \
               any(keyword.lower() in str(element_id).lower() for keyword in keywords):

                extracted_texts.append({
                    "tag": element.name,
                    "class": element_class,
                    "id": element_id,
                    "text": element.get_text().strip()
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
    with ThreadPoolExecutor(max_workers=5) as executor:
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
