# 📋 Feedback Admin Guide - Pookie4u

## How to Access User Feedback

User feedback is stored in the MongoDB database under the `feedback` collection. You can access it in two ways:

---

## Method 1: Using the API Endpoint (Recommended)

### Get All Feedback
```bash
curl https://your-backend-url.com/api/feedback/all
```

**Response Example:**
```json
{
  "success": true,
  "total": 25,
  "feedback": [
    {
      "_id": "65f1a2b3c4d5e6f7g8h9i0j1",
      "user_id": "65abc123...",
      "user_email": "user@example.com",
      "user_name": "John Doe",
      "type": "bug",
      "message": "Login button not working on iOS",
      "contact_email": "user@example.com",
      "images": [],
      "status": "pending",
      "created_at": "2024-10-28T10:30:00",
      "updated_at": "2024-10-28T10:30:00"
    }
  ]
}
```

### Filter by Status
```bash
# Get only pending feedback
curl "https://your-backend-url.com/api/feedback/all?status=pending"

# Get only resolved feedback
curl "https://your-backend-url.com/api/feedback/all?status=resolved"
```

### Filter by Type
```bash
# Get only bug reports
curl "https://your-backend-url.com/api/feedback/all?type=bug"

# Get only feature requests
curl "https://your-backend-url.com/api/feedback/all?type=feature"

# Get general feedback
curl "https://your-backend-url.com/api/feedback/all?type=general"
```

### Combine Filters
```bash
# Get pending bug reports
curl "https://your-backend-url.com/api/feedback/all?status=pending&type=bug"

# Limit results to 50
curl "https://your-backend-url.com/api/feedback/all?limit=50"
```

---

## Method 2: Direct MongoDB Access

### Using MongoDB Shell
```bash
# Connect to MongoDB
mongosh

# Switch to your database
use pookie4u_db

# Get all feedback
db.feedback.find().pretty()

# Get only pending feedback
db.feedback.find({ status: "pending" }).pretty()

# Get only bug reports
db.feedback.find({ type: "bug" }).pretty()

# Count total feedback
db.feedback.countDocuments()

# Get recent feedback (last 10)
db.feedback.find().sort({ created_at: -1 }).limit(10).pretty()

# Get feedback from specific user
db.feedback.find({ user_email: "user@example.com" }).pretty()
```

### Using MongoDB Compass (GUI)
1. Download MongoDB Compass: https://www.mongodb.com/products/compass
2. Connect to your MongoDB instance
3. Navigate to `feedback` collection
4. Use filters to search/sort data

---

## Feedback Data Structure

Each feedback document contains:

| Field | Type | Description |
|-------|------|-------------|
| `_id` | ObjectId | Unique feedback ID |
| `user_id` | String | User's database ID |
| `user_email` | String | User's email address |
| `user_name` | String | User's display name |
| `type` | String | bug, feature, or general |
| `message` | String | Feedback message text |
| `contact_email` | String | Contact email (optional) |
| `images` | Array | Base64 image attachments |
| `status` | String | pending, reviewed, or resolved |
| `created_at` | String | ISO timestamp |
| `updated_at` | String | ISO timestamp |

---

## Feedback Types

### 1. Bug Reports (`type: "bug"`)
- User reports issues or errors
- Should be prioritized for fixing

### 2. Feature Requests (`type: "feature"`)
- User suggests new features
- Can be prioritized by user demand

### 3. General Feedback (`type: "general"`)
- General comments, suggestions
- May include compliments or complaints

---

## Feedback Status

### `pending`
- New feedback that hasn't been reviewed
- Default status for all submissions

### `reviewed`
- Feedback has been seen/acknowledged
- Update status manually after review

### `resolved`
- Issue fixed or feature implemented
- Can notify user of resolution

---

## Common MongoDB Queries

### Get All Pending Bug Reports
```javascript
db.feedback.find({ 
  type: "bug", 
  status: "pending" 
}).sort({ created_at: -1 })
```

### Get Feedback Count by Type
```javascript
db.feedback.aggregate([
  { $group: { _id: "$type", count: { $sum: 1 } } }
])
```

### Get Recent Feedback (Last 7 Days)
```javascript
db.feedback.find({
  created_at: {
    $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
  }
}).sort({ created_at: -1 })
```

### Update Feedback Status
```javascript
db.feedback.updateOne(
  { _id: ObjectId("YOUR_FEEDBACK_ID") },
  { $set: { 
      status: "resolved",
      updated_at: new Date().toISOString()
    }
  }
)
```

---

## Tips for Managing Feedback

1. **Check Regularly**: Review feedback at least once a day
2. **Prioritize Bugs**: Fix critical bugs immediately
3. **Track Feature Requests**: Keep a list of most-requested features
4. **Respond to Users**: Users appreciate acknowledgment
5. **Mark as Resolved**: Update status after addressing issues

---

## Example Workflow

1. **Daily Morning**: Check new pending feedback
   ```bash
   curl "https://your-backend-url.com/api/feedback/all?status=pending"
   ```

2. **Review Each Item**: 
   - Bugs → Create GitHub issue
   - Features → Add to roadmap
   - General → Read and note

3. **Update Status**: Mark reviewed items
   ```javascript
   db.feedback.updateMany(
     { status: "pending" },
     { $set: { status: "reviewed" } }
   )
   ```

4. **Weekly Review**: Check all reviewed items and mark resolved ones

---

## Access URLs

**Production API:**
```
https://your-domain.com/api/feedback/all
```

**Local Development:**
```
http://localhost:8001/api/feedback/all
```

**MongoDB Connection:**
```
mongodb://localhost:27017/pookie4u_db
```

---

## Contact

For questions about feedback management, contact your development team.
