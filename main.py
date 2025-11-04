from fastapi import FastAPI, Request
from pydantic import BaseModel
import tempfile
import base64
import io
import sys
import os
from docx import Document

app = FastAPI()

class CodeInput(BaseModel):
    code: str
    token: str = "n8n"

@app.post("/run")
async def run_code(input: CodeInput):
    if input.token != os.getenv("API_TOKEN"):
        return {"error": "Invalid token"}

    try:
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        exec(input.code, {}, {})
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        if 'doc' in locals() and isinstance(doc, Document):
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            docx_b64 = base64.b64encode(buffer.read()).decode('utf-8')
            return {"success": True, "docxBase64": docx_b64, "output": output}
        else:
            return {"success": True, "output": output}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
