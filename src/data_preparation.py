"""
Módulo de Preparación y Transformación de Datos para StreamView Analytics
Destino: Modelado dimensional y analítico para Tableau
"""

import pandas as pd
import numpy as np
from pathlib import Path


TAXONOMY_MAP = {
    'Action & Adventure': ['Action', 'Adventure'],
    'Sci-Fi & Fantasy': ['Science Fiction', 'Fantasy'],
    'War & Politics': ['War', 'Politics']
}


def parse_and_harmonize_genres(genre_str):
    """Limpia y armoniza la taxonomía de géneros entre películas y series."""
    if pd.isna(genre_str) or not str(genre_str).strip():
        return []
    cleaned = str(genre_str).replace('[', '').replace(']', '').replace("'", '').replace('"', '')
    raw_list = [g.strip() for g in cleaned.split(',') if g.strip()]
    harmonized = []
    for g in raw_list:
        if g in TAXONOMY_MAP:
            harmonized.extend(TAXONOMY_MAP[g])
        elif g.lower() == 'unknown':
            continue
        else:
            harmonized.append(g)
    
    # Conservar orden preservando unicidad dentro del mismo título
    seen = set()
    result = []
    for g in harmonized:
        if g not in seen:
            seen.add(g)
            result.append(g)
    return result


def calculate_bayesian_weighted_rating(df, percentile=0.70):
    """
    Calcula la calificación ponderada bayesiana (Weighted Rating / IMDB formula)
    WR = (v / (v + m)) * R + (m / (v + m)) * C
    Donde:
      v = vote_count
      R = vote_average
      m = umbral mínimo de votos (percentil 70 de títulos con votos > 0)
      C = media global de vote_average para títulos con votos > 0
    """
    voters = df[df['vote_count'] > 0]
    C = voters['vote_average'].mean()
    m = voters['vote_count'].quantile(percentile)
    
    v = df['vote_count']
    R = df['vote_average']
    
    # Calcular solo cuando vote_count > 0; si es 0, dejar NA para excluir de agregaciones
    weighted = np.where(
        v > 0,
        (v / (v + m)) * R + (m / (v + m)) * C,
        np.nan
    )
    return pd.Series(weighted, index=df.index).round(2), round(C, 2), round(m, 1)


def limpiar_fuente(df_raw, fuente):
    """Aplica la limpieza inicial y estandarización a un dataset fuente."""
    df = df_raw.copy()
    
    # Estandarización de nombres de columnas
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(' ', '_', regex=False)
    )
    
    # Limpieza de textos vacíos
    columnas_texto = df.select_dtypes(include=['object', 'string']).columns
    for columna in columnas_texto:
        df[columna] = df[columna].astype('string').str.strip()
        df[columna] = df[columna].replace({'': pd.NA, 'nan': pd.NA, 'None': pd.NA})
        
    # Conversión de tipos
    if 'date_added' in df.columns:
        df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
        
    columnas_numericas = ['show_id', 'release_year', 'popularity', 'vote_count', 'vote_average']
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    # Creación de clave primaria compuesta para evitar colisiones de show_id
    df['content_key'] = fuente + '_' + df['show_id'].astype('Int64').astype(str)
    
    # Deduplicación por show_id dentro de la misma fuente
    df = df.drop_duplicates(subset='show_id', keep='first').reset_index(drop=True)
    return df


