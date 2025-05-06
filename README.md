# 🔍 Repmt - Repository Prompt Generator for Python Projects
![Downloads](https://static.pepy.tech/badge/repmt/month) 
[![PyPI Version](https://img.shields.io/pypi/v/repmt)](https://pypi.org/project/repmt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/repmt)](https://pypi.org/project/repmt/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Repmt** is a lightweight tool that analyzes Python repositories and generates **static, structured prompts** — ideal for technical documentation, AI prompt engineering, onboarding new developers, and building intelligent agents. 

Check the Library on Pypi: https://pypi.org/project/repmt/

It provides a **Streamlit-powered UI** to let users select specific files, modules, or directories and generate meaningful, formatted prompts from them.

---

## 🚀 Features

- 🧠 **Static Code-to-Prompt Generation** – Turn codebases into well-structured, static prompts
- 📊 **Streamlit UI** – Choose what you want to generate: prompt type, modules, files, etc.
- 📂 **Selective Targeting** – Focus only on selected modules, folders, or classes
- 📄 **Multi-Format Output (Coming Soon)** – Output to Markdown, HTML, or JSON
- 🧭 **Prompt Types** – Tailored for GPT, documentation, architecture summarization, or onboarding
- 🧼 **Temporary Use Option** – Auto-cleanup after execution

---

## 📦 Installation

```bash

pip install repmt

🖥️ Launch the Streamlit UI
repmt


You will be prompted to:

Select a directory or Python project to analyze

Choose the type of prompt to generate

Choose specific modules, folders, or files to include

Export or copy the generated prompt

⚡ One-Time Use (Temporary)
You can use repmt temporarily without keeping it installed:

pip install repmt && repmt --temp /path/to/repo && pip uninstall repmt -y
The --temp flag auto-uninstalls repmt after use.

🧪 Example Use Cases
Feed structured code chunks into LLMs for contextual reasoning

Document legacy or open-source codebases

Generate onboarding prompts for dev teams

Preprocess repos for embedding-based AI agents

🔐 License
MIT License — Free for both open-source and commercial use.
See LICENSE for more details.

🤝 Contributing
We welcome contributions!
Please read our Contribution Guidelines before submitting PRs.

🛡️ Security
To report a vulnerability, please email: repromptsquest@gmail.com

🙌 Acknowledgements
Thanks to the open-source community and prompt engineering ecosystem for inspiring this project.

Built with ❤️ to make Python repositories more AI-readable and human-friendly.


---

Let me know if you’d like:
- A badge-ready `setup.py` with `console_scripts`
- A `streamlit_app.py` that cleanly links to `repmt`
- Automatic prompt file saving
- Screenshot assets for your GitHub repo visuals

Happy open-sourcing!







