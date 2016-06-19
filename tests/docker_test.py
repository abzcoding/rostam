import unittest
from rostam.docker.api import DockerApi
from requests.exceptions import ConnectionError


class APITest(unittest.TestCase):
    def test_client_version(self):
        cli = DockerApi()
        try:
            self.assertEqual(cli.version()['Os'], 'linux')
        except ConnectionError:
            print "cannot connect to docker api"

    def test_client_build(self):
        cli = DockerApi()
        output = ""
        build_result = "succeed"
        try:
            output = cli.build(directory=".\\tests\\docker", tag="test", timeout=100)
        except (RuntimeError, ConnectionError):
            build_result = 'failed'
        if build_result != 'failed':
            self.assertIn('{"stream":"Step 1 : FROM scratch\\n"}\r\n', output)
            self.assertIn('{"stream":"Step 2 : COPY hello /\\n"}\r\n', output)
            self.assertIn('{"stream":"Step 3 : CMD /hello\\n"}\r\n', output)
            self.assertTrue('Successfully built' in output[-1])


if __name__ == '__main__':
    unittest.main()
