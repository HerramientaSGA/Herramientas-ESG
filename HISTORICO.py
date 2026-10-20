import json
import time
import unicodedata
import urllib.request

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------
# Configuración
# ----------------------------------------------------------------------
API = "https://api.worldbank.org/v2"
ANIO_INICIO_DESCARGA = 2000
ANIOS_A_CONSERVAR = 10

# "calculado": percentil 0-100 calculado con la serie GOV_WGI_*.EST de todos los países
#              (mantiene la definición y los umbrales de la especificación).
# "puntuacion": usa la nueva "puntuación 0-100" (GOV_WGI_*.SC). Cambia la definición.
MODO_PERCENTIL = "calculado"

# Columna de Historico.xlsx -> código del Banco Mundial
INDICADORES = {
    "Pobreza_Multidimennsional_Porcentual": "SI.POV.MDIM",
    "Poblacion_Destino": "SP.POP.TOTL",
    "Crecimiento_Poblacional": "SP.POP.GROW",
    "Pobreza_Poblacion_Porcentual": "SI.POV.DDAY",
    "Pobreza_Multidimensional_Porcentual": "SI.POV.MPWB",
    "Porcentaje_Edad_Laboral": "SP.POP.1564.TO.ZS",
    "Porcentaje_Edad_Laboral_Estudios": "SE.SEC.CUAT.UP.ZS",
    "Tasa_Desempleo": "SL.UEM.TOTL.NE.ZS",
    "Cantidad_Turistas_Año": "ST.INT.ARVL",
    "Tasa_Participacion_Fuerza_Laboral": "SL.TLF.CACT.NE.ZS",
    "Inseguridad_Alimentaria": "SN.ITK.MSFI.ZS",
    "Efectividad_Gubernamental": "GOV_WGI_GE.EST",
    "Control_Corrupcion": "GOV_WGI_CC.EST",
    "Rendicion_Cuentas": "GOV_WGI_VA.EST",
    "Estado_Derecho": "GOV_WGI_RL.EST",
    "Homicidios": "VC.IHR.PSRC.P5",
    "IPC": "FP.CPI.TOTL.ZG",
    "Acceso_Agua_Potable": "SH.H2O.BASW.ZS",
    "Acceso_Saneamiento": "SH.STA.BASS.ZS",
    "Poblacion_Urbana": "EN.POP.SLUM.UR.ZS",
}
# Percentiles (0-100) que el Banco Mundial ya no publica como tales
PERCENTILES = {
    "Estabilidad_Politica": ("GOV_WGI_PV.EST", "GOV_WGI_PV.SC"),
    "Calidad_Regulatoria": ("GOV_WGI_RQ.EST", "GOV_WGI_RQ.SC"),
}

# Orden exacto de las columnas que espera Power BI
COLUMNAS_DATOS = [
    "año", "Poblacion_Destino", "Pobreza_Multidimennsional_Porcentual", "Crecimiento_Poblacional",
    "Pobreza_Poblacion_Porcentual", "Pobreza_Multidimensional_Porcentual", "Porcentaje_Edad_Laboral",
    "Porcentaje_Edad_Laboral_Estudios", "Tasa_Desempleo", "Cantidad_Turistas_Año",
    "Tasa_Participacion_Fuerza_Laboral", "Inseguridad_Alimentaria", "Estabilidad_Politica",
    "Efectividad_Gubernamental", "Control_Corrupcion", "Rendicion_Cuentas", "Estado_Derecho",
    "Calidad_Regulatoria", "Homicidios", "IPC", "Acceso_Agua_Potable", "Acceso_Saneamiento",
    "Poblacion_Urbana", "ratio_turistas_residentes",
]
COLUMNAS_CAT = [
    "Control_Corrupcion_cat", "Estado_Derecho_cat", "Efectividad_Gubernamental_cat",
    "Rendicion_Cuentas_cat", "Estabilidad_Politica_cat", "Calidad_Regulatoria_cat", "Homicidios_cat",
    "Crecimiento_Poblacional_cat", "IPC_cat", "Pobreza_Poblacion_Porcentual_cat",
    "Pobreza_Multidimennsional_Porcentual_cat", "Porcentaje_Edad_Laboral_cat",
    "Porcentaje_Edad_Laboral_Estudios_cat", "Tasa_Desempleo_cat", "ratio_turistas_residentes_cat",
    "Acceso_Agua_Potable_cat", "Acceso_Saneamiento_cat", "Inseguridad_Alimentaria_cat",
    "Poblacion_Urbana_cat",
]

