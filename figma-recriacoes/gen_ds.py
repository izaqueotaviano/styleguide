#!/usr/bin/env python3
"""Gera o design system completo em um único HTML (para importar no Figma Make)."""
import csv, collections, pathlib, html

HERE = pathlib.Path(__file__).parent
OUT = HERE / "design-system.html"

# ---------------------------------------------------------------- dados
groups = collections.OrderedDict()
with (HERE / "colors.tsv").open() as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        groups.setdefault(r["GROUP"], []).append(r)

TEXT_SIZE = [("xs", 12, 16.8), ("sm", 14, 19.6), ("md", 16, 22.4), ("lg", 18, 25)]
HEAD_SIZE = [("xs", 12, 16.8), ("sm", 14, 19.6), ("md", 16, 22.4), ("lg", 20, 25),
             ("xl", 24, 30), ("2xl", 28, 30.8), ("3xl", 36, 36)]
WEIGHTS = [("normal", 400), ("medium", 500), ("semibold", 600), ("bold", 700)]
RADIUS = [("xs", "4px"), ("sm", "6px"), ("md", "8px"), ("lg", "10px"),
          ("xl", "12px"), ("2xl", "16px"), ("full", "9999px")]
SPACING = [("2xs", 4), ("xs", 8), ("sm", 12), ("md", 16), ("lg", 20),
           ("xl", 24), ("2xl", 32), ("3xl", 64)]
STYLES = [
    ("Display 3XL", "display", "3xl", 600, "Títulos de capa e valores de destaque"),
    ("Heading LG", "ui", "lg", 600, "Título de seção"),
    ("Body", "ui", "md", 400, "Texto corrido padrão"),
    ("Body emphasized", "ui", "md", 600, "Texto corrido com ênfase"),
    ("Body small", "ui", "sm", 400, "Texto de apoio"),
    ("Body small emphasized", "ui", "sm", 600, "Rótulo de botão e campo"),
    ("Caption", "ui", "xs", 400, "Metadados e legendas"),
    ("Caption emphasized", "ui", "xs", 600, "Tags e etiquetas"),
    ("Mono", "mono", "sm", 400, "SKU, CNPJ, códigos e valores tabulares"),
]

def esc(s): return html.escape(str(s))

def is_translucent(v):
    return v.startswith("rgba") and not v.rstrip(")").endswith("1")

