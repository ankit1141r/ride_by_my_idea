#!/usr/bin/env python3
"""
Git Commit Helper - Commit project to GitHub
"""
import subprocess
import sys


def run_command(cmd, description):
    """Run a git command."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} - Success")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def main():
    """Main function."""
    print("\n" + "=" * 70)
    print("  📦 RideConnect - Git Commit Helper")
    print("=" * 70 + "\n")
    
    print("This will commit your project to GitHub\n")
    
    # Check if git is initialized
    print("📋 Checking Git status...")
    result = subprocess.run("git status", shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("\n⚠️  Git is not initialized in this directory")
        response = input("\nInitialize Git repository? (y/n): ").lower()
        if response in ['y', 'yes']:
            if not run_command("git init", "Initializing Git repository"):
                return
        else:
            print("\n❌ Cannot proceed without Git repository")
            return
    else:
        print("✅ Git repository found")
    
    # Check for remote
    print("\n📡 Checking remote repository...")
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    
    if not result.stdout:
        print("\n⚠️  No remote repository configured")
        print("\nPlease provide your GitHub repository URL")
        print("Example: https://github.com/username/repo.git")
        repo_url = input("\nGitHub Repository URL: ").strip()
        
        if repo_url:
            if not run_command(f'git remote add origin "{repo_url}"', "Adding remote repository"):
                return
        else:
            print("\n❌ Repository URL required")
            return
    else:
        print("✅ Remote repository configured:")
        print(result.stdout)
    
    # Add all files
    if not run_command("git add .", "Adding all files"):
        return
    
    # Get commit message
    print("\n📝 Commit Message:")
    print("   Default: 'Complete RideConnect Platform - Full Implementation'")
    custom_message = input("\n   Enter custom message (or press Enter for default): ").strip()
    
    commit_message = custom_message if custom_message else "Complete RideConnect Platform - Full Implementation"
    
    # Commit
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("\n⚠️  Nothing to commit or commit failed")
        print("   This might be okay if everything is already committed")
    
    # Push
    print("\n🚀 Ready to push to GitHub")
    response = input("\nPush to GitHub now? (y/n): ").lower()
    
    if response in ['y', 'yes']:
        # Try to get current branch
        result = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True)
        branch = result.stdout.strip() if result.stdout else "main"
        
        if not branch:
            branch = "main"
            print(f"\n📌 Creating and switching to '{branch}' branch...")
            run_command(f"git branch -M {branch}", f"Setting branch to {branch}")
        
        print(f"\n📤 Pushing to branch: {branch}")
        if run_command(f"git push -u origin {branch}", "Pushing to GitHub"):
            print("\n" + "=" * 70)
            print("  🎉 SUCCESS! Project pushed to GitHub!")
            print("=" * 70)
            print("\n✅ Your RideConnect platform is now on GitHub!")
            print("\n📱 Next steps:")
            print("   1. Visit your GitHub repository")
            print("   2. Check all files are uploaded")
            print("   3. Deploy to Render/Railway for public access")
            print()
        else:
            print("\n❌ Push failed")
            print("\n💡 Common fixes:")
            print("   1. Make sure you're logged into GitHub")
            print("   2. Check repository URL is correct")
            print("   3. Ensure you have push permissions")
            print("   4. Try: git push -f origin main (force push)")
    else:
        print("\n📦 Changes committed locally")
        print("   Run 'git push' when ready to upload to GitHub")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
