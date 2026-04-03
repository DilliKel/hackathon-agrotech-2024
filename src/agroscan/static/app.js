const form = document.getElementById("diagnostico-form");
const submitBtn = document.getElementById("submit-btn");
const statusEl = document.getElementById("status");
const resultPanel = document.getElementById("result-panel");

const out = {
  diagnostico: document.getElementById("r-diagnostico"),
  t1: document.getElementById("r-t1"),
  t2: document.getElementById("r-t2"),
  t3: document.getElementById("r-t3"),
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const respostas = Array.from(form.querySelectorAll("input"))
    .map((i) => i.value.trim())
    .filter(Boolean);

  if (!respostas.length) {
    statusEl.textContent = "Preencha pelo menos uma resposta.";
    return;
  }

  submitBtn.disabled = true;
  statusEl.textContent = "Processando embeddings e inferencia...";

  try {
    const resp = await fetch("/diagnostico", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ respostas }),
    });

    const data = await resp.json();
    if (!resp.ok || data.error) {
      throw new Error(data.error || "Erro ao gerar diagnostico.");
    }

    out.diagnostico.textContent = data.diagnostico || "-";
    out.t1.textContent = data.tratamento_nivel_1 || "-";
    out.t2.textContent = data.tratamento_nivel_2 || "-";
    out.t3.textContent = data.tratamento_nivel_3 || "-";

    resultPanel.hidden = false;
    statusEl.textContent = "Diagnostico gerado com sucesso.";
  } catch (err) {
    statusEl.textContent = err.message;
  } finally {
    submitBtn.disabled = false;
  }
});