# ---------------------------------------------------------------- CSS
CSS = r"""
:root{
  /* ---------- Tipografia: famílias ---------- */
  --font-display:'Martian Grotesk','Martian Grotesk Standard','Space Grotesk',Inter,system-ui,sans-serif;
  --font-ui:'Google Sans','Google Sans Text','Product Sans',Inter,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  --font-mono:'Martian Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;

  /* ---------- Tipografia: escala ---------- */
  --font-weight-normal:400; --font-weight-medium:500; --font-weight-semibold:600; --font-weight-bold:700;
  --font-text-xs-size:12px;  --font-text-xs-line-height:16.8px;
  --font-text-sm-size:14px;  --font-text-sm-line-height:19.6px;
  --font-text-md-size:16px;  --font-text-md-line-height:22.4px;
  --font-text-lg-size:18px;  --font-text-lg-line-height:25px;
  --font-heading-xs-size:12px;  --font-heading-xs-line-height:16.8px;
  --font-heading-sm-size:14px;  --font-heading-sm-line-height:19.6px;
  --font-heading-md-size:16px;  --font-heading-md-line-height:22.4px;
  --font-heading-lg-size:20px;  --font-heading-lg-line-height:25px;
  --font-heading-xl-size:24px;  --font-heading-xl-line-height:30px;
  --font-heading-2xl-size:28px; --font-heading-2xl-line-height:30.8px;
  --font-heading-3xl-size:36px; --font-heading-3xl-line-height:36px;

  /* ---------- Borda ---------- */
  --border-radius-xs:4px; --border-radius-sm:6px; --border-radius-md:8px; --border-radius-lg:10px;
  --border-radius-xl:12px; --border-radius-2xl:16px; --border-radius-full:9999px;
  --border-width-regular:0.5px;

  /* ---------- Espaçamento ---------- */
  --spacing-2xs:4px; --spacing-xs:8px; --spacing-sm:12px; --spacing-md:16px;
  --spacing-lg:20px; --spacing-xl:24px; --spacing-2xl:32px; --spacing-3xl:64px;

  /* ---------- Elevação ---------- */
  --shadow-low:0 1px 2px rgba(0,0,0,.05);
  --shadow-card:0 2px 8px rgba(0,0,0,.08);
  --shadow-window:0 12px 40px rgba(0,0,0,.06);
  --shadow-phone:0 8px 24px rgba(0,0,0,.12);
}

/* ---------- Cores: modo claro ---------- */
:root, [data-theme="light"]{
__LIGHT__
}
/* ---------- Cores: modo escuro ---------- */
[data-theme="dark"]{
__DARK__
}

/* ================================================================
   Base
   ================================================================ */
*{box-sizing:border-box}
[hidden]{display:none !important}
html{scroll-behavior:smooth}
body{
  margin:0;background:var(--color-background-tertiary);color:var(--color-text-primary);
  font-family:var(--font-ui);font-size:var(--font-text-md-size);line-height:var(--font-text-md-line-height);
  -webkit-font-smoothing:antialiased;
}

.wrap{max-width:1360px;margin:0 auto;padding:0 32px}

/* topo */
.topbar{
  position:sticky;top:0;z-index:50;background:var(--color-background-tertiary);
  border-bottom:var(--border-width-regular) solid var(--color-border-tertiary);
}
.topbar .wrap{display:flex;align-items:center;justify-content:space-between;gap:24px;height:60px}
.brand{display:flex;align-items:center;gap:10px;font-family:var(--font-display);font-weight:600;font-size:16px}
.brand .dot{width:26px;height:26px;border-radius:var(--border-radius-md);background:var(--brand);
  display:grid;place-items:center;color:#fff;font-size:14px}
.topnav{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}
.topnav::-webkit-scrollbar{display:none}
.topnav a{
  color:var(--color-text-tertiary);text-decoration:none;font-size:var(--font-text-sm-size);
  padding:6px 10px;border-radius:var(--border-radius-md);white-space:nowrap;
}
.topnav a:hover{background:var(--hover);color:var(--color-text-primary)}
.themetoggle{
  height:32px;padding:0 12px;border-radius:var(--border-radius-md);cursor:pointer;
  font-family:inherit;font-size:var(--font-text-sm-size);
  border:var(--border-width-regular) solid var(--color-border-primary);
  background:transparent;color:var(--color-text-primary);
}

/* capa */
.cover{padding:80px 0 56px;border-bottom:var(--border-width-regular) solid var(--color-border-tertiary)}
.cover h1{
  font-family:var(--font-display);font-size:clamp(40px,7vw,72px);line-height:1.02;
  font-weight:var(--font-weight-semibold);letter-spacing:-.03em;margin:0 0 20px;
}
.cover p{margin:0;max-width:62ch;font-size:var(--font-text-lg-size);line-height:var(--font-text-lg-line-height);color:var(--color-text-secondary)}
.meta{display:flex;flex-wrap:wrap;gap:32px;margin-top:40px}
.meta div{min-width:120px}
.meta .k{font-size:var(--font-text-xs-size);color:var(--color-text-tertiary);margin-bottom:4px}
.meta .v{font-family:var(--font-display);font-size:var(--font-heading-xl-size);line-height:1.1;font-weight:600}

/* seções */
section{padding:72px 0;border-bottom:var(--border-width-regular) solid var(--color-border-tertiary)}
.sechead{margin-bottom:40px}
.eyebrow{
  font-family:var(--font-mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--color-text-tertiary);margin:0 0 10px;
}
h2.title{font-family:var(--font-display);font-size:var(--font-heading-2xl-size);line-height:var(--font-heading-2xl-line-height);
  font-weight:600;letter-spacing:-.02em;margin:0 0 10px}
.sechead p{margin:0;max-width:70ch;color:var(--color-text-secondary);font-size:var(--font-text-sm-size);line-height:1.6}
h3.sub{font-family:var(--font-display);font-size:var(--font-heading-lg-size);line-height:var(--font-heading-lg-line-height);
  font-weight:600;margin:48px 0 16px}
h3.sub:first-of-type{margin-top:0}
.note{
  margin:16px 0 0;padding:14px 16px;border-radius:var(--border-radius-xl);
  background:var(--color-background-secondary);
  border:var(--border-width-regular) solid var(--color-border-tertiary);
  font-size:var(--font-text-sm-size);line-height:1.6;color:var(--color-text-secondary);max-width:82ch;
}
.note strong{color:var(--color-text-primary)}
code{font-family:var(--font-mono);font-size:.86em}

/* ================================================================
   Foundations — cor
   ================================================================ */
.ctable{border:var(--border-width-regular) solid var(--color-border-tertiary);border-radius:var(--border-radius-2xl);overflow:hidden;margin-bottom:32px}
.ctable .caption{
  padding:14px 18px;background:var(--color-background-secondary);
  border-bottom:var(--border-width-regular) solid var(--color-border-tertiary);
  font-weight:600;font-size:var(--font-text-sm-size);
}
.crow{
  display:grid;grid-template-columns:190px 1fr 160px 160px;gap:20px;align-items:center;
  padding:14px 18px;border-bottom:var(--border-width-regular) solid var(--color-border-tertiary);
  background:var(--color-background-primary);
}
.crow:last-child{border-bottom:0}
.crow .nm{font-size:var(--font-text-sm-size);font-weight:500}
.crow .vr{font-family:var(--font-mono);font-size:12px;color:var(--color-text-tertiary);word-break:break-all}
.sw{display:flex;align-items:center;gap:10px}
.sw .chipbox{
  width:44px;height:44px;flex:0 0 44px;border-radius:var(--border-radius-xl);position:relative;overflow:hidden;
  border:var(--border-width-regular) solid var(--color-border-secondary);
}
.sw .chipbox.alpha{
  background-image:linear-gradient(45deg,#ddd 25%,transparent 25%),linear-gradient(-45deg,#ddd 25%,transparent 25%),
    linear-gradient(45deg,transparent 75%,#ddd 75%),linear-gradient(-45deg,transparent 75%,#ddd 75%);
  background-size:12px 12px;background-position:0 0,0 6px,6px -6px,-6px 0;
}
.sw .chipbox i{position:absolute;inset:0;display:block}
.sw .hex{font-family:var(--font-mono);font-size:10px;color:var(--color-text-tertiary);line-height:1.35;
  word-break:break-all;min-width:0}
.colhead{display:grid;grid-template-columns:190px 1fr 160px 160px;gap:20px;padding:0 18px 10px;
  font-size:var(--font-text-xs-size);color:var(--color-text-tertiary)}

/* ================================================================
   Foundations — tipografia / borda / espaço
   ================================================================ */
.tgrid{display:flex;flex-wrap:wrap;gap:32px 48px}
.tcol{flex:1 1 260px;min-width:240px}
.trow{display:flex;align-items:center;gap:18px;padding:12px 0;border-bottom:var(--border-width-regular) solid var(--color-border-tertiary)}
.trow:last-child{border-bottom:0}
.tdemo{
  width:104px;flex:0 0 104px;height:60px;display:flex;align-items:center;justify-content:center;
  border-radius:var(--border-radius-md);background:var(--color-background-secondary);overflow:hidden;position:relative;
}
.tdemo .guide{position:absolute;left:14px;right:14px;background:rgba(70,130,213,.10);
  border-top:1px solid rgba(70,130,213,.5);border-bottom:1px solid rgba(70,130,213,.5)}
.tdemo span{position:relative;z-index:1}
.tinfo .nm{font-size:var(--font-text-sm-size);font-weight:600;line-height:1.3}
.tinfo .vr{font-family:var(--font-mono);font-size:11px;color:var(--color-text-tertiary);margin-top:2px;word-break:break-all}
.tinfo .vl{font-family:var(--font-mono);font-size:11px;color:var(--color-text-tertiary);opacity:.7}

.fontcard{
  border:var(--border-width-regular) solid var(--color-border-tertiary);border-radius:var(--border-radius-2xl);
  padding:28px;background:var(--color-background-primary);flex:1 1 300px;
}
.fontcard .spec{font-size:64px;line-height:1.1;margin-bottom:20px}
.fontcard .nm{font-size:var(--font-text-md-size);font-weight:600}
.fontcard .vr{font-family:var(--font-mono);font-size:12px;color:var(--color-text-tertiary);margin-top:4px;word-break:break-all}
.fontcard .use{margin-top:12px;font-size:var(--font-text-sm-size);color:var(--color-text-secondary);line-height:1.5}

.styleitem{padding:14px 0;border-bottom:var(--border-width-regular) solid var(--color-border-tertiary)}
.styleitem:last-child{border-bottom:0}
.styleitem .vr{font-family:var(--font-mono);font-size:11px;color:var(--color-text-tertiary);margin-top:6px}

.swatchrow{display:flex;flex-wrap:wrap;gap:20px}
.rbox{text-align:center}
.rbox .box{width:76px;height:76px;background:var(--color-background-info);
  border:1px solid var(--color-border-info);margin-bottom:8px}
.rbox .nm{font-size:var(--font-text-sm-size);font-weight:600}
.rbox .vr{font-family:var(--font-mono);font-size:11px;color:var(--color-text-tertiary)}
.spacerow{display:flex;align-items:flex-end;gap:20px;flex-wrap:wrap}
.sbox .bar{background:var(--color-background-info);border:1px solid var(--color-border-info);border-radius:2px;margin-bottom:8px}
.sbox .nm{font-size:var(--font-text-sm-size);font-weight:600}
.sbox .vr{font-family:var(--font-mono);font-size:11px;color:var(--color-text-tertiary)}

.elev{display:flex;flex-wrap:wrap;gap:24px}
.ecard{
  width:200px;height:120px;border-radius:var(--border-radius-xl);background:var(--color-background-primary);
  border:var(--border-width-regular) solid var(--color-border-tertiary);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;
}
.ecard .nm{font-size:var(--font-text-sm-size);font-weight:600}
.ecard .vr{font-family:var(--font-mono);font-size:11px;color:var(--color-text-tertiary)}

/* ================================================================
   Componentes
   ================================================================ */
.specimen{
  border:var(--border-width-regular) solid var(--color-border-tertiary);border-radius:var(--border-radius-2xl);
  background:var(--color-background-primary);padding:28px;margin-bottom:24px;
}
.specimen > .lbl{
  font-family:var(--font-mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;
  color:var(--color-text-tertiary);margin-bottom:18px;
}
.stack{display:flex;flex-direction:column;gap:14px}
.inline{display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.vlabel{font-size:11px;color:var(--color-text-tertiary);margin-bottom:6px;font-family:var(--font-mono)}
.grid2{display:flex;flex-wrap:wrap;gap:32px}

/* --- Button --- */
.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:8px;
  font-family:inherit;font-weight:var(--font-weight-semibold);border:none;cursor:pointer;white-space:nowrap;
  height:36px;padding:0 16px;border-radius:var(--border-radius-md);font-size:var(--font-heading-sm-size);
}
.btn svg{width:16px;height:16px}
.btn.default{background:var(--color-background-inverse);color:var(--color-text-inverse)}
.btn.secondary{background:transparent;color:var(--color-text-primary);
  border:var(--border-width-regular) solid var(--color-border-primary)}
.btn.danger{background:var(--color-background-danger);color:#fff}
.btn.brand{background:var(--brand);color:#fff}
.btn.small{height:32px;padding:0 12px;border-radius:var(--border-radius-sm);font-size:var(--font-heading-xs-size)}
.btn:disabled{opacity:.5;cursor:default}
.btn.danger:disabled{opacity:.6}
.btn.default:focus-visible{outline:none;box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-primary)}
.btn.secondary:focus-visible,.btn.brand:focus-visible{outline:none;box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-info)}
.btn.danger:focus-visible{outline:none;box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-danger)}
.btn.focus.default{box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-primary)}
.btn.focus.secondary,.btn.focus.brand{box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-info)}
.btn.focus.danger{box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-danger)}

/* --- Icon button --- */
.iconbtn{
  display:inline-flex;align-items:center;justify-content:center;cursor:pointer;
  background:transparent;border:none;color:var(--color-text-primary);
  width:32px;height:32px;border-radius:var(--border-radius-md);
}
.iconbtn.small{width:28px;height:28px;border-radius:var(--border-radius-sm)}
.iconbtn.secondary{border:var(--border-width-regular) solid var(--color-border-primary)}
.iconbtn:disabled{opacity:.5;cursor:default}
.iconbtn svg{width:20px;height:20px}
.iconbtn.small svg{width:16px;height:16px}
.iconbtn.focus{background:var(--color-background-primary);
  box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-info)}

/* --- Switch / Radio / Checkbox --- */
.switch{
  appearance:none;-webkit-appearance:none;margin:0;position:relative;cursor:pointer;flex:0 0 auto;
  background:var(--color-background-tertiary);border:var(--border-width-regular) solid var(--color-border-primary);
  border-radius:var(--border-radius-full);width:36px;height:20px;
}
.switch.small{width:28px;height:16px}
/* o nó é ancorado nas quatro bordas: fica centrado na altura e com folga igual
   dos dois lados, independentemente da espessura da borda do trilho */
.switch::after{
  content:'';position:absolute;top:2px;bottom:2px;left:2px;width:auto;aspect-ratio:1;
  background:#fff;border:var(--border-width-regular) solid var(--color-border-primary);
  border-radius:var(--border-radius-full);
}
.switch:checked{background:var(--color-border-info);border-color:var(--color-border-info)}
.switch:checked::after{left:auto;right:2px;border-color:var(--color-border-info)}
.switch:disabled{opacity:.5;cursor:default}
.switch:focus-visible{outline:none;box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-info)}

.radio{
  appearance:none;-webkit-appearance:none;margin:0;cursor:pointer;flex:0 0 auto;
  border:var(--border-width-regular) solid var(--color-border-primary);border-radius:var(--border-radius-full);
  background:var(--color-background-primary);width:20px;height:20px;
  display:inline-flex;align-items:center;justify-content:center;padding:3px;
}
.radio.small{width:16px;height:16px}
.radio:checked{border:1px solid var(--color-border-info)}
.radio:checked::after{content:'';display:block;width:100%;height:100%;border-radius:var(--border-radius-full);background:var(--color-border-info)}
.radio:disabled{opacity:.5;cursor:default}
.radio:focus-visible{outline:none;box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-info)}

.checkbox{
  appearance:none;-webkit-appearance:none;margin:0;cursor:pointer;position:relative;flex:0 0 auto;
  border:var(--border-width-regular) solid var(--color-border-secondary);background:var(--color-background-primary);
  width:20px;height:20px;border-radius:var(--border-radius-sm);
}
.checkbox.small{width:16px;height:16px;border-radius:var(--border-radius-xs)}
.checkbox:checked{background:var(--color-border-info);border-color:var(--color-border-info)}
.checkbox:checked::after{content:'';position:absolute;inset:0;background:#fff;
  -webkit-mask:url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M5 10.5l3 3 7-7.5" fill="none" stroke="black" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>') center/70% no-repeat;
  mask:url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M5 10.5l3 3 7-7.5" fill="none" stroke="black" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>') center/70% no-repeat}
.checkbox:disabled{opacity:.5;cursor:default}
.checkbox:focus-visible{outline:none;box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-info)}

/* --- Campos --- */
.input{
  font-family:inherit;background:var(--color-background-primary);
  border:1px solid var(--color-border-secondary);border-radius:var(--border-radius-md);
  padding:0 12px;color:var(--color-text-primary);font-size:var(--font-text-sm-size);
  width:200px;height:32px;
}
.input.large{height:40px}
.input::placeholder{color:var(--color-text-tertiary)}
.input:focus{outline:none;border-color:var(--color-border-primary);
  box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-info)}
.input.focus{border-color:var(--color-border-primary);
  box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-info)}
.input:disabled{opacity:.5}
.textarea{
  font-family:inherit;background:var(--color-background-primary);
  border:var(--border-width-regular) solid var(--color-border-secondary);border-radius:var(--border-radius-md);
  padding:16px;color:var(--color-text-primary);font-size:var(--font-text-sm-size);
  width:260px;height:110px;resize:vertical;line-height:1.4;
}
.textarea::placeholder{color:var(--color-text-tertiary)}
.textarea:focus{outline:none;border-color:var(--color-border-primary);
  box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var(--color-ring-info)}
.textarea:disabled{opacity:.5}

/* --- Tag --- */
.tag{
  display:inline-flex;align-items:center;height:22px;padding:0 8px;width:max-content;
  border-radius:var(--border-radius-xs);font-size:var(--font-heading-xs-size);
  font-weight:var(--font-weight-semibold);
}
.tag.info{background:var(--color-background-info);color:var(--color-text-info)}
.tag.successtone{background:var(--color-background-success);color:var(--color-text-success)}
.tag.warningtone{background:var(--color-background-warning);color:var(--color-text-warning)}
.tag.dangertone{background:var(--color-background-danger);color:#fff}

/* --- Chip --- */
.chip{
  height:32px;padding:0 14px;border-radius:var(--border-radius-full);cursor:pointer;font-family:inherit;
  border:var(--border-width-regular) solid var(--color-border-secondary);
  background:transparent;color:var(--color-text-secondary);font-size:var(--font-text-sm-size);
}
.chip[aria-pressed="true"]{background:var(--color-background-inverse);color:var(--color-text-inverse);border-color:transparent}

/* --- Skeleton --- */
.skel{display:flex;gap:20px;align-items:center;opacity:.2;width:100%}
.skel .dot{border-radius:var(--border-radius-full);background:var(--color-text-tertiary);flex:0 0 auto}
.skel .bar{flex:1 1 0;border-radius:var(--border-radius-md);background:var(--color-border-secondary)}
.skel.inlinecard .dot{width:32px;height:32px}
.skel.inlinecard .bar{height:32px}
.skel.fullscreen .dot{width:44px;height:44px}
.skel.fullscreen .bar{height:44px}

/* --- App header / container --- */
.appheader{
  width:400px;display:flex;align-items:center;justify-content:space-between;
  border-bottom:var(--border-width-regular) solid var(--color-border-tertiary);
  height:52px;padding:0 12px;
}
.appheader.close{height:auto;padding:16px 17px}
.appname{display:flex;align-items:center;gap:8px}
.glyph{width:20px;height:20px;border:1px solid var(--color-border-secondary);border-radius:5px;
  display:grid;place-items:center;font-size:11px;font-weight:700;line-height:1}
.appname .t{font-size:var(--font-text-sm-size)}
.appheader .metatxt{font-size:var(--font-text-xs-size);color:var(--color-text-tertiary)}
.appcontainer{
  width:440px;background:var(--color-background-primary);
  border:var(--border-width-regular) solid var(--color-border-secondary);
  border-radius:var(--border-radius-lg);overflow:hidden;
}
.appbody{display:flex;flex-direction:column;gap:24px;padding:24px}

/* --- Sidebar --- */
.sidebar{
  background:var(--color-background-tertiary);border:var(--border-width-regular) solid var(--color-border-secondary);
  border-radius:var(--border-radius-md);height:430px;display:flex;flex-direction:column;
  padding:8px 8px 12px;overflow:hidden;
}
.sidebar.collapsed{width:52px}
.sidebar.expanded{width:256px}
.sbhead{height:52px;display:flex;align-items:center;justify-content:center;flex:0 0 auto}
.sidebar.expanded .sbhead{justify-content:space-between;padding:0 8px}
.wordmark{font-family:var(--font-display);font-size:18px;font-weight:600}
.navrow{
  display:flex;align-items:center;gap:12px;height:36px;padding:0 8px;border-radius:var(--border-radius-md);
  border:0;background:transparent;cursor:pointer;width:100%;color:var(--color-text-primary);
  font-family:inherit;font-size:var(--font-text-sm-size);text-align:left;white-space:nowrap;
}
.navrow svg{width:20px;height:20px;flex:0 0 20px;color:var(--color-text-secondary)}
.sidebar.collapsed .navrow{justify-content:center;padding:0}
.sidebar.collapsed .navrow span{display:none}
.sbsec{margin-top:20px}
.sbsec .lb{font-size:var(--font-text-xs-size);color:var(--color-text-tertiary);padding:4px 4px 8px 8px}
.chatrow{
  height:32px;padding:0 14px 0 8px;border-radius:var(--border-radius-md);border:0;background:transparent;
  cursor:pointer;width:100%;text-align:left;font-family:inherit;font-size:var(--font-text-sm-size);
  color:var(--color-text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}
.chatrow.active{background:var(--color-background-secondary)}
.sbscroll{flex:1 1 auto;overflow:hidden}
.sbfoot{flex:0 0 auto;display:flex;align-items:center;gap:8px;padding:4px}
.avatar{width:28px;height:28px;flex:0 0 28px;border-radius:var(--border-radius-full);background:var(--accent-avatar);
  display:grid;place-items:center;color:#fff}
.avatar svg{width:15px;height:15px}
.acct{display:flex;flex-direction:column;white-space:nowrap}
.acct .n{font-size:var(--font-text-sm-size);line-height:19.6px;color:var(--color-text-secondary)}
.acct .p{font-size:var(--font-text-xs-size);line-height:16.8px;color:var(--color-text-tertiary)}
.sidebar.collapsed .acct{display:none}

/* --- Mensagens --- */
.bubble{
  background:var(--color-background-secondary);max-width:400px;border-radius:var(--border-radius-xl);
  padding:12px 16px 12px 12px;font-size:var(--font-text-md-size);line-height:var(--font-text-md-line-height);
}
.bubble b{font-weight:var(--font-weight-semibold)}
.claudetext{font-family:var(--font-ui);font-size:var(--font-text-md-size);line-height:1.6;margin:0;max-width:560px}
.sparkrow{display:flex;align-items:center;gap:12px;height:36px}
.spark{width:28px;height:28px;color:var(--brand);flex:0 0 28px}
.thinking{font-style:italic;font-size:var(--font-text-sm-size);color:var(--color-text-secondary)}

/* --- Chat input --- */
.composer{
  width:460px;background:var(--color-background-primary);
  border:var(--border-width-regular) solid var(--color-border-secondary);
  border-radius:var(--border-radius-2xl);overflow:hidden;box-shadow:var(--shadow-card);
}
.composer .in{padding:12px 16px;font-size:var(--font-text-md-size);color:var(--color-text-tertiary)}
.composer .ctrl{display:flex;align-items:center;justify-content:space-between;padding:12px}
.composer .right{display:flex;align-items:center;gap:8px}
.model{display:flex;align-items:center;gap:4px;height:32px;padding:0 4px 0 8px;border:0;background:transparent;
  cursor:pointer;font-family:var(--font-display);font-size:var(--font-text-sm-size);
  color:var(--color-text-primary);border-radius:var(--border-radius-md)}
.model svg{width:20px;height:20px;color:var(--color-text-secondary)}
.send{width:32px;height:32px;border-radius:var(--border-radius-md);
  border:var(--border-width-regular) solid var(--color-border-secondary);
  background:var(--brand);color:#fff;display:grid;place-items:center;cursor:pointer}
.send svg{width:16px;height:16px}
.composer.single{display:flex;align-items:center;justify-content:space-between;padding:12px;gap:8px}
.composer.single .in{flex:1;padding:4px}

/* --- Titlebar --- */
.titlebar{
  width:460px;height:68px;background:var(--color-background-tertiary);display:flex;align-items:center;
  justify-content:space-between;padding:16px;border-radius:var(--border-radius-md);
}
.tchip{display:flex;align-items:center;gap:6px;height:36px;padding:4px 4px 4px 8px;
  border-radius:var(--border-radius-sm);background:transparent;border:0;cursor:pointer;
  font-family:inherit;font-size:var(--font-text-md-size);color:var(--color-text-primary)}
.tchip svg{width:20px;height:20px;color:var(--color-text-secondary)}
.share{min-width:75px;height:36px;padding:0 12px;
  border:var(--border-width-regular) solid var(--color-border-secondary);
  border-radius:var(--border-radius-md);background:transparent;cursor:pointer;
  font-family:inherit;font-size:var(--font-text-sm-size);color:var(--color-text-primary)}

/* ================================================================
   Telas
   ================================================================ */
.screengrid{display:flex;flex-wrap:wrap;gap:40px}
.screenwrap .cap{font-size:var(--font-text-sm-size);font-weight:600;margin-bottom:10px}
.screenwrap .capsub{font-size:var(--font-text-xs-size);color:var(--color-text-tertiary);margin-bottom:12px}

/* janela desktop */
.window{
  width:820px;height:520px;background:var(--color-background-tertiary);
  border:var(--border-width-regular) solid var(--color-border-secondary);
  border-radius:var(--border-radius-2xl);overflow:hidden;display:flex;box-shadow:var(--shadow-window);
}
.rail{
  flex:0 0 52px;background:var(--color-background-secondary);
  border-right:var(--border-width-regular) solid var(--color-border-secondary);
  display:flex;flex-direction:column;justify-content:space-between;align-items:center;padding:8px 0 12px;
}
.rail .items{display:flex;flex-direction:column;gap:4px;align-items:center}
.rail button{width:36px;height:36px;border:0;background:transparent;border-radius:var(--border-radius-md);
  cursor:pointer;display:grid;place-items:center;color:var(--color-text-secondary)}
.rail svg{width:20px;height:20px}
.wmain{flex:1 1 auto;min-width:0;display:flex;flex-direction:column;position:relative}
.wtop{height:60px;flex:0 0 60px;display:flex;align-items:center;justify-content:space-between;padding:0 16px;
  border-bottom:var(--border-width-regular) solid var(--color-border-tertiary)}
.wbody{flex:1 1 auto;overflow:hidden;padding:24px;display:flex;flex-direction:column;gap:16px;align-items:center}
.thread{width:100%;max-width:560px;display:flex;flex-direction:column;gap:16px}
.userrow{display:flex;justify-content:flex-end}

/* telefone */
.phone{
  width:300px;height:600px;position:relative;overflow:hidden;
  border-radius:36px;border:1px solid var(--color-border-secondary);
  background:var(--color-background-tertiary);box-shadow:var(--shadow-phone);
  display:flex;flex-direction:column;
}
.pstatus{height:38px;flex:0 0 38px;padding:14px 16px 0;display:flex;align-items:center;justify-content:space-between;font-size:13px;font-weight:600}
.pnav{height:46px;flex:0 0 46px;padding:0 12px;display:flex;align-items:center;justify-content:space-between;gap:8px}
.pnavbtn{width:36px;height:36px;flex:0 0 36px;border-radius:var(--border-radius-full);border:0;
  background:var(--color-background-primary);box-shadow:var(--shadow-card);display:grid;place-items:center;
  color:var(--color-text-primary)}
.pnavbtn svg{width:20px;height:20px}
.pttl{flex:1;text-align:center}
.pttl .t{font-size:15px;font-weight:600;line-height:1.2}
.pttl .s{font-family:var(--font-mono);font-size:10px;color:var(--color-text-tertiary)}
.pbody{flex:1 1 auto;overflow:hidden;padding:0 14px}
.pfoot{flex:0 0 auto;padding:10px 14px 22px;background:var(--color-background-primary);
  border-top:var(--border-width-regular) solid var(--color-border-tertiary);display:flex;align-items:center;gap:10px}
.pcart{display:flex;flex-direction:column;gap:1px}
.pcart .c{font-size:10px;color:var(--color-text-tertiary)}
.pcart .v{font-family:var(--font-display);font-size:18px;line-height:1.1;font-weight:600}
.pfoot .btn{flex:1;height:40px;font-size:var(--font-text-sm-size)}

.pill{display:flex;align-items:center;gap:6px;height:26px;padding:0 10px;border-radius:var(--border-radius-full);
  background:var(--color-background-success);color:var(--color-text-success);
  border:var(--border-width-regular) solid var(--color-border-success);font-size:11px}
.pill .pip{width:6px;height:6px;border-radius:50%;background:currentColor}

.steps{display:flex;gap:6px;padding:0 14px 12px}
.stp{flex:1}
.stp .bar{height:3px;border-radius:2px;background:var(--color-border-tertiary);margin-bottom:6px}
.stp.on .bar{background:var(--color-background-inverse)}
.stp .lb{font-size:9px;color:var(--color-text-tertiary)}
.stp.on .lb{color:var(--color-text-primary);font-weight:600}

.reccard{
  display:flex;align-items:flex-start;gap:10px;padding:12px;width:100%;
  background:var(--color-background-primary);border:var(--border-width-regular) solid var(--color-border-tertiary);
  border-radius:var(--border-radius-2xl);margin-bottom:8px;
}
.reccard .ico{width:34px;height:34px;flex:0 0 34px;border-radius:var(--border-radius-xl);
  background:var(--color-background-secondary);display:grid;place-items:center;
  font-size:12px;font-weight:600;color:var(--color-text-secondary)}
.reccard .b{flex:1;min-width:0;display:flex;flex-direction:column;gap:3px}
.reccard .n{font-size:14px;font-weight:600;line-height:1.3}
.reccard .m{font-size:11px;color:var(--color-text-tertiary)}
.reccard .m .mono{font-family:var(--font-mono)}

.money{font-family:var(--font-display);font-weight:600}

footer{padding:56px 0 80px;color:var(--color-text-tertiary);font-size:var(--font-text-sm-size);line-height:1.7}
footer a{color:var(--color-text-secondary)}
@media (max-width:900px){
  .crow,.colhead{grid-template-columns:1fr;gap:10px}
  .colhead{display:none}
  .wrap{padding:0 20px}
}
"""

