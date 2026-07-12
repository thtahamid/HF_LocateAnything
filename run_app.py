#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import trackio as wandb

def generate_summary_report(run):
    """Fetches collected telemetry data from trackio and prints a hardware report."""
    print("\n" + "="*50)
    print("📋 GRADIO APP RUNTIME REPORT (TRACKIO)")
    print("="*50)
    
    # Extract structural summaries recorded by Trackio
    try:
        # Fetch tracked system histories
        history = run.history()
        
        # CPU Metrics
        if "system.cpu" in history:
            cpus = history["system.cpu"]
            print(f"💻 Average CPU Utilization : {sum(cpus)/len(cpus):.2f}%")
            print(f"🚀 Peak CPU Utilization    : {max(cpus):.2f}%")
            
        # RAM Metrics
        if "system.memory" in history:
            ram = history["system.memory"]
            print(f"💾 Average RAM Utilization : {sum(ram)/len(ram):.2f}%")
            print(f"🔥 Peak RAM Utilization    : {max(ram):.2f}%")
            
        # GPU / VRAM Metrics (if CUDA was active during inference)
        if "system.gpu.0.gpu" in history:
            gpus = history["system.gpu.0.gpu"]
            vram = history["system.gpu.0.memory"]
            print(f"🎮 Average GPU Utilization : {sum(gpus)/len(gpus):.2f}%")
            print(f"⚡ Peak GPU Utilization    : {max(gpus):.2f}%")
            print(f"📼 Peak VRAM Allocation    : {max(vram):.2f}%")
            
    except Exception as e:
        print(f"⚠️ Could not extract automated telemetry graphs: {e}")
        print("💡 You can view full plots by running: trackio show")
        
    print("="*50 + "\n")

def main():
    # 1. Initialize Trackio in the background script
    print("[Trackio] Initializing background resource profiler...")
    run = wandb.init(
        project="gradio-app-telemetry",
        name=f"run_{int(time.time())}",
        config={
            "environment": "ZeroGPU-Emulation" if "spaces" in sys.modules else "Local-Hardware",
            "python_version": sys.version.split()[0]
        }
    )

    # 2. Launch your original Gradio file as a subprocess
    app_filename = "app.py"  # Change this if your script has a different name
    print(f"[Wrapper] Starting application: {app_filename}...")
    
    process = None
    try:
        # Start the app and inherit standard inputs/outputs so you see your logs live
        process = subprocess.Popen([sys.executable, app_filename])
        
        # Keep the wrapper alive while checking system metrics
        while process.poll() is None:
            # We log a simple timestamp pulse to keep the run timeline moving forward.
            # Trackio automatically collects system hardware stats in a background thread.
            wandb.log({"runtime_seconds_elapsed": time.process_time()})
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n[Wrapper] Shutdown signal received. Closing application...")
    finally:
        # Ensure the app subprocess is terminated safely if closed via Ctrl+C
        if process and process.poll() is None:
            process.terminate()
            process.wait()
        
        # 3. Stop recording and build the summary report
        print("[Trackio] Finalizing session data...")
        generate_summary_report(run)
        wandb.finish()

if __name__ == "__main__":
    main()