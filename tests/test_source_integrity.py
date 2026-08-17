from __future__ import annotations

import unittest

from scripts.verify_source_integrity import REPOSITORY_ROOT, load_manifest, verify


class ProtectedSourceIntegrityTests(unittest.TestCase):
    def test_all_protected_sources_match_manifest(self) -> None:
        self.assertEqual(verify(REPOSITORY_ROOT), [])

    def test_recovered_notebook_hash_is_pinned(self) -> None:
        manifest = load_manifest(REPOSITORY_ROOT)
        sources = {source["path"]: source for source in manifest["sources"]}
        recovered = sources["notebooks/tcc-recovered-from-colab.ipynb"]
        self.assertEqual(
            recovered["sha256"],
            "7c58b4b0d0a9cae0accd49f77cd46fd8fd02316961ec588394463b5e9456f330",
        )

    def test_reconstructed_notebook_hash_is_pinned(self) -> None:
        manifest = load_manifest(REPOSITORY_ROOT)
        sources = {source["path"]: source for source in manifest["sources"]}
        reconstructed = sources["notebooks/tcc-reconstructed.ipynb"]
        self.assertTrue(reconstructed["immutable"])
        self.assertEqual(reconstructed["role"], "completed_reconstruction_snapshot")
        self.assertEqual(
            reconstructed["sha256"],
            "4b9f385dd51a798248dd6bfcbf0ad2e8815f90de7bc5fb59cd98a7431057d044",
        )


if __name__ == "__main__":
    unittest.main()
