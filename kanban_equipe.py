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

st.markdown("""
<style>
    :root {
        --bg: #0b0f17;
        --panel: #121826;
        --panel-2: #172033;
        --border: #263247;
        --text: #f8fafc;
        --muted: #94a3b8;
        --blue: #5d7cf3;
        --blue-2: #3b5bdb;
        --green: #22c55e;
        --yellow: #f59e0b;
        --red: #ef4444;
    }

    .stApp {
        background: radial-gradient(circle at top left, #172033 0, #0b0f17 38%, #070a10 100%);
        color: var(--text);
    }

    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: var(--text);
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1480px;
    }

    div[data-testid="stHeader"] {
        background: transparent;
    }

    .hero {
        background: linear-gradient(135deg, rgba(31,78,121,.95), rgba(18,24,38,.95));
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 22px;
        padding: 22px 28px;
        box-shadow: 0 18px 45px rgba(0,0,0,.28);
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 30px;
        font-weight: 900;
        letter-spacing: .5px;
        margin: 0;
    }

    .hero-subtitle {
        color: #cbd5e1;
        font-size: 14px;
        margin-top: 4px;
    }

    .date-pill {
        background: rgba(255,255,255,.08);
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 14px;
        padding: 12px 16px;
        text-align: center;
        font-weight: 800;
    }

    .metric-card {
        background: rgba(18,24,38,.96);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 18px;
        min-height: 100px;
        box-shadow: 0 10px 24px rgba(0,0,0,.20);
    }

    .metric-label {
        color: var(--muted);
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: .7px;
        font-weight: 800;
    }

    .metric-value {
        font-size: 34px;
        font-weight: 900;
        margin-top: 4px;
    }

    .section-card {
        background: rgba(18,24,38,.94);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 14px 30px rgba(0,0,0,.20);
        margin-bottom: 16px;
    }

    .card-title {
        font-size: 18px;
        font-weight: 900;
        margin-bottom: 8px;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 7px 11px;
        border-radius: 999px;
        font-weight: 900;
        font-size: 13px;
        border: 1px solid rgba(255,255,255,.10);
    }

    .pendente { background-color: rgba(239,68,68,.16); color: #fecaca; }
    .andamento { background-color: rgba(245,158,11,.16); color: #fde68a; }
    .finalizado { background-color: rgba(34,197,94,.16); color: #bbf7d0; }

    .demand-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 14px;
        margin-bottom: 12px;
    }

    .demand-client {
        font-size: 17px;
        font-weight: 900;
    }

    .demand-meta {
        color: var(--muted);
        font-size: 13px;
        margin-top: 3px;
    }

    .item-chip {
        display: inline-block;
        background: rgba(93,124,243,.14);
        border: 1px solid rgba(93,124,243,.28);
        border-radius: 999px;
        padding: 6px 10px;
        margin: 3px 4px 3px 0;
        font-size: 13px;
        font-weight: 800;
        color: #dbeafe;
    }

    .info-line {
        color: #cbd5e1;
        font-size: 14px;
        margin: 4px 0;
    }

    .small-muted {
        color: var(--muted);
        font-size: 13px;
    }

    div.stButton > button, div.stDownloadButton > button {
        width: 100%;
        min-height: 45px;
        background: linear-gradient(135deg, var(--blue), var(--blue-2)) !important;
        color: white !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        border: 0 !important;
        box-shadow: 0 8px 18px rgba(59,91,219,.25);
    }

    div.stButton > button:hover, div.stDownloadButton > button:hover {
        filter: brightness(1.08);
        transform: translateY(-1px);
    }

    .danger button {
        background: linear-gradient(135deg, #ef4444, #991b1b) !important;
    }

    div[data-testid="stExpander"] {
        background: rgba(18,24,38,.94);
        border: 1px solid var(--border);
        border-radius: 18px;
        overflow: hidden;
        margin-bottom: 14px;
        box-shadow: 0 12px 28px rgba(0,0,0,.18);
    }

    div[data-testid="stExpander"] summary {
        font-weight: 900;
        padding: 14px 18px;
    }

    div[data-testid="stExpander"] details {
        border: none;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stDateInput"] input,
    div[data-baseweb="select"] > div {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }

    .stCheckbox label span {
        color: #e2e8f0 !important;
        font-weight: 700;
    }

    hr {
        border-color: rgba(148,163,184,.22);
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
    elif tam == "60x40":
        return 24
    elif tam == "30x40":
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


def calcular_resumo(demandas):
    total_demandas = len(demandas)
    total_quadros = 0
    total_caixas = 0
    pendentes = 0
    andamento = 0
    finalizadas = 0

    for d in demandas:
        etapas = d.get('etapas', {})
        marcadas = sum(1 for v in etapas.values() if v)
        if marcadas == 0:
            pendentes += 1
        elif marcadas == len(ETAPAS_PRODUCAO):
            finalizadas += 1
        else:
            andamento += 1

        for it in d.get('itens', []):
            qtd = int(it.get('qtd', 0))
            tam = it.get('tam', '')
            total_quadros += qtd
            total_caixas += math.ceil(qtd / obter_capacidade(d.get('cliente', ''), tam))

    return total_demandas, total_quadros, total_caixas, pendentes, andamento, finalizadas


def linha_cliente_etiqueta(cliente):
    cli_upper = str(cliente).upper()
    if "LUCAS" in cli_upper or "BIGODINHO" in cli_upper:
        return "CNPJ: 49.657.733/0001-92"
    if "JIMMY" in cli_upper:
        return "CNPJ: 30.514.229/0001-05"
    return f"CLIENTE: {cli_upper}"


def gerar_txt_etiquetas(demandas, titulo):
    linhas = [titulo, ""]
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


def render_metric(label, value, hint=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="small-muted">{hint}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# 📋 CABEÇALHO
# ==============================================================================
bd = carregar_bd()
data_str = st.session_state.data_foco.strftime("%Y-%m-%d")
demandas_do_dia_header = bd.get(data_str, [])
qtd_header = len(demandas_do_dia_header)

st.markdown(
    f"""
    <div class="hero">
        <div style="display:flex; justify-content:space-between; align-items:center; gap:20px; flex-wrap:wrap;">
            <div>
                <div class="hero-title">ECO DECOR · DEMANDA DIÁRIA</div>
                <div class="hero-subtitle">Painel de acompanhamento de produção, etiquetas, arte, corte, nota fiscal e entrega.</div>
            </div>
            <div class="date-pill">
                {st.session_state.data_foco.strftime('%d/%m/%Y')}<br>
                <span style="color:#cbd5e1; font-size:12px;">{qtd_header} demanda(s) no dia</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

nav_1, nav_2, nav_3, nav_4, nav_5 = st.columns([1, 1, 2, 1, 1], vertical_alignment="center")
if nav_2.button("◀ DIA ANTERIOR", key="btn_ant"):
    st.session_state.data_foco -= datetime.timedelta(days=1)
    st.rerun()
nova_data = nav_3.date_input("Data da demanda", value=st.session_state.data_foco, format="DD/MM/YYYY", label_visibility="collapsed")
if nova_data != st.session_state.data_foco:
    st.session_state.data_foco = nova_data
    st.rerun()
if nav_4.button("PRÓXIMO DIA ▶", key="btn_prox"):
    st.session_state.data_foco += datetime.timedelta(days=1)
    st.rerun()

st.divider()

# ------------------------------------------------------------------------------
# MODO: LISTA KANBAN
# ------------------------------------------------------------------------------
if st.session_state.modo_demanda == 'lista':
    demandas_do_dia = bd.get(data_str, [])
    demandas_do_dia.sort(key=lambda x: (x.get('ordem') if x.get('ordem') is not None else 999, x['id']))

    total_demandas, total_quadros, total_caixas, pendentes, andamento, finalizadas = calcular_resumo(demandas_do_dia)

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1: render_metric("Demandas", total_demandas, "cards do dia")
    with m2: render_metric("Quadros", total_quadros, "unidades totais")
    with m3: render_metric("Caixas", total_caixas, "estimativa")
    with m4: render_metric("Pendentes", pendentes, "sem etapa marcada")
    with m5: render_metric("Andamento", andamento, "produção ativa")
    with m6: render_metric("Finalizadas", finalizadas, "liberadas")

    st.write("")
    c_topo1, c_topo2 = st.columns([1, 1])
    if c_topo1.button("➕ ADICIONAR NOVA DEMANDA", use_container_width=True):
        st.session_state.modo_demanda = 'nova'
        st.session_state.itens_temp = []
        st.session_state.demanda_edit = None
        st.rerun()

    if demandas_do_dia:
        conteudo_massa = gerar_txt_etiquetas(
            demandas_do_dia,
            f"=== ETIQUETAS DO DIA: {st.session_state.data_foco.strftime('%d/%m/%Y')} ==="
        )
        c_topo2.download_button(
            "📥 EXTRAIR TODAS AS ETIQUETAS DO DIA",
            data=conteudo_massa,
            file_name=f"ETIQUETAS_GERAL_{data_str}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    else:
        c_topo2.button("📥 EXTRAIR TODAS AS ETIQUETAS DO DIA", disabled=True, use_container_width=True)

    st.write("")

    if not demandas_do_dia:
        st.info(f"Nenhuma demanda para {st.session_state.data_foco.strftime('%d/%m/%Y')}.")
    else:
        st.markdown("<div class='card-title'>📋 Demandas cadastradas</div>", unsafe_allow_html=True)

        for idx, d in enumerate(demandas_do_dia):
            etapas = d.get('etapas', {})
            marcadas = sum(1 for v in etapas.values() if v)
            if marcadas == len(ETAPAS_PRODUCAO):
                status_class = "finalizado"
                status_txt = "🟢 Finalizado"
            elif marcadas > 0:
                status_class = "andamento"
                status_txt = "🟡 Em andamento"
            else:
                status_class = "pendente"
                status_txt = "🔴 Pendente"

            medidas_str = " · ".join([f"{it['qtd']}x {it['tam']}" for it in d.get('itens', [])])
            titulo_expander = f"{d['cliente']} · NF {d['nf']} · {medidas_str}"

            with st.expander(titulo_expander):
                st.markdown(
                    f"""
                    <div class="demand-header">
                        <div>
                            <div class="demand-client">{d['cliente']}</div>
                            <div class="demand-meta">NF: {d['nf']} · Progresso: {marcadas}/{len(ETAPAS_PRODUCAO)}</div>
                        </div>
                        <span class="status-badge {status_class}">{status_txt}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if isinstance(d.get('itens'), list) and len(d.get('itens', [])) > 0:
                    st.markdown("<div class='small-muted'>Medidas e caixas estimadas</div>", unsafe_allow_html=True)
                    chips = []
                    for it in d['itens']:
                        tam, qtd = it['tam'], int(it['qtd'])
                        cap = obter_capacidade(d['cliente'], tam)
                        caixas = math.ceil(qtd / cap)
                        chips.append(f"<span class='item-chip'>{qtd} un · {tam} · {caixas} cx</span>")
                    st.markdown("".join(chips), unsafe_allow_html=True)

                if d.get('agendamento'):
                    st.markdown(f"<div class='info-line'>📅 <b>Agendamento:</b> {d['agendamento']}</div>", unsafe_allow_html=True)
                if d.get('referencia'):
                    st.markdown(f"<div class='info-line'>📝 <b>Referência:</b> {d['referencia']}</div>", unsafe_allow_html=True)

                st.divider()
                st.markdown("<div class='small-muted'>Etapas da produção</div>", unsafe_allow_html=True)
                mudou_algo = False
                colunas_etapas = st.columns(3)
                for i, etapa in enumerate(ETAPAS_PRODUCAO):
                    with colunas_etapas[i % 3]:
                        v = st.checkbox(etapa, value=etapas.get(etapa, False), key=f"c{d['id']}{i}")
                    if v != etapas.get(etapa, False):
                        etapas[etapa] = v
                        mudou_algo = True
                if mudou_algo:
                    supabase.table("demandas").update({"etapas": etapas}).eq("id", d['id']).execute()
                    st.rerun()

                st.divider()
                c1, c2, c3, c4, c5 = st.columns(5)
                if c1.button("✏️ Editar", key=f"ed_{d['id']}"):
                    st.session_state.modo_demanda = 'editar'
                    st.session_state.demanda_edit = d
                    st.session_state.itens_temp = d['itens'] if isinstance(d['itens'], list) else []
                    st.rerun()
                if c2.button("🗑️ Excluir", key=f"del_{d['id']}"):
                    supabase.table("demandas").delete().eq("id", d['id']).execute()
                    st.rerun()
                if c3.button("⬆️ Subir", key=f"up_{d['id']}"):
                    if idx > 0:
                        mover_demanda(d, demandas_do_dia[idx-1], idx, idx-1)
                if c4.button("⬇️ Descer", key=f"down_{d['id']}"):
                    if idx < len(demandas_do_dia) - 1:
                        mover_demanda(d, demandas_do_dia[idx+1], idx, idx+1)
                if c5.button("📄 Extrair", key=f"etq_{d['id']}"):
                    st.session_state.demanda_etiqueta = d
                    st.session_state.modo_demanda = 'etiquetas'
                    st.rerun()

# ------------------------------------------------------------------------------
# MODO: GERADOR DE TXT PARA ETIQUETAS (INDIVIDUAL)
# ------------------------------------------------------------------------------
elif st.session_state.modo_demanda == 'etiquetas':
    d = st.session_state.demanda_etiqueta
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='card-title'>📄 Dados para etiquetas · NF {d['nf']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='small-muted'>Cliente original: {d['cliente']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.write("📦 **Resumo para o arquivo:**")
        conteudo_txt = gerar_txt_etiquetas([d], "=== DADOS PARA IMPRESSÃO DE ETIQUETAS ===")
        for it in d.get('itens', []):
            tam = it['tam']
            cap = obter_capacidade(d['cliente'], tam)
            st.write(f"- **{tam}** → etiqueta com **{cap} unidades**")

        st.code(conteudo_txt, language="text")
        st.download_button(
            "📥 BAIXAR DOCUMENTO DE TEXTO (.TXT)",
            data=conteudo_txt,
            file_name=f"DADOS_ETIQUETA_NF_{d['nf']}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    if st.button("❌ VOLTAR AO PAINEL"):
        st.session_state.modo_demanda = 'lista'
        st.rerun()

# ------------------------------------------------------------------------------
# MODO: NOVA OU EDITAR DEMANDA
# ------------------------------------------------------------------------------
elif st.session_state.modo_demanda in ['nova', 'editar']:
    is_edit = st.session_state.modo_demanda == 'editar'
    d_edit = st.session_state.demanda_edit if is_edit else {}

    st.markdown(
        f"""
        <div class="section-card">
            <div class="card-title">{'✏️ Editar Demanda' if is_edit else '➕ Nova Demanda'}</div>
            <div class="small-muted">Preencha cliente, NF, medidas, agendamento e referência.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        c_form1, c_form2 = st.columns([2, 1])
        cli_d = c_form1.text_input("Nome do cliente:", value=d_edit.get('cliente', '')).strip().upper()
        nf_d = c_form2.text_input("Número da NF:", value=d_edit.get('nf', '')).strip().upper()

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

        st.divider()
        st.write("📦 **Itens da demanda:**")
        if not st.session_state.itens_temp:
            st.caption("Nenhuma medida adicionada ainda.")
        for i, item in enumerate(st.session_state.itens_temp):
            c_it1, c_it2 = st.columns([5, 1])
            c_it1.markdown(f"<span class='item-chip'>{item['qtd']} unidades · {item['tam']}</span>", unsafe_allow_html=True)
            if c_it2.button("🗑️", key=f"rem_item_{i}"):
                st.session_state.itens_temp.pop(i)
                st.rerun()

        st.write("")
        c_m1, c_m2, c_m3 = st.columns([2, 2, 2])
        t_med = c_m1.selectbox("Medida:", ["30x40", "60x40", "90x60"])
        t_qtd = c_m2.number_input("QTD:", min_value=1, value=1)
        if c_m3.button("➕ Adicionar Medida"):
            st.session_state.itens_temp.append({"tam": t_med, "qtd": t_qtd})
            st.rerun()

        st.divider()
        txt_agend = st.text_input("Agendamento:", value=d_edit.get('agendamento', '')).strip().upper()
        txt_ref = st.text_area("Referência:", value=d_edit.get('referencia', '')).strip().upper()

        c_salvar, c_voltar = st.columns(2)
        if c_salvar.button("✅ SALVAR NA NUVEM"):
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

        if c_voltar.button("❌ VOLTAR"):
            st.session_state.modo_demanda = 'lista'
            st.session_state.itens_temp = []
            st.rerun()
