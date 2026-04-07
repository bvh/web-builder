import pytest


@pytest.fixture
def sample_source_tree(tmp_path):
    """Create a minimal source directory tree for testing."""
    source = tmp_path / "source"
    source.mkdir()

    # Root-level files
    (source / "index.md").write_text("# Home")
    (source / "config.json").write_text("{}")
    (source / "favicon.ico").write_bytes(b"\x00")

    # Subdirectory with markdown
    about = source / "about"
    about.mkdir()
    (about / "index.md").write_text("# About")

    # Subdirectory with an image
    photos = source / "photos"
    photos.mkdir()
    (photos / "photo.jpg").write_bytes(b"\xff\xd8\xff")

    # Dotfile (should be skipped)
    (source / ".hidden").write_text("secret")

    return source


@pytest.fixture
def sample_source_with_symlink(sample_source_tree):
    """Extend sample_source_tree with a symlink (should be skipped)."""
    link = sample_source_tree / "link_to_about"
    link.symlink_to(sample_source_tree / "about")
    return sample_source_tree
