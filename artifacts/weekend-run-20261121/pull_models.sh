#!/bin/bash
for m in granite3.3:8b llama3.1:8b-instruct-q4_K_M; do
  echo "== $m $(date -u +%FT%TZ)"
  curl -s -N --max-time 7200 http://172.31.0.1:11440/api/pull -d "{\"model\":\"$m\",\"stream\":true}" | grep --line-buffered -vE '"completed"'
  echo "== end $m $(date -u +%FT%TZ)"
done
curl -s http://172.31.0.1:11440/api/tags
