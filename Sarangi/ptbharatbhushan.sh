yt-dlp \
  --match-title "(?i)sarangi" \
  --ignore-errors \
  --cookies "cookies.txt" \
  -x --audio-format mp3 \
  -o "%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/@bharatbhushan.goswami/videos"