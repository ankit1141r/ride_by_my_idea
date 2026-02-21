"""
Fix Android Build Issues
Creates missing resources and fixes configuration
"""

import os

def create_missing_resources():
    """Create missing Android resource files"""
    
    # Create res directories
    rider_res = "android-ride-hailing/rider-app/src/main/res"
    driver_res = "android-ride-hailing/driver-app/src/main/res"
    
    for app_res in [rider_res, driver_res]:
        # Create directories
        os.makedirs(f"{app_res}/xml", exist_ok=True)
        os.makedirs(f"{app_res}/mipmap-hdpi", exist_ok=True)
        os.makedirs(f"{app_res}/mipmap-mdpi", exist_ok=True)
        os.makedirs(f"{app_res}/mipmap-xhdpi", exist_ok=True)
        os.makedirs(f"{app_res}/mipmap-xxhdpi", exist_ok=True)
        os.makedirs(f"{app_res}/mipmap-xxxhdpi", exist_ok=True)
        os.makedirs(f"{app_res}/values", exist_ok=True)
        
        # Create backup_rules.xml
        backup_rules = f"{app_res}/xml/backup_rules.xml"
        if not os.path.exists(backup_rules):
            with open(backup_rules, 'w') as f:
                f.write('''<?xml version="1.0" encoding="utf-8"?>
<full-backup-content>
    <exclude domain="sharedpref" path="device_prefs.xml"/>
</full-backup-content>
''')
            print(f"✓ Created {backup_rules}")
        
        # Create data_extraction_rules.xml
        data_extraction = f"{app_res}/xml/data_extraction_rules.xml"
        if not os.path.exists(data_extraction):
            with open(data_extraction, 'w') as f:
                f.write('''<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <exclude domain="sharedpref" path="device_prefs.xml"/>
    </cloud-backup>
</data-extraction-rules>
''')
            print(f"✓ Created {data_extraction}")
        
        # Create themes.xml
        themes = f"{app_res}/values/themes.xml"
        if not os.path.exists(themes):
            with open(themes, 'w') as f:
                f.write('''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.RideConnect" parent="android:Theme.Material.Light.NoActionBar" />
</resources>
''')
            print(f"✓ Created {themes}")
        
        # Create placeholder launcher icons (simple XML drawables)
        for density in ['hdpi', 'mdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']:
            icon_dir = f"{app_res}/mipmap-{density}"
            
            # ic_launcher.xml
            ic_launcher = f"{icon_dir}/ic_launcher.xml"
            if not os.path.exists(ic_launcher):
                with open(ic_launcher, 'w') as f:
                    f.write('''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@android:color/white"/>
    <foreground android:drawable="@android:color/holo_blue_dark"/>
</adaptive-icon>
''')
            
            # ic_launcher_round.xml
            ic_launcher_round = f"{icon_dir}/ic_launcher_round.xml"
            if not os.path.exists(ic_launcher_round):
                with open(ic_launcher_round, 'w') as f:
                    f.write('''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@android:color/white"/>
    <foreground android:drawable="@android:color/holo_blue_dark"/>
</adaptive-icon>
''')
        
        print(f"✓ Created launcher icons for {app_res}")

if __name__ == "__main__":
    print("=" * 60)
    print("Fixing Android Build Issues")
    print("=" * 60)
    print()
    
    create_missing_resources()
    
    print("\n✓ All resources created!")
    print("\nNow try building again:")
    print("  cd android-ride-hailing")
    print("  gradlew.bat assembleDebug")
