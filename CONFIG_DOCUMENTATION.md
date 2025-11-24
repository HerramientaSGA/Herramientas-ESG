# 📄 Documentación de config.json

Este documento describe la estructura y el propósito de cada campo en el archivo `config.json`.

## 🎯 Propósito

El archivo `config.json` almacena la configuración del país y ubicación que se va a analizar. Es actualizado automáticamente cuando se recibe un nuevo formulario a través de Power Automate y GitHub Issues.

## 📋 Estructura Completa

```json
{
  "@odata.etag": "",
  "ItemInternalId": "beaad7b8-4286-4224-8421-cae4adf92d29",
  "Id": "14",
  "Hora de inicio": "45979.6351967593",
  "Hora de finalización": "45979.6354861111",
  "Correo electrónico": "anonymous",
  "Nombre": "",
  "Language": "Español (España, alfabetización internacional)",
  "Indique su nombre": "ww",
  "Indique su correo corporativo": "ww",
  "Indique la localización según las coordenadas de google maps (p_x002e_ej_x002e_ -5_x002e_919447, 39_x002e_352937)": "30.041084, 31.236116",
  "Indique el municipio": "El cairo",
  "Indique la región": "El cairo",
  "Indique el país": "Egypt",
  "⚠️ Atención_x003a_ Esta acción eliminará los procesos del proyecto actual_x002e_..": "Aceptar",
  "Latitud": "30.041084",
  "Longitud": "31.236116",
  "Distancia al aeropuerto (km)": "13",
  "Aeropuerto más cercano": "Almaza Air Force Base",
  "Tipo_Aeropuerto": "medium_airport",
  "id_formulario": "Unico"
}
```

## 🔍 Descripción de Campos

### Metadatos del Formulario

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `@odata.etag` | String | Etiqueta de versión de OData | `""` |
| `ItemInternalId` | String (UUID) | ID interno único del elemento | `"beaad7b8-4286-4224-8421-cae4adf92d29"` |
| `Id` | String | Identificador numérico del formulario | `"14"` |
| `id_formulario` | String | Tipo de formulario | `"Unico"` |

### Información Temporal

| Campo | Tipo | Descripción | Formato | Ejemplo |
|-------|------|-------------|---------|---------|
| `Hora de inicio` | String | Timestamp de inicio del formulario | Número de serie de fecha de Excel | `"45979.6351967593"` |
| `Hora de finalización` | String | Timestamp de finalización del formulario | Número de serie de fecha de Excel | `"45979.6354861111"` |

**Nota:** Los timestamps están en formato de número de serie de Excel (días desde 1900-01-01).

### Datos del Usuario

| Campo | Tipo | Obligatorio | Descripción | Ejemplo |
|-------|------|-------------|-------------|---------|
| `Nombre` | String | No | Nombre del sistema/formulario | `""` |
| `Indique su nombre` | String | Sí | Nombre del usuario que completa el formulario | `"ww"` |
| `Correo electrónico` | String | No | Email del sistema | `"anonymous"` |
| `Indique su correo corporativo` | String | Sí | Email corporativo del usuario | `"ww"` |
| `Language` | String | No | Idioma del formulario | `"Español (España, alfabetización internacional)"` |

### 🌍 Ubicación Geográfica (CRÍTICO)

Estos son los campos más importantes para el análisis:

| Campo | Tipo | Obligatorio | Descripción | Uso en HISTORICO.py | Ejemplo |
|-------|------|-------------|-------------|---------------------|---------|
| **`Indique el país`** | String | **SÍ** | **Nombre del país a analizar** | **Usado para buscar código ISO del país** | `"Egypt"` |
| `Indique la región` | String | Sí | Región o provincia dentro del país | Referencia geográfica | `"El cairo"` |
| `Indique el municipio` | String | Sí | Municipio o ciudad | Referencia geográfica | `"El cairo"` |
| `Latitud` | String | Sí | Coordenada de latitud decimal | Ubicación exacta | `"30.041084"` |
| `Longitud` | String | Sí | Coordenada de longitud decimal | Ubicación exacta | `"31.236116"` |
| `Indique la localización según las coordenadas de google maps (...)` | String | Sí | Coordenadas en formato Google Maps | Extracción de lat/long | `"30.041084, 31.236116"` |