# ---------------------------------------------------------------- ícones
IC = {
    "plus": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><line x1="10" y1="4" x2="10" y2="16"/><line x1="4" y1="10" x2="16" y2="10"/></svg>',
    "code": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7.5 6 4 10l3.5 4"/><path d="M12.5 6 16 10l-3.5 4"/></svg>',
    "close": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><line x1="5" y1="5" x2="15" y2="15"/><line x1="15" y1="5" x2="5" y2="15"/></svg>',
    "caret": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 8.5 10 12l3.5-3.5"/></svg>',
    "side": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="14" height="12" rx="2.5"/><line x1="8" y1="4" x2="8" y2="16"/></svg>',
    "chat": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3.5 12V6.5a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H7l-3.5 2.2V12Z"/><path d="M8 13.2v.3a2 2 0 0 0 2 2h4l2.5 1.6V10a2 2 0 0 0-1.5-1.94"/></svg>',
    "newchat": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 15.5V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2H8l-4 2.5Z"/><line x1="10" y1="6.5" x2="10" y2="10.5"/><line x1="8" y1="8.5" x2="12" y2="8.5"/></svg>',
    "proj": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3.5 6.5A1.5 1.5 0 0 1 5 5h3l1.5 2H15a1.5 1.5 0 0 1 1.5 1.5v5A1.5 1.5 0 0 1 15 15H5a1.5 1.5 0 0 1-1.5-1.5v-7Z"/></svg>',
    "art": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3.5" y="3.5" width="6" height="6" rx="1.5"/><rect x="10.5" y="3.5" width="6" height="6" rx="1.5"/><rect x="3.5" y="10.5" width="6" height="6" rx="1.5"/><rect x="10.5" y="10.5" width="6" height="6" rx="1.5"/></svg>',
    "back": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12.5 4 6.5 10l6 6"/></svg>',
    "arrow": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h9"/><path d="M8.5 4.5 12 8l-3.5 3.5"/></svg>',
    "up": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="13" x2="8" y2="3.5"/><path d="M4 7 8 3l4 4"/></svg>',
    "avatar": '<svg viewBox="0 0 20 20" fill="currentColor"><path d="M10 3.5 12 8.5 17 10.5 12 12.5 10 17.5 8 12.5 3 10.5 8 8.5Z"/></svg>',
    "spark": '<svg viewBox="0 0 28 28" fill="currentColor"><path d="M14 1.5c.5 3.2.9 4.9 1.9 6 1 1 2.7 1.4 6 1.9-3.3.5-5 .9-6 1.9-1 1-1.4 2.7-1.9 6-.5-3.3-.9-5-1.9-6-1-1-2.7-1.4-6-1.9 3.3-.5 5-.9 6-1.9 1-1.1 1.4-2.8 1.9-6Z"/></svg>',
    "search": '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="9" cy="9" r="5.2"/><line x1="13" y1="13" x2="16.5" y2="16.5"/></svg>',
}

