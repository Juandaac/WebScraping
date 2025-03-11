from serpapi import GoogleSearch

def buscar_google(palabra_clave, num_paginas=3):
    resultados_totales = []

    for pagina in range(num_paginas):
        params = {
            "q": palabra_clave,  # Término de búsqueda
            "hl": "es",          # Idioma español
            "gl": "co",          # Ubicación (puedes cambiarlo)
            "num": 10,           # Número de resultados por página
            "start": pagina * 10, # Página actual (0, 10, 20, 30, etc.)
            "api_key": "389b6761114c8b4b8bea3c8a76f692882d3d7485e134a904945b926320c52c79"
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        if "organic_results" not in results:
            print(f"⚠ No se encontraron más resultados en la página {pagina + 1}")
            break

        # Extraer títulos, enlaces y fragmentos de texto (snippets)
        resultados_pag = [
            {
                "titulo": resultado.get("title", "Sin título"),
                "enlace": resultado.get("link", "Sin enlace"),
                "texto": resultado.get("snippet", "Sin descripción")
            }
            for resultado in results["organic_results"]
        ]

        resultados_totales.extend(resultados_pag)

    return resultados_totales

# 🔍 Prueba con una búsqueda
palabra = input("🔹 Ingrese una palabra clave: ")
num_paginas = int(input("📄 Ingrese el número de páginas a obtener: "))

resultados = buscar_google(palabra, num_paginas)

print("\n📌 Resultados encontrados:")
for i, resultado in enumerate(resultados, 1):
    print(f"{i}. 📝 {resultado['titulo']}")
    print(f"   🔗 {resultado['enlace']}")
    print(f"   📝 {resultado['texto']}\n")
