# AgroScan

O AgroScan utiliza **embeddings multilíngues** para diagnosticar pragas agrícolas com base nas respostas dos usuários sobre sintomas e condições de plantio. O backend é implementado em **Python** com **Flask**, e a API pode ser exposta no **Google Colab** usando túnel HTTPS para acesso externo.

---
## Protótipo do Aplicativo

<div align="center">
  <strong>Acesse o protótipo do aplicativo no Figma:</strong><br>
  <a href="https://www.figma.com/proto/5MJSndRcf5vzjuyOpr34bC/Mobile-Dashboard-UI-(Community)?node-id=0-1&t=Kyf1DkGB5MBF07TB-1">
    Link para o Figma
  </a>
</div>

---
## Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação](#instalação)
- [Configuração](#configuração)
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
- **pyngrok/ngrok**: Exposição opcional da API Flask para acesso externo.
- **pytest**: Testes automatizados básicos da API e do classificador.
- **Google Colab**: Ambiente de execução para os notebooks e a API.

---

## Instalação

### 1. Clonar o Repositório
```bash
git clone https://github.com/DilliKel/hackathon-agrotech-2024.git
cd hackathon-agrotech-2024
```

### 2. Instalar Dependências
As dependências podem ser instaladas no Google Colab ou em um ambiente local.

Para instalação local, use:
```bash
pip install -r requirements.txt
```

Para instalação no Google Colab, rode:
```python
!pip install -r requirements.txt
```

---

## Configuração

1. **Upload das Planilhas**: Carregue `Base.csv` e `Culturas_e_pragas.csv` diretamente no Google Colab usando o seguinte código:

   ```python
   from google.colab import files
   uploaded = files.upload()  # Faça o upload das planilhas
   ```

2. **Exposição da API (opcional)**: Para teste externo no Colab, utilize ngrok/pyngrok para publicar uma URL HTTPS temporária.

---

## Uso

### Executar o Projeto no Google Colab

1. **Carregar as Planilhas**:
   - Use o `files.upload()` para fazer o upload das planilhas `Base.csv` e `Culturas_e_pragas.csv`.
   
2. **Rodar o Código da API**:
   - Inicie o Flask no Colab com o comando `app.run()`.

3. **Obter o Link do ngrok**:
   - Copie o link gerado pelo ngrok para acessar a API de qualquer lugar.

4. **Endpoint principal da AgroScan API**:

   - **`/diagnostico`** (POST): Recebe as respostas do usuário e retorna um diagnóstico e recomendações de tratamento.
     - Exemplo de requisição:
       ```bash
       curl -X POST https://<ngrok-link>.ngrok.io/diagnostico \
       -H "Content-Type: application/json" \
       -d '{"respostas": ["Milho", "Folhas amareladas", "Seca prolongada"]}'
       ```

### Executar localmente (estrutura modular)

1. **Rodar a API local**:
   ```bash
   .\\.venv\\Scripts\\Activate.ps1
   python -m src.agroscan.api
   ```
   Acesse no navegador: `http://127.0.0.1:5000`

2. **Fluxo visual (MVP Web)**:
   - Preencha os campos do formulario na tela.
   - Clique em **Gerar diagnostico**.
   - Veja o retorno em tela com: diagnostico, tratamento nivel 1, 2 e 3.

3. **Rodar a interface Gradio local**:
   ```bash
   python app/gradio_ui.py
   ```

4. **Executar testes**:
   ```bash
   pytest -q
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

## Plano de Melhorias para Amanhã

1. Implementar endpoint com metadados de decisão (`tipo_match`, `score`, `top_k`).
2. Criar script de auditoria das planilhas com relatório de inconsistências.
3. Padronizar os CSVs (capitalização, acentuação e valores booleanos/categóricos).
4. Adicionar testes cobrindo os novos metadados e casos reais de regressão.
5. Ajustar UI para exibir confiança e a origem do diagnóstico.

---

## Estrutura do Projeto

```
hackathon-agrotech-2024/
│
├── AgroScan_API/
│   ├── AgroScan_API.ipynb
│   ├── Base.csv
│   └── Culturas_e_pragas.csv
├── src/
│   ├── __init__.py
│   └── agroscan/
│       ├── __init__.py
│       ├── data_loader.py
│       ├── classifier.py
│       └── api.py
├── app/
│   └── gradio_ui.py
├── tests/
│   ├── conftest.py
│   ├── test_classifier.py
│   └── test_api.py
├── requirements.txt
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
