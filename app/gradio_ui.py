from __future__ import annotations

import re
from pathlib import Path

import gradio as gr
import spaces

from src.agroscan.classifier import AgroScanClassifier

_ROOT = Path(__file__).resolve().parent.parent
_PARENTESES_FINAL = re.compile(r"\s*\([^)]*\)\s*$")

# Imagens representativas por diagnóstico (valores da coluna DIAGNÓSTICO em Base.csv),
# obtidas via API pública do Wikimedia Commons. Categorias genéricas demais para
# corresponder a uma espécie específica ficam com None — a UI esconde a imagem nesse caso.
PRAGA_IMAGENS: dict[str, str | None] = {
    "Broca-do-fruto": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Euaresta_aequalis.jpg",
    "Brocas e Insetos de Colmo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Eucomatocera_vittata-Kadavoor-2017-05-23-001.jpg/330px-Eucomatocera_vittata-Kadavoor-2017-05-23-001.jpg",
    "Brocas e Pragas do Tronco": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Wood-boring_beetle_%28Buprestidae_sp.%29%2C_Hogsback_Mountain%2C_Marquette%2C_Michigan.jpg/330px-Wood-boring_beetle_%28Buprestidae_sp.%29%2C_Hogsback_Mountain%2C_Marquette%2C_Michigan.jpg",
    "Brocas e Pragas dos Frutos": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Euaresta_aequalis.jpg/330px-Euaresta_aequalis.jpg",
    "Cochonilha": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Wax_Scale.jpg/330px-Wax_Scale.jpg",
    "Lagarta-do-cartucho": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Spodoptera_frugiperda.jpg/330px-Spodoptera_frugiperda.jpg",
    "Lagartas": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Chenille_de_Grand_porte_queue_%28macaon%29.jpg/330px-Chenille_de_Grand_porte_queue_%28macaon%29.jpg",
    "Larva-de-arame ou Corós": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Denticollis.linearis.3.jpg/330px-Denticollis.linearis.3.jpg",
    "Percevejo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Nezara_viridula2.jpg/330px-Nezara_viridula2.jpg",
    "Percevejo-da-soja": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Nezara_viridula2.jpg/330px-Nezara_viridula2.jpg",
    "Pragas Foliares e do Grão": None,
    "Pragas de Folha e Fruto": None,
    "Pragas de Folhas e Frutos": None,
    "Pragas de Raiz e Solo": None,
    "Pragas de Solo": None,
    "Pragas de Solo e Colmo": None,
    "Pragas do Solo": None,
}


def _valores_canonicos(valores) -> list[str]:
    """Deduplica valores que só diferem em acento/caixa, preferindo a grafia capitalizada."""
    agrupados: dict[str, str] = {}
    for valor in valores:
        valor = str(valor).strip()
        if not valor:
            continue
        chave = AgroScanClassifier._normalizar_texto(valor)
        atual = agrupados.get(chave)
        if atual is None or (valor[:1].isupper() and not atual[:1].isupper()):
            agrupados[chave] = valor
    return sorted(agrupados.values())


def build_interface(classifier: AgroScanClassifier) -> gr.Blocks:
    perguntas = [c for c in classifier.data.df_base.columns if c != classifier.data.diag_base_col]

    @spaces.GPU
    def executar_diagnostico(*respostas_usuario):
        resultado = classifier.diagnostico_e_tratamento(list(respostas_usuario))

        if "error" in resultado:
            return (
                gr.update(visible=True),
                f"## ⚠️ {resultado['error']}",
                gr.update(value=None, visible=False),
                "",
                "",
                "",
            )

        diagnostico = resultado.get("diagnostico", "-")
        url_imagem = PRAGA_IMAGENS.get(diagnostico)

        return (
            gr.update(visible=True),
            f"## 🐛 {diagnostico}",
            gr.update(value=url_imagem, visible=url_imagem is not None),
            f"### 🌿 Nível 1 — Orgânico\n\n{resultado.get('tratamento_nivel_1', '-')}",
            f"### 💊 Nível 2 — Genérico\n\n{resultado.get('tratamento_nivel_2', '-')}",
            f"### ⚠️ Nível 3 — Agrotóxico Controlado\n\n{resultado.get('tratamento_nivel_3', '-')}",
        )

    with gr.Blocks(theme=gr.themes.Soft(), title="AgroScan") as demo:
        gr.Markdown("# 🌾 AgroScan — Diagnóstico de Pragas Agrícolas")
        gr.Markdown(
            "Sistema que usa **embeddings semânticos multilíngues** para identificar pragas "
            "com base nos sintomas informados e retornar recomendações de tratamento em três níveis."
        )

        entradas = [
            gr.Dropdown(
                label=_PARENTESES_FINAL.sub("", pergunta).strip(),
                choices=_valores_canonicos(classifier.data.df_base[pergunta]),
            )
            for pergunta in perguntas
        ]

        with gr.Row():
            botao_diagnosticar = gr.Button("Gerar Diagnóstico", variant="primary", size="lg")

        with gr.Column(visible=False) as coluna_resultado:
            gr.Markdown("---")
            with gr.Row():
                with gr.Column(scale=2):
                    diagnostico_md = gr.Markdown()
                with gr.Column(scale=1):
                    imagem_praga = gr.Image(show_label=False, visible=False, height=220)
            with gr.Row():
                tratamento1_md = gr.Markdown()
                tratamento2_md = gr.Markdown()
                tratamento3_md = gr.Markdown()

        botao_diagnosticar.click(
            fn=executar_diagnostico,
            inputs=entradas,
            outputs=[
                coluna_resultado,
                diagnostico_md,
                imagem_praga,
                tratamento1_md,
                tratamento2_md,
                tratamento3_md,
            ],
        )

    return demo


if __name__ == "__main__":
    classifier = AgroScanClassifier.from_csv(
        _ROOT / "data" / "Base.csv",
        _ROOT / "data" / "Culturas_e_pragas.csv",
    )
    build_interface(classifier).launch()
