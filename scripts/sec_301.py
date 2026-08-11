import csv
import json
import re
import pdfplumber

PDF_PATH = "data/raw/FLIP_301.pdf"
OUTPUT_CSV  = "data/intermediate/flip_301.csv"
#OUTPUT_JSON = "data/intermediate/htsus_table.json"

# ---------------------------------------------------------------------------
# Patrón para detectar un código HTSUS al inicio de una línea
# Ejemplos: 0201.10.05  /  8411.91.90  /  9802.00.80
# ---------------------------------------------------------------------------
HTSUS_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}(?:\.\d+)?")

def clean_description(text: str) -> str:
    """Limpia la descripción: une saltos de línea/espacios y asegura el punto final."""
    if not text:
        return ""
        
    # --- BLINDAJE DE CODIFICACIÓN ---
    # Reemplaza el error del apóstrofe
    text = text.replace("â€™", "'")
    
    # (Opcional) Si luego notas errores con comillas, puedes descomentar esto:
    # text = text.replace("â€œ", '"').replace("â€", '"')
    
    # Reemplaza cualquier secuencia de espacios blancos (incluyendo \n) por un solo espacio
    cleaned = re.sub(r'\s+', ' ', text).strip()
    
    # Añade el punto final si no está presente
    if cleaned and not cleaned.endswith('.'):
        cleaned += '.'
        
    return cleaned

def extract_rows_from_pdf(pdf_path: str) -> list[dict]:
    """
    Lee página a página y reconstruye filas a partir del texto plano.
    Estrategia:
      1. Intentar extract_table() de pdfplumber en cada página.
      2. Si no hay tabla estructurada, caer back a parse de texto layout.
    """
    rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):

            # ── Intento 1: extracción de tabla estructurada ──────────────
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        # Limpia celdas None
                        row = [cell.strip() if cell else "" for cell in row]
                        if not row:
                            continue
                        # Ignora filas de encabezado
                        if row[0].upper() in ("HTSUS", "HTSUS DESCRIPTION"):
                            continue
                        # Necesitamos al menos 2 columnas
                        htsus_code = row[0] if len(row) > 0 else ""
                        
                        # APLICADO AQUÍ:
                        description = clean_description(row[1] if len(row) > 1 else "")
                        scope_lim   = row[2] if len(row) > 2 else ""

                        if HTSUS_RE.match(htsus_code):
                            rows.append({
                                "HTSUS": htsus_code,
                                "Description": description,
                                "Scope Limitations": scope_lim,
                            })
                continue  # página procesada con tabla estructurada

            # ── Intento 2: parse de texto en modo layout ─────────────────
            text = page.extract_text(layout=True) or ""
            lines = text.splitlines()

            current_htsus = ""
            current_desc_parts = []
            current_scope = ""

            def flush_row():
                """Guarda la fila acumulada si tiene código HTSUS."""
                nonlocal current_htsus, current_desc_parts, current_scope
                if current_htsus:
                    # APLICADO AQUÍ:
                    raw_desc = " ".join(current_desc_parts)
                    rows.append({
                        "HTSUS": current_htsus,
                        "Description": clean_description(raw_desc),
                        "Scope Limitations": current_scope.strip(),
                    })
                current_htsus = ""
                current_desc_parts = []
                current_scope = ""

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                # Detecta inicio de nueva fila por código HTSUS
                m = HTSUS_RE.match(stripped)
                if m:
                    flush_row()
                    # El código termina donde acaba el match
                    code_end = m.end()
                    current_htsus = stripped[:code_end].strip()
                    remainder = stripped[code_end:].strip()

                    # La última "palabra" puede ser la limitación de scope
                    # (Aircraft, Ex, Pharma o vacío)
                    scope_keywords = {"Aircraft", "Ex", "Pharma"}
                    words = remainder.split()
                    if words and words[-1] in scope_keywords:
                        current_scope = words[-1]
                        current_desc_parts = [" ".join(words[:-1])]
                    else:
                        current_scope = ""
                        current_desc_parts = [remainder] if remainder else []
                else:
                    # Continuación de descripción o scope
                    scope_keywords = {"Aircraft", "Ex", "Pharma"}
                    words = stripped.split()
                    if words and words[-1] in scope_keywords and current_htsus:
                        current_scope = words[-1]
                        current_desc_parts.append(" ".join(words[:-1]))
                    elif current_htsus:
                        current_desc_parts.append(stripped)

            flush_row()  # última fila de la página

    return rows

def save_csv(rows: list[dict], path: str):
    fieldnames = ["HTSUS", "Description", "Scope Limitations"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  CSV guardado: {path}  ({len(rows)} filas)")

# def save_json(rows: list[dict], path: str):
#    with open(path, "w", encoding="utf-8") as f:
#        json.dump(rows, f, ensure_ascii=False, indent=2)
#    print(f"  JSON guardado: {path}  ({len(rows)} registros)")

if __name__ == "__main__":
    print(f"Procesando: {PDF_PATH}")
    rows = extract_rows_from_pdf(PDF_PATH)
    print(f"Total de filas extraídas: {len(rows)}")

    # Vista previa de las primeras 5 filas
    print("\n── Vista previa (primeras 5 filas) ──")
    for r in rows[:5]:
        print(r)

    save_csv(rows, OUTPUT_CSV)
    # save_json(rows, OUTPUT_JSON)  <--- LÍNEA ELIMINADA O COMENTADA
    print("\n¡Listo!")