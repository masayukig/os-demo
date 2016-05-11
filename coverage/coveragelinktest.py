import unittest
from coveragelink import CoverageLink


class CoverageLinkTestsCase(unittest.TestCase):

    def test_object(self):
        project = 'demo'
        url = 'invalid'
        link = CoverageLink(project, url)
        self.assertEqual(link.project, project)
        self.assertEqual(link.url, url)
        self.assertIsNone(link.type)
        self.assertEqual(link.status, 'unknown')
        self.assertFalse(link.isValid())
        json = link.json()
        self.assertEqual(json['project'], project)
        self.assertEqual(json['url'], url)
        self.assertEqual(json['status'], 'unknown')

    def test_invalid_url(self):
        project = 'demo'
        url = 'invalid'
        link = CoverageLink(project, url)
        with self.assertRaisesRegexp(Exception,'Invalid URL'):
          link.validate()

    def test_valid_url(self):
        project = 'magnum'
        url = 'http://logs.openstack.org/07/07ec627ca09c477dc620ea25443f6da604d9eb46/post/magnum-coverage/b97f0c2/cover/'
        link = CoverageLink(project, url)
        self.assertTrue(link.validate())

if __name__ == '__main__':
    unittest.main()
