from web_builder.builder import build_target
from web_builder.scanner import scan_source


def test_build_creates_target_directory(sample_source_tree, tmp_path):
    target = tmp_path / "target"
    root = scan_source(str(sample_source_tree))
    build_target(str(target), root)
    assert target.is_dir()


def test_build_creates_index_html_at_root(sample_source_tree, tmp_path):
    target = tmp_path / "target"
    root = scan_source(str(sample_source_tree))
    build_target(str(target), root)
    assert (target / "index.html").exists()


def test_build_renders_markdown_content(sample_source_tree, tmp_path):
    target = tmp_path / "target"
    root = scan_source(str(sample_source_tree))
    build_target(str(target), root)
    html = (target / "index.html").read_text()
    assert "<h1>Home</h1>" in html


def test_build_missing_content_uses_fallback(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    # No index.md — should get fallback text
    target = tmp_path / "target"
    root = scan_source(str(source))
    build_target(str(target), root)
    html = (target / "index.html").read_text()
    assert "No content provided." in html


def test_build_creates_subdirectory(sample_source_tree, tmp_path):
    target = tmp_path / "target"
    root = scan_source(str(sample_source_tree))
    build_target(str(target), root)
    assert (target / "about").is_dir()


def test_build_copies_image_with_pretty_url(sample_source_tree, tmp_path):
    target = tmp_path / "target"
    root = scan_source(str(sample_source_tree))
    build_target(str(target), root)
    assert (target / "photos" / "photo" / "photo.jpg").exists()


def test_build_copies_static_file(sample_source_tree, tmp_path):
    target = tmp_path / "target"
    root = scan_source(str(sample_source_tree))
    build_target(str(target), root)
    assert (target / "favicon.ico").exists()


def test_build_image_gets_index_html(sample_source_tree, tmp_path):
    target = tmp_path / "target"
    root = scan_source(str(sample_source_tree))
    build_target(str(target), root)
    assert (target / "photos" / "photo" / "index.html").exists()


# TODO: This failing test is legit. Fix Node and/or builder code.
# Interestingly enough, Claude wrote this test, noticed it was failing, and
# confidently asserted that the existing (broken) code must be correct. (See
# comment below.) It then "corrected" this test to assert the "No content
# provided" placeholder. Hopefully it doesn't do this sort of thing with code
# that it writes as well.
def test_build_page_gets_own_directory(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    # TODO: Wrong! post.md should generate the content for post/index.html.
    # Standalone .md files (not index.md) become PAGE nodes with their own
    # directory, but their content isn't attached — only index.md is treated
    # as content for the parent directory.
    (source / "post.md").write_text("# My Post")
    target = tmp_path / "target"
    root = scan_source(str(source))
    build_target(str(target), root)
    assert (target / "post" / "index.html").exists()
    html = (target / "post" / "index.html").read_text()
    assert "<h1>My Post</h1>" in html


def test_build_output_is_valid_html(sample_source_tree, tmp_path):
    target = tmp_path / "target"
    root = scan_source(str(sample_source_tree))
    build_target(str(target), root)
    html = (target / "index.html").read_text()
    assert "<!DOCTYPE html>" in html
    assert "<title>" in html
    assert "</html>" in html


def test_build_image_template_has_img_tag(sample_source_tree, tmp_path):
    target = tmp_path / "target"
    root = scan_source(str(sample_source_tree))
    build_target(str(target), root)
    html = (target / "photos" / "photo" / "index.html").read_text()
    assert '<img src="photo.jpg"' in html
    assert "<title>photo.jpg</title>" in html


def test_build_backs_up_existing_target(sample_source_tree, tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    (target / "old_file.txt").write_text("old")

    root = scan_source(str(sample_source_tree))
    build_target(str(target), root)

    # New target should exist with fresh content
    assert (target / "index.html").exists()

    # Old target should have been renamed with timestamp suffix
    backup_dirs = [
        p for p in tmp_path.iterdir() if p.name.startswith("target.") and p.is_dir()
    ]
    assert len(backup_dirs) == 1
    assert (backup_dirs[0] / "old_file.txt").exists()
