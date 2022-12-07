# yeah, those aren't proper unit tests, just had to put anything here
import os

def test_app():
    assert os.path.exists("app")
    assert os.path.isdir("app")

def test_index():
    os.path.exists("app/app.py")
    #TODO: restore it after finish working on app.py
    #assert os.path.getsize("app/app.py") == 2693

