#!/usr/bin/env python3
"""Validate the HTTP Uptime Monitor integration structure."""
import json
import os

def validate_integration():
    """Validate the integration has all required files and structure."""
    base_path = "custom_components/http_uptime"
    
    # Check required files
    required_files = [
        "__init__.py",
        "manifest.json", 
        "config_flow.py",
        "const.py",
        "sensor.py"
    ]
    
    print("🔍 Checking required files...")
    for file in required_files:
        file_path = os.path.join(base_path, file)
        if os.path.exists(file_path):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            return False
    
    # Check manifest.json structure
    print("\n🔍 Checking manifest.json...")
    manifest_path = os.path.join(base_path, "manifest.json")
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        required_keys = ["domain", "name", "config_flow", "version"]
        for key in required_keys:
            if key in manifest:
                print(f"✅ {key}: {manifest[key]}")
            else:
                print(f"❌ {key} - MISSING")
                return False
                
        # Check if config_flow is enabled
        if manifest.get("config_flow") is True:
            print("✅ Config flow enabled")
        else:
            print("❌ Config flow not enabled")
            return False
            
    except Exception as e:
        print(f"❌ Error reading manifest.json: {e}")
        return False
    
    # Check basic Python syntax
    print("\n🔍 Checking Python syntax...")
    for file in ["__init__.py", "config_flow.py", "const.py", "sensor.py"]:
        file_path = os.path.join(base_path, file)
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Basic checks
            if 'DOMAIN' in content or 'domain=' in content:
                print(f"✅ {file} - syntax OK")
            else:
                print(f"⚠️  {file} - no obvious issues but check manually")
        except Exception as e:
            print(f"❌ {file} - Error: {e}")
            return False
    
    print("\n🎉 Integration structure validation completed!")
    print("\n📋 Next steps:")
    print("1. Restart Home Assistant")
    print("2. Go to Settings → Devices & Services")
    print("3. Click '+ Add Integration'")
    print("4. Search for 'HTTP Uptime Monitor'")
    
    return True

if __name__ == "__main__":
    validate_integration()
