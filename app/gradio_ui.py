from __future__ import annotations

import re
from pathlib import Path

import gradio as gr
import spaces

from src.agroscan.classifier import AgroScanClassifier

_ROOT = Path(__file__).resolve().parent.parent
_PARENTESES_FINAL = re.compile(r"\s*\([^)]*\)\s*$")


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


def build_interface(classifier: AgroScanClassifier) -> gr.Interface:
    perguntas = [c for c in classifier.data.df_base.columns if c != classifier.data.diag_base_col]

    @spaces.GPU
    def interface_gradio(*respostas_usuario):
        respostas = list(respostas_usuario)
        resultado = classifier.diagnostico_e_tratamento(respostas)
        if "error" in resultado:
            return [resultado["error"], "-", "-", "-"]
        return [
            resultado.get("diagnostico", "-"),
            resultado.get("tratamento_nivel_1", "-"),
            resultado.get("tratamento_nivel_2", "-"),
            resultado.get("tratamento_nivel_3", "-"),
        ]

    inputs = [
        gr.Dropdown(
            label=_PARENTESES_FINAL.sub("", pergunta).strip(),
            choices=_valores_canonicos(classifier.data.df_base[pergunta]),
        )
        for pergunta in perguntas
    ]
    outputs = [
        gr.Textbox(label="Diagnóstico"),
        gr.Textbox(label="Tratamento Nível 1 (Orgânico)"),
        gr.Textbox(label="Tratamento Nível 2 (Genérico)"),
        gr.Textbox(label="Tratamento Nível 3 (Agrotóxico Controlado)"),
    ]

    return gr.Interface(
        fn=interface_gradio,
        inputs=inputs,
        outputs=outputs,
        title="AgroScan",
        description="Responda às perguntas para obter diagnóstico e recomendações de tratamento.",
    )


if __name__ == "__main__":
    classifier = AgroScanClassifier.from_csv(
        _ROOT / "data" / "Base.csv",
        _ROOT / "data" / "Culturas_e_pragas.csv",
    )
    build_interface(classifier).launch()