#### ⚠️ Importante: Campo "Indique el país"

Este es el **único campo utilizado por HISTORICO.py** para determinar qué país analizar.

**Requisitos:**
- Debe estar en **inglés**
- Debe coincidir con nombres reconocidos por el Banco Mundial
- Se acepta coincidencia parcial (ej: "egypt" encuentra "Egypt, Arab Rep.")

**Ejemplos válidos:**
```json
✅ "Egypt"           → Encuentra "Egypt, Arab Rep."
✅ "Tanzania"        → Encuentra "Tanzania"
✅ "United States"   → Encuentra "United States"
✅ "Spain"           → Encuentra "Spain"
✅ "Kenya"           → Encuentra "Kenya"

❌ "Egipto"          → No encontrará el país (usar "Egypt")
❌ "Estados Unidos"  → No encontrará el país (usar "United States")
❌ "España"          → No encontrará el país (usar "Spain")
```

### 🛫 Información de Aeropuerto

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `Aeropuerto más cercano` | String | Nombre del aeropuerto más próximo | `"Almaza Air Force Base"` |
| `Distancia al aeropuerto (km)` | String | Distancia en kilómetros al aeropuerto | `"13"` |
| `Tipo_Aeropuerto` | String | Clasificación del aeropuerto | `"medium_airport"` |

**Tipos de aeropuerto válidos:**
- `"large_airport"` - Aeropuerto internacional grande
- `"medium_airport"` - Aeropuerto mediano
- `"small_airport"` - Aeropuerto pequeño
- `"heliport"` - Helipuerto
- `"closed"` - Aeropuerto cerrado

### 🔐 Confirmaciones del Usuario

| Campo | Tipo | Descripción | Valor esperado |
|-------|------|-------------|----------------|
| `⚠️ Atención_x003a_ Esta acción eliminará los procesos del proyecto actual_x002e_...` | String | Confirmación de sobrescritura de datos | `"Aceptar"` |

**Nota:** Este campo contiene caracteres codificados de Power Automate (`_x002e_` = `.`, `_x003a_` = `:`).

## 🔄 Flujo de Actualización

```
1. Usuario completa formulario en Power Automate
   ↓
2. Power Automate crea GitHub Issue con JSON
   ↓
3. Workflow update-config-json.yml se activa
   ↓
4. Extrae JSON del issue body
   ↓
5. Sobrescribe config.json completamente
   ↓
6. Commit automático: "Update config.json"
   ↓
7. Push al repositorio
   ↓
8. Workflow blank.yml detecta cambio
   ↓
9. Ejecuta HISTORICO.py con nuevo país
```

## 📝 Ejemplo de Uso en Código

### Lectura en HISTORICO.py

```python
import json

# Leer configuración
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Obtener país (campo crítico)
nombre_pais = config.get("Indique el país")
if not nombre_pais:
    raise ValueError("El archivo config.json debe contener la clave 'Indique el país'.")

print(f"Analizando país: {nombre_pais}")
# Output: Analizando país: Egypt
```

### Acceso a otros campos

```python
# Información de ubicación
latitud = config.get("Latitud")
longitud = config.get("Longitud")
municipio = config.get("Indique el municipio")
region = config.get("Indique la región")

print(f"Ubicación: {municipio}, {region}")
print(f"Coordenadas: {latitud}, {longitud}")

# Información del usuario
nombre_usuario = config.get("Indique su nombre")
email_usuario = config.get("Indique su correo corporativo")

print(f"Formulario completado por: {nombre_usuario} ({email_usuario})")

# Información del aeropuerto
aeropuerto = config.get("Aeropuerto más cercano")
distancia = config.get("Distancia al aeropuerto (km)")
tipo_aeropuerto = config.get("Tipo_Aeropuerto")

print(f"Aeropuerto cercano: {aeropuerto} ({tipo_aeropuerto}) a {distancia} km")
```

