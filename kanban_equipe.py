import streamlit as st
import datetime
import json
import math
import re
import unicodedata
from pathlib import Path
from html import escape
from supabase import create_client, Client

# ==============================================================================
# ECO DECOR - DEMANDA DIÁRIA | 2026.10.19-data-no-card
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
    :root { color-scheme: light; }
    .stApp { background: #e5ede8; color: #17251e; }
    [data-testid="stHeader"] { background: rgba(229,237,232,.96); }
    .block-container { max-width: 1440px; padding: 4rem 2rem 3rem; }
    h1, h2, h3, h4, [data-testid="stWidgetLabel"] p { color: #17251e !important; }
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
        color: #4b6054 !important; font-size: 14px; }
    .main-header { background: linear-gradient(120deg, #ffffff, #edf6ef); border: 1px solid #c2d6c9; border-left: 5px solid #16824a;
        border-radius: 16px; padding: 24px 28px; margin-bottom: 12px;
        box-shadow: 0 5px 16px rgba(25,64,42,.09); }
    .eyebrow { color: #197142; font-size: 12px; font-weight: 800; letter-spacing: .1em; }
    .main-title { font-size: clamp(25px, 3vw, 34px); font-weight: 800; margin: 5px 0; color: #14291d; }
    .main-subtitle { color: #4b6054; font-size: 15px; line-height: 1.5; }
    .metric-grid { display: grid; grid-template-columns: repeat(6,minmax(0,1fr)); gap: 12px; margin: 8px 0 20px; }
    .metric-card { background: #fbfdfb; border: 1px solid #c2d6c9; border-top: 3px solid #24915a;
        border-radius: 12px; padding: 14px 16px;
        box-shadow: 0 5px 14px rgba(25,64,42,.11), 0 1px 3px rgba(25,64,42,.05); }
    .metric-label { color: #465d4f; font-size: 13px; font-weight: 600; }
    .metric-value { color: #145c35; font-size: 28px; font-weight: 800; margin-top: 3px; }
    [class*="st-key-card_demanda_"] { background: white; border-color: #cfdfd4 !important;
        border-left: 4px solid #24915a !important; border-radius: 14px; padding: 16px !important;
        box-shadow: 0 6px 18px rgba(25,64,42,.12), 0 1px 3px rgba(25,64,42,.06); }
    .st-key-filtros_producao { background: #f0f6f2; border-color: #bfd4c6 !important;
        box-shadow: 0 4px 12px rgba(25,64,42,.09); }
    .st-key-cadastro_demanda { background: #f8fcf9; border-color: #bfd4c6 !important;
        box-shadow: 0 6px 18px rgba(25,64,42,.11); }
    .demand-title { font-size: 19px; line-height: 1.4; font-weight: 750; color: #17251e; overflow-wrap: anywhere; }
    .demand-meta { color: #42584a; font-size: 14px; margin: 5px 0; overflow-wrap: anywhere; }
    .date-badge { display: inline-block; background: #edf7f0; color: #185d37; padding: 6px 10px;
        font-size: 13px; border-radius: 7px; margin-bottom: 8px; }
    .status-badge { display:inline-block; padding: 5px 10px; border-radius: 7px; font-weight: 700;
        font-size: 13px; margin: 6px 0; border: 1px solid transparent; }
    .pendente { background: #fff2e9; color: #8b3a13; border-color: #f4d5bd; }
    .andamento { background: #fff7d7; color: #71530a; border-color: #ecdda2; }
    .finalizado { background: #e8f6ed; color: #166236; border-color: #b8dfc7; }
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
        min-height: 42px; border-radius: 9px; font-weight: 650; }
    button[kind="secondary"], button[kind="secondaryFormSubmit"] {
        background: white !important; border: 1px solid #a9cbb6 !important; color: #195e38 !important; }
    button[kind="primary"], button[kind="primaryFormSubmit"], .stDownloadButton button {
        background: #167344 !important; border: 1px solid #167344 !important; color: white !important; }
    button[kind="primary"] p, button[kind="primaryFormSubmit"] p, .stDownloadButton button p { color: white !important; }
    .stButton button:hover { border-color: #167344 !important; box-shadow: 0 0 0 2px #d8eddf; }
    [class*="st-key-popover_data_"] button[data-testid="stPopoverButton"] {
        background: #edf7f0 !important; color: #185d37 !important;
        border: 1px solid #c9e4d3 !important; border-radius: 7px;
        min-height: 36px; font-size: 13px;
    }
    button:disabled { opacity: .42; box-shadow: none !important; }
    [data-testid="stTextInput"] label, [data-testid="stTextArea"] label,
    [data-testid="stNumberInput"] label, [data-testid="stSelectbox"] label,
    [data-testid="stDateInput"] label { font-weight: 650; }
    [data-baseweb="input"], [data-baseweb="select"] > div, textarea {
        background: #f4fbf6 !important; border: 1px solid #96bda4 !important;
        border-radius: 9px !important; color: #17251e !important; }
    input, textarea { color: #17251e !important; }
    input::placeholder, textarea::placeholder { color: #617669 !important; opacity: 1; }
    [data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within, textarea:focus {
        border-color: #167344 !important; box-shadow: 0 0 0 2px #d8eddf !important; }
    [data-testid="stExpander"], [data-testid="stForm"] {
        background: #fbfdfb; border: 1px solid #c2d6c9; border-radius: 10px;
        box-shadow: 0 2px 7px rgba(25,64,42,.07); }
    [data-testid="stExpander"] summary { color: #234b32; font-weight: 650; }
    [data-testid="stForm"] { padding: 16px; }
    .alert-box { border: 1px solid #d6e5db; border-left: 4px solid #24915a;
        border-radius: 10px; padding: 12px 14px; margin: 8px 0; background: #fbfdfb; }
    .alert-head { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
    .alert-title { font-size: 15px; font-weight: 700; color: #17251e; }
    .alert-date { font-size: 13px; color: #31543d; white-space: nowrap; }
    .alert-meta { font-size: 14px; color: #42584a; margin-top: 6px; }
    .alert-critico { border-left-color: #bb6535; }
    .alert-sucesso { border-left-color: #16824a; }
    @media (max-width: 768px) {
        .block-container { padding: 3.5rem .8rem 2rem; }
        .main-header { padding: 18px; }
        .metric-grid { grid-template-columns: repeat(2,minmax(0,1fr)); gap: 8px; }
        .metric-card { padding: 12px; }
        .metric-value { font-size: 25px; }
        .demand-title { font-size: 17px; }
        .alert-head { align-items: flex-start; flex-wrap: wrap; }
        input, textarea { font-size: 16px !important; }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
        [data-testid="stColumn"] { min-width: min(100%, 280px) !important; flex: 1 1 280px !important; }
        .stButton button { width: 100%; }
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
    "ARTE (CAIO/LUCAS)",
    "IMPRESSÃO (CAIO)",
    "CORTE EM ANDAMENTO (CASSIO)",
    "CORTE FINALIZADO (CASSIO)",
    "PRODUÇÃO EM ANDAMENTO (GUSTAVO)",
    "PRODUÇÃO FINALIZADO (GUSTAVO)",
    "NOTA FISCAL (MICHELLI)",
    "LIBERADO PARA ENTREGA (MICHELLI)",
]

ETAPAS_COMPATIBILIDADE = {
    "CORTE EM ANDAMENTO (CASSIO)": "CORTE EM ANDAMENTO (DAVID)",
    "CORTE FINALIZADO (CASSIO)": "CORTE FINALIZADO (DAVID)",
    "PRODUÇÃO EM ANDAMENTO (GUSTAVO)": "PRODUÇÃO EM ANDAMENTO (SASKA)",
    "PRODUÇÃO FINALIZADO (GUSTAVO)": "PRODUÇÃO FINALIZADO (SASKA)",
}

ARQUIVO_NOTIFICACOES = Path(__file__).resolve().parent / "notificacoes_kanban.json"
HORAS_NOTIFICACAO = 24
DIAS_NOTIFICACAO_PASSADO = 1
DIAS_NOTIFICACAO_FUTURO = 10

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
CLIENTE_BIGODINHO = "GALPAO DROP LTDA (BIGODINHO)"


def is_cliente_bigodinho(cliente):
    return "BIGODINHO" in str(cliente or "").upper()


def obter_capacidade(cliente, tam):
    cli_upper = str(cliente).upper()
    is_bigodinho = any(palavra in cli_upper for palavra in ["BIGODINHO", "LUCAS", "JIMMY", "REP"])
    if tam in ("80x50", "90x60"):
        return 10 if is_bigodinho else 11
    if tam == "85x55":
        return 11
    if tam == "60x40":
        return 22
    if tam == "30x40":
        return 43
    if tam in ("20x50", "50x20"):
        return 50
    if tam == "55x35":
        return 35
    return 1


def linha_cliente_etiqueta(cliente):
    cli_upper = str(cliente).upper()
    if is_cliente_bigodinho(cliente):
        return f"CLIENTE: {CLIENTE_BIGODINHO}"
    if "LUCAS" in cli_upper:
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
    marcadas = sum(1 for etapa in ETAPAS_PRODUCAO if _etapa_marcada(etapas, etapa))
    if marcadas == len(ETAPAS_PRODUCAO):
        return "finalizado", "🟢", marcadas
    if marcadas > 0:
        return "andamento", "🟡", marcadas
    return "pendente", "🔴", marcadas


def _normalizar(valor):
    texto = unicodedata.normalize("NFKD", str(valor).strip().lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "", texto)


def _etapa_marcada(etapas, etapa):
    etapa_antiga = ETAPAS_COMPATIBILIDADE.get(etapa)
    return bool(etapas.get(etapa, False) or (etapa_antiga and etapas.get(etapa_antiga, False)))


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


@st.cache_data(ttl=45, show_spinner=False)
def buscar_demandas_geral(termo_busca, data_centro_str, dias_raio=20, limite=80):
    """Busca demanda em várias datas/colunas, sem alterar nada no Supabase.

    A busca tenta primeiro pelas colunas mais importantes. Depois faz uma busca
    limitada em datas próximas para pegar medida/referência dentro dos itens.
    """
    termo_limpo = str(termo_busca or "").strip()
    termo_norm = _normalizar(termo_limpo)
    if not termo_norm:
        return []

    encontrados = {}

    def adicionar(lista):
        for demanda in lista or []:
            demanda_id = str(demanda.get("id") or demanda.get("nf") or len(encontrados))
            encontrados[demanda_id] = demanda

    # Busca rápida por colunas simples do Supabase.
    for coluna in ["nf", "cliente", "referencia", "agendamento"]:
        try:
            resposta = (
                supabase.table("demandas")
                .select("*")
                .ilike(coluna, f"%{termo_limpo}%")
                .limit(limite)
                .execute()
            )
            adicionar(resposta.data)
        except Exception:
            pass

    # Fallback: datas próximas para localizar medida/quantidade dentro de itens JSON.
    try:
        data_centro = datetime.datetime.strptime(data_centro_str, "%Y-%m-%d").date()
    except Exception:
        data_centro = datetime.date.today()

    for deslocamento in range(-dias_raio, dias_raio + 1):
        if len(encontrados) >= limite:
            break
        data_busca = (data_centro + datetime.timedelta(days=deslocamento)).strftime("%Y-%m-%d")
        try:
            adicionar([
                demanda for demanda in carregar_demandas_data(data_busca)
                if termo_norm in _texto_busca_demanda(demanda)
            ])
        except Exception:
            pass

    dados = list(encontrados.values())
    dados.sort(key=lambda x: (str(x.get("data", "")), x.get("ordem") if x.get("ordem") is not None else 999), reverse=True)
    return dados[:limite]


def limpar_cache():
    carregar_demandas_data.clear()
    buscar_demandas_geral.clear()


def voltar_lista():
    st.session_state.modo_demanda = "lista"
    st.session_state.demanda_edit = None
    st.session_state.demanda_etiqueta = None
    st.session_state.itens_temp = []
    st.session_state.mostrar_txt_geral = False


def cancelar_data_card(demanda_id):
    """Fecha o calendário e descarta a escolha, sem gravar na demanda."""
    st.session_state.pop(f"data_card_{demanda_id}", None)
    st.session_state[f"popover_data_{demanda_id}"] = False
    st.session_state.pop(f"erro_data_card_{demanda_id}", None)


def salvar_data_card(demanda_id):
    """Atualiza somente a data do ID escolhido; não regrava itens ou etapas."""
    nova_data = st.session_state.get(f"data_card_{demanda_id}")
    if not isinstance(nova_data, datetime.date):
        st.session_state[f"erro_data_card_{demanda_id}"] = "Escolha uma data antes de salvar."
        return
    try:
        supabase.table("demandas").update({"data": nova_data.isoformat()}).eq("id", demanda_id).execute()
    except Exception as e:
        st.session_state[f"erro_data_card_{demanda_id}"] = f"Erro ao alterar a data: {e}"
        return
    limpar_cache()
    st.session_state.data_foco = nova_data
    st.session_state.pagina_atual = 1
    cancelar_data_card(demanda_id)


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


def _texto_busca_demanda(demanda):
    """Texto simples para buscar por NF, cliente, medida ou referência."""
    partes = [
        demanda.get("cliente", ""),
        demanda.get("nf", ""),
        demanda.get("referencia", ""),
        demanda.get("agendamento", ""),
    ]
    for item in demanda.get("itens", []) or []:
        partes.append(item.get("tam", ""))
        partes.append(str(item.get("qtd", "")))
    return _normalizar(" ".join(str(parte) for parte in partes))


def filtrar_demandas(demandas, termo_busca):
    termo = _normalizar(termo_busca)
    if not termo:
        return demandas
    return [
        demanda for demanda in demandas
        if termo in _texto_busca_demanda(demanda)
    ]


def filtrar_por_producao(demandas, situacao="Todas", etapa="Todas"):
    """Filtra a lista na tela, sem gravar nem inferir uma etapa atual."""
    status_filtro = {"Pendentes": "pendente", "Em andamento": "andamento", "Finalizadas": "finalizado"}
    return [
        d for d in demandas
        if (situacao == "Todas" or status_demanda(d)[0] == status_filtro.get(situacao))
        and (etapa == "Todas" or _etapa_marcada(d.get("etapas", {}) or {}, etapa))
    ]


def _data_demanda(demanda):
    try:
        return datetime.datetime.strptime(str(demanda.get("data", "")), "%Y-%m-%d").date()
    except Exception:
        return None


def _agora_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")


def _ler_notificacoes_local():
    modelo = {"vistos": {}, "notificacoes": []}
    if not ARQUIVO_NOTIFICACOES.exists():
        return modelo
    try:
        dados = json.loads(ARQUIVO_NOTIFICACOES.read_text(encoding="utf-8"))
        if not isinstance(dados, dict):
            return modelo
        dados.setdefault("vistos", {})
        dados.setdefault("notificacoes", [])
        return dados
    except Exception:
        return modelo


def _salvar_notificacoes_local(dados):
    try:
        ARQUIVO_NOTIFICACOES.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


def _notificacao_ativa(item):
    try:
        criado = datetime.datetime.fromisoformat(item.get("criado_em", ""))
    except Exception:
        return False
    return datetime.datetime.now() - criado <= datetime.timedelta(hours=HORAS_NOTIFICACAO)


def carregar_demandas_janela_notificacao(data_base):
    demandas = []
    for deslocamento in range(-DIAS_NOTIFICACAO_PASSADO, DIAS_NOTIFICACAO_FUTURO + 1):
        data_busca = (data_base + datetime.timedelta(days=deslocamento)).strftime("%Y-%m-%d")
        try:
            demandas.extend(carregar_demandas_data(data_busca))
        except Exception:
            pass
    return demandas


def gerar_alertas_demandas(_demandas_do_dia, data_referencia):
    """Avisa somente eventos importantes de todos os dias próximos.

    Não altera dados no Supabase. O histórico é local e cada notificação fica
    visível por 24 horas quando necessário:
    - toda demanda sem etapa marcada, status 0/9;
    - demanda que ficou finalizada.
    """
    dados = _ler_notificacoes_local()
    vistos = dados.get("vistos", {})
    notificacoes = [
        item for item in dados.get("notificacoes", [])
        if _notificacao_ativa(item)
    ]

    demandas_janela = carregar_demandas_janela_notificacao(data_referencia)
    ids_notificacao = {item.get("id") for item in notificacoes}

    for demanda in demandas_janela:
        demanda_id = str(demanda.get("id") or demanda.get("nf") or "")
        if not demanda_id:
            continue

        classe, _, marcadas = status_demanda(demanda)
        cliente = str(demanda.get("cliente", "") or "SEM CLIENTE")
        nf = str(demanda.get("nf", "") or "SEM NF")
        data_demanda = str(demanda.get("data", ""))
        medidas = _texto_medidas(demanda)
        anterior = vistos.get(demanda_id)

        if marcadas == 0:
            id_nova = f"nova_{demanda_id}"
            if id_nova not in ids_notificacao:
                notificacoes.append({
                    "id": id_nova,
                    "nivel": "critico",
                    "tipo": "nova",
                    "titulo": f"Nova demanda — NF {nf}",
                    "texto": f"{cliente} • {medidas} • 0/{len(ETAPAS_PRODUCAO)} etapas.",
                    "data": data_demanda,
                    "criado_em": _agora_iso(),
                })
                ids_notificacao.add(id_nova)

        if anterior and anterior.get("status") != "finalizado" and classe == "finalizado":
            id_finalizada = f"finalizada_{demanda_id}_{_agora_iso()}"
            notificacoes.append({
                "id": id_finalizada,
                "nivel": "sucesso",
                "tipo": "finalizada",
                "titulo": f"Demanda finalizada — NF {nf}",
                "texto": f"{cliente} • {medidas} • {marcadas}/{len(ETAPAS_PRODUCAO)} etapas.",
                "data": data_demanda,
                "criado_em": _agora_iso(),
            })

        vistos[demanda_id] = {
            "status": classe,
            "nf": nf,
            "cliente": cliente,
            "data": data_demanda,
            "atualizado_em": _agora_iso(),
        }

    dados["vistos"] = vistos
    dados["notificacoes"] = notificacoes
    _salvar_notificacoes_local(dados)

    prioridade = {"critico": 0, "sucesso": 1, "info": 2}
    notificacoes.sort(
        key=lambda item: (
            prioridade.get(item.get("nivel"), 9),
            item.get("criado_em", ""),
        ),
        reverse=True,
    )
    return notificacoes


def _formatar_data_alerta(alerta):
    data_raw = str(alerta.get("data", "") or "")
    if not data_raw:
        encontrado = re.search(r"Data:\s*(\d{4}-\d{2}-\d{2})", str(alerta.get("texto", "")))
        data_raw = encontrado.group(1) if encontrado else ""
    if not data_raw:
        return ""
    try:
        return datetime.datetime.strptime(data_raw, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return data_raw


def _texto_alerta_limpo(alerta):
    texto = str(alerta.get("texto", ""))
    texto = re.sub(r"\s*•\s*Data:\s*\d{4}-\d{2}-\d{2}", "", texto)
    return texto


def _classe_alerta(alerta):
    tipo = str(alerta.get("tipo", "")).lower()
    titulo = str(alerta.get("titulo", "")).lower()
    if tipo == "finalizada" or "finalizada" in titulo:
        return "alert-sucesso"
    if tipo == "nova" or "nova demanda" in titulo:
        return "alert-critico"
    return {
        "critico": "alert-critico",
        "sucesso": "alert-sucesso",
        "info": "alert-info",
    }.get(alerta.get("nivel"), "alert-info")


def mostrar_painel_alertas(alertas):
    finalizadas = sum(1 for item in alertas if "finalizada" in item["titulo"].lower())
    novas = sum(1 for item in alertas if "nova demanda" in item["titulo"].lower())

    with st.expander(
        f"🔔 Notificações importantes — {len(alertas)} aviso(s)",
        expanded=False,
    ):
        if not alertas:
            st.success("Nenhuma novidade importante desde a última atualização da tela.")
            st.caption(
                "O painel mostra como nova toda demanda em 0/9 etapas e avisa por 24 horas quando uma demanda fica finalizada, "
                "mesmo que a demanda seja de amanhã ou dos próximos dias."
            )
            return

        c1, c2 = st.columns(2)
        c1.metric("Demandas novas", novas)
        c2.metric("Finalizadas", finalizadas)

        for alerta in alertas[:12]:
            classe = _classe_alerta(alerta)
            data_alerta = _formatar_data_alerta(alerta)
            texto_alerta = _texto_alerta_limpo(alerta)
            st.markdown(
                f"""
                <div class="alert-box {classe}">
                    <div class="alert-head">
                        <div class="alert-title">{escape(str(alerta["titulo"]))}</div>
                        <div class="alert-date">📅 {escape(data_alerta)}</div>
                    </div>
                    <div class="alert-meta">{escape(texto_alerta)}</div>
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
        <div class="eyebrow">ECODECOR · PRODUÇÃO</div>
        <div class="main-title">Controle de demandas</div>
        <div class="main-subtitle">Acompanhe os pedidos, confira as etapas e prepare as etiquetas.</div>
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

    alertas_do_dia = gerar_alertas_demandas(demandas_do_dia, st.session_state.data_foco)
    mostrar_painel_alertas(alertas_do_dia)

    st.write("")
    topo1, topo2, topo3 = st.columns([1.2, 1.2, 1.2])
    if topo1.button("➕ Nova demanda", type="primary", use_container_width=True):
        st.session_state.modo_demanda = "nova"
        st.session_state.itens_temp = []
        st.session_state.demanda_edit = None
        st.rerun()

    if demandas_do_dia and topo2.button("📄 Preparar TXT geral", use_container_width=True):
        st.session_state.mostrar_txt_geral = not st.session_state.mostrar_txt_geral

    itens_por_pagina = topo3.selectbox("Cards por página", [5, 10, 15, 20, 30], index=1, label_visibility="collapsed")

    with st.container(border=True, key="filtros_producao"):
        busca_demanda = st.text_input(
            "🔎 Buscar demanda",
            placeholder="NF, cliente, medida ou referência",
            key="busca_demanda",
        ).strip()
        filtro1, filtro2 = st.columns(2)
        situacao = filtro1.selectbox("Situação", ["Todas", "Pendentes", "Em andamento", "Finalizadas"], key="filtro_situacao")
        etapa = filtro2.selectbox("Etapa concluída", ["Todas"] + ETAPAS_PRODUCAO, key="filtro_etapa")
        st.caption("Etapa concluída filtra as etapas já marcadas; não indica qual trabalho deve ser feito agora.")

    if busca_demanda:
        demandas_base = buscar_demandas_geral(busca_demanda, data_str)
    else:
        demandas_base = demandas_do_dia
    demandas_filtradas = filtrar_por_producao(demandas_base, situacao, etapa)
    lista_filtrada = bool(busca_demanda) or situacao != "Todas" or etapa != "Todas"

    if busca_demanda:
        st.caption(
            f"Resumo dos resultados da busca: {len(demandas_filtradas)} de {len(demandas_base)} demanda(s). "
            "A busca inclui outras datas, retorna até 80 resultados e procura medidas nas datas próximas. "
            "O TXT geral continua sendo somente do dia selecionado."
        )
    else:
        st.caption(f"Resumo de {data_label} · {len(demandas_filtradas)} de {len(demandas_do_dia)} demanda(s), conforme os filtros.")

    # Reinicia a página apenas quando a pesquisa muda, não em todo clique.
    contexto_lista = (data_str, busca_demanda, situacao, etapa, itens_por_pagina)
    if st.session_state.get("contexto_lista") != contexto_lista:
        st.session_state.pagina_atual = 1
        st.session_state.contexto_lista = contexto_lista

    contagens = {"pendente": 0, "andamento": 0, "finalizado": 0}
    for demanda in demandas_filtradas:
        contagens[status_demanda(demanda)[0]] += 1
    indicadores = [
        ("Demandas", len(demandas_filtradas)), ("Quadros", total_quadros(demandas_filtradas)),
        ("Caixas", total_caixas(demandas_filtradas)), ("Pendentes", contagens["pendente"]),
        ("Em andamento", contagens["andamento"]), ("Finalizadas", contagens["finalizado"]),
    ]
    st.markdown("<div class='metric-grid'>" + "".join(
        f"<div class='metric-card'><div class='metric-label'>{rotulo}</div><div class='metric-value'>{valor}</div></div>"
        for rotulo, valor in indicadores
    ) + "</div>", unsafe_allow_html=True)
    if lista_filtrada:
        st.caption("Para reordenar demandas, limpe a busca e deixe os dois filtros em Todas.")

    if st.session_state.mostrar_txt_geral and demandas_do_dia:
        conteudo_massa = gerar_txt_etiquetas(demandas_do_dia, data_label=data_label)
        with st.expander(f"Preview do TXT geral de etiquetas — {data_label}", expanded=True):
            st.code(conteudo_massa[:4000] + ("\n..." if len(conteudo_massa) > 4000 else ""), language="text")
            st.download_button(
                "📥 Baixar todas as etiquetas do dia",
                data=conteudo_massa,
                file_name=f"ETIQUETAS_GERAL_{data_str}.txt",
                mime="text/plain",
                use_container_width=True,
            )

    st.divider()

    if not demandas_filtradas:
        if not demandas_base and not busca_demanda:
            st.info(f"Nenhuma demanda para {data_label}.")
        else:
            st.info("Nenhuma demanda encontrada com a busca e os filtros atuais.")
    else:
        total_paginas = max(1, math.ceil(len(demandas_filtradas) / itens_por_pagina))
        st.session_state.pagina_atual = min(max(1, st.session_state.pagina_atual), total_paginas)

        p1, p2, p3 = st.columns([1, 2, 1])
        if p1.button("⬅ Página", disabled=st.session_state.pagina_atual <= 1):
            st.session_state.pagina_atual -= 1
            st.rerun()
        p2.markdown(f"<p style='text-align:center;color:#166534;font-weight:800;'>Página {st.session_state.pagina_atual} de {total_paginas}</p>", unsafe_allow_html=True)
        if p3.button("Página ➡", disabled=st.session_state.pagina_atual >= total_paginas):
            st.session_state.pagina_atual += 1
            st.rerun()

        ini = (st.session_state.pagina_atual - 1) * itens_por_pagina
        fim = ini + itens_por_pagina
        demandas_visiveis = demandas_filtradas[ini:fim]

        for idx_local, d in enumerate(demandas_visiveis):
            idx_global = ini + idx_local
            classe, icone, marcadas = status_demanda(d)
            itens = d.get("itens", []) or []
            medidas_str = " | ".join([f"{it.get('qtd', 0)}x {it.get('tam', '')}" for it in itens])

            with st.container(border=True, key=f"card_demanda_{d['id']}"):
                rotulo_status = {"pendente": "Pendente", "andamento": "Em andamento", "finalizado": "Finalizada"}[classe]
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"<div class='demand-title'>{escape(str(d.get('cliente', '')))}</div>", unsafe_allow_html=True)
                    data_card = d.get("data", data_str)
                    st.markdown(f"<div class='demand-meta'>NF: <b>{escape(str(d.get('nf', '')))}</b> • {escape(medidas_str)}</div>", unsafe_allow_html=True)
                    st.markdown(f"<span class='status-badge {classe}'>{icone} {rotulo_status} · {marcadas}/{len(ETAPAS_PRODUCAO)}</span>", unsafe_allow_html=True)
                with col_b:
                    data_formatada = data_card
                    try:
                        data_formatada = datetime.datetime.strptime(str(data_card), "%Y-%m-%d").strftime("%d/%m/%Y")
                    except Exception:
                        pass
                    editor_data = st.popover(
                        f"📅 {data_formatada}",
                        key=f"popover_data_{d['id']}",
                        on_change="rerun",
                        help="Clique para alterar a data desta demanda.",
                    )
                    if editor_data.open:
                        with editor_data:
                            st.markdown("**Alterar data da demanda**")
                            st.caption(f"{d.get('cliente', '')} · NF {d.get('nf', '')}")
                            data_original = _data_demanda(d) or st.session_state.data_foco
                            st.date_input("Nova data:", value=data_original,
                                          format="DD/MM/YYYY", key=f"data_card_{d['id']}")
                            st.caption("A demanda só muda de dia ao clicar em Salvar data.")
                            erro_data = st.session_state.get(f"erro_data_card_{d['id']}")
                            if erro_data:
                                st.error(erro_data)
                            salvar_data, cancelar_data = st.columns(2)
                            salvar_data.button("Salvar data", key=f"salvar_data_card_{d['id']}",
                                               type="primary", on_click=salvar_data_card, args=(d['id'],))
                            cancelar_data.button("Cancelar", key=f"cancelar_data_card_{d['id']}",
                                                 on_click=cancelar_data_card, args=(d['id'],))
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
                        if b3.button("⬆️ Subir", key=f"up_{d['id']}", disabled=lista_filtrada or idx_global <= 0):
                            mover_demanda(d, demandas_do_dia[idx_global - 1], idx_global, idx_global - 1)
                        if b4.button("⬇️ Descer", key=f"down_{d['id']}", disabled=lista_filtrada or idx_global >= len(demandas_do_dia) - 1):
                            mover_demanda(d, demandas_do_dia[idx_global + 1], idx_global, idx_global + 1)

                    st.write("---")
                    with st.form(key=f"form_etapas_{d['id']}"):
                        st.markdown("**✅ Etapas da produção**")
                        etapas_atuais = d.get("etapas", {}) or {}
                        novas_etapas = {}
                        cols_etapas = st.columns(3)
                        for i, etapa in enumerate(ETAPAS_PRODUCAO):
                            with cols_etapas[i % 3]:
                                novas_etapas[etapa] = st.checkbox(etapa, value=_etapa_marcada(etapas_atuais, etapa), key=f"chk_{d['id']}_{i}")
                        if st.form_submit_button("💾 Salvar etapas"):
                            try:
                                supabase.table("demandas").update({"etapas": novas_etapas}).eq("id", d["id"]).execute()
                                limpar_cache()
                                st.success("Etapas salvas.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao salvar etapas: {e}")

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

    with st.container(border=True, key="cadastro_demanda"):
        st.markdown("**📝 Dados principais**")
        data_demanda = st.session_state.data_foco
        if is_edit:
            data_demanda = st.date_input(
                "Data da demanda:",
                value=_data_demanda(d_edit) or st.session_state.data_foco,
                format="DD/MM/YYYY",
                key=f"editar_data_demanda_{d_edit['id']}",
                help="Ao salvar, a demanda será transferida para o dia escolhido, mantendo itens e etapas.",
            )
        cliente_atual = str(d_edit.get("cliente", "") or "").strip().upper()
        tipo_cliente = st.radio(
            "Tipo de cliente:",
            ["Cliente normal", "Etiqueta personalizada Bigodinho"],
            index=1 if is_cliente_bigodinho(cliente_atual) else 0,
            horizontal=True,
        )
        if tipo_cliente == "Etiqueta personalizada Bigodinho":
            cli_d = CLIENTE_BIGODINHO
            st.text_input("Nome do cliente:", value=cli_d, disabled=True)
        else:
            cli_d = st.text_input("Nome do cliente:", value=cliente_atual).strip().upper()
        col_nf, col_agendamento = st.columns(2)
        nf_d = col_nf.text_input("Número da NF:", value=d_edit.get("nf", "")).strip().upper()
        txt_agend = col_agendamento.text_input("Agendamento:", value=d_edit.get("agendamento", "")).strip().upper()
        txt_ref = st.text_area("Referência:", value=d_edit.get("referencia", "")).strip().upper()
        st.caption("Adicione as medidas abaixo e confira os itens antes de salvar a demanda.")

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
            medidas_disponiveis = (
                ["60x40", "80x50"]
                if is_cliente_bigodinho(cli_d)
                else ["20x50", "30x40", "55x35", "60x40", "80x50", "85x55"]
            )
            t_med = c_m1.selectbox("Medida:", medidas_disponiveis)
            t_qtd = c_m2.number_input("QTD:", min_value=1, value=1, step=1)
            add_item = st.form_submit_button("➕ Adicionar medida")
            if add_item:
                st.session_state.itens_temp.append({"tam": t_med, "qtd": int(t_qtd)})
                st.rerun()

        st.write("---")
        st.markdown("**✅ Finalizar cadastro**")
        col_salvar, col_voltar = st.columns([1, 1])
        with col_salvar:
            salvar = st.button("✅ Salvar demanda", type="primary", use_container_width=True)
        with col_voltar:
            voltar_sem_salvar = st.button("❌ Voltar sem salvar", use_container_width=True)

        if voltar_sem_salvar:
            voltar_lista()
            st.rerun()

        if salvar:
            nf_duplicada = validar_nf_duplicada(nf_d, is_edit=is_edit, id_atual=d_edit.get("id"))
            if nf_duplicada:
                st.error("⚠️ Esta NF já existe. Corrija antes de salvar.")
            elif not cli_d or not nf_d or len(st.session_state.itens_temp) == 0:
                st.warning("⚠️ Preencha cliente, NF e adicione pelo menos uma medida.")
            elif data_demanda is None:
                st.warning("⚠️ Escolha a data da demanda antes de salvar.")
            else:
                dados = {
                    "data": data_demanda.isoformat(),
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
                    if is_edit:
                        st.session_state.data_foco = data_demanda
                    voltar_lista()
                    st.success("Demanda salva.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

st.caption("Ecodecor · Demandas · versão 2026.10.19-data-no-card")
