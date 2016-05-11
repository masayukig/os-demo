import unittest
from coveragelink import CoverageLink


class CoverageLinkTestsCase(unittest.TestCase):

    def test_object(self):

        project = 'demo'
        url = 'invalid'
        link = CoverageLink(project, url, type)
        assertEquals(link.project, project)
        assertEquals(link.url, url)
        assertEquals(link.type, 'unknown')
        assertFalse(link.isValid())
