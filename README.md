# Kepler ChessAnalitic

## Instalación y ejecución

Este proyecto utiliza un archivo `pyproject.toml` para gestionar sus dependencias. Para instalar el proyecto en otra PC, sigue estos breves pasos:

1. **Clona el repositorio y entra a la carpeta del proyecto:**
   ```bash
   git clone <url-del-repo>
   cd Kepler-ChessAnalitic
   ```

2. **Crea un entorno virtual (recomendado):**
   ```bash
   python3 -m venv .venv
   ```

3. **Activa el entorno virtual:**
   - En Linux/macOS: `source .venv/bin/activate`
   - En Windows: `.venv\Scripts\activate`

4. **Instala las dependencias desde el `pyproject.toml`:**
   ```bash
   pip install -e .
   ```
   *(Nota: Si también necesitas las herramientas de desarrollo como pytest o para correr los notebooks, ejecuta: `pip install -e ".[dev]" `)*

¡Listo! Ya tienes todas las librerías (pandas, scikit-learn, etc.) instaladas y el proyecto está listo para ejecutarse.
