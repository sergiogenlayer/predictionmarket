#!/usr/bin/env python3
"""Recalcula las formulas de un .xlsx con LibreOffice (para que la cache
de valores quede escrita y el fichero se previsualice bien).

Uso: python recalc_lo.py fichero.xlsx
Requiere libreoffice-calc instalado (los runners de GitHub lo traen).
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

MACRO = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic">
    Sub RecalculateAndSave()
      ThisComponent.calculateAll()
      ThisComponent.store()
      ThisComponent.close(True)
    End Sub
</script:module>"""


def recalc(path):
    path = Path(path).resolve()
    env = dict(os.environ, SAL_USE_VCLPLUGIN="svp")
    with tempfile.TemporaryDirectory(prefix="lo-profile-") as prof:
        url = Path(prof).as_uri()
        subprocess.run(
            ["soffice", "--headless", "--terminate_after_init", f"-env:UserInstallation={url}"],
            check=True, capture_output=True, timeout=180, env=env)
        macro_dir = Path(prof) / "user" / "basic" / "Standard"
        macro_dir.mkdir(parents=True, exist_ok=True)
        (macro_dir / "Module1.xba").write_text(MACRO)
        subprocess.run(
            ["soffice", "--headless", "--norestore", f"-env:UserInstallation={url}",
             "vnd.sun.star.script:Standard.Module1.RecalculateAndSave?language=Basic&location=application",
             str(path)],
            check=True, capture_output=True, timeout=300, env=env)


if __name__ == "__main__":
    recalc(sys.argv[1])
    print(f"Recalculado: {sys.argv[1]}")
