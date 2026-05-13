import streamlit as st
import datetime
import json
import os
from supabase import create_client, Client

# ==============================================================================
# 🎨 DESIGN E ESTILO
# ==============================================================================
st.set_page_config(page_title="ECO DECOR - Demanda diária", page_icon="📋", layout="centered")

st.markdown("""
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
# ⚙️ CONEXÃO COM O SUPABASE
# ==============================================================================
URL_SUPABASE = "https://amnjfpettwnrhszgdpyk.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFtbmpmcGV0dHducmhzemdkcHlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2MDY0MjUsImV4cCI6MjA5NDE4MjQyNX0.WHbyxzceCNo1_btFkpwM0nov4I73zqiSa4taYkH6msc"

try:
    supabase: Client = create_client(URL_SUPABASE, CHAVE_SUPABASE)
except Exception as e:
    st.error(f"Erro ao inicializar o Supabase: {e}")

ETAPAS_PRODUCAO = [
    "ETIQUETAS (LUCAS)", "ARTE (TALLES/LUCAS)", "IMPRESSÃO (TALLES)",
    "CORTE EM ANDAMENTO (DAVID)", "CORTE FINALIZADO (DAVID)",
    "PRODUÇÃO EM ANDAMENTO (SASKA)", "PRODUÇÃO FINALIZADO (SASKA)",
    "NOTA FISCAL (MICHELLI)", "LIBERADO PARA ENTREGA (MICHELLI)"
]

# Variáveis de Estado
if 'data_foco' not in st.session_state: st.session_state.data_foco = datetime.date.today() + datetime.timedelta(days=1)
if 'modo_demanda' not in st.session_state: st.session_state.modo_demanda = 'lista'
if 'itens_temp' not in st.session_state: st.session_state.itens_temp = []
if 'demanda_edit' not in st.session_state: st.session_state.demanda_edit = None

# ==============================================================================
# 🧹 FUNÇÃO DE LIMPEZA AUTOMÁTICA E CARREGAMENTO
# ==============================================================================
def limpar_demandas_antigas():
    try:
        data_limite = datetime.date.today() - datetime.timedelta(days=5)
        data_limite_str = data_limite.strftime("%Y-%m-%d")
        supabase.table("demandas").delete().lt("data", data_limite_str).execute()
    except Exception as e:
        pass

def carregar_bd():
    limpar_demandas_antigas()
    try:
        resposta = supabase.table("demandas").select("*").execute()
        bd_organizado = {}
        for d in resposta.data:
            data_str = str(d['data'])
            if data_str not in bd_organizado: bd_organizado[data_str] = []
            bd_organizado[data_str].append(d)
        return bd_organizado
    except Exception as e:
        return {}

def mover_demanda(d_atual, d_alvo, idx_atual, idx_alvo):
    ordem_atual = d_atual.get('ordem') if d_atual.get('ordem') is not None else idx_atual
    ordem_alvo = d_alvo.get('ordem') if d_alvo.get('ordem') is not None else idx_alvo
    if ordem_atual == ordem_alvo: ordem_atual, ordem_alvo = idx_atual, idx_alvo
    try:
        supabase.table("demandas").update({"ordem": ordem_alvo}).eq("id", d_atual['id']).execute()
        supabase.table("demandas").update({"ordem": ordem_atual}).eq("id", d_alvo['id']).execute()
        st.rerun()
    except Exception as e:
        st.error("Erro ao mover card.")

# ==============================================================================
# 📋 INTERFACE KANBAN E CABEÇALHO CENTRALIZADO
# ==============================================================================

# Cria colunas com espaços vazios nas pontas (2 e 2) para "espremer" a logo e o título para o centro
col_vazia_esq, col_logo, col_titulo, col_vazia_dir = st.columns([2, 1, 3, 2], vertical_alignment="center")

with col_logo:
    try:
        # A logo no tamanho ideal para acompanhar o texto
        st.image("ECO TRANSPARENTE Logo Nova.png", width=60) 
    except:
        st.write("🖼️") 

with col_titulo:
    st.markdown("<h2 style='margin: 0; text-align: left;'>DEMANDA DIÁRIA</h2>", unsafe_allow_html=True)

st.write("---") # Linha divisória

# Navegação de Datas (Também espremida para o centro com proporções [2, 1, 3, 1, 2])
nav_espaco1, btn_ant, nav_data, btn_prox, nav_espaco2 = st.columns([2, 1, 3, 1, 2], vertical_alignment="center")

if btn_ant.button("◀", key="btn_ant"): 
    st.session_state.data_foco -= datetime.timedelta(days=1)
    st.rerun()
    
nova_data = nav_data.date_input("", value=st.session_state.data_foco, format="DD/MM/YYYY", label_visibility="collapsed")
if nova_data != st.session_state.data_foco: 
    st.session_state.data_foco = nova_data
    st.rerun()
    
if btn_prox.button("▶", key="btn_prox"): 
    st.session_state.data_foco += datetime.timedelta(days=1)
    st.rerun()

st.divider()
bd = carregar_bd()
data_str = st.session_state.data_foco.strftime("%Y-%m-%d")

# ------------------------------------------------------------------------------
# MODO: LISTA
# ------------------------------------------------------------------------------
if st.session_state.modo_demanda == 'lista':
    if st.button("➕ ADICIONAR NOVA DEMANDA"):
        st.session_state.modo_demanda = 'nova'
        st.session_state.itens_temp = []
        st.session_state.demanda_edit = None
        st.rerun()

    st.write("---")
    demandas_do_dia = bd.get(data_str, [])
    demandas_do_dia.sort(key=lambda x: (x.get('ordem', 999), x['id']))

    if not demandas_do_dia:
        st.info(f"Nenhuma demanda para {st.session_state.data_foco.strftime('%d/%m/%Y')}.")
    else:
        for idx, d in enumerate(demandas_do_dia):
            etapas = d.get('etapas', {})
            marcadas = sum(1 for v in etapas.values() if v)
            total = len(ETAPAS_PRODUCAO)
            
            if marcadas == 0: status_html = "<span class='status-badge pendente'>🔴 PENDENTE</span>"
            elif marcadas == total: status_html = "<span class='status-badge finalizado'>🟢 FINALIZADO</span>"
            else: status_html = f"<span class='status-badge andamento'>🟡 ANDAMENTO ({marcadas}/{total})</span>"

            medidas_str = ""
            if isinstance(d['itens'], list) and len(d['itens']) > 0:
                medidas_str = " - " + " | ".join([f"{it['qtd']}x {it['tam']}" for it in d['itens']])
            elif isinstance(d['itens'], str):
                medidas_str = f" - {d['itens']}"

            titulo_expander = f"{d['cliente']} - NF: {d['nf']}{medidas_str}"

            with st.expander(titulo_expander):
                st.markdown(f"{status_html}", unsafe_allow_html=True)
                if d.get('agendamento'): st.write(f"📅 **Agendado para:** {d['agendamento']}")
                if d.get('referencia'): st.write(f"📝 **Referência:** {d['referencia']}")
                st.write("---")
                st.markdown("### ✅ CHECKLIST")
                
                mudou_algo = False
                for i, etapa in enumerate(ETAPAS_PRODUCAO):
                    valor_atual = etapas.get(etapa, False)
                    novo_valor = st.checkbox(etapa, value=valor_atual, key=f"chk_{d['id']}_{i}")
                    if novo_valor != valor_atual:
                        etapas[etapa] = novo_valor
                        mudou_algo = True
                
                if mudou_algo:
                    supabase.table("demandas").update({"etapas": etapas}).eq("id", d['id']).execute()
                    st.rerun()

                st.write("---")
                st.markdown("### ⚙️ AÇÕES")
                c1, c2, c3, c4 = st.columns(4)
                if c1.button("✏️ Editar", key=f"ed_{d['id']}"):
                    st.session_state.modo_demanda = 'editar'
                    st.session_state.demanda_edit = d
                    st.session_state.itens_temp = d['itens'] if isinstance(d['itens'], list) else []
                    st.rerun()
                if c2.button("🗑️ Excluir", key=f"del_{d['id']}"):
                    supabase.table("demandas").delete().eq("id", d['id']).execute()
                    st.rerun()
                if c3.button("⬆️ Subir", key=f"up_{d['id']}"):
                    if idx > 0: mover_demanda(d, demandas_do_dia[idx-1], idx, idx-1)
                if c4.button("⬇️ Descer", key=f"down_{d['id']}"):
                    if idx < len(demandas_do_dia) - 1: mover_demanda(d, demandas_do_dia[idx+1], idx, idx+1)

# ------------------------------------------------------------------------------
# MODO: NOVA OU EDITAR DEMANDA
# ------------------------------------------------------------------------------
elif st.session_state.modo_demanda in ['nova', 'editar']:
    is_edit = st.session_state.modo_demanda == 'editar'
    d_edit = st.session_state.demanda_edit if is_edit else {}
    st.write(f"### {'✏️ Editar Demanda' if is_edit else '➕ Nova Demanda'}")
    
    with st.container(border=True):
        cli_d = st.text_input("Nome do cliente:", value=d_edit.get('cliente', '')).strip().upper()
        nf_d = st.text_input("Número da NF:", value=d_edit.get('nf', '')).strip().upper()
        st.write("📦 **ITENS DA DEMANDA:**")
        
        for i, item in enumerate(st.session_state.itens_temp):
            c_it1, c_it2 = st.columns([4, 1])
            c_it1.write(f"• **{item['qtd']}** unidades de **{item['tam']}**")
            if c_it2.button("🗑️", key=f"rem_item_{i}"):
                st.session_state.itens_temp.pop(i)
                st.rerun()
                
        st.write("---")
        c_m1, c_m2, c_m3 = st.columns([2, 2, 2])
        t_med = c_m1.selectbox("Medida:", ["30x40", "60x40", "90x60"])
        t_qtd = c_m2.number_input("QTD:", min_value=1, value=1)
        if c_m3.button("➕ Adicionar Medida"):
            st.session_state.itens_temp.append({"tam": t_med, "qtd": t_qtd})
            st.rerun()

        st.write("---")
        txt_agend = st.text_input("Agendamento:", value=d_edit.get('agendamento', '')).strip().upper()
        txt_ref = st.text_area("Referência:", value=d_edit.get('referencia', '')).strip().upper()
        
        c_salvar, c_voltar = st.columns(2)
        if c_salvar.button("✅ SALVAR NA NUVEM"):
            if cli_d and nf_d and len(st.session_state.itens_temp) > 0:
                dados = {
                    "data": st.session_state.data_foco.strftime("%Y-%m-%d") if not is_edit else d_edit['data'],
                    "cliente": cli_d, "nf": nf_d, "itens": st.session_state.itens_temp,
                    "agendamento": txt_agend, "referencia": txt_ref,
                }
                try:
                    if is_edit:
                        supabase.table("demandas").update(dados).eq("id", d_edit['id']).execute()
                    else:
                        dados["etapas"] = {etapa: False for etapa in ETAPAS_PRODUCAO}
                        dados["ordem"] = 999
                        supabase.table("demandas").insert(dados).execute()
                    st.session_state.modo_demanda = 'lista'
                    st.session_state.itens_temp = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao guardar: {e}")
            else:
                st.warning("⚠️ Preencha Nome, NF e adicione uma medida!")

        if c_voltar.button("❌ VOLTAR"):
            st.session_state.modo_demanda = 'lista'
            st.session_state.itens_temp = []
            st.rerun()
