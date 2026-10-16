# Kanban Ecodecor — 16/10/2026

Versão: `2026.10.16-interface-verde`.

## O que mudou

- Notificações continuam disponíveis com contador, mas ficam fechadas por padrão. A atualização não manda abri-las. O funcionário ainda pode abrir quando quiser.
- Interface clara, contraste verde, botões principais destacados e campos organizados.
- Cards em containers reais do Streamlit, com nome, NF, data e situação por escrito.
- Filtros de situação e de etapa já marcada. Não se presume uma etapa atual.
- Indicadores calculados para a lista filtrada, com contexto do dia ou da busca. O TXT geral mantém o escopo do dia selecionado.
- Busca paginada não volta automaticamente para a primeira página. Busca também mostra resultados de outros dias quando o dia selecionado está vazio.
- Reordenação fica desabilitada durante filtros/busca: para usá-la, limpar busca e selecionar Todas nos dois filtros. Sem filtros, segue disponível.
- Texto de cliente, NF, medidas e notificações escapado ao entrar em HTML.

## Preservação

Não houve alteração de esquema, migração ou gravação no banco real durante o desenvolvimento. Mantidos cliente Bigodinho, capacidades (inclusive 30x40 = 43), geração de etiquetas, nomes/compatibilidade das etapas, consultas, cadastro, edição e exclusão existentes. Dependências e logos do repositório não foram substituídos.

O código anterior está no histórico Git: commit `d4085c5af4ad41f20742296d267386d34662d0c4`, blob `a1a9e8bbf2600e69f4422e59d88f98b5d986f986`. A cópia local em `backup_original` normaliza CRLF para LF e contém uma linha vazia adicional ao final; foi comparada após normalização, não deve ser tratada como cópia binária idêntica. Essa pasta é apenas local, não integra a publicação.

## Testes

Na raiz do repositório:

```powershell
python -m unittest discover -s tests -v
python -m py_compile kanban_equipe.py
```

14 testes automatizados com AppTest e funções puras. O cliente Supabase é substituído antes de iniciar o app; conexão de socket bloqueada nos testes. Cadastros e edições são somente em memória, notificações em diretórios temporários.

Cobertura: avisos fechados após atualizar, filtros/compatibilidade de etapas antigas, busca/paginação/dia vazio, etiquetas/voltar, salvar etapas, cadastro Bigodinho, edição, filtros sem resultado, HTML escapado, reordenação do dia e capacidades.

Conferência visual em navegador local com dados fictícios: lista → editar → salvar → consultar agendamento; notificações fechadas e layout desktop. Na largura 390 px, cards cabem no viewport e indicadores se organizam em duas colunas, sem transbordamento horizontal. Não equivale a um teste em todos os celulares.

Limite do AppTest 1.56: o clique Editar dentro de um card com rerun deixa elementos antigos na árvore do teste. A edição automatizada inicia pelo estado de edição; o fluxo completo de navegação foi conferido no navegador. Avisos de runtime ausente/NumPy recarregado pertencem ao ambiente de testes, sem falha de asserção.

Revisão independente do diff e repetição da suíte: sem regressões concretas identificadas. Não se testou gravação contra o Supabase de produção nem se realizou auditoria completa de permissões/RLS.

## Como conferir depois de publicado

Abra o app habitual, atualize a página e confira a versão no rodapé. Notificações devem começar fechadas. Abra-as manualmente, confira um pedido e teste os filtros. O cadastro e as etiquetas continuam nos botões habituais.

O tema está em `.streamlit/config.toml`. Em execução local, iniciar da raiz do projeto; em hospedagem Streamlit, aguardar a implantação/reinicialização do app. Publicação do código no GitHub e implantação do serviço são etapas distintas.

## Reversão

Reverter o commit/PR desta melhoria e aguardar a implantação anterior, sem modificar dados do Supabase. Não restaurar dados nem trocar credenciais para reverter somente a interface. O histórico Git preserva a versão anterior.

## Referências de visual

Os princípios já consultados em *Storytelling com Dados*, de Cole Nussbaumer Knaflic (PDF, pp. 44 e 104), orientaram a hierarquia de informação e o uso seletivo de cor. Não foram adicionados gráficos ou indicadores estatísticos sem necessidade. Os outros livros enviados não justificam mudanças nas regras de produção ou no banco.

## Segurança existente — fora do escopo

O código já tinha configuração de cliente Supabase com chave do tipo `anon`; ela não foi alterada. A presença de chave anon não comprova que as políticas do banco estão corretas. Recomenda-se revisão separada de autenticação, RLS e tratamento de concorrência. Não colocar chaves privilegiadas no fonte.