# ---------------------------------------------------------------- foundations
def css_vars(mode):
    key = "LIGHT" if mode == "light" else "DARK"
    lines = []
    for rows in groups.values():
        for r in rows:
            lines.append(f"  --{r['VAR']}:{r[key]};")
    extra = {
        "light": ["  --brand:#c6613f;", "  --brand-hover:#b5573a;",
                  "  --accent-avatar:#c46686;", "  --hover:rgba(31,30,29,.06);"],
        "dark":  ["  --brand:#c6613f;", "  --brand-hover:#d0724f;",
                  "  --accent-avatar:#c46686;", "  --hover:rgba(255,255,255,.07);"],
    }[mode]
    return "\n".join(lines + extra)

def color_section():
    out = ['<div class="colhead"><span>Nome</span><span>Variável</span><span>Light</span><span>Dark</span></div>']
    for gname, rows in groups.items():
        out.append('<div class="ctable">')
        out.append(f'<div class="caption">{esc(gname)}</div>')
        for r in rows:
            cells = []
            for mode in ("LIGHT", "DARK"):
                v = r[mode]
                cls = "chipbox alpha" if is_translucent(v) else "chipbox"
                cells.append(
                    f'<div class="sw"><span class="{cls}"><i style="background:{esc(v)}"></i></span>'
                    f'<span class="hex">{esc(v)}</span></div>')
            out.append(
                f'<div class="crow"><span class="nm">{esc(r["NAME"])}</span>'
                f'<span class="vr">--{esc(r["VAR"])}</span>{cells[0]}{cells[1]}</div>')
        out.append("</div>")
    return "\n".join(out)