def procesar_pipeline(movies_path, tv_path, output_dir='data/processed'):
    """Ejecuta el pipeline completo y exporta los datasets para Tableau."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("1. Cargando fuentes de datos...")
    df_movies_raw = pd.read_csv(movies_path)
    df_tv_raw = pd.read_csv(tv_path)
    
    print("2. Limpiando y estandarizando catálogos...")
    df_movies = limpiar_fuente(df_movies_raw, 'movies')
    df_tv = limpiar_fuente(df_tv_raw, 'tv_shows')
    
    print("3. Concatenando catálogo unificado...")
    # Columnas que se deben conservar según la auditoría técnica
    columnas_conservadas = [
        'content_key', 'show_id', 'type', 'title', 'release_year',
        'date_added', 'country', 'language', 'genres',
        'popularity', 'vote_count', 'vote_average'
    ]
    
    df_catalogo = pd.concat(
        [df_movies[columnas_conservadas], df_tv[columnas_conservadas]],
        ignore_index=True,
        sort=False
    )
    
    print("4. Feature Engineering y enriquecimiento dimensional...")
    # Extracción de país primario para mapeo nativo en Tableau
    df_catalogo['primary_country'] = (
        df_catalogo['country']
        .dropna()
        .str.split(',')
        .str[0]
        .str.strip()
    )
    df_catalogo['primary_country'] = df_catalogo['primary_country'].fillna('Unknown')
    
    # Enriquecimiento temporal
    df_catalogo['year_added'] = df_catalogo['date_added'].dt.year.astype('Int64')
    df_catalogo['month_added'] = df_catalogo['date_added'].dt.month.astype('Int64')
    
    # Flags de calidad y votos
    df_catalogo['has_valid_votes'] = df_catalogo['vote_count'] > 0
    
    # Calificación ponderada bayesiana
    df_catalogo['weighted_rating'], C_val, m_val = calculate_bayesian_weighted_rating(df_catalogo)
    print(f"   -> Calificación bayesiana aplicada: Media global C={C_val}, Umbral m={m_val}")
    
    # Armonización de géneros
    df_catalogo['genres_list'] = df_catalogo['genres'].apply(parse_and_harmonize_genres)
    df_catalogo['genres_harmonized'] = df_catalogo['genres_list'].apply(lambda x: ', '.join(x) if x else 'Unknown')
    
    # Reordenar y formatear catálogo limpio a nivel título
    columnas_finales_catalogo = [
        'content_key', 'show_id', 'type', 'title', 'release_year',
        'date_added', 'year_added', 'month_added', 'country', 'primary_country',
        'language', 'popularity', 'vote_average', 'vote_count',
        'has_valid_votes', 'weighted_rating', 'genres_harmonized'
    ]
    df_catalog_clean = df_catalogo[columnas_finales_catalogo].copy()
    
    print("5. Generando tabla dimensional de géneros (Formato Long / Bridge)...")
    # Explode para relación 1-a-N en Tableau
    df_genres_bridge = (
        df_catalogo[['content_key', 'genres_list']]
        .explode('genres_list')
        .rename(columns={'genres_list': 'genre'})
    )
    df_genres_bridge['genre'] = df_genres_bridge['genre'].fillna('Unknown').replace('', 'Unknown')
    df_genres_bridge = df_genres_bridge.drop_duplicates().reset_index(drop=True)
    
    print("6. Generando tabla maestra denormalizada (Tableau Master)...")
    df_master = df_catalog_clean.merge(df_genres_bridge, on='content_key', how='left')
    
    print("7. Exportando datasets a disco...")
    catalog_file = output_path / 'streamview_catalog_clean.csv'
    genres_file = output_path / 'streamview_genres_bridge.csv'
    master_file = output_path / 'streamview_tableau_master.csv'
    
    df_catalog_clean.to_csv(catalog_file, index=False, encoding='utf-8')
    df_genres_bridge.to_csv(genres_file, index=False, encoding='utf-8')
    df_master.to_csv(master_file, index=False, encoding='utf-8')
    
    print(f"   [OK] Catálogo limpio: {catalog_file} ({len(df_catalog_clean):,} filas)")
    print(f"   [OK] Puente géneros:  {genres_file} ({len(df_genres_bridge):,} filas)")
    print(f"   [OK] Tableau Master:  {master_file} ({len(df_master):,} filas)")
    
    return df_catalog_clean, df_genres_bridge, df_master


if __name__ == '__main__':
    procesar_pipeline(
        movies_path='data/netflix_movies_detailed_up_to_2025.csv',
        tv_path='data/netflix_tv_shows_detailed_up_to_2025.csv',
        output_dir='data/processed'
    )

