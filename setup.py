from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).parent


def get_install_requires() -> list[str]:
    requirements_file = ROOT / "requirements.txt"
    if not requirements_file.exists():
        return []

    requirements = []
    for line in requirements_file.read_text(encoding="utf-8").splitlines():
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith("#"):
            requirements.append(stripped_line)
    return requirements


setup(
    name="loan-data-analytics",
    version="0.1.0",
    description="Loan analytics package for amortization schedule calculations.",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("*.tests", "*.tests.*", "tests.*", "tests")),
    include_package_data=True,
    install_requires=get_install_requires(),
    python_requires=">=3.10",
)