def type_section():
    fonts = [
        ("Martian Grotesk", "--font-display", "Aa", "Títulos, valores monetários e números de destaque."),
        ("Google Sans", "--font-ui", "Aa", "Toda a interface: rótulos, corpo de texto, campos e botões."),
        ("Martian Mono", "--font-mono", "Aa", "SKU, CNPJ, códigos e números em tabela. Companheira da Martian Grotesk."),
    ]
    out = ['<div class="tgrid" style="margin-bottom:8px">']
    for nm, var, spec, use in fonts:
        fam = {"--font-display": "var(--font-display)", "--font-ui": "var(--font-ui)", "--font-mono": "var(--font-mono)"}[var]
        out.append(
            f'<div class="fontcard"><div class="spec" style="font-family:{fam}">{spec}</div>'
            f'<div class="nm">{esc(nm)}</div><div class="vr">{esc(var)}</div>'
            f'<div class="use">{esc(use)}</div></div>')
    out.append("</div>")

    out.append('<h3 class="sub">Peso</h3><div class="tgrid"><div class="tcol">')
    for nm, w in WEIGHTS:
        out.append(
            f'<div class="trow"><div class="tdemo"><span style="font-weight:{w};font-size:18px">{w}</span></div>'
            f'<div class="tinfo"><div class="nm">{esc(nm.capitalize())}</div>'
            f'<div class="vr">--font-weight-{nm}</div></div></div>')
    out.append("</div></div>")

    def scale(title, items, prefix, weight):
        h = [f'<h3 class="sub">{title}</h3><div class="tgrid"><div class="tcol">']
        h.append('<div class="vlabel">Tamanho</div>')
        for k, size, _ in items:
            h.append(
                f'<div class="trow"><div class="tdemo"><span style="font-size:{size}px;font-weight:{weight}">{k.upper()}</span></div>'
                f'<div class="tinfo"><div class="nm">{title.split("/")[0].strip()} {k.upper()}</div>'
                f'<div class="vr">--font-{prefix}-{k}-size</div><div class="vl">{size}px</div></div></div>')
        h.append('</div><div class="tcol"><div class="vlabel">Entrelinha</div>')
        for k, size, lh in items:
            h.append(
                f'<div class="trow"><div class="tdemo">'
                f'<span class="guide" style="height:{lh}px"></span>'
                f'<span style="font-size:{size}px;line-height:{lh}px;font-weight:{weight}">{k.upper()}</span></div>'
                f'<div class="tinfo"><div class="nm">{title.split("/")[0].strip()} {k.upper()}</div>'
                f'<div class="vr">--font-{prefix}-{k}-line-height</div><div class="vl">{lh}px</div></div></div>')
        h.append("</div></div>")
        return "\n".join(h)

    out.append(scale("Text / escala", TEXT_SIZE, "text", 400))
    out.append(scale("Heading / escala", HEAD_SIZE, "heading", 600))

    out.append('<h3 class="sub">Estilos</h3><div class="tgrid"><div class="tcol" style="flex:1 1 100%">')
    for nm, fam, key, w, desc in STYLES:
        famvar = {"display": "var(--font-display)", "ui": "var(--font-ui)", "mono": "var(--font-mono)"}[fam]
        size = f"var(--font-{'heading' if key in dict((k,1) for k,_,_ in HEAD_SIZE) and fam=='display' else 'text'}-{key}-size)"
        # usa a escala heading quando o peso é semibold, senão text
        base = "heading" if w >= 600 else "text"
        size = f"var(--font-{base}-{key}-size)"
        lh = f"var(--font-{base}-{key}-line-height)"
        out.append(
            f'<div class="styleitem"><div style="font-family:{famvar};font-size:{size};line-height:{lh};font-weight:{w}">{esc(nm)}</div>'
            f'<div class="vr">font-style-{nm.lower().replace(" ", "-")} · {esc(desc)}</div></div>')
    out.append("</div></div>")
    return "\n".join(out)

def border_section():
    out = ['<h3 class="sub">Raio</h3><div class="swatchrow">']
    for k, v in RADIUS:
        out.append(
            f'<div class="rbox"><div class="box" style="border-radius:{v}"></div>'
            f'<div class="nm">{k.upper()}</div><div class="vr">--border-radius-{k}</div>'
            f'<div class="vr">{v}</div></div>')
    out.append('</div><h3 class="sub">Espessura</h3><div class="swatchrow">')
    out.append(
        '<div class="rbox" style="text-align:left"><div style="width:200px;border-top:var(--border-width-regular) solid var(--color-border-info);margin:38px 0"></div>'
        '<div class="nm">Regular</div><div class="vr">--border-width-regular</div><div class="vr">0.5px</div></div>')
    out.append("</div>")
    return "\n".join(out)

