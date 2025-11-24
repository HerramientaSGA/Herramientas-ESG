# 📊 SGA - Sistema de Gestión y Análisis de Indicadores de Desarrollo

Sistema automatizado para la recolección, procesamiento y análisis de indicadores económicos y de desarrollo del Banco Mundial.

## 🎯 Descripción General

**SGA** es una plataforma automatizada que:
- 🌍 Recopila datos económicos y de desarrollo de países específicos
- 📈 Procesa indicadores del Banco Mundial automáticamente
- 🔄 Categoriza métricas según estándares internacionales
- 📑 Genera reportes históricos en formato Excel
- ⚡ Se ejecuta automáticamente cada 5 minutos vía GitHub Actions

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Power Automate / Forms                    │
│                  (Entrada de datos de usuario)               │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              GitHub Issue (Datos del formulario)             │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│     Workflow: update-config-json.yml                         │
│     → Actualiza config.json con datos del formulario         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│     Workflow: blank.yml (cada 5 minutos)                     │
│     → Ejecuta HISTORICO.py                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              HISTORICO.py (Script principal)                 │
│  1. Lee país desde config.json                               │
│  2. Descarga 21+ indicadores del Banco Mundial               │
│  3. Procesa y limpia datos                                   │
│  4. Categoriza según umbrales internacionales                │
│  5. Genera Historico.xlsx                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│           Auto-commit y Push al repositorio                  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Estructura del Proyecto

```
SGA/
├── .github/workflows/          # Automatización con GitHub Actions
│   ├── blank.yml              # Ejecuta HISTORICO.py cada 5 minutos
│   └── update-config-json.yml # Actualiza config.json desde issues
├── HISTORICO.py               # Script principal de procesamiento
├── config.json                # Configuración del país a analizar
├── Historico.xlsx             # Salida: Datos históricos (últimos 10 años)
├── datos_generados.xlsx       # Salida: Datos generados adicionales
├── Ejecucion.json            # Metadatos de ejecución
└── README.md                  # Esta documentación
```

## 🔧 Componentes Principales

### 1. HISTORICO.py

Script de Python que automatiza todo el proceso de recolección y análisis de datos.

**Funcionalidades clave:**
- ✅ Búsqueda automática de código ISO del país
- ✅ Descarga de 21+ indicadores del Banco Mundial
- ✅ Transformación de datos de formato ancho a largo
- ✅ Limpieza y normalización de datos numéricos
- ✅ Categorización según estándares internacionales
- ✅ Generación de ratio turistas/residentes
- ✅ Exportación a Excel de últimos 10 años

**Dependencias:**
```python
pandas      # Manipulación de datos
numpy       # Operaciones numéricas
json        # Lectura de configuración
openpyxl    # Escritura de archivos Excel
xlrd        # Lectura de archivos Excel
```

### 2. config.json

Archivo de configuración que contiene los datos del formulario de entrada.

**Campos principales:**
```json
{
  "Indique el país": "Egypt",              // País a analizar
  "Indique su nombre": "...",              // Nombre del usuario
  "Indique su correo corporativo": "...",  // Email del usuario
  "Indique la localización...": "...",     // Coordenadas GPS
  "Indique el municipio": "...",           // Municipio
  "Indique la región": "...",              // Región
  "Latitud": "...",                        // Latitud decimal
  "Longitud": "...",                       // Longitud decimal
  "Distancia al aeropuerto (km)": "...",   // Distancia al aeropuerto
  "Aeropuerto más cercano": "...",         // Nombre del aeropuerto
  "Tipo_Aeropuerto": "..."                 // Tipo de aeropuerto
}
```

### 3. GitHub Actions Workflows

#### blank.yml - Actualización de datos del Banco Mundial

```yaml
Trigger: Manual o cada 5 minutos
Acción:
  1. Instala Python 3.11
  2. Instala dependencias (pandas, numpy, openpyxl, xlrd)
  3. Ejecuta HISTORICO.py
  4. Hace commit de Historico.xlsx
  5. Push al repositorio
```

#### update-config-json.yml - Sincronización de configuración

```yaml
Trigger: Al abrir un nuevo issue de GitHub
Acción:
  1. Extrae JSON del cuerpo del issue
  2. Actualiza config.json
  3. Hace commit y push
```

## 📊 Indicadores Procesados

El sistema procesa **21+ indicadores** del Banco Mundial organizados en 6 categorías:

### 🏛️ Gobernanza y Estabilidad
- **Control de Corrupción** (escala -2.5 a +2.5)
- **Estado de Derecho** (escala -2.5 a +2.5)
- **Efectividad Gubernamental** (escala -2.5 a +2.5)
- **Rendición de Cuentas** (escala -2.5 a +2.5)
- **Estabilidad Política** (percentil 0-100)
- **Calidad Regulatoria** (percentil 0-100)

### 👥 Demografía y Población
- **Población Total**
- **Población Urbana** (%)
- **Crecimiento Poblacional** (% anual)
- **Porcentaje en Edad Laboral** (15-64 años)
- **Porcentaje con Educación Secundaria** (%)

