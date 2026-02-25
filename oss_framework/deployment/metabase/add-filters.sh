#!/bin/bash
# Add filters to Metabase dashboards using curl
# Usage: ./add-filters.sh [email] [password]

EMAIL="${1:-frank.lucido@gmail.com}"
PASSWORD="${2:-vincent0408}"
BASE_URL="http://localhost:3000"

echo "🔐 Logging in as $EMAIL..."

# Login and get session token
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/session" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" 2>&1)

SESSION_TOKEN=$(echo "$SESSION_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$SESSION_TOKEN" ]; then
  echo "❌ Login failed"
  echo "Response: $SESSION_RESPONSE"
  exit 1
fi

echo "✅ Login successful"
echo ""

# Get all dashboards
echo "📊 Getting dashboards..."
DASHBOARDS=$(curl -s "$BASE_URL/api/dashboard" \
  -H "X-Metabase-Session: $SESSION_TOKEN" \
  -H "Content-Type: application/json")

echo "✅ Found dashboards:"
echo "$DASHBOARDS" | grep -o '"name":"[^"]*","id":[0-9]*' | while read line; do
  name=$(echo "$line" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
  id=$(echo "$line" | grep -o '"id":[0-9]*' | cut -d':' -f2)
  echo "  ID $id: $name"
done

echo ""

# Function to add filters to a dashboard
add_filters() {
  local dash_id=$1
  local dash_name=$2
  local filters_json=$3
  
  echo "📋 Processing: $dash_name (ID: $dash_id)"
  
  # Get current dashboard state
  local current=$(curl -s "$BASE_URL/api/dashboard/$dash_id" \
    -H "X-Metabase-Session: $SESSION_TOKEN")
  
  # Extract current parameters
  local current_params=$(echo "$current" | grep -o '"parameters":\[[^]]*\]' || echo '"parameters":[]')
  
  echo "  Current filters: $current_params"
  
  # Update dashboard with new filters
  local update_response=$(curl -s -X PUT "$BASE_URL/api/dashboard/$dash_id" \
    -H "X-Metabase-Session: $SESSION_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"parameters\": $filters_json}" 2>&1)
  
  if echo "$update_response" | grep -q '"id":'; then
    echo "  ✅ Filters added successfully"
  else
    echo "  ⚠️  Update response: $update_response"
  fi
  
  echo ""
}

# Dashboard 1: Chronic Absenteeism Risk - School, Grade, Row Limit
echo "=== Dashboard 1: Chronic Absenteeism Risk ==="
DASH1_ID=$(echo "$DASHBOARDS" | grep -o '"name":"Dashboard 1: Chronic Absenteeism Risk","id":[0-9]*' | grep -o '"id":[0-9]*' | cut -d':' -f2)
if [ ! -z "$DASH1_ID" ]; then
  FILTERS1='[{"name":"School","slug":"school_filter","id":"school_filter","type":"string/contains","sectionId":"string","required":false,"default":null},{"name":"Grade Level","slug":"grade_filter","id":"grade_filter","type":"string/contains","sectionId":"string","required":false,"default":null},{"name":"Row Limit","slug":"row_limit","id":"row_limit","type":"number/=","sectionId":"number","required":false,"default":50}]'
  add_filters "$DASH1_ID" "Dashboard 1" "$FILTERS1"
fi

# Dashboard 2: Wellbeing - School, Counselor, Row Limit
echo "=== Dashboard 2: Wellbeing Risk ==="
DASH2_ID=$(echo "$DASHBOARDS" | grep -o '"name":"Dashboard 2: Student Wellbeing Risk Profiles","id":[0-9]*' | grep -o '"id":[0-9]*' | cut -d':' -f2)
if [ ! -z "$DASH2_ID" ]; then
  FILTERS2='[{"name":"School","slug":"school_filter","id":"school_filter","type":"string/contains","sectionId":"string","required":false,"default":null},{"name":"Counselor","slug":"counselor_filter","id":"counselor_filter","type":"string/contains","sectionId":"string","required":false,"default":null},{"name":"Row Limit","slug":"row_limit","id":"row_limit","type":"number/=","sectionId":"number","required":false,"default":100}]'
  add_filters "$DASH2_ID" "Dashboard 2" "$FILTERS2"
fi

# Dashboard 3: Equity - FERPA Min Student Count
echo "=== Dashboard 3: Equity Outcomes ==="
DASH3_ID=$(echo "$DASHBOARDS" | grep -o '"name":"Dashboard 3: Equity Outcomes Analysis","id":[0-9]*' | grep -o '"id":[0-9]*' | cut -d':' -f2)
if [ ! -z "$DASH3_ID" ]; then
  FILTERS3='[{"name":"Min Student Count (FERPA)","slug":"min_student_count","id":"min_student_count","type":"number/=","sectionId":"number","required":false,"default":5}]'
  add_filters "$DASH3_ID" "Dashboard 3" "$FILTERS3"
fi

# Dashboard 4: Class Effectiveness - Teacher, Term, Subject
echo "=== Dashboard 4: Class Effectiveness ==="
DASH4_ID=$(echo "$DASHBOARDS" | grep -o '"name":"Dashboard 4: Class Effectiveness Comparison","id":[0-9]*' | grep -o '"id":[0-9]*' | cut -d':' -f2)
if [ ! -z "$DASH4_ID" ]; then
  FILTERS4='[{"name":"Teacher","slug":"teacher_filter","id":"teacher_filter","type":"string/contains","sectionId":"string","required":false,"default":null},{"name":"Term","slug":"term_filter","id":"term_filter","type":"string/contains","sectionId":"string","required":false,"default":null},{"name":"Subject","slug":"subject_filter","id":"subject_filter","type":"string/contains","sectionId":"string","required":false,"default":null}]'
  add_filters "$DASH4_ID" "Dashboard 4" "$FILTERS4"
fi

# Dashboard 5: Performance Correlations - Significance Threshold
echo "=== Dashboard 5: Performance Correlations ==="
DASH5_ID=$(echo "$DASHBOARDS" | grep -o '"name":"Dashboard 5: Performance Correlations","id":[0-9]*' | grep -o '"id":[0-9]*' | cut -d':' -f2)
if [ ! -z "$DASH5_ID" ]; then
  FILTERS5='[{"name":"Significance Threshold","slug":"significance_threshold","id":"significance_threshold","type":"number/=","sectionId":"number","required":false,"default":0.3}]'
  add_filters "$DASH5_ID" "Dashboard 5" "$FILTERS5"
fi

echo "✅ Done! Refresh your dashboard pages to see the filters."
echo ""
echo "Note: You'll need to manually link the filters to cards by:"
echo "1. Opening each dashboard"
echo "2. Clicking 'Edit'"
echo "3. Clicking on each filter"
echo "4. Selecting which cards it applies to"