import os
import sys
import subprocess

def main():
    try:
        import PyInstaller  
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name", "UrbanNest",
        "--add-data", "images;images" if os.name == "nt" else "images:images",
        "--add-data", "src/interfaces/NightTrain.json;interfaces" if os.name == "nt" else "src/interfaces/NightTrain.json:interfaces",
        "--add-data", "src/interfaces/Logo.png;interfaces" if os.name == "nt" else "src/interfaces/Logo.png:interfaces",
        "--icon", "src/interfaces/Logo.ico" if os.name == "nt" else "src/interfaces/Logo.png",
        "src/main.py"
    ]

    print("Ejecutando:", " ".join(cmd))
    subprocess.check_call(cmd)

    print("\n✅ Ejecutable generado en la carpeta 'dist/'")

if __name__ == "__main__":
    main()

