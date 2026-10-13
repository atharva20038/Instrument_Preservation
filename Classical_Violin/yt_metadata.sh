mkdir metadata

yt-dlp \
  --ignore-errors \
  --cookies "cookies.txt" \
  --remote-components "ejs:github" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=dPTzHiFIqS4"

yt-dlp \
  --ignore-errors \
  --cookies "cookies.txt" \
  --remote-components "ejs:github" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=CNK_15G_QU0"

yt-dlp \
  --ignore-errors \
  --cookies "cookies.txt" \
  --remote-components "ejs:github" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=AxSjVvTU4Zw" 

yt-dlp \
  --ignore-errors \
  --cookies "cookies.txt" \
  --remote-components "ejs:github" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=I4eEylizW4I" 
