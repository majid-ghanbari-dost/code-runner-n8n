from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import subprocess
import os
from fastapi.responses import FileResponse

app = FastAPI()

API_TOKEN = os.getenv('API_TOKEN')

class CodeRequest(BaseModel):
    code: str

async def verify_token(authorization: str = Header(None)):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="توکن نامعتبر! دسترسی رد شد.")
    return True

@app.post("/execute-code")
async def execute_code(request: CodeRequest, verified = Depends(verify_token)):
    try:
        temp_file = "/tmp/temp_code.py"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(request.code)
        
        result = subprocess.run(["python", temp_file], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"خطا در اجرای کد: {result.stderr}")  # log برای debug
            raise HTTPException(status_code=500, detail=f"خطا در اجرای کد: {result.stderr}")
        
        output_file = "/tmp/output.docx"  # همیشه این نام
        if not os.path.exists(output_file):
            print("فایل output.docx ساخته نشد!")  # log
            raise HTTPException(status_code=404, detail="فایل ورد ساخته نشد!")
        
        print(f"فایل ساخته شد: {os.path.getsize(output_file)} bytes")  # log موفقیت
        
        return FileResponse(
            path=output_file,
            filename="translated_document.docx",  # نام دانلود
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="تایم‌اوت — کد طولانی")
    except Exception as e:
        print(f"خطای کلی: {str(e)}")  # log
        raise HTTPException(status_code=500, detail=f"خطای کلی: {str(e)}")

@app.get("/")
async def root():
    return {"پیام": "سرور آماده است! برای تست، به /execute-code POST کنید با توکن."}
