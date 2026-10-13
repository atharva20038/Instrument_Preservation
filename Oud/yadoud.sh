yt-dlp \
  --ignore-errors \
  --cookies "cookies.txt" \
  -x --audio-format mp3 \
  -o "%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=s2qsh_I1t7o"