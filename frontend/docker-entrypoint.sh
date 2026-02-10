#!/bin/sh
# Generate runtime config from environment variables
mkdir -p /app/public

cat > /app/public/config.json <<EOF
{
  "apiUrl": "${NEXT_PUBLIC_API_URL:-/api}"
}
EOF

echo "Generated config.json with apiUrl: ${NEXT_PUBLIC_API_URL:-/api}"

# Start the Next.js server
exec node server.js
