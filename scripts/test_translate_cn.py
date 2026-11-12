import importlib.util
import os
import subprocess
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


class ShellTranslationTests(unittest.TestCase):
    def test_parameter_expansions_are_not_translated(self):
        for expression in (
            '${WebPort:-80}', '${Port:-80}', '${Port:=80}', '${Port:?No Port:}',
            '${Port:+Yes}', '${No}', '${No//Yes/No}', '${Port:-${No:-80}}',
            '${Port:-No\nPort:}', '${Port:-"}No"}', '${Port:-"{No"}', r'${Port:-\}No}', '${Port:-No',
        ):
            with self.subTest(expression=expression):
                self.assertEqual(translator.translate_text(expression), expression)

    def test_words_and_identifiers_are_not_partially_translated(self):
        text = 'WebPort: Note: Nothing Restored YesValue No_1 _No No1 $No $Yes'
        self.assertEqual(translator.translate_text(text), text)

    def test_display_labels_still_translate(self):
        self.assertEqual(translator.translate_text('Port: ${WebPort:-80}'),
                         '端口： ${WebPort:-80}')
        self.assertEqual(translator.translate_text('Yes / No'), '是 / 否')
        self.assertEqual(translator.translate_text('Not Running'), '未运行')
        self.assertEqual(translator.translate_text(r'\nChoose an option:'), r'\n请选择一个选项:')
        self.assertEqual(translator.translate_text('Note: Port: 80'), 'Note: 端口： 80')

    def test_translated_port_default_executes_in_bash(self):
        code = translator.translate_text('WebPort="${WebPort:-80}"\nprintf "%s" "$WebPort"\n')
        for value, expected in (('', '80'), ('8080', '8080'), ('65535', '65535')):
            with self.subTest(value=value):
                result = subprocess.run(
                    ['bash', '-eu', '-c', 'WebPort="$1"\n' + code, 'test', value],
                    capture_output=True, text=True, check=True,
                )
                self.assertEqual(result.stdout, expected)
                self.assertEqual(result.stderr, '')

    def test_multiline_file_preserves_parameter_defaults(self):
        text = 'echo "Port: ${Port:-No\nPort:}"\n'
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / 'in.sh', Path(tmp) / 'out.sh'
            src.write_text(text, encoding='utf-8')
            translator.translate_file(src, dst)
            self.assertEqual(dst.read_text(encoding='utf-8'),
                             'echo "端口： ${Port:-No\nPort:}"\n')

    def test_shipped_ip_certificate_port_paths(self):
        # Run the shipped port-selection/issue block only. Mock ACME and port
        # checks so this cannot install software, touch certificates or listen.
        root = Path(__file__).resolve().parents[1]
        prelude = r"""
set -e
prompt_or_default() { printf -v "$1" '%s' "$TEST_PORT"; }
is_port_in_use() { [[ "$BUSY" == 1 && "$1" == 80 ]]; }
LOGI() { echo "$*"; }
LOGE() { echo "$*"; }
fake_acme() { printf 'ACME'; printf ' <%s>' "$@"; printf '\n'; }
run_test() {
local ipv4=192.0.2.10 server_ip=192.0.2.10 domain_args='-d 192.0.2.10'
local green='' yellow='' red='' plain='' NONINTERACTIVE=0
"""
        cases = (
            ('default', '', 0, '', 80), ('custom', '8080', 0, '', 8080),
            ('invalid', 'oops', 0, '', 80), ('out_of_range', '65536', 0, '', 80),
            ('busy_abort', '', 1, '', None), ('busy_alternative', '', 1, '8081', 8081),
        )
        for filename in ('install-cn.sh', 'x-ui-cn.sh'):
            source = (root / filename).read_text(encoding='utf-8')
            start = source.index('    local WebPort=""', source.index('shortlived profile'))
            issue = source.index('        --certificate-profile shortlived', start)
            end = source.index('\n    if [ $? -ne 0 ]; then', issue)
            block = source[start:end].replace('~/.acme.sh/acme.sh', 'fake_acme')
            for name, port, busy, alt, expected in cases:
                with self.subTest(file=filename, case=name):
                    stdin = (port + '\n' if filename == 'x-ui-cn.sh' else '') + alt + '\n'
                    result = subprocess.run(
                        ['bash', '-c', prelude + block + '\n}\nrun_test\n'],
                        input=stdin, text=True, capture_output=True,
                        env=dict(os.environ, TEST_PORT=port, BUSY=str(busy)),
                    )
                    self.assertNotIn('bad substitution', result.stderr)
                    if expected is None:
                        self.assertNotEqual(result.returncode, 0)
                        self.assertNotIn('ACME', result.stdout)
                    else:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertIn(f'<--httpport> <{expected}>', result.stdout)
                        self.assertIn('<--certificate-profile> <shortlived>', result.stdout)


if __name__ == "__main__":
    unittest.main()
