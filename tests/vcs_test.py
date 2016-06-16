import unittest
import os.path
import shutil
from rostam.vcs.git import Git


class GitTest(unittest.TestCase):
    def test_git_pull(self):
        dir = "./tests/temp/test"
        if os.path.exists(dir):
            shutil.rmtree(dir)
        repo = Git(repo_url="https://github.com/abzcoding/test.git", repo_path=dir)
        repo.pull()
        readme = dir + "/README.md"
        # check if repository was cloned correctly
        self.assertTrue(os.path.isfile(readme))
        # check the content of cloned file
        with open(readme, 'rb') as inp:
            data = inp.read()
            self.assertEqual(data, "# test\n")


if __name__ == '__main__':
    unittest.main()
