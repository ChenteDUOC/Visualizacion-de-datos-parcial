"""
Generador de Visualizaciones y Gráficos para StreamView Analytics
Crea imágenes en alta resolución (PNG) en la carpeta images/ para el Informe Ejecutivo PDF y la entrega Duoc UC.
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Configuración estética global (Principios Gestalt y contraste)
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = 'Segoe UI', 'DejaVu Sans', 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

OUTPUT_DIR = Path('images')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Paleta corporativa de StreamView Analytics
COLOR_PRIMARY = '#1f77b4'   # Azul corporativo (Movies)
COLOR_SECONDARY = '#ff7f0e' # Coral / Naranja (TV Shows)
COLOR_NEUTRAL = '#2c3e50'
COLOR_BG_CARD = '#f8f9fa'

# Carga de datos procesados
df_catalog = pd.read_csv('data/processed/streamview_catalog_clean.csv')
df_genres = pd.read_csv('data/processed/streamview_genres_bridge.csv')
df_master = pd.read_csv('data/processed/streamview_tableau_master.csv')

df_catalog['date_added'] = pd.to_datetime(df_catalog['date_added'])


def generar_kpis_overview():
    """Genera una tarjeta visual de KPIs ejecutivos para la portada o cabecera."""
    fig, ax = plt.subplots(figsize=(14, 3.2), facecolor='white')
    ax.axis('off')
    
    kpis = [
        ("31,991", "TÍTULOS TOTALES", "Catálogo unificado global"),
        ("16,000", "PELÍCULAS (50.0%)", "Producciones cinematográficas"),
        ("15,991", "SERIES (50.0%)", "Temporadas y series"),
        ("6.63", "RATING PONDERADO", "Escala bayesiana (1 - 10)"),
        ("85.7%", "COBERTURA DE VOTOS", "27,431 títulos con reseñas")
    ]
    
    n = len(kpis)
    for i, (val, title, subtitle) in enumerate(kpis):
        x = (i + 0.5) / n
        # Tarjeta redondeada
        rect = plt.Rectangle((i/n + 0.02, 0.08), 1/n - 0.04, 0.84, 
                             facecolor=COLOR_BG_CARD, edgecolor='#e2e8f0', 
                             linewidth=1.5, transform=ax.transAxes, zorder=1)
        ax.add_patch(rect)
        
        ax.text(x, 0.65, val, ha='center', va='center', fontsize=22, fontweight='bold', 
                color=COLOR_PRIMARY if i != 1 and i != 2 else (COLOR_PRIMARY if i == 1 else COLOR_SECONDARY), 
                transform=ax.transAxes, zorder=2)
        ax.text(x, 0.38, title, ha='center', va='center', fontsize=10, fontweight='bold', 
                color=COLOR_NEUTRAL, transform=ax.transAxes, zorder=2)
        ax.text(x, 0.20, subtitle, ha='center', va='center', fontsize=8, 
                color='#64748b', transform=ax.transAxes, zorder=2)

    plt.title("STREAMVIEW ANALYTICS — INDICADORES CLAVE DEL CATÁLOGO GLOBAL (EP1)", 
              fontsize=13, fontweight='bold', pad=15, color=COLOR_NEUTRAL)
    plt.tight_layout()
    output_file = OUTPUT_DIR / '01_kpis_overview.png'
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"✅ Generado: {output_file}")


def generar_distribucion_generos():
    """Genera gráfico de barras horizontales de géneros coloreado por rating ponderado."""
    genre_stats = (
        df_master.groupby('genre')
        .agg(
            total_titles=('content_key', 'nunique'),
            avg_rating=('weighted_rating', 'mean')
        )
        .sort_values(by='total_titles', ascending=True)
    )
    
    # Excluir 'Unknown' para visualización principal
    genre_stats = genre_stats[genre_stats.index != 'Unknown']
    
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
    
    # Normalizar para colormap
    norm = plt.Normalize(genre_stats['avg_rating'].min(), genre_stats['avg_rating'].max())
    cmap = plt.cm.Blues
    colors = cmap(norm(genre_stats['avg_rating']))
    
    bars = ax.barh(genre_stats.index, genre_stats['total_titles'], color=colors, edgecolor='none', height=0.7)
    
    # Etiquetas de datos
    for bar, rating in zip(bars, genre_stats['avg_rating']):
        w = bar.get_width()
        ax.text(w + 120, bar.get_y() + bar.get_height()/2, 
                f"{w:,}  ({rating:.2f} ★)", 
                va='center', ha='left', fontsize=8.5, color='#334155')
        
    ax.set_xlim(0, genre_stats['total_titles'].max() * 1.18)
    ax.set_xlabel("Cantidad de Títulos Únicos", fontsize=10, fontweight='bold', labelpad=10)
    ax.set_title("Distribución de Contenido por Género y Calificación Media Ponderada\n(Longitud = Cantidad de Títulos | Color = Rating Bayesiano)", 
                 fontsize=12, fontweight='bold', pad=15, color=COLOR_NEUTRAL)
    
    # Barra de color
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.04, pad=0.1)
    cbar.set_label("Calificación Media Ponderada (Weighted Rating)", fontsize=8.5)
    
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    output_file = OUTPUT_DIR / '02_genres_distribution.png'
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"✅ Generado: {output_file}")


def generar_distribucion_geografica():
    """Genera gráfico de los principales países productores."""
    country_counts = (
        df_catalog[df_catalog['primary_country'] != 'Unknown']['primary_country']
        .value_counts()
        .head(15)
        .sort_values(ascending=True)
    )
    
    fig, ax = plt.subplots(figsize=(10, 6.5), facecolor='white')
    bars = ax.barh(country_counts.index, country_counts.values, color=COLOR_PRIMARY, height=0.65)
    
    for bar in bars:
        w = bar.get_width()
        pct = (w / len(df_catalog)) * 100
        ax.text(w + 100, bar.get_y() + bar.get_height()/2, 
                f"{w:,} ({pct:.1f}%)", 
                va='center', ha='left', fontsize=8.5, color='#334155')
        
    ax.set_xlim(0, country_counts.max() * 1.15)
    ax.set_xlabel("Cantidad de Títulos Producidos", fontsize=10, fontweight='bold')
    ax.set_title("Top 15 Países de Producción en el Catálogo de StreamView\n(Dimensión primary_country para Geocodificación en Tableau)", 
                 fontsize=12, fontweight='bold', pad=15, color=COLOR_NEUTRAL)
    
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    output_file = OUTPUT_DIR / '03_geographic_production.png'
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"✅ Generado: {output_file}")


def generar_evolucion_temporal():
    """Genera gráfico de líneas temporal de incorporaciones por mes."""
    df_temporal = (
        df_catalog.dropna(subset=['date_added'])
        .set_index('date_added')
        .groupby([pd.Grouper(freq='ME'), 'type'])['content_key']
        .nunique()
        .unstack(fill_value=0)
    )
    
    # Filtrar desde 2015 para evitar años dispersos y enfocar la narrativa
    df_temporal = df_temporal[df_temporal.index >= '2015-01-01']
    
    fig, ax = plt.subplots(figsize=(12, 5.5), facecolor='white')
    
    if 'Movie' in df_temporal.columns:
        ax.plot(df_temporal.index, df_temporal['Movie'], label='Películas (Movies)', 
                color=COLOR_PRIMARY, linewidth=2.2)
    if 'TV Show' in df_temporal.columns:
        ax.plot(df_temporal.index, df_temporal['TV Show'], label='Series (TV Shows)', 
                color=COLOR_SECONDARY, linewidth=2.2)
        
    ax.set_ylabel("Títulos Incorporados al Mes", fontsize=10, fontweight='bold')
    ax.set_xlabel("Fecha de Incorporación (date_added)", fontsize=10, fontweight='bold')
    ax.set_title("Evolución Mensual de Incorporación de Contenidos (2015 - 2025)\n(Eje Estratégico de Retención y Frescura de Catálogo)", 
                 fontsize=12, fontweight='bold', pad=15, color=COLOR_NEUTRAL)
    
    ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9.5)
    plt.tight_layout()
    output_file = OUTPUT_DIR / '04_temporal_evolution.png'
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"✅ Generado: {output_file}")


def generar_matriz_calidad_popularidad():
    """Genera gráfico de dispersión con 4 cuadrantes estratégicos."""
    df_sample = df_catalog[df_catalog['has_valid_votes']].sample(n=min(3000, len(df_catalog)), random_state=42)
    
    med_pop = df_sample['popularity'].median()
    mean_wr = df_sample['weighted_rating'].mean()
    
    fig, ax = plt.subplots(figsize=(10, 7), facecolor='white')
    
    # Puntos por tipo
    for t, col, marker in [('Movie', COLOR_PRIMARY, 'o'), ('TV Show', COLOR_SECONDARY, '^')]:
        sub = df_sample[df_sample['type'] == t]
        ax.scatter(sub['popularity'], sub['weighted_rating'], 
                   c=col, alpha=0.45, s=np.clip(sub['vote_count'] / 50, 15, 250), 
                   label=t, edgecolors='none')
        
    # Líneas de referencia para los 4 cuadrantes
    ax.axvline(med_pop, color='#94a3b8', linestyle='--', linewidth=1.2)
    ax.axhline(mean_wr, color='#94a3b8', linestyle='--', linewidth=1.2)
    
    # Cuadrantes anotados
    ax.text(med_pop * 0.15, 8.8, "💎 JOYAS OCULTAS\n(Alto Rating / Baja Tracción)", 
            fontsize=9, fontweight='bold', color='#0284c7', ha='center', bbox=dict(boxstyle='round,pad=0.4', facecolor='#e0f2fe', edgecolor='none'))
    ax.text(med_pop * 4.5, 8.8, "⭐ ÉXITOS COMERCIALES\n(Alto Rating / Alta Tracción)", 
            fontsize=9, fontweight='bold', color='#16a34a', ha='center', bbox=dict(boxstyle='round,pad=0.4', facecolor='#dcfce7', edgecolor='none'))
    ax.text(med_pop * 0.15, 5.0, "📦 CONTENIDO DE RELLENO\n(Bajo Rating / Baja Tracción)", 
            fontsize=9, fontweight='bold', color='#64748b', ha='center', bbox=dict(boxstyle='round,pad=0.4', facecolor='#f1f5f9', edgecolor='none'))
    ax.text(med_pop * 4.5, 5.0, "⚡ VIRALES POLÉMICOS\n(Bajo Rating / Alta Tracción)", 
            fontsize=9, fontweight='bold', color='#dc2626', ha='center', bbox=dict(boxstyle='round,pad=0.4', facecolor='#fee2e2', edgecolor='none'))
    
    ax.set_xscale('log')
    ax.set_xlabel("Popularidad (Escala Logarítmica)", fontsize=10, fontweight='bold')
    ax.set_ylabel("Calificación Ponderada Bayesiana (Weighted Rating)", fontsize=10, fontweight='bold')
    ax.set_title("Matriz de Calidad vs. Popularidad de Contenidos\n(Tamaño = Volumen de Votos | Filtro: has_valid_votes = True)", 
                 fontsize=12, fontweight='bold', pad=15, color=COLOR_NEUTRAL)
    
    ax.legend(frameon=True, facecolor='white', loc='lower right', fontsize=9.5)
    plt.tight_layout()
    output_file = OUTPUT_DIR / '05_quality_vs_popularity_scatter.png'
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"✅ Generado: {output_file}")


def generar_heatmap_genero_decada():
    """Genera heatmap de género por década."""
    df_master['decade'] = (df_master['release_year'] // 10 * 10).astype(str) + 's'
    
    # Filtrar décadas con volumen suficiente (desde 1980s)
    df_filtered = df_master[(df_master['release_year'] >= 1980) & (df_master['genre'] != 'Unknown')]
    
    pivot = df_filtered.pivot_table(
        index='genre', 
        columns='decade', 
        values='weighted_rating', 
        aggfunc='mean'
    )
    
    # Ordenar por cantidad total de títulos
    top_genres = df_filtered['genre'].value_counts().index
    pivot = pivot.loc[top_genres]
    
    fig, ax = plt.subplots(figsize=(11, 7.5), facecolor='white')
    sns.heatmap(pivot, cmap='YlGnBu', annot=True, fmt='.2f', linewidths=0.5, 
                cbar_kws={'label': 'Weighted Rating Promedio'}, ax=ax)
    
    ax.set_xlabel("Década de Lanzamiento Original", fontsize=10, fontweight='bold')
    ax.set_ylabel("Género Armonizado", fontsize=10, fontweight='bold')
    ax.set_title("Calificación Media Ponderada por Género a lo largo de las Décadas\n(Evaluación de Calidad Histórica por Categoría)", 
                 fontsize=12, fontweight='bold', pad=15, color=COLOR_NEUTRAL)
    
    plt.tight_layout()
    output_file = OUTPUT_DIR / '06_genre_by_year_heatmap.png'
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"✅ Generado: {output_file}")


def generar_diagrama_storytelling():
    """Genera un diagrama conceptual que ilustra la narrativa visual del Story."""
    fig, ax = plt.subplots(figsize=(13, 3.5), facecolor='white')
    ax.axis('off')
    
    steps = [
        ("1. Panorama Global", "31,991 títulos\n50% Películas / 50% Series\n85.7% con votos válidos", "#0284c7"),
        ("2. Qué se Produce", "Drama y Comedia dominan\nAnimación lidera en rating\nBrecha volumen vs calidad", "#3b82f6"),
        ("3. De Dónde Viene", "EE.UU. lidera (27.5%)\nJapón, China, Corea crecen\nGlobalización de series", "#6366f1"),
        ("4. Cuándo se Agrega", "Aceleración desde 2020\nPicos estacionales Q4\nEstrategia de retención", "#8b5cf6"),
        ("5. Recomendaciones", "Focalizar 'Joyas Ocultas'\nAdquisición con alta tracción\nOptimizar inversión", "#10b981")
    ]
    
    n = len(steps)
    for i, (title, desc, color) in enumerate(steps):
        x = (i + 0.5) / n
        rect = plt.Rectangle((i/n + 0.02, 0.1), 1/n - 0.04, 0.8, 
                             facecolor=color, edgecolor='none', 
                             transform=ax.transAxes, zorder=1, alpha=0.15)
        ax.add_patch(rect)
        
        # Borde superior coloreado
        top_bar = plt.Rectangle((i/n + 0.02, 0.85), 1/n - 0.04, 0.05, 
                                facecolor=color, edgecolor='none', 
                                transform=ax.transAxes, zorder=2)
        ax.add_patch(top_bar)
        
        ax.text(x, 0.68, title, ha='center', va='center', fontsize=11, fontweight='bold', 
                color=color, transform=ax.transAxes, zorder=3)
        ax.text(x, 0.38, desc, ha='center', va='center', fontsize=8.5, 
                color='#334155', transform=ax.transAxes, zorder=3, linespacing=1.4)
        
        # Flecha conectora
        if i < n - 1:
            ax.annotate('', xy=((i+1)/n + 0.015, 0.5), xytext=((i+1)/n - 0.015, 0.5),
                        xycoords='axes fraction',
                        arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=2))

    plt.title("NARRATIVA VISUAL (DATA STORYTELLING) — FLUJO SECUENCIAL DE 5 PUNTOS (IE10: 18%)", 
              fontsize=12, fontweight='bold', pad=15, color=COLOR_NEUTRAL)
    plt.tight_layout()
    output_file = OUTPUT_DIR / '07_storytelling_flow.png'
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f"✅ Generado: {output_file}")


def main():
    print("Iniciando generación de visualizaciones de alta resolución...")
    generar_kpis_overview()
    generar_distribucion_generos()
    generar_distribucion_geografica()
    generar_distribucion_geografica()
    generar_evolucion_temporal()
    generar_matriz_calidad_popularidad()
    generar_heatmap_genero_decada()
    generar_diagrama_storytelling()
    print("\n🎉 Todas las visualizaciones fueron generadas exitosamente en images/")


if __name__ == '__main__':
    main()
