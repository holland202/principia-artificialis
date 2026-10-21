"""No repo writes, no scientific runs: adversarial synthetic fixtures for doc_evidence_check."""
import tempfile
import unittest
from pathlib import Path

import doc_evidence_check as checker


class DocumentaryEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'docs').mkdir()
        (self.root / 'README.md').write_text('# readme\n', encoding='utf-8')

    def tearDown(self):
        self.tmp.cleanup()

    def inspect(self, markdown, name='docs/new.md'):
        return checker.audit_text(self.root, Path(name), markdown)

    def test_existing_relative_and_anchored_file(self):
        errors, _ = self.inspect('[repo](../README.md#some-heading)')
        self.assertEqual([], errors)

    def test_missing_local_link_fails(self):
        errors, _ = self.inspect('[gone](../not-there.md)')
        self.assertEqual(1, len(errors))
        self.assertIn('BROKEN_LOCAL_LINK', errors[0])

    def test_reference_style_definition(self):
        errors, _ = self.inspect('[source][s]\n\n[s]: ../unknown.md')
        self.assertEqual(1, len(errors))

    def test_image_target_checked(self):
        errors, _ = self.inspect('![diagram](../missing.png)')
        self.assertEqual(1, len(errors))

    def test_external_and_anchor_only_ignored(self):
        errors, _ = self.inspect('[web](https://example.org/a) [mailto](mailto:someone@example.org) [heading](#local)')
        self.assertEqual([], errors)

    def test_fenced_and_inline_code_ignored(self):
        errors, _ = self.inspect('`[pretend](../bad.md)`\n```md\n[pretend](../bad.md)\n```')
        self.assertEqual([], errors)

    def test_percent_decoding(self):
        (self.root / 'docs' / 'two words.md').write_text('ok', encoding='utf-8')
        errors, _ = self.inspect('[ok](two%20words.md)')
        self.assertEqual([], errors)

    def test_escaping_repo_is_rejected(self):
        errors, _ = self.inspect('[oops](../../../../etc/passwd)')
        self.assertEqual(1, len(errors))
        self.assertIn('escapes repository', errors[0])

    def test_verified_language_is_advisory_not_verdict(self):
        errors, advisories = self.inspect('Tests passed successfully.')
        self.assertEqual([], errors)
        self.assertEqual(1, len(advisories))
        self.assertIn('REVIEW_EVIDENCE_POINTER', advisories[0])

    def test_named_source_suppresses_heuristic_lead(self):
        errors, advisories = self.inspect('Tests passed.\nReference code: `scripts/example.py`')
        self.assertEqual([], errors)
        self.assertEqual([], advisories)

    def test_missing_input_fails_closed(self):
        errors, _ = checker.audit_file(self.root, 'docs/absent.md')
        self.assertEqual(1, len(errors))

    def test_positive_and_negative_instrument(self):
        self.assertTrue(checker.selftest())
        self.assertEqual(0, checker.main(['--selftest']))
        self.assertEqual(1, checker.main(['--sabotage']))

    def test_check_file_in_subfolder(self):
        (self.root / 'docs' / 'new.md').write_text('[repo](../README.md)', encoding='utf-8')
        self.assertEqual(([], []), checker.audit_file(self.root, 'docs/new.md'))


if __name__ == '__main__':
    unittest.main()
