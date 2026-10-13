mkdir metadata

yt-dlp \
  -vU \
  --cookies "cookies.txt" \
  --remote-components "ejs:github" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=zEUGx6Cmmqc"

yt-dlp \
  -vU \
  --cookies "cookies.txt" \
  --remote-components "ejs:github" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=e26zZ83Oh6Y"

yt-dlp \
  -vU \
  --cookies "cookies.txt" \
  --remote-components "ejs:github" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=NyuRqKgP2T4"  

yt-dlp \
  -vU \
  --cookies "cookies.txt" \
  --remote-components "ejs:github" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=RhxMNHfsrNI"  

yt-dlp \
  -vU \
  --cookies "cookies.txt" \
  --remote-components "ejs:github" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=a59SLwrJEJ4"  

yt-dlp \
  -vU \
  --cookies "cookies.txt" \
  --remote-components "ejs:github" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=srBUB4XEjoo"  

  
  
  
  