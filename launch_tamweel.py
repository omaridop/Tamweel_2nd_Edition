import subprocess
import time
import sys
import os
import webbrowser

def launch():
    print("\n" + "="*50)
    print("   TAMWEEL AI | SYSTEM LAUNCHER")
    print("="*50 + "\n")

    # 1. Start Backend
    print("🚀 Starting FastAPI Backend (Port 8000)...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd="backend",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # 2. Wait a bit for backend to initialize
    time.sleep(3)

    # 3. Start Frontend
    print("🚀 Starting React Frontend (Vite)...")
    # Determine the correct command for npm on windows vs unix
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    
    frontend_process = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd="frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    print("\n✅ Both systems are launching!")
    print("🔗 Backend: http://localhost:8000")
    print("🔗 Frontend: http://localhost:5173 (or 5174)")
    print("\nCredentials:")
    print("👤 User  : anas@tamweel.ai / password123")
    print("💼 Admin : admin@tamweel.ai / adminpassword")
    print("\n" + "-"*50)
    print("Press Ctrl+C to stop both servers.")
    print("-"*50 + "\n")

    # Open the browser automatically to the login page
    time.sleep(2)
    webbrowser.open("http://localhost:5173/login")

    try:
        while True:
            # Just keep the script running
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Tamweel AI...")
        backend_process.terminate()
        frontend_process.terminate()
        print("👋 Goodbye!")

if __name__ == "__main__":
    launch()
