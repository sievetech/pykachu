# -*- coding: utf-8 -*-
#!/usr/bin/env python

import unittest
import mock


class TestJob(unittest.TestCase):
    def test_maximum_step(self):
        from pykachu import Job
        j = Job(total=1)
        with mock.patch.object(j, "connection"):
            j.another_step()
            j.another_step()
            self.assertEqual(1, j.last_step)


if __name__ == "__main__":
    unittest.main()