def spacing_section():
    out = ['<div class="spacerow">']
    for k, v in SPACING:
        out.append(
            f'<div class="sbox"><div class="bar" style="width:{max(v,8)}px;height:{v*2}px"></div>'
            f'<div class="nm">{k.upper()}</div><div class="vr">--spacing-{k}</div><div class="vr">{v}px</div></div>')
    out.append("</div>")
    return "\n".join(out)

def elevation_section():
    shadows = [
        ("Low", "--shadow-low", "0 1px 2px rgba(0,0,0,.05)"),
        ("Card", "--shadow-card", "0 2px 8px rgba(0,0,0,.08)"),
        ("Window", "--shadow-window", "0 12px 40px rgba(0,0,0,.06)"),
        ("Phone", "--shadow-phone", "0 8px 24px rgba(0,0,0,.12)"),
    ]
    out = ['<div class="elev">']
    for nm, var, val in shadows:
        out.append(f'<div class="ecard" style="box-shadow:var({var})"><div class="nm">{esc(nm)}</div><div class="vr">{esc(var)}</div></div>')
    out.append("</div>")
    out.append('<h3 class="sub">Anéis de foco</h3>')
    out.append('<p class="sechead" style="margin-bottom:20px;color:var(--color-text-secondary);font-size:14px">'
               'Dois anéis: 2px na cor do fundo, depois 3.5px na cor do ring. Separa o elemento do halo em qualquer superfície.</p>')
    out.append('<div class="elev">')
    for nm, ring in [("Primary", "--color-ring-primary"), ("Info", "--color-ring-info"), ("Danger", "--color-ring-danger")]:
        out.append(
            f'<div class="ecard" style="box-shadow:0 0 0 2px var(--color-background-primary),0 0 0 3.5px var({ring})">'
            f'<div class="nm">{esc(nm)}</div><div class="vr">{esc(ring)}</div></div>')
    out.append("</div>")
    return "\n".join(out)

# ---------------------------------------------------------------- montagem parcial
HEAD = """<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Design System — base Convertize</title>
<style>
__CSS__
</style>
</head>
<body data-theme="light">

<div class="topbar">
  <div class="wrap">
    <div class="brand"><span class="dot">◆</span> Design System</div>
    <nav class="topnav">
      <a href="#cor">Cor</a>
      <a href="#tipografia">Tipografia</a>
      <a href="#borda">Borda</a>
      <a href="#espaco">Espaço</a>
      <a href="#elevacao">Elevação</a>
      <a href="#componentes">Componentes</a>
      <a href="#telas">Telas</a>
    </nav>
    <button class="themetoggle" id="themeBtn">Tema escuro</button>
  </div>
</div>

<div class="wrap">
  <header class="cover">
    <h1>Design System</h1>
    <p>Fundações, componentes e telas derivados do arquivo <em>MCP Apps for Claude</em>,
       com a tipografia trocada para <strong>Martian Grotesk</strong> e <strong>Google Sans</strong>.
       Tudo em um arquivo só, com o conteúdo no HTML — pronto para importar no Figma Make.</p>
    <div class="meta">
      <div><div class="k">Tokens de cor</div><div class="v">__NCOLORS__</div></div>
      <div><div class="k">Modos</div><div class="v">2</div></div>
      <div><div class="k">Escala de texto</div><div class="v">__NTYPE__</div></div>
      <div><div class="k">Raios</div><div class="v">__NRADIUS__</div></div>
      <div><div class="k">Componentes</div><div class="v">16</div></div>
    </div>
  </header>
</div>
"""

def section(id_, eyebrow, title, desc, body):
    return f"""
<section id="{id_}">
  <div class="wrap">
    <div class="sechead">
      <p class="eyebrow">{esc(eyebrow)}</p>
      <h2 class="title">{esc(title)}</h2>
      <p>{desc}</p>
    </div>
    {body}
  </div>
</section>
"""

parts = [
    HEAD.replace("__CSS__", CSS.replace("__LIGHT__", css_vars("light")).replace("__DARK__", css_vars("dark")))
        .replace("__NCOLORS__", str(sum(len(v) for v in groups.values())))
        .replace("__NTYPE__", str(len(TEXT_SIZE) + len(HEAD_SIZE)))
        .replace("__NRADIUS__", str(len(RADIUS))),
    section("cor", "Fundações", "Cor",
            "Os 37 tokens semânticos em quatro famílias — Background, Text, Border e Ring — cada uma dividida "
            "entre Surface (neutros) e Accent (estados). Cada token tem valor próprio em modo claro e escuro; "
            "é essa dupla que faz o tema inteiro virar com uma variável só.",
            color_section()),
    section("tipografia", "Fundações", "Tipografia",
            "Três famílias com papéis separados. A escala tem duas trilhas: <code>text</code> para leitura "
            "e <code>heading</code> para títulos e ênfase — mesma nomenclatura, pesos diferentes.",
            type_section()),
    section("borda", "Fundações", "Borda",
            "Raio e espessura. A borda de 0,5px é a assinatura do sistema: separa superfícies sem pesar.",
            border_section()),
    section("espaco", "Fundações", "Espaço",
            "Escala de espaçamento derivada do uso real nos componentes — múltiplos de 4.",
            spacing_section()),
    section("elevacao", "Fundações", "Elevação e foco",
            "Sombras por contexto e os anéis de foco. Navegue por <kbd>Tab</kbd> nos componentes para vê-los em ação.",
            elevation_section()),
]

OUT.write_text("".join(parts), encoding="utf-8")
print("parcial:", OUT, OUT.stat().st_size, "bytes")

# ================================================================
#  COMPONENTES
# ================================================================
def spec(label, body):
    return f'<div class="specimen"><div class="lbl">{esc(label)}</div>{body}</div>'

def btn_row(variant, label):
    cells = []
    for size, scls in (("Default", ""), ("Small", " small")):
        cells.append(f'<button class="btn {variant}{scls}">Button</button>')
        cells.append(f'<button class="btn {variant}{scls} focus">Button</button>')
        cells.append(f'<button class="btn {variant}{scls}" disabled>Button</button>')
    return (f'<div><div class="vlabel">Variant={label} · Default / Focused / Disabled · tamanhos Default e Small</div>'
            f'<div class="inline">{"".join(cells)}</div></div>')

buttons = spec("Button", '<div class="stack">'
    + btn_row("default", "Default") + btn_row("secondary", "Secondary")
    + btn_row("danger", "Danger") + btn_row("brand", "Brand") + '</div>')

iconbtns = spec("Icon button", '<div class="stack">'
    f'<div><div class="vlabel">Variant=Ghost · Default / Focused / Disabled</div><div class="inline">'
    f'<button class="iconbtn">{IC["plus"]}</button>'
    f'<button class="iconbtn focus">{IC["plus"]}</button>'
    f'<button class="iconbtn" disabled>{IC["plus"]}</button>'
    f'<button class="iconbtn small">{IC["plus"]}</button>'
    f'<button class="iconbtn small focus">{IC["plus"]}</button>'
    f'<button class="iconbtn small" disabled>{IC["plus"]}</button></div></div>'
    f'<div><div class="vlabel">Variant=Secondary</div><div class="inline">'
    f'<button class="iconbtn secondary">{IC["plus"]}</button>'
    f'<button class="iconbtn secondary focus">{IC["plus"]}</button>'
    f'<button class="iconbtn secondary" disabled>{IC["plus"]}</button>'
    f'<button class="iconbtn secondary small">{IC["plus"]}</button>'
    f'<button class="iconbtn secondary small" disabled>{IC["plus"]}</button></div></div>'
    '</div>')

def toggles():
    rows = []
    for cls, name in (("switch", "Switch"), ("radio", "Radio"), ("checkbox", "Checkbox")):
        tag = "input"
        typ = "checkbox" if cls != "radio" else "radio"
        big, small = "", " small"
        r = [f'<div><div class="vlabel">{name} · Large e Small · normal / marcado / desabilitado / marcado+desabilitado</div><div class="inline">']
        for sz in (big, small):
            r.append(f'<{tag} type="{typ}" class="{cls}{sz}">')
            r.append(f'<{tag} type="{typ}" class="{cls}{sz}" checked>')
            r.append(f'<{tag} type="{typ}" class="{cls}{sz}" disabled>')
            r.append(f'<{tag} type="{typ}" class="{cls}{sz}" checked disabled>')
        r.append("</div></div>")
        rows.append("".join(r))
    return spec("Switch · Radio · Checkbox", '<div class="stack">' + "".join(rows) + "</div>")

