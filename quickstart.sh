#!/bin/bash
# Quick start script for AI Dev Graph

set -e

echo "🧠 AI Dev Graph - Quick Start"
echo "=============================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instala Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION encontrado"

# Check if already installed
if python3 -c "import ai_dev_graph" 2>/dev/null; then
    echo "✓ ai_dev_graph ya está instalado"
else
    echo "📦 Instalando ai_dev_graph..."
    pip install -e . > /dev/null 2>&1
    echo "✓ Instalación completada"
fi

# Initialize graph if not exists
if [ ! -f "graphs/v0_initial.json" ]; then
    echo "📊 Inicializando grafo..."
    python3 -m ai_dev_graph.cli init > /dev/null 2>&1
    echo "✓ Grafo inicializado"
fi

echo ""
echo "🚀 Iniciando servidor..."
echo ""
echo "───────────────────────────────────────────"
echo "🌐 Admin Panel:  http://localhost:8000/admin"
echo "📚 API Docs:     http://localhost:8000/docs"
echo "🏥 Health:       http://localhost:8000/health"
echo "───────────────────────────────────────────"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

python3 -m ai_dev_graph.cli server --reload
