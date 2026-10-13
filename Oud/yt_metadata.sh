
mkdir metadata

yt-dlp \
--match-filters "title~=(?i)sitar" \
  --match-filters "title~=(?i)oud" \
  --ignore-errors \
  --remote-components "ejs:github" \
  --cookies "cookies.txt" \
  --skip-download \
  --write-info-json \
  -o "metadata/%(upload_date)s - %(title)s.%(ext)s" \
  "https://www.youtube.com/@yadoud/videos"