### 💰 Economía y Pobreza
- **Pobreza Multidimensional** (% población)
- **Pobreza Extrema** (% población < $2.15/día)
- **Tasa de Desempleo** (%)
- **Inflación - IPC** (% anual)

### ✈️ Turismo
- **Cantidad de Turistas por Año**
- **Ratio Turistas/Residentes** (métrica calculada)

### 🛡️ Seguridad
- **Homicidios** (por cada 100,000 habitantes)
- **Inseguridad Alimentaria** (%)

### 🚰 Servicios Básicos
- **Acceso a Agua Potable** (%)
- **Acceso a Saneamiento** (%)

## 🎨 Sistema de Categorización

Cada indicador se categoriza en niveles de riesgo usando emojis visuales:

| Categoría | Emoji | Significado |
|-----------|-------|-------------|
| **BAJO ⭣** | ⭣ | Nivel óptimo o bajo riesgo |
| **MEDIO ⭤** | ⭤ | Nivel moderado o riesgo medio |
| **ALTO ⭡** | ⭡ | Nivel elevado o alto riesgo |
| **MUY ALTO ⚠** | ⚠ | Nivel crítico o muy alto riesgo |

### Ejemplos de Umbrales

#### Gobernanza (Control de Corrupción, Estado de Derecho, etc.)
```
≥ 1.0    → BAJO ⭣ (Buena gobernanza)
0.0-0.99 → MEDIO ⭤
-0.01 a -1.0 → ALTO ⭡
< -1.0   → MUY ALTO ⚠ (Gobernanza deficiente)
```

#### Homicidios (por 100,000 habitantes)
```
< 5      → BAJO ⭣ (Seguro)
5-15     → MEDIO ⭤
15-30    → ALTO ⭡
> 30     → MUY ALTO ⚠ (Muy peligroso)
```

#### Inflación (IPC % anual)
```
< 3%     → BAJO ⭣ (Estable)
3-15%    → MEDIO ⭤
> 15%    → ALTO ⭡ (Problemático)
```

## 🚀 Instalación y Uso

### Requisitos Previos

```bash
Python 3.11+
pip (gestor de paquetes de Python)
```

### Instalación Local

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/SGA.git
cd SGA
```

2. **Instalar dependencias:**
```bash
pip install pandas numpy openpyxl xlrd
```

3. **Configurar el país en config.json:**
```json
{
  "Indique el país": "Tanzania"
}
```

4. **Ejecutar el script:**
```bash
python HISTORICO.py
```

5. **Resultado:**
```bash
✅ Código de país encontrado: TZA
✅ Poblacion_Destino cargado.
✅ Crecimiento_Poblacional cargado.
...
✅ Datos guardados en 'Historico.xlsx'.
```

### Uso Automático (GitHub Actions)

El sistema se ejecuta automáticamente:
- ⏱️ **Cada 5 minutos** si hay cambios en config.json
- 📝 **Al crear un nuevo issue** en GitHub con formato JSON
- 🔄 **Manualmente** desde la pestaña Actions

## 📤 Salida de Datos

### Historico.xlsx

Archivo Excel con las siguientes columnas:

| Columna | Descripción | Tipo |
|---------|-------------|------|
| **año** | Año del dato | Entero (Int64) |
| **Indicador_nombre** | Valor numérico del indicador | Float |
| **Indicador_nombre_cat** | Categoría del indicador (BAJO/MEDIO/ALTO/MUY ALTO) | String |

**Ejemplo:**

| año | Poblacion_Destino | Homicidios | Homicidios_cat | Control_Corrupcion | Control_Corrupcion_cat |
|-----|-------------------|------------|----------------|--------------------|-----------------------|
| 2014 | 45000000 | 3.2 | BAJO ⭣ | -0.8 | ALTO ⭡ |
| 2015 | 46000000 | 3.1 | BAJO ⭣ | -0.7 | ALTO ⭡ |
| ... | ... | ... | ... | ... | ... |

**Notas:**
- Solo se guardan los **últimos 10 años** de datos
- Los valores faltantes aparecen como `NaN`
- Las categorías usan emojis para visualización rápida

## 🔍 Funcionamiento Técnico

### 1. Lectura de Configuración
```python
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
nombre_pais = config.get("Indique el país")
```

### 2. Búsqueda de Código de País
```python
# Coincidencia parcial: "egypt" → "Egypt, Arab Rep."
mask = df["Country Name"].str.lower().str.contains(nombre_pais, na=False)
country_code = df[mask]["Country Code"].values[0]  # "EGY"
```

### 3. Descarga de Datos
```python
url = "https://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=excel"
df = pd.read_excel(url, sheet_name="Data", header=3)
```

### 4. Transformación de Formato
```python
# Convierte columnas horizontales de años a filas
df_result = df.melt(
    id_vars="Country Code",
    var_name="año",
    value_name="Poblacion_Destino"
)
```

### 5. Categorización
```python
# Ejemplo: Homicidios
condiciones = [
    Datos_Fecha["Homicidios"] < 5,
    (Datos_Fecha["Homicidios"] >= 5) & (Datos_Fecha["Homicidios"] <= 15),
    (Datos_Fecha["Homicidios"] > 15) & (Datos_Fecha["Homicidios"] <= 30),
    Datos_Fecha["Homicidios"] > 30
]
valores = ["BAJO ⭣", "MEDIO ⭤", "ALTO ⭡", "MUY ALTO ⚠"]
df["Homicidios_cat"] = np.select(condiciones, valores)
```

### 6. Exportación
```python
# Solo últimos 10 años
Datos_Fecha = Datos_Fecha.iloc[-10:]
Datos_Fecha.to_excel("Historico.xlsx", index=False)
```

## 📝 Ejemplos de Uso

### Ejemplo 1: Analizar un nuevo país

1. Modificar `config.json`:
```json
{
  "Indique el país": "Kenya"
}
```

2. Ejecutar:
```bash
python HISTORICO.py
```

3. Resultado:
```
Nombre de país en JSON: Kenya
✅ Código de país encontrado: KEN
✅ Datos guardados en 'Historico.xlsx'.
```

### Ejemplo 2: Integración con Power Automate

1. Usuario completa formulario en Power Automate
2. Power Automate crea issue en GitHub con JSON
3. Workflow `update-config-json.yml` actualiza config.json
4. Workflow `blank.yml` ejecuta HISTORICO.py
5. Datos actualizados se commitean automáticamente

### Ejemplo 3: Ver datos procesados

```python
import pandas as pd

