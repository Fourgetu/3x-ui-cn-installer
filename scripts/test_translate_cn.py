import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location("translate_cn", Path(__file__).with_name("translate-cn.py"))
translator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(translator)


class ReleaseURLTests(unittest.TestCase):
    def test_release_refs_keep_chinese_menu_and_tagged_services(self):
        target = "https://raw.githubusercontent.com/Fourgetu/3x-ui-cn-installer/main"
        for ref in ("${script_ref}", "v${ver}", "v3.9.0-fourgetu.2"):
            with self.subTest(ref=ref), tempfile.TemporaryDirectory() as tmp:
                base = f"https://raw.githubusercontent.com/Fourgetu/3x-ui/{ref}"
                path = Path(tmp) / "installer.sh"
                path.write_text(
                    f'echo "{base}/x-ui.sh"\n'
                    f'echo "{base}/install.sh"\n'
                    f'echo "{base}/x-ui.service.debian"\n'
                    f'echo "{base}/update.sh"\n', encoding="utf-8"
                )
                translator.patch_urls(path, "Fourgetu/3x-ui", "main", target, "Fourgetu/3x-ui")
                patched = path.read_text(encoding="utf-8")
                self.assertIn(f'{target}/x-ui-cn.sh', patched)
                self.assertIn(f'{target}/install-cn.sh', patched)
                self.assertNotIn(f'{base}/x-ui.sh', patched)
                self.assertIn(f'{base}/x-ui.service.debian', patched)
                self.assertIn(f'{base}/update.sh', patched)


if __name__ == "__main__":
    unittest.main()
