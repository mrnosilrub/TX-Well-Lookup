#!/usr/bin/env bash
set -euo pipefail

# Usage: API_BASE=http://127.0.0.1:8123 ./scripts/smoke.sh
API_BASE=${API_BASE:-http://127.0.0.1:8000}

echo "Using API_BASE=${API_BASE}"

curl_json() {
	local path="$1"; shift || true
	code=$(curl -sS -o /dev/null -w "%{http_code}" "${API_BASE}${path}")
	if [[ "${code}" != "200" ]]; then
		echo "FAIL: GET ${path} => ${code}" >&2
		exit 1
	fi
	echo "OK: GET ${path} => ${code}"
}

echo "-- Liveness/Readiness"
curl_json "/health"
curl_json "/live" || true
curl_json "/ready" || true

echo "-- Simple search"
code=$(curl -sS -o /tmp/smoke_search.json -w "%{http_code}" "${API_BASE}/v1/search?limit=1")
[[ "${code}" == "200" ]] || { echo "FAIL: /v1/search => ${code}"; exit 1; }
echo "OK: /v1/search => ${code}"

echo "-- PDF export (POST)"
pdf_out="/tmp/smoke.pdf"
curl -sS -X POST "${API_BASE}/v1/reports?format=pdf" \
	-H 'Content-Type: application/json' \
	-d '{"county":"galveston","limit":25}' -o "${pdf_out}"
head4=$(head -c 4 "${pdf_out}" || true)
size_pdf=$(stat -f%z "${pdf_out}" 2>/dev/null || stat -c%s "${pdf_out}")
if [[ "${head4}" != "%PDF" || ${size_pdf} -le 1000 ]]; then
	echo "FAIL: PDF invalid header or too small (${size_pdf} bytes)" >&2
	exit 1
fi
echo "OK: PDF bytes=${size_pdf}"

echo "-- CSV export (POST)"
csv_out="/tmp/smoke.csv"
curl -sS -X POST "${API_BASE}/v1/search.csv" \
	-H 'Content-Type: application/json' \
	-d '{"county":"galveston","limit":25}' -o "${csv_out}"
size_csv=$(stat -f%z "${csv_out}" 2>/dev/null || stat -c%s "${csv_out}")
if [[ ${size_csv} -le 20 ]] || ! grep -q "id,owner,county" "${csv_out}"; then
	echo "FAIL: CSV seems empty or missing header (size=${size_csv})" >&2
	exit 1
fi
echo "OK: CSV bytes=${size_csv}"

echo "-- Batch ZIP (POST)"
zip_out="/tmp/smoke.zip"
printf 'address\nGalveston, TX\nHouston, TX\n' > /tmp/smoke_inputs.csv
curl -sS -X POST "${API_BASE}/v1/batch?limit=2" \
	-F 'file=@/tmp/smoke_inputs.csv' -o "${zip_out}"
head2=$(head -c 2 "${zip_out}" || true)
size_zip=$(stat -f%z "${zip_out}" 2>/dev/null || stat -c%s "${zip_out}")
if [[ "${head2}" != $'PK' || ${size_zip} -le 1000 ]]; then
	echo "FAIL: ZIP invalid header or too small (${size_zip} bytes)" >&2
	exit 1
fi
echo "OK: ZIP bytes=${size_zip}"

echo "All smoke checks passed."


