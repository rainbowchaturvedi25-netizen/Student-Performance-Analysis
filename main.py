"""
Student Performance Analysis Prototype Launcher.
Serves the modern frontend and backend RESTful API.
"""

import uvicorn

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000
    print("\n" + "=" * 65)
    print(" 🚀 Starting Student Performance Analysis System")
    print(f" 👉 Web Application & Dashboard : http://{host}:{port}")
    print(f" 👉 Interactive Swagger API Docs : http://{host}:{port}/docs")
    print(f" 👉 ReDoc Documentation        : http://{host}:{port}/redoc")
    print(f" 👉 Health Check Endpoint      : http://{host}:{port}/api/health")
    print("=" * 65 + "\n")
    uvicorn.run("backend.api:app", host=host, port=port, reload=False)
