from app.api.reports import ALLOWED_IMAGE_TYPES, VALID_WORKFLOW, _safe_filename, _verified_image_mime


def test_image_magic_bytes_are_verified_not_taken_from_client_header() -> None:
    assert _verified_image_mime(b"\xff\xd8\xffpayload") == "image/jpeg"
    assert _verified_image_mime(b"\x89PNG\r\n\x1a\npayload") == "image/png"
    assert _verified_image_mime(b"RIFFxxxxWEBPpayload") == "image/webp"
    assert _verified_image_mime(b"not really an image") is None


def test_safe_filename_replaces_unsafe_names_and_enforces_extension() -> None:
    assert _safe_filename("../../secret.exe", "image/png") == "attachment.png"
    assert _safe_filename("road photo.png", "image/png") == "road_photo.png"
    assert set(ALLOWED_IMAGE_TYPES) == {"image/jpeg", "image/png", "image/webp"}


def test_report_workflow_has_terminal_closed_state() -> None:
    assert VALID_WORKFLOW["SUBMITTED"] == {"UNDER_REVIEW", "REJECTED"}
    assert VALID_WORKFLOW["RESOLVED"] == {"CLOSED"}
    assert VALID_WORKFLOW["CLOSED"] == set()
