import streamlit as st
import datetime
import json
import random
import os

# ==============================================================================
# 🎨 DESIGN E ESTILO
# ==============================================================================
st.set_page_config(
    page_title="ECO DECOR - Kanban de Produção",
    page_icon="📋", 
    layout="centered"
)

st.markdown("""
    <meta name="google" content="notranslate">
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    h1, h2, h3, h4 { color: #fafafa !important; }
    div.stButton > button {
        width: 100%; height: 50px; background-color: #5d7cf3 !important;
        color: white !important; font-weight: bold !important; border-radius: 8px; border: none;
    }
    .status-badge { padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 14px; }
    .pendente { background-color: #4a0000; color: #ff6666; }
    .andamento { background-color: #4a4a00; color: #ffff66; }
    .finalizado { background-color: #003311; color: #66ff99; }
    .stContainer { background-color: #1a1c24; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# ⚙️ BANCO DE DADOS (LOCAL/NUVEM) E CONFIGURAÇÕES
# ==============================================================================
# Na nuvem, o arquivo fica salvo na mesma pasta do script
ARQUIVO_BD = 'banco_demandas_kanban.json'

ETAPAS_PRODUCAO = [
    "ETIQUETAS (LUCAS/URIEL)",
    "ARTE (TALLES)",
    "IMPRESSÃO (TALLES)",
    "CORTE EM ANDAMENTO (DAVID)",
    "CORTE FINALIZADO (DAVID)",
    "PRODUÇÃO EM ANDAMENTO (SASKA)",
    "PRODUÇÃO FINALIZADO (SASKA)",
    "NOTA FISCAL (URIEL)",
    "LIBERADO PARA ENTREGA (MICHELLI)"
]

def carregar_bd():
    if os.path.exists(ARQUIVO_BD):
        with open(ARQUIVO_BD, 'r', encoding='utf-8') as f: return json.load(f)
    return {}

def salvar_bd(bd):
    with open(ARQUIVO_BD, 'w', encoding='utf-8') as f: json.dump(bd, f, indent=4, ensure_ascii=False)

if 'data_foco' not in st.session_state: 
    st.session_state.data_foco = datetime.date.today() + datetime.timedelta(days=1)
if 'modo_demanda' not in st.session_state: 
    st.session_state.modo_demanda = 'lista'

# ==============================================================================
# 📋 INTERFACE DO KANBAN
# ==============================================================================
st.markdown("<h2 style='text-align: center;'>📋 KANBAN DE PRODUÇÃO</h2>", unsafe_allow_html=True)

# Navegação de Datas
nav1, nav2, nav3, nav4, nav5 = st.columns([1,1,2,1,1])
if nav2.button("◀", key="btn_ant"): st.session_state.data_foco -= datetime.timedelta(days=1); st.rerun()
nova_data = nav3.date_input("", value=st.session_state.data_foco, format="DD/MM/YYYY", label_visibility="collapsed")
if nova_data != st.session_state.data_foco: st.session_state.data_foco = nova_data; st.rerun()
if nav4.button("▶", key="btn_prox"): st.session_state.data_foco += datetime.timedelta(days=1); st.rerun()

st.divider()
bd = carregar_bd()
data_str = st.session_state.data_foco.strftime("%Y-%m-%d")

# ------------------------------------------------------------------------------
# MODO 1: VISUALIZAR A LISTA E MARCAR CHECKLIST
# ------------------------------------------------------------------------------
if st.session_state.modo_demanda == 'lista':
    
    if st.button("➕ ADICIONAR NOVA DEMANDA", use_container_width=True):
        st.session_state.modo_demanda = 'nova'
        st.rerun()

    st.write("---")
    demandas_do_dia = bd.get(data_str, [])

    if not demandas_do_dia:
        st.info(f"Tranquilidade! Nenhuma demanda registrada para {st.session_state.data_foco.strftime('%d/%m/%Y')}.")
    else:
        for d in demandas_do_dia:
            # Lógica de cores do Status
            etapas = d.get('etapas', {})
            marcadas = sum(1 for v in etapas.values() if v)
            total_etapas = len(ETAPAS_PRODUCAO)
            
            if marcadas == 0: status_html = "<span class='status-badge pendente'>🔴 PENDENTE</span>"
            elif marcadas == total_etapas: status_html = "<span class='status-badge finalizado'>🟢 FINALIZADO</span>"
            else: status_html = f"<span class='status-badge andamento'>🟡 EM ANDAMENTO ({marcadas}/{total_etapas})</span>"

            with st.expander(f"{d['cliente']} / NF: {d['nf']}"):
                st.markdown(f"**NF {d['nf']}** | {status_html}", unsafe_allow_html=True)
                
                for it in d['itens']:
                    st.write(f"• {it['tam']} - {it['qtd']} UN")
                
                if d.get('agend'): st.write(f"• 📅 {d['agend']}")
                if d.get('ref'): st.write(f"• 📝 {d['ref']}")
                
                st.write("---")
                st.markdown("### ✅ CHECKLIST DA EQUIPE")
                
                mudou_algo = False
                for i, etapa_nome in enumerate(ETAPAS_PRODUCAO):
                    valor_atual = etapas.get(etapa_nome, False)
                    novo_valor = st.checkbox(etapa_nome, value=valor_atual, key=f"chk_{d['id']}_{i}")
                    if novo_valor != valor_atual:
                        etapas[etapa_nome] = novo_valor
                        mudou_algo = True
                
                if mudou_algo:
                    d['etapas'] = etapas
                    salvar_bd(bd)
                    st.rerun()

                if st.button("🗑️ Excluir Demanda", key=f"del_{d['id']}"):
                    bd[data_str] = [x for x in bd[data_str] if x['id'] != d['id']]
                    salvar_bd(bd)
                    st.rerun()

# ------------------------------------------------------------------------------
# MODO 2: ADICIONAR NOVA DEMANDA
# ------------------------------------------------------------------------------
elif st.session_state.modo_demanda == 'nova':
    st.write(f"### ➕ Nova Demanda ({st.session_state.data_foco.strftime('%d/%m/%Y')})")
    
    with st.container(border=True):
        cli_d = st.text_input("Nome do cliente:").strip().upper()
        nf_d = st.text_input("Número da NF:").strip().upper()
        
        c1, c2 = st.columns(2)
        t_med = c1.selectbox("Medida:", ["30x40", "60x40", "90x60"])
        t_qtd = c2.number_input("QTD:", min_value=1, value=10)
        
        txt_agend = st.text_input("Agendamento (Opcional):").strip().upper()
        txt_ref = st.text_area("Referência Específica (Opcional):").strip().upper()
        
        if st.button("✅ SALVAR DEMANDA NO SISTEMA"):
            if cli_d and nf_d:
                if data_str not in bd: bd[data_str] = []
                
                nova_demanda = {
                    "id": f"{nf_d}_{random.randint(1000,9999)}",
                    "cliente": cli_d,
                    "nf": nf_d,
                    "itens": [{"tam": t_med, "qtd": t_qtd}],
                    "agend": txt_agend,
                    "ref": txt_ref,
                    "etapas": {etapa: False for etapa in ETAPAS_PRODUCAO}
                }
                
                bd[data_str].append(nova_demanda)
                salvar_bd(bd)
                
                st.session_state.modo_demanda = 'lista'
                st.success("Demanda salva! Avisando a produção...")
                st.rerun()
            else:
                st.warning("Preencha o Nome e a NF!")

    if st.button("❌ CANCELAR E VOLTAR"):
        st.session_state.modo_demanda = 'lista'
        st.rerun()