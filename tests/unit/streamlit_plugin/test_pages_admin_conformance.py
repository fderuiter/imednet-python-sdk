from __future__ import annotations
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock
import importlib.util

REPO_ROOT = Path(__file__).resolve().parents[3]
PACKAGE_ROOT = REPO_ROOT / "packages" / "plugins-streamlit" / "src" / "imednet_streamlit"

class _FakeStreamlit:
    def __init__(self):
        self.titles = []
        self.markdowns = []
        self.successes = []
        self.errors = []
        self.infos = []
    
    def title(self, text):
        self.titles.append(text)
    
    def markdown(self, text):
        self.markdowns.append(text)
        
    def text_input(self, label, **kwargs):
        return "fake_" + label
        
    def button(self, label):
        return True
        
    def success(self, text):
        self.successes.append(text)
        
    def error(self, text):
        self.errors.append(text)
        
    def info(self, text):
        self.infos.append(text)
        
    def subheader(self, text):
        pass
        
    def json(self, data):
        pass
        
    def download_button(self, *args, **kwargs):
        pass

def test_admin_page():
    fake_st = _FakeStreamlit()
    fake_st_module = ModuleType("streamlit")
    for attr in dir(fake_st):
        if not attr.startswith("_"):
            setattr(fake_st_module, attr, getattr(fake_st, attr))
    
    saved = sys.modules.get("streamlit")
    sys.modules["streamlit"] = fake_st_module
    try:
        page_path = PACKAGE_ROOT / "pages" / "admin.py"
        module_name = "imednet_streamlit.pages.admin"
        module_spec = importlib.util.spec_from_file_location(module_name, page_path)
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module
        module_spec.loader.exec_module(module)
        
        assert "🏢 Enterprise Admin Portal" in fake_st.titles
    finally:
        if saved is None:
            del sys.modules["streamlit"]
        else:
            sys.modules["streamlit"] = saved

def test_conformance_page():
    fake_st = _FakeStreamlit()
    fake_st_module = ModuleType("streamlit")
    for attr in dir(fake_st):
        if not attr.startswith("_"):
            setattr(fake_st_module, attr, getattr(fake_st, attr))
            
    saved = sys.modules.get("streamlit")
    sys.modules["streamlit"] = fake_st_module
    try:
        page_path = PACKAGE_ROOT / "pages" / "conformance.py"
        module_name = "imednet_streamlit.pages.conformance"
        module_spec = importlib.util.spec_from_file_location(module_name, page_path)
        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module
        module_spec.loader.exec_module(module)
        
        assert "♿ Accessibility Conformance Portal" in fake_st.titles
    finally:
        if saved is None:
            del sys.modules["streamlit"]
        else:
            sys.modules["streamlit"] = saved
