from __future__ import annotations

import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MAINTENANCE_PATH = REPOSITORY_ROOT / "docs" / "maintenance.md"
README_PATH = REPOSITORY_ROOT / "README.md"
EXPECTED_DOCUMENTS = {
    "data-guide.md",
    "evolution-history.md",
    "evolution-results.md",
    "evolution-scope.md",
    "final-validation.md",
    "maintenance.md",
    "reconstruction-analysis.md",
    "reconstruction-history.md",
    "result-comparison.md",
}


class MaintenanceDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.maintenance = MAINTENANCE_PATH.read_text(encoding="utf-8")
        cls.readme = README_PATH.read_text(encoding="utf-8")

    def test_all_reconstruction_modules_are_documented(self) -> None:
        modules = (
            "__init__.py",
            "data.py",
            "eda.py",
            "poc1.py",
            "poc2.py",
            "score.py",
            "schema.py",
        )
        for module in modules:
            with self.subTest(module=module):
                self.assertIn(f"src/tcc_reconstruction/{module}", self.maintenance)

    def test_validation_sequence_and_dataset_boundary_are_explicit(self) -> None:
        required_fragments = (
            "## Sequência recomendada",
            "## Verificações sem dataset",
            "## Operações que exigem o dataset",
            "make test",
            "make validate",
            "make notebook",
            "LENDING_CLUB_DATA_PATH",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.maintenance)

    def test_local_colab_and_troubleshooting_are_covered(self) -> None:
        required_headings = (
            "## Execução no Google Colab",
            "### Memória insuficiente",
            "### Caminho do dataset",
            "### Kernel Jupyter",
        )
        for heading in required_headings:
            with self.subTest(heading=heading):
                self.assertIn(heading, self.maintenance)

    def test_limitations_and_authoritative_links_remain_visible(self) -> None:
        self.assertIn("## Limitações e resultados irreproduzíveis", self.maintenance)
        self.assertIn("docs/final-validation.md", self.maintenance)
        self.assertIn("docs/result-comparison.md", self.maintenance)

    def test_readme_links_maintenance_guide(self) -> None:
        self.assertIn("docs/maintenance.md", self.readme)
        self.assertIn("docs/evolution-history.md", self.readme)

    def test_maintenance_preserves_current_evolution_rules(self) -> None:
        for fragment in (
            "notebooks/tcc-evolved.ipynb",
            "único ponto de entrada",
            "make reproduce-reconstructed",
            "cópia temporária",
            "não escolha modelo, corte ou limiar pelo teste",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.maintenance)

    def test_documentation_has_the_consolidated_structure(self) -> None:
        documents = {path.name for path in (REPOSITORY_ROOT / "docs").glob("*.md")}
        self.assertEqual(documents, EXPECTED_DOCUMENTS)
        for document in EXPECTED_DOCUMENTS:
            with self.subTest(document=document):
                self.assertIn(f"docs/{document}", self.readme)


if __name__ == "__main__":
    unittest.main()
