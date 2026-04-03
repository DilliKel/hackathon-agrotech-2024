from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class DataBundle:
    df_base: pd.DataFrame
    df_culturas_pragas: pd.DataFrame
    diag_base_col: str
    diag_trat_col: str
    trat1_col: str | None
    trat2_col: str | None
    trat3_col: str | None


def _first_existing_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def load_csv_data(base_csv_path: str | Path, culturas_csv_path: str | Path) -> DataBundle:
    df_base = pd.read_csv(base_csv_path)
    df_culturas_pragas = pd.read_csv(culturas_csv_path)

    diag_base_col = _first_existing_column(
        df_base, ["DIAGNÓSTICO", "DIAGNOSTICO", "Diagnostico", "Diagnóstico"]
    )
    diag_trat_col = _first_existing_column(
        df_culturas_pragas, ["Categoria da Praga", "Diagnostico", "Diagnóstico"]
    )
    trat1_col = _first_existing_column(
        df_culturas_pragas, ["Tratamento Nível 1 (Orgânico)", "Tratamento Nível 1"]
    )
    trat2_col = _first_existing_column(
        df_culturas_pragas, ["Tratamento Nível 2 (Genérico)", "Tratamento Nível 2"]
    )
    trat3_col = _first_existing_column(
        df_culturas_pragas,
        ["Tratamento Nível 3 (Agrotóxico Controlado)", "Tratamento Nível 3"],
    )

    if diag_base_col is None or diag_trat_col is None:
        raise ValueError("Colunas de diagnóstico não encontradas nas planilhas.")

    return DataBundle(
        df_base=df_base,
        df_culturas_pragas=df_culturas_pragas,
        diag_base_col=diag_base_col,
        diag_trat_col=diag_trat_col,
        trat1_col=trat1_col,
        trat2_col=trat2_col,
        trat3_col=trat3_col,
    )