# Nombres alternativos frecuentes -> código ISO3
ALIAS = {
    "united republic of tanzania": "TZA", "tanzania, united republic of": "TZA",
    "usa": "USA", "us": "USA", "u.s.": "USA", "united states of america": "USA", "america": "USA",
    "uk": "GBR", "u.k.": "GBR", "great britain": "GBR", "britain": "GBR", "england": "GBR",
    "united kingdom of great britain and northern ireland": "GBR",
    "russia": "RUS", "south korea": "KOR", "republic of korea": "KOR", "korea": "KOR",
    "north korea": "PRK", "iran": "IRN", "egypt": "EGY", "vietnam": "VNM", "viet nam": "VNM",
    "turkey": "TUR", "turkiye": "TUR", "czech republic": "CZE", "czechia": "CZE",
    "ivory coast": "CIV", "cote d'ivoire": "CIV", "cape verde": "CPV", "cabo verde": "CPV",
    "laos": "LAO", "syria": "SYR", "venezuela": "VEN", "yemen": "YEM", "gambia": "GMB",
    "the gambia": "GMB", "bahamas": "BHS", "the bahamas": "BHS", "macedonia": "MKD",
    "north macedonia": "MKD", "slovakia": "SVK", "kyrgyzstan": "KGZ",
    "democratic republic of the congo": "COD", "dr congo": "COD", "drc": "COD",
    "republic of the congo": "COG", "congo-brazzaville": "COG", "micronesia": "FSM",
    "saint lucia": "LCA", "st lucia": "LCA", "st. lucia": "LCA", "brunei": "BRN",
    "hong kong": "HKG", "macau": "MAC", "macao": "MAC", "palestine": "PSE",
}

ETQ = {"B": "BAJO ⭣", "M": "MEDIO ⭤", "A": "ALTO ⭡", "MA": "MUY ALTO ⚠"}


# ----------------------------------------------------------------------
# Región del país (siete opciones de la especificación VF_INDICADORES)
# ----------------------------------------------------------------------
# África · América del Norte · América Latina y el Caribe · Asia · Europa · Medio Oriente · Oceanía
# Se obtiene del código ISO3 con la clasificación de regiones de la ONU (M49). «Medio Oriente» es
# Asia occidental en M49 (incluye Turquía, Chipre, Georgia, Armenia y Azerbaiyán); Irán queda en
# Asia (Asia meridional) y Egipto en África (África septentrional).
# Para mover un país de región sin tocar la tabla: AJUSTES_REGION = {"IRN": "Medio Oriente"}
REGIONES_VALIDAS = ["África", "América del Norte", "América Latina y el Caribe", "Asia", "Europa", "Medio Oriente", "Oceanía"]
COLUMNA_REGION = "Region"
AJUSTES_REGION = {}
REGIONES = {
    "África": (
        "AGO BDI BEN BFA BWA CAF CIV CMR COD COG COM CPV DJI DZA EGY ERI ETH GAB GHA GIN GMB GNB "
        "GNQ KEN LBR LBY LSO MAR MDG MLI MOZ MRT MUS MWI NAM NER NGA RWA SDN SEN SLE SOM SSD STP "
        "SWZ SYC TCD TGO TUN TZA UGA ZAF ZMB ZWE"
    ),
    "América del Norte": (
        "BMU CAN GRL USA"
    ),
    "América Latina y el Caribe": (
        "ABW ARG ATG BHS BLZ BOL BRA BRB CHL COL CRI CUB CUW CYM DMA DOM ECU GRD GTM GUY HND HTI "
        "JAM KNA LCA MAF MEX NIC PAN PER PRI PRY SLV SUR SXM TCA TTO URY VCT VEN VGB VIR"
    ),
    "Asia": (
        "AFG BGD BRN BTN CHN HKG IDN IND IRN JPN KAZ KGZ KHM KOR LAO LKA MAC MDV MMR MNG MYS NPL "
        "PAK PHL PRK SGP THA TJK TKM TLS UZB VNM"
    ),
    "Europa": (
        "ALB AND AUT BEL BGR BIH BLR CHE CHI CZE DEU DNK ESP EST FIN FRA FRO GBR GIB GRC HRV HUN "
        "IMN IRL ISL ITA LIE LTU LUX LVA MCO MDA MKD MLT MNE NLD NOR POL PRT ROU RUS SMR SRB SVK "
        "SVN SWE UKR XKX"
    ),
    "Medio Oriente": (
        "ARE ARM AZE BHR CYP GEO IRQ ISR JOR KWT LBN OMN PSE QAT SAU SYR TUR YEM"
    ),
    "Oceanía": (
        "ASM AUS FJI FSM GUM KIR MHL MNP NCL NRU NZL PLW PNG PYF SLB TON TUV VUT WSM"
    ),
}
REGION_DE_PAIS = {iso: region for region, codigos in REGIONES.items() for iso in codigos.split()}


