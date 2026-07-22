from pathlib import Path
from src.agroscan.classifier import AgroScanClassifier
from app.gradio_ui import build_interface

ROOT = Path(__file__).resolve().parent

classifier = AgroScanClassifier.from_csv(
    ROOT / "data" / "Base.csv",
    ROOT / "data" / "Culturas_e_pragas.csv",
)

demo = build_interface(classifier)
demo.launch()