# Leer el archivo generado
df = pd.read_excel("Historico.xlsx")

# Ver últimos 5 años
print(df.tail())

# Filtrar categorías de alto riesgo
alto_riesgo = df[df["Homicidios_cat"] == "MUY ALTO ⚠"]
print(alto_riesgo)
```

## 🛠️ Mantenimiento

### Agregar un nuevo indicador

1. Buscar el indicador en la [API del Banco Mundial](https://data.worldbank.org/)
2. Agregar al diccionario `urls` en HISTORICO.py:
```python
urls = {
    # ... indicadores existentes ...
    "Nuevo_Indicador": "https://api.worldbank.org/v2/en/indicator/CODIGO?downloadformat=excel"
}
```

3. Agregar reglas de categorización:
```python
if "Nuevo_Indicador" in Datos_Fecha.columns:
    condiciones = [...]
    valores = ["BAJO ⭣", "MEDIO ⭤", "ALTO ⭡", "MUY ALTO ⚠"]
    categorizar_npselect(Datos_Fecha, "Nuevo_Indicador", condiciones, valores)
```

### Modificar umbrales de categorización

Editar las condiciones en la sección 8️⃣ de HISTORICO.py:
```python
# Ejemplo: Cambiar umbrales de homicidios
condiciones = [
    Datos_Fecha["Homicidios"] < 3,     # Antes: < 5
    (Datos_Fecha["Homicidios"] >= 3) & (Datos_Fecha["Homicidios"] <= 10),  # Antes: 5-15
    ...
]
```

### Cambiar frecuencia de ejecución

Editar `.github/workflows/blank.yml`:
```yaml
schedule:
  - cron: '*/5 * * * *'  # Cada 5 minutos
  # - cron: '0 * * * *'  # Cada hora
  # - cron: '0 0 * * *'  # Cada día a medianoche
```

## 🐛 Solución de Problemas

### Error: "No se encontró el país"

**Causa:** El nombre del país no coincide con la base de datos del Banco Mundial.

**Solución:** Usar nombre en inglés o variante reconocida:
```json
❌ "España" → ✅ "Spain"
❌ "Egipto" → ✅ "Egypt"
❌ "Estados Unidos" → ✅ "United States"
```

### Error: "Fallo en la lectura del Excel"

**Causa:** Problema de conectividad con la API del Banco Mundial.

**Solución:**
1. Verificar conexión a internet
2. Reintentar después de unos minutos
3. Verificar que la URL del indicador sea válida

### Columnas vacías en el resultado

**Causa:** El país no tiene datos disponibles para ese indicador.

**Comportamiento:** El script continúa con los demás indicadores.

## 📚 Referencias

- [API del Banco Mundial](https://data.worldbank.org/)
- [Worldwide Governance Indicators](https://www.worldbank.org/en/publication/worldwide-governance-indicators)
- [Documentación de pandas](https://pandas.pydata.org/docs/)
- [GitHub Actions](https://docs.github.com/en/actions)

## 📊 Estadísticas del Proyecto

- **Indicadores procesados:** 21+
- **Fuentes de datos:** API del Banco Mundial
- **Frecuencia de actualización:** Cada 5 minutos
- **Datos históricos:** Últimos 10 años
- **Automatización:** 100% (GitHub Actions)
- **Categorías de análisis:** 6 áreas principales

## 🤝 Contribución

Para contribuir al proyecto:
1. Hacer fork del repositorio
2. Crear una rama con tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📧 Contacto y Soporte

Para preguntas, sugerencias o reportar problemas:
- Crear un [Issue](https://github.com/tu-usuario/SGA/issues) en GitHub
- Consultar la documentación técnica en `/docs`

---

**Última actualización:** 2024
**Versión:** 1.0
**Mantenedor:** Sistema automatizado SGA