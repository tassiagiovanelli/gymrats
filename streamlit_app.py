import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date
import pytz

# Page configuration
st.set_page_config(page_title="Gymrats Dashboard", page_icon="📈", layout="wide")
st.image("https://img.utdstc.com/icon/55f/304/55f30479adbe539eb6a68aa776833c8bb2811e29deafcc1b8ab71e6862427eb9:200", width=100 )
st.title("Gymrats Dashboard")
st.markdown("[Download the Gymrats](https://play.google.com/store/apps/details?id=com.hasz.gymrats.app&hl=pt_BR )")
st.markdown("Upload your CSV files (e.g., account_check_ins.csv, challenges.csv, account_check_in_activities.csv, and others) to visualize your training data and performance.")

# Language toggle
trocar_idioma = st.checkbox("Display weekdays in Portuguese")

if trocar_idioma:
    dias_semana_ordem = ['Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado','Domingo']
    mapa_dias = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
else:
    dias_semana_ordem = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    mapa_dias = {dia: dia for dia in dias_semana_ordem}

uploaded_files = st.file_uploader("Upload your CSV data", type="csv", accept_multiple_files=True)

if uploaded_files:
    check_ins_list = []
    desafios = None
    activities = None
    media = None
    arquivos_carregados = []

    for file in uploaded_files:
        arquivos_carregados.append(file.name)
        if file.name == "account_check_ins.csv":
            check_ins_list.append(pd.read_csv(file))
        elif file.name == "challenges.csv":
            desafios = pd.read_csv(file)
        elif file.name == "account_check_in_activities.csv":
            activities = pd.read_csv(file)
        elif file.name == "account_check_in_media.csv":
            media = pd.read_csv(file)

    st.caption(f"Loaded files: {', '.join(arquivos_carregados)}")

    arquivos_essenciais = ["account_check_ins.csv"]
    for nome in arquivos_essenciais:
        if nome not in arquivos_carregados:
            st.warning(f"Essential file missing: {nome}")

    if check_ins_list:
        check_ins = pd.concat(check_ins_list, ignore_index=True)
        check_ins['created_at'] = pd.to_datetime(check_ins['created_at'], utc=True)
        tz_sp = pytz.timezone('America/Sao_Paulo')
        check_ins['created_at'] = check_ins['created_at'].dt.tz_convert(tz_sp).dt.tz_localize(None)
        check_ins['date'] = check_ins['created_at'].dt.normalize()
        check_ins['day_name'] = check_ins['created_at'].dt.day_name()
        check_ins['hour'] = check_ins['created_at'].dt.hour

        if 'id' in check_ins.columns:
            check_ins = check_ins.drop_duplicates(subset=['id'])
        elif 'workout_id' in check_ins.columns:
            check_ins = check_ins.drop_duplicates(subset=['workout_id'])
        else:
            check_ins = check_ins.drop_duplicates(subset=['user_id', 'created_at'])

        # --- Integração com activities ---
        if activities is not None and 'check_in_id' in activities.columns:
            activities_agg = activities.groupby('check_in_id').agg(
                total_duration=('duration', 'sum'),
                total_calories=('calories', 'sum')
            ).reset_index()
            check_ins = check_ins.merge(activities_agg, left_on='id', right_on='check_in_id', how='left', suffixes=('', '_activity'))
            check_ins['duration'] = check_ins['total_duration'].fillna(check_ins['duration'])
            check_ins['calorias'] = check_ins['total_calories'].fillna(check_ins['calorias'])
        # --- Fim da integração com activities ---

        # --- Integração com media (fix seguro) ---
        if media is not None and 'check_in_id' in media.columns and 'url' in media.columns:
            media_agg = media.groupby('check_in_id').agg(
                photo_url=('url', 'first')
            ).reset_index()
            check_ins = check_ins.merge(media_agg, left_on='id', right_on='check_in_id', how='left')
        # --- Fim da integração com media ---


        data_min_overall = check_ins['date'].min().date() if not check_ins.empty else date.today()
        data_max_overall = check_ins['date'].max().date() if not check_ins.empty else date.today()

        try:
            data_inicio, data_fim = st.date_input("Select the range", value=(data_min_overall, data_max_overall), min_value=data_min_overall, max_value=data_max_overall)
        except Exception:
            st.warning("Could not set date range, using full data range.")
            data_inicio, data_fim = data_min_overall, data_max_overall

        check_ins_filtered = check_ins[(check_ins['date'] >= pd.to_datetime(data_inicio)) & (check_ins['date'] <= pd.to_datetime(data_fim))]

        # --- REMOVIDO: Filtro por Desafio ---
        # if desafios is not None and 'id' in desafios.columns and 'name' in desafios.columns:
        #     desafio_map = dict(zip(desafios['id'], desafios['name']))
        #     desafio_opcoes = ['All Workouts'] + list(desafios['name'].dropna().unique())
        #     desafio_nome_selecionado = st.selectbox("Filter by Challenge", options=desafio_opcoes)
        #     if desafio_nome_selecionado != 'All Workouts':
        #         selected_challenge_id = desafios[desafios['name'] == desafio_nome_selecionado]['id'].iloc[0]
        #         check_ins_filtered = check_ins_filtered[check_ins_filtered['challenge_id'] == selected_challenge_id]
        # --- FIM DA REMOÇÃO ---

        # --- Adicionar verificação para check_ins_filtered não vazio ---
        if check_ins_filtered.empty:
            st.warning("No data found for the selected period. Please adjust your date range or upload more data.")
        else:
            total_treinos = len(check_ins_filtered)
            dias_unicos = check_ins_filtered['date'].nunique()
            hoje = pd.to_datetime(datetime.today().date())
            inicio_ano = pd.to_datetime(datetime(hoje.year, 1, 1).date())

            dias_passados = (hoje - inicio_ano).days + 1
            semanas_totais = dias_passados / 7 if dias_passados > 0 else 1

            media_treinos_por_semana = round(total_treinos / semanas_totais, 2)
            media_dias_ativos_por_semana = round(dias_unicos / semanas_totais, 2)
            porcentagem_uso = round((dias_unicos / dias_passados) * 100, 2) if dias_passados > 0 else 0

            media_calorias_treino = round(check_ins_filtered['calorias'].mean(), 2) if 'calorias' in check_ins_filtered.columns and check_ins_filtered['calorias'].notna().any() else 'N/A'
            
            if 'duration' in check_ins_filtered.columns:
                check_ins_filtered['duration'] = pd.to_numeric(check_ins_filtered['duration'], errors='coerce')
                media_tempo_treino = check_ins_filtered['duration'].mean()
                media_tempo_formatado = f"{int(round(media_tempo_treino))} min" if pd.notnull(media_tempo_treino) else 'N/A'
            else:
                media_tempo_formatado = 'N/A'

            frequencia_dias = check_ins_filtered['day_name'].value_counts().reindex(dias_semana_ordem, fill_value=0)
            dia_mais_faltado = frequencia_dias.idxmin() if not frequencia_dias.empty else 'N/A'
            horario_mais_comum = check_ins_filtered['hour'].mode()[0] if not check_ins_filtered['hour'].mode().empty else 'N/A'

            st.subheader("Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Check-ins", total_treinos)
            col2.metric("Unique Active Days", dias_unicos)
            col3.metric("% This Year", f"{dias_unicos}/{dias_passados} ({porcentagem_uso}%)")

            col4, col5, col6, col7 = st.columns(4)
            col4.metric("Avg Workouts/Week", media_treinos_por_semana)
            col5.metric("Avg Active Days/Week", media_dias_ativos_por_semana)
            col6.metric("Avg Calories/Workout", media_calorias_treino)
            col7.metric("Avg Time/Workout", media_tempo_formatado)

            st.markdown(f"**Most missed day:** {mapa_dias.get(dia_mais_faltado, dia_mais_faltado)}")
            st.markdown(f"**Most frequent hour:** {horario_mais_comum}h")

            st.subheader("Workout Evolution in the Year")

            calendar_df = pd.DataFrame({'date': pd.date_range(data_inicio, data_fim)})
            calendar_df['day_name'] = calendar_df['date'].dt.day_name()

            resumo_diario = check_ins_filtered.groupby(['date', 'day_name']).agg({
                'id': 'count',
                'title': lambda x: ', '.join(x.dropna().astype(str))
            }).reset_index().rename(columns={'id': 'qtd_treinos'})

            resumo_diario['day_name'] = resumo_diario['day_name'].map(mapa_dias)

            merged_daily = calendar_df.merge(resumo_diario, on='date', how='left')
            merged_daily['day_name'] = merged_daily['day_name_y'].fillna(merged_daily['day_name_x'].map(mapa_dias))
            merged_daily['qtd_treinos'] = merged_daily['qtd_treinos'].fillna(0)
            merged_daily['title'] = merged_daily['title'].fillna('')

            chart = alt.Chart(merged_daily).mark_line(point=True).encode(
                x='date:T',
                y=alt.Y('qtd_treinos:Q', title='Check-in Count', scale=alt.Scale(nice=False)),
                tooltip=[
                    alt.Tooltip('date:T', title='Date'),
                    alt.Tooltip('day_name:N', title='Weekday'),
                    alt.Tooltip('qtd_treinos:Q', title='Check-in Count'),
                    alt.Tooltip('title:N', title='Check-ins')
                ]
            ).properties(width=1100, height=300)

            st.altair_chart(chart, use_container_width=True)

            st.subheader("Monthly Workout Summary")
            check_ins_filtered['mes'] = check_ins_filtered['date'].dt.to_period('M')
            check_ins_filtered['day_name_mapped'] = check_ins_filtered['day_name'].map(mapa_dias)

            resumo_mensal = check_ins_filtered.groupby(['mes', 'day_name_mapped']).agg(
                check_in_count=('id', 'count')
            ).reset_index()

            tabela = resumo_mensal.pivot(index='mes', columns='day_name_mapped', values='check_in_count').fillna(0)

            for dia in dias_semana_ordem:
                if dia not in tabela.columns:
                    tabela[dia] = 0
            tabela = tabela[dias_semana_ordem]

            tabela['Check-in Count'] = check_ins_filtered.groupby('mes')['id'].count().values
            tabela['Active Days'] = check_ins_filtered.groupby('mes')['date'].nunique().values

            tabela['Month Days'] = tabela.index.to_timestamp().days_in_month
            tabela['Missed Days'] = tabela['Month Days'] - tabela['Active Days']
            tabela['% Month'] = tabela['Active Days'].astype(str) + '/' + tabela['Month Days'].astype(str) + ' (' + (tabela['Active Days']/tabela['Month Days']*100).round(2).astype(str) + '%)'

            tabela = tabela.reset_index().rename(columns={'mes': 'Month'})
            st.dataframe(tabela)

            st.subheader("Export Detailed Table")
            colunas_exportar = ['created_at', 'title', 'duration', 'description', 'calorias', 'photo_url']
            colunas_existentes = [col for col in colunas_exportar if col in check_ins_filtered.columns]

            tabela_exportar = check_ins_filtered[colunas_existentes].rename(columns={
                'created_at': 'Date',
                'title': 'Title',
                'duration': 'Duration (min)',
                'description': 'Description',
                'calorias': 'Calories',
                'photo_url': 'Image'
            })
            st.dataframe(tabela_exportar.drop(columns=['Image'], errors='ignore'))

            if 'photo_url' in check_ins_filtered.columns:
                st.subheader("🏋️ Workout Photo Wall")
                imagens_urls = check_ins_filtered['photo_url'].dropna().unique().tolist()

                if len(imagens_urls) > 0:
                    num_cols = 3
                    cols = st.columns(num_cols)
                    for i, url in enumerate(imagens_urls):
                        with cols[i % num_cols]:
                            try:
                                st.image(url, width=200, caption=f"Foto {i+1}")
                            except Exception as e:
                                st.warning(f"Could not load image {url}: {e}")
                else:
                    st.info("No workout images found for the selected period.")

            st.subheader("🗓️ Frequency Heatmap")
            calendario_heatmap = check_ins_filtered.groupby('date').size().reset_index(name='Check-ins')
            calendario_heatmap['day'] = calendario_heatmap['date'].dt.day
            calendario_heatmap['month'] = calendario_heatmap['date'].dt.month_name()
            calendario_heatmap['weekday'] = calendario_heatmap['date'].dt.day_name()
            calendario_heatmap['weekday_mapped'] = calendario_heatmap['weekday'].map(mapa_dias)

            heat = alt.Chart(calendario_heatmap).mark_rect().encode(
                x=alt.X('weekday_mapped:N', sort=dias_semana_ordem, title='Weekday'),
                y=alt.Y('month:N', title='Month'),
                color=alt.Color('Check-ins:Q', scale=alt.Scale(scheme='blues')),
                tooltip=['date:T', 'Check-ins']
            ).properties(width=700, height=300)

            st.altair_chart(heat, use_container_width=True)
else:
    st.info("Please upload your CSV file(s) to get started.")

