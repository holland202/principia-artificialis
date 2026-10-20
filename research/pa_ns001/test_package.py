import hashlib
from pathlib import Path
import tempfile
import unittest

from verify_package import check


class TestPackage(unittest.TestCase):
    def manifest(self, data=b'public fixture\n'):
        return {'schema': 'pa-ns001-package/1', 'files': [{'path': 'fixture.txt', 'bytes': len(data),
                'sha256': hashlib.sha256(data).hexdigest(), 'md5': hashlib.md5(data).hexdigest()}]}

    def test_genuine_and_modified_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'fixture.txt'
            path.write_bytes(b'public fixture\n')
            self.assertTrue(check(temp, self.manifest())['accepted'])
            path.write_bytes(b'changed fixture\n')
            self.assertFalse(check(temp, self.manifest())['accepted'])

    def test_missing_file_never_skips(self):
        with tempfile.TemporaryDirectory() as temp:
            result = check(temp, self.manifest())
            self.assertFalse(result['accepted'])
            self.assertEqual(result['failures'][0]['reason'], 'missing')

    def test_empty_and_malformed_manifests(self):
        for manifest in ({}, None, {'schema': 'pa-ns001-package/1', 'files': []}):
            with self.assertRaises(ValueError):
                check('.', manifest)

    def test_paths_and_duplicates_are_rejected(self):
        for name in ('../outside', '/outside'):
            manifest = self.manifest()
            manifest['files'][0]['path'] = name
            with self.assertRaises(ValueError):
                check('.', manifest)
        manifest = self.manifest()
        manifest['files'].append(manifest['files'][0])
        with self.assertRaises(ValueError):
            check('.', manifest)


if __name__ == '__main__':
    unittest.main()
