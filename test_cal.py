from unittest import TestCase
from unittest.mock import Mock, patch, PropertyMock

import cal


class MyTestCase(TestCase):
    def test_real(self):
        c: cal.DBAPI = cal.DatabaseAPI()
        app = cal.LogSystem(c)
        print(app.log_message("hi"))

