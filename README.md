本文详细说明了多签密钥生成脚本、环境配置SOP、以及 Electrum 导入指南。
请妥善保存。


🛠️ 1. 环境部署指南

1. 安装软件:

• [Python 3.10+](https://www.python.org/) (安装时勾选 Add to PATH)。

• [VS Code](https://code.visualstudio.com/) 及其 Python 扩展。

2. 断网操作: 建议在完全离线环境下运行脚本。

🚀 2. 运行与生成步骤 (Operation)

1. 在 VS Code 中打开终端，执行 python multisig_gen.py。

2. 输入多签总人数 N。

3. 依次为每位参与者输入“脑口令”和“扩展词”。

4. 获取同级目录下的 multisig_keys.json。

📂 3. Electrum 导入流程 (Importing)

1. 模式: 选择 Multisig wallet。

2. 比例: 设置 M of N (例如 2-of-3)。

3. 主密钥: 粘贴 JSON 中的 zprv。

4. 共同签署人: 粘贴其余参与者的 zpub。

5. 地址校验: 确认生成的地址以 bc1q 开头。
