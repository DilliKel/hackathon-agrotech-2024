const FALLBACK_QUESTIONS = [
  "Qual cultura esta sendo atacada?",
  "Quais sintomas voce esta observando?",
  "Houve mudancas recentes no solo ou clima?",
];

function resolveApiBase() {
  if (window.AGROSCAN_API_BASE) {
    return window.AGROSCAN_API_BASE.replace(/\/$/, "");
  }

  if (window.location.hostname.endsWith("github.io")) {
    return "";
  }

  return "";
}

function renderQuestions(container, questions) {
  container.innerHTML = "";

  questions.forEach((pergunta, idx) => {
    const label = document.createElement("label");
    label.className = "question";

    const span = document.createElement("span");
    span.textContent = `${idx + 1}. ${pergunta}`;

    const input = document.createElement("input");
    input.type = "text";
    input.name = `resposta-${idx}`;
    input.required = true;

    label.appendChild(span);
    label.appendChild(input);
    container.appendChild(label);
  });
}

async function loadQuestions() {
  const apiBase = resolveApiBase();

  try {
    const resp = await fetch(`${apiBase}/perguntas`);
    if (!resp.ok) {
      throw new Error("Falha ao carregar perguntas.");
    }

    const data = await resp.json();
    if (Array.isArray(data.perguntas) && data.perguntas.length > 0) {
      return data.perguntas;
    }

    return FALLBACK_QUESTIONS;
  } catch (_) {
    return FALLBACK_QUESTIONS;
  }
}

const form = document.getElementById("diagnostico-form");
const submitBtn = document.getElementById("submit-btn");
const statusEl = document.getElementById("status");
const resultPanel = document.getElementById("result-panel");
const questionsContainer = document.getElementById("questions-container");

const out = {
  diagnostico: document.getElementById("r-diagnostico"),
  t1: document.getElementById("r-t1"),
  t2: document.getElementById("r-t2"),
  t3: document.getElementById("r-t3"),
};

loadQuestions().then((questions) => {
  renderQuestions(questionsContainer, questions);
});

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
    const apiBase = resolveApiBase();
    const resp = await fetch(`${apiBase}/diagnostico`, {
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
