from pathlib import Path

from web_builder.node import Node, NodeType


# --- Type determination ---


def test_directory_without_parent_is_home(tmp_path):
    node = Node(tmp_path)
    assert node.type == NodeType.HOME


def test_directory_with_parent_is_directory(tmp_path):
    child_dir = tmp_path / "about"
    child_dir.mkdir()
    parent = Node(tmp_path)
    child = Node(child_dir, parent)
    assert child.type == NodeType.DIRECTORY


def test_markdown_file_is_page(tmp_path):
    md_file = tmp_path / "post.md"
    md_file.write_text("# Post")
    parent = Node(tmp_path)
    node = Node(md_file, parent)
    assert node.type == NodeType.PAGE


def test_jpg_file_is_image(tmp_path):
    jpg_file = tmp_path / "photo.jpg"
    jpg_file.write_bytes(b"\xff")
    parent = Node(tmp_path)
    node = Node(jpg_file, parent)
    assert node.type == NodeType.IMAGE


def test_jpeg_file_is_image(tmp_path):
    jpeg_file = tmp_path / "photo.jpeg"
    jpeg_file.write_bytes(b"\xff")
    parent = Node(tmp_path)
    node = Node(jpeg_file, parent)
    assert node.type == NodeType.IMAGE


def test_ico_file_is_static(tmp_path):
    ico_file = tmp_path / "favicon.ico"
    ico_file.write_bytes(b"\x00")
    parent = Node(tmp_path)
    node = Node(ico_file, parent)
    assert node.type == NodeType.STATIC


def test_no_extension_is_static(tmp_path):
    no_ext = tmp_path / "README"
    no_ext.write_text("readme")
    parent = Node(tmp_path)
    node = Node(no_ext, parent)
    assert node.type == NodeType.STATIC


# --- Parent-child registration ---


def test_child_registered_with_parent(tmp_path):
    child_dir = tmp_path / "sub"
    child_dir.mkdir()
    parent = Node(tmp_path)
    child = Node(child_dir, parent)
    assert child in parent.children
    assert child.parent is parent


def test_multiple_children(tmp_path):
    parent = Node(tmp_path)
    for name in ["a.txt", "b.txt", "c.txt"]:
        f = tmp_path / name
        f.write_text("")
        Node(f, parent)
    assert len(parent.children) == 3


def test_add_content(tmp_path):
    node = Node(tmp_path)
    content_path = tmp_path / "index.md"
    content_path.write_text("# Hello")
    node.add_content(content_path)
    assert node.content_source == content_path


def test_add_config(tmp_path):
    node = Node(tmp_path)
    config_path = tmp_path / "config.json"
    config_path.write_text("{}")
    node.add_config(config_path)
    assert node.config_source == config_path


# --- Target path computation ---


def test_home_directory_target_is_none(tmp_path):
    node = Node(tmp_path)
    assert node.directory_target is None


def test_home_content_target(tmp_path):
    node = Node(tmp_path)
    assert node.content_target == Path("index.html")


def test_home_copy_target_is_none(tmp_path):
    node = Node(tmp_path)
    assert node.copy_target is None


def test_directory_directory_target(tmp_path):
    child_dir = tmp_path / "about"
    child_dir.mkdir()
    parent = Node(tmp_path)
    child = Node(child_dir, parent)
    assert child.directory_target == Path("about")


def test_directory_content_target(tmp_path):
    child_dir = tmp_path / "about"
    child_dir.mkdir()
    parent = Node(tmp_path)
    child = Node(child_dir, parent)
    assert child.content_target == Path("about/index.html")


def test_page_directory_target(tmp_path):
    md_file = tmp_path / "post.md"
    md_file.write_text("# Post")
    parent = Node(tmp_path)
    node = Node(md_file, parent)
    assert node.directory_target == Path("post")


def test_page_content_target(tmp_path):
    md_file = tmp_path / "post.md"
    md_file.write_text("# Post")
    parent = Node(tmp_path)
    node = Node(md_file, parent)
    assert node.content_target == Path("post/index.html")


def test_page_copy_target_is_none(tmp_path):
    md_file = tmp_path / "post.md"
    md_file.write_text("# Post")
    parent = Node(tmp_path)
    node = Node(md_file, parent)
    assert node.copy_target is None


def test_image_directory_target(tmp_path):
    jpg = tmp_path / "photo.jpg"
    jpg.write_bytes(b"\xff")
    parent = Node(tmp_path)
    node = Node(jpg, parent)
    assert node.directory_target == Path("photo")


def test_image_copy_target(tmp_path):
    jpg = tmp_path / "photo.jpg"
    jpg.write_bytes(b"\xff")
    parent = Node(tmp_path)
    node = Node(jpg, parent)
    assert node.copy_target == Path("photo/photo.jpg")


def test_image_content_target(tmp_path):
    jpg = tmp_path / "photo.jpg"
    jpg.write_bytes(b"\xff")
    parent = Node(tmp_path)
    node = Node(jpg, parent)
    assert node.content_target == Path("photo/index.html")


def test_static_copy_target(tmp_path):
    ico = tmp_path / "favicon.ico"
    ico.write_bytes(b"\x00")
    parent = Node(tmp_path)
    node = Node(ico, parent)
    assert node.copy_target == Path("favicon.ico")


def test_static_directory_target_is_none(tmp_path):
    ico = tmp_path / "favicon.ico"
    ico.write_bytes(b"\x00")
    parent = Node(tmp_path)
    node = Node(ico, parent)
    assert node.directory_target is None


def test_static_content_target_is_none(tmp_path):
    ico = tmp_path / "favicon.ico"
    ico.write_bytes(b"\x00")
    parent = Node(tmp_path)
    node = Node(ico, parent)
    assert node.content_target is None
