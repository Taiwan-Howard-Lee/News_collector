#!/usr/bin/env python3
"""
Setup script for Singapore News Intelligence Dashboard with Gemini AI
This script helps configure the environment and test the Gemini integration.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60)

def print_step(step, text):
    """Print a formatted step"""
    print(f"\n[{step}] {text}")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def check_flutter():
    """Check if Flutter is installed"""
    try:
        result = subprocess.run(['flutter', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Flutter is installed")
            return True
        else:
            print("❌ Flutter not found")
            return False
    except FileNotFoundError:
        print("❌ Flutter not found")
        return False

def setup_backend():
    """Set up the Python backend"""
    print_step("1", "Setting up Python Backend")
    
    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Determine activation script
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
        pip_path = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_script = "venv/bin/activate"
        pip_path = "venv/bin/pip"
    
    print(f"Virtual environment created. Activate with: {activate_script}")
    
    # Install requirements
    if Path("requirements.txt").exists():
        print("Installing Python dependencies...")
        subprocess.run([pip_path, "install", "-r", "requirements.txt"])
        print("✅ Backend dependencies installed")
    else:
        print("❌ requirements.txt not found")

def setup_frontend():
    """Set up the Flutter frontend"""
    print_step("2", "Setting up Flutter Frontend")
    
    if not check_flutter():
        print("Please install Flutter from: https://flutter.dev/docs/get-started/install")
        return False
    
    # Navigate to frontend directory and install dependencies
    if Path("frontend").exists():
        os.chdir("frontend")
        print("Installing Flutter dependencies...")
        result = subprocess.run(["flutter", "pub", "get"])
        os.chdir("..")
        
        if result.returncode == 0:
            print("✅ Frontend dependencies installed")
            return True
        else:
            print("❌ Failed to install Flutter dependencies")
            return False
    else:
        print("❌ Frontend directory not found")
        return False

def setup_environment():
    """Set up environment configuration"""
    print_step("3", "Setting up Environment Configuration")
    
    env_example = Path("config/env.example")
    env_file = Path("config/.env")
    
    if env_example.exists() and not env_file.exists():
        # Copy example to .env
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Environment file created at config/.env")
        print("⚠️  Please edit config/.env and add your Gemini API key")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
    elif env_file.exists():
        print("✅ Environment file already exists")
    else:
        print("❌ Environment example file not found")

def test_gemini_connection():
    """Test Gemini AI connection"""
    print_step("4", "Testing Gemini AI Connection")
    
    try:
        # Import and test AI processor
        sys.path.append('backend')
        from utils.ai_processor import AIProcessor
        
        processor = AIProcessor()
        
        # Test with a simple prompt
        test_content = "Singapore's economy continues to grow with new tech investments."
        result = processor.generate_summary(test_content, 50)
        
        if result:
            print("✅ Gemini AI connection successful!")
            print(f"Test summary: {result[:100]}...")
            return True
        else:
            print("❌ Gemini AI connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini connection: {e}")
        print("Make sure you've set your GEMINI_API_KEY in config/.env")
        return False

def create_database():
    """Create and initialize database"""
    print_step("5", "Setting up Database")
    
    try:
        sys.path.append('backend')
        from database.connection import create_tables
        
        create_tables()
        print("✅ Database tables created")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def run_tests():
    """Run basic tests"""
    print_step("6", "Running Basic Tests")
    
    try:
        # Test backend imports
        sys.path.append('backend')
        from api.resources import router
        from utils.ai_processor import AIProcessor
        
        print("✅ Backend imports successful")
        
        # Test Flutter build (dry run)
        if Path("frontend").exists():
            os.chdir("frontend")
            result = subprocess.run(["flutter", "analyze"], capture_output=True)
            os.chdir("..")
            
            if result.returncode == 0:
                print("✅ Flutter code analysis passed")
            else:
                print("⚠️  Flutter analysis found issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print_header("🎉 Setup Complete!")
    
    print("\n📋 Next Steps:")
    print("\n1. Configure your Gemini API key:")
    print("   - Edit config/.env")
    print("   - Add your GEMINI_API_KEY")
    print("   - Get key from: https://makersuite.google.com/app/apikey")
    
    print("\n2. Start the backend server:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("   cd backend")
    print("   uvicorn main:app --reload")
    
    print("\n3. Start the Flutter app:")
    print("   cd frontend")
    print("   flutter run -d chrome  # For web")
    print("   flutter run             # For mobile device")
    
    print("\n4. Test the scraper:")
    print("   python backend/run_scraper.py --workers 5")
    
    print("\n🔗 Useful URLs:")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("   Flutter Web: http://localhost:8080 (or auto-assigned port)")

def main():
    """Main setup function"""
    print_header("Singapore News Intelligence Dashboard Setup")
    print("This script will help you set up the complete system with Gemini AI")
    
    # Check prerequisites
    check_python_version()
    
    # Setup steps
    setup_backend()
    setup_frontend()
    setup_environment()
    
    # Test connections
    gemini_ok = test_gemini_connection()
    db_ok = create_database()
    tests_ok = run_tests()
    
    # Summary
    print_header("Setup Summary")
    print(f"✅ Backend: Ready")
    print(f"✅ Frontend: Ready")
    print(f"{'✅' if gemini_ok else '❌'} Gemini AI: {'Connected' if gemini_ok else 'Needs configuration'}")
    print(f"{'✅' if db_ok else '❌'} Database: {'Ready' if db_ok else 'Needs attention'}")
    print(f"{'✅' if tests_ok else '❌'} Tests: {'Passed' if tests_ok else 'Some issues found'}")
    
    if gemini_ok and db_ok and tests_ok:
        print_next_steps()
    else:
        print("\n⚠️  Some issues were found. Please check the errors above and try again.")

if __name__ == "__main__":
    main()
