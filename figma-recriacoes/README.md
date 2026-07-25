# Recriações do Figma — MCP Apps for Claude

Telas do arquivo Figma **"MCP Apps for Claude (Community)"** (`wfiXKYbSeeM1kFwLwlIRiI`)
recriadas em HTML/CSS/JS interativo. Cada arquivo é autocontido — abra direto no navegador,
sem build nem dependências.

## Arquivos

| Arquivo | Página no Figma | Node |
|---|---|---|
| `inline-card.html` | App → Inline card | `67:3145` |
| `fullscreen.html` | App → Fullscreen | `67:3156` |
| `forms.html` | Desktop web components → Forms (Controls) | `26:1233` |
| `inline-carousel-skeleton.html` | Inline carousel (estado de carregamento) | `467:31022` |
| `border.html` | Border (design tokens) | `467:21770` |

## O que é interativo

- **inline-card.html** — sidebar expande/colapsa (com Starred, Recents e account switcher),
  dropdown de título, seletor de modelo, feedback 👍/👎, copiar com toast, e o Spark
  ciclando entre Default → Thinking → Thinking (long) ao clicar em "regenerar".
- **fullscreen.html** — composer "Ask App" e botão de fechar o container.
- **forms.html** — todos os controles funcionam de verdade (checkbox, radio, switch, inputs),
  com os estados `disabled` reais e os anéis de foco exatos do design (Tab para ver).
- **inline-carousel-skeleton.html** — seta "next" rola o carrossel um card por vez.
- **border.html** — tabela estática de tokens.

## Fidelidade

Os tokens de design (cores, raios, espaçamentos, sombras de foco, opacidades) foram extraídos
do próprio arquivo Figma via MCP e estão declarados como CSS custom properties no topo de cada
arquivo.

Duas aproximações conscientes, por limitação do ambiente:

1. **Ícones** — os SVGs exportados pelo Figma expiram em ~7 dias e a rede do ambiente bloqueia
   downloads de `figma.com`. Os ícones foram redesenhados inline no mesmo estilo (traço fino,
   20×20).
2. **Fontes** — as fontes Anthropic (Styrene / Tiempos) não são públicas. O CSS as declara
   primeiro e cai para um stack equivalente (sans do sistema / serifada tipo Georgia).

## Ressalvas

- **`inline-carousel-skeleton.html`** não existe como tela no Figma. O arquivo tem o carrossel
  já preenchido ("Nearby trails"), mas nenhum estado de carregamento desenhado para ele.
  O skeleton foi construído seguindo as dimensões reais dos cards (220×280, gap 12) e o mesmo
  padrão de shimmer usado nos outros skeletons do arquivo.
- **`border.html`** — os nomes e a ordem dos tokens vêm da página original, mas os valores em px
  foram derivados do uso real nos componentes, não relidos da tabela de variáveis (a conta
  atingiu o limite mensal da API do Figma no plano Starter).

## Pendente

Três páginas ainda não recriadas, bloqueadas pelo mesmo limite de API:

- `467:20292` — não inspecionada
- `7:19` — não inspecionada
- `455:241691` — seção "Examples" (mockups mobile, tema claro e escuro)
