import io
import pytest
import sys

from custom_python_actions.check_sort import check_sort


def test_check_sort_succeeds():
    check_sort(".github/tests/test_data/open-repositories-1.txt")


def test_check_sort_fails():
    filename = ".github/tests/test_data/open-repositories-2.txt"
    errorMessage = f"{filename} is not correctly sorted"

    with pytest.raises(Exception):
        capturedOutput = io.StringIO()
        check_sort(filename)
        sys.stdout = capturedOutput

        assert capturedOutput.getvalue() == errorMessage
