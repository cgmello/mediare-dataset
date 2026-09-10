import json
from pathlib import Path
import tempfile
import unittest

from coletar_cjpg import carregar_processos, parse_pagina


PROCESSO = "1234567-89.2025.8.26.0001"


class ColetarCjpgTests(unittest.TestCase):
    def test_parse_extracts_body_and_short_metadata(self):
        body = "Fundamentação pública da decisão. " * 30
        html = f"""
        <table><tr class="fundocinza1"><td>
          Processo: {PROCESSO} Classe: Procedimento Comum Cível
          Assunto: Danos Materiais Comarca: São Paulo Vara: 1ª Vara
          Data de Disponibilização: 01/09/2026
          <div class="mensagemSemFormatacao">{body}</div>
        </td></tr></table>
        """
        rows = parse_pagina(html)
        self.assertEqual(rows[0]["processo"], PROCESSO)
        self.assertEqual(rows[0]["classe"], "Procedimento Comum Cível")
        self.assertIn("Fundamentação pública", rows[0]["texto"])

    def test_malformed_long_metadata_is_not_accepted(self):
        body = "corpo " * 200
        html = f"""
        <table><tr class="fundocinza1"><td>
          {PROCESSO} Data de Disponibilização: {body}
          <div class="mensagemSemFormatacao">{body}</div>
        </td></tr></table>
        """
        row = parse_pagina(html)[0]
        self.assertNotIn("data", row)
        self.assertGreater(len(row["texto"]), 400)

    def test_load_processes_deduplicates_and_ignores_invalid_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.jsonl"
            second = Path(directory) / "second.jsonl"
            first.write_text(
                json.dumps({"processo": PROCESSO}) + "\nnot-json\n",
                encoding="utf-8",
            )
            second.write_text(
                json.dumps({"processo": PROCESSO}) + "\n",
                encoding="utf-8",
            )
            self.assertEqual(carregar_processos([first, second]), {PROCESSO})


if __name__ == "__main__":
    unittest.main()
