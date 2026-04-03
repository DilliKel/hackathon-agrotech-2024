from __future__ import annotations

from pathlib import Path
import unicodedata
from collections import Counter

from sentence_transformers import SentenceTransformer, util

from .data_loader import DataBundle, load_csv_data

DEFAULT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class AgroScanClassifier:
    def __init__(
        self,
        data: DataBundle,
        model_name: str = DEFAULT_MODEL_NAME,
        model: SentenceTransformer | None = None,
    ) -> None:
        self.data = data
        self.model = model or SentenceTransformer(model_name)

        self.diagnosticos_base = (
            self.data.df_base[self.data.diag_base_col].astype(str).tolist()
        )
        self.embeddings_diagnosticos = self.model.encode(
            self.diagnosticos_base,
            convert_to_tensor=True,
            normalize_embeddings=True,
        )
        self.categorias_tratamento = (
            self.data.df_culturas_pragas[self.data.diag_trat_col].astype(str).tolist()
        )
        self.embeddings_categorias = self.model.encode(
            self.categorias_tratamento,
            convert_to_tensor=True,
            normalize_embeddings=True,
        )

    @classmethod
    def from_csv(
        cls,
        base_csv_path: str | Path,
        culturas_csv_path: str | Path,
        model_name: str = DEFAULT_MODEL_NAME,
        model: SentenceTransformer | None = None,
    ) -> "AgroScanClassifier":
        data = load_csv_data(base_csv_path, culturas_csv_path)
        return cls(data=data, model_name=model_name, model=model)

    def diagnostico_e_tratamento(self, respostas: list[str]) -> dict[str, str]:
        texto = " ".join([str(r).strip() for r in respostas if str(r).strip()])
        if not texto:
            return {"error": "Respostas vazias ou inválidas"}

        # Prioriza match estruturado (linha da planilha) quando as respostas
        # batem exatamente com os campos da base.
        diagnostico = self._diagnostico_por_match_estruturado(respostas)
        if diagnostico is None:
            embedding_respostas = self.model.encode(
                texto, convert_to_tensor=True, normalize_embeddings=True
            )
            similaridades = util.cos_sim(embedding_respostas, self.embeddings_diagnosticos)[0]
            indice = int(similaridades.argmax().item())
            diagnostico = self.diagnosticos_base[indice]

        tratamento_df = self._buscar_tratamento(diagnostico)

        if tratamento_df.empty:
            return {
                "diagnostico": diagnostico,
                "tratamento_nivel_1": "Tratamento não encontrado",
                "tratamento_nivel_2": "Tratamento não encontrado",
                "tratamento_nivel_3": "Tratamento não encontrado",
            }

        tratamento = tratamento_df.iloc[0]
        return {
            "diagnostico": diagnostico,
            "tratamento_nivel_1": str(tratamento[self.data.trat1_col]) if self.data.trat1_col else "Tratamento não encontrado",
            "tratamento_nivel_2": str(tratamento[self.data.trat2_col]) if self.data.trat2_col else "Tratamento não encontrado",
            "tratamento_nivel_3": str(tratamento[self.data.trat3_col]) if self.data.trat3_col else "Tratamento não encontrado",
        }

    def _diagnostico_por_match_estruturado(self, respostas: list[str]) -> str | None:
        colunas_perguntas = [
            col for col in self.data.df_base.columns if col != self.data.diag_base_col
        ]

        # So aplica match estruturado quando ha respostas para todas as perguntas.
        if len(respostas) < len(colunas_perguntas):
            return None

        respostas_norm = [self._normalizar_texto(r) for r in respostas[: len(colunas_perguntas)]]
        if any(not r for r in respostas_norm):
            return None

        matches: list[str] = []
        for _, row in self.data.df_base.iterrows():
            valores_row = [self._normalizar_texto(row[col]) for col in colunas_perguntas]
            if valores_row == respostas_norm:
                matches.append(str(row[self.data.diag_base_col]))

        if not matches:
            return None

        # Se houver duplicatas conflitantes, usa maioria e mantem comportamento deterministico.
        return Counter(matches).most_common(1)[0][0]

    def _buscar_tratamento(self, diagnostico: str):
        # 1) Tenta match textual exato.
        tratamento_df = self.data.df_culturas_pragas[
            self.data.df_culturas_pragas[self.data.diag_trat_col].astype(str) == diagnostico
        ]
        if not tratamento_df.empty:
            return tratamento_df

        # 2) Tenta match textual normalizado (acento, caixa e pontuação simples).
        diagnostico_norm = self._normalizar_texto(diagnostico)
        categoria_norm = self.data.df_culturas_pragas[self.data.diag_trat_col].astype(str).map(self._normalizar_texto)
        tratamento_df = self.data.df_culturas_pragas[categoria_norm == diagnostico_norm]
        if not tratamento_df.empty:
            return tratamento_df

        # 3) Fallback semântico para cobrir variações como "de" vs "do".
        embedding_diag = self.model.encode(
            diagnostico,
            convert_to_tensor=True,
            normalize_embeddings=True,
        )
        similaridades = util.cos_sim(embedding_diag, self.embeddings_categorias)[0]
        indice = int(similaridades.argmax().item())
        categoria_mais_proxima = self.categorias_tratamento[indice]
        return self.data.df_culturas_pragas[
            self.data.df_culturas_pragas[self.data.diag_trat_col].astype(str)
            == categoria_mais_proxima
        ]

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        texto = unicodedata.normalize("NFD", str(texto))
        texto = "".join(ch for ch in texto if unicodedata.category(ch) != "Mn")
        return " ".join(texto.lower().strip().split())
