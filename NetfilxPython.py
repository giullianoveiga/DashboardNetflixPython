import streamlit as st
import pandas as pd
import plotly.express as px

# Definir o layout da página como wide
st.set_page_config(layout="wide")


# Função para carregar e processar os dados
@st.cache_data
def load_data():
    df = pd.read_csv('n_movies.csv')

    # Limpar a coluna 'year' e extrair apenas o primeiro ano numérico
    df['year'] = df['year'].str.extract(r'(\d{4})')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)

    # Manter apenas o primeiro gênero de cada linha
    df['genre'] = df['genre'].apply(lambda x: x.split(',')[0] if isinstance(x, str) else x)

    # Remover vírgulas da coluna de votos, substituir NaN por 0 e converter para numérico
    df['votes'] = df['votes'].str.replace(',', '').fillna(0).astype(int)

    # Converter a coluna 'duration' para numérico
    df['duration'] = df['duration'].str.extract(r'(\d+)').astype(float)

    return df


# Função para desenhar os gráficos com storytelling dinâmico
def draw_graphs(filtered_data, df):
    netflix_color = '#8c0005'
    red_shades = ['#8c0005', '#a10008', '#b5000a', '#cc000e', '#e50914', '#ff1b1c']

    # Gráfico dos 10 mais votados (barras empilhadas)
    top10_voted = filtered_data.nlargest(10, 'votes')
    fig1 = px.bar(top10_voted, x='title', y='votes', color='genre', title="🎥 **Top 10 Mais Votados**",
                  color_discrete_sequence=red_shades, barmode='stack')

    # Gráfico dos 10 títulos com melhores notas (barras empilhadas)
    top10_rated = filtered_data.nlargest(10, 'rating')
    fig2 = px.bar(top10_rated, x='title', y='rating', color='title', title=f"⭐ **Top 10 Títulos com Melhores Notas**",
                  color_discrete_sequence=red_shades, barmode='stack')

    # Gráfico dos 10 gêneros com mais títulos
    top10_genres = df['genre'].value_counts().nlargest(10).reset_index()
    top10_genres.columns = ['genre', 'count']
    fig3 = px.bar(top10_genres, x='genre', y='count', color='genre', title="🎬 **Top 10 Gêneros com Mais Títulos**",
                  color_discrete_sequence=px.colors.sequential.Reds)

    # Gráfico da Distribuição de Avaliações por Gênero
    fig4 = px.box(df, x='genre', y='rating', title="📊 **Distribuição de Avaliações por Gênero**",
                  color_discrete_sequence=[netflix_color])

    # Gráfico da Relação entre Votos e Avaliação
    fig5 = px.scatter(filtered_data, x='votes', y='rating', title="🔍 **Relação entre Votos e Avaliação**",
                      labels={'votes': 'Número de Votos', 'rating': 'Avaliação'},
                      hover_data=['title'], color_discrete_sequence=[netflix_color])

    # Gráfico da Popularidade dos Gêneros ao Longo do Tempo
    genre_popularity = df.groupby(['year', 'genre']).size().reset_index(name='count')
    fig6 = px.line(genre_popularity, x='year', y='count', color='genre',
                   title="📈 **Popularidade dos Gêneros ao Longo do Tempo**", color_discrete_sequence=red_shades)

    # Distribuir os gráficos em colunas (2 gráficos por linha)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1)
        st.write(
            f"📝 '{top10_voted.iloc[0]['title']}' lidera com {top10_voted.iloc[0]['votes']} votos.")

    with col2:
        st.plotly_chart(fig2)
        st.write(f"📝 '{top10_rated.iloc[0]['title']}' tem a maior avaliação com {top10_rated.iloc[0]['rating']}.")
    st.write("---")
    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(fig3)
        st.write(f"📝 '{top10_genres.iloc[0]['genre']}' lidera com {top10_genres.iloc[0]['count']} títulos.")

    with col4:
        st.plotly_chart(fig4)
        st.write(f"📝 '{df['genre'].mode()[0]}' tende a ter as avaliações mais altas.")
    st.write("---")
    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(fig5)
        st.write(f"📝 '{filtered_data.iloc[0]['title']}' se destaca com alta avaliação e votos.")

    with col6:
        st.plotly_chart(fig6)
        st.write(f"📝 '{genre_popularity.iloc[0]['genre']}' tem crescido desde {genre_popularity['year'].min()}.")


# Função para exibir os cartões com informações e storytelling
def draw_cards(movie_info, filtered_data):
    st.write("### Título Selecionado")

    # Ordenar os filmes por avaliação e encontrar a posição do filme selecionado
    all_ratings_sorted = filtered_data.sort_values(by='rating', ascending=False).reset_index()
    position_in_ranking = all_ratings_sorted[all_ratings_sorted['title'] == movie_info['title']].index[0] + 1

    cols = st.columns([2, 1, 1, 1])

    # Exibir as informações nos cartões de acordo com o filme selecionado
    cols[0].metric(label="🎬 Título", value=movie_info['title'])
    cols[1].metric(label="📅 Ano", value=str(movie_info['year']))
    cols[2].metric(label="🎭 Gênero", value=movie_info['genre'])
    cols[3].metric(label="⭐ Avaliação", value=str(movie_info['rating']))

    # Adicionar um layout com duas colunas para a descrição e a posição no ranking
    st.write("<div style='padding-top: 20px;'>", unsafe_allow_html=True)
    col_desc, col_position = st.columns([3, 1])

    with col_desc:
        st.write("### 📝 Descrição")
        st.write(movie_info['description'])

    with col_position:
        # Exibir o cartão de posição no ranking com padding de 50px
        st.markdown("<div style='padding-left: 50px;'>", unsafe_allow_html=True)
        st.metric(label="Posição no Ranking", value=f"🏆 {position_in_ranking}º")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")




# Função principal do dashboard
def main():
    st.markdown("""
        <style>
        .title {
            text-align: center;
            font-size: 3rem;
            color: #8c0005;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 class="title">Dashboard Netflix com Python</h1>', unsafe_allow_html=True)

    df = load_data()

    col1, col2 = st.columns([1, 4])

    with col1:
        st.image("netflix.png", width=200)
        st.markdown("<div style='padding-right: 20px;'>", unsafe_allow_html=True)

        genre_filter = st.selectbox("Filtrar por Gênero", options=df['genre'].unique())
        year_filter = st.slider("Filtrar por Ano", min_value=int(df['year'].min()), max_value=int(df['year'].max()),
                                value=(int(df['year'].min()), int(df['year'].max())))
        rating_filter = st.slider("Filtrar por Avaliação", min_value=float(df['rating'].min()), max_value=float(df['rating'].max()),
                                  value=(float(df['rating'].min()), float(df['rating'].max())))

        filtered_data = df[
            (df['genre'] == genre_filter) &
            (df['year'].between(year_filter[0], year_filter[1])) &
            (df['rating'].between(rating_filter[0], rating_filter[1]))
        ]

        movie_selected = st.selectbox("Selecione um Filme", options=filtered_data['title'].unique())
        movie_info = filtered_data[filtered_data['title'] == movie_selected].iloc[0]

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        draw_cards(movie_info, filtered_data)
        draw_graphs(filtered_data, df)


if __name__ == "__main__":
    main()
