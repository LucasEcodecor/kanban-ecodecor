import streamlit as st
import datetime
import math
from supabase import create_client, Client

# ==============================================================================
# 🚀 ECO DECOR - DEMANDA DIÁRIA | V6 TURBO MOBILE
# Melhorias focadas em velocidade + uso no celular:
# - Busca apenas a data selecionada no Supabase
# - Cache curto da data atual
# - Paginação de cards
# - Etapas salvas em lote dentro de formulário
# - TXT geral de etiquetas gerado apenas quando solicitado
# - Formulários para reduzir reruns desnecessários
# - Layout responsivo para produção usar no celular
# ==============================================================================

st.set_page_config(
    page_title="ECO DECOR - Demanda diária",
    page_icon="ECO TRANSPARENTE Logo Nova.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    h1, h2, h3, h4 { color: #fafafa !important; }

    .main-header {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 1px solid #2f3542;
        border-radius: 18px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    }
    .main-title { font-size: 30px; font-weight: 900; margin: 0; letter-spacing: .3px; }
    .main-subtitle { color: #cbd5e1; margin-top: 6px; font-size: 15px; }

    .metric-card {
        background-color: #151a23;
        border: 1px solid #2d3748;
        border-radius: 14px;
        padding: 14px 16px;
        min-height: 86px;
    }
    .metric-label { color: #94a3b8; font-size: 13px; font-weight: 700; }
    .metric-value { color: #ffffff; font-size: 26px; font-weight: 900; margin-top: 5px; }

    .demand-card {
        background-color: #151a23;
        border: 1px solid #2d3748;
        border-radius: 16px;
        padding: 12px 14px;
        margin-bottom: 10px;
    }
    .demand-title { font-size: 17px; font-weight: 900; color: #f8fafc; }
    .demand-meta { color: #cbd5e1; font-size: 13px; margin-top: 4px; }
    .status-badge {
        display:inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        font-weight: 900;
        font-size: 13px;
        margin: 6px 0;
    }
    .pendente { background-color: #451a1a; color: #fecaca; border: 1px solid #7f1d1d; }
    .andamento { background-color: #422006; color: #fde68a; border: 1px solid #92400e; }
    .finalizado { background-color: #052e16; color: #bbf7d0; border: 1px solid #166534; }

    div.stButton > button, div.stDownloadButton > button {
        width: 100%;
        min-height: 44px;
        background-color: #3157d5 !important;
        color: white !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background-color: #2445ad !important;
        color: white !important;
    }

    .soft-box {
        background-color: #111827;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 14px;
    }

    .alert-box {
        background-color: #111827;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 12px 14px;
        margin: 8px 0;
    }
    .alert-title {
        color: #f8fafc;
        font-size: 15px;
        font-weight: 900;
        margin-bottom: 4px;
    }
    .alert-meta {
        color: #cbd5e1;
        font-size: 12.5px;
        line-height: 1.35;
    }
    .alert-critico { border-color: #dc2626; }
    .alert-atencao { border-color: #eab308; }
    .alert-info { border-color: #2563eb; }

    /* ===============================================================
       📱 AJUSTES RESPONSIVOS PARA CELULAR
       Mantém o desktop largo, mas empilha colunas no telefone.
       =============================================================== */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-top: 2.25rem !important;
            max-width: 100% !important;
        }

        .main-header {
            padding: 16px 14px 18px 14px;
            border-radius: 14px;
            margin-top: 12px;
            margin-bottom: 14px;
            overflow: visible !important;
        }
        .main-title {
            display: block;
            font-size: 19px;
            line-height: 1.35;
            white-space: normal;
            word-break: normal;
            overflow: visible !important;
        }
        .main-subtitle {
            display: block;
            font-size: 12.5px;
            line-height: 1.45;
            margin-top: 8px;
            overflow: visible !important;
        }

        /* Força os blocos horizontais do Streamlit a virarem coluna no celular */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.45rem !important;
        }
        div[data-testid="column"] {
            min-width: 100% !important;
            width: 100% !important;
            flex: 1 1 100% !important;
        }

        .metric-card {
            min-height: 64px;
            padding: 10px 12px;
            margin-bottom: 6px;
            border-radius: 12px;
        }
        .metric-label { font-size: 12px; }
        .metric-value { font-size: 22px; }

        .demand-card {
            padding: 12px;
            border-radius: 14px;
            margin-bottom: 12px;
        }
        .demand-title {
            font-size: 16px;
            line-height: 1.25;
        }
        .demand-meta {
            font-size: 12.5px;
            line-height: 1.35;
        }
        .status-badge {
            font-size: 12px;
            padding: 5px 9px;
        }

        div.stButton > button, div.stDownloadButton > button {
            min-height: 50px;
            font-size: 14px !important;
            border-radius: 12px !important;
            margin-top: 4px;
        }

        div[data-testid="stExpander"] {
            border-radius: 12px !important;
        }

        textarea, input, select {
            font-size: 16px !important; /* evita zoom automático no iPhone */
        }
    }

    @media (min-width: 769px) {
        .block-container {
            padding-top: 1.25rem !important;
            max-width: 1400px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# ⚙️ CONFIGURAÇÕES
# ==============================================================================
URL_SUPABASE = "https://amnjfpettwnrhszgdpyk.supabase.co"
CHAVE_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFtbmpmcGV0dHducmhzemdkcHlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2MDY0MjUsImV4cCI6MjA5NDE4MjQyNX0.WHbyxzceCNo1_btFkpwM0nov4I73zqiSa4taYkH6msc"

ETAPAS_PRODUCAO = [
    "ETIQUETAS (LUCAS)",
    "ARTE (TALLES/LUCAS)",
    "IMPRESSÃO (TALLES)",
    "CORTE EM ANDAMENTO (DAVID)",
    "CORTE FINALIZADO (DAVID)",
    "PRODUÇÃO EM ANDAMENTO (SASKA)",
    "PRODUÇÃO FINALIZADO (SASKA)",
    "NOTA FISCAL (MICHELLI)",
    "LIBERADO PARA ENTREGA (MICHELLI)",
]

try:
    supabase: Client = create_client(URL_SUPABASE, CHAVE_SUPABASE)
except Exception as e:
    st.error(f"Erro ao inicializar o Supabase: {e}")
    st.stop()

# ==============================================================================
# 🧠 SESSION STATE
# ==============================================================================
if "data_foco" not in st.session_state:
    st.session_state.data_foco = datetime.date.today() + datetime.timedelta(days=1)
if "modo_demanda" not in st.session_state:
    st.session_state.modo_demanda = "lista"
if "itens_temp" not in st.session_state:
    st.session_state.itens_temp = []
if "demanda_edit" not in st.session_state:
    st.session_state.demanda_edit = None
if "demanda_etiqueta" not in st.session_state:
    st.session_state.demanda_etiqueta = None
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = 1
if "mostrar_txt_geral" not in st.session_state:
    st.session_state.mostrar_txt_geral = False

# ==============================================================================
# 🧰 FUNÇÕES
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


def linha_cliente_etiqueta(cliente):
    cli_upper = str(cliente).upper()
    if "LUCAS" in cli_upper or "BIGODINHO" in cli_upper:
        return "CNPJ: 49.657.733/0001-92"
    if "JIMMY" in cli_upper:
        return "CNPJ: 30.514.229/0001-05"
    return f"CLIENTE: {cli_upper}"


def gerar_txt_etiquetas(demandas, data_label=None):
    linhas = []
    if data_label:
        linhas.append(f"=== ETIQUETAS DO DIA: {data_label} ===\n")
    else:
        linhas.append("=== DADOS PARA IMPRESSÃO DE ETIQUETAS ===\n")

    for dem in demandas:
        linha_cli = linha_cliente_etiqueta(dem.get("cliente", ""))
        for it in dem.get("itens", []) or []:
            tam = it.get("tam", "")
            cap = obter_capacidade(dem.get("cliente", ""), tam)
            linhas.append(f"NF: {dem.get('nf', '')}")
            linhas.append(linha_cli)
            linhas.append(f"MEDIDA: {tam}")
            linhas.append(f"QUANTIDADE: {cap} unidades")
            linhas.append("-" * 30)
    return "\n".join(linhas)


def total_quadros(demandas):
    total = 0
    for d in demandas:
        for it in d.get("itens", []) or []:
            try:
                total += int(it.get("qtd", 0))
            except Exception:
                pass
    return total


def total_caixas(demandas):
    caixas = 0
    for d in demandas:
        for it in d.get("itens", []) or []:
            try:
                qtd = int(it.get("qtd", 0))
                cap = obter_capacidade(d.get("cliente", ""), it.get("tam", ""))
                caixas += math.ceil(qtd / cap) if cap else 0
            except Exception:
                pass
    return caixas


def status_demanda(d):
    etapas = d.get("etapas", {}) or {}
    marcadas = sum(1 for etapa in ETAPAS_PRODUCAO if etapas.get(etapa, False))
    if marcadas == len(ETAPAS_PRODUCAO):
        return "finalizado", "🟢", marcadas
    if marcadas > 0:
        return "andamento", "🟡", marcadas
    return "pendente", "🔴", marcadas


@st.cache_data(ttl=20, show_spinner=False)
def carregar_demandas_data(data_str):
    resposta = (
        supabase.table("demandas")
        .select("*")
        .eq("data", data_str)
        .order("ordem", desc=False)
        .execute()
    )
    dados = resposta.data or []
    dados.sort(key=lambda x: (x.get("ordem") if x.get("ordem") is not None else 999, x.get("id", 0)))
    return dados


def limpar_cache():
    carregar_demandas_data.clear()


def voltar_lista():
    st.session_state.modo_demanda = "lista"
    st.session_state.demanda_edit = None
    st.session_state.demanda_etiqueta = None
    st.session_state.itens_temp = []
    st.session_state.mostrar_txt_geral = False


def mover_demanda(d_atual, d_alvo, idx_atual, idx_alvo):
    ordem_atual = d_atual.get("ordem") if d_atual.get("ordem") is not None else idx_atual
    ordem_alvo = d_alvo.get("ordem") if d_alvo.get("ordem") is not None else idx_alvo
    if ordem_atual == ordem_alvo:
        ordem_atual, ordem_alvo = idx_atual, idx_alvo
    try:
        supabase.table("demandas").update({"ordem": ordem_alvo}).eq("id", d_atual["id"]).execute()
        supabase.table("demandas").update({"ordem": ordem_atual}).eq("id", d_alvo["id"]).execute()
        limpar_cache()
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao mover card: {e}")


def excluir_demanda(d):
    try:
        supabase.table("demandas").delete().eq("id", d["id"]).execute()
        limpar_cache()
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao excluir: {e}")


def validar_nf_duplicada(nf, is_edit=False, id_atual=None):
    if not nf:
        return False
    try:
        busca = supabase.table("demandas").select("id").eq("nf", nf).execute()
        for item in busca.data or []:
            if not is_edit or item.get("id") != id_atual:
                return True
    except Exception:
        return False
    return False


def _texto_medidas(demanda):
    partes = []
    for item in demanda.get("itens", []) or []:
        tam = item.get("tam", "")
        qtd = item.get("qtd", "")
        if tam or qtd:
            partes.append(f"{tam} ({qtd})")
    return ", ".join(partes) if partes else "sem medidas"


def _data_demanda(demanda):
    try:
        return datetime.datetime.strptime(str(demanda.get("data", "")), "%Y-%m-%d").date()
    except Exception:
        return None


def gerar_alertas_demandas(demandas, data_referencia):
    """Gera alertas visuais locais. Não altera dados no Supabase."""
    hoje = datetime.date.today()
    alertas = []

    for demanda in demandas:
        classe, _, marcadas = status_demanda(demanda)
        concluida = classe == "finalizado"
        data_demanda = _data_demanda(demanda) or data_referencia
        cliente = str(demanda.get("cliente", "") or "SEM CLIENTE")
        nf = str(demanda.get("nf", "") or "SEM NF")
        medidas = _texto_medidas(demanda)

        if not demanda.get("cliente") or not demanda.get("nf") or not demanda.get("itens"):
            alertas.append({
                "nivel": "critico",
                "titulo": f"Cadastro incompleto — NF {nf}",
                "texto": f"{cliente} • {medidas}. Confira cliente, NF e medidas antes de produzir.",
            })

        if data_demanda < hoje and not concluida:
            alertas.append({
                "nivel": "critico",
                "titulo": f"Atrasada — NF {nf}",
                "texto": f"{cliente} • {medidas} • {marcadas}/{len(ETAPAS_PRODUCAO)} etapas concluídas.",
            })
        elif data_demanda == hoje and not concluida:
            alertas.append({
                "nivel": "atencao",
                "titulo": f"Para hoje — NF {nf}",
                "texto": f"{cliente} • {medidas} • falta finalizar etapas de produção.",
            })

        if demanda.get("agendamento"):
            alertas.append({
                "nivel": "info",
                "titulo": f"Agendamento — NF {nf}",
                "texto": f"{cliente} • {demanda.get('agendamento')} • {medidas}.",
            })

        if 0 < marcadas < len(ETAPAS_PRODUCAO):
            faltantes = [
                etapa for etapa in ETAPAS_PRODUCAO
                if not (demanda.get("etapas", {}) or {}).get(etapa, False)
            ][:3]
            alertas.append({
                "nivel": "info",
                "titulo": f"Em andamento — NF {nf}",
                "texto": f"{cliente} • próximas etapas: {', '.join(faltantes)}.",
            })

    prioridade = {"critico": 0, "atencao": 1, "info": 2}
    alertas.sort(key=lambda item: prioridade.get(item["nivel"], 9))
    return alertas


def mostrar_painel_alertas(alertas):
    criticos = sum(1 for item in alertas if item["nivel"] == "critico")
    atencao = sum(1 for item in alertas if item["nivel"] == "atencao")
    infos = sum(1 for item in alertas if item["nivel"] == "info")

    with st.expander(
        f"🔔 Alertas do dia — {len(alertas)} aviso(s)",
        expanded=bool(criticos or atencao),
    ):
        if not alertas:
            st.success("Nenhum alerta importante para esta data.")
            return

        c1, c2, c3 = st.columns(3)
        c1.metric("Críticos", criticos)
        c2.metric("Atenção", atencao)
        c3.metric("Informativos", infos)

        for alerta in alertas[:12]:
            classe = {
                "critico": "alert-critico",
                "atencao": "alert-atencao",
                "info": "alert-info",
            }.get(alerta["nivel"], "alert-info")
            st.markdown(
                f"""
                <div class="alert-box {classe}">
                    <div class="alert-title">{alerta["titulo"]}</div>
                    <div class="alert-meta">{alerta["texto"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if len(alertas) > 12:
            st.caption(f"Mostrando 12 de {len(alertas)} alertas. Abra os cards para ver o restante.")

# ==============================================================================
# 📋 CABEÇALHO
# ==============================================================================
st.markdown(
    """
    <div class="main-header">
        <div class="main-title">ECO DECOR<br><span style="font-size:0.92em; color:#e5e7eb;">DEMANDA DIÁRIA</span></div>
        <div class="main-subtitle">Painel otimizado para produção, etiquetas, celular e acompanhamento de etapas.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

nav1, nav2, nav3, nav4, nav5 = st.columns([1, 1, 2, 1, 1], vertical_alignment="center")
if nav2.button("◀ Anterior", key="btn_ant"):
    st.session_state.data_foco -= datetime.timedelta(days=1)
    st.session_state.pagina_atual = 1
    st.session_state.mostrar_txt_geral = False
    st.rerun()

nova_data = nav3.date_input(
    "Data da demanda",
    value=st.session_state.data_foco,
    format="DD/MM/YYYY",
    label_visibility="collapsed",
)
if nova_data != st.session_state.data_foco:
    st.session_state.data_foco = nova_data
    st.session_state.pagina_atual = 1
    st.session_state.mostrar_txt_geral = False
    st.rerun()

if nav4.button("Próximo ▶", key="btn_prox"):
    st.session_state.data_foco += datetime.timedelta(days=1)
    st.session_state.pagina_atual = 1
    st.session_state.mostrar_txt_geral = False
    st.rerun()

if nav5.button("🔄 Atualizar", key="btn_refresh"):
    limpar_cache()
    st.rerun()

st.divider()

data_str = st.session_state.data_foco.strftime("%Y-%m-%d")
data_label = st.session_state.data_foco.strftime("%d/%m/%Y")

# ==============================================================================
# 📌 MODO LISTA
# ==============================================================================
if st.session_state.modo_demanda == "lista":
    with st.spinner("Carregando demandas do dia..."):
        demandas_do_dia = carregar_demandas_data(data_str)

    pendentes = 0
    andamento = 0
    finalizadas = 0
    for d in demandas_do_dia:
        classe, _, _ = status_demanda(d)
        if classe == "pendente":
            pendentes += 1
        elif classe == "andamento":
            andamento += 1
        else:
            finalizadas += 1

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.markdown(f"<div class='metric-card'><div class='metric-label'>Demandas</div><div class='metric-value'>{len(demandas_do_dia)}</div></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='metric-card'><div class='metric-label'>Quadros</div><div class='metric-value'>{total_quadros(demandas_do_dia)}</div></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='metric-card'><div class='metric-label'>Caixas</div><div class='metric-value'>{total_caixas(demandas_do_dia)}</div></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='metric-card'><div class='metric-label'>Em andamento</div><div class='metric-value'>{andamento}</div></div>", unsafe_allow_html=True)
    m5.markdown(f"<div class='metric-card'><div class='metric-label'>Finalizadas</div><div class='metric-value'>{finalizadas}</div></div>", unsafe_allow_html=True)

    alertas_do_dia = gerar_alertas_demandas(demandas_do_dia, st.session_state.data_foco)
    mostrar_painel_alertas(alertas_do_dia)

    st.write("")
    topo1, topo2, topo3 = st.columns([1.2, 1.2, 1.2])
    if topo1.button("➕ Nova demanda", use_container_width=True):
        st.session_state.modo_demanda = "nova"
        st.session_state.itens_temp = []
        st.session_state.demanda_edit = None
        st.rerun()

    if demandas_do_dia and topo2.button("📄 Preparar TXT geral", use_container_width=True):
        st.session_state.mostrar_txt_geral = not st.session_state.mostrar_txt_geral

    itens_por_pagina = topo3.selectbox("Cards por página", [5, 10, 15, 20, 30], index=1, label_visibility="collapsed")

    if st.session_state.mostrar_txt_geral and demandas_do_dia:
        conteudo_massa = gerar_txt_etiquetas(demandas_do_dia, data_label=data_label)
        with st.expander("Preview do TXT geral de etiquetas", expanded=True):
            st.code(conteudo_massa[:4000] + ("\n..." if len(conteudo_massa) > 4000 else ""), language="text")
            st.download_button(
                "📥 Baixar todas as etiquetas do dia",
                data=conteudo_massa,
                file_name=f"ETIQUETAS_GERAL_{data_str}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    st.divider()

    if not demandas_do_dia:
        st.info(f"Nenhuma demanda para {data_label}.")
    else:
        total_paginas = max(1, math.ceil(len(demandas_do_dia) / itens_por_pagina))
        st.session_state.pagina_atual = min(max(1, st.session_state.pagina_atual), total_paginas)

        p1, p2, p3 = st.columns([1, 2, 1])
        if p1.button("⬅ Página", disabled=st.session_state.pagina_atual <= 1):
            st.session_state.pagina_atual -= 1
            st.rerun()
        p2.markdown(f"<p style='text-align:center;color:#cbd5e1;font-weight:800;'>Página {st.session_state.pagina_atual} de {total_paginas}</p>", unsafe_allow_html=True)
        if p3.button("Página ➡", disabled=st.session_state.pagina_atual >= total_paginas):
            st.session_state.pagina_atual += 1
            st.rerun()

        ini = (st.session_state.pagina_atual - 1) * itens_por_pagina
        fim = ini + itens_por_pagina
        demandas_visiveis = demandas_do_dia[ini:fim]

        for idx_local, d in enumerate(demandas_visiveis):
            idx_global = ini + idx_local
            classe, icone, marcadas = status_demanda(d)
            itens = d.get("itens", []) or []
            medidas_str = " | ".join([f"{it.get('qtd', 0)}x {it.get('tam', '')}" for it in itens])

            st.markdown("<div class='demand-card'>", unsafe_allow_html=True)
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"<div class='demand-title'>{d.get('cliente', '')}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='demand-meta'>NF: <b>{d.get('nf', '')}</b> • {medidas_str}</div>", unsafe_allow_html=True)
                st.markdown(f"<span class='status-badge {classe}'>{icone} {marcadas}/{len(ETAPAS_PRODUCAO)}</span>", unsafe_allow_html=True)
            with col_b:
                if st.button("📄 Etiquetas", key=f"etq_{d['id']}"):
                    st.session_state.demanda_etiqueta = d
                    st.session_state.modo_demanda = "etiquetas"
                    st.rerun()

            with st.expander("Abrir detalhes e etapas", expanded=False):
                cinfo1, cinfo2 = st.columns([1, 1])
                with cinfo1:
                    st.markdown("**📦 Medidas e caixas**")
                    for it in itens:
                        try:
                            tam = it.get("tam", "")
                            qtd = int(it.get("qtd", 0))
                            cap = obter_capacidade(d.get("cliente", ""), tam)
                            caixas = math.ceil(qtd / cap)
                            st.markdown(f"- **{tam}** — {qtd} un — **{caixas} caixa(s)** *(cap. {cap}/cx)*")
                        except Exception:
                            st.markdown(f"- {it}")
                    if d.get("agendamento"):
                        st.markdown(f"📅 **Agendamento:** {d.get('agendamento')}")
                    if d.get("referencia"):
                        st.markdown(f"📝 **Referência:** {d.get('referencia')}")

                with cinfo2:
                    st.markdown("**⚙️ Ações**")
                    b1, b2 = st.columns(2)
                    if b1.button("✏️ Editar", key=f"ed_{d['id']}"):
                        st.session_state.modo_demanda = "editar"
                        st.session_state.demanda_edit = d
                        st.session_state.itens_temp = itens.copy() if isinstance(itens, list) else []
                        st.rerun()
                    if b2.button("🗑️ Excluir", key=f"del_{d['id']}"):
                        excluir_demanda(d)

                    b3, b4 = st.columns(2)
                    if b3.button("⬆️ Subir", key=f"up_{d['id']}", disabled=idx_global <= 0):
                        mover_demanda(d, demandas_do_dia[idx_global - 1], idx_global, idx_global - 1)
                    if b4.button("⬇️ Descer", key=f"down_{d['id']}", disabled=idx_global >= len(demandas_do_dia) - 1):
                        mover_demanda(d, demandas_do_dia[idx_global + 1], idx_global, idx_global + 1)

                st.write("---")
                with st.form(key=f"form_etapas_{d['id']}"):
                    st.markdown("**✅ Etapas da produção**")
                    etapas_atuais = d.get("etapas", {}) or {}
                    novas_etapas = {}
                    cols_etapas = st.columns(3)
                    for i, etapa in enumerate(ETAPAS_PRODUCAO):
                        with cols_etapas[i % 3]:
                            novas_etapas[etapa] = st.checkbox(etapa, value=etapas_atuais.get(etapa, False), key=f"chk_{d['id']}_{i}")
                    if st.form_submit_button("💾 Salvar etapas"):
                        try:
                            supabase.table("demandas").update({"etapas": novas_etapas}).eq("id", d["id"]).execute()
                            limpar_cache()
                            st.success("Etapas salvas.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar etapas: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 📄 MODO ETIQUETAS
# ==============================================================================
elif st.session_state.modo_demanda == "etiquetas":
    d = st.session_state.demanda_etiqueta
    if not d:
        st.warning("Nenhuma demanda selecionada.")
        if st.button("Voltar"):
            voltar_lista()
            st.rerun()
    else:
        st.markdown("### 📄 Dados para etiquetas")
        st.info(f"Cliente: **{d.get('cliente', '')}** | NF: **{d.get('nf', '')}**")
        conteudo_txt = gerar_txt_etiquetas([d])
        st.code(conteudo_txt, language="text")
        st.download_button(
            "📥 Baixar TXT de etiquetas",
            data=conteudo_txt,
            file_name=f"DADOS_ETIQUETA_NF_{d.get('nf', '')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
        if st.button("❌ Voltar ao painel"):
            voltar_lista()
            st.rerun()

# ==============================================================================
# ➕ MODO NOVA / EDITAR
# ==============================================================================
elif st.session_state.modo_demanda in ["nova", "editar"]:
    is_edit = st.session_state.modo_demanda == "editar"
    d_edit = st.session_state.demanda_edit if is_edit and st.session_state.demanda_edit else {}
    st.markdown(f"### {'✏️ Editar demanda' if is_edit else '➕ Nova demanda'}")

    with st.container(border=True):
        with st.form("form_demanda_principal"):
            cli_d = st.text_input("Nome do cliente:", value=d_edit.get("cliente", "")).strip().upper()
            nf_d = st.text_input("Número da NF:", value=d_edit.get("nf", "")).strip().upper()
            txt_agend = st.text_input("Agendamento:", value=d_edit.get("agendamento", "")).strip().upper()
            txt_ref = st.text_area("Referência:", value=d_edit.get("referencia", "")).strip().upper()
            salvar = st.form_submit_button("✅ Salvar demanda")

        st.write("---")
        st.markdown("**📦 Itens adicionados**")
        if not st.session_state.itens_temp:
            st.caption("Nenhum item adicionado ainda.")
        else:
            for i, item in enumerate(st.session_state.itens_temp):
                c_it1, c_it2 = st.columns([5, 1])
                c_it1.markdown(f"• **{item.get('qtd', 0)}** unidades de **{item.get('tam', '')}**")
                if c_it2.button("🗑️", key=f"rem_item_{i}"):
                    st.session_state.itens_temp.pop(i)
                    st.rerun()

        with st.form("form_adicionar_item"):
            c_m1, c_m2 = st.columns([1, 1])
            t_med = c_m1.selectbox("Medida:", ["30x40", "60x40", "90x60"])
            t_qtd = c_m2.number_input("QTD:", min_value=1, value=1, step=1)
            add_item = st.form_submit_button("➕ Adicionar medida")
            if add_item:
                st.session_state.itens_temp.append({"tam": t_med, "qtd": int(t_qtd)})
                st.rerun()

        if salvar:
            nf_duplicada = validar_nf_duplicada(nf_d, is_edit=is_edit, id_atual=d_edit.get("id"))
            if nf_duplicada:
                st.error("⚠️ Esta NF já existe. Corrija antes de salvar.")
            elif not cli_d or not nf_d or len(st.session_state.itens_temp) == 0:
                st.warning("⚠️ Preencha cliente, NF e adicione pelo menos uma medida.")
            else:
                dados = {
                    "data": d_edit.get("data", data_str) if is_edit else data_str,
                    "cliente": cli_d,
                    "nf": nf_d,
                    "itens": st.session_state.itens_temp,
                    "agendamento": txt_agend,
                    "referencia": txt_ref,
                }
                try:
                    if is_edit:
                        supabase.table("demandas").update(dados).eq("id", d_edit["id"]).execute()
                    else:
                        dados["etapas"] = {etapa: False for etapa in ETAPAS_PRODUCAO}
                        dados["ordem"] = 999
                        supabase.table("demandas").insert(dados).execute()
                    limpar_cache()
                    voltar_lista()
                    st.success("Demanda salva.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    if st.button("❌ Voltar sem salvar"):
        voltar_lista()
        st.rerun()
