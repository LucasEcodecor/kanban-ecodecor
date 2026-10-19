# Contraste e sombras — Kanban Ecodecor

Versão `2026.10.19-contraste-sombras`.

## Ajuste solicitado

Reduzir a sensação de excesso de branco usando sombras discretas nos pedidos, quantidades e blocos de preenchimento. Mantidos o tema claro e a identidade verde.

## Alterações

- Fundo cinza-esverdeado `#e5ede8`, coerente entre CSS e `.streamlit/config.toml`.
- Indicadores claros com sombra curta, borda superior verde e números escuros.
- Cards de pedidos com sombra suave e borda lateral existente.
- Filtros e cadastro com fundo verde muito suave e sombra própria.
- Cabeçalho levemente tonalizado e detalhes/formulários com sombras menores.
- Não foram acrescentados efeitos de movimento, nem usada apenas a cor para indicar a situação.

## Segurança e verificação

- 17 testes aprovados: os 14 testes existentes e 3 novos contratos visuais.
- Testes realizados com banco fictício, pastas temporárias e bloqueio de conexão de socket. Nenhum cadastro fictício foi enviado ao Supabase.
- `python -m py_compile kanban_equipe.py` aprovado.
- Comparação AST: todas as funções Python são idênticas à versão anterior. Mudanças fora do CSS limitadas a duas chaves de containers e identificação da versão.
- Conferência no navegador local com pedidos fictícios: sombras, legibilidade, indicadores e cadastro. Isso não comprova implantação do serviço online.
- Notificações continuam fechadas por padrão; nenhuma regra de produção, capacidade de caixa, etiqueta, consulta ou configuração de banco foi alterada.

## Arquivos

- `kanban_equipe.py`: CSS, chaves dos dois blocos visuais e versão.
- `.streamlit/config.toml`: cor de fundo.
- `tests/test_visual_sombras.py`: testes de estilo sem importar o app ou conectar ao banco.
- Este documento.

Cópia local anterior em `backup_antes_sombras_20261019`; não publicada. Histórico oficial anterior preservado no commit `08c886be4dd69fb78cb52d30ef2aae04648a9b05`. Para reverter somente o visual, reverter o PR desta alteração, sem restaurar bancos nem alterar dados.

## Testar

```powershell
python -m unittest discover -s tests -v
python -m py_compile kanban_equipe.py
```

No app, atualizar a página e conferir o rodapé com a versão. Caso a hospedagem use a branch main, aguardar sua implantação; não se declara que o serviço online reiniciou apenas porque o GitHub foi atualizado.
