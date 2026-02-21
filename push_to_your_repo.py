#!/usr/bin/env python3
"""
Push RideConnect to your GitHub repository
Repository: https://github.com/ankit1141r/ride_by_my_idea.git
"""
import subprocess
import sys
import os

REPO_URL = "https://github.com/ankit1141r/ride_by_my_idea.git"
REPO_NAME = "ankit1141r/ride_by_my_idea"

def run_command(command, description, check=False):
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
        if result.stderr and result.returncode != 0:
            print(result.stderr)
            
        if check and result.returncode != 0:
            print(f"❌ {description} - Failed!")
            return False
        
        print(f"✅ {description} - Success!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         🚀 Push to GitHub Repository                       ║
    ║         https://github.com/ankit1141r/ride_by_my_idea      ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check if git is initialized
    if not os.path.exists(".git"):
        print("\n📦 Initializing git repository...")
        run_command("git init", "Initialize Git")
    
    # Check current remote
    print("\n🔍 Checking git remote...")
    run_command("git remote -v", "Show current remotes")
    
    # Remove old origin and add new one
    print("\n🔗 Setting up remote...")
    run_command("git remote remove origin", "Remove old origin (if exists)")
    run_command(f"git remote add origin {REPO_URL}", "Add remote origin", check=True)
    
    # Set branch to main
    run_command("git branch -M main", "Set branch to main")
    
    # Add all files
    print("\n📁 Adding all files...")
    if not run_command("git add .", "Add all files", check=True):
        print("\n⚠️  Failed to add files!")
        return
    
    # Show what will be committed
    print("\n📝 Files to be committed:")
    run_command("git status --short", "Show staged files")
    
    # Commit
    commit_message = "feat: Complete ride-hailing platform with Railway deployment support - Backend API, Web Frontend, Android Apps"
    print(f"\n💾 Committing with message: {commit_message}")
    run_command(f'git commit -m "{commit_message}"', "Commit changes")
    
    # Push to GitHub
    print("\n" + "="*60)
    print("🚀 PUSHING TO GITHUB")
    print("="*60)
    print(f"\nRepository: {REPO_URL}")
    print("\n⚠️  Note: You may need to authenticate with GitHub")
    print("   Use your GitHub username and Personal Access Token")
    print("\n")
    
    input("Press Enter to continue with push...")
    
    # Try to push (force push to overwrite if needed)
    if run_command("git push -u origin main --force", "Push to GitHub", check=True):
        print("\n" + "="*60)
        print("✅ SUCCESS! Code pushed to GitHub!")
        print("="*60)
        print(f"\n🔗 Your repository: https://github.com/{REPO_NAME}")
        print("\n" + "="*60)
        print("📋 NEXT STEPS: Deploy to Railway.app")
        print("="*60)
        print("\n1. Go to https://railway.app")
        print("2. Sign in with GitHub")
        print("3. Click 'New Project'")
        print("4. Select 'Deploy from GitHub repo'")
        print(f"5. Choose: {REPO_NAME}")
        print("6. Add PostgreSQL database")
        print("7. Add Redis database")
        print("8. Configure environment variables:")
        print("   - DATABASE_URL=${{Postgres.DATABASE_URL}}")
        print("   - REDIS_URL=${{Redis.REDIS_URL}}")
        print("   - SECRET_KEY=your-secret-key")
        print("   - JWT_SECRET_KEY=your-jwt-secret")
        print("   - APP_ENV=production")
        print("   - DEBUG=false")
        print("   - PORT=8000")
        print("\n📖 See RAILWAY_QUICK_START.md for detailed instructions")
        print("\n🎉 Your app will be live at: https://your-app.up.railway.app")
    else:
        print("\n" + "="*60)
        print("⚠️  PUSH FAILED")
        print("="*60)
        print("\nThis might be due to:")
        print("1. Authentication required - use GitHub Personal Access Token")
        print("2. Repository doesn't exist - create it first at:")
        print("   https://github.com/new")
        print("\nTo create a Personal Access Token:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Click 'Generate new token (classic)'")
        print("3. Select 'repo' scope")
        print("4. Use the token as your password when pushing")
        print("\nTry running these commands manually:")
        print(f"  git remote add origin {REPO_URL}")
        print("  git branch -M main")
        print("  git push -u origin main")

if __name__ == "__main__":
    main()
