import random
import uuid
import pandas as pd
from faker import Faker

random.seed(42)
Faker.seed(42)


SECTORES = ["Logistica", "Tecnologia", "Salud", "Educacion", "Agroindustria", "Comercio", "Manufactura", "Turismo"]
fake = Faker("es_CO")


def generar_datos(numero_filas):
    empresas = []
    for _ in range(numero_filas):
        empresas.append({
            "id": str(uuid.uuid4()),
            "nombre": fake.company(),
            "nit": fake.numerify("#########-#"),
            "sector": random.choice(SECTORES),
            "contacto": fake.name(),
            "correo": fake.company_email(),
            "telefono": fake.numerify("3#########"),
            "activa": random.choice([True, False]),
        })
    return empresas


def obtener_muestra(datos, porcentaje):
    return datos.sample(frac=porcentaje, random_state=random.randint(0, 9999)).index



def escribir_mal(texto):
    variantes = [texto.upper(), texto.lower(), f" {texto.lower()} ", f" {texto} "]
    return random.choice(variantes)



def convertir_booleano(valor):
    if valor:
        return random.choice(["SI", "1"])
    return random.choice(["No", "0"])



def formatear_nit(nit, con_puntos):
    digitos = nit.replace("-", "")
    if con_puntos:
        return f"{digitos[0:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9]}"
    return digitos



def formatear_telefono(telefono):
    formato = random.choice([0, 1, 2])
    if formato == 0:
        return telefono
    if formato == 1:
        return f"{telefono[0:3]} {telefono[3:6]} {telefono[6:]}"
    return f"+57 {telefono[0:3]}-{telefono[3:6]}-{telefono[6:]}"



def ensuciar(datos_df):
    datos_df = datos_df.copy()


    filas_con_puntos = set(obtener_muestra(datos_df, 0.5))
    datos_df["nit"] = [formatear_nit(nit, i in filas_con_puntos) for i, nit in zip(datos_df.index, datos_df["nit"])]


    nits = datos_df["nit"].to_dict()
    for fila in obtener_muestra(datos_df, 0.03):
        otra = random.choice([i for i in datos_df.index if i != fila])
        datos_df.loc[fila, "nit"] = nits[otra]


    filas_elegidas = obtener_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "nombre"] = " " + datos_df.loc[filas_elegidas, "nombre"] + " "

    filas_elegidas = obtener_muestra(datos_df, 0.15)
    datos_df.loc[filas_elegidas, "nombre"] = datos_df.loc[filas_elegidas, "nombre"].str.upper()


    datos_df["telefono"] = datos_df["telefono"].map(formatear_telefono)


    filas_elegidas = obtener_muestra(datos_df, 0.06)
    datos_df.loc[filas_elegidas, "correo"] = datos_df.loc[filas_elegidas, "correo"].str.replace("@", "", regex=False)


    filas_elegidas = obtener_muestra(datos_df, 0.30)
    datos_df.loc[filas_elegidas, "sector"] = datos_df.loc[filas_elegidas, "sector"].map(escribir_mal)


    datos_df["activa"] = datos_df["activa"].astype(object)
    filas_elegidas = obtener_muestra(datos_df, 0.20)
    datos_df.loc[filas_elegidas, "activa"] = datos_df.loc[filas_elegidas, "activa"].map(convertir_booleano)


    filas_elegidas = obtener_muestra(datos_df, 0.08)
    datos_df.loc[filas_elegidas, "contacto"] = None

    return datos_df


def generar_empresas(n=300):
    duplicados = round(n * 0.05)
    base = n - duplicados

    df = pd.DataFrame(generar_datos(base))
    df = ensuciar(df)

    copias = df.iloc[random.sample(range(base), duplicados)]
    df = pd.concat([df, copias], ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = generar_empresas()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())
