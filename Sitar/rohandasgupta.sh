yt-dlp \
  --ignore-errors \
  --cookies "cookies.txt" \
  --match-filters "title~=(?i)sitar" \
  --match-filters "description~=(?i)sitar" \
  -x --audio-format mp3 \
  -o "%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/@RohanDasgupta/videos"