## 🛠️ Actualización Manual

Si necesitas actualizar el archivo manualmente:

### 1. Editar config.json

```bash
nano config.json
# o
code config.json
```

### 2. Modificar el país

```json
{
  "Indique el país": "Kenya"
}
```

**Nota:** Solo necesitas modificar el campo `"Indique el país"` para cambiar el análisis. Los demás campos son opcionales para HISTORICO.py.

### 3. Verificar formato JSON

```bash
python -m json.tool config.json
```

Si hay errores, verás un mensaje como:
```
Expecting property name enclosed in double quotes: line 5 column 3 (char 123)
```

### 4. Ejecutar análisis

```bash
python HISTORICO.py
```

## 🔍 Validación de config.json

### Script de validación

Puedes usar este script para validar el archivo:

```python
import json
import sys

def validar_config(archivo="config.json"):
    """Valida la estructura de config.json"""

    # 1. Verificar que sea JSON válido
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: JSON inválido - {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Error: Archivo {archivo} no encontrado")
        return False

    # 2. Verificar campo obligatorio
    if "Indique el país" not in config:
        print("❌ Error: Falta el campo obligatorio 'Indique el país'")
        return False

    pais = config.get("Indique el país")
    if not pais or pais.strip() == "":
        print("❌ Error: El campo 'Indique el país' está vacío")
        return False

    # 3. Verificar que esté en formato esperado
    print(f"✅ Configuración válida")
    print(f"   País: {pais}")

    # Mostrar información adicional si existe
    if "Latitud" in config and "Longitud" in config:
        print(f"   Coordenadas: {config['Latitud']}, {config['Longitud']}")

    if "Indique el municipio" in config:
        print(f"   Municipio: {config['Indique el municipio']}")

    return True

if __name__ == "__main__":
    validar_config()
```

**Uso:**
```bash
python validar_config.py
```

## 🐛 Problemas Comunes

### Error: KeyError: 'Indique el país'

**Causa:** El campo obligatorio no existe en el JSON.

**Solución:**
```json
{
  "Indique el país": "Tanzania"
}
```

### Error: json.decoder.JSONDecodeError

**Causa:** JSON mal formado (falta coma, comilla, etc.).

**Solución:** Verificar sintaxis:
- Todas las claves deben estar entre comillas dobles
- Valores string entre comillas dobles
- Última clave-valor sin coma al final
- No se permiten comentarios en JSON

### País no encontrado

**Causa:** Nombre del país no coincide con base de datos del Banco Mundial.

**Solución:** Usar nombres en inglés:
```json
✅ Correcto:
{
  "Indique el país": "Egypt"
}

❌ Incorrecto:
{
  "Indique el país": "Egipto"
}
```

## 📚 Referencias

- [JSON Standard](https://www.json.org/)
- [Power Automate Documentation](https://docs.microsoft.com/en-us/power-automate/)
- [World Bank Country Codes](https://wits.worldbank.org/wits/wits/witshelp/content/codes/country_codes.htm)

## 🔒 Seguridad y Privacidad

### Datos sensibles

El archivo puede contener:
- ✉️ Correos electrónicos de usuarios
- 📍 Ubicaciones geográficas precisas
- 👤 Nombres de usuarios

**Recomendaciones:**
1. No compartir el archivo públicamente si contiene datos reales
2. Usar `.gitignore` para excluir `config.json` si es necesario
3. Considerar anonimizar datos en repositorios públicos

### Ejemplo de .gitignore

Si deseas excluir `config.json` del control de versiones:

```bash
# .gitignore
config.json
```

**Nota:** En este proyecto, `config.json` se versiona porque es necesario para la automatización. Los datos son proporcionados conscientemente por los usuarios a través del formulario.

---

**Última actualización:** 2024
**Versión:** 1.0
