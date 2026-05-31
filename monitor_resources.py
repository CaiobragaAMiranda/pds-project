import psutil
import time
import os
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

def monitor(duration_seconds=60, interval=2):
    print(f"{'Tempo (s)':<10} | {'RAM (MB)':<12} | {'VRAM (MB)':<12} | {'Status'}")
    print("-" * 50)
    
    start_time = time.time()
    max_ram = 0
    max_vram = 0
    
    try:
        while time.time() - start_time < duration_seconds:
            # Monitor CPU RAM
            ram_mb = psutil.virtual_memory().used / (1024 * 1024)
            process_ram = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
            
            # Monitor GPU VRAM
            vram_mb = 0
            if HAS_TORCH and torch.cuda.is_available():
                vram_mb = torch.cuda.memory_allocated() / (1024 * 1024)
            
            max_ram = max(max_ram, process_ram)
            max_vram = max(max_vram, vram_mb)
            
            elapsed = int(time.time() - start_time)
            
            status = "OK"
            if process_ram > 2048 or vram_mb > 2048:
                status = "⚠️ ALERTA: > 2GB"
                
            print(f"{elapsed:<10} | {process_ram:<12.2f} | {vram_mb:<12.2f} | {status}")
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido.")
    
    print("\n" + "="*30)
    print(f"PICO DE RAM DO PROCESSO: {max_ram:.2f} MB")
    print(f"PICO DE VRAM (GPU): {max_vram:.2f} MB")
    print("="*30)

if __name__ == "__main__":
    monitor(duration_seconds=300) # Monitora por 5 minutos
