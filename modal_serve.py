"""
Modal deployment for the financial-ratio similarity service.
Deploy with: modal deploy modal_serve.py
"""
import modal

app = modal.App("dtsc3601-financial-similarity")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi",
        "scikit-learn==1.7.2",
        "joblib",
        "pandas",
        "numpy",
    )
    .add_local_file("serve.py", "/root/serve.py")
    .add_local_file("pipeline_def.py", "/root/pipeline_def.py")
    .add_local_file("pipeline.joblib", "/root/pipeline.joblib")
)


@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    import sys
    sys.path.insert(0, "/root")

    import os
    os.chdir("/root")

    from serve import app as web_app

    return web_app
