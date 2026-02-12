import sys
import subprocess
import hashlib
import json
import os

# --- 1. 自动依赖检查与安装 ---
def check_and_install_dependencies():
    try:
        import bip_utils
    except ImportError:
        print("[*] 正在安装依赖库 (bip-utils)...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "bip_utils"])
            print("[+] 依赖安装成功！\n")
        except Exception:
            sys.exit("[!] 自动安装失败，请手动执行: pip install bip-utils")

check_and_install_dependencies()

from bip_utils import (
    Bip32Slip10Secp256k1,
    Base58Decoder,
    Base58Encoder
)

# --- 2. 核心转换逻辑 ---

def convert_to_electrum_version(extended_key_str, target_version_bytes):
    """将标准 xpub/xprv 转换为 Electrum 的 Zpub/Zprv"""
    raw_bytes = Base58Decoder.CheckDecode(extended_key_str)
    new_bytes = target_version_bytes + raw_bytes[4:]
    return Base58Encoder.CheckEncode(new_bytes)

def generate_single_key(participant_id):
    """为单个参与者生成密钥组"""
    print(f"\n" + "-"*30)
    print(f">>> 配置参与者 #{participant_id}")
    print("-"*30)
    
    brain_pass = input(f"请输入【参与者 #{participant_id}】的脑口令: ").strip()
    ext_word = input(f"请输入【参与者 #{participant_id}】的扩展词 (无则回车): ").strip()
    
    if not brain_pass:
        print("❌ 错误：脑口令不能为空！")
        return None

    # PBKDF2 高强度拉伸 (2048次)
    salt = ("mnemonic" + ext_word).encode('utf-8')
    seed = hashlib.pbkdf2_hmac('sha512', brain_pass.encode('utf-8'), salt, 2048)

    # BIP48 路径派生 m/48'/0'/0'/2' (P2WSH)
    bip32_ctx = Bip32Slip10Secp256k1.FromSeed(seed)
    path = "m/48'/0'/0'/2'"
    derived_ctx = bip32_ctx.DerivePath(path)

    # Electrum P2WSH 版本字节
    ZPRV_VERSION = b'\x02\xaa\x7a\x99'
    ZPUB_VERSION = b'\x02\xaa\x7e\xd3'

    zprv = convert_to_electrum_version(derived_ctx.PrivateKey().ToExtended(), ZPRV_VERSION)
    zpub = convert_to_electrum_version(derived_ctx.PublicKey().ToExtended(), ZPUB_VERSION)

    return {
        "participant_id": participant_id,
        "derivation_path": path,
        "zprv": zprv,
        "zpub": zpub
    }

# --- 3. 主程序入口 ---

def main():
    print("="*60)
    print("      Electrum P2WSH (bc1) 多签批量生成 & JSON 导出 V5.0")
    print("="*60)

    try:
        user_input = input("请输入需要生成的总人数 (例如 3): ").strip()
        if not user_input: return
        total_participants = int(user_input)
    except ValueError:
        print("❌ 错误：请输入一个有效的数字。")
        return

    all_keys = []
    for i in range(1, total_participants + 1):
        key_data = generate_single_key(i)
        if key_data:
            all_keys.append(key_data)

    if not all_keys:
        return

    # --- 屏幕显示结果 ---
    print("\n" + "="*60)
    print("✅ 密钥生成完毕！")
    print("="*60)
    for key in all_keys:
        print(f"P#{key['participant_id']} Zpub: {key['zpub']}")

    # --- JSON 导出逻辑 ---
    export_filename = "multisig_keys.json"
    
    # 构建 JSON 结构
    json_data = {
        "wallet_type": "Electrum P2WSH Multisig (bc1)",
        "derivation_path": "m/48'/0'/0'/2'",
        "total_participants": len(all_keys),
        "keys": all_keys
    }

    try:
        with open(export_filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        
        print("\n" + "="*60)
        print(f"📁 导出成功！")
        print(f"文件位置: {os.path.abspath(export_filename)}")
        print("="*60)
    except Exception as e:
        print(f"\n❌ JSON 导出失败: {e}")

    print("\n⚠️  安全警告：")
    print("1. JSON 文件包含私钥 (Zprv)，请在备份到加密介质后立即删除此文件！")
    print("2. 严禁将此 JSON 文件上传至任何云端或通过即时通讯工具发送。")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已手动退出。")
    except Exception as e:
        print(f"\n运行出错: {e}")
