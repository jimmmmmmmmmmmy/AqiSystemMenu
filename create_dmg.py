#!/usr/bin/env python3
import os
import subprocess
import shutil

def create_dmg():
    # Configuration
    app_name = "AQI Display"
    dmg_name = f"{app_name}_Installer"
    volume_name = f"{app_name} Installer"
    source_app = f"dist/{app_name}.app"
    
    # Clean up any existing files
    for file in [f"{dmg_name}.dmg", f"{dmg_name}_temp.dmg"]:
        if os.path.exists(file):
            os.remove(file)
    
    # Create a temporary DMG
    subprocess.run([
        "hdiutil", "create",
        "-srcfolder", source_app,
        "-volname", volume_name,
        "-fs", "HFS+",
        "-fsargs", "-c c=64,a=16,e=16",
        "-format", "UDRW",
        f"{dmg_name}_temp.dmg"
    ])
    
    # Convert the temporary DMG to the final compressed DMG
    subprocess.run([
        "hdiutil", "convert",
        f"{dmg_name}_temp.dmg",
        "-format", "UDZO",
        "-o", f"{dmg_name}.dmg"
    ])
    
    # Clean up temporary DMG
    os.remove(f"{dmg_name}_temp.dmg")
    
    print(f"Created {dmg_name}.dmg successfully!")

if __name__ == "__main__":
    # First build the app using py2app
    print("Building application using py2app...")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    subprocess.run(["python3", "setup.py", "py2app"])
    
    # Then create the DMG
    print("Creating DMG...")
    create_dmg()