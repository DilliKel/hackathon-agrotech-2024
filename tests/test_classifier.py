import torch

from agroscan.classifier import AgroScanClassifier
from agroscan.data_loader import DataBundle


class FakeModel:
    def encode(self, texts, convert_to_tensor=True, normalize_embeddings=True):
        if isinstance(texts, list):
            vectors = [self._to_vec(t) for t in texts]
            return torch.stack(vectors)
        return self._to_vec(texts)

    def _to_vec(self, text):
        t = str(text).lower()
        if "solo" in t:
            return torch.tensor([1.0, 0.0])
        if "lagarta" in t:
            return torch.tensor([0.0, 1.0])
        return torch.tensor([0.7, 0.7])


def test_diagnostico_e_tratamento_retorna_campos_esperados():
    import pandas as pd

    df_base = pd.DataFrame({"DIAGNÓSTICO": ["Pragas do Solo", "Lagartas"]})
    df_trat = pd.DataFrame(
        {
            "Categoria da Praga": ["Pragas do Solo", "Lagartas"],
            "Tratamento Nível 1 (Orgânico)": ["Org Solo", "Org Lag"],
            "Tratamento Nível 2 (Genérico)": ["Gen Solo", "Gen Lag"],
            "Tratamento Nível 3 (Agrotóxico Controlado)": ["Agr Solo", "Agr Lag"],
        }
    )

    bundle = DataBundle(
        df_base=df_base,
        df_culturas_pragas=df_trat,
        diag_base_col="DIAGNÓSTICO",
        diag_trat_col="Categoria da Praga",
        trat1_col="Tratamento Nível 1 (Orgânico)",
        trat2_col="Tratamento Nível 2 (Genérico)",
        trat3_col="Tratamento Nível 3 (Agrotóxico Controlado)",
    )

    clf = AgroScanClassifier(data=bundle, model=FakeModel())
    out = clf.diagnostico_e_tratamento(["solo seco", "raiz roida"])

    assert out["diagnostico"] == "Pragas do Solo"
    assert out["tratamento_nivel_1"] == "Org Solo"
    assert out["tratamento_nivel_2"] == "Gen Solo"
    assert out["tratamento_nivel_3"] == "Agr Solo"


def test_diagnostico_e_tratamento_faz_fallback_semantico_categoria():
    import pandas as pd

    # "Pragas de Solo" nao existe igual no tratamento, mas e semanticamente proxima.
    df_base = pd.DataFrame({"DIAGNÓSTICO": ["Pragas de Solo", "Lagartas"]})
    df_trat = pd.DataFrame(
        {
            "Categoria da Praga": ["Pragas do Solo", "Lagartas"],
            "Tratamento Nível 1 (Orgânico)": ["Org Solo", "Org Lag"],
            "Tratamento Nível 2 (Genérico)": ["Gen Solo", "Gen Lag"],
            "Tratamento Nível 3 (Agrotóxico Controlado)": ["Agr Solo", "Agr Lag"],
        }
    )

    bundle = DataBundle(
        df_base=df_base,
        df_culturas_pragas=df_trat,
        diag_base_col="DIAGNÓSTICO",
        diag_trat_col="Categoria da Praga",
        trat1_col="Tratamento Nível 1 (Orgânico)",
        trat2_col="Tratamento Nível 2 (Genérico)",
        trat3_col="Tratamento Nível 3 (Agrotóxico Controlado)",
    )

    clf = AgroScanClassifier(data=bundle, model=FakeModel())
    out = clf.diagnostico_e_tratamento(["solo seco", "raiz roida"])

    assert out["diagnostico"] == "Pragas de Solo"
    assert out["tratamento_nivel_1"] == "Org Solo"
    assert out["tratamento_nivel_2"] == "Gen Solo"
    assert out["tratamento_nivel_3"] == "Agr Solo"


def test_match_estruturado_prioriza_linha_exata_da_base():
    import pandas as pd

    df_base = pd.DataFrame(
        {
            "Municipio": ["Boa Vista", "Alto Alegre"],
            "Porte": ["Pequeno", "Medio"],
            "Cultura": ["Mandioca", "Milho"],
            "Sintoma": ["Folhas amareladas e murcha inicial", "Folhas amareladas e com buracos"],
            "DIAGNÓSTICO": ["Percevejo", "Lagarta-do-cartucho"],
        }
    )
    df_trat = pd.DataFrame(
        {
            "Categoria da Praga": ["Percevejo", "Lagarta-do-cartucho"],
            "Tratamento Nível 1 (Orgânico)": ["Org Per", "Org Lag"],
            "Tratamento Nível 2 (Genérico)": ["Gen Per", "Gen Lag"],
            "Tratamento Nível 3 (Agrotóxico Controlado)": ["Agr Per", "Agr Lag"],
        }
    )

    bundle = DataBundle(
        df_base=df_base,
        df_culturas_pragas=df_trat,
        diag_base_col="DIAGNÓSTICO",
        diag_trat_col="Categoria da Praga",
        trat1_col="Tratamento Nível 1 (Orgânico)",
        trat2_col="Tratamento Nível 2 (Genérico)",
        trat3_col="Tratamento Nível 3 (Agrotóxico Controlado)",
    )

    clf = AgroScanClassifier(data=bundle, model=FakeModel())
    out = clf.diagnostico_e_tratamento(
        ["Boa Vista", "Pequeno", "Mandioca", "Folhas amareladas e murcha inicial"]
    )

    assert out["diagnostico"] == "Percevejo"
    assert out["tratamento_nivel_1"] == "Org Per"
