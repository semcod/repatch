import unittest
from types import SimpleNamespace

from repatch import RepatchService


class RepatchServiceTests(unittest.TestCase):
    def test_rejects_invalid_scope(self):
        service = RepatchService(model="test-model", completion_fn=lambda **_: None)
        with self.assertRaises(ValueError):
            service.generate_patch_suggestions("<div />", ["display", "invalid"])

    def test_returns_three_variants_from_completion(self):
        captured = {}

        def fake_completion(**kwargs):
            captured.update(kwargs)
            choices = [
                SimpleNamespace(
                    message=SimpleNamespace(
                        content='{"keep":["title"],"change":["button"],"patched_fragment":"<h1>A</h1>"}'
                    )
                ),
                SimpleNamespace(
                    message=SimpleNamespace(
                        content='{"keep":["subtitle"],"change":["colors"],"patched_fragment":"<h1>B</h1>"}'
                    )
                ),
                SimpleNamespace(
                    message=SimpleNamespace(
                        content='{"keep":["cta"],"change":["layout"],"patched_fragment":"<h1>C</h1>"}'
                    )
                ),
            ]
            return SimpleNamespace(choices=choices)

        service = RepatchService(model="test-model", completion_fn=fake_completion)
        result = service.generate_patch_suggestions(
            fragment="<button>Zapisz dziecko</button>",
            scopes=["display", "colors"],
        )

        self.assertEqual(3, len(result))
        self.assertEqual(3, captured["n"])
        self.assertEqual({"type": "json_object"}, captured["response_format"])
        self.assertEqual("test-model", captured["model"])
        self.assertIn("Selected scopes: colors, display", captured["messages"][1]["content"])
        self.assertIn("<button>Zapisz dziecko</button>", captured["messages"][1]["content"])
        self.assertEqual(["title"], result[0].keep)


if __name__ == "__main__":
    unittest.main()
