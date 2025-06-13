import sys
import os
from gui.main_window import CVAnalyzerApp

def main():
    """Main entry point for the CV Analyzer application"""
    try:
        app = CVAnalyzerApp()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 