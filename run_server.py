#!/usr/bin/env python3
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting Shree Shyam Toys Server on http://0.0.0.0:{port} ...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
