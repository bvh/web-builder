import pytest

from web_builder.node import NodeType
from web_builder.scanner import scan_source


def test_scan_returns_home_node(sample_source_tree):
    root = scan_source(str(sample_source_tree))
    assert root.type == NodeType.HOME


def test_scan_finds_subdirectory(sample_source_tree):
    root = scan_source(str(sample_source_tree))
    child_names = {c.source.name for c in root.children}
    assert "about" in child_names
    about = next(c for c in root.children if c.source.name == "about")
    assert about.type == NodeType.DIRECTORY


def test_scan_finds_static_file(sample_source_tree):
    root = scan_source(str(sample_source_tree))
    child_names = {c.source.name for c in root.children}
    assert "favicon.ico" in child_names


def test_scan_attaches_index_md_as_content(sample_source_tree):
    root = scan_source(str(sample_source_tree))
    assert root.content_source is not None
    assert root.content_source.name == "index.md"


def test_scan_attaches_config_json_as_config(sample_source_tree):
    root = scan_source(str(sample_source_tree))
    assert root.config_source is not None
    assert root.config_source.name == "config.json"


def test_scan_index_md_not_a_child_node(sample_source_tree):
    root = scan_source(str(sample_source_tree))
    child_names = {c.source.name for c in root.children}
    assert "index.md" not in child_names


def test_scan_config_json_not_a_child_node(sample_source_tree):
    root = scan_source(str(sample_source_tree))
    child_names = {c.source.name for c in root.children}
    assert "config.json" not in child_names


def test_scan_skips_dotfiles(sample_source_tree):
    root = scan_source(str(sample_source_tree))
    child_names = {c.source.name for c in root.children}
    assert ".hidden" not in child_names


def test_scan_skips_symlinks(sample_source_with_symlink):
    root = scan_source(str(sample_source_with_symlink))
    child_names = {c.source.name for c in root.children}
    assert "link_to_about" not in child_names


def test_scan_nonexistent_path_raises(tmp_path):
    with pytest.raises(ValueError, match="does not exist"):
        scan_source(str(tmp_path / "nonexistent"))


def test_scan_file_path_raises(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("hello")
    with pytest.raises(ValueError, match="must be a directory"):
        scan_source(str(f))


def test_scan_nested_structure(sample_source_tree):
    root = scan_source(str(sample_source_tree))
    photos = next(c for c in root.children if c.source.name == "photos")
    photo_child_names = {c.source.name for c in photos.children}
    assert "photo.jpg" in photo_child_names


def test_scan_subdirectory_content(sample_source_tree):
    root = scan_source(str(sample_source_tree))
    about = next(c for c in root.children if c.source.name == "about")
    assert about.content_source is not None
    assert about.content_source.name == "index.md"
