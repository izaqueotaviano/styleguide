# Recriações do Figma — MCP Apps for Claude

Telas, componentes e páginas de tokens do arquivo Figma **"MCP Apps for Claude (Community)"**
recriados em HTML/CSS/JS interativo. Cada arquivo é autocontido — abra direto no navegador,
sem build nem dependências.

## Arquivos

### Design tokens

| Arquivo | Página no Figma | Node |
|---|---|---|
| `color.html` | 🖌️ Color | `467:20292` |
| `typography.html` | 🔠 Typography | `7:19` |
| `border.html` | Border | `467:21770` |

### Componentes

| Arquivo | Página no Figma | Node |
|---|---|---|
| `forms.html` | 🖥️ Desktop web components → Forms (Controls) | `26:1233` |
| `ui-components.html` | 🖥️ Desktop web components → UI | `24:1672` |

### Telas — desktop

| Arquivo | Página no Figma | Node |
|---|---|---|
| `inline-card.html` | App → Inline card | `67:3145` |
| `fullscreen.html` | App → Fullscreen | `67:3156` |
| `inline-carousel.html` | 🎠 Inline carousel (preenchido, light + dark) | `467:31022` |
| `inline-carousel-skeleton.html` | Inline carousel — estado de carregamento | — |

### Telas — mobile

| Arquivo | Página no Figma | Node |
|---|---|---|
| `mobile-examples.html` | 📱 Mobile components → Examples | `467:51261` |

## O que é interativo

- **inline-card.html** — sidebar expande/colapsa (com Starred, Recents e account switcher),
  dropdown de título, seletor de modelo, feedback 👍/👎, copiar com toast, e o Spark
  ciclando entre Default → Thinking → Thinking (long) ao clicar em "regenerar".
- **fullscreen.html** — composer "Ask App" e botão de fechar o container.
- **inline-carousel.html** — alterna light/dark, seta percorre os cards (com wrap), e o marcador
  salva cada trilha.
- **inline-carousel-skeleton.html** — seta "next" rola o carrossel um card por vez.
- **mobile-examples.html** — as três telas (Sidebar, New chat, Active chat) em light e dark;
  o ícone de menu abre e fecha o drawer, o título cicla entre modelos, o composer e o feedback
  funcionam.
- **forms.html** — todos os controles funcionam de verdade (checkbox, radio, switch, inputs),
  com os estados `disabled` reais e os anéis de foco exatos do design (Tab para ver).
- **ui-components.html** — sidebar nas duas variantes, os três estados do Spark row, as duas
  versões do Chat input e as três do App header.
- **color.html** — alterna entre ver os dois modos, só light ou só dark.
- **typography.html** e **border.html** — tabelas estáticas.

## Fidelidade

Os tokens de design (cores, raios, espaçamentos, sombras de foco, opacidades, tamanhos de fonte
e line-heights) foram extraídos do próprio arquivo Figma via MCP e estão declarados como CSS
custom properties no topo de cada arquivo.

Três aproximações conscientes, por limitação do ambiente:

1. **Ícones** — os SVGs exportados pelo Figma expiram em ~7 dias e a rede do ambiente bloqueia
   downloads de `figma.com` (403 no proxy). Os ícones foram redesenhados inline no mesmo estilo.
2. **Fotos das trilhas** — mesmo motivo. Em `inline-carousel.html` são gradientes que aproximam
   a paleta de cada cena; a geometria do card e todos os textos são os reais.
3. **Fontes** — as fontes Anthropic (Anthropic Sans / Serif, Styrene, Tiempos) não são públicas.
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
  já preenchido, mas nenhum estado de carregamento desenhado para ele. O skeleton segue as
  dimensões reais dos cards (220×280, gap 12) e o padrão de shimmer usado nos outros skeletons.
- **`border.html`** — os nomes e a ordem dos tokens vêm da página original, mas os valores em px
  foram derivados do uso real nos componentes, não relidos da tabela de variáveis.
- **`inline-carousel.html`** — o 4º card ("Canyon Ridge Trail") é inventado. No Figma só três
  cards estão visíveis e o quarto fica atrás do fade, sem conteúdo legível.

## Ainda não recriado

A página **📱 Mobile components** tem mais dois frames além de Examples, que não foram feitos:

- **UI / Controls** (`455:246644`) — Button mobile, Composer (Resting/Active/Streaming/Stopping),
  icon button, radio, check, toggle, text field
- **UI / User Messaging & Navigation** (`732:5860`) — mensagens, greeting, footer controls,
  spark message, sidebar e nav bar mobile
- **App** (`459:26732`) — inline card mobile (Inline Loading / Inline Shimmer / Active),
  full screen e sheet
