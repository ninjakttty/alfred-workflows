#!/usr/bin/env python3
import os
import plistlib
import subprocess
import sys
import xml.sax.saxutils as saxutils


def iterm_running():
    try:
        return subprocess.run(
            ["/usr/bin/osascript", "-e", 'application id "com.googlecode.iterm2" is running'],
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip() == "true"
    except Exception:
        return False


def iterm_windows():
    try:
        result = subprocess.run(
            ["/usr/bin/osascript", "-e", 'tell application id "com.googlecode.iterm2" to count windows'],
            capture_output=True,
            text=True,
            check=False,
        )
        out = result.stdout.strip()
        return int(out) if out.isdigit() else 0
    except Exception:
        return 0


def item(title, subtitle, arg, icon="icon.png"):
    return (
        "  <item uid=\"{uid}\" arg=\"{arg}\" valid=\"yes\">\n"
        "    <title>{title}</title>\n"
        "    <subtitle>{subtitle}</subtitle>\n"
        "    <icon>{icon}</icon>\n"
        "  </item>\n"
    ).format(
        uid=saxutils.escape(arg),
        arg=saxutils.escape(arg),
        title=saxutils.escape(title),
        subtitle=saxutils.escape(subtitle),
        icon=saxutils.escape(icon),
    )


query = sys.argv[1] if len(sys.argv) > 1 else ""
if iterm_running() and iterm_windows() > 0:
    xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<items>\n"
        + item(
            "Open iTerm directory in Finder",
            "Use the active iTerm tab",
            "cdf",
        )
        + "</items>\n"
    )
else:
    xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<items>\n"
        + item(
            "Did you mean cdi?",
            "Open iTerm first, then run cdi",
            "cdi",
        )
        + "</items>\n"
    )
print(xml, end="")
