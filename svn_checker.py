import json
import os
import subprocess
import datetime
import locale

CONFIG_FILE = "config.json"

def run_command(command, cwd=None):
    try:
        # Use Popen/run with bytes, then decode safely
        result = subprocess.run(
            command, 
            cwd=cwd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # System encoding or cp1254 (Turkish) may be used by svn in cmd
        sys_encoding = locale.getpreferredencoding()
        try:
            stdout_str = result.stdout.decode(sys_encoding, errors='replace')
        except:
            stdout_str = result.stdout.decode('utf-8', errors='replace')
            
        try:
            stderr_str = result.stderr.decode(sys_encoding, errors='replace')
        except:
            stderr_str = result.stderr.decode('utf-8', errors='replace')

        if result.returncode != 0:
            return f"ERROR: {stderr_str.strip()}"
        
        return stdout_str.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"

def get_svn_info(path):
    output = run_command(["svn", "info"], cwd=path)
    if output.startswith("ERROR:"):
        return {"error": output}
    
    info = {}
    for line in output.splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            info[key.strip()] = value.strip()
    return info

def get_remote_revision(url):
    output = run_command(["svn", "info", url])
    if output.startswith("ERROR:"):
        return None
    for line in output.splitlines():
        if line.startswith("Revision:") or line.startswith("Revizyon:"):
            return line.split(": ", 1)[1].strip()
    return None

def get_svn_log(path, local_rev, remote_rev):
    try:
        start_rev = int(local_rev) + 1
    except ValueError:
        start_rev = local_rev
        
    output = run_command(["svn", "log", "-r", f"{start_rev}:HEAD"], cwd=path)
    if output.startswith("ERROR:"):
        return output
    return output

def get_svn_diff(path, local_rev, remote_rev):
        try:
            start_rev = int (local_rev) + 1
        except ValueError:
            start_rev = local_rev
            
        output = run_command(["svn", "diff", "-r", f"{start_rev}:{remote_rev}"], cwd=path)
        if output.startswith("ERROR:"):
            return output
        return output
        
def get_svn_diffSummarize(path, local_rev, remote_rev):
        try:
            start_rev = int(local_rev) + 1
        except ValueError:
                start_rev = local_rev
                
        output = run_command(["svn", "diff", "--summarize", "-r",f"{start_rev}:{remote_rev}"], cwd=path)
        if output.startswith("ERROR:"):
            return output 
        return output

def main():
    print("=== SVN Log & Revizyon Kontrol Araci ===")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, CONFIG_FILE)
    
    if not os.path.exists(config_path):
        print(f"Hata: {CONFIG_FILE} dosyasi bulunamadi. ({config_path})")
        return

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Hata: {CONFIG_FILE} okunamadi. Lutfen dosyanin gecerli bir JSON formati oldugundan emin olun. Detay: {e}")
        return

    paths = config.get("paths", [])
    if not paths:
        print("Uyari: config.json icerisinde kontrol edilecek hicbir dosya yolu (paths) bulunamadi.")
        return

    now = datetime.datetime.now()
    today_time = now.strftime("%Y-%m-%d-%H-%M-%S")
    
    output_dir_config = config.get("output_dir", "")
    if not output_dir_config:
        output_dir_config = base_dir
    elif not os.path.isabs(output_dir_config):
        output_dir_config = os.path.join(base_dir, output_dir_config)

    main_log_folder = os.path.join(output_dir_config, f"log-{today_time}")
    
    if not os.path.exists(main_log_folder):
        try:
            os.makedirs(main_log_folder)
        except Exception as e:
            print(f"Hata: Ana log klasoru olusturulamadi '{main_log_folder}'. Detay: {e}")
            return

    for path in paths:
        print(f"\n--- Kontrol ediliyor: {path} ---")
        path_name = os.path.basename(os.path.normpath(path))
        if not path_name:
            path_name = "BilinmeyenProje"

        report_summary_file = os.path.join(main_log_folder, f"{path_name}_summary.txt")
        report_folder = os.path.join(main_log_folder, path_name)

        # Rapor klasorunu olustur (alt klasor)
        if not os.path.exists(report_folder):
            try:
                os.makedirs(report_folder)
            except Exception as e:
                print(f"Hata: Rapor alt klasoru olusturulamadi '{report_folder}'. Detay: {e}")
                continue

        # SVN path gecerli mi?
        if not os.path.exists(path):
            result_text = f"Hata: Belirtilen dizin bilgisayarda bulunamadi -> {path}\nLutfen json icindeki yolu kontrol ediniz.\n"
            print(result_text.strip())
            with open(report_summary_file, 'w', encoding='utf-8') as rf:
                rf.write(result_text)
            continue

        info = get_svn_info(path)
        if "error" in info:
            result_text = f"Hata: SVN bilgisi alinamadi. Bu dizin bir SVN projesi olmayabilir veya 'svn' komutu calismiyor.\nDizin: {path}\nDetay: {info['error']}\n"
            print(result_text.strip())
            with open(report_summary_file, 'w', encoding='utf-8') as rf:
                rf.write(result_text)
            continue

        # Turkish and English keys support for "Revision" and "URL"
        local_rev = info.get("Last Changed Rev")
        url = info.get("URL") or info.get("URL Adresi")

        if not local_rev or not url:
            result_text = f"Hata: SVN bilgileri eksik alindi (Revision veya URL bulunamadi). Dizin: {path}\nBulunan bilgiler: {list(info.keys())}\n"
            print(result_text.strip())
            with open(report_summary_file, 'w', encoding='utf-8') as rf:
                rf.write(result_text)
            continue
        
        print(f"Lokal Revizyon: {local_rev}")
        print("Sunucudaki guncel revizyon kontrol ediliyor...")
        
        remote_rev = get_remote_revision(url)
        if not remote_rev:
            result_text = f"Hata: Sunucu revizyonu alinamadi. Ag baglantinizi veya yetkilerinizi kontrol edin. URL: {url}\n"
            print(result_text.strip())
            with open(report_summary_file, 'w', encoding='utf-8') as rf:
                rf.write(result_text)
            continue

        print(f"Sunucu Revizyonu: {remote_rev}")

        with open(report_summary_file, 'w', encoding='utf-8') as rf:
            rf.write(f"Proje Yolu: {path}\n")
            rf.write(f"Proje URL: {url}\n")
            rf.write(f"Lokal Revizyon (Bilgisayardaki): {local_rev}\n")
            rf.write(f"Sunucu Revizyonu (Remote): {remote_rev}\n\n")

            if str(local_rev) == str(remote_rev):
                print("Fark yok.")
                rf.write("Sonuc: Lokal ve sunucu esit. Fark yok.\n")
            else:
                print("Fark var! Loglar cekiliyor...")
                rf.write("Sonuc: Guncellemeler var! Asagida son degisiklikler listelenmistir:\n")
                rf.write("-" * 50 + "\n")
                log_output = get_svn_log(path, local_rev, remote_rev)
                rf.write(log_output)
                rf.write("\n" + "-" * 50 + "\n")
                log_output_diffSummarize = get_svn_diffSummarize(path,local_rev,remote_rev)
                rf.write(log_output_diffSummarize)
                rf.write("\n" + "-" * 50 + "\n")
                
        if str(local_rev) != str(remote_rev):
            log_output_diff = get_svn_diff(path, local_rev, remote_rev)
            diffs = log_output_diff.split("Index: ")
            for diff in diffs:
                if not diff.strip():
                    continue
                lines = diff.splitlines()
                file_name = lines[0].strip()
                if not file_name:
                    continue
                
                safe_file_name = file_name.replace("/", "_").replace("\\", "_").replace(".", "_") + "_log.txt"
                file_diff_path = os.path.join(report_folder, safe_file_name)
                
                with open(file_diff_path, 'w', encoding='utf-8') as f_diff:
                    f_diff.write("Index: " + diff)

        print(f"Rapor olusturuldu: {report_summary_file}")
        
    print("\nTum islemler tamamlandi.")

if __name__ == "__main__":
    main()