fields = spec("Text input · Text area", '<div class="stack">'
    '<div><div class="vlabel">Text input · Default e Large · Default / Focused / Disabled</div><div class="inline">'
    '<input class="input" placeholder="Placeholder">'
    '<input class="input focus" placeholder="Placeholder" value="Focused">'
    '<input class="input" placeholder="Placeholder" disabled>'
    '<input class="input large" placeholder="Placeholder">'
    '<input class="input large focus" placeholder="Placeholder" value="Focused">'
    '<input class="input large" placeholder="Placeholder" disabled></div></div>'
    '<div><div class="vlabel">Text area · Default / Disabled</div><div class="inline">'
    '<textarea class="textarea" placeholder="Placeholder"></textarea>'
    '<textarea class="textarea" placeholder="Placeholder" disabled></textarea></div></div>'
    '</div>')

tags = spec("Tag · Chip", '<div class="stack">'
    '<div><div class="vlabel">Tag · tons semânticos</div><div class="inline">'
    '<span class="tag info">Primeira compra</span>'
    '<span class="tag successtone">Recorrente</span>'
    '<span class="tag warningtone">Estoque baixo</span>'
    '<span class="tag dangertone">Bloqueado</span></div></div>'
    '<div><div class="vlabel">Chip · filtro</div><div class="inline">'
    '<button class="chip" aria-pressed="true">Todos</button>'
    '<button class="chip">Águas</button>'
    '<button class="chip">Refrigerantes</button>'
    '<button class="chip">Mercearia</button></div></div>'
    '</div>')

skeleton = spec("App skeleton", '<div class="stack">'
    '<div style="width:400px"><div class="vlabel">Size=Inline card</div>'
    '<div class="skel inlinecard"><span class="dot"></span><span class="bar"></span><span class="bar"></span><span class="bar"></span></div></div>'
    '<div style="width:400px"><div class="vlabel">Size=Fullscreen</div>'
    '<div class="skel fullscreen"><span class="dot"></span><span class="bar"></span><span class="bar"></span><span class="bar"></span></div></div>'
    '</div>')

appheaders = spec("App header · App container", '<div class="stack">'
    f'<div><div class="vlabel">Accessory=Expand</div><div class="appheader">'
    f'<div class="appname"><span class="glyph">A</span><span class="t">App</span></div>'
    f'<button class="iconbtn">{IC["code"]}</button></div></div>'
    f'<div><div class="vlabel">Accessory=Meta</div><div class="appheader">'
    f'<div class="appname"><span class="glyph">A</span><span class="t">App</span></div>'
    f'<span class="metatxt">5 pages found</span></div></div>'
    f'<div><div class="vlabel">Accessory=Close</div><div class="appheader close">'
    f'<div class="appname"><span class="glyph">A</span><span class="t">App</span></div>'
    f'<button class="iconbtn">{IC["close"]}</button></div></div>'
    f'<div><div class="vlabel">App container</div><div class="appcontainer">'
    f'<div class="appheader" style="width:100%">'
    f'<div class="appname"><span class="glyph">A</span><span class="t">App</span></div>'
    f'<button class="iconbtn">{IC["code"]}</button></div>'
    f'<div class="appbody">'
    + ('<div class="skel inlinecard"><span class="dot"></span><span class="bar"></span><span class="bar"></span><span class="bar"></span></div>' * 3)
    + '</div></div></div></div>')

def sidebar(expanded):
    cls = "expanded" if expanded else "collapsed"
    nav = "".join(
        f'<button class="navrow">{IC[k]}<span>{lbl}</span></button>'
        for k, lbl in (("newchat", "New chat"), ("chat", "Chats"), ("proj", "Projects"), ("art", "Artifacts"), ("code", "Code")))
    body = ""
    if expanded:
        body = ('<div class="sbscroll"><div class="sbsec"><div class="lb">Recents</div>'
                '<button class="chatrow active">Make a Fairy Story</button>'
                '<button class="chatrow">Springtime Poetry</button>'
                '<button class="chatrow">Data Migration Plan</button></div></div>')
    else:
        body = '<div class="sbscroll"></div>'
    head = (f'<span class="wordmark">Claude</span><button class="iconbtn">{IC["side"]}</button>'
            if expanded else f'<button class="iconbtn">{IC["side"]}</button>')
    acct = ('<span class="acct"><span class="n">Sarah Chen</span><span class="p">Pro plan</span></span>' if expanded else "")
    return (f'<div class="sidebar {cls}"><div class="sbhead">{head}</div>'
            f'<div>{nav}</div>{body}'
            f'<div class="sbfoot"><span class="avatar">{IC["avatar"]}</span>{acct}</div></div>')

sidebars = spec("Sidebar", '<div class="inline" style="align-items:flex-start;gap:24px">'
    f'<div><div class="vlabel">Collapsed=false</div>{sidebar(True)}</div>'
    f'<div><div class="vlabel">Collapsed=true</div>{sidebar(False)}</div></div>')

messages = spec("Titlebar · Mensagens · Spark row", '<div class="stack">'
    f'<div><div class="vlabel">Chat titlebar</div><div class="titlebar">'
    f'<button class="tchip">Product roadmap {IC["caret"]}</button>'
    f'<button class="share">Share</button></div></div>'
    '<div><div class="vlabel">User message</div>'
    '<div style="width:460px;display:flex;justify-content:flex-end">'
    '<div class="bubble">Create a sprint planning page in <b>App</b> for today’s meeting</div></div></div>'
    '<div><div class="vlabel">Claude response</div>'
    '<p class="claudetext">Here’s a sprint planning template with a standard agenda. '
    'Review and hit Create page when it looks right.</p></div>'
    f'<div><div class="vlabel">Spark row · State=Default / Thinking / Thinking (long)</div>'
    f'<div class="sparkrow"><span class="spark">{IC["spark"]}</span></div>'
    f'<div class="sparkrow"><span class="spark">{IC["spark"]}</span></div>'
    f'<div class="sparkrow"><span class="spark">{IC["spark"]}</span>'
    f'<span class="thinking">Thinking deeply, stand by…</span></div></div>'
    '</div>')

composer = spec("Chat input", '<div class="stack">'
    f'<div><div class="vlabel">Size=Multiline</div><div class="composer">'
    f'<div class="in">Reply to Claude</div>'
    f'<div class="ctrl"><button class="iconbtn">{IC["plus"]}</button>'
    f'<div class="right"><button class="model">Sonnet 4.5 {IC["caret"]}</button>'
    f'<button class="send">{IC["up"]}</button></div></div></div></div>'
    f'<div><div class="vlabel">Size=Single line</div><div class="composer single">'
    f'<button class="iconbtn">{IC["plus"]}</button><span class="in">Ask App</span>'
    f'<button class="send">{IC["up"]}</button></div></div>'
    '</div>')

COMPONENTS = buttons + iconbtns + toggles() + fields + tags + skeleton + appheaders + sidebars + messages + composer

# ================================================================
#  TELAS
# ================================================================
rail = ('<aside class="rail"><div class="items">'
        + "".join(f'<button>{IC[k]}</button>' for k in ("side", "newchat", "chat", "proj", "art", "code"))
        + f'</div><span class="avatar">{IC["avatar"]}</span></aside>')

inline_card = f"""
<div class="screenwrap">
  <div class="cap">Inline card — app dentro da conversa</div>
  <div class="capsub">Sidebar 52px · thread 560px · card do App com skeleton</div>
  <div class="window">
    {rail}
    <div class="wmain">
      <div class="wtop">
        <button class="tchip">Product roadmap {IC["caret"]}</button>
        <button class="share">Share</button>
      </div>
      <div class="wbody">
        <div class="thread">
          <div class="userrow"><div class="bubble">Create a sprint planning page in <b>App</b></div></div>
          <div class="appcontainer" style="width:100%">
            <div class="appheader" style="width:100%">
              <div class="appname"><span class="glyph">A</span><span class="t">App</span></div>
              <button class="iconbtn">{IC["code"]}</button>
            </div>
            <div class="appbody" style="gap:16px;padding:20px">
              <div class="skel inlinecard"><span class="dot"></span><span class="bar"></span><span class="bar"></span><span class="bar"></span></div>
              <div class="skel inlinecard"><span class="dot"></span><span class="bar"></span><span class="bar"></span><span class="bar"></span></div>
              <div class="skel inlinecard"><span class="dot"></span><span class="bar"></span><span class="bar"></span><span class="bar"></span></div>
            </div>
          </div>
          <p class="claudetext">Here’s a sprint planning template with a standard agenda.</p>
          <div class="sparkrow"><span class="spark">{IC["spark"]}</span></div>
        </div>
      </div>
    </div>
  </div>
</div>
"""

