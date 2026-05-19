import streamlit as st
import datetime
import math
from supabase import create_client, Client

# ==============================================================================
# 🎨 CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="ECO DECOR - Demanda diária",
    page_icon="ECO TRANSPARENTE Logo Nova.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 🎨 DESIGN RESPONSIVO - DESKTOP + CELULAR
# ==============================================================================
st.markdown("""
<style>
    :root {
        --bg: #0e1117;
        --card: #171b26;
        --card-2: #1f2433;
        --border: #2f3548;
        --text: #fafafa;
        --muted: #aab2c5;
        --primary: #5d7cf3;
        --primary-2: #425bd6;
        --danger: #ff4b4b;
        --warning: #facc15;
        --success: #22c55e;
    }

    .stApp { background-color: var(--bg); color: var(--text); }
    h1, h2, h3, h4, h5, h6, p, label, span { color: var(--text) !important; }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1250px;
    }

    div.stButton > button, div.stDownloadButton > button {
        width: 100%;
        min-height: 46px;
        background: linear-gradient(135deg, var(--primary), var(--primary-2)) !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,.08) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,.25);
    }

    div.stButton > button:hover, div.stDownloadButton > button:hover {
        filter: brightness(1.08);
        transform: translateY(-1px);
    }

    .eco-header {
        background: linear-gradient(135deg, #121827, #1d2740);
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 12px 30px rgba(0,0,0,.28);
    }

    .eco-title {
        font-size: 30px;
        font-weight: 900;
        text-align: center;
        margin: 0;
        letter-spacing: .5px;
    }

    .eco-subtitle {
        text-align: center;
        color: var(--muted) !important;
        font-size: 15px;
        margin-top: 4px;
    }

    .metric-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 14px 16px;
        box-shadow: 0 10px 22px rgba(0,0,0,.18);
        min-height: 92px;
    }

    .metric-label {
        color: var(--muted) !important;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .metric-value {
        color: #ffffff !important;
        font-size: 28px;
        font-weight: 900;
        line-height: 1;
    }

    .demand-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 10px 24px rgba(0,0,0,.22);
    }

    .demand-head {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: flex-start;
        margin-bottom: 10px;
    }

    .demand-client {
        font-size: 18px;
        font-weight: 900;
        line-height: 1.15;
    }

    .demand-nf {
        color: var(--muted) !important;
        font-weight: 800;
        margin-top: 3px;
    }

    .status-badge {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-weight: 900;
        font-size: 13px;
        white-space: nowrap;
    }
    .pendente { background-color: rgba(239,68,68,.18); color: #ff8b8b !important; border: 1px solid rgba(239,68,68,.35); }
    .andamento { background-color: rgba(250,204,21,.15); color: #fde047 !important; border: 1px solid rgba(250,204,21,.35); }
    .finalizado { background-color: rgba(34,197,94,.15); color: #86efac !important; border: 1px solid rgba(34,197,94,.35); }

    .item-pill {
        display: inline-block;
        background: var(--card-2);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 6px 10px;
        margin: 4px 4px 4px 0;
        font-size: 13px;
        font-weight: 800;
    }

    .info-line {
        color: var(--muted) !important;
        font-size: 14px;
        margin: 5px 0;
    }

    .section-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 10px 24px rgba(0,0,0,.20);
    }

    textarea, input, select {
        border-radius: 12px !important;
    }

    div[data-testid="stExpander"] {
        background-color: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
    }

    div[data-testid="stExpander"] details {
        background: transparent !important;
        border: 0 !important;
    }

    div[data-testid="stCheckbox"] label {
        background: #151a25;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 8px 10px;
        width: 100%;
        margin-bottom: 4px;
    }

    .mobile-note { display: none; }

    @media (max-width: 768px) {
        .block-container {
            padding-left: .75rem;
            padding-right: .75rem;
            padding-top: .75rem;
        }

        .eco-header {
            padding: 14px;
            border-radius: 16px;
        }

        .eco-title {
            font-size: 22px;
        }

        .eco-subtitle {
            font-size: 13px;
        }

        .metric-card {
            min-height: auto;
            padding: 12px;
            border-radius: 14px;
        }

        .metric-value {
            font-size: 23px;
        }

        .demand-card {
            border-radius: 16px;
            padding: 13px;
        }

        .demand-head {
            display: block;
        }

        .demand-client {
            font-size: 16px;
        }

        .status-badge {
            margin-top: 8px;
            font-size: 12px;
        }

        div.stButton > button, div.stDownloadButton > button {
            min-height: 44px;
            font-size: 13px !important;
            padding-left: 8px !important;
            padding-right: 8px !important;
        }

        .item-pill {
            display: block;
            margin: 6px 0;
            text-align: center;
        }

        .mobile-note {
            display: block;
            color: var(--muted) !important;
            font-size: 12px;
            text-align: center;
            margin-top: 6px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# ⚙️ CONFIGURAÇÕES DE CAIXAS
# ==============================================================================
def obter_capacidade(cliente, tam):
    cli_upper = str(cliente).upper()
    is_bigodinho = any(palavra in cli_upper for palavra in ["BIGODINHO", "LUCAS", "JIMMY", "REP"])
    if tam == "90x60":
        return 10 if is_bigodinho else 11
    if tam == "60x40":
        return 24
    if tam == "30x40":
        return 50
    return 1

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

if 'data_foco' not in st.session_state:
    st.session_state.data_foco = datetime.date.today() + datetime.timedelta(days=1)
if 'modo_demanda' not in st.session_state:
    st.session_state.modo_demanda = 'lista'
if 'itens_temp' not in st.session_state:
    st.session_state.itens_temp = []
if 'demanda_edit' not in st.session_state:
    st.session_state.demanda_edit = None
if 'demanda_etiqueta' not in st.session_state:
    st.session_state.demanda_etiqueta = None

# ==============================================================================
# 🧹 FUNÇÕES TÉCNICAS E BANCO DE DADOS
# ==============================================================================
def limpar_demandas_antigas():
    try:
        data_limite = datetime.date.today() - datetime.timedelta(days=5)
        data_limite_str = data_limite.strftime("%Y-%m-%d")
        supabase.table("demandas").delete().lt("data", data_limite_str).execute()
    except Exception:
        pass


def carregar_bd():
    limpar_demandas_antigas()
    try:
        resposta = supabase.table("demandas").select("*").execute()
        bd_organizado = {}
        for d in resposta.data:
            data_str = str(d['data'])
            if data_str not in bd_organizado:
                bd_organizado[data_str] = []
            bd_organizado[data_str].append(d)
        return bd_organizado
    except Exception:
        return {}


def mover_demanda(d_atual, d_alvo, idx_atual, idx_alvo):
    ordem_atual = d_atual.get('ordem') if d_atual.get('ordem') is not None else idx_atual
    ordem_alvo = d_alvo.get('ordem') if d_alvo.get('ordem') is not None else idx_alvo
    if ordem_atual == ordem_alvo:
        ordem_atual, ordem_alvo = idx_atual, idx_alvo
    try:
        supabase.table("demandas").update({"ordem": ordem_alvo}).eq("id", d_atual['id']).execute()
        supabase.table("demandas").update({"ordem": ordem_atual}).eq("id", d_alvo['id']).execute()
        st.rerun()
    except Exception:
        st.error("Erro ao mover card.")


def status_demanda(etapas):
    marcadas = sum(1 for v in etapas.values() if v)
    total = len(ETAPAS_PRODUCAO)
    if marcadas == total:
        return marcadas, total, "finalizado", "🟢 Finalizado"
    if marcadas > 0:
        return marcadas, total, "andamento", "🟡 Em andamento"
    return marcadas, total, "pendente", "🔴 Pendente"


def linha_cliente_etiqueta(cliente):
    cli_upper = str(cliente).upper()
    if "LUCAS" in cli_upper or "BIGODINHO" in cli_upper:
        return "CNPJ: 49.657.733/0001-92"
    if "JIMMY" in cli_upper:
        return "CNPJ: 30.514.229/0001-05"
    return f"CLIENTE: {cli_upper}"


def montar_txt_etiquetas(demandas, data_titulo=None):
    linhas = []
    if data_titulo:
        linhas.append(f"=== ETIQUETAS DO DIA: {data_titulo} ===\n")
    else:
        linhas.append("=== DADOS PARA IMPRESSÃO DE ETIQUETAS ===\n")

    for dem in demandas:
        linha_cli = linha_cliente_etiqueta(dem['cliente'])
        for it in dem.get('itens', []):
            tam = it['tam']
            cap = obter_capacidade(dem['cliente'], tam)
            linhas.append(f"NF: {dem['nf']}")
            linhas.append(linha_cli)
            linhas.append(f"MEDIDA: {tam}")
            linhas.append(f"QUANTIDADE: {cap} unidades")
            linhas.append("-" * 30)
    return "\n".join(linhas)


def render_metric(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_demand_header(d, etapas):
    marcadas, total, status_class, status_label = status_demanda(etapas)
    itens_html = "".join([f"<span class='item-pill'>{int(it['qtd'])}x {it['tam']}</span>" for it in d.get('itens', [])])
    st.markdown(
        f"""
        <div class="demand-card">
            <div class="demand-head">
                <div>
                    <div class="demand-client">{d['cliente']}</div>
                    <div class="demand-nf">NF: {d['nf']}</div>
                </div>
                <span class="status-badge {status_class}">{status_label} · {marcadas}/{total}</span>
            </div>
            <div>{itens_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# 📋 CABEÇALHO
# ==============================================================================
st.markdown(
    """
    <div class="eco-header">
        <div class="eco-title">ECO DECOR · DEMANDA DIÁRIA</div>
        <div class="eco-subtitle">Painel de acompanhamento de produção, etiquetas e entrega</div>
        <div class="mobile-note">Versão otimizada para celular</div>
    </div>
    """,
    unsafe_allow_html=True,
)

nav_ant, nav_data, nav_prox = st.columns([1, 3, 1], vertical_alignment="center")
if nav_ant.button("◀", key="btn_ant", use_container_width=True):
    st.session_state.data_foco -= datetime.timedelta(days=1)
    st.rerun()
nova_data = nav_data.date_input("Data da demanda", value=st.session_state.data_foco, format="DD/MM/YYYY", label_visibility="collapsed")
if nova_data != st.session_state.data_foco:
    st.session_state.data_foco = nova_data
    st.rerun()
if nav_prox.button("▶", key="btn_prox", use_container_width=True):
    st.session_state.data_foco += datetime.timedelta(days=1)
    st.rerun()

bd = carregar_bd()
data_str = st.session_state.data_foco.strftime("%Y-%m-%d")

# ------------------------------------------------------------------------------
# MODO: LISTA KANBAN
# ------------------------------------------------------------------------------
if st.session_state.modo_demanda == 'lista':
    demandas_do_dia = bd.get(data_str, [])
    demandas_do_dia.sort(key=lambda x: (x.get('ordem') if x.get('ordem') is not None else 999, x['id']))

    total_demandas = len(demandas_do_dia)
    total_quadros = sum(int(it.get('qtd', 0)) for dem in demandas_do_dia for it in dem.get('itens', []))
    total_caixas = sum(math.ceil(int(it.get('qtd', 0)) / obter_capacidade(dem['cliente'], it['tam'])) for dem in demandas_do_dia for it in dem.get('itens', []))
    finalizadas = sum(1 for dem in demandas_do_dia if sum(1 for v in dem.get('etapas', {}).values() if v) == len(ETAPAS_PRODUCAO))

    m1, m2, m3, m4 = st.columns(4)
    with m1: render_metric("Demandas", total_demandas)
    with m2: render_metric("Quadros", total_quadros)
    with m3: render_metric("Caixas", total_caixas)
    with m4: render_metric("Finalizadas", finalizadas)

    st.write("")
    c_topo1, c_topo2 = st.columns([1, 1])
    if c_topo1.button("➕ ADICIONAR NOVA DEMANDA", use_container_width=True):
        st.session_state.modo_demanda = 'nova'
        st.session_state.itens_temp = []
        st.session_state.demanda_edit = None
        st.rerun()

    if demandas_do_dia:
        conteudo_massa = montar_txt_etiquetas(demandas_do_dia, st.session_state.data_foco.strftime('%d/%m/%Y'))
        c_topo2.download_button(
            "📥 EXTRAIR ETIQUETAS DO DIA",
            data=conteudo_massa,
            file_name=f"ETIQUETAS_GERAL_{data_str}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.write("")

    if not demandas_do_dia:
        st.info(f"Nenhuma demanda para {st.session_state.data_foco.strftime('%d/%m/%Y')}.")
    else:
        for idx, d in enumerate(demandas_do_dia):
            etapas = d.get('etapas', {})
            render_demand_header(d, etapas)

            with st.expander("Abrir detalhes e etapas", expanded=False):
                st.markdown(f"**Cliente:** {d['cliente']}  ")
                st.markdown(f"**NF:** {d['nf']}")

                if isinstance(d.get('itens'), list) and len(d['itens']) > 0:
                    st.markdown("**📦 Medidas e caixas:**")
                    for it in d['itens']:
                        tam, qtd = it['tam'], int(it['qtd'])
                        cap = obter_capacidade(d['cliente'], tam)
                        caixas = math.ceil(qtd / cap)
                        txt_cx = "caixa" if caixas == 1 else "caixas"
                        st.markdown(f"- **{tam}** · {qtd} un · **{caixas} {txt_cx}** · Cap: {cap}/cx")

                if d.get('agendamento'):
                    st.markdown(f"<div class='info-line'>📅 <b>Agendamento:</b> {d['agendamento']}</div>", unsafe_allow_html=True)
                if d.get('referencia'):
                    st.markdown(f"<div class='info-line'>📝 <b>Referência:</b> {d['referencia']}</div>", unsafe_allow_html=True)

                st.write("---")
                st.markdown("**Etapas da produção**")
                mudou_algo = False
                etapa_cols = st.columns(3)
                for i, etapa in enumerate(ETAPAS_PRODUCAO):
                    with etapa_cols[i % 3]:
                        v = st.checkbox(etapa, value=etapas.get(etapa, False), key=f"c{d['id']}{i}")
                    if v != etapas.get(etapa, False):
                        etapas[etapa] = v
                        mudou_algo = True
                if mudou_algo:
                    supabase.table("demandas").update({"etapas": etapas}).eq("id", d['id']).execute()
                    st.rerun()

                st.write("---")
                st.markdown("**Ações**")
                a1, a2, a3 = st.columns(3)
                b1, b2 = st.columns(2)
                if a1.button("✏️ Editar", key=f"ed_{d['id']}"):
                    st.session_state.modo_demanda = 'editar'
                    st.session_state.demanda_edit = d
                    st.session_state.itens_temp = d['itens'] if isinstance(d['itens'], list) else []
                    st.rerun()
                if a2.button("🗑️ Excluir", key=f"del_{d['id']}"):
                    supabase.table("demandas").delete().eq("id", d['id']).execute()
                    st.rerun()
                if a3.button("📄 Extrair", key=f"etq_{d['id']}"):
                    st.session_state.demanda_etiqueta = d
                    st.session_state.modo_demanda = 'etiquetas'
                    st.rerun()
                if b1.button("⬆️ Subir", key=f"up_{d['id']}"):
                    if idx > 0:
                        mover_demanda(d, demandas_do_dia[idx-1], idx, idx-1)
                if b2.button("⬇️ Descer", key=f"down_{d['id']}"):
                    if idx < len(demandas_do_dia) - 1:
                        mover_demanda(d, demandas_do_dia[idx+1], idx, idx+1)

# ------------------------------------------------------------------------------
# MODO: GERADOR DE TXT PARA ETIQUETAS INDIVIDUAL
# ------------------------------------------------------------------------------
elif st.session_state.modo_demanda == 'etiquetas':
    d = st.session_state.demanda_etiqueta
    st.markdown("<div class='section-card'><h3>📄 Dados para etiquetas</h3></div>", unsafe_allow_html=True)
    st.info(f"Cliente original: **{d['cliente']}** | NF: **{d['nf']}**")

    conteudo_txt = montar_txt_etiquetas([d])

    with st.container(border=True):
        st.write("📦 **Resumo para o arquivo:**")
        for it in d.get('itens', []):
            tam = it['tam']
            cap = obter_capacidade(d['cliente'], tam)
            st.write(f"- {tam} → quantidade da etiqueta: **{cap} unidades**")

        st.write("---")
        st.text_area("Preview do TXT", conteudo_txt, height=260)
        st.download_button(
            "📥 BAIXAR DOCUMENTO DE TEXTO (.TXT)",
            data=conteudo_txt,
            file_name=f"DADOS_ETIQUETA_NF_{d['nf']}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if st.button("❌ VOLTAR AO PAINEL", use_container_width=True):
        st.session_state.modo_demanda = 'lista'
        st.rerun()

# ------------------------------------------------------------------------------
# MODO: NOVA OU EDITAR DEMANDA
# ------------------------------------------------------------------------------
elif st.session_state.modo_demanda in ['nova', 'editar']:
    is_edit = st.session_state.modo_demanda == 'editar'
    d_edit = st.session_state.demanda_edit if is_edit else {}
    st.markdown(f"<div class='section-card'><h3>{'✏️ Editar Demanda' if is_edit else '➕ Nova Demanda'}</h3></div>", unsafe_allow_html=True)

    with st.container(border=True):
        f1, f2 = st.columns([2, 1])
        with f1:
            cli_d = st.text_input("Nome do cliente:", value=d_edit.get('cliente', '')).strip().upper()
        with f2:
            nf_d = st.text_input("Número da NF:", value=d_edit.get('nf', '')).strip().upper()

        nf_duplicada = False
        if nf_d:
            if not is_edit or (is_edit and nf_d != d_edit.get('nf', '').upper()):
                try:
                    busca = supabase.table("demandas").select("id").eq("nf", nf_d).execute()
                    if len(busca.data) > 0:
                        nf_duplicada = True
                        st.error("⚠️ Este número de NF já foi utilizado!")
                except Exception:
                    pass

        st.write("📦 **Itens da demanda:**")
        if st.session_state.itens_temp:
            for i, item in enumerate(st.session_state.itens_temp):
                c_it1, c_it2 = st.columns([5, 1])
                c_it1.markdown(f"<span class='item-pill'>{item['qtd']} unidades · {item['tam']}</span>", unsafe_allow_html=True)
                if c_it2.button("🗑️", key=f"rem_item_{i}"):
                    st.session_state.itens_temp.pop(i)
                    st.rerun()
        else:
            st.caption("Nenhuma medida adicionada ainda.")

        st.write("---")
        c_m1, c_m2, c_m3 = st.columns([2, 2, 2])
        t_med = c_m1.selectbox("Medida:", ["30x40", "60x40", "90x60"])
        t_qtd = c_m2.number_input("QTD:", min_value=1, value=1)
        if c_m3.button("➕ Adicionar Medida", use_container_width=True):
            st.session_state.itens_temp.append({"tam": t_med, "qtd": t_qtd})
            st.rerun()

        st.write("---")
        txt_agend = st.text_input("Agendamento:", value=d_edit.get('agendamento', '')).strip().upper()
        txt_ref = st.text_area("Referência:", value=d_edit.get('referencia', '')).strip().upper()

        c_salvar, c_voltar = st.columns(2)
        if c_salvar.button("✅ SALVAR NA NUVEM", use_container_width=True):
            if nf_duplicada:
                st.error("⚠️ Corrija o número da NF antes de salvar. Essa nota já existe no sistema!")
            elif cli_d and nf_d and len(st.session_state.itens_temp) > 0:
                dados = {
                    "data": st.session_state.data_foco.strftime("%Y-%m-%d") if not is_edit else d_edit['data'],
                    "cliente": cli_d,
                    "nf": nf_d,
                    "itens": st.session_state.itens_temp,
                    "agendamento": txt_agend,
                    "referencia": txt_ref,
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
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.warning("⚠️ Preencha Nome, NF e adicione uma medida!")

        if c_voltar.button("❌ VOLTAR", use_container_width=True):
            st.session_state.modo_demanda = 'lista'
            st.session_state.itens_temp = []
            st.rerun()
