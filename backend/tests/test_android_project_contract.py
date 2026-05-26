# -*- coding: utf-8 -*-
"""
Android project structure contract tests.

These tests verify that the Android thin client has the minimum source and
resource files referenced by AndroidManifest.xml.
"""

from pathlib import Path


ANDROID_ROOT = Path(__file__).resolve().parents[2] / "android" / "app" / "src" / "main"


def _read(relative_path: str) -> str:
    """Read an Android project file as UTF-8 text."""
    return (ANDROID_ROOT / relative_path).read_text(encoding="utf-8")


def test_manifest_referenced_activity_and_resources_exist():
    """Manifest references must resolve to concrete local files/resources."""
    assert (ANDROID_ROOT / "java/com/mybizcon/client/MainActivity.kt").exists()
    assert (ANDROID_ROOT / "res/values/strings.xml").exists()
    assert (ANDROID_ROOT / "res/values/styles.xml").exists()
    assert (ANDROID_ROOT / "res/mipmap/ic_launcher.xml").exists()
    assert (ANDROID_ROOT / "res/mipmap/ic_launcher_round.xml").exists()


def test_main_activity_provides_permission_shortcuts():
    """Launcher activity should expose accessibility and overlay settings shortcuts."""
    source = _read("java/com/mybizcon/client/MainActivity.kt")
    assert "Settings.ACTION_ACCESSIBILITY_SETTINGS" in source
    assert "Settings.ACTION_MANAGE_OVERLAY_PERMISSION" in source


def test_overlay_uses_active_accessibility_service_not_new_instance():
    """Overlay must not instantiate AccessibilityService directly."""
    overlay = _read("java/com/mybizcon/client/TranslationOverlayService.kt")
    service = _read("java/com/mybizcon/client/MyBIZconAccessibilityService.kt")
    assert "MyBIZconAccessibilityService().injectSuggestedReply" not in overlay
    assert "MyBIZconAccessibilityService.injectIntoActiveMessenger" in overlay
    assert "activeInstance = this" in service
    assert "fun injectSuggestedReply(draftText: String): Boolean" in service


def test_android_exposes_hinoter_note_capture_contract():
    """Android thin client should be ready to trigger HiNoter-style note capture."""
    service = _read("java/com/mybizcon/client/MyBIZconAccessibilityService.kt")
    overlay = _read("java/com/mybizcon/client/TranslationOverlayService.kt")
    activity = _read("java/com/mybizcon/client/MainActivity.kt")
    strings = _read("res/values/strings.xml")

    assert "NOTES_CAPTURE_URL" in service
    assert "/notes/capture" in service
    assert "sendNoteCaptureToBackend" in service
    assert "ACTION_CAPTURE_NOTE" in overlay
    assert "ACTION_SHOW_NOTE_CAPTURE" in overlay
    assert "captureNoteFromActiveMessenger" in service
    assert '"source_type", "android_overlay"' in service
    assert "conn.connectTimeout = 10000" in service
    assert "conn?.disconnect()" in service
    assert "open_note_capture_demo" in strings
    assert "ACTION_SHOW_NOTE_CAPTURE" in activity


def test_android_resets_scraped_message_cache_when_conversation_changes():
    """Changing chat title must clear stale note-capture message state."""
    service = _read("java/com/mybizcon/client/MyBIZconAccessibilityService.kt")

    assert "private fun resetScrapedMessageCache()" in service
    assert 'lastScrapedText = ""' in service
    assert 'lastScrapedSender = "Unknown"' in service
    assert "activeConversationTitle = titleText\n                resetScrapedMessageCache()" in service
