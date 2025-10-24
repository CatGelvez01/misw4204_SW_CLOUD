# scripts/bench_producer.py
import os
import time
import uuid
import argparse
from celery import Celery

BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

# Task del repo:
TASK_NAME = "app.tasks.video_tasks.process_video_task"  # firma real: (video_id)

def make_run_id() -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    short = uuid.uuid4().hex[:6]
    return f"run_{ts}_{short}"

def main():
    parser = argparse.ArgumentParser(description="Encola ráfagas a Celery")
    parser.add_argument("--video-id", help="ID del video en DB (el task espera video_id)")
    parser.add_argument("--file", help="Ruta archivo (solo si tuvieras otro task que lo acepte)")
    parser.add_argument("--burst", type=int, default=100)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--mode", choices=["kwargs","args"], default="args",
                        help="Cómo enviar parámetros (default: args)")
    args = parser.parse_args()

    run_id = make_run_id()
    print(f"[producer] run_id={run_id}")
    print(f"[producer] broker={BROKER_URL} backend={BACKEND_URL}")

    app = Celery("bench_producer", broker=BROKER_URL, backend=BACKEND_URL)

    # Construcción de payload según lo que pases
    use_kwargs = (args.mode == "kwargs")
    payload_args = []
    payload_kwargs = {}

    if args.video_id:
        # Lo que tu worker realmente espera:
        payload_args = [args.video_id]
        use_kwargs = False  # forzamos posicional para evitar TypeError
    elif args.file:
        # Solo valida existencia si te basas en archivo
        if not os.path.exists(args.file):
            raise SystemExit(f"[producer] archivo no existe: {args.file}")
        payload_args = [args.file]
        payload_kwargs = {"file_path": args.file, "run_id": run_id}
    else:
        raise SystemExit("[producer] Debes pasar --video-id (recomendado) o --file")

    enqueued = 0
    for i in range(args.burst):
        try:
            if use_kwargs:
                app.send_task(TASK_NAME, kwargs=payload_kwargs)
            else:
                app.send_task(TASK_NAME, args=payload_args)
            enqueued += 1
            if args.sleep > 0:
                time.sleep(args.sleep)
        except Exception as e:
            print(f"[producer] ERROR idx={i}: {e}")

    print(f"[producer] encoladas {enqueued} tareas (burst={args.burst})")

if __name__ == "__main__":
    main()
