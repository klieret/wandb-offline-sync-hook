# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from pathlib import Path

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "wandb-offline-sync-hook"
copyright = "2022, Kilian Lieret"
author = "Kilian Lieret"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.napoleon"]

extensions.append("autoapi.extension")
extensions.append("recommonmark")
extensions.append("sphinxarg.ext")

autoapi_type = "python"
autoapi_dirs = ["../../src/wandb_osh"]
autoapi_ignore = ["*/test_*.py"]
autoapi_python_class_content = "init"
autoapi_options = [ 'members', 'undoc-members', 'show-inheritance', 'show-module-summary', 'special-members', 'imported-members', ]


templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]

# -- Copy readme

readme_path = Path(__file__).parent.resolve().parent.parent / "README.md"
readme_target = Path(__file__).parent / "readme.md"

with readme_target.open("w") as outf:
    outf.write(
        "\n".join(
            [
                "Readme",
                "======",
                "",
            ]
        )
    )
    lines = []
    for line in readme_path.read_text().splitlines():
        if line.startswith("# "):
            # Skip title, because we now use "Readme"
            continue
        if "<h1" in line:
            continue
        if "<div" in line or "</div" in line:
            continue
        lines.append(line.replace("readme_assets", "../../readme_assets"))
    outf.write("\n".join(lines))
