cache="${alfred_workflow_cache:-$HOME/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/net.ninjakitty.fast-city-time}/v7"
if [[ ! -x "$cache/city-time" || ! -f "$cache/cities.json" ]]; then
  /bin/mkdir -p "$cache"
  tmp=$(/usr/bin/mktemp "$cache/city-time.XXXXXX") || exit 1
  /usr/bin/base64 -D -i city-time.b64 -o "$tmp" || exit 1
  /bin/chmod +x "$tmp"
  /bin/cp cities.json "$cache/cities.json"
  /bin/mv "$tmp" "$cache/city-time"
fi
exec "$cache/city-time" "$@"
