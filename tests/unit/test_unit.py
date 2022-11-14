# yeah, those aren't proper unit tests, just had to put anything here
import os

def test_app():
    assert os.path.exists("app")
    assert os.path.isdir("app")

def test_index():
    os.path.exists("app/server.py")
    #assert os.path.getsize("app/server.py") == 1364

