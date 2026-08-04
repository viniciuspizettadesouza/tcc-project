# Revisão da Fase 1 — fundação reprodutível

Data da validação: 4 de agosto de 2026.

## Resultado

A fundação foi preparada sem criar o notebook reconstruído, carregar o dataset ou executar qualquer modelo. O commit permanece pendente de revisão e aprovação.

## Entregas

- artefato recuperado do TCC preservado em `notebooks/tcc-recovered-from-colab.ipynb`, recebido originalmente como `Copy of Trabalho Data Mining.ipynb` após a perda do notebook original no Google Colab;
- uma cópia técnica foi criada originalmente na Fase 1, mas removida do estado final após a confirmação de que não era fonte independente; sua existência histórica permanece auditável no Git;
- manifesto de fontes em `provenance/source-manifest.json`;
- verificador independente em `scripts/verify_source_integrity.py`;
- dependências diretas fixadas em `requirements.txt` para Python 3.12;
- instruções local e Colab no README;
- instruções e análise atualizadas para distinguir notebook original perdido, artefato recuperado e notebook reconstruído.

## Evidência de integridade

| Fonte | Tamanho | SHA-256 | Resultado |
|---|---:|---|---|
| `TCC_Vinicius_P_Souza.pdf` | 1.854.902 bytes | `abfed8559ee14018fb9204dd061aa6003d6ceb65e6cb63a9722d02e8e3182bdf` | íntegra |
| artefato recuperado do TCC | 139.488 bytes | `7c58b4b0d0a9cae0accd49f77cd46fd8fd02316961ec588394463b5e9456f330` | íntegro |

O teste negativo truncou somente uma cópia temporária fora do repositório. O verificador detectou tamanho, hash e equivalência incorretos e terminou com código diferente de zero.

## Ambiente validado

- Python 3.12.3;
- instalação nova em ambiente temporário;
- dependências diretas nas versões fixadas em `requirements.txt`;
- JupyterLab 4.6.2;
- `pip check`: nenhuma dependência quebrada;
- importação conjunta da pilha científica e dos estimadores principais: aprovada;
- JupyterLab CLI: versão respondida corretamente.

O pacote Kaggle foi instalado e teve a versão confirmada. Autenticação e download não foram testados, pois dependem de credenciais do usuário e pertencem à Fase 2.

## Comandos de validação

```bash
python scripts/verify_source_integrity.py
python -m py_compile scripts/verify_source_integrity.py
python -m json.tool provenance/source-manifest.json
python -m pip install -r requirements.txt
python -m pip check
python -m jupyterlab --version
git diff --check
```

Também foram validados os padrões do `.gitignore` para `data/`, `.env`, `kaggle.json`, `models/`, `outputs/` e `.venv/`.

## Limites desta validação

- O fluxo do README para Google Colab não foi executado remotamente.
- Somente Python 3.12 foi declarado e validado.
- Dependências diretas estão fixadas; dependências transitivas continuam sendo resolvidas pelo `pip` conforme plataforma.
- Nenhuma credencial, dataset ou saída de modelo foi criada no repositório.

## Checklist de encerramento

- [x] escopo limitado à Fase 1;
- [x] fonte recebida inalterada;
- [x] artefato recuperado validado por tamanho e SHA-256;
- [x] instalação limpa e smoke test executados;
- [x] documentação atualizada;
- [x] `git diff --check` sem erros;
- [ ] diff aprovado pelo responsável;
- [ ] commit da Fase 1 criado após aprovação.
