
mkdir metadata

yt-dlp \
--match-filters "title~=(?i)sitar" \
  --match-filters "description~=(?i)sitar" \
  --ignore-errors \
  --remote-components "ejs:github" \
  --cookies "cookies.txt" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/@RohanDasgupta/videos"