def region_de(iso3):
    """Región (una de las siete de la especificación) del país; cadena vacía si no se conoce."""
    return AJUSTES_REGION.get(iso3) or REGION_DE_PAIS.get(iso3, "")


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------
def normalizar(texto):
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii")
    t = " ".join(t.lower().replace("_x002e_", ".").split())
    return t[4:] if t.startswith("the ") else t


def get_json(url, intentos=4):
    for i in range(intentos):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # red o servicio momentáneamente no disponible
            if i == intentos - 1:
                raise RuntimeError(f"No se pudo descargar {url}: {e}")
            time.sleep(5 * (i + 1))


def serie_api(url):
    """Devuelve la lista completa de registros de la API (gestiona la paginación)."""
    datos, pagina = [], 1
    while True:
        resp = get_json(f"{url}&page={pagina}")
        if not isinstance(resp, list) or len(resp) < 2:
            msg = resp[0].get("message") if isinstance(resp, list) and resp else resp
            raise RuntimeError(f"Respuesta no válida del Banco Mundial para {url}: {msg}")
        datos += resp[1] or []
        if pagina >= int(resp[0].get("pages", 1)):
            return datos
        pagina += 1


# ----------------------------------------------------------------------
# 1. País desde config.json
# ----------------------------------------------------------------------
def leer_pais(ruta="config.json"):
    with open(ruta, "r", encoding="utf-8") as f:
        config = json.load(f)
    if isinstance(config, list):
        if not config:
            raise ValueError("config.json no contiene ninguna respuesta.")
        fila = config[-1]                                       # la respuesta más reciente
    else:
        fila = config
    if not isinstance(fila, dict) or not fila:
        raise ValueError("config.json no contiene ninguna respuesta.")
    if "Indique el país (En inglés)" in fila:
        clave = "Indique el país (En inglés)"
    else:
        candidatas = [k for k in fila if "pais" in normalizar(k)]
        if not candidatas:
            raise ValueError("No se encuentra en config.json la pregunta del país.")
        clave = candidatas[0]
    valor = str(fila.get(clave) or "").strip()
    if not valor:
        raise ValueError("La pregunta del país está vacía en config.json.")
    return valor


# ----------------------------------------------------------------------
# 2. País -> código ISO3 del Banco Mundial
# ----------------------------------------------------------------------
def paises_banco_mundial():
    filas = serie_api(f"{API}/country?format=json&per_page=400")
    return {p["id"]: p["name"] for p in filas if p["region"]["value"] != "Aggregates"}


def resolver_pais(nombre, paises):
    n = normalizar(nombre).strip(" .")
    if n.upper() in paises:                                   # escrito como código ISO3
        return n.upper()
    formas = {}
    for iso, nom in paises.items():
        for f in {normalizar(nom), normalizar(nom.split(",")[0])}:
            formas.setdefault(f, set()).add(iso)
    if n in formas and len(formas[n]) == 1:                   # nombre exacto
        return next(iter(formas[n]))
    if n in ALIAS and ALIAS[n] in paises:                     # nombre alternativo
        return ALIAS[n]
    palabras = [iso for f, isos in formas.items() for iso in isos
                if f.startswith(n + " ") or f == n]
    if len(set(palabras)) == 1:                               # único comienzo coincidente
        return palabras[0]
    raise ValueError(
        f"No se reconoce el país «{nombre}». Escríbalo en inglés tal como lo nombra el Banco "
        f"Mundial (por ejemplo, Tanzania, Spain, Mexico) o añada la variante a ALIAS.")


# ----------------------------------------------------------------------
# 3. Descarga de datos
# ----------------------------------------------------------------------
def descargar(iso3, codigo, anio_fin):
    filas = serie_api(f"{API}/country/{iso3}/indicator/{codigo}?format=json&per_page=200"
                      f"&date={ANIO_INICIO_DESCARGA}:{anio_fin}")
    return {int(r["date"]): r["value"] for r in filas if r["value"] is not None}


