import streamlit as st
import time
import os

# 1. CONFIGURAÇÃO DA PÁGINA (Preto Absoluto e Otimizado para TV)
st.set_page_config(page_title="CF BQ - Official Web Timer", layout="wide")

# =====================================================================
# 🎨 CSS BLINDADO - CENTRALIZAÇÃO ABSOLUTA E OCULTAÇÃO DE PLAYER
# =====================================================================
st.markdown("""
    <style>
    /* Esconde o cabeçalho oficial, o menu e o rodapé do Streamlit */
    header, footer, [data-testid="stHeader"] { visibility: hidden !important; height: 0px !important; }
    
    /* Força o aplicativo a travar o tamanho na tela visível e remove scroll */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {
        overflow: hidden !important;
        height: 100vh !important;
        background-color: #000000 !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    /* Zera os blocos internos de espaçamento vertical do Streamlit */
    .block-container { 
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        height: 100vh !important;
        max-width: 100% !important;
    }
    
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    /* 🔥 MATADOR DE CONTROLES DE ÁUDIO: Esconde qualquer player de som que o Streamlit tente desenhar */
    audio { display: none !important; height: 0px !important; width: 0px !important; visibility: hidden !important; }
    
    /* Configuração da Barra Lateral */
    [data-testid="stSidebar"] { background-color: #121212 !important; border-right: 2px solid #D97824 !important; }
    [data-testid="stSidebar"] label { color: #E0E0E0 !important; font-weight: bold; font-size: 14px; }
    
    /* 🎯 POSITION ABSOLUTE: Fixa o display no centro físico e equilibra com a barra lateral */
    .main-display {
        position: absolute;
        top: 50%;
        left: 55%;
        transform: translate(-50%, -50%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        width: 75%;
        height: 95vh;
    }
    
    /* Fontes Otimizadas para a TV do Box */
    .status-text { 
        font-family: 'Impact', sans-serif; 
        font-size: 42px; 
        text-align: center; 
        letter-spacing: 2px; 
        margin-bottom: 5px;
    }
    .timer-text { 
        font-family: 'Impact', sans-serif; 
        font-size: 160px; 
        text-align: center; 
        line-height: 1; 
        margin: 10px 0;
        letter-spacing: 2px;
    }
    .round-text { 
        font-family: 'Arial', sans-serif; 
        font-size: 32px; 
        color: #D97824; 
        font-weight: bold; 
        text-align: center; 
        margin-top: 5px; 
    }
    
    /* Estilização dos Botões */
    div.stButton > button { 
        font-family: 'Impact', sans-serif; 
        font-size: 18px; 
        background-color: #D97824; 
        color: white; 
        border: none; 
        border-radius: 8px; 
        height: 42px; 
    }
    div.stButton > button:hover { background-color: #b3601b; color: white; }
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZAÇÃO DE VARIÁVEIS DE SESSÃO
if "em_execucao" not in st.session_state: st.session_state.em_execucao = False
if "modo_anuncio" not in st.session_state: st.session_state.modo_anuncio = False
if "indice_anuncio" not in st.session_state: st.session_state.indice_anuncio = 0
if "resetado" not in st.session_state: st.session_state.resetado = True

# Placeholders invisíveis para os bipes
som_curto_placeholder = st.empty()
som_longo_placeholder = st.empty()

def disparar_som(tipo):
    try:
        if tipo == "321" and os.path.exists("beep_curto.wav"):
            som_curto_placeholder.audio("beep_curto.wav", autoplay=True)
        elif tipo == "go" and os.path.exists("beep_longo.wav"):
            som_longo_placeholder.audio("beep_longo.wav", autoplay=True)
    except:
        pass

# 3. PAINEL LATERAL (CONFIGURAÇÕES)
with st.sidebar:
    st.markdown("<h2 style='color: #D97824; font-family: Impact; text-align: center; margin-bottom: 20px;'>CONFIGURAÇÕES</h2>", unsafe_allow_html=True)
    
    travado_por_anuncio = st.session_state.modo_anuncio
    
    protocolo = st.selectbox("Protocolo / WOD:", ["EMOM", "AMRAP / For Time", "TABATA"], disabled=travado_por_anuncio)
    direcao = st.selectbox("Tipo de Contagem:", ["Decrescente (Regressiva)", "Crescente (Progressiva)"], disabled=travado_por_anuncio)
    
    st.markdown("**Tempo de Trabalho:**")
    c1, c2, c3 = st.columns(3)
    with c1: h_val = st.number_input("Horas", min_value=0, max_value=23, value=0, step=1, disabled=travado_por_anuncio)
    with c2: m_val = st.number_input("Min", min_value=0, max_value=59, value=1, step=1, disabled=travado_por_anuncio)
    with c3: s_val = st.number_input("Seg", min_value=0, max_value=59, value=0, step=1, disabled=travado_por_anuncio)
    
    tempo_total_segundos = (h_val * 3600) + (m_val * 60) + s_val
    
    label_rounds = "Séries (Trabalho/Descanso):" if protocolo == "TABATA" else "Total de Rounds:"
    disabled_rounds = True if (protocolo == "AMRAP / For Time" or travado_por_anuncio) else False
    rounds_totais = st.number_input(label_rounds, min_value=1, value=5, disabled=disabled_rounds)
    if protocolo == "AMRAP / For Time":
        rounds_totais = 1

    tempo_descanso = 10
    if protocolo == "TABATA":
        tempo_descanso = st.number_input("Tempo de Descanso (segundos):", min_value=1, value=10, disabled=travado_por_anuncio)

    st.markdown("---")
    
    btn_start = st.button("START WOD 🚀", use_container_width=True, disabled=st.session_state.modo_anuncio or st.session_state.em_execucao)
    btn_stop = st.button("STOP 🛑", use_container_width=True, disabled=st.session_state.modo_anuncio or not st.session_state.em_execucao)
    
    pode_resetar = (not st.session_state.em_execucao) and (not st.session_state.resetado) and (not st.session_state.modo_anuncio)
    btn_reset = st.button("RESET 🔄", use_container_width=True, disabled=not pode_resetar)
    
    label_mural = "VOLTAR P/ RELÓGIO 🕒" if st.session_state.modo_anuncio else "EXIBIR ANÚNCIOS 📢"
    btn_anuncio = st.button(label_mural, use_container_width=True)

    if btn_start:
        if tempo_total_segundos > 0:
            st.session_state.em_execucao = True
            st.session_state.modo_anuncio = False
            st.session_state.resetado = False
        else:
            st.sidebar.error("Insira um tempo válido!")
            
    if btn_stop:
        st.session_state.em_execucao = False
        
    if btn_reset:
        st.session_state.resetado = True
        st.session_state.em_execucao = False
        st.session_state.modo_anuncio = False
        st.rerun()
        
    if btn_anuncio:
        st.session_state.modo_anuncio = not st.session_state.modo_anuncio
        st.session_state.em_execucao = False

# 4. PAINEL CENTRAL (ESTRUTURA FIXA ABSOLUTA)
st.markdown("<div class='main-display'>", unsafe_allow_html=True)

if os.path.exists("logo_cfbq.png"):
    st.image("logo_cfbq.png", width=340)
else:
    st.markdown("<h1 style='color: #D97824; font-family: Impact;'>CF BQ</h1>", unsafe_allow_html=True)

status_box = st.empty()
timer_box = st.empty()
round_box = st.empty()

st.markdown("</div>", unsafe_allow_html=True)

# FORMATADOR
def formatar_tempo(segundos):
    h, resto = divmod(segundos, 3600)
    m, s = divmod(resto, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# =====================================================================
# EXECUÇÃO: MURAL DE ANÚNCIOS CORRIGIDO (Via Método Nativo + Proporção Segura)
# =====================================================================
if st.session_state.modo_anuncio:
    status_box.markdown("<div class='status-text' style='color: #D97824; margin-bottom: 10px;'>MURAL DE ANÚNCIOS / PARCEIROS</div>", unsafe_allow_html=True)
    round_box.empty()
    
    pasta_anuncios = "anuncios"
    if os.path.exists(pasta_anuncios):
        lista_fotos = [f for f in os.listdir(pasta_anuncios) if f.lower().endswith('.png')]
        
        if lista_fotos:
            while st.session_state.modo_anuncio:
                img_atual = lista_fotos[st.session_state.indice_anuncio % len(lista_fotos)]
                caminho_completo = os.path.join(pasta_anuncios, img_atual)
                
                # Renderiza usando o componente nativo do Streamlit, que não quebra o caminho de imagem local
                timer_box.image(caminho_completo, width=520)
                
                time.sleep(5)
                st.session_state.indice_anuncio += 1
                st.rerun()
        else:
            timer_box.markdown("<div class='timer-text' style='font-size:35px; color:#555555;'>NENHUM AD .PNG NA PASTA ANUNCIOS</div>", unsafe_allow_html=True)
    else:
        timer_box.markdown("<div class='timer-text' style='font-size:35px; color:#555555;'>PASTA 'ANUNCIOS' NÃO ENCONTRADA</div>", unsafe_allow_html=True)

# =====================================================================
# EXECUÇÃO: CRONÔMETRO ATIVO
# =====================================================================
elif st.session_state.em_execucao:
    regressiva = "Decrescente" in direcao
    
    # COUNTDOWN PREPARATÓRIO
    for i in range(10, 0, -1):
        if not st.session_state.em_execucao: break
        status_box.markdown("<div class='status-text' style='color: #D97824;'>PREPARE-SE! (COUNTDOWN)</div>", unsafe_allow_html=True)
        timer_box.markdown(f"<div class='timer-text' style='color: #D97824;'>00:00:{i:02d}</div>", unsafe_allow_html=True)
        round_box.markdown("<div class='round-text'>PREPARAÇÃO</div>", unsafe_allow_html=True)
        if i <= 3: disparar_som("321")
        time.sleep(1)

    if st.session_state.em_execucao: disparar_som("go")

    # LOOP DOS ROUNDS
    for r in range(1, rounds_totais + 1):
        if not st.session_state.em_execucao: break
        
        txt_round = "AMRAP / TIME CAP" if protocolo == "AMRAP / For Time" else f"ROUND: {r} / {rounds_totais}"
        round_box.markdown(f"<div class='round-text'>{txt_round}</div>", unsafe_allow_html=True)
        
        ciclo_tempo = tempo_total_segundos
        while ciclo_tempo >= 0 and st.session_state.em_execucao:
            segundos_tela = ciclo_tempo if regressiva else (tempo_total_segundos - ciclo_tempo)
            cor_atual = "#D97824" if 1 <= ciclo_tempo <= 3 else "#FFFFFF"
            
            status_box.markdown("<div class='status-text' style='color: #00FF66;'>WORK!</div>", unsafe_allow_html=True)
            timer_box.markdown(f"<div class='timer-text' style='color: {cor_atual};'>{formatar_tempo(segundos_tela)}</div>", unsafe_allow_html=True)
            
            if 1 <= ciclo_tempo <= 3: disparar_som("321")
            if ciclo_tempo == 0: disparar_som("go")
            
            time.sleep(1)
            ciclo_tempo -= 1
            
        # INTERVALO DO TABATA
        if protocolo == "TABATA" and r < rounds_totais and st.session_state.em_execucao:
            t_rest = tempo_descanso
            while t_rest > 0 and st.session_state.em_execucao:
                status_box.markdown("<div class='status-text' style='color: #3366FF;'>REST / DESCANSO</div>", unsafe_allow_html=True)
                timer_box.markdown(f"<div class='timer-text' style='color: #3366FF;'>{formatar_tempo(t_rest)}</div>", unsafe_allow_html=True)
                if t_rest <= 3: disparar_som("321")
                time.sleep(1)
                t_rest -= 1
            if st.session_state.em_execucao: disparar_som("go")

    # FIM DO WOD
    if st.session_state.em_execucao:
        st.session_state.em_execucao = False
        status_box.markdown("<div class='status-text' style='color: #D97824;'>WORKOUT DONE! 🔥</div>", unsafe_allow_html=True)
        timer_box.markdown("<div class='timer-text' style='color: #D97824;'>00:00:00</div>", unsafe_allow_html=True)
        round_box.markdown("<div class='round-text'>WOD FINALIZADO!</div>", unsafe_allow_html=True)
    else:
        st.rerun()

# =====================================================================
# ESTADO DE ESPERA (PADRÃO)
# =====================================================================
else:
    if not st.session_state.resetado:
        status_box.markdown("<div class='status-text' style='color: #FF3333;'>TREINO INTERROMPIDO</div>", unsafe_allow_html=True)
    else:
        status_box.markdown("<div class='status-text'>READY TO WORK</div>", unsafe_allow_html=True)
        
    timer_box.markdown("<div class='timer-text'>00:00:00</div>", unsafe_allow_html=True)
    round_box.markdown("<div class='round-text'>ROUND: -- / --</div>", unsafe_allow_html=True)