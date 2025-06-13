# 为 Addy 贡献代码

首先，感谢您考虑为 Addy 项目做出贡献！我们非常欢迎各种形式的贡献，无论是报告 Bug、提交功能请求，还是直接贡献代码和文档。

## 目录

*   [行为准则](#行为准则)
*   [如何贡献](#如何贡献)
    *   [报告 Bug](#报告-bug)
    *   [提交功能建议](#提交功能建议)
    *   [提交代码](#提交代码)
*   [开发环境设置](#开发环境设置)
*   [代码风格指南](#代码风格指南)
*   [提交 Pull Request](#提交-pull-request)
*   [社区](#社区)

## 行为准则

本项目遵循 [贡献者公约行为准则](CODE_OF_CONDUCT.md) (待创建)。我们希望所有参与者都能遵守该准则，共同营造一个友好和包容的社区环境。

## 如何贡献

### 报告 Bug

如果您在使用 Addy 的过程中发现了 Bug，请通过以下步骤报告：

1.  **检查现有问题**: 在项目的 [GitHub Issues](https://github.com/your-repo/Addy/issues) 中搜索是否已经有人报告了相同的 Bug。
2.  **确保可复现**: 请尽可能提供详细的复现步骤，包括您的操作系统版本、Python 版本、Addy 版本以及导致 Bug 的具体操作。
3.  **提供清晰的描述**: 清晰地描述 Bug 的表现、期望的行为以及实际发生的行为。如果可能，请附上相关的日志信息或截图。
4.  **创建新的 Issue**: 如果没有找到相关的 Issue，请创建一个新的 Bug 报告。使用清晰的标题和描述，并打上 `bug` 标签。

### 提交功能建议

如果您对 Addy 有新的功能想法或改进建议，欢迎提交：

1.  **检查现有建议**: 在项目的 [GitHub Issues](https://github.com/your-repo/Addy/issues) 中搜索是否已经有人提出了类似的功能建议。
2.  **清晰描述您的想法**: 详细说明您希望实现的功能、它能解决什么问题以及它将如何工作。考虑其潜在的用户价值和实现方式。
3.  **创建新的 Issue**: 如果没有找到相关的建议，请创建一个新的功能请求。使用清晰的标题和描述，并打上 `enhancement` 或 `feature request` 标签。

### 提交代码

如果您希望直接贡献代码，请遵循以下步骤：

1.  **Fork 项目**: 将项目 Fork 到您自己的 GitHub 账户。
2.  **Clone 您的 Fork**: 将您 Fork 的仓库 Clone 到本地：
    ```bash
    git clone https://github.com/YOUR_USERNAME/Addy.git
    cd Addy
    ```
3.  **创建分支**: 从 `main` (或当前的开发主分支) 创建一个新的特性分支：
    ```bash
    git checkout -b feature/your-feature-name
    ```
    或者修复 Bug 的分支：
    ```bash
    git checkout -b fix/bug-description
    ```
4.  **进行修改**: 在您的分支上进行代码修改和开发。
5.  **编写测试**: 为您的修改添加必要的单元测试或集成测试。
6.  **确保测试通过**: 运行所有测试以确保您的更改没有破坏现有功能。
7.  **遵循代码风格**: 确保您的代码符合项目的代码风格指南 (见下文)。
8.  **提交更改**: 将您的更改提交到本地分支：
    ```bash
    git add .
    git commit -m "feat: 描述您的功能"  # 或者 fix: 描述您的修复
    ```
    请遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范编写提交信息。
9.  **Push 到您的 Fork**: 将您的分支 Push 到 GitHub 上的 Fork 仓库：
    ```bash
    git push origin feature/your-feature-name
    ```
10. **创建 Pull Request**: 在 GitHub 上打开一个 Pull Request (PR)，从您的特性分支合并到原始项目的 `main` 分支。PR 的标题和描述应清晰说明您的更改内容和目的。关联相关的 Issue (例如 `Closes #123`)。

## 开发环境设置

1.  确保您已安装 Python 3.8+。
2.  克隆项目后，在项目根目录创建并激活虚拟环境 (推荐)：
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
3.  安装项目依赖：
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt  # (如果存在开发依赖)
    ```
4.  根据 [配置指南](CONFIG_GUIDE.md) 配置 `config.ini` 文件，特别是 API 密钥等。

## 代码风格指南

*   **Python**: 我们遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格指南。
*   **Linter 和 Formatter**: 项目可能使用 `flake8` 进行代码检查，使用 `black` 或 `autopep8` 进行代码格式化。请在提交前运行这些工具。
    ```bash
    # 示例
    flake8 .
    black .
    ```
*   **命名约定**: 遵循 Python 的标准命名约定 (例如，函数和变量使用 `snake_case`，类名使用 `CamelCase`)。
*   **注释和文档字符串**: 为复杂的代码段添加注释，为所有公共模块、类和函数编写清晰的文档字符串 (Docstrings)，遵循 [PEP 257](https://www.python.org/dev/peps/pep-0257/)。

## 提交 Pull Request

*   确保您的 PR 只包含与单个功能或 Bug 修复相关的更改。避免在一个 PR 中混合多个不相关的改动。
*   在 PR 描述中清晰地解释您的更改内容、原因以及如何测试。
*   如果您的 PR 解决了某个 Issue，请在描述中链接到该 Issue (例如 `Fixes #123` 或 `Closes #123`)。
*   确保所有自动化检查 (CI/CD) 都通过。
*   项目维护者会审查您的 PR。请耐心等待并准备好根据反馈进行修改。

## 社区

如果您有任何问题或想参与讨论，可以通过以下方式联系我们：

*   **GitHub Issues**: 用于 Bug 报告和功能请求。
*   **(待添加)**: 其他社区渠道，如 Discord 服务器、邮件列表等。

感谢您的贡献！