CUST = [("MS", "Mercearia São Jorge", "(11) 98812-4477 · São Paulo · SP", "successtone", "Recorrente"),
        ("PE", "Padaria Estrela do Norte", "(11) 97744-1290 · Guarulhos · SP", "successtone", "Recorrente"),
        ("BT", "Bar do Tião", "(11) 96633-8821 · Osasco · SP", "warningtone", "Inativo 60d")]

def custcards(limit=3):
    out = []
    for ini, nome, meta, tone, tag in CUST[:limit]:
        out.append(f'<div class="reccard"><span class="ico">{ini}</span><span class="b">'
                   f'<span class="n">{esc(nome)}</span>'
                   f'<span class="m"><span class="mono">{esc(meta)}</span></span>'
                   f'<span><span class="tag {tone}">{esc(tag)}</span></span></span></div>')
    return "".join(out)

televendas_desktop = f"""
<div class="screenwrap">
  <div class="cap">Televendas — novo pedido (desktop)</div>
  <div class="capsub">Aplicação do sistema: 4 passos, carrinho fixo à direita</div>
  <div class="window">
    {rail}
    <div class="wmain">
      <div class="wtop">
        <div style="display:flex;align-items:baseline;gap:10px">
          <strong style="font-size:16px">Novo pedido</strong>
          <span style="font-family:var(--font-mono);font-size:12px;color:var(--color-text-tertiary)">#PV-24817</span>
        </div>
        <span class="pill"><span class="pip"></span>Em chamada <span style="font-family:var(--font-mono)">02:14</span></span>
      </div>
      <div style="display:flex;flex:1;min-height:0">
        <div style="flex:1;min-width:0;padding:20px;overflow:hidden">
          <div style="display:flex;gap:8px;margin-bottom:20px">
            <span class="chip" aria-pressed="true">1 Cliente</span>
            <span class="chip">2 Produtos</span>
            <span class="chip">3 Entrega</span>
            <span class="chip">4 Pagamento</span>
          </div>
          <div style="font-family:var(--font-display);font-size:20px;font-weight:600;margin-bottom:14px">Cliente</div>
          {custcards()}
        </div>
        <div style="flex:0 0 240px;border-left:var(--border-width-regular) solid var(--color-border-tertiary);
                    background:var(--color-background-primary);display:flex;flex-direction:column;padding:16px">
          <div style="font-weight:600;font-size:14px;margin-bottom:14px">Carrinho</div>
          <div style="flex:1;display:flex;align-items:center;justify-content:center;color:var(--color-text-tertiary);
                      font-size:12px;text-align:center;line-height:1.5">O carrinho está vazio.<br>Adicione produtos no passo 2.</div>
          <div style="border-top:var(--border-width-regular) solid var(--color-border-tertiary);padding-top:12px">
            <div style="display:flex;justify-content:space-between;font-size:13px;color:var(--color-text-secondary);margin-bottom:8px">
              <span>Subtotal</span><span style="font-family:var(--font-mono)">R$ 0,00</span></div>
            <div style="display:flex;justify-content:space-between;align-items:baseline;
                        border-top:var(--border-width-regular) solid var(--color-border-tertiary);padding-top:10px">
              <span style="font-weight:600;font-size:14px">Total</span>
              <span class="money" style="font-size:24px">R$ 0,00</span></div>
            <button class="btn default" style="width:100%;margin-top:12px" disabled>Escolher produtos {IC["arrow"]}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
"""

televendas_mobile = f"""
<div class="screenwrap">
  <div class="cap">Televendas — mobile</div>
  <div class="capsub">Mesmo fluxo, carrinho em bottom sheet</div>
  <div class="phone">
    <div class="pstatus"><span>9:41</span><span style="font-family:var(--font-mono);font-size:11px">▮▮▮</span></div>
    <div class="pnav">
      <button class="pnavbtn">{IC["back"]}</button>
      <div class="pttl"><div class="t">Novo pedido</div><div class="s">#PV-24817</div></div>
      <span class="pill"><span class="pip"></span><span style="font-family:var(--font-mono)">02:14</span></span>
    </div>
    <div class="steps">
      <div class="stp on"><div class="bar"></div><div class="lb">Cliente</div></div>
      <div class="stp"><div class="bar"></div><div class="lb">Produtos</div></div>
      <div class="stp"><div class="bar"></div><div class="lb">Entrega</div></div>
      <div class="stp"><div class="bar"></div><div class="lb">Pagamento</div></div>
    </div>
    <div class="pbody">
      <div style="font-family:var(--font-display);font-size:19px;font-weight:600;margin:4px 0 10px">Cliente</div>
      {custcards()}
    </div>
    <div class="pfoot">
      <div class="pcart"><span class="c">0 itens</span><span class="v">R$ 0,00</span></div>
      <button class="btn default" disabled>Escolher produtos</button>
    </div>
  </div>
</div>
"""

mobile_chat = f"""
<div class="screenwrap">
  <div class="cap">Claude mobile — nova conversa</div>
  <div class="capsub">Tela vazia com o spark e o composer</div>
  <div class="phone">
    <div class="pstatus"><span>9:41</span><span style="font-family:var(--font-mono);font-size:11px">▮▮▮</span></div>
    <div class="pnav">
      <button class="pnavbtn">{IC["side"]}</button>
      <div class="pttl"><div class="t">Opus 4.6</div></div>
      <button class="pnavbtn">{IC["newchat"]}</button>
    </div>
    <div class="pbody" style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px">
      <span class="spark" style="width:34px;height:34px">{IC["spark"]}</span>
      <div style="font-family:var(--font-display);font-size:21px;font-weight:500;text-align:center;line-height:1.3">
        How can I help you<br>this morning?</div>
    </div>
    <div class="pfoot" style="border-radius:0">
      <div class="composer single" style="width:100%;box-shadow:none;border-radius:var(--border-radius-2xl)">
        <button class="iconbtn">{IC["plus"]}</button>
        <span class="in" style="color:var(--color-text-tertiary)">Chat with Claude</span>
        <button class="send">{IC["up"]}</button>
      </div>
    </div>
  </div>
</div>
"""

SCREENS = ('<div class="screengrid">' + inline_card + televendas_desktop + '</div>'
           '<div class="screengrid" style="margin-top:40px">' + televendas_mobile + mobile_chat + '</div>')

FOOT = """
<footer>
  <div class="wrap">
    <p><strong>Como usar.</strong> Todos os tokens são CSS custom properties declaradas em <code>:root</code>
       (modo claro) e <code>[data-theme="dark"]</code> (modo escuro). Trocar o tema é trocar um atributo no
       <code>&lt;body&gt;</code> — nenhum componente precisa saber em que modo está.</p>
    <p><strong>Fontes.</strong> <code>--font-display</code> aponta para Martian Grotesk e <code>--font-ui</code>
       para Google Sans, com fallbacks logo em seguida na mesma declaração. Nenhuma das duas é distribuída
       publicamente: instale-as localmente (ou suba na organização) e elas assumem sozinhas — sem tocar em
       mais nada. Até lá o texto renderiza com o fallback.</p>
    <p><strong>Origem.</strong> Cores, escalas e medidas foram extraídas do arquivo Figma
       “MCP Apps for Claude (Community)”; a tipografia foi substituída conforme pedido.</p>
  </div>
</footer>

<script>
  var b = document.body, t = document.getElementById('themeBtn');
  t.addEventListener('click', function () {
    var dark = b.dataset.theme === 'dark';
    b.dataset.theme = dark ? 'light' : 'dark';
    t.textContent = dark ? 'Tema escuro' : 'Tema claro';
  });
</script>
</body>
</html>
"""

parts.append(section("componentes", "Biblioteca", "Componentes",
    "Cada componente com todas as variantes e estados. Os anéis de foco aparecem tanto por "
    "<kbd>Tab</kbd> quanto na coluna marcada como Focused, para ficarem visíveis na exportação.",
    COMPONENTS))
parts.append(section("telas", "Aplicação", "Telas",
    "As fundações e os componentes montados em telas reais — a prova de que o sistema fecha.",
    SCREENS))
parts.append(FOOT)

OUT.write_text("".join(parts), encoding="utf-8")
print("final:", OUT, OUT.stat().st_size, "bytes")
