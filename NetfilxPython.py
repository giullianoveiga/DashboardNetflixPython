import streamlit as st
import pandas as pd
import plotly.express as px

# Definir o layout da página como wide
st.set_page_config(layout="wide", page_title="Dashboard Netflix")

st.markdown("""
    <style>
    body {
        background-color: #000000;
        color: #FFFFFF;
    }
    .stSelectbox, .stSlider {
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)


# Função para carregar e processar os dados
def load_data():
    # Carregar o arquivo CSV
    df = pd.read_csv(r'D:\IBRINK-PC-USER\Desktop\Dados\BaseDados\n_movies.csv')

    # Limpar a coluna 'year' e extrair apenas o primeiro ano numérico
    df['year'] = df['year'].str.extract(r'(\d{4})')

    # Remover quaisquer valores ausentes
    df = df.dropna(subset=['year'])

    # Converter a coluna 'year' para numérico
    df['year'] = df['year'].astype(int)

    # Manter apenas o primeiro gênero de cada linha
    df['genre'] = df['genre'].apply(lambda x: x.split(',')[0] if isinstance(x, str) else x)

    # Remover vírgulas da coluna de votos, substituir NaN por 0 e converter para numérico
    df['votes'] = df['votes'].str.replace(',', '').fillna(0).astype(int)

    # Converter a coluna 'duration' para numérico (extrair números antes de 'min')
    df['duration'] = df['duration'].str.extract(r'(\d+)').astype(float)

    return df


# Função para desenhar os gráficos com base na ordem selecionada
def draw_graphs(filtered_data, df):
    netflix_color = '#8c0005'
    red_shades = ['#8c0005', '#a10008', '#b5000a', '#cc000e', '#e50914', '#ff1b1c']

    # Gráfico dos 10 mais votados (barras empilhadas)
    top10_voted = filtered_data.nlargest(10, 'votes')
    fig1 = px.bar(top10_voted, x='title', y='votes', color='genre', title="Top 10 Títulos com Mais Votos",
                  color_discrete_sequence=red_shades, barmode='stack')

    # Gráfico dos 10 títulos com melhores notas (barras empilhadas)
    top10_rated = filtered_data.nlargest(10, 'rating')
    fig2 = px.bar(top10_rated, x='title', y='rating', color='title',
                  title="Top 10 Títulos com Melhores Notas",
                  color_discrete_sequence=red_shades, barmode='stack')

    # Gráfico estático dos 10 gêneros com mais títulos (usando o dataframe original)
    top10_genres = df['genre'].value_counts().nlargest(10).reset_index()
    top10_genres.columns = ['genre', 'count']
    fig3 = px.bar(top10_genres, x='genre', y='count', color='genre', title="Top 10 Gêneros com Mais Títulos",
                  color_discrete_sequence=px.colors.sequential.Reds)

    # Gráfico estático da Distribuição de Avaliações por Gênero
    fig4 = px.box(df, x='genre', y='rating', title="Distribuição de Avaliações por Gênero",
                  color_discrete_sequence=[netflix_color])

    # Gráfico da Relação entre Votos e Avaliação
    fig5 = px.scatter(filtered_data, x='votes', y='rating', title="Relação entre Número de Votos e Avaliação",
                      labels={'votes': 'Número de Votos', 'rating': 'Avaliação'},
                      hover_data=['title'], color_discrete_sequence=[netflix_color])

    # Gráfico dinâmico da Popularidade dos Gêneros ao Longo do Tempo (usando o dataframe original)
    genre_popularity = df.groupby(['year', 'genre']).size().reset_index(name='count')
    fig6 = px.line(genre_popularity, x='year', y='count', color='genre',
                   title="Popularidade dos Gêneros ao Longo do Tempo",
                   color_discrete_sequence=red_shades)

    # Exibir os gráficos distribuídos em colunas
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1)
    with col2:
        st.plotly_chart(fig2)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(fig3)
    with col4:
        st.plotly_chart(fig4)

    col5, col6 = st.columns(2)
    with col5:
        st.plotly_chart(fig5)
    with col6:
        st.plotly_chart(fig6)


# Função para exibir os cartões com informações
def draw_cards(movie_info):
    st.write("### Título Selecionado")

    # Ajustar a largura das colunas, com o título ocupando mais espaço
    cols = st.columns([2, 1, 1, 1])

    # Exibir as informações nos cartões de acordo com o filme selecionado
    cols[0].metric(label="Título", value=movie_info['title'])
    cols[1].metric(label="Ano", value=str(movie_info['year']))
    cols[2].metric(label="Gênero", value=movie_info['genre'])
    cols[3].metric(label="Avaliação", value=str(movie_info['rating']))

    # Exibir a descrição completa abaixo dos cartões
    st.write("### Descrição")
    st.write(movie_info['description'])

    # Adicionar um divisor
    st.write("---")


# Função principal do dashboard
def main():
    # CSS customizado para centralizar e estilizar o título com a cor vermelha personalizada
    st.markdown("""
        <style>
        .title {
            text-align: center;
            font-size: 3rem;
            color: #8c0005; /* Vermelho Personalizado */
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # Centralizar e renomear o título
    st.markdown('<h1 class="title">Dashboard Netflix com Python</h1>', unsafe_allow_html=True)

    # Carregar os dados
    df = load_data()

    # Criar colunas para a organização com menor largura para col1 (1:4)
    col1, col2 = st.columns([1, 4])

    # Parte 1 - Filtros e informações na coluna 1 (coluna compacta)
    with col1:
        # Exibir a logo da Netflix acima dos filtros
        st.image("D:/IBRINK-PC-USER/Desktop/Dados/BaseDados/netflix.png", width=200)

        st.markdown("<div style='padding-right: 20px;'>", unsafe_allow_html=True)

        # Filtro de Gênero
        genre_filter = st.selectbox("Filtrar por Gênero", options=df['genre'].unique())

        # Filtro de Ano
        year_filter = st.slider("Filtrar por Ano", min_value=int(df['year'].min()), max_value=int(df['year'].max()),
                                value=(int(df['year'].min()), int(df['year'].max())))

        # Filtro de Avaliação
        rating_filter = st.slider("Filtrar por Avaliação", min_value=float(df['rating'].min()), max_value=float(df['rating'].max()),
                                  value=(float(df['rating'].min()), float(df['rating'].max())))

        # Filtrar os dados com base nos filtros aplicados
        filtered_data = df[
            (df['genre'] == genre_filter) &
            (df['year'].between(year_filter[0], year_filter[1])) &
            (df['rating'].between(rating_filter[0], rating_filter[1]))
        ]

        # Filtro de título baseado no gênero selecionado
        movie_selected = st.selectbox("Selecione um Filme", options=filtered_data['title'].unique())

        # Exibir as informações do filme selecionado
        movie_info = filtered_data[filtered_data['title'] == movie_selected].iloc[0]

        st.markdown("</div>", unsafe_allow_html=True)

    # Parte 2 - Exibir os cartões e gráficos na coluna 2 (coluna principal)
    with col2:
        # Exibir os cartões dinâmicos com as informações do filme selecionado
        draw_cards(movie_info)

        # Exibir os gráficos solicitados distribuídos em 2 colunas por linha
        draw_graphs(filtered_data, df)


# Executar a função principal
if __name__ == "__main__":
    main()
