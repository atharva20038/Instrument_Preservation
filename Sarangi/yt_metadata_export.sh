mkdir -p metadata

yt-dlp \
  --match-title "(?i)sarangi" \
  --ignore-errors \
  --remote-components "ejs:github" \
  --cookies "cookies.txt" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/@bharatbhushan.goswami/videos"