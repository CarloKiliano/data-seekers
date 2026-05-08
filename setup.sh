#!/usr/bin/env bash
# ============================================================
# Data Seekers – Panam NoSQL Project
# setup.sh — Instalación completa del entorno (macOS / Linux)
#
# USO:
#   chmod +x setup.sh
#   ./setup.sh
# ============================================================

set -e  # Detener si cualquier comando falla

# ── Colores para output ──────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # Sin color

# ── Banner ───────────────────────────────────────────────────
echo ""
echo -e "${BLUE}${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}${BOLD}║      Data Seekers – Panam NoSQL Project          ║${NC}"
echo -e "${BLUE}${BOLD}║              Setup de Entorno                    ║${NC}"
echo -e "${BLUE}${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# ── 1. Verificar Python 3.10+ ────────────────────────────────
echo -e "${YELLOW}[1/6] Verificando versión de Python...${NC}"

PYTHON_CMD=""
for cmd in python3.11 python3.10 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VERSION=$($cmd --version 2>&1 | grep -oP '\d+\.\d+')
        MAJOR=$(echo $VERSION | cut -d. -f1)
        MINOR=$(echo $VERSION | cut -d. -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON_CMD=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}✗ Python 3.10+ no encontrado.${NC}"
    echo "  Instálalo desde: https://www.python.org/downloads/"
    exit 1
fi

echo -e "${GREEN}✓ Usando: $($PYTHON_CMD --version)${NC}"

# ── 2. Crear entorno virtual ─────────────────────────────────
echo ""
echo -e "${YELLOW}[2/6] Creando entorno virtual (.venv)...${NC}"

if [ -d ".venv" ]; then
    echo -e "${YELLOW}  ⚠ Ya existe .venv. Omitiendo creación.${NC}"
    echo "    (Borra la carpeta .venv y re-ejecuta para recrearlo limpio)"
else
    $PYTHON_CMD -m venv .venv
    echo -e "${GREEN}✓ Entorno virtual creado en .venv/${NC}"
fi

# ── 3. Activar entorno virtual ───────────────────────────────
echo ""
echo -e "${YELLOW}[3/6] Activando entorno virtual...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✓ Entorno virtual activo: $(which python)${NC}"

# ── 4. Actualizar pip e instalar dependencias ────────────────
echo ""
echo -e "${YELLOW}[4/6] Instalando dependencias desde requirements.txt...${NC}"
pip install --upgrade pip --quiet
pip install -r requirements.txt

echo -e "${GREEN}✓ Dependencias instaladas correctamente${NC}"

# ── 5. Configurar archivo .env ───────────────────────────────
echo ""
echo -e "${YELLOW}[5/6] Configurando variables de entorno...${NC}"

if [ -f ".env" ]; then
    echo -e "${YELLOW}  ⚠ .env ya existe. No se sobreescribirá.${NC}"
else
    cp .env.example .env
    echo -e "${GREEN}✓ Archivo .env creado desde .env.example${NC}"
    echo -e "  ${BOLD}→ Edita .env si necesitas cambiar host/puertos de BD${NC}"
fi

# ── 6. Verificar Docker ──────────────────────────────────────
echo ""
echo -e "${YELLOW}[6/6] Verificando Docker...${NC}"

if command -v docker &>/dev/null && command -v docker-compose &>/dev/null; then
    echo -e "${GREEN}✓ Docker y Docker Compose disponibles${NC}"
    echo ""
    echo -e "  Para levantar MongoDB y Cassandra:"
    echo -e "  ${BOLD}  docker-compose up -d mongodb cassandra${NC}"
    echo ""
    echo -e "  Para también levantar Jupyter en Docker:"
    echo -e "  ${BOLD}  docker-compose up -d${NC}"
elif command -v docker &>/dev/null; then
    echo -e "${YELLOW}  ⚠ Docker disponible pero docker-compose no encontrado.${NC}"
    echo "    Instala Docker Compose: https://docs.docker.com/compose/install/"
else
    echo -e "${YELLOW}  ⚠ Docker no encontrado.${NC}"
    echo "    Instala Docker Desktop: https://www.docker.com/products/docker-desktop/"
    echo "    O instala MongoDB y Cassandra manualmente (ver README.md)"
fi

# ── Resumen final ────────────────────────────────────────────
echo ""
echo -e "${BLUE}${BOLD}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}✅  Setup completado exitosamente${NC}"
echo -e "${BLUE}${BOLD}══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BOLD}Próximos pasos:${NC}"
echo ""
echo -e "  1. Activa el entorno virtual en tu terminal:"
echo -e "     ${BOLD}source .venv/bin/activate${NC}  (macOS/Linux)"
echo -e "     ${BOLD}.venv\\Scripts\\activate${NC}      (Windows)"
echo ""
echo -e "  2. Levanta las bases de datos con Docker:"
echo -e "     ${BOLD}docker-compose up -d mongodb cassandra${NC}"
echo ""
echo -e "  3. Espera ~30s a que Cassandra inicie y ejecuta los notebooks en orden:"
echo -e "     ${BOLD}jupyter notebook${NC}"
echo -e "     00 → 01 → 02 → 03 → 04"
echo ""
echo -e "  4. Para cargar datos a las BDs directamente:"
echo -e "     ${BOLD}python carga_datos_mongodb.py${NC}"
echo -e "     ${BOLD}python carga_datos_cassandra.py${NC}"
echo ""
