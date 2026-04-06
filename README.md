# AgroScan

Diagnosticador de pragas agrícolas com **embeddings semânticos multilíngues**. O usuário responde perguntas sobre sintomas e condições da cultura; o sistema encontra o diagnóstico mais próximo por similaridade de cosseno e retorna recomendações de tratamento em três níveis.

---

## Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação](#instalação)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## Sobre o Projeto

O AgroScan visa fornecer uma ferramenta de diagnóstico para pragas agrícolas, ajudando produtores a identificar e tratar pragas com base nas culturas cultivadas, condições climáticas e sintomas observados. A recomendação usa similaridade semântica com o modelo `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, com dados extraídos de planilhas CSV (`Base.csv` e `Culturas_e_pragas.csv`).

---

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **Flask**: Framework para criar a API.
- **Sentence-Transformers**: Para embeddings semânticos multilíngues.
- **pandas**: Manipulação e leitura de dados das planilhas.
- **pytest**: Testes automatizados da API e do classificador.

---

## Instalação

### 1. Clonar o Repositório
```bash
git clone https://github.com/DilliKel/hackathon-agrotech-2024.git
cd hackathon-agrotech-2024
```

### 2. Criar e Ativar Ambiente Virtual
```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

---

## Uso

### Rodar a API local

```bash
python -m src.agroscan.api
```

Acesse em `http://127.0.0.1:5000`.

**Fluxo:**
1. Preencha os campos do formulário na tela inicial.
2. Clique em **Gerar diagnóstico**.
3. Veja o retorno com: diagnóstico, tratamento nível 1, 2 e 3.

**Endpoint direto (POST)**:
```bash
curl -X POST http://127.0.0.1:5000/diagnostico \
  -H "Content-Type: application/json" \
  -d '{"respostas": ["Milho", "Folhas amareladas", "Seca prolongada"]}'
```

### Rodar a interface Gradio (alternativa)

```bash
python app/gradio_ui.py
```

### Executar testes

```bash
python -m pytest -q
```

---

## Status Atual (Abr/2026)

- API web local funcionando em `/`, `/health` e `/diagnostico`.
- Classificador com embeddings multilíngues e fallback robusto para tratamento.
- Regra de prioridade para **match estruturado exato** da linha da base antes do fallback semântico.
- Testes automatizados passando.

---

## Melhorias Recomendadas

1. **Qualidade de dados**
   - Padronizar valores categóricos (`Sim/sim`, nomes de meses e culturas).
   - Remover duplicatas e criar validação automática de consistência dos CSVs.
2. **Explicabilidade do diagnóstico**
   - Retornar no payload se o resultado veio de `match_exato` ou `fallback_semantico`.
   - Expor score de confiança e top-3 hipóteses para debug.
3. **Cobertura de testes**
   - Adicionar testes com dados reais das planilhas.
   - Incluir testes de regressão para casos de borda (variações de acento, caixa e sinônimos).
4. **UX do MVP**
   - Melhorar feedback visual de carregamento e mensagens de erro por campo.
   - Mostrar histórico das últimas consultas na interface.
5. **Operação e entrega**
   - Criar script de auditoria de dados para rodar antes de cada demo.
   - Adicionar pipeline CI simples para rodar `pytest` em push/PR.

---

## Estrutura do Projeto

```
hackathon-agrotech-2024/
│
├── data/
│   ├── Base.csv
│   └── Culturas_e_pragas.csv
├── src/
│   ├── __init__.py
│   └── agroscan/
│       ├── __init__.py
│       ├── data_loader.py
│       ├── classifier.py
│       ├── api.py
│       ├── templates/
│       └── static/
├── app/
│   └── gradio_ui.py
├── tests/
│   ├── conftest.py
│   ├── test_classifier.py
│   └── test_api.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

---

## Contribuição

Contribuições são bem-vindas! Siga os passos abaixo para contribuir:

1. Faça um fork do projeto.
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`).
3. Faça commit de suas alterações (`git commit -m 'Adiciona NovaFeature'`).
4. Envie para a branch principal (`git push origin feature/NovaFeature`).
5. Abra um Pull Request.

---

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
