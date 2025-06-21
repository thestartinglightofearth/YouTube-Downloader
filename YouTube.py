import yt_dlp, os, requests, re, ffmpeg
from pyfiglet import figlet_format


def filter_text(text):
    result = []
    for ch in text:
        if ch.isalnum() or ch in [" ", ".", ",", "।"]:
            result.append(ch)
    return "".join(result)


class Colors:
    def __init__(self):
        self.bgcolor = "\x1b[101;m"
        self.red = "\x1b[91;m"
        self.green = "\x1b[92;m"
        self.yellow = "\x1b[93;m"
        self.blue = "\x1b[94;m"
        self.magenta = "\x1b[95;m"
        self.cyan = "\x1b[96;m"
        self.reset = "\x1b[00;m"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    banner = ""
    for i in figlet_format("YouTube", font="larry3d").splitlines():
        banner += " " + i + " \n"
    print(Colors().bgcolor + banner + Colors().reset)


def format_filesize(filesize):
    if filesize is None:
        return "Unknown size"
    if filesize < 1024 * 1024:
        return f"{filesize / 1024:.2f} KB"
    else:
        return f"{filesize / (1024 * 1024):.2f} MB"


class YouTube:
    def __init__(self, url):
        self.url = url
        self.best_audio = None
        self.video_info = {}
        self.download_link = []
        self.download_banner = []
        self.print_info()

    def find_best_audio(self, formats):
        best_audio = None
        max_abr = 0
        for fmt in formats:
            if fmt.get("vcodec") == "none":
                abr = fmt.get("abr") or 0
                if abr > max_abr:
                    max_abr = abr
                    best_audio = fmt
        if not best_audio:
            max_abr = 0
            for fmt in formats:
                abr = fmt.get("abr") or 0
                if abr > max_abr and abr > 0:
                    max_abr = abr
                    best_audio = fmt
        self.best_audio = best_audio.get("url")

    def download_file(self, url, filename=None):
        if filename is None:
            filename = url.split("/")[-1]
        status = os.system(f'aria2c "{url}" -o "{filename}" -x 16 -s 16')
        if status == 0:
            print(f"Downloaded: {filename}")
        else:
            print("Download failed.")

    def downloader(self):
        try:
            i = 0
            for item in self.download_banner:
                print(f"{i}.", item)
                i += 1
            try:
                chose = input(Colors().green + ">> " + Colors().reset)
                dlink = self.download_link[int(chose)][0]
                vext = self.download_link[int(chose)][1]
                kind = self.download_link[int(chose)][2]
                if kind == "Video Only":
                    self.merge_video(dlink, vext)
                else:
                    self.download_file(
                        dlink, filter_text(self.video_info.get("title")) + "." + vext
                    )
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

    def merge_video(self, url, ext):
        title = filter_text(self.video_info.get("title"))
        video_file = title + "." + ext
        audio_file = ".tmp_audio"

        self.download_file(url, video_file)
        self.download_file(self.best_audio, audio_file)
        os.system(
            'ffmpeg -i "'
            + video_file
            + '" -i "'
            + audio_file
            + '" -c:v copy -c:a aac "ripon_'
            + video_file
            + '"'
        )
        os.remove(audio_file)
        os.remove(video_file)

    def show_details(self, info):
        try:
            self.video_info["title"] = info.get("title")
            i = 0
            self.find_best_audio(info.get("formats", []))
            for f in info.get("formats", []):
                ext = f.get("ext", "unknown")
                height = f.get("height")
                acodec = f.get("acodec")
                vcodec = f.get("vcodec")
                format_note = f.get("format_note", "")
                filesize = format_filesize(
                    f.get("filesize") or f.get("filesize_approx")
                )

                # Identify format type
                if acodec != "none" and vcodec != "none":
                    kind = "Video+Audio"
                elif acodec != "none":
                    kind = "Audio Only"
                elif vcodec != "none":
                    kind = "Video Only"
                else:
                    kind = "Unknown"
                if (
                    kind != "Unknown"
                    and filesize != None
                    and f.get("url") != None
                    and filesize != "Unknown size"
                ):
                    self.download_banner.append(
                        f"{kind:<12} | ext: {ext:<4} | height: {height or 'N/A':<5} | note: {format_note:<10} | size: {filesize or 'unknown'}"
                    )
                    self.download_link.append([f.get("url"), f.get("ext"), kind])
                    i += 1
            self.downloader()
        except Exception as e:
            print("Error:", e)

    def print_info(self):
        try:
            option = {
                "skip_download": "true",
                "quiet": "true",
                "force_generic_extractor": False,
            }
            ydl = yt_dlp.YoutubeDL(option)
            info = ydl.extract_info(self.url, download=False)
            self.show_details(info)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    clear_screen()
    print_banner()
    url = input(Colors().green + " Enter you video url: " + Colors().reset)
    YouTube(url)
