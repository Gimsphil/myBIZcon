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