def percentil_calculado(iso3, codigo_est, anio_fin, paises):
    filas = serie_api(f"{API}/country/all/indicator/{codigo_est}?format=json&per_page=20000"
                      f"&date={ANIO_INICIO_DESCARGA}:{anio_fin}")
    df = pd.DataFrame([(r["countryiso3code"], int(r["date"]), r["value"]) for r in filas
                       if r["value"] is not None and r["countryiso3code"] in paises],
                      columns=["iso", "año", "valor"])
    resultado = {}
    for anio, g in df.groupby("año"):
        g = g.set_index("iso")["valor"]
        if iso3 in g.index and len(g) > 1:
            resultado[anio] = round(float((g < g[iso3]).sum()) / (len(g) - 1) * 100, 2)
    return resultado


# ----------------------------------------------------------------------
# 4. Categorización (etiquetas BAJO / MEDIO / ALTO / MUY ALTO; umbrales de la especificación VF_INDICADORES)
# ----------------------------------------------------------------------
def categorizar(df):
    def sel(col, condiciones, valores):
        df[f"{col}_cat"] = np.select(condiciones, valores, default=None).astype(object)

    for col in ["Control_Corrupcion", "Estado_Derecho", "Efectividad_Gubernamental", "Rendicion_Cuentas"]:
        x = df[col]
        sel(col, [x >= 1.0, (x >= 0.0) & (x < 1.0), (x >= -1.0) & (x <= -0.01), x < -1.0],
            [ETQ["B"], ETQ["M"], ETQ["A"], ETQ["MA"]])
    for col in ["Estabilidad_Politica", "Calidad_Regulatoria"]:
        x = df[col]
        sel(col, [x >= 75, (x >= 50) & (x < 75), (x >= 25) & (x <= 49), x < 25],
            [ETQ["B"], ETQ["M"], ETQ["A"], ETQ["MA"]])
    x = df["Homicidios"]
    sel("Homicidios", [x < 5, (x >= 5) & (x <= 15), (x > 15) & (x <= 30), x > 30],
        [ETQ["B"], ETQ["M"], ETQ["A"], ETQ["MA"]])
    x = df["Crecimiento_Poblacional"]
    sel("Crecimiento_Poblacional", [x < 0, (x >= 0) & (x <= 1), (x > 1) & (x <= 2), x > 2],
        [ETQ["A"], ETQ["M"], ETQ["B"], ETQ["A"]])
    df["IPC_cat"] = pd.cut(df["IPC"], bins=[-np.inf, 3, 15, np.inf],
                           labels=[ETQ["B"], ETQ["M"], ETQ["A"]], right=False).astype(object)
    tramos = {
        "Pobreza_Poblacion_Porcentual": [(0, 10), (10, 50), (50, np.inf)],
        "Pobreza_Multidimennsional_Porcentual": [(0, 10), (10, 30), (30, np.inf)],
        "ratio_turistas_residentes": [(0, 100), (100, 300), (300, np.inf)],
        "Acceso_Agua_Potable": [(90, np.inf), (60, 90), (0, 60)],
        "Acceso_Saneamiento": [(90, np.inf), (60, 90), (0, 60)],
        "Inseguridad_Alimentaria": [(0, 10), (10, 25), (25, np.inf)],
        "Poblacion_Urbana": [(0, 10), (10, 30), (30, np.inf)],
    }
    for col, rangos in tramos.items():
        sel(col, [(df[col] >= lo) & (df[col] < hi) for lo, hi in rangos],
            [ETQ["B"], ETQ["M"], ETQ["A"]])
    # % de población en edad laboral: <55 % ALTO (envejecida) · 55-70 % MEDIO (equilibrada) · >70 % ALTO (presión laboral)
    x = df["Porcentaje_Edad_Laboral"]
    sel("Porcentaje_Edad_Laboral", [x < 55, (x >= 55) & (x <= 70), x > 70], [ETQ["A"], ETQ["M"], ETQ["A"]])
    # Tasa de desempleo: <6 % BAJO · 6-10 % MEDIO · >10 % ALTO
    x = df["Tasa_Desempleo"]
    sel("Tasa_Desempleo", [x < 6, (x >= 6) & (x <= 10), x > 10], [ETQ["B"], ETQ["M"], ETQ["A"]])
    # Población en edad laboral con educación secundaria o superior: ≥60 % BAJO · 30-59 % MEDIO · <30 % ALTO
    x = df["Porcentaje_Edad_Laboral_Estudios"]
    sel("Porcentaje_Edad_Laboral_Estudios", [x >= 60, (x >= 30) & (x < 60), x < 30], [ETQ["B"], ETQ["M"], ETQ["A"]])
    df.replace({"nan": None}, inplace=True)
    return df


