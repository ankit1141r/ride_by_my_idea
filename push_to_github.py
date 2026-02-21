#!/usr/bin/env python3
"""
Push RideConnect to GitHub
"""
import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        if result.returncode != 0:
            print(f"⚠️  Command returned code {result.returncode}")
            return False
        
        print(f"✅ {description} - Success!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         🚀 Push RideConnect to GitHub                      ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check git status
    print("\n📊 Checking git status...")
    run_command("git status", "Git Status Check")
    
    # Add all files
    if not run_command("git add .", "Adding all files to git"):
        print("\n⚠️  Failed to add files, but continuing...")
    
    # Show what will be committed
    print("\n📝 Files to be committed:")
    run_command("git status --short", "Show staged files")
    
    # Commit
    commit_message = "feat: Add Railway deployment configuration and complete ride-hailing platform"
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("\n⚠️  Commit failed - maybe no changes to commit?")
        print("Checking if we can push existing commits...")
    
    # Check remote
    print("\n🔍 Checking git remote...")
    run_command("git remote -v", "Show git remotes")
    
    # Push to GitHub
    print("\n" + "="*60)
    print("🚀 PUSHING TO GITHUB")
    print("="*60)
    print("\n⚠️  If this is your first push, you may need to:")
    print("   1. Create a repository on GitHub")
    print("   2. Run: git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git")
    print("   3. Run: git branch -M main")
    print("   4. Run: git push -u origin main")
    print("\n")
    
    # Try to push
    if run_command("git push", "Pushing to GitHub"):
        print("\n" + "="*60)
        print("✅ SUCCESS! Code pushed to GitHub!")
        print("="*60)
        print("\n📋 NEXT STEPS:")
        print("   1. Go to https://railway.app")
        print("   2. Sign in with GitHub")
        print("   3. Click 'New Project'")
        print("   4. Select 'Deploy from GitHub repo'")
        print("   5. Choose your repository")
        print("   6. Add PostgreSQL and Redis databases")
        print("   7. Configure environment variables")
        print("\n📖 See RAILWAY_QUICK_START.md for detailed instructions")
    else:
        print("\n" + "="*60)
        print("⚠️  PUSH FAILED - Manual Setup Required")
        print("="*60)
        print("\n📋 Run these commands manually:")
        print("\n1. Create a new repository on GitHub")
        print("   Go to: https://github.com/new")
        print("\n2. Set up remote and push:")
        print("   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git")
        print("   git branch -M main")
        print("   git push -u origin main")
        print("\n3. Then deploy to Railway:")
        print("   See RAILWAY_QUICK_START.md")

if __name__ == "__main__":
    main()
