
import random
import uuid
from pathlib import Path
from datetime import timedelta

import pandas as pd
from faker import Faker


# ==========================================
# 1. CONFIGURACIÓN
# ==========================================

fake = Faker("es_CO")

ESTADOS = [
    "pendiente",
    "en_curso",
    "completado",
    "cerrado",
]

# Listas fijas para las llaves foráneas.
IDS_EMPRESA = [
    str(uuid.uuid5(uuid.NAMESPACE_DNS, f"empresa-{i}"))
    for i in range(1, 6)
]

IDS_CATEGORIA = [
    str(uuid.uuid5(uuid.NAMESPACE_DNS, f"categoria-{i}"))
    for i in range(1, 5)
]

IDS_PRIORIDAD = [
    str(uuid.uuid5(uuid.NAMESPACE_DNS, f"prioridad-{i}"))
    for i in range(1, 4)
]


# ==========================================
# 2. GENERAR RETOS
# ==========================================

def generar_retos(n=500):
    """Genera n retos ficticios y devuelve un DataFrame."""

    Faker.seed(42)
    fake.seed_instance(42)
    random.seed(42)

    registros = []

    for _ in range(n):
        fecha_inicio = fake.date_between(
            start_date="-1y",
            end_date="+3m",
        )

        fecha_fin = fecha_inicio + timedelta(
            days=random.randint(15, 180)
        )

        registro = {
            "id": str(uuid.uuid4()),
            "nombre": fake.sentence(
                nb_words=6
            ).rstrip("."),
            "descripcion": fake.sentence(
                nb_words=12
            ),
            "fecha_inicio": fecha_inicio.strftime(
                "%Y-%m-%d"
            ),
            "fecha_fin": fecha_fin.strftime(
                "%Y-%m-%d"
            ),
            "estado": random.choice(ESTADOS),
            "id_empresa": random.choice(IDS_EMPRESA),
            "id_categoria": random.choice(IDS_CATEGORIA),
            "id_prioridad": random.choice(IDS_PRIORIDAD),
        }

        registros.append(registro)

    df = pd.DataFrame(registros)

    # ==========================================
    # 3. ENSUCIAR LOS DATOS
    # ==========================================

    # 10 % de nombres con espacios sobrantes.
    indices = random.sample(
        list(df.index), int(n * 0.10)
    )

    for i in indices:
        df.at[i, "nombre"] = (
            f"  {df.at[i, 'nombre']}   "
        )

    # 12 % de descripciones nulas.
    indices = random.sample(
        list(df.index), int(n * 0.12)
    )

    df.loc[indices, "descripcion"] = None

    # Mayúsculas y minúsculas mezcladas en nombres.
    indices = random.sample(
        list(df.index), int(n * 0.10)
    )

    for i in indices:
        if random.choice([True, False]):
            df.at[i, "nombre"] = (
                df.at[i, "nombre"].upper()
            )
        else:
            df.at[i, "nombre"] = (
                df.at[i, "nombre"].lower()
            )

    # Fechas de inicio en dos formatos diferentes.
    indices = random.sample(
        list(df.index), int(n * 0.10)
    )

    for i in indices:
        fecha = pd.to_datetime(
            df.at[i, "fecha_inicio"]
        )

        if random.choice([True, False]):
            df.at[i, "fecha_inicio"] = (
                fecha.strftime("%d/%m/%Y")
            )
        else:
            df.at[i, "fecha_inicio"] = (
                fecha.strftime("%Y-%m-%d")
            )

    # 8 % de fechas de fin nulas.
    indices_nulos = random.sample(
        list(df.index), int(n * 0.08)
    )

    df.loc[indices_nulos, "fecha_fin"] = None

    # 5 % de fechas de fin anteriores al inicio.
    disponibles = [
        i for i in df.index
        if i not in indices_nulos
    ]

    indices_incorrectos = random.sample(
        disponibles, int(n * 0.05)
    )

    for i in indices_incorrectos:
        inicio = pd.to_datetime(
            df.at[i, "fecha_inicio"],
            dayfirst="/" in df.at[i, "fecha_inicio"],
        )

        dias_antes = random.randint(1, 90)

        df.at[i, "fecha_fin"] = (
            inicio - timedelta(days=dias_antes)
        ).strftime("%Y-%m-%d")

    # Variantes inconsistentes del estado.
    variantes_estado = {
        "pendiente": ["pendiente", "PENDIENTE", " Pendiente "],
        "en_curso": ["en_curso", "EN CURSO", "en curso"],
        "completado": ["completado", "COMPLETADO", "Completado"],
        "cerrado": ["cerrado", "Cerrado ", "CERRADO"],
    }

    indices = random.sample(
        list(df.index), int(n * 0.10)
    )

    for i in indices:
        estado_original = df.at[i, "estado"]
        df.at[i, "estado"] = random.choice(
            variantes_estado[estado_original]
        )

    # 5 % de identificadores de empresa en mayúsculas.
    indices = random.sample(
        list(df.index), int(n * 0.05)
    )

    for i in indices:
        df.at[i, "id_empresa"] = (
            df.at[i, "id_empresa"].upper()
        )

    # ==========================================
    # 4. DUPLICADOS EXACTOS
    # ==========================================

    cantidad_duplicados = int(n * 0.05)

    duplicados = df.sample(
        n=cantidad_duplicados,
        random_state=42,
    )

    df = pd.concat(
        [df, duplicados],
        ignore_index=True,
    )

    return df


# ==========================================
# 5. EJECUCIÓN DIRECTA
# ==========================================

if __name__ == "__main__":
    df = generar_retos(n=500)

    print("Dimensiones del DataFrame:")
    print(df.shape)

    print("\nPrimeras filas:")
    print(df.head())

    print("\nValores nulos por columna:")
    print(df.isna().sum())

    # Exportar el CSV para la etapa de limpieza.
    raiz = Path(__file__).resolve().parent.parent
    carpeta_datos = raiz / "data"
    carpeta_datos.mkdir(parents=True, exist_ok=True)

    archivo = carpeta_datos / "retos_sucios.csv"

    df.to_csv(
        archivo,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\nCSV generado en: {archivo}")
