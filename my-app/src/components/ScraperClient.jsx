import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Form, Button, Table, Alert, ListGroup } from "react-bootstrap";
import "../styles/scraper.css";

const ScraperClient = () => {
  const [urls, setUrls] = useState([]);
  const [keywords, setKeywords] = useState([""]);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  const API_URL = "http://127.0.0.1:5000/scrape"; // Microservicio Flask
  const SEARCH_API_URL = "http://127.0.0.1:5000/search"; // Nuevo endpoint para búsqueda en Google

  // Función para obtener URLs desde el endpoint de búsqueda
  const fetchUrls = async () => {
    try {
      const response = await axios.get(SEARCH_API_URL, { params: { query: searchQuery } });
      setUrls(response.data.urls);
    } catch (err) {
      setError("Error al obtener URLs desde Google Search API.");
    }
  };

  const handleKeywordChange = (index, value) => {
    const newKeywords = [...keywords];
    newKeywords[index] = value;
    setKeywords(newKeywords);
  };

  const addKeywordField = () => setKeywords([...keywords, ""]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    const validKeywords = keywords.filter((keyword) => keyword.trim() !== "");

    if (urls.length === 0 || validKeywords.length === 0) {
      setError("Debe obtener URLs y al menos una palabra clave.");
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(API_URL, {
        urls: urls,
        keywords: validKeywords,
      });
      setResults(response.data.results);
    } catch (err) {
      setError("Error al conectar con el servidor. Asegúrese de que el backend está en ejecución.");
    }
    setLoading(false);
  };

  return (
    <Container className="mt-5">
      <h2 className="mb-4 text-center">🔍 Web Scraper Cliente</h2>
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Form>
        <Form.Group className="mb-3">
          <Form.Label>🔎 Término de Búsqueda en Google</Form.Label>
          <Form.Control
            type="text"
            placeholder="Ingrese el término de búsqueda"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Button variant="secondary" onClick={fetchUrls} className="mt-2">
            Obtener URLs
          </Button>
        </Form.Group>
      </Form>

      {urls.length > 0 && (
        <div className="mb-4">
          <h5>🔗 URLs obtenidas:</h5>
          <ListGroup>
            {urls.map((url, idx) => (
              <ListGroup.Item key={idx}>{url}</ListGroup.Item>
            ))}
          </ListGroup>
        </div>
      )}

      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Label>🔑 Palabras Clave</Form.Label>
          {keywords.map((keyword, index) => (
            <Form.Control
              key={index}
              type="text"
              placeholder="Ingrese una palabra clave"
              value={keyword}
              onChange={(e) => handleKeywordChange(index, e.target.value)}
              className="mb-2"
            />
          ))}
          <Button variant="secondary" onClick={addKeywordField} className="mt-2">
            + Agregar otra palabra clave
          </Button>
        </Form.Group>

        <Button variant="primary" type="submit" disabled={loading}>
          {loading ? "🔄 Analizando..." : "🚀 Analizar"}
        </Button>
      </Form>

      {results.length > 0 && (
        <div className="mt-5">
          <h4>📌 Resultados del Web Scraping</h4>
          {results.map((result, idx) => (
            <div key={idx} className="mt-4">
              <h5 className="text-primary">🌍 {result.url}</h5>
              {result.error ? (
                <Alert variant="danger">❌ Error: {result.error}</Alert>
              ) : (
                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>Etiqueta</th>
                      <th>Clase</th>
                      <th>ID</th>
                      <th>Texto Encontrado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.matches.map((match, index) => (
                      <tr key={index}>
                        <td>{match.tag}</td>
                        <td>{match.class ? match.class.join(", ") : "N/A"}</td>
                        <td>{match.id || "N/A"}</td>
                        <td>{match.text}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </div>
          ))}
        </div>
      )}
    </Container>
  );
};

export default ScraperClient;
