# Recriações do Figma — MCP Apps for Claude

Telas e páginas de tokens do arquivo Figma **"MCP Apps for Claude (Community)"**
recriadas em HTML/CSS/JS interativo. Cada arquivo é autocontido — abra direto no navegador,
sem build nem dependências.

## Arquivos

### Telas

| Arquivo | Página no Figma | Node |
|---|---|---|
| `inline-card.html` | App → Inline card | `67:3145` |
| `fullscreen.html` | App → Fullscreen | `67:3156` |
| `inline-carousel-skeleton.html` | Inline carousel (estado de carregamento) | `467:31022` |

### Design tokens

| Arquivo | Página no Figma | Node |
|---|---|---|
| `color.html` | 🖌️ Color | `467:20292` |
| `typography.html` | 🔠 Typography | `7:19` |
| `border.html` | Border | `467:21770` |
| `forms.html` | Desktop web components → Forms (Controls) | `26:1233` |

## O que é interativo

- **inline-card.html** — sidebar expande/colapsa (com Starred, Recents e account switcher),
  dropdown de título, seletor de modelo, feedback 👍/👎, copiar com toast, e o Spark
  ciclando entre Default → Thinking → Thinking (long) ao clicar em "regenerar".
- **fullscreen.html** — composer "Ask App" e botão de fechar o container.
- **forms.html** — todos os controles funcionam de verdade (checkbox, radio, switch, inputs),
  com os estados `disabled` reais e os anéis de foco exatos do design (Tab para ver).
- **inline-carousel-skeleton.html** — seta "next" rola o carrossel um card por vez.
- **color.html** — alterna entre ver os dois modos, só light ou só dark.
- **typography.html** e **border.html** — tabelas estáticas.

## Fidelidade

Os tokens de design (cores, raios, espaçamentos, sombras de foco, opacidades, tamanhos de fonte
e line-heights) foram extraídos do próprio arquivo Figma via MCP e estão declarados como CSS
custom properties no topo de cada arquivo.

Duas aproximações conscientes, por limitação do ambiente:

1. **Ícones** — os SVGs exportados pelo Figma expiram em ~7 dias e a rede do ambiente bloqueia
   downloads de `figma.com`. Os ícones foram redesenhados inline no mesmo estilo (traço fino,
   20×20).
2. **Fontes** — as fontes Anthropic (Anthropic Sans / Serif, Styrene, Tiempos) não são públicas.
   O CSS as declara primeiro e cai para um stack equivalente do sistema.

## Divergências encontradas no arquivo original

O arquivo Figma tem algumas inconsistências. Onde reproduzi-las produziria material de
referência incorreto, corrigi e documentei:

- **`color-text-disabled`** — o swatch está vinculado por engano a `text/inverse`. Prevaleceram
  os números R/G/B mostrados na linha (o primário a 50%).
- **`Background / Accent`** — os rótulos R/G/B não são atualizados por modo (mostram o mesmo
  valor em light e dark). Prevaleceu a variável vinculada ao swatch.
- **Coluna `Heading / Leading`** — repetia os nomes `…-size` em vez de `…-line-height`.
- **`Heading XL`** — aparecia como `ont-heading-xl-size`, sem o "f".
- **Estilos** — os dois primeiros usavam ambos `font-style-heading`; o primeiro virou
  `font-style-heading-large`.

## Ressalvas

- **`inline-carousel-skeleton.html`** não existe como tela no Figma. O arquivo tem o carrossel
  já preenchido ("Nearby trails"), mas nenhum estado de carregamento desenhado para ele.
  O skeleton foi construído seguindo as dimensões reais dos cards (220×280, gap 12) e o mesmo
  padrão de shimmer usado nos outros skeletons do arquivo.
- **`border.html`** — os nomes e a ordem dos tokens vêm da página original, mas os valores em px
  foram derivados do uso real nos componentes, não relidos da tabela de variáveis.

## Pendente

- Seção **"Examples"** (`455:241691`) — mockups mobile em tema claro e escuro.
- Carrossel **preenchido** e sua versão em tema escuro / mobile (`467:31022`).
- Variante **"Meta"** do App header e o App skeleton Fullscreen como componentes isolados.
