from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOBILE = ROOT / "mobile"


def test_flutter_project_exists_with_stable_package_id():
    assert (MOBILE / "pubspec.yaml").is_file()
    assert (MOBILE / "lib" / "main.dart").is_file()
    assert (MOBILE / "lib" / "channel_client.dart").is_file()
    gradle = (MOBILE / "android" / "app" / "build.gradle.kts").read_text(encoding="utf-8")
    assert 'applicationId = "ru.businessmindset.app"' in gradle
    assert 'namespace = "ru.businessmindset.app"' in gradle


def test_signing_key_example_exists_and_real_key_ignored():
    example = MOBILE / "android" / "key.properties.example"
    assert example.is_file()
    assert not (MOBILE / "android" / "key.properties").exists()
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "mobile/android/key.properties" in gitignore
    assert "*.jks" in gitignore or "mobile/android/**/*.jks" in gitignore
    assert "mobile/**/*.apk" in gitignore


def test_client_uses_only_app_v1_channel_prefix():
    client = (MOBILE / "lib" / "channel_client.dart").read_text(encoding="utf-8")
    assert "static const prefix = '/app/v1'" in client
    assert "api.telegram.org" not in client.lower()
    assert "deepseek" not in client.lower()
    main = (MOBILE / "lib" / "main.dart").read_text(encoding="utf-8")
    assert "ChannelClient" in main
    assert "SessionStore" in main


def test_build_script_points_to_release_apk_path():
    script = (MOBILE / "tool" / "build_author_apk.ps1").read_text(encoding="utf-8")
    assert "flutter build apk --release" in script
    assert "app-release.apk" in script