# ----------------------------------------------------------------------
# 5. Validación antes de guardar
# ----------------------------------------------------------------------
RANGOS = {
    "Estabilidad_Politica": (0, 100), "Calidad_Regulatoria": (0, 100),
    "Control_Corrupcion": (-3, 3), "Estado_Derecho": (-3, 3),
    "Efectividad_Gubernamental": (-3, 3), "Rendicion_Cuentas": (-3, 3),
    "Pobreza_Poblacion_Porcentual": (0, 100), "Pobreza_Multidimennsional_Porcentual": (0, 100),
    "Pobreza_Multidimensional_Porcentual": (0, 100), "Porcentaje_Edad_Laboral": (0, 100),
    "Porcentaje_Edad_Laboral_Estudios": (0, 100), "Tasa_Desempleo": (0, 100),
    "Tasa_Participacion_Fuerza_Laboral": (0, 100), "Inseguridad_Alimentaria": (0, 100),
    "Acceso_Agua_Potable": (0, 100), "Acceso_Saneamiento": (0, 100), "Poblacion_Urbana": (0, 100),
    "Crecimiento_Poblacional": (-25, 25), "Homicidios": (0, 300), "Poblacion_Destino": (1, 2e9),
    "Cantidad_Turistas_Año": (0, 2e9),
}


def validar(df):
    errores = []
    if list(df.columns) != COLUMNAS_DATOS + COLUMNAS_CAT + [COLUMNA_REGION]:
        errores.append("las columnas no coinciden con las que espera Power BI")
    regiones_raras = set(df[COLUMNA_REGION].dropna().unique()) - set(REGIONES_VALIDAS) - {""}
    if regiones_raras:
        errores.append(f"región no válida: {sorted(regiones_raras)}")
    if df["Poblacion_Destino"].notna().sum() == 0:
        errores.append("no hay datos de población: el país no tiene datos en el Banco Mundial")
    for col, (lo, hi) in RANGOS.items():
        fuera = df[(df[col].notna()) & ((df[col] < lo) | (df[col] > hi))]
        if len(fuera):
            errores.append(f"{col} fuera de rango [{lo}, {hi}] en {list(fuera['año'])}: "
                           f"{list(fuera[col].round(2))}")
    if errores:
        raise ValueError("Datos no válidos; NO se guarda Historico.xlsx:\n  - " + "\n  - ".join(errores))


# ----------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------
def main():
    nombre = leer_pais()
    paises = paises_banco_mundial()
    iso3 = resolver_pais(nombre, paises)
    print(f"País en config.json: «{nombre}» -> {iso3} ({paises[iso3]})")
    region = region_de(iso3)
    print(f"Región: {region or '(no se conoce; la columna Region queda vacía)'}")

    anio_fin = pd.Timestamp.today().year
    series = {}
    for col, codigo in INDICADORES.items():
        series[col] = descargar(iso3, codigo, anio_fin)
        print(f"  {col:40} {codigo:20} años con dato: {len(series[col])}")
    for col, (cod_est, cod_sc) in PERCENTILES.items():
        if MODO_PERCENTIL == "calculado":
            series[col] = percentil_calculado(iso3, cod_est, anio_fin, paises)
        else:
            series[col] = descargar(iso3, cod_sc, anio_fin)
        print(f"  {col:40} {MODO_PERCENTIL + ' (' + cod_est + ')':20} años con dato: {len(series[col])}")

    anios_con_dato = sorted({a for s in series.values() for a in s})
    if not anios_con_dato:
        raise ValueError("El Banco Mundial no devuelve ningún dato para este país.")
    ultimo = anios_con_dato[-1]
    anios = list(range(ultimo - ANIOS_A_CONSERVAR + 1, ultimo + 1))

    df = pd.DataFrame({"año": anios})
    for col in COLUMNAS_DATOS[1:-1]:
        df[col] = [series[col].get(a, np.nan) for a in anios]
    df["ratio_turistas_residentes"] = df["Cantidad_Turistas_Año"] / df["Poblacion_Destino"] * 100
    df = categorizar(df)
    df[COLUMNA_REGION] = region
    df = df[COLUMNAS_DATOS + COLUMNAS_CAT + [COLUMNA_REGION]]

    validar(df)
    df.to_excel("Historico.xlsx", index=False)   # hoja "Sheet1", como espera Power BI
    print(f"\nHistorico.xlsx guardado: {iso3} ({region}), años {anios[0]}-{anios[-1]}, {len(df.columns)} columnas.")


if __name__ == "__main__":
    main()
