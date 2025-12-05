#!/usr/bin/env bash
set -euo pipefail

# Alberta ESL AI - Database Seed Script
# Creates demo session and sample reading results for demonstration

echo "🌱 Seeding database with demo data..."

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend is not running at http://localhost:8000"
    echo "Please start the backend first: make api"
    exit 1
fi

echo "✅ Backend is running"

# Create a demo class session
echo "📝 Creating demo class session..."
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/create-session \
  -H "Content-Type: application/json" \
  -d '{
    "teacher_name": "Ms. Johnson",
    "grade_level": "Grade 4 ESL",
    "settings": {}
  }')

CLASS_CODE=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['class_code'])")
SESSION_ID=$(echo "$SESSION_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

echo "✅ Created session: $SESSION_ID with class code: $CLASS_CODE"

# Add sample participants
echo "👥 Adding sample participants..."

PARTICIPANTS=(
  '{"class_code":"'$CLASS_CODE'","nickname":"Ahmed","l1":"ar"}'
  '{"class_code":"'$CLASS_CODE'","nickname":"Maria","l1":"es"}'
  '{"class_code":"'$CLASS_CODE'","nickname":"Wei","l1":"zh"}'
  '{"class_code":"'$CLASS_CODE'","nickname":"Fatima","l1":"ar"}'
  '{"class_code":"'$CLASS_CODE'","nickname":"Carlos","l1":"es"}'
)

PARTICIPANT_IDS=()

for participant_data in "${PARTICIPANTS[@]}"; do
  PARTICIPANT_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/join \
    -H "Content-Type: application/json" \
    -d "$participant_data")
  
  PARTICIPANT_ID=$(echo "$PARTICIPANT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['participant_id'])")
  NICKNAME=$(echo "$participant_data" | python3 -c "import sys, json; print(json.load(sys.stdin)['nickname'])")
  PARTICIPANT_IDS+=("$PARTICIPANT_ID")
  
  echo "  ✅ Added participant: $NICKNAME (ID: $PARTICIPANT_ID)"
done

# Generate sample reading results
echo "📚 Generating sample reading results..."

# Sample reading scores (realistic for Grade 4 ESL students)
# Using query parameters format for the POST /v1/reading/results endpoint
save_reading_result() {
  local session_id=$1
  local participant_id=$2
  local wpm=$3
  local wcpm=$4
  local accuracy=$5
  local passage_id=$6
  
  curl -s -X POST "http://localhost:8000/v1/reading/results?session_id=${session_id}&participant_id=${participant_id}&wpm=${wpm}&wcpm=${wcpm}&accuracy=${accuracy}&passage_id=${passage_id}" > /dev/null
}

# Add results for each participant
save_reading_result "$SESSION_ID" "${PARTICIPANT_IDS[0]}" 75.5 68.0 0.90 "sample_gr2_weather"
echo "  ✅ Added reading result for Ahmed"
save_reading_result "$SESSION_ID" "${PARTICIPANT_IDS[1]}" 82.3 78.0 0.95 "sample_gr2_weather"
echo "  ✅ Added reading result for Maria"
save_reading_result "$SESSION_ID" "${PARTICIPANT_IDS[2]}" 68.2 60.5 0.88 "sample_gr2_weather"
echo "  ✅ Added reading result for Wei"
save_reading_result "$SESSION_ID" "${PARTICIPANT_IDS[3]}" 91.0 87.0 0.96 "sample_gr4_seasons"
echo "  ✅ Added reading result for Fatima"
save_reading_result "$SESSION_ID" "${PARTICIPANT_IDS[4]}" 78.5 73.0 0.93 "sample_gr4_seasons"
echo "  ✅ Added reading result for Carlos"
# Second round for some students
save_reading_result "$SESSION_ID" "${PARTICIPANT_IDS[0]}" 80.0 74.0 0.92 "sample_gr4_seasons"
echo "  ✅ Added second reading result for Ahmed"
save_reading_result "$SESSION_ID" "${PARTICIPANT_IDS[1]}" 88.0 84.0 0.95 "sample_gr4_seasons"
echo "  ✅ Added second reading result for Maria"
save_reading_result "$SESSION_ID" "${PARTICIPANT_IDS[2]}" 72.0 66.0 0.91 "sample_gr2_weather"
echo "  ✅ Added second reading result for Wei"

echo ""
echo "🎉 Database seeding complete!"
echo ""
echo "Demo Data Summary:"
echo "  📊 Session ID: $SESSION_ID"
echo "  🔑 Class Code: $CLASS_CODE"
echo "  👥 Participants: ${#PARTICIPANT_IDS[@]}"
echo "  📚 Reading Results: 8"
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:3000/session"
echo "  2. View session details for code: $CLASS_CODE"
echo "  3. Visit http://localhost:3000/reading"
echo "  4. Enter session ID: $SESSION_ID to view reading results"
echo ""
