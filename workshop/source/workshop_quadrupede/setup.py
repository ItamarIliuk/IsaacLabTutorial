"""Instalação do pacote workshop_quadrupede."""

from setuptools import find_packages, setup

setup(
    name="workshop-quadrupede",
    version="1.0.0",
    description="Ambiente de locomoção quadrúpede para o workshop NVIDIA Isaac Lab",
    author="Summit de IA — Joinville, SC",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "isaaclab",
    ],
)
