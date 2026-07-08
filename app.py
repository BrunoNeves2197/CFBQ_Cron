import streamlit as st
import time
import os

# 1. CONFIGURAÇÃO DA PÁGINA (Preto Absoluto e Otimizado para TV)
st.set_page_config(page_title="CF BQ - Official Web Timer", layout="wide")

# =====================================================================
# 🎨 CSS BLINDADO - CONTROLE TOTAL DOS BOTÕES DE MAIS E MENOS
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

    .block-container { 
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        height: 100vh !important;
        max-width: 100% !important;
    }
    
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    audio { display: none !important; height: 0px !important; width: 0px !important; visibility: hidden !important; }
    
    /* Configuração da Barra Lateral */
    [data-testid="stSidebar"] { background-color: #121212 !important; border-right: 2px solid #D97824 !important; }
    [data-testid="stSidebar"] label { color: #E0E0E0 !important; font-weight: bold; font-size: 14px; }
    
    /* 🔥 ULTRA FORÇADOR DE BOTÕES + E - PARA TODOS OS INPUTS NUMÉRICOS */
    div[data-testid="stNumberInput"] {
        width: 100% !important;
    }
    
    /* Customiza a cor dos botões de + e - para o Laranja Oficial */
    div[data-testid="stNumberInput"] button {
        background-color: #D97824 !important;
        color: white !important;
        border: none !important;
    }
    
    div[data-testid="stNumberInput"] button:hover {
        background-color: #b3601b !important;
    }
    
    /* Alinha o texto interno no centro */
    div[data-testid="stNumberInput"] input {
        text-align: center !important;
        font-weight: bold !important;
    }
    
    /* POSITION ABSOLUTE: Fixa o display no centro físico */
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
    
    .status-text { font-family: 'Impact', sans-serif; font-size: 42px; text-align: center; letter-spacing: 2px; margin-bottom: 5px; }
    .timer-text { font-family: 'Impact', sans-serif; font-size: 160px; text-align: center; line-height: 1; margin: 10px 0; letter-spacing: 2px; }
    .round-text { font-family: 'Arial', sans-serif; font-size: 32px; color: #D97824; font-weight: bold; text-align: center; margin-top: 5px; }
    
    div.stButton > button { font-family: 'Impact', sans-serif; font-size: 18px; background-color: #D97824; color: white; border: none; border-radius: 8px; height: 42px; }
    div.stButton > button:hover { background-color: #b3601b; color: white; }
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZAÇÃO DE VARIÁVEIS DE SESSÃO
if "em_execucao" not in st.session_state: st.session_state.em_execucao = False
if "modo_anuncio" not in st.session_state: st.session_state.modo_anuncio = False
if "indice_anuncio" not in st.session_state: st.session_state.indice_anuncio = 0
if "resetado" not in st.session_state: st.session_state.resetado = True

if "tempo_decorrido" not in st.session_state: st.session_state.tempo_decorrido = 0
if "fase_preparacao" not in st.session_state: st.session_state.fase_preparacao = True
if "countdown_prep" not in st.session_state: st.session_state.countdown_prep = 10
if "round_atual" not in st.session_state: st.session_state.round_atual = 1
if "em_descanso" not in st.session_state: st.session_state.em_descanso = False

# Caixa de som limpa
som_box = st.empty()

def disparar_som(tipo):
    try:
        som_box.empty()
        if tipo == "321" and os.path.exists("beep_curto.wav"):
            som_box.audio("beep_curto.wav", autoplay=True)
        elif tipo == "go" and os.path.exists("beep_longo.wav"):
            som_box.audio("beep_longo.wav", autoplay=True)
    except:
        pass

# 3. PAINEL LATERAL (CONFIGURAÇÕES)
with st.sidebar:
    st.markdown("<h2 style='color: #D97824; font-family: Impact; text-align: center; margin-bottom: 20px;'>CONFIGURAÇÕES</h2>", unsafe_allow_html=True)
    
    travado_por_anuncio = st.session_state.modo_anuncio or st.session_state.em_execucao
    
    protocolo = st.selectbox("Protocolo / WOD:", ["EMOM", "AMRAP / For Time", "TABATA"], disabled=travado_por_anuncio)
    direcao = st.selectbox("Tipo de Contagem:", ["Decrescente (Regressiva)", "Crescente (Progressiva)"], disabled=travado_por_anuncio)
    
    st.markdown("**Tempo de Trabalho:**")
    c_min, c_seg = st.columns(2)
    with c_min: m_val = st.number_input("Minutos:", min_value=0, max_value=59, value=1, step=1, disabled=travado_por_anuncio)
    with c_seg: s_val = st.number_input("Segundos:", min_value=0, max_value=59, value=0, step=1, disabled=travado_por_anuncio)
    
    h_val = st.number_input("Horas (Opcional):", min_value=0, max_value=23, value=0, step=1, disabled=travado_por_anuncio)
    
    tempo_total_segundos = (h_val * 3600) + (m_val * 60) + s_val
    
    label_rounds = "Séries (Trab/Desc):" if protocolo == "TABATA" else "Total de Rounds:"
    disabled_rounds = True if (protocolo == "AMRAP / For Time" or travado_por_anuncio) else False
    rounds_totais = st.number_input(label_rounds, min_value=1, value=5, step=1, disabled=disabled_rounds)
    if protocolo == "AMRAP / For Time":
        rounds_totais = 1

    tempo_descanso = 10
    if protocolo == "TABATA":
        tempo_descanso = st.number_input("Tempo de Descanso (segundos):", min_value=1, value=10, step=1, disabled=travado_por_anuncio)

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
            st.session_state.fase_preparacao = True
            st.session_state.countdown_prep = 10
            st.session_state.tempo_decorrido = 0
            st.session_state.round_atual = 1
            st.session_state.em_descanso = False
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

# 4. PAINEL CENTRAL (ESTRUTURA ABSOLUTA)
st.markdown("<div class='main-display'>", unsafe_allow_html=True)

if os.path.exists("logo_cfbq.png"):
    st.image("logo_cfbq.png", width=340)
else:
    st.markdown("<h1 style='color: #D97824; font-family: Impact;'>CF BQ</h1>", unsafe_allow_html=True)

status_box = st.empty()
timer_box = st.empty()
round_box = st.empty()

st.markdown("</div>", unsafe_allow_html=True)

def formatar_tempo(segundos):
    h, resto = divmod(segundos, 3600)
    m, s = divmod(resto, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# =====================================================================
# MODO ANÚNCIOS
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
                timer_box.image(os.path.join(pasta_anuncios, img_atual), width=520)
                time.sleep(5)
                st.session_state.indice_anuncio += 1
                st.rerun()

# =====================================================================
# ENGINE DO CRONÔMETRO (SINCRO DE BIPES NO SEGUNDO EXATO)
# =====================================================================
elif st.session_state.em_execucao:
    regressiva = "Decrescente" in direcao

    # ⏱️ FASE 1: COUNTDOWN PREPARATÓRIO (10 SEGUNDOS)
    if st.session_state.fase_preparacao:
        status_box.markdown("<div class='status-text' style='color: #D97824;'>PREPARE-SE! (COUNTDOWN)</div>", unsafe_allow_html=True)
        timer_box.markdown(f"<div class='timer-text' style='color: #D97824;'>00:00:{st.session_state.countdown_prep:02d}</div>", unsafe_allow_html=True)
        round_box.markdown("<div class='round-text'>PREPARAÇÃO</div>", unsafe_allow_html=True)
        
        # 3, 2, 1 -> Bipa Curto
        if 1 <= st.session_state.countdown_prep <= 3: 
            disparar_som("321")
            
        time.sleep(1)
        st.session_state.countdown_prep -= 1
        
        # 🎯 CORREÇÃO: Dispara o som longo ANTES de virar o estado e dar rerun
        if st.session_state.countdown_prep < 0:
            disparar_som("go") # 0 -> Apito longo de INÍCIO REAL DO WOD!
            st.session_state.fase_preparacao = False
        st.rerun()

    # ⏱️ FASE 2: EXECUÇÃO DO TREINO
    else:
        r = st.session_state.round_atual
        if r > rounds_totais:
            st.session_state.em_execucao = False
            disparar_som("go") # Bipe longo final do WOD Completo
            status_box.markdown("<div class='status-text' style='color: #D97824;'>WORKOUT DONE! 🔥</div>", unsafe_allow_html=True)
            timer_box.markdown("<div class='timer-text' style='color: #D97824;'>00:00:00</div>", unsafe_allow_html=True)
            round_box.markdown("<div class='round-text'>WOD FINALIZADO!</div>", unsafe_allow_html=True)
            st.rerun()

        txt_round = "AMRAP / TIME CAP" if protocolo == "AMRAP / For Time" else f"ROUND: {r} / {rounds_totais}"
        round_box.markdown(f"<div class='round-text'>{txt_round}</div>", unsafe_allow_html=True)

        if not st.session_state.em_descanso:
            # 🟢 MODO WORK
            tempo_restante_ciclo = tempo_total_segundos - st.session_state.tempo_decorrido
            segundos_tela = tempo_restante_ciclo if regressiva else st.session_state.tempo_decorrido
            
            # Bipa curto no 3, 2, 1 antes de virar ou terminar
            cor_atual = "#FFFFFF"
            if 1 <= tempo_restante_ciclo <= 3:
                cor_atual = "#D97824"
                disparar_som("321")

            status_box.markdown("<div class='status-text' style='color: #00FF66;'>WORK!</div>", unsafe_allow_html=True)
            timer_box.markdown(f"<div class='timer-text' style='color: {cor_atual};'>{formatar_tempo(segundos_tela)}</div>", unsafe_allow_html=True)
            
            time.sleep(1)
            st.session_state.tempo_decorrido += 1

            if st.session_state.tempo_decorrido > tempo_total_segundos:
                disparar_som("go") # Bipe LONGO na virada do EMOM / Término
                if protocolo == "TABATA":
                    st.session_state.em_descanso = True
                    st.session_state.tempo_decorrido = 0
                else:
                    st.session_state.round_atual += 1
                    st.session_state.tempo_decorrido = 0
            st.rerun()

        else:
            # 🔵 MODO REST (DESCANSO TABATA)
            tempo_restante_descanso = tempo_descanso - st.session_state.tempo_decorrido
            
            if 1 <= tempo_restante_descanso <= 3:
                disparar_som("321")

            status_box.markdown("<div class='status-text' style='color: #3366FF;'>REST / DESCANSO</div>", unsafe_allow_html=True)
            timer_box.markdown(f"<div class='timer-text' style='color: #3366FF;'>{formatar_tempo(tempo_restante_descanso)}</div>", unsafe_allow_html=True)
            
            time.sleep(1)
            st.session_state.tempo_decorrido += 1

            if st.session_state.tempo_decorrido > tempo_descanso:
                disparar_som("go") # Bipe LONGO na volta pro WORK
                st.session_state.em_descanso = False
                st.session_state.round_atual += 1
                st.session_state.tempo_decorrido = 0
            st.rerun()

# =====================================================================
# ESTADO DE ESPERA
# =====================================================================
else:
    if not st.session_state.resetado:
        status_box.markdown("<div class='status-text' style='color: #FF3333;'>TREINO INTERROMPIDO</div>", unsafe_allow_html=True)
    else:
        status_box.markdown("<div class='status-text'>READY TO WORK</div>", unsafe_allow_html=True)
        
    timer_box.markdown("<div class='timer-text'>00:00:00</div>", unsafe_allow_html=True)
    round_box.markdown("<div class='round-text'>ROUND: -- / --</div>", unsafe_allow_html=True)